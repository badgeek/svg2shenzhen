#! /usr/bin/env python

import inkex
import os
import subprocess
import tempfile
import shutil
import copy
import platform
import webbrowser
import hashlib
import xml.etree.ElementTree as ET
import pickle
from copy import deepcopy
from inkex import bezier
from inkex.transforms import Transform
from pathlib import Path


homePath = str()
homePath = Path.home()

EXPORT_PNG_MAX_PROCESSES = 3
EXPORT_KICAD_MAX_PROCESSES = 2

PCB_HEADER = '''
(kicad_pcb (version 4) (host pcbnew 4.0.7)

	(general
		(links 0)
		(no_connects 0)
		(area 77.052499 41.877835 92.193313 53.630501)
		(thickness 1.6)
		(drawings 8)
		(tracks 0)
		(zones 0)
		(modules 1)
		(nets 1)
	)

	(page A4)
	(layers
		(0 F.Cu signal)
		(31 B.Cu signal)
		(32 B.Adhes user)
		(33 F.Adhes user)
		(34 B.Paste user)
		(35 F.Paste user)
		(36 B.SilkS user)
		(37 F.SilkS user)
		(38 B.Mask user)
		(39 F.Mask user)
		(40 Dwgs.User user)
		(41 Cmts.User user)
		(42 Eco1.User user)
		(43 Eco2.User user)
		(44 Edge.Cuts user)
		(45 Margin user)
		(46 B.CrtYd user)
		(47 F.CrtYd user)
		(48 B.Fab user)
		(49 F.Fab user)
	)

	(setup
		(last_trace_width 0.25)
		(trace_clearance 0.2)
		(zone_clearance 0.508)
		(zone_45_only no)
		(trace_min 0.2)
		(segment_width 0.2)
		(edge_width 0.15)
		(via_size 0.6)
		(via_drill 0.4)
		(via_min_size 0.4)
		(via_min_drill 0.3)
		(uvia_size 0.3)
		(uvia_drill 0.1)
		(uvias_allowed no)
		(uvia_min_size 0.2)
		(uvia_min_drill 0.1)
		(pcb_text_width 0.3)
		(pcb_text_size 1.5 1.5)
		(mod_edge_width 0.15)
		(mod_text_size 1 1)
		(mod_text_width 0.15)
		(pad_size 1.524 1.524)
		(pad_drill 0.762)
		(pad_to_mask_clearance 0.2)
		(aux_axis_origin 0 0)
		(visible_elements FFFFFF7F)
		(pcbplotparams
			(layerselection 0x010f0_80000001)
			(usegerberextensions false)
			(excludeedgelayer true)
			(linewidth 0.100000)
			(plotframeref false)
			(viasonmask false)
			(mode 1)
			(useauxorigin false)
			(hpglpennumber 1)
			(hpglpenspeed 20)
			(hpglpendiameter 15)
			(hpglpenoverlay 2)
			(psnegative false)
			(psa4output false)
			(plotreference true)
			(plotvalue true)
			(plotinvisibletext false)
			(padsonsilk false)
			(subtractmaskfromsilk false)
			(outputformat 1)
			(mirror false)
			(drillshape 1)
			(scaleselection 1)
			(outputdirectory gerbers/))
	)

	(net 0 "")

	(net_class Default "This is the default net class."
		(clearance 0.2)
		(trace_width 0.25)
		(via_dia 0.6)
		(via_drill 0.4)
		(uvia_dia 0.3)
		(uvia_drill 0.1)
	)
'''

PCB_FOOTER = '''
)
'''

PCB_LIB_TABLE = '''
(fp_lib_table
  (lib (name "{name}")(type KiCad)(uri "$(KIPRJMOD)/{folder}")(options "")(descr ""))
)
'''

