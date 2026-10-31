@echo off
setlocal enabledelayedexpansion
title Infinix GT 20 Pro (X6871) - Native iOS ROM 1-Click Flasher
color 0B
cd /d "%~dp0"

echo ===============================================================================
echo        INFINIX GT 20 PRO (X6871 / MT6895) - NATIVE iOS ROM 1-CLICK FLASHER
echo                  Darwin XNU Kernel + iOS 16 Userspace Deployment
echo ===============================================================================
echo.

REM 1. Locate fastboot binary
set "FASTBOOT_BIN="
where fastboot >nul 2>nul
if %ERRORLEVEL% equ 0 (
    set "FASTBOOT_BIN=fastboot"
) else if exist "C:\FastbootFirmwareFlasher\platform-tools\fastboot.exe" (
    set "FASTBOOT_BIN=C:\FastbootFirmwareFlasher\platform-tools\fastboot.exe"
) else if exist "%LOCALAPPDATA%\Android\Sdk\platform-tools\fastboot.exe" (
    set "FASTBOOT_BIN=%LOCALAPPDATA%\Android\Sdk\platform-tools\fastboot.exe"
) else if exist "platform-tools\fastboot.exe" (
    set "FASTBOOT_BIN=platform-tools\fastboot.exe"
) else (
    echo [!] ERROR: Fastboot executable not found!
    echo     Please install Android Platform-Tools or add fastboot.exe to your PATH.
    echo     Download: https://developer.android.com/tools/releases/platform-tools
    echo.
    pause
    exit /b 1
)

echo [*] Fastboot binary located: %FASTBOOT_BIN%
echo.

REM 2. Check connected Fastboot devices
echo [*] Polling for connected device in Fastboot / Bootloader mode...
"%FASTBOOT_BIN%" devices > "%TEMP%\fb_dev.txt" 2>&1
findstr /r "[a-zA-Z0-9]" "%TEMP%\fb_dev.txt" >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [!] WARNING: No device detected in Fastboot mode!
    echo     1. Power off your Infinix GT 20 Pro.
    echo     2. Hold [Volume Down + Power] until the FASTBOOT banner appears.
    echo     3. Connect USB cable to PC.
    echo.
    echo Press any key to continue once connected, or close this window...
    pause >nul
)

echo [*] Querying device bootloader parameters...
"%FASTBOOT_BIN%" getvar product 2>&1
"%FASTBOOT_BIN%" getvar unlocked 2>&1
echo.

:MENU
echo ===============================================================================
echo                             ROM DEPLOYMENT MENU
echo ===============================================================================
echo  [1] Non-Destructive RAM Boot (SAFE - Boots xnu_boot.img in DRAM, leaves ROM intact)
echo  [2] Flash Darwin XNU Boot Partition (fastboot flash boot xnu_boot.img)
echo  [3] Build / Staged iOS RootFS Image (Runs build_ios_rootfs.py)
echo  [4] Flash iOS RootFS to Storage (fastboot flash userdata / dynamic partition)
echo  [5] 1-Click Complete Install (Flash XNU Boot + Flash iOS RootFS + Reboot)
echo  [6] Bootloader Unlock Helper (fastboot flashing unlock)
echo  [7] Query Device Hardware Diagnostics (fastboot getvar all)
echo  [8] Exit
echo ===============================================================================
set /p CHOICE="Select an option [1-8]: "

if "%CHOICE%"=="1" goto OP_BOOT_RAM
if "%CHOICE%"=="2" goto OP_FLASH_BOOT
if "%CHOICE%"=="3" goto OP_BUILD_ROOTFS
if "%CHOICE%"=="4" goto OP_FLASH_ROOTFS
if "%CHOICE%"=="5" goto OP_FULL_INSTALL
if "%CHOICE%"=="6" goto OP_UNLOCK
if "%CHOICE%"=="7" goto OP_DIAG
if "%CHOICE%"=="8" goto OP_EXIT
echo [!] Invalid selection. Please choose 1 to 8.
echo.
goto MENU

:OP_BOOT_RAM
echo.
echo [*] Selected: [1] Non-Destructive DRAM Boot
set "BOOT_IMG="
if exist "xnu_boot.img" set "BOOT_IMG=xnu_boot.img"
if exist "output\xnu_boot.img" set "BOOT_IMG=output\xnu_boot.img"
if exist "..\output\xnu_boot.img" set "BOOT_IMG=..\output\xnu_boot.img"

if "%BOOT_IMG%"=="" (
    echo [!] ERROR: xnu_boot.img not found! Ensure it is in the same directory.
    pause
    goto MENU
)

echo [*] Streaming Darwin XNU boot image to device DRAM (%BOOT_IMG%)...
"%FASTBOOT_BIN%" boot "%BOOT_IMG%"
if %ERRORLEVEL% equ 0 (
    echo [+] Fastboot boot command executed successfully!
    echo     Watch device display and UART serial console (115200 baud).
) else (
    echo [!] Fastboot boot failed. Verify bootloader is unlocked.
)
pause
goto MENU

:OP_FLASH_BOOT
echo.
echo [*] Selected: [2] Flash Darwin XNU Boot Partition
set "BOOT_IMG="
if exist "xnu_boot.img" set "BOOT_IMG=xnu_boot.img"
if exist "output\xnu_boot.img" set "BOOT_IMG=output\xnu_boot.img"
if exist "..\output\xnu_boot.img" set "BOOT_IMG=..\output\xnu_boot.img"

if "%BOOT_IMG%"=="" (
    echo [!] ERROR: xnu_boot.img not found!
    pause
    goto MENU
)

