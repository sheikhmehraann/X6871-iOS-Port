# iOS Userspace Adaptation & Surgery: iOS 16.7.16 Baseline

Our objective is to adapt **genuine Apple iOS userspace**, not an Android GSI skin or launcher recreation.

---

## 1. Baseline Target Firmware

- **Target Device Identity:** iPhone X (`D22AP` / `iPhone10,6`)
- **Firmware Version:** iOS 16.7.16 (`20H350`)
- **IPSW Source:** `iPhone10,6_16.7.16_20H350_Restore.ipsw`
- **Architecture:** ARMv8.2-A without Pointer Authentication Codes (Non-PAC). Matches the instruction set capabilities of the Cortex-A78 / Cortex-A55 cores.

---

## 2. Launchd Neutralization Surgery

Genuine iOS userspace relies on `launchd` (PID 1) to spawn all system daemons. However, standard iOS builds contain watchdog daemons that actively panic the kernel if proprietary Apple hardware is missing.

[launchd_surgery.py](file:///userspace/launchd_surgery.py) neutralizes the following daemons before rootfs mounting:

| Daemon Plist | Default Apple Behavior | Failure on MT6895 Hardware | Action Taken |
| :--- | :--- | :--- | :--- |
| `com.apple.watchdogd.plist` | Monitors Secure Enclave (SEP) heartbeat | Panics kernel after 60s without SEP hardware | **Removed** |
| `com.apple.CommCenter.plist` | Manages Qualcomm/Intel cellular baseband | Bus timeout panic when baseband PCIe is absent | **Removed** |
| `com.apple.basebandd.plist` | Low-level modem firmware IPC | Bootloop on missing IPC channel | **Removed** |
| `com.apple.symptomsd.plist` | Network telemetry & diagnostics | Heavy memory consumption & loop errors | **Removed** |
| `com.apple.wifid.plist` | Apple proprietary Broadcom Wi-Fi stack | MTK Wi-Fi driver incompatible | **Neutralized** |

---

## 3. iCloud Activation Lock Bypass

On initial boot, iOS launches `Setup.app` (Setup Assistant), which queries Apple activation servers with device ECID and ticket. On non-Apple hardware, this fails permanently.

### Neutralization Method
Creating an empty token file at:
```text
/private/var/mobile/Library/Preferences/.SkipSetup
```
This forces `launchd` and `SpringBoard` to treat the setup assistant as already finished, directly launching the home screen interface.

---

## 4. System Services Status

| iOS Subsystem | Underlying Daemon / Framework | Status on X6871 | Strategy |
| :--- | :--- | :--- | :--- |
| **Mach Init & Daemons** | `launchd` | ✅ Functional | Neutralized plists prevent kernel panics |
| **Shared Libraries** | `dyld` / dyld_shared_cache | ✅ Functional | Matches ARM64 non-PAC Mach-O ABI |
| **Window Server** | `backboardd` | ⚠️ In Progress | Uses simple linear framebuffer |
| **Home Screen UI** | `SpringBoard` | ⚠️ In Progress | CPU software rasterizer fallback |
| **Touch Events** | `IOHIDFamily` / `BackBoardServices` | ⚠️ In Progress | Requires I2C FocalTech FT3683G driver |
| **Cellular Voice/Data** | `CommCenter` | ❌ Disabled | Bypassed to prevent panic |
| **Cameras & Face ID** | `mediaserverd` | ❌ Disabled | Proprietary MTK ISP unsupported |
