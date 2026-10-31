#ifndef DRIVER_PMIC_SPMI_H
#define DRIVER_PMIC_SPMI_H

#include <stdint.h>

#define MT6895_SPMI_BASE        0x1C804000UL
#define MT6895_TOPRGU_BASE      0x10007000UL

/* TOPRGU Watchdog */
#define WDT_MODE_REG            (MT6895_TOPRGU_BASE + 0x00)
#define WDT_LENGTH_REG          (MT6895_TOPRGU_BASE + 0x04)
#define WDT_RESTART_REG         (MT6895_TOPRGU_BASE + 0x08)

void pmic_init(void);
void watchdog_ping(void);
void watchdog_disable_hw(void);

#endif /* DRIVER_PMIC_SPMI_H */
