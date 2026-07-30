# -*- coding: utf-8 -*-
"""gps_gimbal 模块自测：建文档、build、recompute、检查包围盒与有效性"""
import sys
if r"D:/claude code/freecad_hexa" not in sys.path:
    sys.path.insert(0, r"D:/claude code/freecad_hexa")
if r"D:/claude code/freecad_hexa/parts" not in sys.path:
    sys.path.insert(0, r"D:/claude code/freecad_hexa/parts")
import FreeCAD
import gps_gimbal

doc = FreeCAD.newDocument("test_gps_gimbal")
parts = gps_gimbal.build(doc)
doc.recompute()

print("object count: %d" % len(parts))
bad = 0
for o in parts:
    bb = o.Shape.BoundBox
    ok = o.Shape.isValid()
    vals = (bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax)
    nan = any(v != v for v in vals)
    if not ok or nan:
        bad += 1
    print("%-14s valid=%s  X[%8.2f,%8.2f] Y[%8.2f,%8.2f] Z[%8.2f,%8.2f]" % (
        o.Name, ok, *vals))

# 总包围盒
xs = [o.Shape.BoundBox for o in parts]
print("TOTAL  X[%.2f, %.2f] Y[%.2f, %.2f] Z[%.2f, %.2f]" % (
    min(b.XMin for b in xs), max(b.XMax for b in xs),
    min(b.YMin for b in xs), max(b.YMax for b in xs),
    min(b.ZMin for b in xs), max(b.ZMax for b in xs)))
print("RESULT: %s" % ("PASS" if bad == 0 else "FAIL(%d)" % bad))

import os, sys as _s
_s.stdout.flush()
os._exit(0)
