#ifndef DRIVER_TOUCH_FT3683G_H
#define DRIVER_TOUCH_FT3683G_H

#include <stdint.h>

#define MT6895_I2C0_BASE    0x11D00000UL
#define FT3683G_I2C_ADDR    0x38

/* FocalTech Protocol Registers */
#define FT_REG_DEV_MODE     0x00
#define FT_REG_GEST_ID      0x01
#define FT_REG_TD_STATUS    0x02
#define FT_REG_TOUCH1_XH    0x03
#define FT_REG_TOUCH1_XL    0x04
#define FT_REG_TOUCH1_YH    0x05
#define FT_REG_TOUCH1_YL    0x06

struct TouchPoint {
    uint16_t x;
    uint16_t y;
    uint8_t  event_flag; /* 0: Press Down, 1: Lift Up, 2: Contact, 3: No Event */
    uint8_t  id;
};

int touch_init(void);
int touch_read_points(struct TouchPoint *points, int max_points);

#endif /* DRIVER_TOUCH_FT3683G_H */
