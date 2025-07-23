// Board config for Cheetah RP2040.

// Board and hardware specific configuration
#define MICROPY_HW_BOARD_NAME           "DCF2025-Badge"
#define MICROPY_HW_FLASH_STORAGE_BYTES  (28 * 1024 * 1024)

// Enable MD5 hash.
#define MICROPY_PY_HASHLIB_MD5          (1)

// Disable internal error numbers.
#define MICROPY_USE_INTERNAL_ERRNO      (0)

// Enable USB Mass Storage with FatFS filesystem.
#define MICROPY_HW_USB_MSC              (1)
//#define MICROPY_HW_USB_VID              (0x2341)
//#define MICROPY_HW_USB_PID              (0x025e)
#define MICROPY_HW_USB_CDC_1200BPS_TOUCH (1)

// I2C1 config (non-default).
#define MICROPY_HW_I2C1_SCL             (27)
#define MICROPY_HW_I2C1_SDA             (26)

