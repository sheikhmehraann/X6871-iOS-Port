#ifndef DRIVER_DSI_DISPLAY_H
#define DRIVER_DSI_DISPLAY_H

#include <stdint.h>

#define MT6895_DSI_BASE         0x14017000UL
#define MT6895_DISP_OVL0_BASE   0x14002000UL
#define MT6895_DISP_RDMA0_BASE  0x14006000UL

#define PANEL_WIDTH             1080
#define PANEL_HEIGHT            2436
#define PANEL_BPP               32
#define FRAMEBUFFER_PHYS_BASE   0x70000000UL

struct FramebufferConfig {
    uint32_t width;
    uint32_t height;
    uint32_t bpp;
    uint32_t pitch;
    uint64_t base_address;
};

void display_get_config(struct FramebufferConfig *cfg);
void display_fill_rect(uint32_t x, uint32_t y, uint32_t w, uint32_t h, uint32_t color);

#endif /* DRIVER_DSI_DISPLAY_H */
