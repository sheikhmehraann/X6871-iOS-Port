# GitHub Actions Build Infrastructure & Workflows

The entire build, test, and release lifecycle is automated through modular GitHub Actions workflows located in `.github/workflows/`.

---

## 1. Workflow Architecture Map

```
                +------------------------------+
                |    push / tag: v* / dispatch |
                +------------------------------+
                               │
                               ▼
                +------------------------------+
                |         release.yml          |
                |   (Master Pipeline Driver)   |
                +------------------------------+
                               │
            ┌──────────────────┼──────────────────┐
            ▼                  ▼                  ▼
  +------------------+ +----------------+ +------------------+
  |  test_and_validate| |   build_shim   | |  build_userspace  |
  |  (Unit Tests)    | | (ARM64 Cross)  | | (Launchd Surgery)|
  +------------------+ +----------------+ +------------------+
                               │
                               ▼
                +------------------------------+
                |       package_release        |
                |  - Compiles DeviceTree.bin   |
                |  - Packs xnu_boot.img (v4)   |
                |  - Computes SHA-256 Manifest |
                |  - Uploads to GoFile CDN     |
                +------------------------------+
```

---

## 2. Workflows Specification

| Workflow File | Runner OS | Purpose | Key Artifacts |
| :--- | :--- | :--- | :--- |
| **`download-firmware.yml`** | `ubuntu-latest` | Ingests stock ROM from FRBox with Range resuming | None committed; temporary workspace only |
| **`extract-firmware.yml`** | `ubuntu-latest` | Parses scatter, unpacks DTB, and runs region analysis | `configs/device_tree_nodes.json` |
| **`build-xnu.yml`** | `macos-14` | Compiles Apple Darwin XNU 8796 with Xcode 15 / iig | `output/kernel/mach_kernel` |
| **`build-shim.yml`** | `ubuntu-latest` | Compiles freestanding ARM64 boot shim via GNU toolchain | `shim/boot_shim.bin`, `boot_shim.elf` |
| **`build-ios-root.yml`** | `ubuntu-latest` | Tests launchd daemon surgery and `.SkipSetup` creation | Userspace test verification logs |
| **`package-release.yml`** | `ubuntu-latest` | Packages AOSP Header v4 boot image and uploads to GoFile | `xnu_boot.img`, `DeviceTree.bin`, `SHA256SUMS.txt` |
| **`release.yml`** | `ubuntu-latest` | Master CI/CD orchestrator on push to `main` or tag `v*` | Full GitHub Release deployment |

---

## 3. Required GitHub Secrets

Configure these secrets in your repository settings (`Settings -> Secrets and variables -> Actions`):

- **`FRBOX_SHARE_ID`**: FRBox share link ID (Default: `k3NB1w3ZXPg`)
- **`FRBOX_PWD`**: FRBox share link access password (Default: `IE5iju`)
- **`GOFILE_TOKEN`**: GoFile account API token (Optional: guest upload mode is used if omitted)
