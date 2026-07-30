# -*- coding: utf-8 -*-
"""
landing_gear.py — 起落架模块（雪橇式高脚架，总高 spec.LANDING_H=360）
命名前缀 LG_。Z 向上，原点在机架中心，单位 mm。

组成：
  1. 底部横滑管 x2（黑色 C_SKID，Ø16 x 460，沿 X，Y=±180，中心 Z=SKID_Z）
     两端黑色海绵套（Ø22 x 60，C_DARK）
  2. 竖撑 x4（银白 C_TUBE，Ø14），X=±130 / Y=±180 处自横管上方起，
     向上外倾 spec.STRUT_TILT_DEG≈15°（在竖直-径向平面内），顶端到机架下板下方
  3. 红色 T 型管夹 x4（C_RED，盒体 + 两正交圆孔 cut 示意 CNC 三通）
  4. 顶部红色安装座 x4（C_RED，盒体+耳片）+ 小螺栓（C_DARK）
"""

import sys
if r"D:/claude code/freecad_hexa" not in sys.path:
    sys.path.insert(0, r"D:/claude code/freecad_hexa")
import math

import FreeCAD
import Part
import spec

# ---------------- 局部细节尺寸（自定） ----------------
SLEEVE_D = 22.0          # 海绵套外径
SLEEVE_LEN = 60.0        # 海绵套长度
CLAMP_L = 46.0           # T 型管夹沿 X 长度
CLAMP_W = 34.0           # T 型管夹沿 Y 宽度
MOUNT_W = 34.0           # 顶部安装座宽度
MOUNT_L = 30.0           # 顶部安装座长度（径向）
MOUNT_H = 18.0           # 顶部安装座高度
MOUNT_EAR = 14.0         # 耳片伸出长度
BOLT_D = 5.0             # 安装座小螺栓直径
BOLT_H = 10.0            # 螺栓露出高度


def _cyl_x(radius, length, center):
    """沿 X 方向的圆柱，中心在 center=(x,y,z)"""
    s = Part.makeCylinder(radius, length)
    s.rotate((0, 0, 0), (0, 1, 0), 90)  # +Z -> +X
    s.translate((center[0] - length / 2.0, center[1], center[2]))
    return s


def _strut_geometry(sx, sy):
    """返回单根竖撑的 (底点, 顶点, 方向, 长度)。sx/sy = ±1"""
    bx = sx * 130.0
    by = sy * (spec.SKID_SPACING / 2.0)
    bz = spec.SKID_Z + spec.SKID_TUBE_D / 2.0          # 从横管上表面起
    tz = spec.FRAME_BOT_Z                              # 顶到机架下板
    h = tz - bz
    # 在“竖直-径向”平面内外倾（顶端向机架中心收）
    shift = h * math.tan(math.radians(spec.STRUT_TILT_DEG))
    r_xy = math.hypot(bx, by)
    ux, uy = bx / r_xy, by / r_xy                      # 底部径向单位向量
    tx, ty = bx - shift * ux, by - shift * uy
    base = FreeCAD.Vector(bx, by, bz)
    top = FreeCAD.Vector(tx, ty, tz)
    direction = (top - base)
    length = direction.Length
    direction.normalize()
    return base, top, direction, length


def build(doc):
    objs = []

    # ---------- 1. 横滑管 x2 + 海绵套 x4 ----------
    for i, sy in enumerate((-1, 1)):
        y = sy * (spec.SKID_SPACING / 2.0)
        skid = _cyl_x(spec.SKID_TUBE_D / 2.0, spec.SKID_LEN, (0, y, spec.SKID_Z))
        objs.append(spec.add_part(doc, skid, "LG_Skid_%d" % (i + 1), spec.C_SKID))
        for j, sx in enumerate((-1, 1)):
            cx = sx * (spec.SKID_LEN / 2.0 - SLEEVE_LEN / 2.0)
            sleeve = _cyl_x(SLEEVE_D / 2.0, SLEEVE_LEN, (cx, y, spec.SKID_Z))
            objs.append(spec.add_part(
                doc, sleeve, "LG_Sleeve_%d%d" % (i + 1, j + 1), spec.C_DARK))

    # ---------- 2~4. 竖撑 / T 型管夹 / 顶部安装座 ----------
    for sx in (-1, 1):
        for sy in (-1, 1):
            tag = "%s%s" % ("F" if sx > 0 else "R", "L" if sy > 0 else "R")
            base, top, direction, length = _strut_geometry(sx, sy)

            # 竖撑：底在横管上表面，顶与安装座顶面/机架下板齐平
            strut = Part.makeCylinder(spec.STRUT_TUBE_D / 2.0,
                                      length, base, direction)
            objs.append(spec.add_part(doc, strut, "LG_Strut_" + tag, spec.C_TUBE))

            # T 型管夹：盒体环抱横管（X 向孔）与竖撑（沿竖撑方向孔）
            cx, cy = sx * 130.0, sy * (spec.SKID_SPACING / 2.0)
            cz = spec.SKID_Z
            box = Part.makeBox(CLAMP_L, CLAMP_W, spec.STRUT_CLAMP_H,
                               FreeCAD.Vector(cx - CLAMP_L / 2.0,
                                              cy - CLAMP_W / 2.0,
                                              cz - spec.STRUT_CLAMP_H / 2.0))
            hole_skid = _cyl_x(spec.SKID_TUBE_D / 2.0 + 0.25,
                               CLAMP_L + 4.0, (cx, cy, cz))
            hole_strut = Part.makeCylinder(spec.STRUT_TUBE_D / 2.0 + 0.25,
                                           spec.STRUT_CLAMP_H * 2.5,
                                           FreeCAD.Vector(cx, cy, cz) - direction * spec.STRUT_CLAMP_H,
                                           direction)
            clamp = box.cut(hole_skid).cut(hole_strut)
            clamp = clamp.removeSplitter()
            objs.append(spec.add_part(doc, clamp, "LG_Clamp_" + tag, spec.C_RED))

            # 顶部安装座：主体盒（顶面贴机架下板）+ 耳片 + 小螺栓
            ux, uy = top.x / math.hypot(top.x, top.y), top.y / math.hypot(top.x, top.y)
            body = Part.makeBox(MOUNT_L, MOUNT_W, MOUNT_H,
                                FreeCAD.Vector(-MOUNT_L / 2.0, -MOUNT_W / 2.0, -MOUNT_H))
            # 让盒体长轴沿径向
            ang = math.degrees(math.atan2(uy, ux))
            body.rotate((0, 0, 0), (0, 0, 1), ang)
            body.translate((top.x, top.y, spec.FRAME_BOT_Z))
            ear = Part.makeBox(MOUNT_EAR, MOUNT_W * 0.6, MOUNT_H * 0.6,
                               FreeCAD.Vector(MOUNT_L / 2.0 - 2.0,
                                              -MOUNT_W * 0.3, -MOUNT_H * 0.6))
            ear.rotate((0, 0, 0), (0, 0, 1), ang)
            ear.translate((top.x, top.y, spec.FRAME_BOT_Z))
            mount = body.fuse(ear).removeSplitter()
            objs.append(spec.add_part(doc, mount, "LG_Mount_" + tag, spec.C_RED))

            bolt = Part.makeCylinder(BOLT_D / 2.0, BOLT_H,
                                     FreeCAD.Vector(top.x, top.y,
                                                    spec.FRAME_BOT_Z - BOLT_H * 0.4))
            objs.append(spec.add_part(doc, bolt, "LG_Bolt_" + tag, spec.C_DARK))

    return objs
