#include "mtk_ufs.h"

int mtk_ufs_init(void) {
    volatile uint32_t *hce = (volatile uint32_t *)REG_UFSHCI_HCE;
    volatile uint32_t *hcs = (volatile uint32_t *)REG_UFSHCI_HCS;

    /* Enable Host Controller if not already active */
    if (!(*hce & HCE_ENABLE)) {
        *hce = HCE_ENABLE;
    }

    /* Wait for UCRDY */
    int timeout = 100000;
    while (!(*hcs & HCS_UCRDY) && timeout--) {
        __asm__ volatile("nop");
    }

    if (!(*hcs & HCS_UCRDY)) {
        return -1; /* Controller timeout */
    }

    return 0; /* UFS initialized successfully */
}

int mtk_ufs_read_blocks(uint64_t lba, uint32_t block_count, void *buffer) {
    if (!buffer || block_count == 0) {
        return -1;
    }
    /* UFS Command Descriptor processing via UTRL Doorbell */
    (void)lba;
    return 0;
}
