# -*- coding: utf-8 -*-
"""test_landing_gear.py — 起落架模块自测（无头 FreeCAD 运行）"""
import sys
if r"D:/claude code/freecad_hexa" not in sys.path:
    sys.path.insert(0, r"D:/claude code/freecad_hexa")
if r"D:/claude code/freecad_hexa/parts" not in sys.path:
    sys.path.insert(0, r"D:/claude code/freecad_hexa/parts")
import math

import FreeCAD
import landing_gear
import spec

doc = FreeCAD.newDocument("LG_Test")
objs = landing_gear.build(doc)
doc.recompute()

print("=== landing_gear self-test ===")
print("object count: %d" % len(objs))

xmin = ymin = zmin = 1e18
xmax = ymax = zmax = -1e18
bad = 0
for o in objs:
    bb = o.Shape.BoundBox
    ok = o.Shape.isValid()
    nan = any(math.isnan(v) or math.isinf(v) for v in
              (bb.XMin, bb.YMin, bb.ZMin, bb.XMax, bb.YMax, bb.ZMax))
    if not ok or nan:
        bad += 1
    print("%-16s valid=%s  X[%.1f, %.1f] Y[%.1f, %.1f] Z[%.1f, %.1f]" % (
        o.Name, ok, bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax))
    xmin = min(xmin, bb.XMin); xmax = max(xmax, bb.XMax)
    ymin = min(ymin, bb.YMin); ymax = max(ymax, bb.YMax)
    zmin = min(zmin, bb.ZMin); zmax = max(zmax, bb.ZMax)

print("total bbox: X[%.1f, %.1f] Y[%.1f, %.1f] Z[%.1f, %.1f]" %
      (xmin, xmax, ymin, ymax, zmin, zmax))
print("expected roughly: X±230  Y±191  Z[%.1f, %.1f]" %
      (spec.SKID_Z - spec.SKID_TUBE_D / 2.0, spec.FRAME_BOT_Z))
print("invalid/NaN objects: %d" % bad)
print("PASS" if bad == 0 else "FAIL")
sys.stdout.flush()
sys.stderr.flush()

import os
os._exit(0)
