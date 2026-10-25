/*
 * XT-AT-PC-RGB-LED v2 - configuration layout and defaults
 * Copyright (C) 2026 Stefan Fambach (SteFam), https://www.fambach.net
 * License: PolyForm Noncommercial 1.0.0, see ../LICENSE.md
 */
#ifndef CONFIG_H
#define CONFIG_H

#include <stdint.h>

#define CONFIG_MAGIC   0xA5
#define CONFIG_VERSION 2

enum colour_order { ORDER_GRB = 0, ORDER_RGB = 1 };
enum turbo_mode { TURBO_REPLACE = 0, TURBO_MIX = 1 };
enum rgb_output { RGB_NONE = 0, RGB_COMMON_ANODE = 1, RGB_COMMON_CATHODE = 2 };

/* Stored at EEPROM address 0. tools/make_eeprom.py writes the same layout. */
struct config {
    uint8_t magic;
    uint8_t version;
    uint8_t order;       /* enum colour_order */
    uint8_t led_count;   /* LEDs in the chain, all show the same colour */
    uint8_t brightness;  /* 0..255, scales all colours */
    uint8_t hdd_hold;    /* minimum HDD colour time in 10 ms steps */
    uint8_t turbo_mode;  /* enum turbo_mode */
    uint8_t power[3];    /* R, G, B */
    uint8_t turbo[3];
    uint8_t hdd[3];
    uint8_t rgb_output;  /* enum rgb_output, plain RGB LED output (ATtiny84 only) */
};

/* Used when the EEPROM is empty or carries an unknown version. */
#define CONFIG_DEFAULTS { \
    CONFIG_MAGIC, CONFIG_VERSION, ORDER_GRB, 1, 128, 5, TURBO_REPLACE, \
    { 0, 255, 0 }, { 255, 0, 0 }, { 0, 0, 255 }, RGB_COMMON_ANODE }

#endif
