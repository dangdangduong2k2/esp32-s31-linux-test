/* SPDX-License-Identifier: MIT
 * One WS2812 on GPIO60, via the companion GPSPI2 overlay.
 * Freestanding RV32 Linux executable: Linux syscalls, no ESP-IDF runtime.
 */
typedef unsigned char u8;
typedef unsigned int u32;
typedef unsigned long long u64;

static long sys3(long n, long x, long y, long z)
{
    register long a0 __asm__("a0") = x;
    register long a1 __asm__("a1") = y;
    register long a2 __asm__("a2") = z;
    register long a3 __asm__("a3") = 0;
    register long a7 __asm__("a7") = n;
    __asm__ volatile ("ecall" : "+r"(a0) : "r"(a1), "r"(a2), "r"(a3), "r"(a7) : "memory");
    return a0;
}

static void say(const char *s)
{
    unsigned n = 0;
    while (s[n]) n++;
    sys3(64, 1, (long)s, n); /* write */
}

static int eq(const char *a, const char *b)
{
    while (*a && *a == *b) { a++; b++; }
    return *a == *b;
}

static int byte_arg(const char *s)
{
    unsigned n = 0;
    if (!*s) return -1;
    while (*s) {
        if (*s < '0' || *s > '9') return -1;
        n = n * 10 + (*s++ - '0');
        if (n > 255) return -1;
    }
    return (int)n;
}

static void number(unsigned n)
{
    char buf[12]; unsigned i = sizeof(buf);
    do { buf[--i] = '0' + n % 10; n /= 10; } while (n);
    sys3(64, 1, (long)(buf + i), sizeof(buf) - i);
}

static int fail(const char *where, long rc)
{
    say("rgb-led: "); say(where); say(" failed, errno=");
    number(rc < 0 ? (unsigned)-rc : 5); say("\n");
    return 1;
}

/* A 32-bit Linux userspace uses the time64 ABI on this RISC-V port. */
static long reset_wait(void)
{
    const struct { long long sec, nsec; } t = {0, 20000000};
    long rc;
    do { rc = sys3(407, 1, 0, (long)&t); } while (rc == -4);
    return rc; /* clock_nanosleep_time64(CLOCK_MONOTONIC, 0, &t, NULL) */
}

struct spi_transfer {
    u64 tx, rx;
    u32 len, speed;
    unsigned short delay;
    u8 bits, cs_change, tx_nbits, rx_nbits, word_delay, pad;
};
_Static_assert(sizeof(struct spi_transfer) == 32, "Linux SPI UAPI size");

static long transmit(int fd, const u8 *data)
{
    struct spi_transfer t = {
        .tx = (u32)data, .rx = 0, .len = 16, .speed = 3200000,
        .delay = 0, .bits = 8, .cs_change = 0, .tx_nbits = 0,
        .rx_nbits = 0, .word_delay = 0, .pad = 0
    };
    long rc = sys3(29, fd, 0x40206b00, (long)&t); /* SPI_IOC_MESSAGE(1) */
    return rc == 16 ? 0 : (rc < 0 ? rc : -5);
}

static void encode(u8 frame[16], unsigned r, unsigned g, unsigned b)
{
    const u8 grb[3] = {g, r, b};
    unsigned out = 0;
    for (unsigned c = 0; c < 3; c++)
        for (int bit = 7; bit >= 1; bit -= 2)
            frame[out++] = ((grb[c] & (1u << bit)) ? 0xe0 : 0x80) |
                           ((grb[c] & (1u << (bit - 1))) ? 0x0e : 0x08);
    while (out < 16) frame[out++] = 0;
}

int main(int argc, char **argv)
{
    if (argc == 2 && eq(argv[1], "--self-test")) {
        u8 frame[16];
        /* Exhaustively decode every channel value and check GRB placement. */
        for (unsigned n = 0; n < 256; n++) {
            unsigned colors[3] = {255 - n, n, n ^ 0x55};
            encode(frame, colors[1], colors[0], colors[2]);
            for (unsigned c = 0; c < 3; c++) {
                unsigned decoded = 0;
                for (unsigned k = 0; k < 8; k++) {
                    unsigned nibble = (frame[c * 4 + k / 2] >> ((k % 2) ? 0 : 4)) & 15;
                    if (nibble != 8 && nibble != 14) return fail("encoding symbol", -22);
                    decoded = (decoded << 1) | (nibble == 14);
                }
                if (decoded != colors[c]) return fail("GRB order", -22);
            }
            for (unsigned k = 12; k < 16; k++)
                if (frame[k]) return fail("low tail", -22);
        }
        if (byte_arg("256") != -1 || byte_arg("-1") != -1 ||
            byte_arg("") != -1 || byte_arg("x") != -1 ||
            byte_arg("255") != 255 || byte_arg("0") != 0)
            return fail("argument bounds", -22);
        say("PASS: 256 GRB encoding vectors, low tails, argument bounds\n");
        return 0;
    }
    int r = 0, g = 0, b = 0;
    if (argc == 2 && eq(argv[1], "red")) r = 64;
    else if (argc == 2 && eq(argv[1], "green")) g = 64;
    else if (argc == 2 && eq(argv[1], "blue")) b = 64;
    else if (argc == 2 && eq(argv[1], "white")) r = g = b = 32;
    else if (argc == 2 && eq(argv[1], "off")) { }
    else if (argc == 4 && (r = byte_arg(argv[1])) >= 0 &&
             (g = byte_arg(argv[2])) >= 0 && (b = byte_arg(argv[3])) >= 0) { }
    else {
        say("Usage: rgb-led red|green|blue|white|off\n"
            "       rgb-led R G B     (each 0..255)\n");
        return 2;
    }
    long fd = sys3(56, -100, (long)"/dev/spidev2.0", 2); /* openat O_RDWR */
    if (fd < 0) return fail("open /dev/spidev2.0 (apply rgb-led overlay first)", fd);
    u8 mode = 0;
    long rc = sys3(29, fd, 0x40016b01, (long)&mode); /* SPI_IOC_WR_MODE */
    if (rc < 0) { sys3(57, fd, 0, 0); return fail("SPI mode", rc); }
    u8 frame[16];
    for (unsigned i = 0; i < 16; i++) frame[i] = 0;
    rc = transmit(fd, frame); /* Force MOSI low before the latch interval. */
    if (rc == 0) rc = reset_wait();
    if (rc != 0) { sys3(57, fd, 0, 0); return fail("initial reset", rc); }
    encode(frame, r, g, b);
    rc = transmit(fd, frame); /* One 16-byte FIFO transfer, no chunk boundary. */
    if (rc == 0) rc = reset_wait();
    sys3(57, fd, 0, 0);
    if (rc != 0) return fail("LED frame/reset", rc);
    say("Sent RGB "); number(r); say(" "); number(g); say(" "); number(b);
    say(" via Linux GPSPI2 -> GPIO60\n");
    return 0;
}

__asm__(".global _start\n"
        "_start:\n"
        "lw a0, 0(sp)\n"
        "addi a1, sp, 4\n"
        "call main\n"
        "li a7, 93\n"
        "ecall\n"
        "1: j 1b\n");
