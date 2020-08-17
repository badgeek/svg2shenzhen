# Svg2Shenzhen

Inkscape extension for exporting drawings into a KiCad PCB

![screenshot_125](https://i.imgur.com/gjFZZu3.jpg)

## Features

- Draw Any kind of shapes without restriction
- Supports Drill Pad, and custom drill size
- Supports Edge Cut (PCB Shape)
- Tested on OSX, Windows and Linux

## Install

Warning: starting from 0.2.18 svg2shenzhen only support Inkscape 1.0 and above

1. Download the latest version (0.2.18.1)
  - Windows https://github.com/badgeek/svg2shenzhen/releases/download/0.2.18.1/svg2shenzhen-extension-0.2.18.1.zip
  - Linux / OSX https://github.com/badgeek/svg2shenzhen/releases/download/0.2.18.1/svg2shenzhen-extension-0.2.18.1.tar.gz
  - Release notes: https://github.com/badgeek/svg2shenzhen/releases/tag/0.2.18.1
  - Older version: https://github.com/badgeek/svg2shenzhen/releases
  
2. Extract and copy the files into the directory indicated in Inkscape under *Edit -> Preferences -> System: User extensions*

## How to

In Inkscape:

1. *Extension > Svg2Shenzhen > Prepare Document*
2. Choose layer (F.Cu.. etc)
3. Draw PCB
4. *Extension > Svg2Shenzhen > Export KiCad*

Download and open [Example PCB](https://raw.githubusercontent.com/badgeek/svg2shenzhen-next/master/examples/viruspcb.svg)

## Tutorials

- Custom Footprints for KiCad - <https://www.gabetaubman.com/blog/posts/kicad-custom-footprint/>
- PCBArt Badge - <http://blog.sheasilverman.com/2019/01/pcbart/>

## Layername definitions

1. After the *Prepare Document* step, only two fabrication layers are used:
   *Edge.Cuts* and *Drill*,
   and for the different PCB-layers, only the *F.Cu* layer is active.
   The others have the post-fix "-disabled" in their layer name;
   change this by removing this post-fix to enable more layers.
2. Special use of the solder-mask layers *F.Mask* and *B.Mask*:
   Due to the fabrication standard of PCB manufacturing,
   when enabled, this will lead to the solder-mask NOT being present
   where there are black areas in your design.
   This is kinda PCB/KiCad standard, but can be confusing.
   If you want to Get-What-You-See from Inkscape,
   meaning that you really draw the color where you want the solder-mask to be,
   change the layer name to *F.Mask-invert*
3. Super easy simple PCB with exposed copper surrounded by solder-mask,
   can be generated automatically by leaving the *F.Mask* layer empty
   and renaming it to *F.Mask-auto*.
4. Feel free to add your own layers, for testing graphics and designing stuff.
   All these other layers will be ignored.

## Tips

1. For *Edge.Cut* layers, you need to convert any polygons or objects to paths with only an outline, no fill.
   Don't use any groups on *Edge.Cut* layers,
   and if you have paths with inner cut-outs,
   break them apart into separate paths.
2. For Drill layers, place circle objects,
   and they will be converted into drill pads in KiCad with the same diameter.
   These drills will not have annular rings,
   unless you also add copper to the *F.Cu* and *B.Cu* layers.
   Don't use any groups on the *Drill* layer either.

## References

- [Svg2Shenzhen Announcement on Gosh Community Forum](https://forum.openhardware.science/t/svg2shenzhen-save-inkscape-drawing-as-kicad-pcb/989)
- [PCB Art with Inkscape - Developer log](http://wiki.8bitmixtape.cc/#/4_7.1-PCB-Art-with-Kicad-and-Inkscape) on the 8BitMixtape Wiki
- [Practical Guide to Designing PCB Art](https://medium.com/@urish/a-practical-guide-to-designing-pcb-art-b5aa22926a5c)
- [KitSprint ANORG 2018](http://wiki.sgmk-ssam.ch/wiki/KitSprint_ANORG_2018#Kicad_bitmap_import_for_Shenzhen_Ready)

## Videos
- Drawing PCBs with Inkscape (FOSSDEM) with @kasbah of kitspace - https://www.youtube.com/watch?v=xXRPw7ItMaM
- Making a PCB Badge for Hackaday Supercon! - https://www.youtube.com/watch?v=YqdBiOj8uXw
- Understanding and Making PCB Art (mrtwinkletwinkle) https://www.youtube.com/watch?v=Sbkvza8cKQE

## Support this project

This project is developed independently and without any connection to funding or big collective or organization.
Donation is highly appreciated.
Go to <https://www.patreon.com/badgeek> to become a patron and support this project

<a href="https://www.patreon.com/badgeek">
  <img src="https://i.imgur.com/ys5X3ZP.png" >
</a>

## Contributors

- Budi Prakosa [@badgeek](https://github.com/badgeek)
- Kaspar Emanuel [@kasbah](https://github.com/kasbah)

## Credits

* inkscape-export-layers - <https://github.com/jespino/inkscape-export-layers>
* bitmap2component (kicad) - <https://github.com/KiCad/kicad-source-mirror/tree/master/bitmap2component>
* csv_output - <https://github.com/tbekolay/csv_output>
* svg2mod - <https://github.com/svg2mod/svg2mod>
