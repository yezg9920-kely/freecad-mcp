# -*- coding: utf-8 -*-
"""test_arms.py - 机臂模块无头自测：build -> recompute -> BoundBox 汇总"""
import sys
if r"D:/claude code/freecad_hexa" not in sys.path:
    sys.path.insert(0, r"D:/claude code/freecad_hexa")
import importlib.util
import math

import FreeCAD

specmod = importlib.util.spec_from_file_location(
    "hx_arms", r"D:/claude code/freecad_hexa/parts/arms.py")
mod = importlib.util.module_from_spec(specmod)
specmod.loader.exec_module(mod)

doc = FreeCAD.newDocument("ArmsTest")
objs = mod.build(doc)
doc.recompute()

print("object count: %d" % len(objs))

xmin = ymin = zmin = 1e18
xmax = ymax = zmax = -1e18
bad = []
for o in objs:
    bb = o.Shape.BoundBox
    vals = (bb.XMin, bb.YMin, bb.ZMin, bb.XMax, bb.YMax, bb.ZMax)
    if any(math.isnan(v) or math.isinf(v) for v in vals):
        bad.append(o.Name)
    print("%-24s X[%8.2f,%8.2f] Y[%8.2f,%8.2f] Z[%7.2f,%7.2f] valid=%s" % (
        o.Name, bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax,
        o.Shape.isValid()))
    xmin = min(xmin, bb.XMin); xmax = max(xmax, bb.XMax)
    ymin = min(ymin, bb.YMin); ymax = max(ymax, bb.YMax)
    zmin = min(zmin, bb.ZMin); zmax = max(zmax, bb.ZMax)

print("TOTAL bbox X[%.2f, %.2f] Y[%.2f, %.2f] Z[%.2f, %.2f]" % (
    xmin, xmax, ymin, ymax, zmin, zmax))
if bad:
    print("BAD NaN/Inf objects: %s" % bad)
    sys.stdout.flush()
    raise SystemExit(1)
print("TEST OK")
sys.stdout.flush()

import os
os._exit(0)
