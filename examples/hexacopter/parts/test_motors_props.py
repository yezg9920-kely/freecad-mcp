# -*- coding: utf-8 -*-
"""motors_props 模块自测：无头 FreeCAD 运行"""
import sys
if r"D:/claude code/freecad_hexa" not in sys.path:
    sys.path.insert(0, r"D:/claude code/freecad_hexa")
import FreeCAD
import motors_props

doc = FreeCAD.newDocument("test_motors_props")
objs = motors_props.build(doc)
doc.recompute()

print("object count:", len(objs))

bad = 0
xmin = ymin = zmin = 1e18
xmax = ymax = zmax = -1e18
for o in objs:
    bb = o.Shape.BoundBox
    ok = o.Shape.isValid()
    # NaN / 异常检查
    vals = [bb.XMin, bb.YMin, bb.ZMin, bb.XMax, bb.YMax, bb.ZMax]
    sane = all(v == v and abs(v) < 1e6 for v in vals)
    if not ok or not sane:
        bad += 1
    print("%-18s valid=%s bbox X[%.1f, %.1f] Y[%.1f, %.1f] Z[%.1f, %.1f]" % (
        o.Name, ok, bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax))
    xmin = min(xmin, bb.XMin); xmax = max(xmax, bb.XMax)
    ymin = min(ymin, bb.YMin); ymax = max(ymax, bb.YMax)
    zmin = min(zmin, bb.ZMin); zmax = max(zmax, bb.ZMax)

print("TOTAL bbox X[%.1f, %.1f] Y[%.1f, %.1f] Z[%.1f, %.1f]" % (
    xmin, xmax, ymin, ymax, zmin, zmax))
print("invalid/insane objects:", bad)
print("TEST", "FAILED" if bad else "PASSED")

import os
sys.stdout.flush()
sys.stderr.flush()
os._exit(0)
