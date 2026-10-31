/*
 * start.S: ARM64 Low-Level Entry Point for X6871 Boot Shim
 */

.section ".text.boot", "ax"
.global _start

_start:
    /* Mask all asynchronous interrupts (DAIF) */
    msr daifset, #0xf

    /* Check CurrentEL: bits [3:2] */
    mrs x4, CurrentEL
    lsr x4, x4, #2
    cmp x4, #2
    b.ne 1f

    /* In EL2: configure HCR_EL2 (AArch64 EL1 execution state) */
    mov x5, #(1 << 31) /* RW = 1 */
    msr hcr_el2, x5
    isb

    /* Return from EL2 to EL1h with all DAIF interrupts masked */
    mov x5, #0x3c5     /* EL1h (M[3:0]=0101, DAIF masked=1111) */
    msr spsr_el2, x5
    adr x5, 1f
    msr elr_el2, x5
    eret

1:
    /* Set up stack pointer */
    ldr x5, =_stack_top
    mov sp, x5

    /* Zero BSS section */
    ldr x5, =__bss_start
    ldr x6, =__bss_end
2:  cmp x5, x6
    b.ge 3f
    str xzr, [x5], #8
    b 2b
3:

    /* Call shim_main(dtb_phys=x0, kernel_entry=x1) */
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
