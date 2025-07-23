# DCFurs Badge Firmware

This directory contains board support and firmware for the 2025 DCFurs badge, to
be built using Micropython. The build instructions should roughly follow the
[RP2](https://github.com/micropython/micropython/tree/master/ports/rp2) port as
follows:

### Clone Micropython

Clone the latest release of Micropython (v1.23.0 at the time of writing):

```
git clone -b v1.23.0 https://github.com/micropython/micropython.git
```

You will probably also need to download the Arm GNU toolchain from
[ARM](https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads) and
install it into your PATH environment variable before proceeding.

### Build prerequisites

From the root of the micropython project, build the `mpy-cross` tool:

```
make -C mpy-cross
```

Then, from the `ports/rp2` directory of the micropython project build the
submodules:

```
make submodules
make clean
```

### Build the DCFurs Badge Firmware

From the `ports/rp2` directory in the micropython project, we can build the
badge firmware by specifying the path to the DCFurs board support directory:

```
make BOARD_DIR=~/path/to/dcfurs-badge-dc32/board/DCF2025_BADGE
```

Once the build has finished, you should be able to find the compiled firmware
in the `ports/rp2/build-DCF2025_BADGE` directory of the micropython project.

### Programming the Badge

Programming of the badge can be achieved using the RP2 USB bootloader:
 1. Remove all power to the badge by disconnecting USB and turning the power
    switch `SW1` to the OFF position.
 2. Press the boot button while powering up the badge via a USB connection
    to your laptop.
 3. The device should enumerate as a USB Mass storage device named `RPI-RP2`
 4. Copy the `firmware.uf2` file from your build directory onto the `RPI-RP2`
    USB drive and the bootloader should begin programming the firmware.
 5. Once programming is complete, the badge will automatically reboot into the
    new firmware.


