# XT-AT-PC-RGB-LED v2 firmware
#   make            build for ATtiny84 + ATtiny85 (8 MHz) and ATtiny13A (9.6 MHz)
#   make size       show flash/RAM usage
#
# Fuses (internal oscillator, no clock divider, EEPROM kept on chip erase):
#   ATtiny84:  lfuse 0xE2  hfuse 0xD7  efuse 0xFF
#   ATtiny85:  lfuse 0xE2  hfuse 0xD7  efuse 0xFF
#   ATtiny13A: lfuse 0x7A  hfuse 0xFF

CC = avr-gcc
OBJCOPY = avr-objcopy
CFLAGS = -Os -std=gnu99 -Wall -Wextra -flto -ffunction-sections -fdata-sections
LDFLAGS = -Wl,--gc-sections

all: build/xt_at_pc_rgb_led_attiny84.hex build/xt_at_pc_rgb_led_attiny85.hex build/xt_at_pc_rgb_led_attiny13a.hex

build/xt_at_pc_rgb_led_attiny84.elf: main.c config.h | build
	$(CC) $(CFLAGS) -mmcu=attiny84 -DF_CPU=8000000UL $(LDFLAGS) -o $@ main.c

build/xt_at_pc_rgb_led_attiny85.elf: main.c config.h | build
	$(CC) $(CFLAGS) -mmcu=attiny85 -DF_CPU=8000000UL $(LDFLAGS) -o $@ main.c

build/xt_at_pc_rgb_led_attiny13a.elf: main.c config.h | build
	$(CC) $(CFLAGS) -mmcu=attiny13a -DF_CPU=9600000UL $(LDFLAGS) -o $@ main.c

build/%.hex: build/%.elf
	$(OBJCOPY) -O ihex -R .eeprom $< $@

build:
	mkdir -p build

size: all
	avr-size --format=avr --mcu=attiny84 build/xt_at_pc_rgb_led_attiny84.elf
	avr-size --format=avr --mcu=attiny85 build/xt_at_pc_rgb_led_attiny85.elf
	avr-size --format=avr --mcu=attiny13a build/xt_at_pc_rgb_led_attiny13a.elf

clean:
	rm -rf build

.PHONY: all size clean
