# Svg2Shenzhen
Inkscape extension for exporting drawing into Kicad PCB

![screenshot_125](https://i.imgur.com/gjFZZu3.jpg)

## Features

- Draw Any kind of shapes without restriction (unlike svg2mod)
- Support Drill Pad, and custom drill size
- Support Edge Cut (PCB Shape)
- Tested on OSX, and Windows and Linux

## Install

Download latest version (0.2.17) of [svg2shenzhen-extension.zip](https://github.com/badgeek/svg2shenzhen-next/releases)

Extract and copy the files into the directory indicated in Edit -> Preferences -> System: User extensions

## How to

    1.Extension > Svg2Shenzhen > Prepare Document
    2.Choose layer (F.Cu.. etc)
    3.Draw PCB
    4.Extension > Svg2Shenzhen > Export Kicad

Download and open [Example PCB](https://raw.githubusercontent.com/badgeek/svg2shenzhen-next/master/examples/viruspcb.svg)

## Tutorials

- Custom Footprints for Kicad - https://www.gabetaubman.com/blog/posts/kicad-custom-footprint/
- PCBArt Badge - http://blog.sheasilverman.com/2019/01/pcbart/

## Layername definitions

![screenshots_inkscape-3d-view](https://github.com/dusjagr/svg2shenzhen/raw/master/examples/myFirstPCB_comboScreen.png)

1. After the Prepare Document only the 2 fabrication layers are used, Edge.Cuts and Drill, and for the different PCB-layers only the F.Cu layer is active. The others have in the layer name "-disabled", change this by removing the ending to enable more layers.
2. Special use of Soldermaks layers: F.Mask and B.Mask. Due to the fabrication standard of PCB manufacturing, when enabled this will lead to the soldemask NOT present, where there are black areas in your design. This is kinda PCB / KiCAD standard, but can be confusing. If you want to Get-What-You-See from inkscape, meaning that you really draw the color, where you want the soldermaks to be change the layer name to "F.Mask-invert"
3. Super easy simple PCB with exposed copper, surrounded by soldermask can be generated automatically by leaving the F.Mask layer empty and renaming it to "F.Mask-auto".
4. Feel free to add your own layers, for testing graphics and designing stuff. All these other layernames will be ignored.

## Tips

1. For Edge.Cut layers, you need to convert any polygons or objects to paths with only an outline, no fill. Don't use any groups on Edge.Cut layers and if you have paths with inner cut outs break them apart into separate paths.
2. For Drill layers, place circle objects and they will be converted into drill pads in KiCad with the same diameter. These drills will not have annular rings unless you also add copper to the F.Cu and B.Cu layers. Don't use any groups on Drill layers either.

## References

- [Svg2Shenzhen Announcement on Gosh Community Forum](https://forum.openhardware.science/t/svg2shenzhen-save-inkscape-drawing-as-kicad-pcb/989)
- [PCB Art with Inkscape - Developer log](http://wiki.8bitmixtape.cc/#/4_7.1-PCB-Art-with-Kicad-and-Inkscape) on 8BitMixtape Wiki
- [Practical Guide to Designing PCB Art](https://medium.com/@urish/a-practical-guide-to-designing-pcb-art-b5aa22926a5c)
- [KitSprint ANORG 2018](http://wiki.sgmk-ssam.ch/wiki/KitSprint_ANORG_2018#Kicad_bitmap_import_for_Shenzhen_Ready)


## Support this project

This project is developed independently and without any connection to funding or big collective or organization, Donation is highly appreciated, go to https://www.patreon.com/badgeek become a patron and support this project

<a href="https://www.patreon.com/badgeek">
  <img src="https://i.imgur.com/ys5X3ZP.png" >
</a>


## Contributors
- Budi Prakosa [@badgeek](https://github.com/badgeek)
- Kaspar Emanuel [@kasbah](https://github.com/kasbah)

## Credits
* inkscape-export-layers - https://github.com/jespino/inkscape-export-layers
* bitmap2component (kicad) - https://github.com/KiCad/kicad-source-mirror/tree/master/bitmap2component
* csv_output - https://github.com/tbekolay/csv_output
* svg2mod - https://github.com/mtl/svg2mod
