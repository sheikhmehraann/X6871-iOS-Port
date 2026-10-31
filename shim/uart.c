#include "uart.h"

static volatile uint32_t *const uart_reg = (volatile uint32_t *)MT6895_UART0_BASE;

void uart_init(void) {
    /* LK bootloader already configured the baudrate and pinmux.
     * We ensure FIFO and transmitter states are active.
     */
}

void uart_putc(char c) {
    if (c == '\n') {
        uart_putc('\r');
    }
    volatile uint32_t *lsr = (volatile uint32_t *)UART_LSR;
    while (!(*lsr & UART_LSR_THRE)) {
        __asm__ volatile("nop");
    }
    volatile uint32_t *thr = (volatile uint32_t *)UART_THR;
    *thr = (uint32_t)(uint8_t)c;
}

void uart_puts(const char *s) {
    while (*s) {
        uart_putc(*s++);
    }
}

void uart_puthex(uint64_t val) {
    uart_puts("0x");
    for (int i = 60; i >= 0; i -= 4) {
        uint8_t nibble = (val >> i) & 0xF;
        uart_putc(nibble < 10 ? ('0' + nibble) : ('a' + (nibble - 10)));
    }
}
