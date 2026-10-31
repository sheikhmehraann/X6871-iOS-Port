#include "mt6895_platform.h"

void mt6895_uart_putc(char c) {
    volatile uint32_t *lsr = (volatile uint32_t *)(MT6895_UART0_BASE + 0x14);
    volatile uint32_t *thr = (volatile uint32_t *)(MT6895_UART0_BASE + 0x00);

    if (c == '\n') {
        mt6895_uart_putc('\r');
    }

    while (!(*lsr & 0x20)) {
        __asm__ volatile("nop");
    }
    *thr = (uint32_t)(uint8_t)c;
}

void mt6895_uart_puts(const char *s) {
    while (*s) {
        mt6895_uart_putc(*s++);
    }
}

void mt6895_watchdog_ping(void) {
    volatile uint32_t *wdt_restart = (volatile uint32_t *)(MT6895_TOPRGU_BASE + 0x08);
    *wdt_restart = 0x1971;
}

void mt6895_platform_early_init(void) {
    mt6895_watchdog_ping();
    mt6895_uart_puts("\n[XNU:MT6895] Apple Darwin Platform Initialized for Infinix GT 20 Pro\n");
    mt6895_uart_puts("[XNU:MT6895] GIC-600 Distributor: 0x0C000000, Redistributor: 0x0C040000\n");
    mt6895_uart_puts("[XNU:MT6895] Display Panel: 1080x2436 @ 32bpp FB at 0x70000000\n");
}
