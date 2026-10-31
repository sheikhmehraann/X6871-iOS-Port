// Board definition for MediaTek Dimensity 8200 (MT6895) - Infinix GT 20 Pro (X6871)
// Target Architecture: ARMv8.2-A (4x Cortex-A78 + 4x Cortex-A55)

#ifndef _MT6895_BOARD_H_
#define _MT6895_BOARD_H_

// Physical DRAM Topology
#define PHYSICAL_RAM_BASE       0x40000000ULL      // DRAM Start Base Address
#define PHYSICAL_RAM_SIZE       0x200000000ULL     // 8GB LPDDR5 Address Space

// ARM Generic Interrupt Controller v3 (GIC-600)
#define MT6895_GICD_BASE        0x0C000000ULL      // GIC Distributor Physical Address
#define MT6895_GICR_BASE        0x0C040000ULL      // GIC Redistributor Physical Address

// MediaTek High-Speed UART0 (Serial Console Output)
#define MT6895_UART0_BASE       0x11002000ULL
#define MT6895_UART_BAUDRATE    921600

// Display Framebuffer Parameters (Infinix GT 20 Pro 144Hz AMOLED Panel)
#define FB_PHYSICAL_BASE        0x70000000ULL      // Reserved LK Framebuffer
#define FB_WIDTH                1080
#define FB_HEIGHT               2436
#define FB_BPP                  32                 // ARGB8888
#define FB_STRIDE               (FB_WIDTH * 4)

// Apple Darwin Machine Emulation Target
#define DARWIN_TARGET_MODEL     "D22AP"            // iPhone X Platform ID
#define DARWIN_SOC_COMPATIBLE   "Apple,A11"        // Non-PAC Architecture Compatibility

#endif // _MT6895_BOARD_H_