PCB_PROJECT_FILE = '''
update=2018 March 15, Thursday 14:41:19
version=1
last_client=kicad
[pcbnew]
version=1
LastNetListRead=
UseCmpFile=1
PadDrill=0.600000000000
PadDrillOvalY=0.600000000000
PadSizeH=1.500000000000
PadSizeV=1.500000000000
PcbTextSizeV=1.500000000000
PcbTextSizeH=1.500000000000
PcbTextThickness=0.300000000000
ModuleTextSizeV=1.000000000000
ModuleTextSizeH=1.000000000000
ModuleTextSizeThickness=0.150000000000
SolderMaskClearance=0.000000000000
SolderMaskMinWidth=0.000000000000
DrawSegmentWidth=0.200000000000
BoardOutlineThickness=0.100000000000
ModuleOutlineThickness=0.150000000000
[cvpcb]
version=1
NetIExt=net
[general]
version=1
[eeschema]
version=1
LibDir=
[eeschema/libraries]
LibName1=power
LibName2=device
LibName3=transistors
LibName4=conn
LibName5=linear
LibName6=regul
LibName7=74xx
LibName8=cmos4000
LibName9=adc-dac
LibName10=memory
LibName11=xilinx
LibName12=microcontrollers
LibName13=dsp
LibName14=microchip
LibName15=analog_switches
LibName16=motorola
LibName17=texas
LibName18=intel
LibName19=audio
LibName20=interface
LibName21=digital-audio
LibName22=philips
LibName23=display
LibName24=cypress
LibName25=siliconi
LibName26=opto
LibName27=atmel
LibName28=contrib
LibName29=valves
'''

MODULE_INVIS_REF_HEADER = '''
(fp_text reference Ref** (at 0 0) (layer F.SilkS) hide
(effects (font (size 1.27 1.27) (thickness 0.15)))
)
(fp_text value Val** (at 0 0) (layer F.SilkS) hide
(effects (font (size 1.27 1.27) (thickness 0.15)))
)
'''

IDENTITY_MATRIX = [[1.0,0.0,0.0],[0.0,1.0,0.0]]


LIBRARY_TABLE_FILE = "fp-lib-table"
EXPORT_IMAGE_FOLDER = "images"
EXPORT_CACHE_FOLDER = ".svg2shenzhen-cache"


