CROSS_COMPILE ?= aarch64-linux-gnu-
CC      := $(CROSS_COMPILE)gcc
LD      := $(CROSS_COMPILE)ld
OBJCOPY := $(CROSS_COMPILE)objcopy

CFLAGS  := -Wall -Wextra -O2 -nostdlib -nostdinc -fno-builtin -fno-stack-protector -ffreestanding -mcpu=cortex-a78
LDFLAGS := -T link.ld -nostdlib --build-id=none

SRCS_C := main.c uart.c mmu.c
SRCS_S := start.S
OBJS   := $(SRCS_S:.S=.o) $(SRCS_C:.c=.o)

all: boot_shim.bin

boot_shim.elf: $(OBJS) link.ld
	$(LD) $(LDFLAGS) -o $@ $(OBJS)

boot_shim.bin: boot_shim.elf
	$(OBJCOPY) -O binary $< $@
	@echo "[+] Successfully built Boot Shim binary: $@"

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

%.o: %.S
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f *.o *.elf *.bin

.PHONY: all clean
