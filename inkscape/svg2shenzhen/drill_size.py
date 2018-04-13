#!/usr/bin/env python

import inkex

class Svg2ShenzhenDrillSize(inkex.Effect):
    def __init__(self):
        inkex.Effect.__init__(self)
        self.OptionParser.add_option("-d", "--drillsize",
                        action="store", type="float",
                        dest="drillsize", default=0.8001,
                        help="Drill Size")
    def effect(self):
        for id, node in self.selected.iteritems():
            if node.tag == inkex.addNS('circle','svg'):
                node.set('drill', str(self.options.drillsize))
                node.set('r', str(self.options.drillsize))

if __name__ == '__main__':
    e = Svg2ShenzhenDrillSize()
    e.affect()
