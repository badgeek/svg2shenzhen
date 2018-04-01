#! /usr/bin/env python

import sys
sys.path.append('/usr/share/inkscape/extensions')
import inkex
import os
import subprocess
import tempfile
import shutil
import copy
import platform
import simplepath, simpletransform
from simplestyle import *
import webbrowser

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
        self.OptionParser.add_option("--dpi", action="store", type="float", dest="dpi", default=600)
        self.OptionParser.add_option("--threshold", action="store", type="float", dest="threshold", default=128.0)
        self.OptionParser.add_option("--openfactory", action="store", type="inkbool", dest="openfactory", default="true")
        self.OptionParser.add_option("--openkicad", action="store", type="inkbool", dest="openkicad", default="true")


        self.doc_width = 0
        self.doc_height = 0

        self.bb_width_center = 0
        self.bb_height_center = 0
        self.bb_scaling = 0

        self.layer_map = {
            #'inkscape-name' : kicad-name,
            'F.Cu' :    "F.Cu",
            'B.Cu' :    "B.Cu",				
            # 'Adhes' : "{}.Adhes",
            # 'Paste' : "{}.Paste",
            'F.Silk' : "F.Silk",
            'B.Silk' : "B.Silk",				
            'F.Mask' :  "F.Mask",
            'B.Mask' :  "B.Mask",				
            # 'CrtYd' : "{}.CrtYd",
            # 'Fab' :   "{}.Fab",
            # 'Edge.Cuts' : "Edge.Cuts"
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

        self.doc_width = width
        self.doc_height = height

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
            root.attrib['viewBox'] = "0 0 %f %f" % (width, width)
        else:
            root.attrib['width'] = str(height) + "mm"
            root.attrib['viewBox'] = "0 0 %f %f" % (height, height)
    
    def createLayer(self, layer_name):
        svg = self.document.xpath('//svg:svg',namespaces=inkex.NSS)[0]
        layer = inkex.etree.SubElement(svg, 'g')
        layer.set(inkex.addNS('label', 'inkscape'), '%s' % layer_name)
        layer.set(inkex.addNS('groupmode', 'inkscape'), 'layer')

    def createWhitebg(self, layer):
        rect = inkex.etree.Element(inkex.addNS('rect','svg'))
        rect.set('x', "0")
        rect.set('y', "0")
        rect.set('width', str(self.doc_width/self.bb_scaling))
        rect.set('height', str(self.doc_height/self.bb_scaling))
        style = {'fill' : '#FFFFFF', 'fill-opacity' : '1', 'stroke': 'none'}
        rect.set('style', formatStyle(style))
        layer.append(rect)

    def prepareDocument(self):
        layer = self.createLayer("[fixed] BG")
        layer.set(inkex.addNS('insensitive', 'sodipodi'), 'true')
        self.createWhitebg(layer)
        self.createLayer("Edge.Cuts")                     
        self.createLayer("B.Cu-disabled")
        self.createLayer("B.Mask-disabled")
        self.createLayer("B.Silk-disabled")                        
        self.createLayer("F.Cu")
        self.createLayer("F.Mask-disabled")        
        self.createLayer("F.Silk-disabled")   
        self.createLayer("Drill")   

    def effect(self):
        self.setDocumentSquare()
        self.setInkscapeScaling()
        self.processExportLayer()
        if (self.options.openfactory):
            webbrowser.open("https://www.pcbway.com/setinvite.aspx?inviteid=54747", new = 2)
        # inkex.debug(self.exportDrill())

    def processExportLayer(self):
        output_path = os.path.expanduser(self.options.path)
        curfile = self.args[-1]
        layers = self.get_layers(curfile)
        counter = 1

        kicad_mod_files = []

        for (layer_id, layer_label, layer_type) in layers:
            if layer_type == "fixed":
                continue

            show_layer_ids = [layer[0] for layer in layers if layer[2] == "fixed" or layer[0] == layer_id]

            if not os.path.exists(os.path.join(output_path)):
                os.makedirs(os.path.join(output_path))
            
            invert = "true"

            if ("-invert" in layer_label):
                layer_label = layer_label.replace("-invert", "")
                invert = "false"

            fd, layer_dest_svg_path = tempfile.mkstemp()
            try:
                with open(layer_dest_svg_path, 'w') as f:
                    self.export_layers(layer_dest_svg_path, show_layer_ids)
                # close the file descriptor
                os.close(fd)
                if self.options.filetype == "kicad_pcb":
                    png_dest_kicad_path = os.path.join(output_path, "%s_%s.png" % (str(counter).zfill(3), layer_label))
                    self.exportToPng(layer_dest_svg_path, png_dest_kicad_path)
                    layer_dest_kicad_path = os.path.join(output_path, "%s_%s.kicad_module" % (str(counter).zfill(3), layer_label))
                    self.exportToKicad(png_dest_kicad_path, layer_dest_kicad_path, layer_label, invert )
                    kicad_mod_files.append(layer_dest_kicad_path)
                elif self.options.filetype == "kicad_module":
                        inkex.debug("kicad_module not implemented")
                else:
                    layer_dest_png_path = os.path.join(output_path, "%s_%s.png" % (str(counter).zfill(3), layer_label))
                    self.exportToPng(layer_dest_svg_path, layer_dest_png_path)
            finally:
                # print "ok"
                os.remove(layer_dest_svg_path)

            counter = counter + 1

        

        kicad_edgecut_string = self.exportEdgeCut()
        kicad_drill_string = self.exportDrill()
        kicad_modules_string = ""

        for kicad_file in kicad_mod_files:
            with open(kicad_file, 'r') as myfile:
                kicad_modules_string = kicad_modules_string + myfile.read()

        kicad_pcb_path = os.path.join(output_path, "compiled.kicad_pcb" )
        with open(kicad_pcb_path, 'w') as the_file:
            the_file.write(pcb_header)
            the_file.write(kicad_modules_string)
            the_file.write(kicad_edgecut_string)
            the_file.write(kicad_drill_string)
            the_file.write(pcb_footer)

        if (self.options.openkicad):
            self.openKicad(kicad_pcb_path)
        
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

            layer_label_name = layer_label.replace("-invert", "")
            # inkex.debug(layer_label_name)
            
            if  layer_label_name in self.layer_map.iterkeys():
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
            command = "xda-open %s" % (kicad_file_path)
        else:
            command = "start %s" % (kicad_file_path)

        p = subprocess.Popen(command.encode("utf-8"), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()



    def exportToKicad(self, png_path, output_path, layer_type, invert = "true"):
        plugin_path = os.path.dirname(os.path.abspath(__file__))

        platform_system = platform.system() 

        if (platform_system == 'Darwin'):
            bitmap2component_exe = os.path.join(plugin_path, 'bitmap2component_osx')
        elif (platform_system == 'Linux'):
            bitmap2component_exe = os.path.join(plugin_path, 'bitmap2component_linux64')
        else:
            bitmap2component_exe = os.path.join(plugin_path, 'bitmap2component.exe')

        command =  "\"%s\" \"%s\" \"%s\" %s %s %s %s" % (bitmap2component_exe, png_path, output_path, layer_type, invert , str(int(self.options.dpi)) , str(int(self.options.threshold)))
        inkex.debug(command)
        p = subprocess.Popen(command.encode("utf-8"), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()


    def exportToPng(self, svg_path, output_path):
        area_param = '-D' if self.options.crop else 'C'
        command = "inkscape %s -d %s -e \"%s\" \"%s\"" % (area_param, self.options.dpi, output_path, svg_path)

        p = subprocess.Popen(command.encode("utf-8"), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()


    def exportEdgeCut(self):
        x0 = 0
        y0 = 0
        mirror = 1.0

        kicad_edgecut_string = ""

        i = 0
        layerPath = '//svg:g[@inkscape:groupmode="layer"]'
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
                layer_m = simpletransform.parseTransform(layer_trans)
            else:
                layer_m = identity_m
            
            nodePath = ('//svg:g[@inkscape:groupmode="layer"][%d]/descendant::svg:path') % i
            for node in self.document.getroot().xpath(nodePath, namespaces=inkex.NSS):
                d = node.get('d')
                p = simplepath.parsePath(d)

                points = []
                if p:
                    #sanity check
                    if p[0][0] == 'M':
                        t = node.get('transform')
                        if t:
                            m = simpletransform.parseTransform(t)
                            trans = simpletransform.composeTransform(layer_m, m)
                        else:
                            trans = layer_m

                        for path in p:
                            if path[0] != "Z":
                                x = (path[1][0])
                                y = (path[1][1])
                                xy = [x,y]
                                simpletransform.applyTransformToPoint(trans,xy)
                                points.append(self.coordToKicad([(xy[0]-x0), xy[1]*mirror-y0]))

                        points_count = len(points)
                        points.append(points[0])

                        for x in range (0, points_count):
                            kicad_edgecut_string = kicad_edgecut_string + ("(gr_line (start %f %f) (end %f %f) (layer Edge.Cuts) (width 0.1))\n"  % (points[x][0],points[x][1],points[x+1][0],points[x+1][1]))
        
        return kicad_edgecut_string

    def exportDrill(self):
        x0 = 0
        y0 = 0
        mirror = 1.0

        self.setInkscapeScaling()

        kicad_drill_string = ""

        i = 0

        pad_template = """
            (module Wire_Pads:SolderWirePad_single_0-8mmDrill (layer F.Cu) (tedit 0) (tstamp 5ABD66D0)
                (at %f %f)
                (pad %d thru_hole circle (at 0 0) (size 1.99898 1.99898) (drill %f) (layers *.Cu *.Mask))
            )
        """

        layerPath = '//svg:g[@inkscape:groupmode="layer"]'
        for layer in self.document.getroot().xpath(layerPath, namespaces=inkex.NSS):
            label_attrib_name = "{%s}label" % layer.nsmap['inkscape']
            if label_attrib_name not in layer.attrib:
                continue
            i += 1

            layer_name = (layer.attrib[label_attrib_name])

            if layer_name != "Drill":
                continue


            layer_trans = layer.get('transform')
            if layer_trans:
                layer_m = simpletransform.parseTransform(layer_trans)
            else:
                layer_m = identity_m
            
            nodePath = ('//svg:g[@inkscape:groupmode="layer"][%d]/descendant::svg:circle') % i

            count = 0
            for node in self.document.getroot().xpath(nodePath, namespaces=inkex.NSS):
                count = count + 1
                cx = float(node.get('cx'))
                cy = float(node.get('cy'))

                # if (node.get('rx') and node.get('ry')):
                #     rx = float(node.get('rx'))
                #     ry = float(node.get('ry'))

                radius = float(node.get('r'))
                t = node.get('transform')

                pt = [cx, cy]

                if t:
                    m = simpletransform.parseTransform(t)
                    trans = simpletransform.composeTransform(layer_m, m)
                else:
                    trans = layer_m

                drill_size = node.get('drill')

                if (not drill_size):
                    drill_size = 0.8001

                simpletransform.applyTransformToPoint(trans,pt)
                padCoord = self.coordToKicad(pt)

                kicad_drill_string = kicad_drill_string + (pad_template % (padCoord[0], padCoord[1], count, float(drill_size) ))
            
            return kicad_drill_string
        
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