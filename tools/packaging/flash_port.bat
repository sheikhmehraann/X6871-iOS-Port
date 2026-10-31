@echo off
REM ============================================================================
REM Flash Port Script: Fastboot RAM Deployment for Infinix GT 20 Pro (X6871 / MT6895)
REM Non-destructive: Boots xnu_boot.img directly into DRAM without flashing flash storage
REM ============================================================================
echo [X6871-Darwin] Fastboot RAM Deployment Staging...

where fastboot >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [!] Error: fastboot executable not found in PATH!
    pause
    exit /b 1
)

echo [*] Checking connected Fastboot devices...
fastboot devices

echo [*] Verifying Bootloader Unlock Status...
fastboot getvar unlocked 2>&1 | findstr /i "yes true" >nul
if %ERRORLEVEL% neq 0 (
    echo [!] WARNING: Bootloader may be locked!
    echo [!] Unlocking is required for unsigned Darwin kernel booting:
    echo     fastboot flashing unlock
)

echo [*] Booting XNU Kernel into RAM (Non-Destructive Test)...
if exist "output\xnu_boot.img" (
    fastboot boot output\xnu_boot.img
) else if exist "..\output\xnu_boot.img" (
    fastboot boot ..\output\xnu_boot.img
) else if exist "xnu_boot.img" (
    fastboot boot xnu_boot.img
) else (
    echo [!] Error: xnu_boot.img not found! Run tools\packaging\package_boot.py first.
)

echo [OK] Deployment sequence finished.
pause
