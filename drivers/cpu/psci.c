#include "psci.h"

static inline int64_t arm_smc(uint64_t func_id, uint64_t arg0, uint64_t arg1, uint64_t arg2) {
    register uint64_t r0 __asm__("x0") = func_id;
    register uint64_t r1 __asm__("x1") = arg0;
    register uint64_t r2 __asm__("x2") = arg1;
    register uint64_t r3 __asm__("x3") = arg2;

    __asm__ volatile(
        "smc #0\n"
        : "+r"(r0)
        : "r"(r1), "r"(r2), "r"(r3)
        : "memory"
    );
    return (int64_t)r0;
}

int32_t psci_cpu_on(uint64_t mpidr, uint64_t entry_point_address, uint64_t context_id) {
    return (int32_t)arm_smc(PSCI_FN_CPU_ON, mpidr, entry_point_address, context_id);
}

int32_t psci_cpu_off(void) {
    return (int32_t)arm_smc(PSCI_FN_CPU_OFF, 0, 0, 0);
}

void psci_system_reset(void) {
    arm_smc(PSCI_FN_SYSTEM_RESET, 0, 0, 0);
    while (1) {
        __asm__ volatile("wfe");
    }
}
