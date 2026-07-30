# -*- coding: utf-8 -*-
"""
Hexacopter 建模共享规格（单位：mm，坐标系：Z 向上，原点在机架中心）
参考机型：DJI S900 / Tarot T960 级大型六旋翼机架（调研核实数据）
所有部件脚本必须 import 本模块，保证尺寸/配色一致。

布局约定（与参考照片一致）：
- 6 根机臂在 XY 平面内呈 60° 等角放射分布：0/60/120/180/240/300 度
- 0° 方向指向 +X；机臂为银白色圆管
- 电机轴线沿 Z，电机中心位于半径 MOTOR_RADIUS 处
- 中央机架 = 上板 + 下板（黑色碳纤，带镂空减重孔），层间红色铝柱/连接块
- 上板上表面 Z = FRAME_TOP_Z；下板下表面 Z = FRAME_BOT_Z
- 起落架向下延伸到 SKID_Z；GPS 桅杆从顶板中心向上
"""

import math

# ---------------- 总体 ----------------
N_ARMS = 6
ARM_ANGLES = [0, 60, 120, 180, 240, 300]   # 各机臂方位角（度）

WHEELBASE = 900.0            # 对角电机间距（DJI S900 官方）
MOTOR_RADIUS = WHEELBASE / 2 # = 450，电机中心半径

# ---------------- 中央机架板 ----------------
FRAME_PLATE_R = 135.0        # 中央板外接圆半径（Ø270，S900 官方）
FRAME_PLATE_T = 2.0          # 板厚（碳纤）
FRAME_GAP = 35.0             # 上下板间距
FRAME_TOP_Z = 17.5           # 上板上表面
FRAME_BOT_Z = FRAME_TOP_Z - FRAME_PLATE_T - FRAME_GAP - FRAME_PLATE_T  # = -21.5
PLATE_HOLE_R = 10.0          # 减重孔默认半径（示意）
BOSS_R = 30.0                # 顶板中央凸台半径
BOSS_H = 4.0                 # 凸台高度
STANDOFF_D = 10.0            # 板间红色铝柱直径

# ---------------- 机臂 ----------------
ARM_TUBE_OD = 25.0           # 机臂圆管外径（官方 Ø25 碳管）
ARM_TUBE_ID = 22.0           # 内径（壁厚 1.5）
ARM_ROOT_R = 85.0            # 管起始半径（插入机架红色连接块）
ARM_TIP_R = 428.0            # 管末端半径（电机座夹紧处）
ARM_Z = 0.0                  # 机臂中心高度（位于两层板中间）

ARM_ROOT_BLOCK_L = 46.0      # 臂根红色连接块长度（沿臂方向）
ARM_ROOT_BLOCK_W = 34.0      # 宽（切向）
ARM_ROOT_BLOCK_H = 30.0      # 高

MOTOR_MOUNT_L = 42.0         # 电机座红色夹紧件长度
MOTOR_MOUNT_W = 34.0
MOTOR_MOUNT_H = 30.0

# ---------------- 电机（4114 级外转子，实测 Ø47×33） ----------------
MOTOR_BODY_D = 42.0          # 定子座直径
MOTOR_BODY_H = 13.0          # 定子座高度
MOTOR_BELL_D = 47.0          # 转子上盖（bell）直径
MOTOR_BELL_H = 20.0          # 转子上盖高度
MOTOR_SHAFT_D = 4.0
MOTOR_SHAFT_H = 8.0
MOTOR_BASE_Z = 15.0          # 电机底面高度（电机座上表面）
MOTOR_TOP_Z = MOTOR_BASE_Z + MOTOR_BODY_H + MOTOR_BELL_H  # = 48

# ---------------- 螺旋桨（15 寸 1552 两叶） ----------------
PROP_DIAMETER = 381.0        # 15"
PROP_HUB_D = 14.0
PROP_HUB_H = 10.0
PROP_BLADE_W_ROOT = 26.0     # 叶根弦长
PROP_BLADE_W_TIP = 14.0      # 叶尖弦长
PROP_THICK = 3.0
PROP_Z = MOTOR_TOP_Z + MOTOR_SHAFT_H + PROP_HUB_H / 2  # 桨中心高度 = 61
# CW/CCW：0/120/240 度臂为 CCW，60/180/300 度臂为 CW

# ---------------- 起落架（雪橇式，S900 官方 460×450×360） ----------------
LANDING_H = 360.0            # 机架底到地面
SKID_TUBE_D = 16.0           # 底部横管（黑色）直径
SKID_LEN = 460.0             # 横管长度（沿 X 方向）
SKID_SPACING = 360.0         # 两根横管间距（Y 方向）
STRUT_TUBE_D = 14.0          # 竖撑管径（银白）
STRUT_TOP_R = 78.0           # 竖撑顶部安装点半径
STRUT_TILT_DEG = 15.0        # 竖撑外倾角（向外张开）
STRUT_CLAMP_H = 26.0         # 红色 T 型管夹高度
SKID_Z = FRAME_BOT_Z - LANDING_H  # 地面横管中心高度 = -381.5

# ---------------- GPS 桅杆 ----------------
GPS_ROD_D = 8.0
GPS_ROD_H = 130.0            # 桅杆露出高度（经验值，调研建议 120-150）
GPS_DOME_D = 55.0            # 天线罩直径
GPS_DOME_H = 14.0            # 罩高（圆盘略鼓）

# ---------------- 云台挂架（机底） ----------------
GIMBAL_RAIL_D = 10.0         # 两根挂杆直径
GIMBAL_RAIL_LEN = 170.0
GIMBAL_RAIL_SPACING = 90.0
GIMBAL_PLATE_W = 110.0
GIMBAL_PLATE_L = 120.0
GIMBAL_PLATE_T = 2.5
GIMBAL_DROP = 80.0           # 挂板低于机架底的距离
CAMERA_W = 90.0; CAMERA_H = 62.0; CAMERA_D = 60.0  # 相机（示意）
CAMERA_LENS_D = 34.0

# ---------------- 配色（ShapeColor, RGB 0~1） ----------------
C_CARBON   = (0.055, 0.055, 0.065)   # 碳纤黑
C_RED      = (0.545, 0.07, 0.075)    # 阳极红（照片偏暗红）
C_SILVER   = (0.74, 0.75, 0.78)      # 银白铝
C_TUBE     = (0.82, 0.82, 0.83)      # 机臂/起落架白管
C_DARK     = (0.13, 0.13, 0.15)      # 深色金属件
C_MOTOR    = (0.42, 0.42, 0.45)      # 电机银灰
C_PROP     = (0.028, 0.028, 0.033)   # 桨黑
C_SKID     = (0.10, 0.10, 0.11)      # 起落架横管黑
C_GPS_DOME = (0.55, 0.55, 0.57)      # GPS 罩灰白
C_LENS     = (0.10, 0.12, 0.16)      # 镜头深蓝黑


def polar(angle_deg, r, z=0.0):
    """极坐标 -> (x, y, z)"""
    a = math.radians(angle_deg)
    return (r * math.cos(a), r * math.sin(a), z)


def set_color(obj, rgb):
    """给对象设置颜色（GUI 可用时生效）"""
    try:
        obj.ViewObject.ShapeColor = rgb
    except Exception:
        pass


def add_part(doc, shape, name, color):
    """把 Part.Shape 包成文档对象并上色，返回对象"""
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    set_color(obj, color)
    return obj