echo [!] WARNING: Flashing will overwrite current Android boot image on active slot!
set /p CONFIRM="Are you sure you want to flash boot partition? (Y/N): "
if /i not "%CONFIRM%"=="Y" goto MENU

echo [*] Flashing %BOOT_IMG% to boot partition...
"%FASTBOOT_BIN%" flash boot "%BOOT_IMG%"
if %ERRORLEVEL% equ 0 (
    echo [+] Boot partition flashed successfully!
) else (
    echo [!] Boot partition flash failed.
)
pause
goto MENU

:OP_BUILD_ROOTFS
echo.
echo [*] Selected: [3] Build / Stage iOS RootFS
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [!] ERROR: Python 3 not found in PATH! Please install Python 3.
    pause
    goto MENU
)

set "BUILDER="
if exist "build_ios_rootfs.py" set "BUILDER=build_ios_rootfs.py"
if exist "userspace\build_ios_rootfs.py" set "BUILDER=userspace\build_ios_rootfs.py"
if exist "..\userspace\build_ios_rootfs.py" set "BUILDER=..\userspace\build_ios_rootfs.py"

if "%BUILDER%"=="" (
    echo [!] ERROR: build_ios_rootfs.py not found!
    pause
    goto MENU
)

echo [*] Running iOS RootFS Builder (pass --download if you do not have IPSW)...
echo  [A] Provide existing IPSW file path
echo  [B] Automatically download iOS 16.7.16 IPSW from Apple CDN (~6.1 GB)
echo  [C] Back to Main Menu
set /p RF_OPT="Select [A/B/C]: "

if /i "%RF_OPT%"=="A" (
    set /p IPSW_FILE="Enter full path to iPhone X iOS 16.7.16 IPSW: "
    python "%BUILDER%" --ipsw "!IPSW_FILE!" --output ios_rootfs.img
) else if /i "%RF_OPT%"=="B" (
    python "%BUILDER%" --download --output ios_rootfs.img
) else (
    goto MENU
)
pause
goto MENU

:OP_FLASH_ROOTFS
echo.
echo [*] Selected: [4] Flash iOS RootFS to Storage
set "ROOTFS_IMG="
if exist "ios_rootfs.img" set "ROOTFS_IMG=ios_rootfs.img"
if exist "output\ios_rootfs.img" set "ROOTFS_IMG=output\ios_rootfs.img"

if "%ROOTFS_IMG%"=="" (
    echo [!] ERROR: ios_rootfs.img not found! Run Option 3 to build it first.
    pause
    goto MENU
)

echo [!] WARNING: Flashing iOS RootFS to device partition.
echo     Target partition: userdata (or dynamic slot in fastbootd)
set /p CONFIRM="Proceed with flashing %ROOTFS_IMG% to userdata? (Y/N): "
if /i not "%CONFIRM%"=="Y" goto MENU

echo [*] Flashing iOS RootFS to userdata...
"%FASTBOOT_BIN%" flash userdata "%ROOTFS_IMG%"
if %ERRORLEVEL% equ 0 (
    echo [+] iOS RootFS flashed successfully!
) else (
    echo [!] Flashing userdata failed. Try booting fastbootd first (fastboot reboot fastboot).
)
pause
goto MENU

:OP_FULL_INSTALL
echo.
echo [*] Selected: [5] 1-Click Complete Install (Boot + RootFS)
set "BOOT_IMG="
if exist "xnu_boot.img" set "BOOT_IMG=xnu_boot.img"
if exist "output\xnu_boot.img" set "BOOT_IMG=output\xnu_boot.img"

set "ROOTFS_IMG="
if exist "ios_rootfs.img" set "ROOTFS_IMG=ios_rootfs.img"
if exist "output\ios_rootfs.img" set "ROOTFS_IMG=output\ios_rootfs.img"

if "%BOOT_IMG%"=="" (
    echo [!] ERROR: xnu_boot.img not found!
    pause
    goto MENU
)

echo [*] Step 1: Flashing Darwin XNU kernel (%BOOT_IMG%)...
"%FASTBOOT_BIN%" flash boot "%BOOT_IMG%"

if not "%ROOTFS_IMG%"=="" (
    echo [*] Step 2: Flashing iOS RootFS (%ROOTFS_IMG%)...
    "%FASTBOOT_BIN%" flash userdata "%ROOTFS_IMG%"
) else (
    echo [.] Staged ios_rootfs.img not found. Boot partition flashed.
    echo     Build rootfs via Option 3 or boot via RAM.
)

echo [*] Step 3: Rebooting device...
set /p RB_CONF="Reboot to Darwin OS now? (Y/N): "
if /i "%RB_CONF%"=="Y" (
    "%FASTBOOT_BIN%" reboot
)
pause
goto MENU

:OP_UNLOCK
echo.
echo [*] Selected: [6] Bootloader Unlock Helper
echo [!] NOTE: Unlocking the bootloader will wipe user data on Android!
set /p UNL_CONF="Execute fastboot flashing unlock? (Y/N): "
if /i "%UNL_CONF%"=="Y" (
    "%FASTBOOT_BIN%" flashing unlock
    echo [*] Follow on-screen confirmation prompt on your Infinix GT 20 Pro display.
)
pause
goto MENU

:OP_DIAG
echo.
echo [*] Selected: [7] Query Device Hardware Diagnostics
"%FASTBOOT_BIN%" getvar all
pause
goto MENU

:OP_EXIT
echo.
echo Exiting Infinix GT 20 Pro iOS ROM Flasher. Goodbye!
exit /b 0
