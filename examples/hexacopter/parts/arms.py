# -*- coding: utf-8 -*-
"""
arms.py - 六旋翼机臂模块（6 根，60° 等角放射）
内容：
  1. 臂管 x6：空心碳管（外圆柱 cut 内圆柱），ARM_ROOT_R -> ARM_TIP_R，中心高 ARM_Z
  2. 臂根红色连接块 x6：盒体 + 圆管让位孔 + 两端圆角，各带 2 颗 Ø4 小螺栓（C_DARK）
  3. 电机座红色夹紧件 x6：抱箍（带孔块体）+ 顶部电机安装平板（4 个 M3 安装孔示意）
命名带方位角后缀，如 Arm_Tube_060。
坐标约定：局部 X 沿臂方向（径向向外），Y 切向，Z 向上；整体绕 Z 旋转 ARM_ANGLES 放置。
"""

import sys
if r"D:/claude code/freecad_hexa" not in sys.path:
    sys.path.insert(0, r"D:/claude code/freecad_hexa")
import math

import FreeCAD
import Part
import spec


def _fused_fillet(shape, face_pick, radius):
    """对满足 face_pick(shape.Faces[i]) 的面的所有边做圆角，失败则原样返回。"""
    edges = []
    for face in shape.Faces:
        if face_pick(face):
            edges.extend(face.Edges)
    try:
        out = shape.makeFillet(radius, edges)
        if out.isValid():
            return out
    except Exception:
        pass
    return shape


def _make_tube(angle_deg):
    """空心臂管：外圆柱 - 内圆柱（径向，壁厚 1.5）。"""
    od = spec.ARM_TUBE_OD
    idd = spec.ARM_TUBE_ID
    r0 = spec.ARM_ROOT_R
    r1 = spec.ARM_TIP_R
    z = spec.ARM_Z
    outer = Part.makeCylinder(od / 2.0, r1 - r0,
                              FreeCAD.Vector(r0, 0, z), FreeCAD.Vector(1, 0, 0))
    # 内孔两端各加长 1mm，避免共面布尔精度问题
    inner = Part.makeCylinder(idd / 2.0, r1 - r0 + 2.0,
                              FreeCAD.Vector(r0 - 1.0, 0, z), FreeCAD.Vector(1, 0, 0))
    tube = outer.cut(inner)
    tube.rotate((0, 0, 0), (0, 0, 1), angle_deg)
    return tube


def _make_root_block(angle_deg):
    """臂根红色连接块：盒体环抱管根，让位孔 + 两端圆角。"""
    L = spec.ARM_ROOT_BLOCK_L
    W = spec.ARM_ROOT_BLOCK_W
    H = spec.ARM_ROOT_BLOCK_H
    cx = spec.ARM_ROOT_R + L / 2.0
    z = spec.ARM_Z
    od = spec.ARM_TUBE_OD

    blk = Part.makeBox(L, W, H, FreeCAD.Vector(cx - L / 2.0, -W / 2.0, z - H / 2.0))
    # 两端（X 法向面）圆角
    blk = _fused_fillet(
        blk,
        lambda f: abs(abs(f.normalAt(0.5, 0.5).x) - 1.0) < 1e-6,
        2.0,
    )
    # 管让位孔：径向圆柱，直径比管外径大 0.6mm，沿臂贯通
    hole = Part.makeCylinder(od / 2.0 + 0.3, L + 4.0,
                             FreeCAD.Vector(cx - L / 2.0 - 2.0, 0, z),
                             FreeCAD.Vector(1, 0, 0))
    blk = blk.cut(hole)
    blk.rotate((0, 0, 0), (0, 0, 1), angle_deg)
    return blk


def _make_root_bolts(angle_deg):
    """臂根连接块顶面 2 颗 Ø4 小螺栓（C_DARK），沿臂方向排布。"""
    L = spec.ARM_ROOT_BLOCK_L
    H = spec.ARM_ROOT_BLOCK_H
    cx = spec.ARM_ROOT_R + L / 2.0
    z_top = spec.ARM_Z + H / 2.0
    bolts = []
    for dx in (-L / 4.0, L / 4.0):
        b = Part.makeCylinder(2.0, 5.0, FreeCAD.Vector(cx + dx, 0, z_top))
        b.rotate((0, 0, 0), (0, 0, 1), angle_deg)
        bolts.append(b)
    return bolts


def _make_motor_clamp(angle_deg):
    """电机座红色夹紧件：带孔抱箍块 + 顶部电机安装平板（4xM3 孔）。"""
    L = spec.MOTOR_MOUNT_L
    W = spec.MOTOR_MOUNT_W
    H = spec.MOTOR_MOUNT_H
    od = spec.ARM_TUBE_OD
    cx = spec.ARM_TIP_R + 2.0            # 箍中心略过管末端
    z = spec.ARM_Z
    plate_top = spec.MOTOR_BASE_Z        # 平板顶面 = 电机底面高度
    plate_t = 3.0
    plate_size = 46.0

    # 抱箍块体（平板以下高度），让位管孔
    block_h = plate_top - plate_t - (z - H / 2.0)
    blk = Part.makeBox(L, W, block_h,
                       FreeCAD.Vector(cx - L / 2.0, -W / 2.0, z - H / 2.0))
    blk = _fused_fillet(
        blk,
        lambda f: abs(abs(f.normalAt(0.5, 0.5).x) - 1.0) < 1e-6,
        2.0,
    )
    hole = Part.makeCylinder(od / 2.0 + 0.3, L + 4.0,
                             FreeCAD.Vector(cx - L / 2.0 - 2.0, 0, z),
                             FreeCAD.Vector(1, 0, 0))
    blk = blk.cut(hole)

    # 顶部电机安装平板 46x46x3
    plate = Part.makeBox(plate_size, plate_size, plate_t,
                         FreeCAD.Vector(cx - plate_size / 2.0, -plate_size / 2.0,
                                        plate_top - plate_t))
    blk = blk.fuse(plate)

    # 4 个 M3 安装孔：Ø3，19/25mm 孔距（对角布局，x 向 19、y 向 25）
    for dx in (-9.5, 9.5):
        for dy in (-12.5, 12.5):
            h = Part.makeCylinder(1.5, plate_t + 4.0,
                                  FreeCAD.Vector(cx + dx, dy, plate_top - plate_t - 2.0))
            blk = blk.cut(h)

    blk.rotate((0, 0, 0), (0, 0, 1), angle_deg)
    return blk


def build(doc):
    """构建 6 根机臂全套零件，返回创建的对象列表。"""
    objs = []
    for ang in spec.ARM_ANGLES:
        suffix = "_%03d" % int(ang)

        tube = _make_tube(ang)
        assert tube.isValid(), "tube %s invalid" % suffix
        objs.append(spec.add_part(doc, tube, "Arm_Tube" + suffix, spec.C_TUBE))

        blk = _make_root_block(ang)
        assert blk.isValid(), "root block %s invalid" % suffix
        objs.append(spec.add_part(doc, blk, "Arm_RootBlock" + suffix, spec.C_RED))

        for i, bolt in enumerate(_make_root_bolts(ang), 1):
            assert bolt.isValid(), "root bolt %s invalid" % suffix
            objs.append(spec.add_part(doc, bolt, "Arm_RootBolt%d%s" % (i, suffix), spec.C_DARK))

        clamp = _make_motor_clamp(ang)
        assert clamp.isValid(), "motor clamp %s invalid" % suffix
        objs.append(spec.add_part(doc, clamp, "Arm_MotorMount" + suffix, spec.C_RED))

    return objs
