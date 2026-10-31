#ifndef DRIVER_MALI_VALHALL_H
#define DRIVER_MALI_VALHALL_H

#include <stdint.h>

#define MT6895_MALI_BASE        0x13000000UL

/* Valhall GPU Architecture Identification Registers */
#define MALI_REG_GPU_ID         (MT6895_MALI_BASE + 0x0000)
#define MALI_REG_L2_FEATURES    (MT6895_MALI_BASE + 0x0004)
#define MALI_REG_SUSPEND_BUF    (MT6895_MALI_BASE + 0x0008)
#define MALI_REG_TILER_FEATURES (MT6895_MALI_BASE + 0x000C)
#define MALI_REG_MEM_FEATURES   (MT6895_MALI_BASE + 0x0010)
#define MALI_REG_MMU_FEATURES   (MT6895_MALI_BASE + 0x0014)
#define MALI_REG_AS_PRESENT     (MT6895_MALI_BASE + 0x0018)
#define MALI_REG_JS_PRESENT     (MT6895_MALI_BASE + 0x001C)

/* GPU Control & Status */
#define MALI_REG_GPU_IRQ_RAW    (MT6895_MALI_BASE + 0x0020)
#define MALI_REG_GPU_IRQ_CLEAR  (MT6895_MALI_BASE + 0x0024)
#define MALI_REG_GPU_IRQ_MASK   (MT6895_MALI_BASE + 0x0028)
#define MALI_REG_GPU_IRQ_STATUS (MT6895_MALI_BASE + 0x002C)

/* Power Management State Control */
#define MALI_REG_PWR_CONTROL    (MT6895_MALI_BASE + 0x0030)
#define MALI_REG_PWR_STATUS     (MT6895_MALI_BASE + 0x0034)

/* 7 Validation Stages for Mali-G610 MC6 Enablement */
enum MaliValidationStage {
    MALI_STAGE_0_UNINITIALIZED = 0,
    MALI_STAGE_1_POWER_ON = 1,
    MALI_STAGE_2_REGISTER_ACCESS = 2,
    MALI_STAGE_3_MEMORY_ALLOCATION = 3,
    MALI_STAGE_4_COMMAND_SUBMISSION = 4,
    MALI_STAGE_5_JOB_COMPLETION = 5,
    MALI_STAGE_6_RENDERED_PIXELS = 6,
    MALI_STAGE_7_COREANIMATION = 7
};

struct MaliGpuDevice {
    uint32_t gpu_id;
    uint32_t num_cores;
    uint32_t l2_slices;
    enum MaliValidationStage current_stage;
};

int mali_power_on(struct MaliGpuDevice *dev);
uint32_t mali_read_id(void);

#endif /* DRIVER_MALI_VALHALL_H */
