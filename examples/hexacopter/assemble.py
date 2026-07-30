# -*- coding: utf-8 -*-
"""
Hexacopter 总装配执行脚本：在 FreeCAD 中新建文档，依次调用各部件模块的 build(doc)，
保存 FCStd 并输出验证截图到 freecad_hexa/shots/。
通过 MCP execute_code 执行：exec(open(r"D:/claude code/freecad_hexa/assemble.py", encoding="utf-8").read())
"""
import importlib.util
import os
import sys
import traceback

import FreeCAD

BASE = os.path.dirname(os.path.abspath(__file__))
DOC_NAME = "Hexacopter"
PART_FILES = [
    "frame.py",
    "arms.py",
    "motors_props.py",
    "landing_gear.py",
    "gps_gimbal.py",
]

if BASE not in sys.path:
    sys.path.insert(0, BASE)

# 重建文档
old = FreeCAD.listDocuments().get(DOC_NAME)
if old is not None:
    FreeCAD.closeDocument(DOC_NAME)
doc = FreeCAD.newDocument(DOC_NAME)

results = {}
for fname in PART_FILES:
    path = os.path.join(BASE, "parts", fname)
    mod_name = "hx_" + fname.replace(".py", "")
    try:
        specmod = importlib.util.spec_from_file_location(mod_name, path)
        mod = importlib.util.module_from_spec(specmod)
        specmod.loader.exec_module(mod)
        objs = mod.build(doc)
        results[fname] = "OK (%d objs)" % len(objs)
    except Exception:
        results[fname] = "FAIL\n" + traceback.format_exc()

doc.recompute()

# 保存
fcstd = os.path.join(BASE, "Hexacopter.FCStd")
doc.saveAs(fcstd)

# 截图验证
shot_dir = os.path.join(BASE, "shots")
os.makedirs(shot_dir, exist_ok=True)
shot_report = []
try:
    import FreeCADGui as Gui
    view = Gui.ActiveDocument.ActiveView
    for viewname, setter in [
        ("iso", "viewIsometric"),
        ("front", "viewFront"),
        ("top", "viewTop"),
    ]:
        getattr(view, setter)()
        view.fitAll()
        p = os.path.join(shot_dir, viewname + ".png")
        view.saveImage(p, 1600, 1200, "Black")
        shot_report.append(p)
except Exception:
    shot_report.append("SHOT_FAIL\n" + traceback.format_exc())

report = ["== ASSEMBLY REPORT =="]
for k, v in results.items():
    report.append("%s: %s" % (k, v))
report.append("total objects: %d" % len(doc.Objects))
report.append("saved: %s" % fcstd)
report.extend(shot_report)
with open(os.path.join(BASE, "report.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(report))
print("\n".join(report))
