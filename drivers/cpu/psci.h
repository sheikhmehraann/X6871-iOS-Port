#ifndef DRIVER_PSCI_H
#define DRIVER_PSCI_H

#include <stdint.h>

/* ARM PSCI SMC Function IDs (ARM DEN 0022D) */
#define PSCI_0_2_FN_BASE            0x84000000
#define PSCI_0_2_FN64_BASE          0xC4000000

#define PSCI_FN_VERSION             (PSCI_0_2_FN_BASE + 0)
#define PSCI_FN_CPU_SUSPEND         (PSCI_0_2_FN64_BASE + 1)
#define PSCI_FN_CPU_OFF             (PSCI_0_2_FN_BASE + 2)
#define PSCI_FN_CPU_ON              (PSCI_0_2_FN64_BASE + 3)
#define PSCI_FN_AFFINITY_INFO       (PSCI_0_2_FN64_BASE + 4)
#define PSCI_FN_SYSTEM_OFF          (PSCI_0_2_FN_BASE + 8)
#define PSCI_FN_SYSTEM_RESET        (PSCI_0_2_FN_BASE + 9)

#define PSCI_RET_SUCCESS            0
#define PSCI_RET_NOT_SUPPORTED      -1
#define PSCI_RET_INVALID_PARAMS     -2
#define PSCI_RET_DENIED             -3
#define PSCI_RET_ALREADY_ON         -4
#define PSCI_RET_ON_PENDING         -5
#define PSCI_RET_INTERNAL_FAILURE   -6

int32_t psci_cpu_on(uint64_t mpidr, uint64_t entry_point_address, uint64_t context_id);
int32_t psci_cpu_off(void);
void psci_system_reset(void);

#endif /* DRIVER_PSCI_H */
