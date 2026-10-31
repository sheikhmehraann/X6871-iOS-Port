/*
 * start.S: ARM64 Low-Level Entry Point for X6871 Boot Shim
 */

.section ".text.boot", "ax"
.global _start

_start:
    /* Mask all asynchronous interrupts (DAIF) */
    msr daifset, #0xf

    /* Check CurrentEL: if in EL2, drop to EL1 or proceed */
    mrs x4, CurrentEL
    lsr x4, x4, #2
    cmp x4, #1
    b.eq 1f

    /* In EL2: configure HCR_EL2 and return to EL1 */
    mov x5, #(1 << 31) /* RW = 1 (AArch64 execution state for EL1) */
    msr hcr_el2, x5
    isb

1:
    /* Set up stack pointer pointing into high DRAM buffer */
    ldr x5, =_stack_top
    mov sp, x5

    /* Call shim_main(dtb_phys=x1, kernel_entry=x0) */
    bl shim_main

    /* If execution returns, halt core gracefully */
halt:
    wfe
    b halt

.section ".bss.stack", "aw", @nobits
.align 4
_stack_bottom:
    .space 16384
_stack_top:
