#include "types.h"
#include "apple_boot.h"
#include "uart.h"
#include "mmu.h"

#define MT6895_TOPRGU_BASE   0x10007000UL
#define WDT_MODE             (volatile uint32_t *)(MT6895_TOPRGU_BASE + 0x00)
#define WDT_RESTART          (volatile uint32_t *)(MT6895_TOPRGU_BASE + 0x08)
#define WDT_MODE_KEY         (0x22000000)
#define WDT_RESTART_KEY      (0x1971)

static struct boot_args g_boot_args __attribute__((aligned(4096)));

static void watchdog_disable(void) {
    /* Disable MTK Toprgu hardware watchdog to prevent reset during early XNU boot */
    *WDT_RESTART = WDT_RESTART_KEY;
    *WDT_MODE = WDT_MODE_KEY;
}

static void my_strncpy(char *dst, const char *src, int n) {
    int i = 0;
    while (i < n - 1 && src[i] != '\0') {
        dst[i] = src[i];
        i++;
    }
    dst[i] = '\0';
}

void shim_main(uint64_t dtb_phys, uint64_t kernel_entry) {
    uart_init();
    uart_puts("\n=======================================================\n");
    uart_puts("   X6871 Darwin XNU Boot Shim (MediaTek Dimensity 8200)\n");
    uart_puts("=======================================================\n");

    uart_puts("[*] Disabling MediaTek TOPRGU Watchdog...\n");
    watchdog_disable();

    uart_puts("[*] Setting up initial ARM64 MMU Translation Tables...\n");
    mmu_setup();

    if (dtb_phys == 0) {
        dtb_phys = 0x66f00000UL; /* Default LK ramdisk offset */
    }

    uart_puts("[*] Locating Apple DeviceTree at physical base: ");
    uart_puthex(dtb_phys);
    uart_puts("\n");

    /* Populate Apple boot_args */
    g_boot_args.Revision = BOOT_ARGS_REVISION;
    g_boot_args.Version = BOOT_ARGS_VERSION;
    g_boot_args.virtBase = 0xFFFFFFF007004000UL;
    g_boot_args.physBase = 0x40000000UL;
    g_boot_args.memSize  = 0x200000000UL; /* 8GB */
    g_boot_args.topOfKernelData = 0x44000000UL;

    /* Video Framebuffer Configuration */
    g_boot_args.video.v_baseAddr = 0x70000000UL;
    g_boot_args.video.v_display  = 1;
    g_boot_args.video.v_width    = 1080;
    g_boot_args.video.v_height   = 2436;
    g_boot_args.video.v_depth    = 32;
    g_boot_args.video.v_rowBytes = 1080 * 4;

    g_boot_args.machineType = 0x44323241; /* "D22A" */
    g_boot_args.deviceTreeP = dtb_phys;
    g_boot_args.deviceTreeLength = 4096;

    my_strncpy(
        g_boot_args.CommandLine,
        "-v debug=0x14e keepsyms=1 amfi_get_out_of_my_way=1 cs_enforcement_disable=1 serial=3 cpus=1",
        BOOT_LINE_LENGTH
    );

    uart_puts("[+] Boot arguments populated:\n");
    uart_puts("    Cmdline: ");
    uart_puts(g_boot_args.CommandLine);
    uart_puts("\n");
    uart_puts("    Framebuffer: 1080x2436 @ 32bpp at ");
    uart_puthex(g_boot_args.video.v_baseAddr);
    uart_puts("\n");

    if (kernel_entry == 0) {
        uart_puts("[*] Shim verification mode (standby). Returning to loader.\n");
        return;
    }

    uart_puts("[*] Transferring execution to Darwin XNU mach_kernel at: ");
    uart_puthex(kernel_entry);
    uart_puts("\n\n");

    /* Function pointer to XNU entry: typedef void (*xnu_entry_t)(struct boot_args *); */
    typedef void (*xnu_entry_t)(struct boot_args *);
    xnu_entry_t xnu_entry = (xnu_entry_t)kernel_entry;
    xnu_entry(&g_boot_args);
}
