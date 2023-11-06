#!/usr/bin/env python3

"""generate an openscad-compatible layout to adapt Kicad PCBs
   to OpenSCAD.
   Aris Adamantiadis 2023"""

import sys
import glom
from kicad_parser import parse

def main(args):
    xmin=999999999999
    ymin=xmin
    p=parse(args[0])
    #print("List of components in pcb:")
    modules = glom.glom(p, ("kicad_pcb.module"))
    for m in modules:
        #print(m["name"])
        #print(m['at'])
        xmin=min(xmin, float(m['at'][0]))
        ymin=min(ymin, float(m['at'][1]))
    #pp(p)
    cuts = glom.glom(p, ("kicad_pcb.gr_line"))
    print("All edge lines:")
    edges = set()
    for c in cuts:
        if c["layer"]=="Edge.Cuts":
            print(c["start"], c["end"])
            a = c["start"]
            b = c["end"]
            edges.add(tuple(a))
            edges.add(tuple(b))
            for i in a,b:
                xmin=min(xmin, float(i[0]))
                ymin=min(ymin, float(i[1]))

    print("Minimum coordinate", xmin, ymin)
    print("Converting everything to (0,0)")
    print()
    print("/* copy paste this in your openscad header */")
    for i, (x,y) in enumerate(edges):
        x = float(x) - xmin
        y = float(y) - ymin
        print(f"edge_{i} = [{x:.5g}, {y:.5g}];")
    for i, m in enumerate(modules):
        print(f'/* {m["name"]} */')
        x = float(m["at"][0]) - xmin
        y = float(m["at"][1]) - ymin
        print(f"m_{i} = [{x:.5g}, {y:.5g}];")

if __name__=="__main__":
    main(sys.argv[1:])
