**Show the people my head. It is well worth seeing.**

## About Georges Danton
Georges-Jaques Danton was a layer who had grown up in the outper parts of the Champagne region of of the Kindom of France. Rising through the ranks of the French legal system he was a relatively unknown Royal Council lawyer on the eve of the Revolution.  His penchant for long addresses without written record of such and photographic recall of classic texts marked him as an orator to be reckoned with. So when it came time for him to rise as a loud voice of the Cordeliers in the French Revolution, he met this with vigor.

Unfortunately as the Revolution wound on, with questions of financial impropriety, and falling out of favor with the mastermind of the Great Terror, Robespierre, he was beheaded on 5 April, 1794.  His last words were to the executioner, Charles-Henri Sanson, "Show the people my head. It is well worth seeing."

**Liberté, égalité, fraternité!**

## Firmware

We will be promoting builds from this repo to releases perodically, see the releases section for the latest firmware.

## Updating

When you load a new firmware uf2 file, it will not delete the existing micropython filesystem, so if you want updated python files, you can either copy them from this repo or delete all the files from that filesystem and hit the reset button on the badge and it will reload them.  It is recommended that you perodically backup or keep a seperate copy of the python files as you work on them, working on them directly on the badge filesystem may cause issues.

## PCB Information

As a policy, DEFCON Furs only makes public the schematic, board images and the Bill of Materials for the DEFCON Furs badges.

The BoM can be viewed online: https://docs.google.com/spreadsheets/d/1CusGsHdCnYlghKfnkGq2Gd75HYyM90Wml26NhFPAL34/edit?usp=sharing

PCBs for the prototype and After Dark versions of the badge were manufactured by OSHPark in Oregon and assembled by Kay in Seattle.
Black and assembled PCBs for sale to the public and DEFCON Furs staff badges were made by PCBWay in Shenzhen and assembled by PCBx.io in Ohio.

The files in the PCB_Stuff directory consist of:

- DCF2025 Badge R1.0_back.png - This is the back of the 1.0 badge as rendered by OSHPark.
- DCF2025 Badge R1.0_front.png - This is the front of the 1.0 badge as rendered by OSHPark.
- DCF2025_Badge_2025-07-18.pdf - This is a PDF of the schematic.
- DCFurs 2025 Badge BoM.xlsx - This is an Excel spreadsheet of the Bill of Materials as exported from Google Docs.

## TODO

- **Prize** Get Meshtastic working on the badge and get a free badge next year!
- Moar animations!
- KiCAD files, minus the board, these will be released in late August or September after we have verified that they do not contain stuff we can't license as open hardware.
- Information about how to connect JTAG to the STM32WL chip.

## More Info
So, were going to do a thing this year where the software on the badge is not complete and people are welcome to make it more complete.    On Wednesday or really early Thursday morning of the con, we will make the repo with this years software public.

Stuff were still working on:
- More animations.
- Support for writing stuff to the M24SR16 NFC chip.
- The radio has some firmware on it already, if we can initialize that and have a way to send and receive using the AT commands, that would be a nice starter.

Things you will want to have to hack the badge:
If your going to muck around with the software on the STM32WL chip, you will want to have a breakout for JTAG like the Adafruit 2743, some wirewrap wire and a JTAG probe like the ST-LINK V3.

## Credits

- **Artwork** - Vurt
- **PCB Design and PM** - Kyle "Kay" Fox
- **Sales and Accounting** - Alofoxx
- **Software** - Loial Otter
- **Software and Build Toolchain** - Naomi Kirby
- **Ideas and maybe software someday** - NullFox
- **Assembly and putting up with Kay** - Colin and Matt at PCBx.io.
- **Soldering on battery packs** - @Fujimaru_husky

## Contributing

To contribute, clone this repository and when your ready to submit your work, send us a pull request. You will want to update the contributors.txt file and the credits.txt file with your attibutions. Contributors agree to abide by the DEFCON Furs code of conduct located at https://2025.dcfurs.com/code-of-conduct and agree to have their code licensed under the GNU General Public License version 2.

## License and Copyrights

Artwork used for this badge is Copyright (C) 2025 Vurt, used with permission.
Hardware design for this badge is Copyright (C) 2022 - 2025 Kyle "Kay" Fox, and is licensed under the Creative Commons BY-SA 4.0 license, see https://creativecommons.org/licenses/by-sa/4.0/



## Tools Used

Software:
- KiCad 8.0.8 
- Inkscape 1.4.2
- svg2shenzhen 0.2.18.7
- Arduino 1.8.19 (Badge test tools and "blessing" code)
- Arduino IDE 2.3.6 (Further refinement of badge test tools and "blessing" code)

Soldering:
- Hakko 936 (Kay's soldering iron)
- Hakko FX-888D (Soldering iron Fujimaru used)
- Pinecil2 (Field repairs)

Solder:
- Production PCBs were made using AIM REL61 solder, this includes repairs made at Alo's house.
- Protoype badges, after-dark badges and repairs done at Kay's house used Sparkle (Senju Metals) M705 solder.   I'd love to use REL61, but I paid $300 for this bottle of M705 in 2011 and I keep it in the fridge like a prized sourdough starter.
- All solder used is lead-free and conforms to SAC305 standards.
- Both PCBx.io and Kay's work conform to IPC-A-610 standards.
- Only halogen-free solder flux was used.
