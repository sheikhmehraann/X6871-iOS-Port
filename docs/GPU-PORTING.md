# GPU Porting Strategy: ARM Mali-G610 MC6 (Valhall v10)

This document analyzes the graphics subsystem of the Infinix GT 20 Pro (`X6871`) and outlines the roadmap for genuine iOS hardware graphics acceleration.

---

## 1. Hardware Architecture: Mali-G610 MC6

The MediaTek MT6895 embeds an **ARM Mali-G610 MC6**, based on ARM's **Valhall 3rd Generation (v10)** architecture:
- **Base MMIO Address:** `0x13000000` (Size: 1 MB)
- **Cores:** 6 Execution Engines (EE) / Shader Cores
- **L2 Cache:** 2 slices (512 KB total)
- **Job Submission Interface:** Valhall Hardware Command Queue (CSG - Command Stream Generator)
- **Power Domain:** MediaTek `MFG_TOP` controlled via SPM / MTCMOS and `MT6363` PMIC buck regulator (`VGPU`)
- **Clock Domain:** `TOPCKGEN` PLL `MFG_PLL` (up to 950 MHz)

---

## 2. The 7 Rigorous Validation Stages

To avoid false claims of GPU acceleration (such as treating a powered-on GPU or compiled module as working 3D acceleration), the port strictly enforces 7 independent hardware verification milestones:

```
[ Stage 1: GPU Power-On ]
         │ (MTCMOS MFG domain enabled, VGPU regulator stable)
         ▼
[ Stage 2: Register Access ]
         │ (Read GPU_ID 0x13000000 returns valid Valhall v10 ID)
         ▼
[ Stage 3: Memory Allocation ]
         │ (Unified Memory mapped via AS0..AS3 page tables)
         ▼
[ Stage 4: Command Submission ]
         │ (Job descriptor written to Job Slot / Command Stream)
         ▼
[ Stage 5: Hardware Job Completion ]
         │ (GPU IRQ raised, Job Done status bit asserted)
         ▼
[ Stage 6: Correct Rendered Pixels ]
         │ (Framebuffer readback matches expected test pattern)
         ▼
[ Stage 7: CoreAnimation Presentation ]
         │ (iOS backboardd/SpringBoard renders via Metal shim)
         ▼
    [ Fully Accelerated ]
```

---

## 3. Comparison with HelioDarwin Mali-G57

HelioDarwin implemented experimental graphics on the **Mali-G57 MC2**:
- Mali-G57 is **Valhall 1st Gen (v7)** with Job Manager (JM) ring buffers.
- Mali-G610 is **Valhall 3rd Gen (v10)** which replaces legacy Job Manager with **Command Stream Generation (CSG)** and different job descriptor layouts.
- **Conclusion:** HelioDarwin's `MaliMetal` kernel ABI patches cannot be blindly copied; the driver must adapt to Valhall v10 CSG ring buffers.

---

## 4. Integration Approaches: Mesa Panfrost vs MaliMetal

### Option A: Panfrost / PanVK (Open Source)
- **Status in Mesa:** Panfrost has upstream support for Valhall architectures (Mali-G310, G510, G610).
- **Pros:** Full open-source Vulkan and OpenGL ES implementation without closed blobs.
- **Challenge:** Darwin XNU does not natively provide DRM/KMS. Requires porting Panfrost user-space and an IOKit kernel shim (`IOAccelerator`).

### Option B: MaliMetal UserClient Shim
- Translates Apple Metal API calls (`MTLDevice`, `MTLCommandQueue`) into Mali command streams or Vulkan primitives.
- **Current Milestone:** Stage 2 (Register Identification). Software rasterization is utilized for SpringBoard UI presentation until Stage 6 is verified on physical hardware.
