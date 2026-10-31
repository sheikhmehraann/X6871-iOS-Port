#include "mmu.h"

/* 4KB Page Tables aligned to 4KB */
__attribute__((aligned(4096))) static uint64_t l1_table[512];
__attribute__((aligned(4096))) static uint64_t l2_table_dram[512];

void mmu_setup(void) {
    /* 1. Map lower 1GB (0x00000000 - 0x40000000) as Device-nGnRE MMIO */
    l1_table[0] = (0x00000000UL) | MMU_DESC_BLOCK | MMU_AF | MMU_ATTR_DEVICE;

    /* 2. Map DRAM (0x40000000 onwards) via Level 2 table (2MB blocks) or 1GB blocks */
    for (uint64_t i = 1; i < 8; i++) {
        uint64_t phys = i * BLOCK_SIZE_1GB;
        l1_table[i] = phys | MMU_DESC_BLOCK | MMU_AF | MMU_SH_INNER | MMU_ATTR_NORMAL;
    }

    /* Configure MAIR_EL1:
     * Attr0: 0x04 (Device-nGnRE)
     * Attr1: 0xFF (Normal Inner/Outer Write-Back Non-Transient)
     */
    uint64_t mair = (0x04UL << 0) | (0xFFUL << 8);
    __asm__ volatile("msr mair_el1, %0" : : "r"(mair));

    /* Configure TCR_EL1:
     * T0SZ=25 (39-bit VA space), 4KB granule, Inner/Outer WB Cacheable, Inner Shareable
     */
    uint64_t tcr = (25UL << 0) | (3UL << 8) | (1UL << 10) | (1UL << 12) | (2UL << 32);
    __asm__ volatile("msr tcr_el1, %0" : : "r"(tcr));

    /* Set TTBR0_EL1 to point to l1_table */
    uint64_t ttbr0 = (uint64_t)l1_table;
    __asm__ volatile("msr ttbr0_el1, %0" : : "r"(ttbr0));
    __asm__ volatile("isb");
}
