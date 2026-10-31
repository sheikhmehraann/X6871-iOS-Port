#ifndef DRIVER_MTK_UFS_H
#define DRIVER_MTK_UFS_H

#include <stdint.h>

#define MT6895_UFSHCI_BASE      0x112B0000UL

/* Standard UFSHCI Registers */
#define REG_UFSHCI_CAP          (MT6895_UFSHCI_BASE + 0x00) /* Host Capabilities */
#define REG_UFSHCI_VER          (MT6895_UFSHCI_BASE + 0x04) /* Version */
#define REG_UFSHCI_HCS          (MT6895_UFSHCI_BASE + 0x30) /* Host Controller Status */
#define REG_UFSHCI_HCE          (MT6895_UFSHCI_BASE + 0x34) /* Host Controller Enable */
#define REG_UFSHCI_UTRLBA       (MT6895_UFSHCI_BASE + 0x50) /* UTRL Base Address Lower */
#define REG_UFSHCI_UTRLBAU      (MT6895_UFSHCI_BASE + 0x54) /* UTRL Base Address Upper */
#define REG_UFSHCI_UTRLDBR      (MT6895_UFSHCI_BASE + 0x58) /* UTRL Doorbell Register */
#define REG_UFSHCI_UTRLCLR      (MT6895_UFSHCI_BASE + 0x5C) /* UTRL Clear Register */
#define REG_UFSHCI_UTMRLBA      (MT6895_UFSHCI_BASE + 0x70) /* UTMRL Base Address Lower */
#define REG_UFSHCI_UTMRLBAU     (MT6895_UFSHCI_BASE + 0x74) /* UTMRL Base Address Upper */
#define REG_UFSHCI_UTMRLDBR     (MT6895_UFSHCI_BASE + 0x78) /* UTMRL Doorbell */

/* Controller Status Bits */
#define HCS_DP                  (1U << 0)  /* Device Present */
#define HCS_UCRDY               (1U << 3)  /* UFSHCI Ready */
#define HCE_ENABLE              (1U << 0)  /* Enable Controller */

int mtk_ufs_init(void);
int mtk_ufs_read_blocks(uint64_t lba, uint32_t block_count, void *buffer);

#endif /* DRIVER_MTK_UFS_H */
