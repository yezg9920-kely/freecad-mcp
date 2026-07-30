# -*- coding: utf-8 -*-
"""
motors_props.py — 电机×6 + 螺旋桨×6 模块
六旋翼（DJI S900 / Tarot T960 级），4114 级外转子电机 + 15 寸 1552 两叶桨。
电机中心位于 spec.polar(angle, spec.MOTOR_RADIUS)，angle 取 spec.ARM_ANGLES。
0/120/240° 臂为 CCW，60/180/300° 臂为 CW（扭转/后掠方向镜像）。
"""

import sys
if r"D:/claude code/freecad_hexa" not in sys.path:
    sys.path.insert(0, r"D:/claude code/freecad_hexa")
import math

import FreeCAD
import Part
import spec

# CW 臂（其余为 CCW）
CW_ANGLES = (60, 180, 300)

# ---------------- 电机局部细节尺寸（自定） ----------------
_BELL_TAPER_H = 3.0        # 上盖顶部收锥高度
_BELL_TOP_R_RATIO = 0.85   # 收锥后顶部半径比例
_SLOT_N = 8                # 散热槽数量
_SLOT_W = 4.0              # 槽宽（切向）
_SLOT_DEPTH = 6.0          # 槽切入径向深度
_SLOT_H = 12.0             # 槽高（竖直）
_SLOT_Z0 = 3.0             # 槽底距 bell 底面


def _make_motor_shapes():
    """在原点构建一个电机（轴线沿 Z，底面 Z=0 的局部坐标），
    返回 (stator, bell, shaft) 三个 shape（不同颜色分开加）。"""
    body_r = spec.MOTOR_BODY_D / 2.0
    bell_r = spec.MOTOR_BELL_D / 2.0
    bh = spec.MOTOR_BELL_H

    # 定子座（黑）
    stator = Part.makeCylinder(body_r, spec.MOTOR_BODY_H)

    # 转子上盖（银灰）：圆柱 + 顶部收锥
    z0 = spec.MOTOR_BODY_H
    bell_cyl = Part.makeCylinder(bell_r, bh - _BELL_TAPER_H,
                                 FreeCAD.Vector(0, 0, z0))
    bell_cone = Part.makeCone(bell_r, bell_r * _BELL_TOP_R_RATIO, _BELL_TAPER_H,
                              FreeCAD.Vector(0, 0, z0 + bh - _BELL_TAPER_H))
    bell = bell_cyl.fuse(bell_cone)

    # 侧面竖直散热槽（小盒体 cut，仅切圆柱段，不切穿上下）
    slot = Part.makeBox(_SLOT_DEPTH, _SLOT_W, _SLOT_H,
                        FreeCAD.Vector(bell_r - _SLOT_DEPTH + 1.0,
                                       -_SLOT_W / 2.0, z0 + _SLOT_Z0))
    cuts = []
    for k in range(_SLOT_N):
        s = slot.copy()
        s.rotate((0, 0, 0), (0, 0, 1), k * 360.0 / _SLOT_N)
        cuts.append(s)
    bell = bell.cut(cuts)

    # 顶部出轴（银）
    shaft = Part.makeCylinder(spec.MOTOR_SHAFT_D / 2.0, spec.MOTOR_SHAFT_H,
                              FreeCAD.Vector(0, 0, spec.MOTOR_BODY_H + bh))
    return stator, bell, shaft


def _blade_wire(r, chord, thick, twist_deg, dy, dz):
    """桨叶截面 wire：位于 x=r 处，弦向沿 Y，厚度沿 Z，
    绕桨叶展向轴（X 轴）扭转 twist_deg，再切向/垂向偏移。"""
    hw = chord / 2.0
    ht = thick / 2.0
    pts = [FreeCAD.Vector(r, -hw, -ht),
           FreeCAD.Vector(r, hw, -ht),
           FreeCAD.Vector(r, hw, ht),
           FreeCAD.Vector(r, -hw, ht)]
    wire = Part.makePolygon(pts + [pts[0]])
    wire.rotate((0, 0, 0), (1, 0, 0), twist_deg)
    wire.translate((0, dy, dz))
    return wire


def _make_blade(sign):
    """单片桨叶（+X 方向伸出）。sign=+1 为 CCW，-1 为 CW（扭转/后掠镜像）。
    叶根/中部/叶尖 3 截面 loft 成实体，带 12°->8° 扭转（washout）、
    叶尖后掠下垂（参考 DJI 1552 折叠桨）。"""
    prop_r = spec.PROP_DIAMETER / 2.0
    t = spec.PROP_THICK
    # (半径, 弦长, 扭转角, 后掠 dy, 下垂 dz)
    secs = [
        (spec.PROP_HUB_D / 2.0 - 1.0, spec.PROP_BLADE_W_ROOT, 12.0 * sign, 0.0, 0.0),
        (prop_r * 0.55, (spec.PROP_BLADE_W_ROOT + spec.PROP_BLADE_W_TIP) / 2.0,
         10.0 * sign, -4.0 * sign, -1.5),
        (prop_r - 4.0, spec.PROP_BLADE_W_TIP, 8.0 * sign, -12.0 * sign, -6.0),
    ]
    wires = [_blade_wire(r, c, t, tw, dy, dz) for (r, c, tw, dy, dz) in secs]
    return Part.makeLoft(wires, True)


def _make_prop_shape(sign):
    """整支螺旋桨（局部坐标，桨毂中心在原点，轴线沿 Z）：
    桨毂 + 两片对称桨叶 fuse 为一个实体。"""
    hub = Part.makeCylinder(spec.PROP_HUB_D / 2.0, spec.PROP_HUB_H,
                            FreeCAD.Vector(0, 0, -spec.PROP_HUB_H / 2.0))
    b1 = _make_blade(sign)
    b2 = b1.copy()
    b2.rotate((0, 0, 0), (0, 0, 1), 180.0)
    return hub.fuse([b1, b2])


def build(doc):
    """构建 6 电机 + 6 螺旋桨 + 6 桨夹螺母，返回创建的对象列表。"""
    objs = []
    for i, angle in enumerate(spec.ARM_ANGLES):
        cx, cy, _ = spec.polar(angle, spec.MOTOR_RADIUS)
        tag = "%03d" % i
        sign = -1.0 if angle in CW_ANGLES else 1.0

        # ---- 电机（底面 Z = MOTOR_BASE_Z） ----
        stator, bell, shaft = _make_motor_shapes()
        for shp, suffix, color in ((stator, "base", spec.C_DARK),
                                   (bell, "bell", spec.C_MOTOR),
                                   (shaft, "shaft", spec.C_SILVER)):
            shp.translate((cx, cy, spec.MOTOR_BASE_Z))
            objs.append(spec.add_part(doc, shp, "Motor_%s_%s" % (tag, suffix), color))

        # ---- 螺旋桨（桨毂中心 Z = PROP_Z，方位角错开） ----
        prop = _make_prop_shape(sign)
        prop.rotate((0, 0, 0), (0, 0, 1), angle + 15.0 + i * 7.0)
        prop.translate((cx, cy, spec.PROP_Z))
        objs.append(spec.add_part(doc, prop, "Prop_%s" % tag, spec.C_PROP))

        # ---- 顶部银色锁紧桨夹/螺母 ----
        nut = Part.makeCylinder(5.0, 5.0,
                                FreeCAD.Vector(cx, cy,
                                               spec.PROP_Z + spec.PROP_HUB_H / 2.0))
        objs.append(spec.add_part(doc, nut, "PropNut_%s" % tag, spec.C_SILVER))

    return objs
