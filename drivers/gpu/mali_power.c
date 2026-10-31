#include "mali_valhall.h"

int mali_power_on(struct MaliGpuDevice *dev) {
    if (!dev) return -1;

    /* Stage 1: Power On Sequence via MTCMOS & PWRAP
     * On MT6895, the GPU power domain (MFG) is gated by SPM / MTCMOS.
     */
    dev->current_stage = MALI_STAGE_1_POWER_ON;

    /* Stage 2: Register access verification */
    volatile uint32_t *gpu_id_reg = (volatile uint32_t *)MALI_REG_GPU_ID;
    dev->gpu_id = *gpu_id_reg;
    dev->current_stage = MALI_STAGE_2_REGISTER_ACCESS;

    return 0;
}

uint32_t mali_read_id(void) {
    volatile uint32_t *gpu_id_reg = (volatile uint32_t *)MALI_REG_GPU_ID;
    return *gpu_id_reg;
}
