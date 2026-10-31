#ifndef _XNU_MT6895_PLATFORM_H_
#define _XNU_MT6895_PLATFORM_H_

#include <stdint.h>

/* MediaTek Dimensity 8200 Ultimate (MT6895) Platform Definitions */
#define MT6895_PLATFORM_NAME    "MT6895"
#define MT6895_BOARD_NAME       "X6871"
#define MT6895_TARGET_IDENTITY  "D22AP"

/* Memory Layout */
#define MT6895_DRAM_PHYS_BASE   0x40000000ULL
#define MT6895_DRAM_SIZE        0x200000000ULL /* 8GB */

/* ARM GIC-600 Generic Interrupt Controller v3 */
#define MT6895_GICD_BASE        0x0C000000ULL  /* Distributor */
#define MT6895_GICR_BASE        0x0C040000ULL  /* Redistributor */
#define MT6895_GICC_BASE        0x0C400000ULL  /* CPU Interface */

/* UART Serial Console */
#define MT6895_UART0_BASE       0x11002000ULL
#define MT6895_UART_BAUDRATE    921600

/* Storage (UFS 3.1) */
#define MT6895_UFSHCI_BASE      0x112B0000ULL

/* Display & Framebuffer (Raydium RM69220 144Hz AMOLED) */
#define MT6895_DSI_BASE         0x14017000ULL
#define MT6895_FB_PHYS_BASE     0x70000000ULL
#define MT6895_FB_WIDTH         1080
#define MT6895_FB_HEIGHT        2436
#define MT6895_FB_BPP           32
#define MT6895_FB_STRIDE        (MT6895_FB_WIDTH * 4)

/* GPU (ARM Mali-G610 MC6 Valhall v10) */
#define MT6895_MALI_BASE        0x13000000ULL

/* Watchdog (TOPRGU) */
#define MT6895_TOPRGU_BASE      0x10007000ULL

void mt6895_platform_early_init(void);
void mt6895_uart_putc(char c);
void mt6895_uart_puts(const char *s);
void mt6895_watchdog_ping(void);

#endif /* _XNU_MT6895_PLATFORM_H_ */