class Svg2ShenzhenExport(inkex.Effect):
    def __init__(self):
        """init the effect library and get options from gui"""
        inkex.Effect.__init__(self)
        self.doc_width = 0
        self.doc_height = 0

        self.bb_width_center = 0
        self.bb_height_center = 0
        self.bb_scaling_w = 0
        self.bb_scaling_h = 0

        self.layer_map = {
            #'inkscape-name' : 'kicad-name',
            'F.Cu'      : 'F.Cu',
            'B.Cu'      : 'B.Cu',
            'B.Adhes'   : 'B.Adhes',
            'F.Adhes'   : 'F.Adhes',
            'B.Paste'   : 'B.Paste',
            'F.Paste'   : 'F.Paste',
            'B.SilkS'   : 'B.SilkS',
            'F.SilkS'   : 'F.SilkS',
            'B.Mask'    : 'B.Mask',
            'F.Mask'    : 'F.Mask',
            'Dwgs.User' : 'Dwgs.User',
            'Cmts.User' : 'Cmts.User',
            'Eco1.User' : 'Eco1.User',
            'Eco2.User' : 'Eco2.User',
            'Margin'    : 'Margin',
            'B.CrtYd'   : 'B.CrtYd',
            'F.CrtYd'   : 'F.CrtYd',
            'B.Fab'     : 'B.Fab',
            'F.Fab'     : 'F.Fab',
            # The following layers are here for backward compatibility:
            'B.Silk'    : 'B.SilkS',
            'F.Silk'    : 'F.SilkS',
            # 'Edge.Cuts' : "Edge.Cuts"
        }

    def add_arguments(self, pars):
        pars.add_argument("--path", default=homePath)
        pars.add_argument('-f', '--filetype', default='jpeg', help='Exported file type')
        pars.add_argument("--crop", type=inkex.Boolean, default=False)
        pars.add_argument("--dpi", type=int, default=600)
        pars.add_argument("--threshold", type=float, default=128.0)
        pars.add_argument("--openfactory", type=inkex.Boolean, default="true")
        pars.add_argument("--openkicad", type=inkex.Boolean, default="true")
        pars.add_argument("--autoflatten", type=inkex.Boolean, default="true")
        pars.add_argument("--debug", type=inkex.Boolean, default=False)

    def coordToKicad(self,XYCoord):
        return [
            (XYCoord[0]-self.bb_width_center)/self.bb_scaling_w,
            (XYCoord[1]-self.bb_height_center)/self.bb_scaling_h,
        ]

    def setInkscapeScaling(self):
        root = self.document.getroot()
        height = float(root.get('height').replace("mm", ""))
        width = float(root.get('width').replace("mm", ""))

        self.doc_width = width
        self.doc_height = height

        viewbox = root.attrib['viewBox'].split(' ')
        viewbox_h = float(viewbox[-1])
        viewbox_w = float(viewbox[-2])

        self.bb_width_center = viewbox_w/2
        self.bb_height_center = viewbox_h/2
        self.bb_scaling_w = viewbox_w/width
        self.bb_scaling_h = viewbox_h/height

    def setDocumentSquare(self):
        root = self.document.getroot()
        height = float(root.attrib['height'].replace("mm", ""))
        width =  float(root.attrib['width'].replace("mm", ""))

        if (width > height):
            root.attrib['height'] = str(width) + "mm"
            root.attrib['viewBox'] = "0 0 %f %f" % (width, width)
        else:
            root.attrib['width'] = str(height) + "mm"
            root.attrib['viewBox'] = "0 0 %f %f" % (height, height)

    def findLayer(self, layerName, contains=False):
        svg_layers = self.document.xpath('//svg:g[@inkscape:groupmode="layer"]', namespaces=inkex.NSS)
        for layer in svg_layers:
            label_attrib_name = "{%s}label" % layer.nsmap['inkscape']
            if label_attrib_name not in layer.attrib:
                continue
            if ((layer.attrib[label_attrib_name] == layerName) and (contains == False)):
                return layer
            elif ((layerName in layer.attrib[label_attrib_name]) and (contains == True)):
                return layer

        return False

    def effect(self):
        # self.setDocumentSquare()
        self.setInkscapeScaling()
        self.processAutoMasks()
        self.processExportLayer()
        if (self.options.openfactory):
            webbrowser.open("https://www.pcbway.com/setinvite.aspx?inviteid=54747", new = 2)

    def processAutoMasks(self):
        self.processAutoMaskFromTo("F.Cu", "F.Mask-auto")
        self.processAutoMaskFromTo("B.Cu", "B.Mask-auto")

    def processAutoMaskFromTo(self, from_layer, to_layer):
        copper_layer = self.findLayer(from_layer, False)
        cpmask_layer = self.findLayer(to_layer, True)
        # copper_layer = cpmask_layer
        if (copper_layer != False and cpmask_layer != False):
            for node in cpmask_layer.xpath("*", namespaces=inkex.NSS):
                cpmask_layer.remove(node)
            for node in copper_layer.xpath("*", namespaces=inkex.NSS):
                cpmask_layer.append(deepcopy(node))


    def processExportLayer(self):
        options = self.options

        if os.path.dirname(os.getcwd()) == options.path:
            inkex.errormsg('EXPORT ERROR! Please Select A Directory To Export To!')
            exit()
        else:
            output_path = os.path.expanduser(options.path)

        curfile = self.options.input_file
        layers = self.get_layers(curfile)
        name = self.get_name()
        kicad_pcb_file = "{}.kicad_pcb".format(name)
        library_folder = "{}.pretty".format(name)
        kicad_project_file = "{}.pro".format(name)
        kicad_mod_file = "{}.kicad_mod".format(name)
        kicad_mod_files = []

        cache_folder_path = os.path.join(output_path, EXPORT_CACHE_FOLDER)

        if options.filetype == "png":
            image_folder_path = output_path
        else:
            image_folder_path = os.path.join(cache_folder_path, EXPORT_IMAGE_FOLDER)

        if options.filetype == "kicad_pcb":
            library_folder_path = os.path.join(output_path, library_folder)
        else:
            library_folder_path = os.path.join(cache_folder_path, library_folder)

        if not os.path.exists(output_path):
            os.makedirs(output_path)
        if not os.path.exists(library_folder_path):
            os.makedirs(library_folder_path)
        if not os.path.exists(image_folder_path):
            os.makedirs(image_folder_path)
        if not os.path.exists(cache_folder_path):
            os.makedirs(cache_folder_path)

        kicad_pcb_path = os.path.join(output_path, kicad_pcb_file )
        kicad_lib_path = os.path.join(output_path, LIBRARY_TABLE_FILE)
        kicad_pro_path = os.path.join(output_path, kicad_project_file )
        kicad_mod_path = os.path.join(output_path, kicad_mod_file)

        options_path = os.path.join(cache_folder_path, 'export_options.pickle')

        curr_options = {
            'dpi': options.dpi,
            'path': options.path,
            'crop': options.crop,
            'filetype': options.filetype,
            'threshold': options.threshold
        }

        if os.path.exists(options_path):
            with open(options_path, 'rb') as f:
                prev_options = pickle.load(f)
            ignore_hashes = prev_options != curr_options
        else:
            ignore_hashes = True

        with open(options_path, 'wb') as f:
            pickle.dump(curr_options, f)

        layer_arguments = []
        temp_svg_paths = []
        for (layer_id, layer_label, layer_type) in layers:
            if layer_type == "fixed":
                continue
            show_layer_ids = [layer[0] for layer in layers if layer[2] == "fixed" or layer[0] == layer_id]
            invert = "true"

            if ("-auto" in layer_label):
                layer_label = layer_label.replace("-auto", "")

            if ("-invert" in layer_label):
                layer_label = layer_label.replace("-invert", "")
                invert = "false"
            hash_sum_path = os.path.join(cache_folder_path, '{}-{}-{}-{}.hash'.format(layer_id, layer_label, layer_type, invert))

            prev_hash_sum = None
            if os.path.exists(hash_sum_path):
              with open(hash_sum_path, 'r') as f:
                  prev_hash_sum = f.read()

            # generate unique filename each layer
            temp_name = next(tempfile._get_candidate_names()) + ".svg"
            layer_dest_svg_path = os.path.join(cache_folder_path, temp_name)
            hash_sum = self.export_layers(layer_dest_svg_path, show_layer_ids)
            temp_svg_paths.append(layer_dest_svg_path)

            layer_dest_png_path = os.path.join(image_folder_path,  "%s_%s.png" % (layer_label, layer_id))
            layer_dest_kicad_path = os.path.join(library_folder_path, "%s_%s.kicad_mod" % (layer_label, layer_id))
            kicad_mod_files.append(layer_dest_kicad_path)


            if ignore_hashes or hash_sum != prev_hash_sum or not os.path.exists(layer_dest_kicad_path):
                with open(hash_sum_path, 'w') as f:
                    f.write(hash_sum)
                layer_arguments.append((layer_dest_svg_path, layer_dest_png_path, layer_dest_kicad_path, layer_label, invert))


        for i in range(0, len(layer_arguments), EXPORT_PNG_MAX_PROCESSES):
            processes = []
            for layer_dest_svg_path, layer_dest_png_path, _, _, _ in layer_arguments[i:i+EXPORT_PNG_MAX_PROCESSES]:
                #export layer to png
                p = self.exportToPng(layer_dest_svg_path, layer_dest_png_path)
                processes.append(p)
            for p in processes:
                p.communicate()

        for layer_dest_svg_path in temp_svg_paths:
            os.remove(layer_dest_svg_path)

        if options.filetype == "kicad_pcb" or options.filetype == "kicad_module":
            for i in range(0, len(layer_arguments), EXPORT_KICAD_MAX_PROCESSES):
                processes = []
                for _, layer_dest_png_path, layer_dest_kicad_path, layer_label, invert in layer_arguments[i:i+EXPORT_KICAD_MAX_PROCESSES]:
                    #export layer png to kicad
                    p = self.exportToKicad(layer_dest_png_path, layer_dest_kicad_path, layer_label, invert)
                    processes.append(p)
                for p in processes:
                    p.communicate()
        else:
            return

        kicad_edgecut_string = self.exportEdgeCut(kicad_mod = options.filetype == "kicad_module")
        kicad_drill_string = self.exportDrill(kicad_mod = options.filetype == "kicad_module")

        if options.filetype == "kicad_pcb":
            kicad_modules_string = ""
            for kicad_file in kicad_mod_files:
                with open(kicad_file, 'r') as f:
                    kicad_modules_string += f.read()

            with open(kicad_pcb_path, 'w') as f:
                f.write(PCB_HEADER)
                f.write(kicad_modules_string)
                f.write(kicad_edgecut_string)
                f.write(kicad_drill_string)
                f.write(PCB_FOOTER)

            with open(kicad_lib_path, 'w') as f:
                f.write(PCB_LIB_TABLE.format(name=name, folder=library_folder))

            with open(kicad_pro_path, 'w') as f:
                f.write(PCB_PROJECT_FILE)

            if (options.openkicad):
                self.openKicad(kicad_pcb_path).communicate()

        elif options.filetype == "kicad_module":
            kicad_modules_string = '(module "{}" (layer F.Cu)'.format(name)
            kicad_modules_string += MODULE_INVIS_REF_HEADER
            for kicad_file in kicad_mod_files:
                with open(kicad_file, 'r') as f:
                    mod = f.readlines()[8:-1]
                    kicad_modules_string += "".join(mod)
            kicad_modules_string += kicad_edgecut_string
            kicad_modules_string += kicad_drill_string
            kicad_modules_string += ")"
            with open(kicad_mod_path, 'w') as f:
                f.write(kicad_modules_string)


    def export_layers(self, dest, show):
        """
        Export selected layers of SVG to the file `dest`.
        :arg  str   dest:  path to export SVG file.
        :arg  list  hide:  layers to hide. each element is a string.
        :arg  list  show:  layers to show. each element is a string.
        """
        doc = copy.deepcopy(self.document)
        root = doc.getroot()
        for layer in doc.xpath('//svg:g[@inkscape:groupmode="layer"]', namespaces=inkex.NSS):
            id = layer.attrib["id"]
            if id in show:
                layer.attrib['style'] = 'display:inline'
            else:
                root.remove(layer)

        # remove the namedview for the hash as it changes based on user zoom/scroll
        namedview = doc.find('sodipodi:namedview', namespaces=inkex.NSS)
        root.remove(namedview)

        doc.write(dest)

        # returns a hash of the exported layer contents which can be used to
        # detect changes
        return hashlib.md5(ET.tostring(root)).hexdigest()

    def get_name(self):
        root = self.document.getroot()
        docname = root.get('{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}docname')
        if docname is None:
            return 'drawing'
        return os.path.splitext(docname)[0]

    def get_layers(self, src):
        svg_layers = self.document.xpath('//svg:g[@inkscape:groupmode="layer"]', namespaces=inkex.NSS)
        layers = []

        for layer in svg_layers:
            label_attrib_name = "{%s}label" % layer.nsmap['inkscape']
            if label_attrib_name not in layer.attrib:
                continue

            layer_id = layer.attrib["id"]
            layer_label = layer.attrib[label_attrib_name]

            layer_label_name = layer_label.replace("-invert", "")
            layer_label_name = layer_label_name.replace("-auto", "")

            if  layer_label_name in self.layer_map.keys():
                layer_type = "export"
                layer_label = layer_label
            elif layer_label.lower().startswith("[fixed] "):
                layer_type = "fixed"
                layer_label = layer_label[8:]
            else:
                continue

            layers.append([layer_id, layer_label, layer_type])

        return layers

    def openKicad(self, kicad_file_path):
        platform_system = platform.system()

        if (platform_system == 'Darwin'):
            command = "open %s" % (kicad_file_path)
        elif (platform_system == 'Linux'):
            command = "xdg-open %s" % (kicad_file_path)
        else:
            command = "start %s" % (kicad_file_path)

        return subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)



    def exportToKicad(self, png_path, output_path, layer_type, invert = "true"):
        plugin_path = os.path.dirname(os.path.abspath(__file__))

        platform_system = platform.system()

        if (platform_system == 'Darwin'):
            bitmap2component_exe = os.path.join(plugin_path, 'bitmap2component_osx')
        elif (platform_system == 'Linux'):
            bitmap2component_exe = os.path.join(plugin_path, 'bitmap2component_linux64')
        else:
            bitmap2component_exe = os.path.join(plugin_path, 'bitmap2component.exe')

        layer_name = self.layer_map[layer_type]
        command =  "\"%s\" \"%s\" \"%s\" %s %s %s %s" % (bitmap2component_exe, png_path, output_path, layer_name, invert , str(int(self.options.dpi)) , str(int(self.options.threshold)))
        if (self.options.debug):
            inkex.utils.debug(command)
        return subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


    def exportToPng(self, svg_path, output_path):
        area_param = '-D' if self.options.crop else '-C'
        command = "inkscape %s -d %s -o \"%s\" \"%s\"" % (area_param, self.options.dpi, output_path, svg_path)
        if (self.options.debug):
            inkex.utils.debug(command)
        return subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


    def exportEdgeCut(self, kicad_mod=False):
        x0 = 0
        y0 = 0
        mirror = 1.0

        line_type = "fp_line" if kicad_mod else "gr_line"

        kicad_edgecut_string = ""

        i = 0
        layerPath = '//svg:g[@inkscape:groupmode="layer"]'

        if (self.options.autoflatten):
            self.flatten_bezier()

        for layer in self.document.getroot().xpath(layerPath, namespaces=inkex.NSS):
            i += 1

            label_attrib_name = "{%s}label" % layer.nsmap['inkscape']
            if label_attrib_name not in layer.attrib:
                continue

            layer_name = (layer.attrib[label_attrib_name])

            if layer_name != "Edge.Cuts":
                continue

            layer_trans = layer.get('transform')
            if layer_trans:
                layer_m = Transform(layer_trans).matrix
            else:
                layer_m = IDENTITY_MATRIX

            nodePath = ('//svg:g[@inkscape:groupmode="layer"][%d]/descendant::svg:path') % i
            for node in self.document.getroot().xpath(nodePath, namespaces=inkex.NSS):
                p = node.path.to_arrays()

                points = []
                if p:
                    #sanity check
                    if p[0][0] == 'M':
                        t = node.get('transform')
                        if t:
                            trans = (Transform(layer_m)*Transform(t)).matrix
                        else:
                            trans = layer_m

                        for path in p:
                            if path[0] != "Z":
                                x = (path[1][0])
                                y = (path[1][1])
                                xy = Transform(trans).apply_to_point([x,y])
                                points.append(self.coordToKicad([(xy[0]-x0), xy[1]*mirror-y0]))

                        points_count = len(points)
                        points.append(points[0])

                        for x in range (0, points_count):
                            kicad_edgecut_string = kicad_edgecut_string + ("(%s (start %f %f) (end %f %f) (layer Edge.Cuts) (width 0.1))\n"  % (line_type, points[x][0],points[x][1],points[x+1][0],points[x+1][1]))

        return kicad_edgecut_string

    def exportDrill(self, kicad_mod=False):
        self.setInkscapeScaling()

        kicad_drill_string = ""

        i = 0

        if kicad_mod:
            pad_template = "(pad {n} thru_hole circle (at {x} {y}) (size {d} {d}) (drill {d}) (layers *.Cu *.Mask))\n"
        else:
            pad_template = """
                (module Wire_Pads:SolderWirePad_single_0-8mmDrill (layer F.Cu) (tedit 0) (tstamp 5ABD66D0)
                    (at {x} {y})
                    (pad {n} thru_hole circle (at 0 0) (size {d} {d}) (drill {d}) (layers *.Cu *.Mask))
                )
            """

        layerPath = '//svg:g[@inkscape:groupmode="layer"][@inkscape:label="Drill"]'

        for layer in self.document.getroot().xpath(layerPath, namespaces=inkex.NSS):

            layer_trans = layer.get('transform')
            if layer_trans:
                layer_m = Transform(layer_trans).matrix
            else:
                layer_m = IDENTITY_MATRIX

            nodePath = 'descendant::svg:circle'

            count = 0
            for node in layer.xpath(nodePath, namespaces=inkex.NSS):
                count = count + 1
                cx = float(node.get('cx'))
                cy = float(node.get('cy'))

                radius = float(node.get('r'))
                drill_size = radius * 2

                t = node.get('transform')

                if t:
                    m = Transform(t).matrix
                    trans = (Transform(layer_m)*Transform(m)).matrix
                else:
                    trans = layer_m

                pt = Transform(trans).apply_to_point([cx, cy])
                padCoord = self.coordToKicad(pt)

                kicad_drill_string += pad_template.format(x=padCoord[0], y=padCoord[1], n=count, d=drill_size)

        return kicad_drill_string

    def flatten_bezier(self):
        layerPath = '//svg:g[@inkscape:groupmode="layer"][@inkscape:label="Edge.Cuts"]'
        for layer in self.document.getroot().xpath(layerPath, namespaces=inkex.NSS):
            nodePath = 'descendant::svg:path'
            for node in layer.xpath(nodePath, namespaces=inkex.NSS):
                if node.tag == inkex.addNS('path','svg'):
                    d = node.get('d')
                    p = inkex.Path(d).to_superpath()
                    bezier.cspsubdiv(p, 0.01)
                    np = []
                    for sp in p:
                        first = True
                        for csp in sp:
                            cmd = 'L'
                            if first:
                                cmd = 'M'
                            first = False
                            np.append([cmd, [csp[1][0], csp[1][1]]])
                            node.set('d', str(inkex.Path(np)))

def _main():
    e = Svg2ShenzhenExport()
    e.run()
    exit()

if __name__ == "__main__":
    _main()
