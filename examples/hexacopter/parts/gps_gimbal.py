# -*- coding: utf-8 -*-
"""
gps_gimbal.py — GPS 桅杆 + 底部云台相机模块
命名前缀：GPS_ / GM_
坐标：全局绝对坐标，Z 向上，原点在机架中心。单位 mm。
"""
import sys
if r"D:/claude code/freecad_hexa" not in sys.path:
    sys.path.insert(0, r"D:/claude code/freecad_hexa")
import FreeCAD
import Part
import spec

V = FreeCAD.Vector


# ---------------------------------------------------------------- GPS 部分
def _build_gps(doc, parts):
    boss_top = spec.FRAME_TOP_Z + spec.BOSS_H          # 凸台顶面 = 21.5

    # 红色折叠座小块 26x26x12，两侧耳片 + 横向枢轴孔
    blk = Part.makeBox(26.0, 26.0, 12.0, V(-13, -13, boss_top))
    ear1 = Part.makeBox(16.0, 5.0, 14.0, V(-8, 13, boss_top))
    ear2 = Part.makeBox(16.0, 5.0, 14.0, V(-8, -18, boss_top))
    mount = blk.fuse([ear1, ear2])
    hole = Part.makeCylinder(2.0, 40.0, V(0, -20, boss_top + 7.0), V(0, 1, 0))
    mount = mount.cut(hole)
    parts.append(spec.add_part(doc, mount, "GPS_FoldMount", spec.C_RED))

    # 黑色桅杆 Ø8 x 130（从折叠座顶面起）
    rod_z0 = boss_top + 12.0
    rod = Part.makeCylinder(spec.GPS_ROD_D / 2, spec.GPS_ROD_H, V(0, 0, rod_z0))
    parts.append(spec.add_part(doc, rod, "GPS_Rod", spec.C_DARK))

    # 灰白天线罩：扁圆盘 + 顶部球冠（总高 GPS_DOME_H）
    dome_z0 = rod_z0 + spec.GPS_ROD_H
    r = spec.GPS_DOME_D / 2
    cap_h = 4.0
    cyl_h = spec.GPS_DOME_H - cap_h
    cyl = Part.makeCylinder(r, cyl_h, V(0, 0, dome_z0))
    # 球冠：球半径 Rs，使半径 r 处冠高 = cap_h
    Rs = (r * r + cap_h * cap_h) / (2 * cap_h)
    sph_c = dome_z0 + cyl_h + cap_h - Rs
    sph = Part.makeSphere(Rs, V(0, 0, sph_c))
    keep = Part.makeBox(2 * Rs, 2 * Rs, Rs, V(-Rs, -Rs, dome_z0 + cyl_h))
    cap = sph.common(keep)
    dome = cyl.fuse(cap)
    parts.append(spec.add_part(doc, dome, "GPS_Dome", spec.C_GPS_DOME))


# ---------------------------------------------------------------- 云台部分
def _build_gimbal(doc, parts):
    rail_r = spec.GIMBAL_RAIL_D / 2
    rail_y = spec.GIMBAL_RAIL_SPACING / 2
    rail_z = spec.FRAME_BOT_Z - 15.0                     # 导轨中心高度 = -36.5
    half_len = spec.GIMBAL_RAIL_LEN / 2

    # 两根导轨碳管（沿 X，Y=±45）
    for i, sy in enumerate((1, -1)):
        rail = Part.makeCylinder(rail_r, spec.GIMBAL_RAIL_LEN,
                                 V(-half_len, sy * rail_y, rail_z), V(1, 0, 0))
        parts.append(spec.add_part(doc, rail, "GM_Rail_%d" % (i + 1), spec.C_DARK))

    # 4 个红色小管夹：从下板底面挂到导轨
    clamp_x = 60.0
    clamp_h = spec.FRAME_BOT_Z - (rail_z - 3.0)          # 包住导轨中心略下
    n = 0
    for sx in (1, -1):
        for sy in (1, -1):
            n += 1
            cl = Part.makeBox(16.0, 16.0, clamp_h,
                              V(sx * clamp_x - 8, sy * rail_y - 8, rail_z - 3.0))
            parts.append(spec.add_part(doc, cl, "GM_Clamp_%d" % n, spec.C_RED))

    # 黑色挂板：W(沿Y) x L(沿X) x 2.5，顶面在 FRAME_BOT_Z 下方 GIMBAL_DROP 处
    plate_top = spec.FRAME_BOT_Z - spec.GIMBAL_DROP      # = -101.5
    plate = Part.makeBox(spec.GIMBAL_PLATE_L, spec.GIMBAL_PLATE_W, spec.GIMBAL_PLATE_T,
                         V(-spec.GIMBAL_PLATE_L / 2, -spec.GIMBAL_PLATE_W / 2,
                           plate_top - spec.GIMBAL_PLATE_T))
    parts.append(spec.add_part(doc, plate, "GM_Plate", spec.C_CARBON))

    # 4 根吊杆（导轨 -> 挂板），Ø6 深色
    n = 0
    for sx in (1, -1):
        for sy in (1, -1):
            n += 1
            h = rail_z - plate_top
            hd = Part.makeCylinder(3.0, h, V(sx * 50.0, sy * rail_y, plate_top))
            parts.append(spec.add_part(doc, hd, "GM_Hanger_%d" % n, spec.C_DARK))

    # 4 颗红色减震球 Ø10（挂板底面与相机顶面之间）
    plate_bot = plate_top - spec.GIMBAL_PLATE_T
    ball_z = plate_bot - 5.0
    n = 0
    for sx in (1, -1):
        for sy in (1, -1):
            n += 1
            b = Part.makeSphere(5.0, V(sx * 40.0, sy * 35.0, ball_z))
            parts.append(spec.add_part(doc, b, "GM_Damper_%d" % n, spec.C_RED))

    # 深灰相机盒：D(沿X) x W(沿Y) x H(沿Z)，前面朝 +X，顶面贴减震球
    cam_top = plate_bot - 10.0
    cam = Part.makeBox(spec.CAMERA_D, spec.CAMERA_W, spec.CAMERA_H,
                       V(-spec.CAMERA_D / 2, -spec.CAMERA_W / 2, cam_top - spec.CAMERA_H))
    parts.append(spec.add_part(doc, cam, "GM_Camera", spec.C_DARK))

    # 镜头 Ø34 短圆柱，沿 +X 伸出
    lens_len = 25.0
    lens_z = cam_top - spec.CAMERA_H / 2
    lens = Part.makeCylinder(spec.CAMERA_LENS_D / 2, lens_len,
                             V(spec.CAMERA_D / 2, 0, lens_z), V(1, 0, 0))
    parts.append(spec.add_part(doc, lens, "GM_Lens", spec.C_LENS))


def build(doc):
    """构建 GPS 桅杆 + 云台相机模块，返回创建的对象列表"""
    parts = []
    _build_gps(doc, parts)
    _build_gimbal(doc, parts)
    return parts
