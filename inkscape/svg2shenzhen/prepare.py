#! /usr/bin/env python

import warnings
import sys
sys.path.append('/usr/share/inkscape/extensions')
import inkex
import os
import subprocess
import tempfile
import shutil
import copy
import simplepath, simpletransform

from simplestyle import *
from copy import deepcopy
from io import BytesIO
from lxml import etree

identity_m = [[1.0,0.0,0.0],[0.0,1.0,0.0]]

kicadLayers = {
    "layerDrill" : "Drill",
    "layerDwgs_user" : "Dwgs.User",
    "layerF_Silks" : "F.SilkS",
    "layerF_Paste" : "F.Paste",
    "layerF_mask" : "F.Mask",
    "layerF_cu" : "F.Cu",
    "layerB_silks" : "B.SilkS",
    "layerB_paste" : "B.Paste",
    "layerB_mask" : "B.Mask",
    "layerB_cu" : "B.Cu",
    "layerEdge_Cuts" : "Edge.Cuts",
    "layerF_Adhes" : "F.Adhes",
    "layerB_Adhes" : "B.Adhes",
    "layerCmts_User" : "Cmts.User",
    "layerEco1_User" : "Eco1.User",
    "layerEco2_User" : "Eco2.User",
    "layerMargin" : "Margin",
    "layerB_CrtYd" : "B.CrtYd",
    "layerF_CrtYd" : "F.CrtYd",
    "layerB_Fab" : "B.Fab",
    "layerF_Fab" : "F.Fab"
}
kicadLayersSelected = {}

