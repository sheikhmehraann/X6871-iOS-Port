#include "pmic_spmi.h"

void pmic_init(void) {
    /* SPMI bus configuration */
}

void watchdog_ping(void) {
    volatile uint32_t *wdt_restart = (volatile uint32_t *)WDT_RESTART_REG;
    *wdt_restart = 0x1971;
}

void watchdog_disable_hw(void) {
    volatile uint32_t *wdt_mode = (volatile uint32_t *)WDT_MODE_REG;
    volatile uint32_t *wdt_restart = (volatile uint32_t *)WDT_RESTART_REG;
    *wdt_restart = 0x1971;
    *wdt_mode = 0x22000000;
}
