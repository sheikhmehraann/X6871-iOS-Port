#ifndef SHIM_MMU_H
#define SHIM_MMU_H

#include "types.h"

#define PAGE_SIZE 4096UL
#define BLOCK_SIZE_2MB (2UL * 1024 * 1024)
#define BLOCK_SIZE_1GB (1024UL * 1024 * 1024)

/* Memory attributes */
#define MMU_ATTR_DEVICE (0x0UL << 2)
#define MMU_ATTR_NORMAL (0x1UL << 2)
#define MMU_DESC_BLOCK  0x1UL
#define MMU_DESC_TABLE  0x3UL
#define MMU_DESC_VALID  0x1UL
#define MMU_AF          (1UL << 10) /* Access Flag */
#define MMU_SH_INNER    (3UL << 8)  /* Inner Shareable */

void mmu_setup(void);

#endif /* SHIM_MMU_H */
