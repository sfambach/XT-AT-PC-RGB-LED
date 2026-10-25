/*
 * XT-AT-PC-RGB-LED v2 - one addressable RGB LED for power, turbo and HDD
 * Copyright (C) 2026 Stefan Fambach (SteFam), https://www.fambach.net
 * License: PolyForm Noncommercial 1.0.0, see ../LICENSE.md
 *
 * ATtiny85 @ 8 MHz or ATtiny13A @ 9.6 MHz, internal oscillator.
 *   PB0  LED data (WS2812 / APA106 / PL9823)
 *   PB1  HDD header pin A      PB2  HDD header pin B
 *   PB3  TURBO header pin A    PB4  TURBO header pin B
 *
 * Each header gets a load resistor between its two pins. A signal is active
 * when its two pins differ, so neither the header polarity nor the switching
 * side (low or high) has to be known in advance.
 */
#include <avr/io.h>
#include <avr/eeprom.h>
#include <avr/interrupt.h>
#include <util/delay.h>
#include "config.h"

#define LED_BIT   _BV(PB0)
#define INPUTS    (_BV(PB1) | _BV(PB2) | _BV(PB3) | _BV(PB4))
#define REFRESH_MS 500

static struct config cfg;

/* 11 cycles per bit: high 3 cycles for 0, 7 cycles for 1 (8 / 9.6 MHz). */
static void send_byte(uint8_t value, uint8_t hi, uint8_t lo)
{
    uint8_t count = 8;
    __asm__ volatile(
        "1:                 \n\t"
        "out  %[port], %[hi]\n\t"
        "nop                \n\t"
        "sbrs %[val], 7     \n\t"
        "out  %[port], %[lo]\n\t"
        "lsl  %[val]        \n\t"
        "nop                \n\t"
        "nop                \n\t"
        "out  %[port], %[lo]\n\t"
        "dec  %[cnt]        \n\t"
        "brne 1b            \n\t"
        : [val] "+r"(value), [cnt] "+r"(count)
        : [port] "I"(_SFR_IO_ADDR(PORTB)), [hi] "r"(hi), [lo] "r"(lo));
}

static uint8_t scale(uint8_t channel)
{
    return (uint16_t)channel * (cfg.brightness + 1) >> 8;
}

static void show(const uint8_t rgb[3])
{
    uint8_t r = scale(rgb[0]), g = scale(rgb[1]), b = scale(rgb[2]);
    uint8_t first = cfg.order == ORDER_RGB ? r : g;
    uint8_t second = cfg.order == ORDER_RGB ? g : r;
    uint8_t hi = PORTB | LED_BIT, lo = PORTB & ~LED_BIT;

    cli();
    for (uint8_t i = 0; i < cfg.led_count; i++) {
        send_byte(first, hi, lo);
        send_byte(second, hi, lo);
        send_byte(b, hi, lo);
    }
    sei();
    _delay_us(80); /* latch */
}

static void load_config(void)
{
    static const struct config defaults = CONFIG_DEFAULTS;

    eeprom_read_block(&cfg, 0, sizeof cfg);
    if (cfg.magic != CONFIG_MAGIC || cfg.version != CONFIG_VERSION || cfg.led_count == 0)
        cfg = defaults;
}

int main(void)
{
    uint8_t mixed[3], current[3] = { 1, 1, 1 };
    const uint8_t *colour;
    uint16_t hdd_hold = 0, refresh = 0;

    DDRB = LED_BIT;
    PORTB = INPUTS; /* pull-ups keep unconnected header pairs equal */
    load_config();

    for (uint8_t i = 0; i < 3; i++) {
        uint16_t sum = cfg.power[i] + cfg.turbo[i];
        mixed[i] = sum > 255 ? 255 : sum;
    }
    _delay_ms(50);

    for (;;) {
        uint8_t pins = PINB;
        uint8_t hdd = ((pins >> PB1) ^ (pins >> PB2)) & 1;
        uint8_t turbo = ((pins >> PB3) ^ (pins >> PB4)) & 1;

        /* short HDD pulses would be invisible, stretch them */
        if (hdd)
            hdd_hold = cfg.hdd_hold * 10;
        else if (hdd_hold)
            hdd_hold--;

        if (hdd_hold || hdd)
            colour = cfg.hdd;
        else if (turbo)
            colour = cfg.turbo_mode == TURBO_MIX ? mixed : cfg.turbo;
        else
            colour = cfg.power;

        if (colour[0] != current[0] || colour[1] != current[1] ||
            colour[2] != current[2] || ++refresh >= REFRESH_MS) {
            show(colour);
            current[0] = colour[0];
            current[1] = colour[1];
            current[2] = colour[2];
            refresh = 0;
        }
        _delay_ms(1);
    }
}