class Svg2ShenzhenPrepare(inkex.Effect):
    def __init__(self):
        """init the effect library and get options from gui"""
        inkex.Effect.__init__(self)

        self.bb_width_center = 0
        self.bb_height_center = 0
        self.bb_scaling_h = 0
        self.bb_scaling_w = 0


    def add_arguments(self, pars):
        pars.add_argument("--docwidth", type=float, default=0.0)
        pars.add_argument("--docheight", type=float, default=0.0)
        pars.add_argument("--name")
        pars.add_argument("--docGrid")
        # Prepare the Arguments for all of the Layers 
        for key, value in kicadLayers.items():
           argumentKey = "--" + key
           pars.add_argument(argumentKey)


    def coordToKicad(self,XYCoord):
        return [
            (XYCoord[0]-self.bb_width_center)/self.bb_scaling_w,
            (XYCoord[1]-self.bb_height_center)/self.bb_scaling_h,
        ]

    def setInkscapeScaling(self):

        root = self.document.getroot()
        height = float(root.get('height').replace("mm", ""))
        width = float(root.get('width').replace("mm", ""))
        root.attrib['viewBox'] = "0 0 " + str(width) + " " + str(height)
        viewbox = root.attrib['viewBox'].split(' ')
        viewbox_h = float(viewbox[-1])
        viewbox_w = float(viewbox[-2])

        self.doc_width = width
        self.doc_height = height
        self.bb_width_center = viewbox_w/2
        self.bb_height_center = viewbox_h/2
        self.bb_scaling_h = viewbox_h/height
        self.bb_scaling_w = viewbox_w/width


    def setDocumentSquare(self, width, height):
        root = self.document.getroot()
        root.attrib['width'] = str(width) + "mm"
        root.attrib['height'] = str(height) + "mm"
        root.attrib['viewBox'] = "0 0 %f %f" % (width, width)


    def createLayer(self, layer_name):
        svg = self.document.xpath('//svg:svg',namespaces=inkex.NSS)[0]
        layer = etree.SubElement(svg, 'g')
        layer.set(inkex.addNS('label', 'inkscape'), '%s' % layer_name)
        layer.set(inkex.addNS('groupmode', 'inkscape'), 'layer')
        return layer

    def createWhitebg(self):
        rect = etree.Element(inkex.addNS('rect','svg'))
        rect.set('x', "0")
        rect.set('y', "0")
        rect.set('width', str(self.doc_width/self.bb_scaling_w))
        rect.set('height', str(self.doc_height/self.bb_scaling_h))
        style = {'fill' : '#FFFFFF', 'fill-opacity' : '1', 'stroke': 'none'}
        rect.set('style', str(inkex.Style(style)))
        return rect

    def findLayer(self, layerName):
        svg_layers = self.document.xpath('//svg:g[@inkscape:groupmode="layer"]', namespaces=inkex.NSS)
        for layer in svg_layers:
            label_attrib_name = "{%s}label" % layer.nsmap['inkscape']
            if label_attrib_name not in layer.attrib:
                continue
            if (layer.attrib[label_attrib_name] == layerName):
                return layer
        return False

    def addStamp(self,layer, textStr):

        # Create text element
        text = etree.Element(inkex.addNS('text','svg'))
        text.text = str(textStr)

        # Set text position to center of document.
        text.set('x', str(self.doc_width / 2))
        text.set('y', str(self.doc_height / 2))

        # Center text horizontally with CSS style.
        style = {'text-align' : 'center', 'text-anchor': 'middle'}
        text.set('style', str(inkex.Style(style)))

        # Connect elements together.
        layer.append(text)


    def prepareDocument(self, options):
        svg_layers = self.document.xpath('//svg:g[@inkscape:groupmode="layer"]', namespaces=inkex.NSS)
        layers = []

        root = self.document.getroot()

        #remove "Layer 1"
        for layer in svg_layers:
            label_attrib_name = "{%s}label" % layer.nsmap['inkscape']
            if label_attrib_name not in layer.attrib:
                continue
            if (layer.attrib[label_attrib_name] == "Layer 1"):
                root.remove(layer)

        for layer in svg_layers:
            label_attrib_name = "{%s}label" % layer.nsmap['inkscape']
            if label_attrib_name not in layer.attrib:
                continue
            layer_label = layer.attrib[label_attrib_name]
            layers.append(layer_label)

        if ("[fixed] BG" not in layers):
            white_layer = self.createLayer("[fixed] BG")
            white_layer.set(inkex.addNS('insensitive', 'sodipodi'), 'true')
            rect = self.createWhitebg()
            white_layer.append(rect)

        # Create the Selected Layers
        kicadLayersArray = list(kicadLayers.items());

        for key, value in reversed(kicadLayersArray):
           disabledValue = '%s-disabled' % (value)
           selectedValue = getattr(options, key)
           if selectedValue == "true" and value not in layers and disabledValue not in layers:
               self.createLayer(value)


    def setDocumentGrid(self):
        doc_view = self.document.xpath('//sodipodi:namedview',namespaces=inkex.NSS)[0]
        doc_view.attrib['borderlayer'] = "true"
        doc_view.attrib['showgrid'] = "true"

        grid = etree.Element(inkex.addNS('grid','inkscape'))
        grid.set('spacingx', '2.54')
        grid.set('spacingy', '2.54')
        grid.set('empspacing', '1')
        grid.set('type', 'xygrid')
        grid.set('units', 'mm')

        doc_view.append(grid)

    def setDefaultUnits(self):
        # just a convenience so that when you draw you will use mm by default
        namedview = self.document.find('sodipodi:namedview', namespaces=inkex.NSS)
        namedview.attrib['{http://www.inkscape.org/namespaces/inkscape}document-units'] = 'mm'

    def effect(self):
        self.setDocumentSquare(self.options.docwidth, self.options.docheight)
        self.setInkscapeScaling()
        self.prepareDocument(self.options)
        if self.options.docGrid == "true":
            self.setDocumentGrid()
        self.setDefaultUnits()
        #warnings.warn(getattr(self.options, "layerF_Silk"))

    def prepareLogo(self, lyr):
        logo_xml = """
        <g
           id="g14283">
          <g
             id="text14253"
             aria-label="Made"
             style="font-style:normal;font-variant:normal;font-weight:normal;font-stretch:normal;font-size:4.23333311px;line-height:125%;font-family:sans-serif;-inkscape-font-specification:'sans-serif, Normal';font-variant-ligatures:none;font-variant-caps:normal;font-variant-numeric:normal;text-align:start;letter-spacing:0px;word-spacing:0px;writing-mode:lr-tb;text-anchor:start;fill:#000000;fill-opacity:1;stroke:none;stroke-width:0.26458332px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1">
            <path
               id="path14275"
               style="stroke-width:0.26458332px"
               d="M 72.624153,150.78851 73.213264,150.78851 74.085562,153.35579 74.951659,150.78851 75.534569,150.78851 75.534569,153.82501 75.143895,153.82501 75.143895,152.03287 Q 75.143895,151.93986 75.148029,151.72488 75.152164,151.50991 75.152164,151.26393 L 74.286067,153.82501 73.878856,153.82501 73.006558,151.26393 73.006558,151.35695 Q 73.006558,151.46857 73.010692,151.69801 73.016893,151.92539 73.016893,152.03287 L 73.016893,153.82501 72.624153,153.82501 72.624153,150.78851 Z" />
            <path
               id="path14277"
               style="stroke-width:0.26458332px"
               d="M 76.400666,153.2359 Q 76.400666,153.39713 76.518488,153.49015 76.63631,153.58317 76.797541,153.58317 76.993911,153.58317 77.177879,153.49222 77.487938,153.34132 77.487938,152.99819 L 77.487938,152.69847 Q 77.419725,152.74187 77.312238,152.77081 77.204751,152.79975 77.101398,152.81215 L 76.876089,152.84109 Q 76.673518,152.86796 76.572232,152.92584 76.400666,153.02299 76.400666,153.2359 Z M 77.301903,152.48349 Q 77.43006,152.46696 77.473469,152.37601 77.498273,152.3264 77.498273,152.23338 77.498273,152.04321 77.361848,151.95846 77.227489,151.87164 76.975308,151.87164 76.683853,151.87164 76.561896,152.02874 76.493684,152.11556 76.473013,152.28712 L 76.125747,152.28712 Q 76.136083,151.87784 76.390331,151.71868 76.646646,151.55745 76.983576,151.55745 77.37425,151.55745 77.618163,151.70628 77.860008,151.85511 77.860008,152.1693 L 77.860008,153.44467 Q 77.860008,153.50255 77.882746,153.53769 77.907551,153.57283 77.984032,153.57283 78.008836,153.57283 78.039842,153.57076 78.070848,153.56663 78.105988,153.56043 L 78.105988,153.83535 Q 78.019172,153.86015 77.973696,153.86635 77.928221,153.87255 77.849673,153.87255 77.657437,153.87255 77.57062,153.73613 77.525145,153.66378 77.506542,153.53149 77.392853,153.68032 77.179947,153.78987 76.96704,153.89943 76.710725,153.89943 76.402733,153.89943 76.206363,153.71339 76.012059,153.52529 76.012059,153.24417 76.012059,152.93618 76.204296,152.76668 76.396532,152.59718 76.708657,152.55791 L 77.301903,152.48349 Z M 76.993911,151.55745 76.993911,151.55745 Z" />
            <path
               id="path14279"
               style="stroke-width:0.26458332px"
               d="M 78.707502,152.74394 Q 78.707502,153.09948 78.858397,153.33925 79.009292,153.57903 79.342088,153.57903 79.60047,153.57903 79.765835,153.35786 79.933267,153.13462 79.933267,152.71914 79.933267,152.29952 79.761701,152.09902 79.590135,151.89645 79.337954,151.89645 79.056834,151.89645 78.881134,152.11142 78.707502,152.3264 78.707502,152.74394 Z M 79.267674,151.57192 Q 79.521922,151.57192 79.693488,151.67941 79.792707,151.74142 79.918797,151.89645 L 79.918797,150.77817 80.276398,150.77817 80.276398,153.82501 79.941535,153.82501 79.941535,153.51702 Q 79.81131,153.72166 79.633543,153.81261 79.455776,153.90356 79.226333,153.90356 78.85633,153.90356 78.585545,153.5935 78.314761,153.28138 78.314761,152.76461 78.314761,152.28092 78.560741,151.92745 78.808787,151.57192 79.267674,151.57192 Z" />
            <path
               id="path14281"
               style="stroke-width:0.26458332px"
               d="M 81.750209,151.56158 Q 81.985854,151.56158 82.207029,151.67321 82.428204,151.78276 82.543959,151.95846 82.655581,152.12589 82.692788,152.34913 82.72586,152.5021 82.72586,152.83696 L 81.103221,152.83696 Q 81.113556,153.17389 81.262384,153.37853 81.411212,153.5811 81.723338,153.5811 82.014793,153.5811 82.188426,153.38886 82.287644,153.27724 82.328986,153.13048 L 82.694855,153.13048 Q 82.680385,153.25244 82.597703,153.40333 82.517088,153.55216 82.415802,153.64725 82.246303,153.81261 81.996189,153.87049 81.861831,153.90356 81.692332,153.90356 81.27892,153.90356 80.9916,153.60384 80.704279,153.30205 80.704279,152.76048 80.704279,152.22718 80.993667,151.89438 81.283055,151.56158 81.750209,151.56158 Z M 82.343455,152.54137 Q 82.320717,152.29952 82.238035,152.15483 82.085073,151.88611 81.727472,151.88611 81.471157,151.88611 81.297524,152.07215 81.123891,152.25612 81.113556,152.54137 L 82.343455,152.54137 Z M 81.71507,151.55745 81.71507,151.55745 Z" />
          </g>
          <g
             id="text14257"
             aria-label="Svg2sz"
             style="font-style:normal;font-variant:normal;font-weight:normal;font-stretch:normal;font-size:4.23333311px;line-height:125%;font-family:sans-serif;-inkscape-font-specification:'sans-serif, Normal';font-variant-ligatures:none;font-variant-caps:normal;font-variant-numeric:normal;text-align:start;letter-spacing:0px;word-spacing:0px;writing-mode:lr-tb;text-anchor:start;fill:#000000;fill-opacity:1;stroke:none;stroke-width:0.26458332px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1">
            <path
               id="path14262"
               style="stroke-width:0.26458332px"
               d="M 69.382842,157.68092 Q 69.397312,157.9393 69.504799,158.10053 69.709438,158.40232 70.226202,158.40232 70.457712,158.40232 70.647881,158.33618 71.015818,158.20802 71.015818,157.87729 71.015818,157.62924 70.860788,157.52382 70.703692,157.42047 70.368829,157.34399 L 69.957484,157.25097 Q 69.554408,157.16002 69.386977,157.05047 69.097589,156.8603 69.097589,156.48203 69.097589,156.07275 69.380775,155.81023 69.663962,155.54772 70.182794,155.54772 70.660284,155.54772 70.99308,155.77923 71.327943,156.00867 71.327943,156.5151 L 70.941404,156.5151 Q 70.910398,156.27119 70.809112,156.14096 70.62101,155.90325 70.170391,155.90325 69.806589,155.90325 69.647426,156.05621 69.488262,156.20918 69.488262,156.41175 69.488262,156.63499 69.674298,156.73834 69.796254,156.80449 70.226202,156.90371 L 70.652016,157.00086 Q 70.960007,157.07114 71.127439,157.19309 71.416827,157.406 71.416827,157.81115 71.416827,158.31551 71.048891,158.53255 70.683021,158.74959 70.197263,158.74959 69.630889,158.74959 69.310495,158.4602 68.990102,158.17288 68.996303,157.68092 L 69.382842,157.68092 Z M 70.213799,155.54152 70.213799,155.54152 Z" />
            <path
               id="path14264"
               style="stroke-width:0.26458332px"
               d="M 72.074151,156.44689 72.665329,158.24936 73.283379,156.44689 73.69059,156.44689 72.855499,158.66071 72.458624,158.66071 71.642136,156.44689 72.074151,156.44689 Z" />
            <path
               id="path14266"
               style="stroke-width:0.26458332px"
               d="M 74.790264,156.40761 Q 75.050713,156.40761 75.245017,156.53577 75.350437,156.60812 75.459991,156.74661 L 75.459991,156.46756 75.803122,156.46756 75.803122,158.48087 Q 75.803122,158.90255 75.679099,159.14646 75.447588,159.59708 74.804733,159.59708 74.447133,159.59708 74.20322,159.43585 73.959307,159.27669 73.930368,158.93562 L 74.30864,158.93562 Q 74.335511,159.08445 74.416127,159.16507 74.542217,159.28909 74.813002,159.28909 75.240883,159.28909 75.373174,158.9873 75.451722,158.80953 75.445521,158.35271 75.3339,158.52221 75.176804,158.6049 75.019707,158.68758 74.761325,158.68758 74.401657,158.68758 74.130873,158.43333 73.862155,158.17701 73.862155,157.5879 73.862155,157.03186 74.13294,156.71974 74.405791,156.40761 74.790264,156.40761 Z M 75.459991,157.54449 Q 75.459991,157.13315 75.290492,156.93471 75.120993,156.73628 74.858477,156.73628 74.465736,156.73628 74.321042,157.10421 74.244561,157.30058 74.244561,157.61891 74.244561,157.99305 74.395456,158.18942 74.548418,158.38372 74.804733,158.38372 75.205743,158.38372 75.36904,158.02198 75.459991,157.81735 75.459991,157.54449 Z M 74.833672,156.39314 74.833672,156.39314 Z" />
            <path
               id="path14268"
               style="stroke-width:0.26458332px"
               d="M 76.224802,158.66071 Q 76.245472,158.2783 76.381898,157.99511 76.520391,157.71193 76.919333,157.48042 L 77.316208,157.25097 Q 77.582858,157.09594 77.690345,156.98639 77.859844,156.81482 77.859844,156.59365 77.859844,156.33527 77.704815,156.18437 77.549786,156.03141 77.291403,156.03141 76.908998,156.03141 76.762237,156.3208 76.683689,156.47583 76.67542,156.75074 L 76.297149,156.75074 Q 76.30335,156.36421 76.439776,156.12029 76.681622,155.69034 77.29347,155.69034 77.801967,155.69034 78.035544,155.96526 78.271188,156.24018 78.271188,156.57711 78.271188,156.93265 78.021075,157.18483 77.876381,157.33159 77.502243,157.54036 L 77.219056,157.69746 Q 77.016485,157.80908 76.90073,157.91036 76.694024,158.0902 76.64028,158.30931 L 78.256719,158.30931 78.256719,158.66071 76.224802,158.66071 Z" />
            <path
               id="path14270"
               style="stroke-width:0.26458332px"
               d="M 78.942982,157.96617 Q 78.959519,158.15221 79.036,158.25143 79.17656,158.43126 79.523825,158.43126 79.730531,158.43126 79.887627,158.34238 80.044724,158.25143 80.044724,158.06333 80.044724,157.9207 79.918633,157.84629 79.838018,157.80081 79.600306,157.74087 L 79.304717,157.66645 Q 79.02153,157.59617 78.887172,157.50935 78.647393,157.35846 78.647393,157.09181 78.647393,156.77762 78.872702,156.58331 79.100079,156.38901 79.482484,156.38901 79.982712,156.38901 80.203887,156.68253 80.34238,156.86857 80.338246,157.08354 L 79.986846,157.08354 Q 79.976511,156.95745 79.897963,156.8541 79.769805,156.70734 79.453545,156.70734 79.242705,156.70734 79.133151,156.78795 79.025664,156.86857 79.025664,157.00086 79.025664,157.14555 79.168291,157.23237 79.250974,157.28405 79.412204,157.32332 L 79.658184,157.38326 Q 80.059193,157.48042 80.195619,157.57137 80.41266,157.71399 80.41266,158.01992 80.41266,158.31551 80.187351,158.53048 79.964108,158.74545 79.505222,158.74545 79.011195,158.74545 78.804489,158.52221 78.599851,158.2969 78.585381,157.96617 L 78.942982,157.96617 Z M 79.492819,156.39314 79.492819,156.39314 Z" />
            <path
               id="path14272"
               style="stroke-width:0.26458332px"
               d="M 80.673108,158.36718 81.98569,156.77968 80.77026,156.77968 80.77026,156.44689 82.485917,156.44689 82.485917,156.75074 81.181604,158.32791 82.525192,158.32791 82.525192,158.66071 80.673108,158.66071 80.673108,158.36718 Z M 81.630156,156.39314 81.630156,156.39314 Z" />
          </g>
        </g>
        """
        logo_file_obj = BytesIO((logo_xml))
        new_obj = (etree.parse(logo_file_obj)).getroot()
        # lyr = self.findLayer("F.Cu")
        lyr.append(new_obj)


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
    e = Svg2ShenzhenPrepare()
    e.run()
    exit()

if __name__ == "__main__":
    _main()
