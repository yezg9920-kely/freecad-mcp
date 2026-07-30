# -*- coding: utf-8 -*-
"""
frame.py - 中央机架模块
内容：上/下碳纤板（圆角六边形 + 镂空减重 + 臂向让位凹口）、顶板中央凸台、6 根红色铝柱。
命名前缀 Frame_。
"""
import sys
if r"D:/claude code/freecad_hexa" not in sys.path:
    sys.path.insert(0, r"D:/claude code/freecad_hexa")
import FreeCAD
import Part
import spec

# ---------------- 局部细节尺寸（非共享，可自定） ----------------
CORNER_R = 20.0            # 六边形板圆角半径
NOTCH_W = 34.0             # 臂向让位凹口宽（要求 >= 30）
NOTCH_IN_R = 95.0          # 凹口起始半径
SLOT_R_IN = 55.0           # 顶板镂空长孔内端半径（55~115 环带内）
SLOT_R_OUT = 85.0          # 顶板镂空长孔外端半径
SLOT_W = 22.0              # 长孔宽（两端圆角）
BOT_HOLE_R = 40.0          # 下板中央大孔半径
BOT_RING_HOLE_R = 18.0     # 下板环布大孔半径
BOT_RING_HOLE_DIST = 78.0  # 下板环布孔中心半径

MID_ANGLES = [a + 30.0 for a in spec.ARM_ANGLES]   # 30/90/150/210/270/330


def _rounded_hex_plate(z0, t):
    """圆角六边形板坯：顶点指向臂方位角，外接圆半径 spec.FRAME_PLATE_R。
    做法：内缩六边形棱柱 + 6 个顶点圆柱 fuse，底面在 z0。"""
    r_vert = spec.FRAME_PLATE_R - CORNER_R
    pts = [spec.polar(a, r_vert) for a in spec.ARM_ANGLES]
    vecs = [FreeCAD.Vector(*p) for p in pts]
    wire = Part.makePolygon(vecs + [vecs[0]])
    prism = Part.Face(wire).extrude(FreeCAD.Vector(0, 0, t))
    corners = []
    for a in spec.ARM_ANGLES:
        x, y, _ = spec.polar(a, r_vert)
        corners.append(Part.makeCylinder(CORNER_R, t, FreeCAD.Vector(x, y, 0)))
    plate = prism.fuse(corners).removeSplitter()
    plate.translate(FreeCAD.Vector(0, 0, z0))
    return plate


def _slot(z0, t):
    """径向圆角长孔刀具（沿 +X，两端半圆），上下各多切 1mm 防共面。"""
    w2 = SLOT_W / 2.0
    h = t + 2.0
    box = Part.makeBox(SLOT_R_OUT - SLOT_R_IN, SLOT_W, h,
                       FreeCAD.Vector(SLOT_R_IN, -w2, -1.0))
    c1 = Part.makeCylinder(w2, h, FreeCAD.Vector(SLOT_R_IN, 0, -1.0))
    c2 = Part.makeCylinder(w2, h, FreeCAD.Vector(SLOT_R_OUT, 0, -1.0))
    s = box.fuse([c1, c2])
    s.translate(FreeCAD.Vector(0, 0, z0))
    return s


def _notch(z0, t):
    """臂向让位凹口刀具（沿 +X 的矩形槽）。"""
    n = Part.makeBox(160.0 - NOTCH_IN_R, NOTCH_W, t + 2.0,
                     FreeCAD.Vector(NOTCH_IN_R, -NOTCH_W / 2.0, -1.0))
    n.translate(FreeCAD.Vector(0, 0, z0))
    return n


def build(doc):
    t = spec.FRAME_PLATE_T
    z_top = spec.FRAME_TOP_Z - t     # 上板底面
    z_bot = spec.FRAME_BOT_Z         # 下板底面
    objs = []

    # ---- 上板：镂空 6 瓣长孔（30/90/... 方向）+ 6 个臂向凹口 ----
    top = _rounded_hex_plate(z_top, t)
    cutters = []
    for a in MID_ANGLES:
        s = _slot(z_top, t)
        s.rotate((0, 0, 0), (0, 0, 1), a)
        cutters.append(s)
    for a in spec.ARM_ANGLES:
        n = _notch(z_top, t)
        n.rotate((0, 0, 0), (0, 0, 1), a)
        cutters.append(n)
    top = top.cut(cutters).removeSplitter()
    objs.append(spec.add_part(doc, top, "Frame_TopPlate", spec.C_CARBON))

    # ---- 下板：中央大孔 + 6 个环布大孔 + 6 个臂向凹口 ----
    bot = _rounded_hex_plate(z_bot, t)
    cutters = [Part.makeCylinder(BOT_HOLE_R, t + 2.0, FreeCAD.Vector(0, 0, z_bot - 1.0))]
    for a in MID_ANGLES:
        x, y, _ = spec.polar(a, BOT_RING_HOLE_DIST)
        cutters.append(Part.makeCylinder(BOT_RING_HOLE_R, t + 2.0,
                                         FreeCAD.Vector(x, y, z_bot - 1.0)))
    for a in spec.ARM_ANGLES:
        n = _notch(z_bot, t)
        n.rotate((0, 0, 0), (0, 0, 1), a)
        cutters.append(n)
    bot = bot.cut(cutters).removeSplitter()
    objs.append(spec.add_part(doc, bot, "Frame_BottomPlate", spec.C_CARBON))

    # ---- 顶板中央凸台（GPS 座安装位） ----
    boss = Part.makeCylinder(spec.BOSS_R, spec.BOSS_H,
                             FreeCAD.Vector(0, 0, spec.FRAME_TOP_Z))
    objs.append(spec.add_part(doc, boss, "Frame_Boss", spec.C_CARBON))

    # ---- 6 根红色铝柱（30/90/... 方向，半径 105，连接上下板） ----
    for i, a in enumerate(MID_ANGLES):
        x, y, _ = spec.polar(a, 105.0)
        so = Part.makeCylinder(spec.STANDOFF_D / 2.0, spec.FRAME_GAP,
                               FreeCAD.Vector(x, y, spec.FRAME_BOT_Z + t))
        objs.append(spec.add_part(doc, so, "Frame_Standoff%d" % (i + 1), spec.C_RED))

    return objs
