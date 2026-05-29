# Ottimizzazioni per avvio veloce LyraOS
BOARD_KERNEL_CMDLINE += quiet loglevel=0 androidboot.selinux=permissive
TARGET_NO_RECOVERY := true
TARGET_ARCH := arm64
TARGET_ARCH_VARIANT := armv8-a

# Parametri Boot Image
BOARD_KERNEL_PAGESIZE := 2048
BOARD_BOOTIMG_HEADER_VERSION := 2
BOARD_MKBOOTIMG_ARGS := --header_version $(BOARD_BOOTIMG_HEADER_VERSION)

# Parametri Boot Image e Kernel
BOARD_KERNEL_CMDLINE := console=ttyS0 androidboot.console=ttyS0 androidboot.selinux=permissive
BOARD_MKBOOTIMG_ARGS := --ramdisk_offset 0x01000000 --tags_offset 0x00000100
TARGET_NO_KERNEL := false
