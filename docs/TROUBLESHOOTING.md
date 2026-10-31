# Troubleshooting & Diagnostics Guide

---

## 1. Fastboot Device Detection & Bootloader Unlock

### Symptom: `fastboot devices` returns blank
- Ensure you have installed the MediaTek USB VCOM / Android Bootloader drivers.
- Verify USB cable connects directly to a high-speed motherboard port (avoid unpowered USB hubs).

### Symptom: `fastboot boot` fails with `FAILED (remote: 'not allowed in locked state')`
- The Infinix GT 20 Pro requires an unlocked bootloader to execute custom kernel payloads.
- Run:
  ```bash
  fastboot flashing unlock
  ```
- Confirm the prompt on the device screen by pressing Volume Up.

---

## 2. Kernel Boot Panics & Diagnostics

### Symptom: Device boots to black screen and reboots after 20-30 seconds
- **Root Cause:** MediaTek TOPRGU hardware watchdog timer fired.
- **Remedy:** Ensure the boot shim executes `watchdog_disable()` at physical address `0x10007000`:
  ```c
  *(volatile uint32_t *)0x10007008 = 0x1971;     /* Ping */
  *(volatile uint32_t *)0x10007000 = 0x22000000; /* Mode key */
  ```

### Symptom: `panic: "Unable to find Driver for this platform: \"D22AP\""`
- **Root Cause:** The Apple DeviceTree passed at `0x66F00000` is corrupted or not recognized by XNU's Platform Expert (`IOPlatformExpert`).
- **Remedy:** Regenerate `DeviceTree.bin` using [tools/firmware/build_devicetree.py](file:///tools/firmware/build_devicetree.py) and confirm `model` and `target-type` are set to `D22AP`.

---

## 3. Serial Debug Console (UART0)

When diagnosing early kernel hangs, solder a 1.8V UART FTDI adapter to the test points or read the high-speed console output:
- **Base Register:** `0x11002000`
- **Baud Rate:** `921600` (or `115200` depending on Little Kernel configuration)
- **Data Bits:** 8, Parity: None, Stop Bits: 1
