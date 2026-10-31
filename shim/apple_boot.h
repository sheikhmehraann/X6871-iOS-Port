#ifndef SHIM_APPLE_BOOT_H
#define SHIM_APPLE_BOOT_H

#include "types.h"

#define BOOT_ARGS_REVISION 1
#define BOOT_ARGS_VERSION 2

#define BOOT_LINE_LENGTH 1024

struct Boot_Video {
    uint64_t v_baseAddr;   /* Base address of video memory */
    uint64_t v_display;    /* Display identifier */
    uint64_t v_rowBytes;   /* Number of bytes per row */
    uint64_t v_width;      /* Width in pixels */
    uint64_t v_height;     /* Height in pixels */
    uint64_t v_depth;      /* Color depth (bits per pixel) */
};

struct boot_args {
    uint16_t Revision;           /* Boot arguments revision */
    uint16_t Version;            /* Boot arguments version */
    uint64_t virtBase;           /* Virtual base address of kernel */
    uint64_t physBase;           /* Physical base address of DRAM (0x40000000) */
    uint64_t memSize;            /* Total DRAM size in bytes (8GB) */
    uint64_t topOfKernelData;    /* Highest physical address of kernel data */
    struct Boot_Video video;     /* Framebuffer configuration */
    uint32_t machineType;        /* Platform machine type */
    uint64_t deviceTreeP;        /* Physical address of Apple DeviceTree */
    uint32_t deviceTreeLength;   /* Length of Apple DeviceTree in bytes */
    char CommandLine[BOOT_LINE_LENGTH]; /* Kernel command line string */
};

#endif /* SHIM_APPLE_BOOT_H */
