/*
 * XT-AT-PC-RGB-LED v2 - one RGB LED for power, turbo and HDD
 * Copyright (C) 2026 Stefan Fambach (SteFam), https://www.fambach.net
 * License: PolyForm Noncommercial 1.0.0, see ../LICENSE.md
 *
 * Internal oscillator: ATtiny84 / ATtiny85 @ 8 MHz, ATtiny13A @ 9.6 MHz.
 *
 * ATtiny85 / ATtiny13A (addressable LED only)
 *   PB0 LED data   PB1/PB2 HDD header pins A/B   PB3/PB4 TURBO header pins A/B
 *
 * ATtiny84 (addressable LED and plain RGB LED at the same time)
 *   PB0 LED data   PA0/PA1 HDD header pins A/B   PA2/PA3 TURBO header pins A/B
 *   PB2 (OC0A) red   PA7 (OC0B) green   PA6 (OC1A) blue
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

#define LED_BIT    _BV(PB0)
#define REFRESH_MS 500

#if defined(__AVR_ATtiny84__) || defined(__AVR_ATtiny84A__)
#define HAS_RGB_OUTPUT 1
#define INPUT_PIN  PINA
#define INPUT_PORT PORTA
#define HDD_A PA0
#define HDD_B PA1
#define TURBO_A PA2
#define TURBO_B PA3
#else
#define HAS_RGB_OUTPUT 0
#define INPUT_PIN  PINB
#define INPUT_PORT PORTB
#define HDD_A PB1
#define HDD_B PB2
#define TURBO_A PB3
#define TURBO_B PB4
#endif
#define INPUTS (_BV(HDD_A) | _BV(HDD_B) | _BV(TURBO_A) | _BV(TURBO_B))

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

#if HAS_RGB_OUTPUT
/*
 * Hardware PWM, 8 bit, ~3.9 kHz. Common anode is driven inverted (low = on).
 * A channel at 0 is disconnected from the timer and held at its off level,
 * because fast PWM never reaches a duty of exactly 0.
 */
static void pwm_init(void)
{
    if (cfg.rgb_output == RGB_NONE)
        return;
    if (cfg.rgb_output == RGB_COMMON_ANODE) {
        PORTB |= _BV(PB2);
        PORTA |= _BV(PA7) | _BV(PA6);
    }
    DDRB |= _BV(PB2);
    DDRA |= _BV(PA7) | _BV(PA6);
    TCCR0A = _BV(WGM01) | _BV(WGM00);
    TCCR0B = _BV(CS01);
    TCCR1A = _BV(WGM10);
    TCCR1B = _BV(WGM12) | _BV(CS11);
}

static uint8_t com_bits(uint8_t value, uint8_t com1, uint8_t com0)
{
    if (value == 0)
        return 0;
    return cfg.rgb_output == RGB_COMMON_ANODE ? (com1 | com0) : com1;
}

static void pwm_show(uint8_t r, uint8_t g, uint8_t b)
{
    if (cfg.rgb_output == RGB_NONE)
        return;
    OCR0A = r - 1;
    OCR0B = g - 1;
    OCR1A = b - 1;
    TCCR0A = _BV(WGM01) | _BV(WGM00) |
             com_bits(r, _BV(COM0A1), _BV(COM0A0)) |
             com_bits(g, _BV(COM0B1), _BV(COM0B0));
    TCCR1A = _BV(WGM10) | com_bits(b, _BV(COM1A1), _BV(COM1A0));
}
#endif

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
#if HAS_RGB_OUTPUT
    pwm_show(r, g, b);
#endif
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
    INPUT_PORT = INPUTS; /* pull-ups keep unconnected header pairs equal */
    load_config();
#if HAS_RGB_OUTPUT
    pwm_init();
#endif

    for (uint8_t i = 0; i < 3; i++) {
        uint16_t sum = cfg.power[i] + cfg.turbo[i];
        mixed[i] = sum > 255 ? 255 : sum;
    }
    _delay_ms(50);

    for (;;) {
        uint8_t pins = INPUT_PIN;
        uint8_t hdd = ((pins >> HDD_A) ^ (pins >> HDD_B)) & 1;
        uint8_t turbo = ((pins >> TURBO_A) ^ (pins >> TURBO_B)) & 1;

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
