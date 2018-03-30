#! /usr/bin/env python

import sys
sys.path.append('/usr/share/inkscape/extensions')
import inkex
import os
import subprocess
import tempfile
import shutil
import copy
import simplepath, simpletransform

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

    def exportDrill(self):
        x0 = 0
        y0 = 0
        mirror = 1.0

        self.setInkscapeScaling()


        i = 0
        layerPath = '//svg:g[@inkscape:groupmode="layer"]'
        for layer in self.document.getroot().xpath(layerPath, namespaces=inkex.NSS):
            label_attrib_name = "{%s}label" % layer.nsmap['inkscape']
            if label_attrib_name not in layer.attrib:
                continue

            i += 1
            
            layer_name = (layer.attrib[label_attrib_name])

            layer_trans = layer.get('transform')
            if layer_trans:
                layer_m = simpletransform.parseTransform(layer_trans)
            else:
                layer_m = identity_m
            
            nodePath = ('//svg:g[@inkscape:groupmode="layer"][%d]/descendant::svg:circle') % i
            for node in self.document.getroot().xpath(nodePath, namespaces=inkex.NSS):
                cx = float(node.get('cx'))
                cy = float(node.get('cy'))
                t = node.get('transform')

                pt = [cx, cy]

                if t:
                    m = simpletransform.parseTransform(t)
                    trans = simpletransform.composeTransform(layer_m, m)
                else:
                    trans = layer_m

                simpletransform.applyTransformToPoint(trans,pt)
                padCoord = self.coordToKicad(pt)


                inkex.debug("(pad %d thru_hole circle (at %f %f) (size 1.524 1.524) (drill 0.762) (layers *.Cu *.Mask))" % (1, padCoord[0], padCoord[1]))

    def makeDocumentSquare(self):
        root = self.document.getroot()
        height = float(root.attrib['height'].replace("mm", ""))
        width =  float(root.attrib['width'].replace("mm", ""))

        if (width > height):
            root.attrib['height'] = str(width) + "mm"
        else:
            root.attrib['width'] = str(height) + "mm"
        

    def exportEdgeCut(self):
        x0 = 0
        y0 = 0
        mirror = 1.0

        self.makeDocumentSquare()
        self.setInkscapeScaling()


        i = 0
        layerPath = '//svg:g[@inkscape:groupmode="layer"]'
        for layer in self.document.getroot().xpath(layerPath, namespaces=inkex.NSS):
            i += 1


            label_attrib_name = "{%s}label" % layer.nsmap['inkscape']
            if label_attrib_name not in layer.attrib:
                continue

            
            layer_name = (layer.attrib[label_attrib_name])


            if layer_name != "Edge.Cut":
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

                        # inkex.debug(p[0])
                        for path in p:
                            if path[0] != "Z":
                                # inkex.debug(path[0])
                                x = (path[1][0])
                                y = (path[1][1])
                                xy = [x,y]
                                simpletransform.applyTransformToPoint(trans,xy)
                                points.append(self.coordToKicad([(xy[0]-x0), xy[1]*mirror-y0]))

                        # inkex.debug(points)

                        points_count = len(points)
                        points.append(points[0])

                        offset = 0
                        for x in range (0, points_count):
                            inkex.debug("(gr_line (start %f %f) (end %f %f) (layer Edge.Cuts) (width 0.1))"  % (points[x][0],points[x][1],points[x+1][0],points[x+1][1]))




    def effect(self):
        # self.exportDrill()
        self.exportEdgeCut()

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


def _main():
    e = PNGExport()
    e.affect()
    exit()

if __name__ == "__main__":
    _main()