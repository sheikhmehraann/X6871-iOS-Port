#include "dsi_display.h"

void display_get_config(struct FramebufferConfig *cfg) {
    if (!cfg) return;
    cfg->width = PANEL_WIDTH;
    cfg->height = PANEL_HEIGHT;
    cfg->bpp = PANEL_BPP;
    cfg->pitch = PANEL_WIDTH * (PANEL_BPP / 8);
    cfg->base_address = FRAMEBUFFER_PHYS_BASE;
}

void display_fill_rect(uint32_t x, uint32_t y, uint32_t w, uint32_t h, uint32_t color) {
    volatile uint32_t *fb = (volatile uint32_t *)FRAMEBUFFER_PHYS_BASE;
    for (uint32_t j = y; j < y + h && j < PANEL_HEIGHT; j++) {
        for (uint32_t i = x; i < x + w && i < PANEL_WIDTH; i++) {
            fb[j * PANEL_WIDTH + i] = color;
        }
    }
}
