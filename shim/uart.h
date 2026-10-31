#ifndef SHIM_UART_H
#define SHIM_UART_H

#include "types.h"

#define MT6895_UART0_BASE 0x11002000UL

/* MTK 16550 Register Offsets */
#define UART_RBR (MT6895_UART0_BASE + 0x00) /* Receiver Buffer */
#define UART_THR (MT6895_UART0_BASE + 0x00) /* Transmitter Holding */
#define UART_LSR (MT6895_UART0_BASE + 0x14) /* Line Status Register */
#define UART_LSR_THRE 0x20                  /* Transmit Holding Register Empty */

void uart_init(void);
void uart_putc(char c);
void uart_puts(const char *s);
void uart_puthex(uint64_t val);

#endif /* SHIM_UART_H */
