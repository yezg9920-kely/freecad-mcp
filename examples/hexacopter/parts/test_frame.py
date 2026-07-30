# -*- coding: utf-8 -*-
"""test_frame.py - frame.py 无头自测"""
import sys
for p in (r"D:/claude code/freecad_hexa", r"D:/claude code/freecad_hexa/parts"):
    if p not in sys.path:
        sys.path.insert(0, p)
import FreeCAD
import frame

doc = FreeCAD.newDocument("FrameTest")
objs = frame.build(doc)
doc.recompute()

print("== FRAME TEST ==")
print("object count: %d" % len(objs))
allok = True
for o in objs:
    s = o.Shape
    bb = s.BoundBox
    valid = s.isValid()
    if not valid:
        allok = False
    print("%-18s valid=%s  X[%.1f, %.1f] Y[%.1f, %.1f] Z[%.1f, %.1f]  vol=%.0f"
          % (o.Name, valid, bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax, s.Volume))

# 总包围盒
xs = [o.Shape.BoundBox for o in objs]
print("TOTAL  X[%.1f, %.1f] Y[%.1f, %.1f] Z[%.1f, %.1f]"
      % (min(b.XMin for b in xs), max(b.XMax for b in xs),
         min(b.YMin for b in xs), max(b.YMax for b in xs),
         min(b.ZMin for b in xs), max(b.ZMax for b in xs)))
print("ALL VALID: %s" % allok)
sys.stdout.flush()
import os
os._exit(0)
