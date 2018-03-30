#! /usr/bin/env python

import sys
sys.path.append('/usr/share/inkscape/extensions')
import inkex
import os
import subprocess
import tempfile
import shutil
import copy


pcb_header = '''
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
			(layerselection 0x00030_80000001)
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
			(outputdirectory ""))
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

pcb_footer = '''
)
'''

identity_m = [[1.0,0.0,0.0],[0.0,1.0,0.0]]


class PNGExport(inkex.Effect):
    def __init__(self):
        """init the effetc library and get options from gui"""
        inkex.Effect.__init__(self)
        self.OptionParser.add_option("--path", action="store", type="string", dest="path", default="~/", help="")
        self.OptionParser.add_option('-f', '--filetype', action='store', type='string', dest='filetype', default='jpeg', help='Exported file type')
        self.OptionParser.add_option("--crop", action="store", type="inkbool", dest="crop", default=False)
        self.OptionParser.add_option("--dpi", action="store", type="float", dest="dpi", default=90.0)
        self.OptionParser.add_option("--threshold", action="store", type="float", dest="threshold", default=128.0)

        self.bb_width_center = 0
        self.bb_height_center = 0
        self.bb_scaling = 0

        self.layer_map = {
            #'inkscape-name' : kicad-name,
            'F.Cu' :    "F.Cu",
            'B.Cu' :    "B.Cu",				
            'Adhes' : "{}.Adhes",
            'Paste' : "{}.Paste",
            'F.SilkS' : "F.SilkS",
            'B.SilkS' : "B.SilkS",				
            'F.Mask' :  "F.Mask",
            'B.Mask' :  "B.Mask",				
            'CrtYd' : "{}.CrtYd",
            'Fab' :   "{}.Fab",
            'Edge.Cuts' : "Edge.Cuts"
        }


    def coordToKicad(self,XYCoord):	
        return [
            (XYCoord[0]-self.bb_width_center)/self.bb_scaling,
            (XYCoord[1]-self.bb_height_center)/self.bb_scaling,
        ]

    def setInkscapeScaling(self):	

        root = self.document.getroot()
        height = float(self.document.getroot().get('height').replace("mm", ""))
        width = float(self.document.getroot().get('width').replace("mm", ""))
        
        viewbox = root.attrib['viewBox'].split(' ')
        viewbox_h = float(viewbox[-1])
        viewbox_w = float(viewbox[-2])

        self.bb_width_center = viewbox_w/2
        self.bb_height_center = viewbox_h/2	
        self.bb_scaling = viewbox_h/height

    def setDocumentSquare(self):
        root = self.document.getroot()
        height = float(root.attrib['height'].replace("mm", ""))
        width =  float(root.attrib['width'].replace("mm", ""))

        if (width > height):
            root.attrib['height'] = str(width) + "mm"
        else:
            root.attrib['width'] = str(height) + "mm"

    def effect(self):

        output_path = os.path.expanduser(self.options.path)
        curfile = self.args[-1]
        layers = self.get_layers(curfile)
        counter = 1

        self.setDocumentSquare()
        self.setInkscapeScaling()

        for (layer_id, layer_label, layer_type) in layers:
            if layer_type == "fixed":
                continue

            show_layer_ids = [layer[0] for layer in layers if layer[2] == "fixed" or layer[0] == layer_id]

            if not os.path.exists(os.path.join(output_path)):
                os.makedirs(os.path.join(output_path))

            with tempfile.NamedTemporaryFile() as fp_svg:
                layer_dest_svg_path = fp_svg.name
                self.export_layers(layer_dest_svg_path, show_layer_ids)

                if self.options.filetype == "kicad_pcb":
                    with tempfile.NamedTemporaryFile() as fp_png:

                        png_dest_kicad_path = os.path.join(output_path, "%s_%s.png" % (str(counter).zfill(3), layer_label))

                        self.exportToPng(layer_dest_svg_path, png_dest_kicad_path)
                        layer_dest_kicad_path = os.path.join(output_path, "%s_%s.kicad_pcb" % (str(counter).zfill(3), layer_label))
                        self.exportToKicad(png_dest_kicad_path, layer_dest_kicad_path, layer_label )

                        # layer_dest_jpg_path = os.path.join(output_path, "%s_%s.jpg" % (str(counter).zfill(3), layer_label))
                        # self.convertPngToJpg(fp_png.name, layer_dest_jpg_path)
                elif self.options.filetype == "kicad_module":
                        inkex.debug("kicad_module not implemented")

                else:
                    layer_dest_png_path = os.path.join(output_path, "%s_%s.png" % (str(counter).zfill(3), layer_label))
                    self.exportToPng(layer_dest_svg_path, layer_dest_png_path)

            counter += 1

    def export_layers(self, dest, show):
        """
        Export selected layers of SVG to the file `dest`.
        :arg  str   dest:  path to export SVG file.
        :arg  list  hide:  layers to hide. each element is a string.
        :arg  list  show:  layers to show. each element is a string.
        """
        doc = copy.deepcopy(self.document)
        for layer in doc.xpath('//svg:g[@inkscape:groupmode="layer"]', namespaces=inkex.NSS):
            layer.attrib['style'] = 'display:none'
            id = layer.attrib["id"]
            if id in show:
                layer.attrib['style'] = 'display:inline'

        doc.write(dest)

    def get_layers(self, src):
        svg_layers = self.document.xpath('//svg:g[@inkscape:groupmode="layer"]', namespaces=inkex.NSS)
        layers = []

        for layer in svg_layers:
            label_attrib_name = "{%s}label" % layer.nsmap['inkscape']
            if label_attrib_name not in layer.attrib:
                continue

            layer_id = layer.attrib["id"]
            layer_label = layer.attrib[label_attrib_name]

            layer_label_name = layer_label
            inkex.debug(layer_label_name)

            if  layer_label_name in self.layer_map.iterkeys():
                layer_type = "export"
                layer_label = layer_label_name
            elif layer_label.lower().startswith("[fixed] "):
                layer_type = "fixed"
                layer_label = layer_label[8:]
            else:
                continue

            layers.append([layer_id, layer_label, layer_type])

        return layers


    def exportToKicad(self, png_path, output_path, layer_type):
        plugin_path = os.path.dirname(os.path.abspath(__file__)) + "/"
        area_param = '-D' if self.options.crop else 'C'
        command =  "\"%sbitmap2component\" \"%s\" \"%s\" %s %s %s" % (plugin_path, png_path, output_path, layer_type, "true" , str(int(self.options.threshold)))
        inkex.debug(command)
        p = subprocess.Popen(command.encode("utf-8"), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()


    def exportToPng(self, svg_path, output_path):
        area_param = '-D' if self.options.crop else 'C'
        command = "inkscape %s -d %s -e \"%s\" \"%s\"" % (area_param, self.options.dpi, output_path, svg_path)

        p = subprocess.Popen(command.encode("utf-8"), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()

    def convertPngToJpg(self, png_path, output_path):
        command = "convert \"%s\" \"%s\"" % (png_path, output_path)
        p = subprocess.Popen(command.encode("utf-8"), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()


def _main():
    e = PNGExport()
    e.affect()
    exit()

if __name__ == "__main__":
    _main()