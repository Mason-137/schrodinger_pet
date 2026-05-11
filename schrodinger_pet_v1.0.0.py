import sys
import os
import re
import json
import shlex
import socket
import gc
import math
import ctypes
import random
import threading
import time
import subprocess
import shutil
import queue
import tempfile
import urllib.request
import urllib.error
import traceback
from pathlib import Path
from dataclasses import dataclass, field
from datetime import date, datetime

from PySide6.QtCore import Qt, QTimer, QPointF, QRectF, QPoint, QFileInfo, QSize, QDate
from PySide6.QtGui import (
    QPainter, QPen, QColor, QPainterPath, QFont,
    QGuiApplication, QAction, QIcon, QPixmap, QCursor, QPolygonF,
)
from PySide6.QtWidgets import (
    QApplication, QWidget, QMenu, QSystemTrayIcon, QMessageBox,
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QCheckBox, QComboBox, QTabWidget, QGroupBox, QFormLayout,
    QSpinBox, QDialogButtonBox, QGridLayout, QListWidget,
    QListWidgetItem, QLineEdit, QFileDialog, QFileIconProvider,
    QStackedWidget, QFrame, QScrollArea, QInputDialog,
    QCalendarWidget, QTextEdit,
)


# ════════════════════════════════════════════════════════════════
#  颜色 (来自 CatBoxCharacter / SchrodingersCat 的设计常量)
# ════════════════════════════════════════════════════════════════
C_BOX_YELLOW   = QColor("#FFCC33")
C_BOX_BORDER   = QColor("#FFFFFF")
C_LOCK         = QColor("#C0C0C0")
C_LOCK_HOLE    = QColor("#3F3F3F")     # ~ DARK_GREY
C_RADIO_BG     = QColor("#FFD700")
C_RADIO_BLADE  = QColor("#1A1A1A")
C_QS_BG        = QColor("#1A1A2E")
C_QS_TEXT      = QColor("#FFFFFF")
C_QS_KET0      = QColor("#5BFF8F")
C_QS_KET1      = QColor("#FF6B6B")
C_HEAD_GREY    = QColor("#949AA3")
C_INNER_EAR    = QColor("#FFB6C1")
C_NOSE         = QColor("#FF9999")
C_PUPIL        = QColor("#000000")
C_EYE_WHITE    = QColor("#FFFFFF")
C_LINE_STROKE  = QColor("#FFFFFF")
C_RED_SYMBOL   = QColor("#E53935")
C_BOX_SECONDARY = QColor("#FFCC33")
C_BOX_PANEL     = QColor("#FFCC33")
CURRENT_BOX_THEME_NAME = "theme"

# 复杂粒子效果开关，由设置界面控制；关闭后更省电。
EFFECT_PARTICLES_ENABLED = True


THEME_PALETTES = {
    "classic": {
        "label": "经典黄盒",
        "box": "#FFCC33",
        "head": "#949AA3",
        "inner_ear": "#FFB6C1",
        "nose": "#FF9999",
        "qs_bg": "#1A1A2E",
        "radio": "#FFD700",
    },
    "warm_sun": {
        "label": "暖阳橙",
        "box": "#FF9F1C",
        "head": "#A0A6AE",
        "inner_ear": "#FFC7D6",
        "nose": "#FF8A80",
        "qs_bg": "#3A2412",
        "radio": "#FFE066",
    },
    "cream": {
        "label": "奶油白",
        "box": "#F7E7B6",
        "head": "#C9C2B8",
        "inner_ear": "#FFD6E0",
        "nose": "#F48FB1",
        "qs_bg": "#463F3A",
        "radio": "#FFD54F",
    },
    "mint": {
        "label": "薄荷绿",
        "box": "#8EE3C8",
        "head": "#9EAAA4",
        "inner_ear": "#D7FFF1",
        "nose": "#FF9AA2",
        "qs_bg": "#0B3D2E",
        "radio": "#E5FF7A",
    },
    "ocean": {
        "label": "海洋蓝",
        "box": "#47B8E0",
        "head": "#8FB8C8",
        "inner_ear": "#BDEBFF",
        "nose": "#FFB7C5",
        "qs_bg": "#073B4C",
        "radio": "#A7F3FF",
    },
    "sky": {
        "label": "天空蓝",
        "box": "#7CC7FF",
        "head": "#AAB9C9",
        "inner_ear": "#D7F0FF",
        "nose": "#FFB3C6",
        "qs_bg": "#123C69",
        "radio": "#D9F99D",
    },
    "sakura": {
        "label": "樱花粉",
        "box": "#FFB7D5",
        "head": "#C9A7B8",
        "inner_ear": "#FFE1EF",
        "nose": "#FF7FA3",
        "qs_bg": "#4A1932",
        "radio": "#FFE066",
    },
    "rose": {
        "label": "玫瑰红",
        "box": "#FF6B8A",
        "head": "#BBA3AA",
        "inner_ear": "#FFD1DC",
        "nose": "#FF4D6D",
        "qs_bg": "#3B0A1E",
        "radio": "#FFE066",
    },
    "lavender": {
        "label": "薰衣草",
        "box": "#B8A1FF",
        "head": "#AAA5C8",
        "inner_ear": "#E7D7FF",
        "nose": "#FFA3C8",
        "qs_bg": "#241943",
        "radio": "#D9F99D",
    },
    "forest": {
        "label": "森林绿",
        "box": "#66BB6A",
        "head": "#8FA58A",
        "inner_ear": "#D7F5D0",
        "nose": "#FFB199",
        "qs_bg": "#123524",
        "radio": "#DCE775",
    },
    "coffee": {
        "label": "咖啡棕",
        "box": "#B08968",
        "head": "#9B8C7D",
        "inner_ear": "#E8C7B8",
        "nose": "#D9897E",
        "qs_bg": "#2B2118",
        "radio": "#F6D365",
    },
    "midnight": {
        "label": "午夜紫",
        "box": "#5B4B8A",
        "head": "#7E7AA2",
        "inner_ear": "#D8B4FE",
        "nose": "#FF8FB3",
        "qs_bg": "#0F1028",
        "radio": "#B8F7D4",
    },
    "mono": {
        "label": "黑白极简",
        "box": "#E5E7EB",
        "head": "#9CA3AF",
        "inner_ear": "#FBCFE8",
        "nose": "#FCA5A5",
        "qs_bg": "#111827",
        "radio": "#FACC15",
    },
    "neon": {"label": "赛博霓虹", "box": "#00E5FF", "head": "#7C3AED", "inner_ear": "#F0ABFC", "nose": "#FB7185", "qs_bg": "#09090B", "radio": "#A3FF12"},
    "aurora": {"label": "极光青紫", "box": "#5EEAD4", "head": "#A78BFA", "inner_ear": "#CCFBF1", "nose": "#F9A8D4", "qs_bg": "#111827", "radio": "#C4B5FD"},
    "matcha": {"label": "抹茶拿铁", "box": "#CDE990", "head": "#A3B18A", "inner_ear": "#E9F5DB", "nose": "#E9AFA3", "qs_bg": "#263A29", "radio": "#F6F1D1"},
    "berry": {"label": "莓果夜色", "box": "#C084FC", "head": "#BE185D", "inner_ear": "#FBCFE8", "nose": "#FDA4AF", "qs_bg": "#2E1065", "radio": "#F0ABFC"},
    "ice": {"label": "冰川银蓝", "box": "#BAE6FD", "head": "#CBD5E1", "inner_ear": "#E0F2FE", "nose": "#F9A8D4", "qs_bg": "#0F172A", "radio": "#67E8F9"},
}


DOCTORAL_DISCIPLINES = {
    "pink": {"label": "文学（文、法、哲、教育、艺术、历史）", "color": "#FFB6C1"},
    "gray": {"label": "理学（理、经管、管理）", "color": "#A9A9A9"},
    "yellow": {"label": "工学", "color": "#FFD700"},
    "green": {"label": "农学", "color": "#228B22"},
    "white": {"label": "医学", "color": "#FFFFFF"},
    "red": {"label": "军事学", "color": "#DC143C"},
}

BOX_COLOR_PALETTES = {
    "theme": {"label": "跟随整体主题", "box": None},
    "classic_yellow": {"label": "经典黄盒", "box": "#FFCC33"},
    "orange": {"label": "橙色盒子", "box": "#FF9F1C"},
    "cream": {"label": "奶油盒子", "box": "#F7E7B6"},
    "mint": {"label": "薄荷盒子", "box": "#8EE3C8"},
    "ocean_blue": {"label": "海蓝盒子", "box": "#47B8E0"},
    "sky_blue": {"label": "天空蓝盒子", "box": "#7CC7FF"},
    "sakura_pink": {"label": "樱花粉盒子", "box": "#FFB7D5"},
    "rose": {"label": "玫瑰红盒子", "box": "#FF6B8A"},
    "lavender": {"label": "薰衣草盒子", "box": "#B8A1FF"},
    "forest_green": {"label": "森林绿盒子", "box": "#66BB6A"},
    "coffee": {"label": "咖啡棕盒子", "box": "#B08968"},
    "midnight": {"label": "午夜紫盒子", "box": "#5B4B8A"},
    "mono": {"label": "银灰盒子", "box": "#E5E7EB"},
    "doctoral_red": {
        "label": "博士红",
        "box": "#17181D",
        "box_secondary": "#B3122F",
        "box_panel": "#D6DCE5",
    },
}


CAT_HEAD_PALETTES = {
    "theme": {
        "label": "跟随整体主题",
        "head": None,
        "inner_ear": None,
        "nose": None,
    },
    "british_shorthair": {
        "label": "英短灰",
        "head": "#949AA3",
        "inner_ear": "#FFB6C1",
        "nose": "#FF9999",
    },
    "silver": {
        "label": "银渐层",
        "head": "#C6CBD3",
        "inner_ear": "#FFD5E1",
        "nose": "#FCA5A5",
    },
    "orange_tabby": {
        "label": "橘猫",
        "head": "#F4A259",
        "inner_ear": "#FFD0B3",
        "nose": "#F9844A",
    },
    "cream_cat": {
        "label": "奶油猫",
        "head": "#F1D6A7",
        "inner_ear": "#FFD6C9",
        "nose": "#F59E9E",
    },
    "white_cat": {
        "label": "白猫",
        "head": "#F3F4F6",
        "inner_ear": "#FFD7E5",
        "nose": "#FF9CB3",
    },
    "black_cat": {
        "label": "黑猫",
        "head": "#2F3437",
        "inner_ear": "#6B4B5A",
        "nose": "#D88C9A",
    },
    "tuxedo": {
        "label": "奶牛猫",
        "head": "#3B3F46",
        "inner_ear": "#F3B6C8",
        "nose": "#F5A3B7",
    },
    "ragdoll": {
        "label": "布偶浅咖",
        "head": "#D8C3A5",
        "inner_ear": "#F8C8D8",
        "nose": "#C98A80",
    },
    "sakura_cat": {
        "label": "樱花粉猫",
        "head": "#D8A7B1",
        "inner_ear": "#FFE1EF",
        "nose": "#FF7FA3",
    },
    "blue_cat": {
        "label": "海蓝猫",
        "head": "#8FB8C8",
        "inner_ear": "#BDEBFF",
        "nose": "#FFB7C5",
    },
    "green_cat": {
        "label": "森林绿猫",
        "head": "#8FA58A",
        "inner_ear": "#D7F5D0",
        "nose": "#FFB199",
    },
    "purple_cat": {
        "label": "午夜紫猫",
        "head": "#7E7AA2",
        "inner_ear": "#D8B4FE",
        "nose": "#FF8FB3",
    },
}


def apply_pet_theme(theme_name, box_theme_name="theme", cat_head_theme_name="british_shorthair", doctoral_discipline="pink"):
    """应用皮肤主题；整体主题与盒子 / 猫头颜色可以独立覆盖。博士红主题可选择学科领子颜色。"""
    global C_BOX_YELLOW, C_HEAD_GREY, C_INNER_EAR, C_NOSE, C_QS_BG, C_RADIO_BG
    global C_BOX_SECONDARY, C_BOX_PANEL, CURRENT_BOX_THEME_NAME

    palette = THEME_PALETTES.get(theme_name) or THEME_PALETTES["classic"]

    box_palette = BOX_COLOR_PALETTES.get(box_theme_name) or BOX_COLOR_PALETTES["theme"]
    head_palette = CAT_HEAD_PALETTES.get(cat_head_theme_name) or CAT_HEAD_PALETTES["british_shorthair"]

    CURRENT_BOX_THEME_NAME = str(box_theme_name or "theme")
    main_box = box_palette.get("box") or palette["box"]
    C_BOX_YELLOW = QColor(main_box)
    
    # 使用盒子主题中的 box_secondary（即衣服装饰红色）
    C_BOX_SECONDARY = QColor(box_palette.get("box_secondary") or main_box)
    
    # 首先使用盒子主题中的 box_panel（默认领子颜色）
    C_BOX_PANEL = QColor(box_palette.get("box_panel") or main_box)
    
    # 如果是博士红主题，再根据学科设置领子颜色（使用 C_BOX_PANEL）
    if box_theme_name == "doctoral_red":
        discipline_palette = DOCTORAL_DISCIPLINES.get(doctoral_discipline) or DOCTORAL_DISCIPLINES["pink"]
        C_BOX_PANEL = QColor(discipline_palette["color"])

    if head_palette.get("head"):
        C_HEAD_GREY = QColor(head_palette["head"])
        C_INNER_EAR = QColor(head_palette["inner_ear"])
        C_NOSE = QColor(head_palette["nose"])
    else:
        C_HEAD_GREY = QColor(palette["head"])
        C_INNER_EAR = QColor(palette["inner_ear"])
        C_NOSE = QColor(palette["nose"])

    C_QS_BG = QColor(palette["qs_bg"])
    C_RADIO_BG = QColor(palette["radio"])



# ════════════════════════════════════════════════════════════════
#  设计常量 (manim 原始坐标; y 向上)
# ════════════════════════════════════════════════════════════════
SCALE_PX_PER_UNIT = 22   # 越大宠物越大, 默认 22; 右键菜单可切换尺寸

# ── 箱子 ──
BOX_BODY_CENTER  = (0.0, -2.0)
BOX_BODY_W, BOX_BODY_H = 4.5, 2.4
BOX_TOP_CENTER   = (0.0, -1.0)
BOX_TOP_W, BOX_TOP_H = 4.5, 0.64
HALF_W, WING_EXT = 2.25, 1.4
LID_LEFT_PTS = [
    (-HALF_W,              1.32 - 2.0),   # = (-2.25, -0.68)
    (-(HALF_W + WING_EXT), 1.04 - 2.0),   # = (-3.65, -0.96)
    (-(HALF_W + WING_EXT), 0.40 - 2.0),   # = (-3.65, -1.60)
    (-HALF_W,              0.68 - 2.0),   # = (-2.25, -1.32)
]
DECO_Y           = -2.2
LOCK_CENTER      = (0.0, DECO_Y)
LOCK_W, LOCK_H   = 0.64, 0.48
LOCK_HOLE_R      = 0.144
QS_CENTER        = (1.1, DECO_Y)
QS_W, QS_H, QS_R = 1.36, 0.72, 0.08
RADIO_CENTER     = (-1.1, DECO_Y)
RADIO_BG_R       = 0.46
RADIO_BLADE_IN   = 0.10
RADIO_BLADE_OUT  = 0.35
RADIO_CENTER_R   = 0.07

# ── 猫 (所有"非 ear/head"部分都已经折进 SH = DOWN * 0.5) ──
EAR_OUTER_LEFT = [
    (-1.36, 0.40), (-1.48, 1.28), (-1.36, 2.08),
    (-0.56, 1.52), (-0.12, 0.72),
]
EAR_INNER_LEFT = [
    (-1.20, 0.64), (-1.32, 1.20), (-1.24, 1.76),
    (-0.68, 1.36), (-0.32, 0.88),
]
HEAD_CENTER    = (0.0, 0.0)
HEAD_W, HEAD_H = 3.84, 3.20

NOSE_PTS = [(-0.16, -0.26), (0.16, -0.26), (0.0, -0.42)]
NOSE_MOUTH_LINE = ((0.0, -0.42), (0.0, -0.55))
WHISKER_DATA = [   # (start, end, manim_signed_angle)
    ((-1.04, -0.18), (-2.36, -0.06), -0.30),
    ((-1.12, -0.42), (-2.44, -0.62), -0.40),
    ((-1.04, -0.66), (-2.36, -1.06), -0.50),
    (( 1.04, -0.18), ( 2.36, -0.06),  0.30),
    (( 1.12, -0.42), ( 2.44, -0.62),  0.40),
    (( 1.04, -0.66), ( 2.36, -1.06),  0.50),
]
RIGHT_EYE_X = [
    ((0.48, 0.06), (0.88, 0.54)),
    ((0.48, 0.54), (0.88, 0.06)),
]

EYE_CFG = {
    "default":  dict(c=(-0.72, 0.30), white_r=0.36, w_squash=1.0,
                     pupil_r=0.16,  p_squash=1.0,
                     hl_offset=(-0.016, 0.08), hl_r=0.048),
    "surprise": dict(c=(-0.72, 0.34), white_r=0.40, w_squash=1.0,
                     pupil_r=0.128, p_squash=1.0,
                     hl_offset=(-0.016, 0.08), hl_r=0.048),
    "angry":    dict(c=(-0.72, 0.30), white_r=0.36, w_squash=0.5,
                     pupil_r=0.136, p_squash=0.6,
                     hl_offset=(-0.016, 0.08), hl_r=0.048),
}
GAZE_COEFF = 0.096

MOUTH_DEFAULT    = ((-0.32, -0.55), (0.32, -0.55), math.pi / 1.2)
MOUTH_SURPRISE_C = (0.0, -0.76)
MOUTH_SURPRISE_R = 0.20
MOUTH_ANGRY_PTS  = [(-0.28, -0.76), (0.0, -0.55), (0.28, -0.76)]

CLIP_Y       = -1.32
RISE_AMOUNT  = 3.5

# Bounding box (用于 widget 尺寸)
DESIGN_X_MIN = -(HALF_W + WING_EXT)               # -3.65
DESIGN_X_MAX = +(HALF_W + WING_EXT)               # +3.65
DESIGN_Y_MIN = BOX_BODY_CENTER[1] - BOX_BODY_H/2  # -3.20
DESIGN_Y_MAX = 3.20



# ════════════════════════════════════════════════════════════════
#  量子特效辅助
# ════════════════════════════════════════════════════════════════
def clamp01(x):
    return max(0.0, min(1.0, float(x)))


def ease_smooth(x):
    """Manim-like smooth easing: 3u^2 - 2u^3."""
    u = clamp01(x)
    return u * u * (3.0 - 2.0 * u)


def ease_out_cubic(x):
    u = clamp01(x)
    return 1.0 - (1.0 - u) ** 3


def lerp(a, b, u):
    return a + (b - a) * u


# ════════════════════════════════════════════════════════════════
#  运行内存清理辅助：best-effort，不结束进程，不删除文件
# ════════════════════════════════════════════════════════════════
def _get_available_memory_mb():
    """返回系统可用内存 MB；拿不到时返回 None。"""
    try:
        if sys.platform.startswith("win"):
            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [
                    ("dwLength", ctypes.c_ulong),
                    ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
                ]

            stat = MEMORYSTATUSEX()
            stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
            if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat)):
                return stat.ullAvailPhys / (1024 * 1024)

        if os.path.exists("/proc/meminfo"):
            with open("/proc/meminfo", "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("MemAvailable:"):
                        return int(line.split()[1]) / 1024.0
    except Exception:
        return None
    return None


def _windows_empty_working_sets(max_pid_slots=8192):
    """Windows: 尝试整理可访问进程的工作集，返回成功数量。"""
    if not sys.platform.startswith("win"):
        return 0

    trimmed = 0
    try:
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        psapi = ctypes.WinDLL("psapi", use_last_error=True)

        PROCESS_QUERY_INFORMATION = 0x0400
        PROCESS_SET_QUOTA = 0x0100
        flags = PROCESS_QUERY_INFORMATION | PROCESS_SET_QUOTA

        DWORD = ctypes.c_ulong
        pids = (DWORD * max_pid_slots)()
        bytes_returned = DWORD()
        enum_ok = psapi.EnumProcesses(
            ctypes.byref(pids), ctypes.sizeof(pids), ctypes.byref(bytes_returned)
        )
        count = int(bytes_returned.value // ctypes.sizeof(DWORD)) if enum_ok else 0

        OpenProcess = kernel32.OpenProcess
        OpenProcess.argtypes = [DWORD, ctypes.c_bool, DWORD]
        OpenProcess.restype = ctypes.c_void_p
        CloseHandle = kernel32.CloseHandle
        CloseHandle.argtypes = [ctypes.c_void_p]
        EmptyWorkingSet = psapi.EmptyWorkingSet
        EmptyWorkingSet.argtypes = [ctypes.c_void_p]
        EmptyWorkingSet.restype = ctypes.c_bool

        # 先整理当前进程，保证没有权限问题。
        try:
            if EmptyWorkingSet(kernel32.GetCurrentProcess()):
                trimmed += 1
        except Exception:
            pass

        current_pid = os.getpid()
        for i in range(count):
            pid = int(pids[i])
            if pid <= 4 or pid == current_pid:
                continue
            handle = OpenProcess(flags, False, pid)
            if not handle:
                continue
            try:
                if EmptyWorkingSet(handle):
                    trimmed += 1
            finally:
                CloseHandle(handle)
    except Exception:
        pass
    return trimmed


def _linux_malloc_trim():
    """Linux/glibc: 让本进程把空闲堆内存还给系统。"""
    if not sys.platform.startswith("linux"):
        return False
    try:
        libc = ctypes.CDLL("libc.so.6")
        if hasattr(libc, "malloc_trim"):
            libc.malloc_trim(0)
            return True
    except Exception:
        pass
    return False


def clean_running_memory():
    """安全的运行内存清理：不杀进程；返回可展示的结果 dict。"""
    before = _get_available_memory_mb()
    collected = gc.collect()
    trimmed = 0
    method = "gc.collect"

    if sys.platform.startswith("win"):
        trimmed = _windows_empty_working_sets()
        method = "gc.collect + Windows EmptyWorkingSet"
    elif sys.platform.startswith("linux"):
        if _linux_malloc_trim():
            method = "gc.collect + malloc_trim"

    # 再收一遍，把动画 / 清理过程中新产生的临时对象也尽量回收。
    collected += gc.collect()
    after = _get_available_memory_mb()
    freed_mb = None
    if before is not None and after is not None:
        freed_mb = max(0.0, after - before)

    return {
        "method": method,
        "freed_mb": freed_mb,
        "trimmed_processes": trimmed,
        "collected_objects": collected,
    }


# ════════════════════════════════════════════════════════════════
#  系统状态 / 快捷工具 / 回收站辅助
# ════════════════════════════════════════════════════════════════
_CPU_PROC_SAMPLE = None


def _get_memory_info():
    """返回内存信息 dict: percent / used_mb / total_mb / available_mb。"""
    try:
        try:
            import psutil  # 可选依赖；没有也能走下面的标准库兜底。
            vm = psutil.virtual_memory()
            return {
                "percent": float(vm.percent),
                "used_mb": float(vm.used) / (1024 * 1024),
                "total_mb": float(vm.total) / (1024 * 1024),
                "available_mb": float(vm.available) / (1024 * 1024),
            }
        except Exception:
            pass

        if sys.platform.startswith("win"):
            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [
                    ("dwLength", ctypes.c_ulong),
                    ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
                ]

            stat = MEMORYSTATUSEX()
            stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
            if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat)):
                total = float(stat.ullTotalPhys)
                avail = float(stat.ullAvailPhys)
                used = max(0.0, total - avail)
                return {
                    "percent": float(stat.dwMemoryLoad),
                    "used_mb": used / (1024 * 1024),
                    "total_mb": total / (1024 * 1024),
                    "available_mb": avail / (1024 * 1024),
                }

        if os.path.exists("/proc/meminfo"):
            data = {}
            with open("/proc/meminfo", "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.split()
                    if len(parts) >= 2:
                        data[parts[0].rstrip(":")] = int(parts[1])
            total = float(data.get("MemTotal", 0))
            avail = float(data.get("MemAvailable", data.get("MemFree", 0)))
            if total > 0:
                used = max(0.0, total - avail)
                return {
                    "percent": used / total * 100.0,
                    "used_mb": used / 1024.0,
                    "total_mb": total / 1024.0,
                    "available_mb": avail / 1024.0,
                }

        if sys.platform == "darwin":
            total_bytes = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")
            out = subprocess.check_output(["vm_stat"], text=True, timeout=2.0)
            page_size = 4096
            free_pages = inactive_pages = speculative_pages = 0
            for line in out.splitlines():
                line = line.strip().replace(".", "")
                if line.startswith("page size of"):
                    nums = [int(s) for s in line.split() if s.isdigit()]
                    if nums:
                        page_size = nums[0]
                elif line.startswith("Pages free:"):
                    free_pages = int(line.split(":")[1].strip())
                elif line.startswith("Pages inactive:"):
                    inactive_pages = int(line.split(":")[1].strip())
                elif line.startswith("Pages speculative:"):
                    speculative_pages = int(line.split(":")[1].strip())
            avail = float((free_pages + inactive_pages + speculative_pages) * page_size)
            used = max(0.0, float(total_bytes) - avail)
            return {
                "percent": used / float(total_bytes) * 100.0,
                "used_mb": used / (1024 * 1024),
                "total_mb": float(total_bytes) / (1024 * 1024),
                "available_mb": avail / (1024 * 1024),
            }
    except Exception:
        return None
    return None


def _read_proc_cpu_sample():
    try:
        with open("/proc/stat", "r", encoding="utf-8") as f:
            parts = f.readline().split()[1:]
        nums = [int(x) for x in parts[:10]]
        idle = nums[3] + (nums[4] if len(nums) > 4 else 0)
        total = sum(nums)
        return total, idle
    except Exception:
        return None


def _get_cpu_percent():
    """返回 CPU 占用百分比；拿不到时返回 None。"""
    global _CPU_PROC_SAMPLE
    try:
        try:
            import psutil  # 可选依赖。
            return float(psutil.cpu_percent(interval=0.20))
        except Exception:
            pass

        if os.path.exists("/proc/stat"):
            s1 = _CPU_PROC_SAMPLE or _read_proc_cpu_sample()
            time.sleep(0.18)
            s2 = _read_proc_cpu_sample()
            _CPU_PROC_SAMPLE = s2
            if s1 and s2:
                total_delta = max(1, s2[0] - s1[0])
                idle_delta = max(0, s2[1] - s1[1])
                return max(0.0, min(100.0, (1.0 - idle_delta / total_delta) * 100.0))

        if sys.platform.startswith("win"):
            commands = [
                ["wmic", "cpu", "get", "loadpercentage", "/value"],
                [
                    "powershell", "-NoProfile", "-Command",
                    "(Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average"
                ],
            ]
            for cmd in commands:
                try:
                    out = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL, timeout=3.0)
                    nums = []
                    for token in out.replace("=", " ").split():
                        try:
                            nums.append(float(token))
                        except ValueError:
                            pass
                    if nums:
                        return max(0.0, min(100.0, sum(nums) / len(nums)))
                except Exception:
                    continue

        if sys.platform == "darwin":
            load1 = os.getloadavg()[0]
            cores = max(1, os.cpu_count() or 1)
            return max(0.0, min(100.0, load1 / cores * 100.0))
    except Exception:
        return None
    return None


def _temperature_level(temp_c):
    if temp_c is None:
        return "unknown"
    try:
        t = float(temp_c)
    except Exception:
        return "unknown"
    if t >= 90:
        return "bad"
    if t >= 80:
        return "warn"
    return "normal"


def _pick_best_temperature_reading(readings):
    """从传感器读数中挑一个最像 CPU 温度的值。readings: [(name, value, source)]"""
    cleaned = []
    for name, value, source in readings:
        try:
            v = float(value)
        except Exception:
            continue
        if not (-20.0 <= v <= 130.0):
            continue
        name = str(name or "").strip()
        source = str(source or "").strip()
        lname = name.lower()
        score = 0
        if "cpu" in lname:
            score += 40
        if "package" in lname:
            score += 35
        if "tdie" in lname or "tctl" in lname:
            score += 35
        if "core" in lname:
            score += 25
        if "ccd" in lname:
            score += 20
        if "acpi" in lname or "thermal zone" in lname:
            score -= 15
        cleaned.append((score, v, name, source))

    if not cleaned:
        return None
    cleaned.sort(key=lambda x: (x[0], x[1]), reverse=True)
    score, value, name, source = cleaned[0]
    return {
        "ok": True,
        "celsius": float(value),
        "name": name or "CPU",
        "source": source or "sensor",
        "level": _temperature_level(value),
    }


def _get_cpu_temperature_info():
    """读取 CPU 温度。优先硬件监控传感器，其次系统 ACPI 温区。

    Windows 上如果没有 LibreHardwareMonitor / OpenHardwareMonitor 这类传感器服务，
    系统可能只暴露 ACPI 温区，精确度取决于主板/笔记本固件。
    """
    readings = []

    # 1) psutil：Linux 常见可用；Windows 通常不可用，但保留兼容。
    try:
        import psutil
        temps = psutil.sensors_temperatures(fahrenheit=False)
        if temps:
            for sensor_name, entries in temps.items():
                for entry in entries:
                    label = getattr(entry, "label", "") or sensor_name
                    current = getattr(entry, "current", None)
                    readings.append((label, current, f"psutil:{sensor_name}"))
            best = _pick_best_temperature_reading(readings)
            if best:
                return best
    except Exception:
        pass

    # 2) Windows：LibreHardwareMonitor / OpenHardwareMonitor WMI。
    if sys.platform.startswith("win"):
        ps_script = """
$targets = @()
foreach ($ns in @("root\\LibreHardwareMonitor", "root\\OpenHardwareMonitor")) {
  try {
    $rows = Get-CimInstance -Namespace $ns -ClassName Sensor -ErrorAction Stop |
      Where-Object { $_.SensorType -eq "Temperature" -and $null -ne $_.Value } |
      Select-Object @{Name="Namespace";Expression={$ns}}, Name, Value
    if ($rows) { $targets += $rows }
  } catch {}
}
$targets | ConvertTo-Json -Compress
"""
        try:
            out = subprocess.check_output(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
                text=True, stderr=subprocess.DEVNULL, timeout=5.0
            ).strip()
            if out:
                data = json.loads(out)
                if isinstance(data, dict):
                    data = [data]
                if isinstance(data, list):
                    readings = []
                    for item in data:
                        if not isinstance(item, dict):
                            continue
                        readings.append((
                            item.get("Name", ""),
                            item.get("Value", None),
                            item.get("Namespace", "HardwareMonitor"),
                        ))
                    best = _pick_best_temperature_reading(readings)
                    if best:
                        return best
        except Exception:
            pass

        # 3) Windows ACPI fallback。很多机器显示的是主板/温区温度，不一定是精准 CPU Package。
        ps_acpi = """
try {
  Get-CimInstance -Namespace root/wmi -ClassName MSAcpi_ThermalZoneTemperature -ErrorAction Stop |
    Select-Object InstanceName, CurrentTemperature |
    ConvertTo-Json -Compress
} catch {}
"""
        try:
            out = subprocess.check_output(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_acpi],
                text=True, stderr=subprocess.DEVNULL, timeout=4.0
            ).strip()
            if out:
                data = json.loads(out)
                if isinstance(data, dict):
                    data = [data]
                readings = []
                for item in data if isinstance(data, list) else []:
                    raw = item.get("CurrentTemperature")
                    try:
                        c = float(raw) / 10.0 - 273.15
                    except Exception:
                        continue
                    name = item.get("InstanceName", "ACPI Thermal Zone")
                    readings.append((name, c, "ACPI"))
                best = _pick_best_temperature_reading(readings)
                if best:
                    best["source"] = "ACPI"
                    return best
        except Exception:
            pass

    # 4) macOS 兜底：有 osx-cpu-temp 时可读。
    if sys.platform == "darwin":
        try:
            if shutil.which("osx-cpu-temp"):
                out = subprocess.check_output(["osx-cpu-temp"], text=True, stderr=subprocess.DEVNULL, timeout=3.0)
                nums = []
                for token in out.replace("°C", " ").replace("C", " ").split():
                    try:
                        nums.append(float(token))
                    except ValueError:
                        pass
                if nums:
                    value = nums[0]
                    return {
                        "ok": True,
                        "celsius": value,
                        "name": "CPU",
                        "source": "osx-cpu-temp",
                        "level": _temperature_level(value),
                    }
        except Exception:
            pass

    return {
        "ok": False,
        "celsius": None,
        "name": "",
        "source": "",
        "level": "unknown",
        "error": "未读取到 CPU 温度传感器",
    }


def get_cpu_temperature_status():
    return _get_cpu_temperature_info()


def format_cpu_temperature_text(res):
    if not res or not res.get("ok") or res.get("celsius") is None:
        return "暂时无法读取 CPU 温度"
    temp = float(res["celsius"])
    source = str(res.get("source", "")).strip()
    suffix = ""
    level = res.get("level", "normal")
    if level == "bad":
        suffix = "，温度很高"
    elif level == "warn":
        suffix = "，温度偏高"
    source_text = f" · {source}" if source else ""
    return f"CPU 温度 {temp:.0f}°C{source_text}{suffix}"


def get_system_status():
    """读取 CPU / 内存状态，供后台线程调用。"""
    cpu = _get_cpu_percent()
    mem = _get_memory_info()

    cpu_level = "unknown"
    mem_level = "unknown"
    if cpu is not None:
        cpu_level = "bad" if cpu >= 90 else "warn" if cpu >= 75 else "normal"
    if mem and mem.get("percent") is not None:
        mp = float(mem["percent"])
        mem_level = "bad" if mp >= 90 else "warn" if mp >= 80 else "normal"

    level_order = {"unknown": 0, "normal": 1, "warn": 2, "bad": 3}
    overall = max([cpu_level, mem_level], key=lambda x: level_order.get(x, 0))

    return {
        "ok": cpu is not None or mem is not None,
        "cpu_percent": cpu,
        "memory": mem,
        "cpu_level": cpu_level,
        "memory_level": mem_level,
        "overall_level": overall,
    }


def format_system_status_text(res):
    if not res or not res.get("ok"):
        return "暂时无法读取电脑状态"

    parts = []
    cpu = res.get("cpu_percent")
    mem = res.get("memory")
    if cpu is not None:
        parts.append(f"CPU {cpu:.0f}%")
    else:
        parts.append("CPU --")

    if mem and mem.get("percent") is not None:
        parts.append(f"内存 {float(mem['percent']):.0f}%")
    else:
        parts.append("内存 --")

    level = res.get("overall_level")
    suffix = ""
    if level == "bad":
        suffix = "，负载很高"
    elif level == "warn":
        suffix = "，有点忙"
    return "  ".join(parts) + suffix


def _get_network_io_totals():
    """返回 (sent_bytes, recv_bytes)。优先 psutil，Windows 兜底使用 GetIfTable。"""
    try:
        try:
            import psutil
            counters = psutil.net_io_counters()
            if counters:
                return int(counters.bytes_sent), int(counters.bytes_recv)
        except Exception:
            pass

        if sys.platform.startswith("linux") and os.path.exists("/proc/net/dev"):
            sent = 0
            recv = 0
            with open("/proc/net/dev", "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    if ":" not in line:
                        continue
                    iface, rest = line.split(":", 1)
                    iface = iface.strip()
                    if iface == "lo":
                        continue
                    parts = rest.split()
                    if len(parts) >= 16:
                        recv += int(parts[0])
                        sent += int(parts[8])
            return sent, recv

        if sys.platform.startswith("win"):
            # GetIfTable 的字节数是 32 位，足够用于短时间速率差值；溢出时会在调用处处理。
            MAX_INTERFACE_NAME_LEN = 256
            MAXLEN_PHYSADDR = 8

            class MIB_IFROW(ctypes.Structure):
                _fields_ = [
                    ("wszName", ctypes.c_wchar * MAX_INTERFACE_NAME_LEN),
                    ("dwIndex", ctypes.c_ulong),
                    ("dwType", ctypes.c_ulong),
                    ("dwMtu", ctypes.c_ulong),
                    ("dwSpeed", ctypes.c_ulong),
                    ("dwPhysAddrLen", ctypes.c_ulong),
                    ("bPhysAddr", ctypes.c_ubyte * MAXLEN_PHYSADDR),
                    ("dwAdminStatus", ctypes.c_ulong),
                    ("dwOperStatus", ctypes.c_ulong),
                    ("dwLastChange", ctypes.c_ulong),
                    ("dwInOctets", ctypes.c_ulong),
                    ("dwInUcastPkts", ctypes.c_ulong),
                    ("dwInNUcastPkts", ctypes.c_ulong),
                    ("dwInDiscards", ctypes.c_ulong),
                    ("dwInErrors", ctypes.c_ulong),
                    ("dwInUnknownProtos", ctypes.c_ulong),
                    ("dwOutOctets", ctypes.c_ulong),
                    ("dwOutUcastPkts", ctypes.c_ulong),
                    ("dwOutNUcastPkts", ctypes.c_ulong),
                    ("dwOutDiscards", ctypes.c_ulong),
                    ("dwOutErrors", ctypes.c_ulong),
                    ("dwOutQLen", ctypes.c_ulong),
                    ("dwDescrLen", ctypes.c_ulong),
                    ("bDescr", ctypes.c_ubyte * 256),
                ]

            iphlpapi = ctypes.windll.iphlpapi
            size = ctypes.c_ulong(0)
            iphlpapi.GetIfTable(None, ctypes.byref(size), False)
            if size.value <= 0:
                return None
            buf = ctypes.create_string_buffer(size.value)
            ret = iphlpapi.GetIfTable(buf, ctypes.byref(size), False)
            if ret != 0:
                return None

            num = ctypes.c_ulong.from_buffer_copy(buf.raw[:4]).value
            offset = 4
            row_size = ctypes.sizeof(MIB_IFROW)
            sent = 0
            recv = 0
            for i in range(int(num)):
                row = MIB_IFROW.from_buffer_copy(buf.raw[offset + i * row_size: offset + (i + 1) * row_size])
                # dwOperStatus == 5 通常表示 connected；其他状态也可能有统计，保守累加非零项。
                recv += int(row.dwInOctets)
                sent += int(row.dwOutOctets)
            return sent, recv
    except Exception:
        return None
    return None


def _format_bytes_rate(bps):
    try:
        bps = max(0.0, float(bps))
    except Exception:
        return "--"
    if bps >= 1024 ** 3:
        return f"{bps / (1024 ** 3):.2f}GB/s"
    if bps >= 1024 ** 2:
        return f"{bps / (1024 ** 2):.1f}MB/s"
    if bps >= 1024:
        return f"{bps / 1024:.0f}KB/s"
    return f"{bps:.0f}B/s"


def _popen_detached(cmd):
    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def open_task_manager_tool():
    if sys.platform.startswith("win"):
        _popen_detached(["taskmgr"])
        return True, "已打开任务管理器"
    if sys.platform == "darwin":
        _popen_detached(["open", "-a", "Activity Monitor"])
        return True, "已打开活动监视器"

    candidates = [
        ["gnome-system-monitor"],
        ["mate-system-monitor"],
        ["xfce4-taskmanager"],
        ["ksysguard"],
        ["xterm", "-e", "top"],
    ]
    for cmd in candidates:
        if shutil.which(cmd[0]):
            _popen_detached(cmd)
            return True, "已打开系统监视器"
    return False, "未找到可用的系统监视器"


def open_settings_tool():
    if sys.platform.startswith("win"):
        try:
            os.startfile("ms-settings:")
            return True, "已打开设置"
        except Exception:
            return False, "打开设置失败"

    if sys.platform == "darwin":
        _popen_detached(["open", "-b", "com.apple.systempreferences"])
        return True, "已打开系统设置"

    candidates = [
        ["gnome-control-center"],
        ["systemsettings"],
        ["xfce4-settings-manager"],
        ["mate-control-center"],
    ]
    for cmd in candidates:
        if shutil.which(cmd[0]):
            _popen_detached(cmd)
            return True, "已打开系统设置"
    return False, "未找到系统设置入口"


def open_control_panel_tool():
    if sys.platform.startswith("win"):
        try:
            _popen_detached(["control"])
            return True, "已打开控制面板"
        except Exception:
            return False, "打开控制面板失败"

    return False, "当前系统没有 Windows 控制面板"


def _send_windows_hotkey(vks):
    """发送 Windows 全局快捷键。"""
    try:
        user32 = ctypes.windll.user32
        KEYEVENTF_KEYUP = 0x0002
        for vk in vks:
            user32.keybd_event(int(vk), 0, 0, 0)
        time.sleep(0.08)
        for vk in reversed(vks):
            user32.keybd_event(int(vk), 0, KEYEVENTF_KEYUP, 0)
        return True
    except Exception:
        return False


def open_system_screenshot_tool():
    """调用系统截图工具。Windows 优先调用 Win+Shift+S / Snipping Tool。"""
    if sys.platform.startswith("win"):
        # Win + Shift + S：系统截图浮层，通常比直接打开 Snipping Tool 更快。
        if _send_windows_hotkey([0x5B, 0x10, ord("S")]):
            return True, "已调用系统截图"
        try:
            os.startfile("ms-screenclip:")
            return True, "已调用系统截图"
        except Exception:
            try:
                _popen_detached(["SnippingTool.exe"])
                return True, "已打开截图工具"
            except Exception:
                return False, "调用系统截图失败"

    if sys.platform == "darwin":
        try:
            _popen_detached(["open", "-a", "Screenshot"])
            return True, "已打开系统截图"
        except Exception:
            return False, "调用系统截图失败"

    candidates = [
        ["gnome-screenshot", "-a"],
        ["flameshot", "gui"],
        ["spectacle", "-r"],
        ["xfce4-screenshooter"],
    ]
    for cmd in candidates:
        if shutil.which(cmd[0]):
            _popen_detached(cmd)
            return True, "已调用系统截图"
    return False, "未找到可用截图工具"


def open_system_screen_recording_tool():
    """调用系统录屏工具。Windows 11 优先使用截图工具录屏 Win+Shift+R。"""
    if sys.platform.startswith("win"):
        # Win + Shift + R：Windows 11 截图工具的屏幕录制区域选择。
        # 相比 系统录屏，对桌面区域/普通窗口更友好。
        if _send_windows_hotkey([0x5B, 0x10, ord("R")]):
            return True, "已调用截图工具录屏"
        try:
            os.startfile("ms-screenclip:")
            return True, "已打开截图工具"
        except Exception:
            return False, "调用截图工具录屏失败，请确认 Windows 11 截图工具已更新"

    if sys.platform == "darwin":
        try:
            _popen_detached(["open", "-a", "Screenshot"])
            return True, "已打开系统截图/录屏工具"
        except Exception:
            return False, "调用系统录屏失败"

    candidates = [
        ["kooha"],
        ["simplescreenrecorder"],
        ["obs"],
        ["kazam"],
    ]
    for cmd in candidates:
        if shutil.which(cmd[0]):
            _popen_detached(cmd)
            return True, "已打开录屏工具"
    return False, "未找到可用录屏工具"



def lock_screen_tool():
    """调用系统锁屏。"""
    try:
        if sys.platform.startswith("win"):
            res = ctypes.windll.user32.LockWorkStation()
            return bool(res), "已锁定电脑" if res else "锁定电脑失败"

        if sys.platform == "darwin":
            candidates = [
                ["/System/Library/CoreServices/Menu Extras/User.menu/Contents/Resources/CGSession", "-suspend"],
                ["pmset", "displaysleepnow"],
            ]
            for cmd in candidates:
                if os.path.exists(cmd[0]) or shutil.which(cmd[0]):
                    _popen_detached(cmd)
                    return True, "已调用锁屏"

        candidates = [
            ["loginctl", "lock-session"],
            ["xdg-screensaver", "lock"],
            ["gnome-screensaver-command", "-l"],
            ["qdbus", "org.freedesktop.ScreenSaver", "/ScreenSaver", "Lock"],
        ]
        for cmd in candidates:
            if shutil.which(cmd[0]):
                _popen_detached(cmd)
                return True, "已调用锁屏"
        return False, "未找到系统锁屏入口"
    except Exception:
        return False, "锁定电脑失败"


def _safe_temp_roots():
    roots = []
    candidates = [
        tempfile.gettempdir(),
        os.environ.get("TEMP", ""),
        os.environ.get("TMP", ""),
    ]
    if sys.platform.startswith("win"):
        local = os.environ.get("LOCALAPPDATA", "")
        if local:
            candidates.append(str(Path(local) / "Temp"))

    seen = set()
    for raw in candidates:
        try:
            p = Path(str(raw).strip()).expanduser()
            if not str(p):
                continue
            p = p.resolve()
            key = str(p).lower()
            if key in seen or not p.exists() or not p.is_dir():
                continue
            # 安全保护：只清理明确叫 Temp/tmp 的目录，避免配置异常时清错。
            if p.name.lower() not in ("temp", "tmp"):
                continue
            seen.add(key)
            roots.append(p)
        except Exception:
            continue
    return roots


def clean_temp_files():
    """清理系统临时文件。只清理临时目录的直接子项，跳过占用/无权限文件。"""
    roots = _safe_temp_roots()
    if not roots:
        return False, "未找到可清理的临时文件夹"

    removed = 0
    failed = 0
    freed_bytes = 0

    for root in roots:
        try:
            children = list(root.iterdir())
        except Exception:
            failed += 1
            continue

        for item in children:
            try:
                if not item.exists() and not item.is_symlink():
                    continue

                size = 0
                try:
                    if item.is_file() or item.is_symlink():
                        size = item.stat().st_size
                    elif item.is_dir():
                        for sub in item.rglob("*"):
                            try:
                                if sub.is_file() or sub.is_symlink():
                                    size += sub.stat().st_size
                            except Exception:
                                pass
                except Exception:
                    size = 0

                if item.is_dir() and not item.is_symlink():
                    shutil.rmtree(item, ignore_errors=False)
                else:
                    item.unlink()

                removed += 1
                freed_bytes += size
            except Exception:
                failed += 1

    if removed == 0:
        msg = "没有可清理的临时文件"
        if failed:
            msg += f"，跳过 {failed} 项"
        return True, msg

    if freed_bytes >= 1024 ** 3:
        freed = f"{freed_bytes / (1024 ** 3):.2f} GB"
    elif freed_bytes >= 1024 ** 2:
        freed = f"{freed_bytes / (1024 ** 2):.1f} MB"
    elif freed_bytes >= 1024:
        freed = f"{freed_bytes / 1024:.0f} KB"
    else:
        freed = f"{freed_bytes} B"

    msg = f"已清理临时文件 {removed} 项，约释放 {freed}"
    if failed:
        msg += f"，跳过 {failed} 项"
    return True, msg


def flush_dns_cache_tool():
    """刷新 DNS 缓存。"""
    try:
        if sys.platform.startswith("win"):
            try:
                subprocess.check_output(
                    ["ipconfig", "/flushdns"],
                    stderr=subprocess.STDOUT,
                    text=True,
                    timeout=8,
                )
                return True, "DNS 缓存已刷新"
            except Exception:
                # 兜底：打开命令窗口执行，便于用户看到系统错误。
                _popen_detached(["cmd", "/c", "ipconfig /flushdns"])
                return True, "已调用刷新 DNS 缓存"

        if sys.platform == "darwin":
            cmds = [
                ["dscacheutil", "-flushcache"],
                ["killall", "-HUP", "mDNSResponder"],
            ]
            any_ok = False
            for cmd in cmds:
                if shutil.which(cmd[0]):
                    try:
                        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=8)
                        any_ok = True
                    except Exception:
                        pass
            return (True, "DNS 缓存已刷新") if any_ok else (False, "未找到 DNS 刷新命令")

        candidates = [
            ["resolvectl", "flush-caches"],
            ["systemd-resolve", "--flush-caches"],
            ["nscd", "-i", "hosts"],
        ]
        for cmd in candidates:
            if shutil.which(cmd[0]):
                try:
                    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=8)
                    return True, "DNS 缓存已刷新"
                except Exception:
                    continue
        return False, "未找到 DNS 刷新命令"
    except Exception:
        return False, "刷新 DNS 缓存失败"


def open_custom_exe_tool(display_name, exe_path, args=None):
    """打开用户自定义 exe。路径不存在时给出明确提示。"""
    args = args or []
    if not exe_path:
        return False, f"{display_name} 路径为空"
    if not os.path.exists(exe_path):
        return False, f"未找到 {display_name}"

    try:
        _popen_detached([exe_path] + list(args))
        return True, f"已打开 {display_name}"
    except Exception:
        try:
            # 某些 Windows 程序用 os.startfile 更兼容。
            if sys.platform.startswith("win") and not args:
                os.startfile(exe_path)
                return True, f"已打开 {display_name}"
        except Exception:
            pass
        return False, f"打开 {display_name} 失败"





def open_downloads_folder_tool():
    path = get_downloads_folder_path()
    if not path.exists():
        return False, f"下载文件夹不存在：{path}"

    try:
        if sys.platform.startswith("win"):
            os.startfile(str(path))
        elif sys.platform == "darwin":
            _popen_detached(["open", str(path)])
        else:
            if shutil.which("xdg-open"):
                _popen_detached(["xdg-open", str(path)])
            else:
                return False, "未找到文件管理器入口"
        return True, f"已打开下载文件夹：{path}"
    except Exception:
        return False, "打开下载文件夹失败"


def empty_recycle_bin():
    """清空回收站 / 废纸篓 / Trash，返回 (ok, message)。"""
    try:
        if sys.platform.startswith("win"):
            shell32 = ctypes.windll.shell32
            # SHERB_NOCONFIRMATION | SHERB_NOPROGRESSUI | SHERB_NOSOUND
            flags = 0x00000001 | 0x00000002 | 0x00000004
            res = shell32.SHEmptyRecycleBinW(None, None, flags)
            if res == 0:
                return True, "回收站已清空"
            return False, f"清空回收站失败：{res}"

        if sys.platform == "darwin":
            script = 'tell application "Finder" to empty trash'
            subprocess.check_call(["osascript", "-e", script], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=30.0)
            return True, "废纸篓已清空"

        # Linux / FreeDesktop Trash 规范。
        trash_base = Path.home() / ".local" / "share" / "Trash"
        removed = 0
        for sub in ("files", "info"):
            folder = trash_base / sub
            if not folder.exists():
                continue
            for item in folder.iterdir():
                try:
                    if item.is_dir() and not item.is_symlink():
                        shutil.rmtree(item)
                    else:
                        item.unlink()
                    removed += 1
                except Exception:
                    pass
        return True, "回收站已清空" if removed else "回收站已经是空的"
    except Exception as exc:
        return False, "清空回收站失败：" + (str(exc) or exc.__class__.__name__)


RANDOM_TIPS = [
    "记得保存文件，猫猫不想看你重写一遍。",
    "喝口水吧，量子猫也需要补充流体。",
    "盯屏幕久了，看看 20 米外放松一下眼睛。",
    "今天也要开心一点。",
    "任务很多时，先完成最小的一件。",
    "桌面太乱的话，可以先建一个临时整理文件夹。",
    "如果电脑开始变慢，先看看 CPU 和内存占用。",
    "休息 5 分钟，回来可能更快。",
    "别忘了备份重要文件。",
    "保持呼吸，保持保存，保持可爱。",
]

FORTUNE_TIPS = [
    "今日运势：宜整理桌面，文件会自己变乖。",
    "今日运势：宜早点休息，晚睡的小猫会掉毛。",
    "今日运势：宜清理下载文件夹，可能会找到遗失的宝藏。",
    "今日运势：宜喝水，CPU 和人都需要降温。",
    "今日运势：宜备份配置，改东西会更安心。",
    "今日运势：宜专注，番茄钟会站在你这边。",
    "今日运势：宜摸摸猫，灵感 +3。",
    "今日运势：不宜开太多标签页，小猫数不过来。",
]

TIME_REMARKS = [
    (6, "早上好，今天也要轻轻启动。"),
    (12, "上午状态不错，记得喝水。"),
    (14, "中午啦，先吃饭再战斗。"),
    (18, "下午继续加油，小猫在岗。"),
    (22, "晚上好，适合收尾和整理。"),
    (24, "夜深了，小猫建议保存文件并早点睡。"),
]




# ════════════════════════════════════════════════════════════════
#  日历 / 生日提醒辅助
# ════════════════════════════════════════════════════════════════
LUNAR_MONTH_NAMES = [
    "", "正月", "二月", "三月", "四月", "五月", "六月",
    "七月", "八月", "九月", "十月", "冬月", "腊月"
]

LUNAR_DAY_NAMES = [
    "",
    "初一", "初二", "初三", "初四", "初五", "初六", "初七", "初八", "初九", "初十",
    "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九", "二十",
    "廿一", "廿二", "廿三", "廿四", "廿五", "廿六", "廿七", "廿八", "廿九", "三十",
]

BIRTHDAY_MODE_LABELS = {
    "off": "关闭生日提醒",
    "solar": "只按阳历提醒",
    "lunar": "只按农历提醒",
    "both": "阳历和农历都提醒",
}

GREETING_FREQUENCY_OPTIONS = [
    (0, "当天只提醒一次"),
    (60, "每 1 小时一次"),
    (120, "每 2 小时一次"),
    (360, "每 6 小时一次"),
    (720, "每 12 小时一次"),
]

# 订日历相关
CALENDAR_EVENT_REMINDER_OPTIONS = [
    (0, "当天只提醒一次"),
    (60, "每 1 小时一次"),
    (120, "每 2 小时一次"),
    (360, "每 6 小时一次"),
    (720, "每 12 小时一次"),
]


def parse_solar_date_text(text):
    """解析 yyyy-mm-dd / yyyy/mm/dd / yyyy.mm.dd。"""
    text = str(text or "").strip().replace("/", "-").replace(".", "-")
    if not text:
        return None
    try:
        return datetime.strptime(text, "%Y-%m-%d").date()
    except Exception:
        return None


def solar_to_lunar_info(solar_date):
    """阳历日期转农历信息。需要 pip install lunardate。"""
    if not solar_date:
        return None
    try:
        from lunardate import LunarDate
        ld = LunarDate.fromSolarDate(solar_date.year, solar_date.month, solar_date.day)
        return {
            "year": int(ld.year),
            "month": int(ld.month),
            "day": int(ld.day),
            "is_leap_month": bool(getattr(ld, "isLeapMonth", False)),
        }
    except Exception:
        return None


def format_lunar_info(info):
    if not info:
        return "农历不可用，请安装 lunardate"
    month = int(info.get("month", 0))
    day = int(info.get("day", 0))
    leap = "闰" if info.get("is_leap_month") else ""
    month_text = LUNAR_MONTH_NAMES[month] if 0 < month < len(LUNAR_MONTH_NAMES) else f"{month}月"
    day_text = LUNAR_DAY_NAMES[day] if 0 < day < len(LUNAR_DAY_NAMES) else f"{day}日"
    return f"{leap}{month_text}{day_text}"


def is_same_lunar_day(a, b):
    if not a or not b:
        return False
    return (
        int(a.get("month", -1)) == int(b.get("month", -2))
        and int(a.get("day", -1)) == int(b.get("day", -2))
        and bool(a.get("is_leap_month", False)) == bool(b.get("is_leap_month", False))
    )


def is_lunar_new_year_date(solar_date):
    """判断某个阳历日期是否为农历正月初一。"""
    lunar = solar_to_lunar_info(solar_date)
    if not lunar:
        return False
    return int(lunar.get("month", 0)) == 1 and int(lunar.get("day", 0)) == 1 and not bool(lunar.get("is_leap_month", False))


def holiday_greeting_match_for_date(solar_date, enable_new_year=True, enable_lunar_new_year=True):
    """返回节日祝福类型；不匹配返回空字符串。"""
    if enable_new_year and solar_date.month == 1 and solar_date.day == 1:
        return "元旦"
    if enable_lunar_new_year and is_lunar_new_year_date(solar_date):
        return "农历新年"
    return ""




# ════════════════════════════════════════════════════════════════
#  网速测量辅助：后台下载少量测试数据，只测下载速度
# ════════════════════════════════════════════════════════════════
def measure_download_speed(target_bytes=4_000_000, timeout_s=10.0):
    """测量下载网速。

    说明：
    - 使用标准库 urllib，避免额外依赖。
    - 只读取 target_bytes 左右的数据，减少流量消耗。
    - 返回 dict，UI 线程只读取结果，不在工作线程里碰 Qt 对象。
    """
    # Cloudflare 的 __down 可以按 bytes 参数返回指定大小的数据；
    # 后面两个作为兜底，防止某些网络屏蔽单一测速源。
    endpoints = [
        f"https://speed.cloudflare.com/__down?bytes={target_bytes}&cache={random.randint(1, 1_000_000_000)}",
        f"https://proof.ovh.net/files/10Mb.dat?cache={random.randint(1, 1_000_000_000)}",
        f"https://speed.hetzner.de/10MB.bin?cache={random.randint(1, 1_000_000_000)}",
    ]

    last_error = None
    headers = {
        "User-Agent": "SchrodingerPetSpeedTest/1.0",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    }

    for url in endpoints:
        total = 0
        start = time.perf_counter()
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout_s) as resp:
                while total < target_bytes:
                    chunk = resp.read(min(128 * 1024, target_bytes - total))
                    if not chunk:
                        break
                    total += len(chunk)
                    if time.perf_counter() - start > timeout_s:
                        break

            elapsed = max(0.001, time.perf_counter() - start)
            if total >= 128 * 1024:
                mbps = total * 8.0 / elapsed / 1_000_000.0
                mBps = total / elapsed / (1024.0 * 1024.0)
                return {
                    "ok": True,
                    "mbps": mbps,
                    "mBps": mBps,
                    "bytes": total,
                    "elapsed": elapsed,
                    "source": url.split("/")[2],
                }
            last_error = "下载数据太少"
        except Exception as exc:
            last_error = str(exc) or exc.__class__.__name__

    return {
        "ok": False,
        "error": last_error or "测速失败",
    }



# ════════════════════════════════════════════════════════════════
#  设置 / 可编辑快捷入口配置
# ════════════════════════════════════════════════════════════════
def _default_pet_data_dir():
    """默认数据目录。这个目录里还会保存 location.json，用来记住自定义保存位置。"""
    if sys.platform.startswith("win"):
        base = Path(os.environ.get("APPDATA", str(Path.home())))
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config")))
    return base / "SchrodingerPet"


def _pet_location_path():
    """保存“当前数据目录在哪里”的定位文件，始终放在默认目录中。"""
    return _default_pet_data_dir() / "location.json"


def _clean_user_dir_path(value):
    if not value:
        return None
    text = str(value).strip().strip('"')
    if not text:
        return None
    return Path(os.path.expandvars(os.path.expanduser(text)))


def _read_pet_data_dir_override():
    loc = _pet_location_path()
    try:
        if not loc.exists():
            return None
        data = json.loads(loc.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return None
        p = _clean_user_dir_path(data.get("data_dir"))
        if not p:
            return None
        return p
    except Exception:
        return None


def _pet_data_dir():
    """当前实际数据目录。配置、存档等文件都会保存在这里。"""
    override = _read_pet_data_dir_override()
    if override:
        return override
    return _default_pet_data_dir()


def _pet_config_path():
    """用户配置文件路径。"""
    return _pet_data_dir() / "config.json"


def _pet_archive_dir():
    """本地设置存档目录。"""
    return _pet_data_dir() / "archives"


def _settings_archive_name():
    return "schrodinger_pet_settings_" + time.strftime("%Y%m%d_%H%M%S") + ".json"


def _pet_log_dir():
    return _pet_data_dir() / "logs"


def _pet_log_path():
    return _pet_log_dir() / "schrodinger_pet.log"


def log_message(message):
    try:
        _pet_log_dir().mkdir(parents=True, exist_ok=True)
        line = time.strftime("[%Y-%m-%d %H:%M:%S] ") + str(message).rstrip() + "\n"
        with _pet_log_path().open("a", encoding="utf-8") as f:
            f.write(line)
    except Exception:
        pass


def log_exception(prefix="Unhandled exception"):
    try:
        log_message(prefix + "\n" + traceback.format_exc())
    except Exception:
        pass


def install_crash_protection():
    def _hook(exc_type, exc, tb):
        try:
            _pet_log_dir().mkdir(parents=True, exist_ok=True)
            with _pet_log_path().open("a", encoding="utf-8") as f:
                f.write(time.strftime("[%Y-%m-%d %H:%M:%S] Unhandled exception\n"))
                traceback.print_exception(exc_type, exc, tb, file=f)
                f.write("\n")
        except Exception:
            pass
        try:
            sys.__excepthook__(exc_type, exc, tb)
        except Exception:
            pass
    sys.excepthook = _hook


def _write_pet_data_dir_override(data_dir):
    """写入或清除自定义数据目录定位文件。"""
    default_dir = _default_pet_data_dir()
    loc = _pet_location_path()
    target = _clean_user_dir_path(data_dir) or default_dir

    try:
        default_dir.mkdir(parents=True, exist_ok=True)
        try:
            same_as_default = target.resolve() == default_dir.resolve()
        except Exception:
            same_as_default = str(target) == str(default_dir)

        if same_as_default:
            if loc.exists():
                loc.unlink()
            return True, "已恢复默认保存位置"

        loc.write_text(
            json.dumps({"data_dir": str(target)}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return True, "保存位置已更新"
    except Exception as exc:
        return False, str(exc) or exc.__class__.__name__


def migrate_pet_data_dir(new_dir):
    """把当前数据目录中的配置、存档等文件复制到新目录，并切换后续保存位置。"""
    target = _clean_user_dir_path(new_dir)
    if not target:
        return False, "保存位置不能为空", None

    current = _pet_data_dir()
    default_dir = _default_pet_data_dir()

    try:
        current_resolved = current.resolve()
    except Exception:
        current_resolved = current.absolute()
    try:
        target_resolved = target.resolve()
    except Exception:
        target_resolved = target.absolute()

    if str(current_resolved).lower() == str(target_resolved).lower():
        return True, "当前已经是这个保存位置", target

    # 避免把目录迁到自己内部导致递归复制。
    try:
        if current_resolved in target_resolved.parents:
            return False, "新保存位置不能放在当前保存目录内部", None
    except Exception:
        pass

    try:
        target.mkdir(parents=True, exist_ok=True)

        if current.exists():
            for item in current.iterdir():
                # location.json 只作为默认目录中的“指针”，不迁移为普通数据。
                if item.name == "location.json":
                    continue

                dst = target / item.name
                if item.is_dir():
                    shutil.copytree(item, dst, dirs_exist_ok=True)
                else:
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, dst)

        ok, msg = _write_pet_data_dir_override(target)
        if not ok:
            return False, "文件已复制，但保存位置切换失败：" + msg, None

        return True, f"保存位置已迁移到：{target}", target
    except Exception as exc:
        return False, str(exc) or exc.__class__.__name__, None


def _make_default_quick_tools():
    return [
        {"name": "打开任务管理器", "type": "builtin", "target": "task_manager"},
        {"name": "打开设置", "type": "builtin", "target": "settings"},
        {"name": "打开控制面板", "type": "builtin", "target": "control_panel"},
        {"name": "打开下载文件夹", "type": "builtin", "target": "downloads"},
    ]


def _make_default_custom_apps():
    return []


def _clone_launch_items(items):
    return [dict(item) for item in items]


def _make_default_network_targets():
    return [
        {"name": "AliDNS", "host": "223.5.5.5", "port": 53},
        {"name": "Cloudflare", "host": "1.1.1.1", "port": 53},
        {"name": "Google DNS", "host": "8.8.8.8", "port": 53},
        {"name": "Baidu", "host": "www.baidu.com", "port": 443},
        {"name": "GitHub", "host": "github.com", "port": 443},
    ]


def _clone_network_targets(targets):
    return [dict(item) for item in targets]


def _normalize_network_targets(targets):
    defaults = _make_default_network_targets()
    if not isinstance(targets, list):
        return _clone_network_targets(defaults)

    cleaned = []
    for item in targets:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "")).strip()
        host = str(item.get("host", "")).strip()
        try:
            port = int(item.get("port", 53))
        except Exception:
            port = 53
        if not name:
            name = host
        if host and 1 <= port <= 65535:
            cleaned.append({"name": name, "host": host, "port": port})
    return cleaned if cleaned else _clone_network_targets(defaults)


def launch_item_icon(item):
    """读取 exe / 文件夹图标；失败时返回空图标。"""
    try:
        if not isinstance(item, dict) or item.get("type") not in ("path", "exe"):
            return QIcon()
        path = str(item.get("path", "")).strip().strip('"')
        if not path or not os.path.exists(path):
            return QIcon()
        return QFileIconProvider().icon(QFileInfo(path))
    except Exception:
        return QIcon()


def _make_default_download_rules():
    return [
        {"extensions": ".py .pyw .ipynb .js .jsx .ts .tsx .html .htm .css .json .xml .yaml .yml .toml .ini .cfg .conf .sql .java .c .cpp .h .hpp .cs .go .rs .php .rb .swift .kt .lua .r .sh .bat .cmd .ps1", "folders": "Code|Codes|Source|Scripts|代码|脚本"},
        {"extensions": ".jpg .jpeg .png .gif .bmp .webp .svg .ico .heic .tif .tiff .psd .ai", "folders": "Images|Pictures|Photos|图片|图像|照片"},
        {"extensions": ".pdf .doc .docx .xls .xlsx .ppt .pptx .txt .md .rtf .csv .epub", "folders": "Documents|Docs|PDF|Office|文档|文件"},
        {"extensions": ".mp4 .mkv .avi .mov .wmv .flv .webm .m4v", "folders": "Videos|Movies|视频"},
        {"extensions": ".mp3 .wav .flac .aac .m4a .ogg .wma", "folders": "Music|Audio|音乐"},
        {"extensions": ".zip .rar .7z .tar .gz .bz2 .xz .iso", "folders": "Compressed|Archives|Archive|Zip|RAR|压缩包|压缩文件"},
        {"extensions": ".exe .msi .apk .dmg .pkg .deb .rpm", "folders": "Programs|Installers|Installer|Apps|Software|安装包|安装程序"},
        {"extensions": "*", "folders": "Other|Others|Misc|杂项|其他"},
    ]


def _clone_download_rules(rules):
    return [dict(rule) for rule in rules]


def _normalize_download_rules(rules):
    defaults = _make_default_download_rules()
    if not isinstance(rules, list):
        return _clone_download_rules(defaults)

    cleaned = []
    for rule in rules:
        if not isinstance(rule, dict):
            continue
        exts = str(rule.get("extensions", "")).strip()
        folders = str(rule.get("folders", rule.get("folder", ""))).strip()
        if not exts or not folders:
            continue
        cleaned.append({"extensions": exts, "folders": folders})
    return cleaned if cleaned else _clone_download_rules(defaults)


def _normalize_launch_items(items, defaults):
    """清理配置中的启动项，避免旧配置或手改 JSON 导致程序崩溃。"""
    if not isinstance(items, list):
        return _clone_launch_items(defaults)

    cleaned = []
    for item in items:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "")).strip()
        item_type = str(item.get("type", "")).strip()
        if not name:
            continue

        category = str(item.get("category", "默认")).strip() or "默认"
        show_in_menu = bool(item.get("show_in_menu", True))
        show_in_palette = bool(item.get("show_in_palette", True))
        run_as_admin = bool(item.get("run_as_admin", False))

        if item_type == "builtin":
            target = str(item.get("target", "")).strip()
            if target:
                cleaned.append({
                    "name": name, "type": "builtin", "target": target,
                    "category": category,
                    "show_in_menu": show_in_menu,
                    "show_in_palette": show_in_palette,
                    "run_as_admin": False,
                })
        elif item_type in ("path", "exe"):
            path = str(item.get("path", "")).strip()
            args = str(item.get("args", "")).strip()
            if path:
                cleaned.append({
                    "name": name, "type": "path", "path": path, "args": args,
                    "category": category,
                    "show_in_menu": show_in_menu,
                    "show_in_palette": show_in_palette,
                    "run_as_admin": run_as_admin,
                })

    return cleaned if cleaned else _clone_launch_items(defaults)


def load_pet_config():
    path = _pet_config_path()
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def save_pet_config(data):
    path = _pet_config_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return True
    except Exception:
        return False


def get_downloads_folder_path(preferred=None):
    
    def clean_path(value):
        if not value:
            return None
        value = str(value).strip().strip('"')
        if not value:
            return None
        return Path(os.path.expandvars(os.path.expanduser(value)))

    p = clean_path(preferred)
    if p:
        return p

    cfg = load_pet_config()
    p = clean_path(cfg.get("downloads_path"))
    if p:
        return p

    candidates = []
    if sys.platform.startswith("win"):
        userprofile = os.environ.get("USERPROFILE")
        if userprofile:
            candidates.append(Path(userprofile) / "Downloads")

    candidates.append(Path.home() / "Downloads")
    candidates.append(Path.home())

    for candidate in candidates:
        if candidate.exists():
            return candidate
    return Path.home() / "Downloads"


def run_launch_item(item):
    """执行一个可配置启动项，返回 (ok, message)。"""
    if not isinstance(item, dict):
        return False, "启动项无效"

    name = str(item.get("name", "启动项")).strip() or "启动项"
    item_type = str(item.get("type", "")).strip()

    if item_type == "builtin":
        target = str(item.get("target", "")).strip()
        builtins = {
            "task_manager": open_task_manager_tool,
            "settings": open_settings_tool,
            "control_panel": open_control_panel_tool,
            "downloads": open_downloads_folder_tool,
            "screenshot": open_system_screenshot_tool,
            "screen_record": open_system_screen_recording_tool,
            "lock_screen": lock_screen_tool,
            "clean_temp": clean_temp_files,
            "flush_dns": flush_dns_cache_tool,
        }
        func = builtins.get(target)
        if not func:
            return False, f"{name} 不可用"
        return func()

    if item_type in ("path", "exe"):
        target_path = str(item.get("path", "")).strip()
        args_text = str(item.get("args", "")).strip()
        args = []
        if args_text:
            try:
                args = shlex.split(args_text, posix=not sys.platform.startswith("win"))
            except Exception:
                args = args_text.split()

        if not target_path:
            return False, f"{name} 路径为空"
        if not os.path.exists(target_path):
            return False, f"未找到 {name}"

        try:
            if sys.platform.startswith("win") and item.get("run_as_admin") and not os.path.isdir(target_path):
                params = args_text if args_text else ""
                rc = ctypes.windll.shell32.ShellExecuteW(None, "runas", target_path, params, None, 1)
                if int(rc) <= 32:
                    return False, f"管理员运行 {name} 失败"
            elif sys.platform.startswith("win") and not args:
                os.startfile(target_path)
            elif os.path.isdir(target_path):
                if sys.platform.startswith("win"):
                    os.startfile(target_path)
                elif sys.platform == "darwin":
                    _popen_detached(["open", target_path])
                else:
                    _popen_detached(["xdg-open", target_path])
            else:
                _popen_detached([target_path] + args)
            return True, f"已打开 {name}"
        except Exception:
            return False, f"打开 {name} 失败"

    return False, f"{name} 类型无效"


def get_startup_command():
    script_path = Path(sys.argv[0]).resolve()
    if script_path.suffix.lower() == ".exe":
        return f'"{script_path}"'
    return f'"{sys.executable}" "{script_path}"'


def is_startup_enabled():
    """检查是否已设置开机自启动。Windows 使用当前用户 Run 项。"""
    if not sys.platform.startswith("win"):
        return False
    try:
        import winreg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ) as key:
            value, _typ = winreg.QueryValueEx(key, "SchrodingerPet")
        return bool(value)
    except Exception:
        return False


def set_startup_enabled(enabled):
    """开启 / 关闭开机自启动。返回 (ok, message)。"""
    if not sys.platform.startswith("win"):
        return False, "当前系统暂只支持 Windows 开机自启动"

    try:
        import winreg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
            if enabled:
                winreg.SetValueEx(key, "SchrodingerPet", 0, winreg.REG_SZ, get_startup_command())
            else:
                try:
                    winreg.DeleteValue(key, "SchrodingerPet")
                except FileNotFoundError:
                    pass
        return True, "开机自启动已开启" if enabled else "开机自启动已关闭"
    except Exception as exc:
        return False, "设置开机自启动失败：" + (str(exc) or exc.__class__.__name__)


def _unique_destination_path(dst):
    if not dst.exists():
        return dst
    stem = dst.stem
    suffix = dst.suffix
    parent = dst.parent
    for i in range(1, 1000):
        candidate = parent / f"{stem}_{i}{suffix}"
        if not candidate.exists():
            return candidate
    return parent / f"{stem}_{int(time.time())}{suffix}"


def preview_downloads_organization(downloads_path=None, rules=None, max_items=40):
    """预览下载整理结果，不移动文件。返回 (ok, message, moves)。"""
    downloads = get_downloads_folder_path(downloads_path)
    if not downloads.exists():
        return False, f"下载文件夹不存在：{downloads}", []
    if not downloads.is_dir():
        return False, f"下载路径不是文件夹：{downloads}", []
    rules = _normalize_download_rules(rules)
    existing_dirs = [p for p in downloads.iterdir() if p.is_dir()]
    lower_map = {p.name.lower(): p for p in existing_dirs}

    parsed_rules = []
    for rule in rules:
        ext_tokens = []
        for raw in str(rule.get("extensions", "")).replace("，", " ").replace(",", " ").split():
            token = raw.strip().lower()
            if not token:
                continue
            if token != "*" and not token.startswith("."):
                token = "." + token
            ext_tokens.append(token)
        folder_tokens = []
        for raw in str(rule.get("folders", "")).replace("；", "|").replace(";", "|").split("|"):
            name = raw.strip()
            if name:
                folder_tokens.append(name)
        if ext_tokens and folder_tokens:
            parsed_rules.append((ext_tokens, folder_tokens))

    moves = []
    skipped_no_folder = 0
    for item in downloads.iterdir():
        if not item.is_file():
            continue
        ext = item.suffix.lower()
        target_dir = None
        matched = False
        for ext_tokens, folder_tokens in parsed_rules:
            if "*" not in ext_tokens and ext not in ext_tokens:
                continue
            matched = True
            for folder_name in folder_tokens:
                candidate = lower_map.get(folder_name.lower())
                if candidate:
                    target_dir = candidate
                    break
            break
        if target_dir is not None:
            moves.append((item, target_dir / item.name))
        elif matched:
            skipped_no_folder += 1

    if not moves:
        msg = f"没有可整理的文件：{downloads}"
        if skipped_no_folder:
            msg += f"\n有 {skipped_no_folder} 个文件匹配规则但缺少已有目标文件夹。"
        return True, msg, []

    counts = {}
    for _src, dst in moves:
        counts[dst.parent.name] = counts.get(dst.parent.name, 0) + 1
    lines = [f"将整理 {len(moves)} 个文件："]
    for folder, count in sorted(counts.items()):
        lines.append(f"  {count} 个 → {folder}")
    lines.append("")
    lines.append("预览明细：")
    for i, (src, dst) in enumerate(moves[:max_items], 1):
        lines.append(f"{i}. {src.name}  →  {dst.parent.name}")
    if len(moves) > max_items:
        lines.append(f"... 还有 {len(moves) - max_items} 个文件未列出")
    if skipped_no_folder:
        lines.append("")
        lines.append(f"另有 {skipped_no_folder} 个文件因缺少已有目标文件夹而跳过。")
    return True, "\n".join(lines), moves


def organize_downloads_folder_with_undo(downloads_path=None, rules=None):
    """整理下载文件夹并返回移动记录，供撤销使用。返回 (ok, msg, moves)。moves: [(new_path, old_path)]"""
    downloads = get_downloads_folder_path(downloads_path)
    if not downloads.exists():
        return False, f"下载文件夹不存在：{downloads}", []
    if not downloads.is_dir():
        return False, f"下载路径不是文件夹：{downloads}", []

    rules = _normalize_download_rules(rules)
    existing_dirs = [p for p in downloads.iterdir() if p.is_dir()]
    lower_map = {p.name.lower(): p for p in existing_dirs}

    parsed_rules = []
    for rule in rules:
        ext_tokens = []
        for raw in str(rule.get("extensions", "")).replace("，", " ").replace(",", " ").split():
            token = raw.strip().lower()
            if not token:
                continue
            if token != "*" and not token.startswith("."):
                token = "." + token
            ext_tokens.append(token)

        folder_tokens = []
        for raw in str(rule.get("folders", "")).replace("；", "|").replace(";", "|").split("|"):
            name = raw.strip()
            if name:
                folder_tokens.append(name)

        if ext_tokens and folder_tokens:
            parsed_rules.append((ext_tokens, folder_tokens))

    if not parsed_rules:
        return False, "没有可用的整理规则", []

    moved = 0
    skipped_no_folder = 0
    failed = 0
    matched = 0
    moves = []

    for item in downloads.iterdir():
        if not item.is_file():
            continue

        ext = item.suffix.lower()
        target_dir = None

        for ext_tokens, folder_tokens in parsed_rules:
            if "*" not in ext_tokens and ext not in ext_tokens:
                continue

            matched += 1
            for folder_name in folder_tokens:
                candidate = lower_map.get(folder_name.lower())
                if candidate:
                    target_dir = candidate
                    break
            break

        if target_dir is None:
            if matched:
                skipped_no_folder += 1
            continue

        try:
            old_path = item
            dst = _unique_destination_path(target_dir / item.name)
            shutil.move(str(item), str(dst))
            moves.append((str(dst), str(old_path)))
            moved += 1
        except Exception:
            failed += 1

    if moved == 0 and failed == 0:
        if skipped_no_folder:
            return True, f"没有可移动文件，部分匹配规则缺少已有目标文件夹；当前路径：{downloads}", moves
        return True, f"下载文件夹已经很整齐：{downloads}", moves

    msg = f"已整理 {moved} 个文件"
    if failed:
        msg += f"，失败 {failed} 个"
    if skipped_no_folder:
        msg += f"，跳过 {skipped_no_folder} 个"
    msg += f"；路径：{downloads}"
    return True, msg, moves


def organize_downloads_folder(downloads_path=None, rules=None):
    """把下载文件夹里的文件按用户规则移动到已有分类文件夹中，不创建新文件夹。"""
    downloads = get_downloads_folder_path(downloads_path)
    if not downloads.exists():
        return False, f"下载文件夹不存在：{downloads}"
    if not downloads.is_dir():
        return False, f"下载路径不是文件夹：{downloads}"

    rules = _normalize_download_rules(rules)

    existing_dirs = [p for p in downloads.iterdir() if p.is_dir()]
    lower_map = {p.name.lower(): p for p in existing_dirs}

    parsed_rules = []
    for rule in rules:
        ext_tokens = []
        for raw in str(rule.get("extensions", "")).replace("，", " ").replace(",", " ").split():
            token = raw.strip().lower()
            if not token:
                continue
            if token != "*" and not token.startswith("."):
                token = "." + token
            ext_tokens.append(token)

        folder_tokens = []
        for raw in str(rule.get("folders", "")).replace("；", "|").replace(";", "|").split("|"):
            name = raw.strip()
            if name:
                folder_tokens.append(name)

        if ext_tokens and folder_tokens:
            parsed_rules.append((ext_tokens, folder_tokens))

    if not parsed_rules:
        return False, "没有可用的整理规则"

    moved = 0
    skipped_no_folder = 0
    failed = 0
    matched = 0

    for item in downloads.iterdir():
        if not item.is_file():
            continue

        ext = item.suffix.lower()
        target_dir = None

        for ext_tokens, folder_tokens in parsed_rules:
            if "*" not in ext_tokens and ext not in ext_tokens:
                continue

            matched += 1
            for folder_name in folder_tokens:
                candidate = lower_map.get(folder_name.lower())
                if candidate:
                    target_dir = candidate
                    break
            break

        if target_dir is None:
            if matched:
                skipped_no_folder += 1
            continue

        try:
            dst = _unique_destination_path(target_dir / item.name)
            shutil.move(str(item), str(dst))
            moved += 1
        except Exception:
            failed += 1

    if moved == 0 and failed == 0:
        if skipped_no_folder:
            return True, f"没有可移动文件，部分匹配规则缺少已有目标文件夹；当前路径：{downloads}"
        return True, f"下载文件夹已经很整齐：{downloads}"

    msg = f"已整理 {moved} 个文件"
    if failed:
        msg += f"，失败 {failed} 个"
    if skipped_no_folder:
        msg += f"，跳过 {skipped_no_folder} 个"
    msg += f"；路径：{downloads}"
    return True, msg


def check_network_status(timeout_s=2.0, targets=None):
    """轻量网络连通性检查，返回 dict。targets 可由设置界面自定义。"""
    targets = _normalize_network_targets(targets)

    last_error = ""
    for target in targets:
        host = str(target.get("host", "")).strip()
        name = str(target.get("name", host)).strip() or host
        try:
            port = int(target.get("port", 53))
        except Exception:
            port = 53
        if not host:
            continue

        start = time.perf_counter()
        try:
            with socket.create_connection((host, port), timeout=timeout_s):
                latency_ms = (time.perf_counter() - start) * 1000.0
                level = "ok"
                if latency_ms >= 800:
                    level = "bad"
                elif latency_ms >= 300:
                    level = "warn"
                return {
                    "ok": True,
                    "online": True,
                    "latency_ms": latency_ms,
                    "target": name,
                    "host": host,
                    "port": port,
                    "level": level,
                }
        except Exception as exc:
            last_error = str(exc) or exc.__class__.__name__

    return {
        "ok": False,
        "online": False,
        "latency_ms": None,
        "target": "",
        "level": "bad",
        "error": last_error or "网络不可用",
    }


def format_network_status_text(res):
    if not res or not res.get("online"):
        return "网络连接异常"
    latency = res.get("latency_ms")
    target = res.get("target", "")
    if latency is None:
        return "网络已连接"
    return f"网络正常  延迟 {latency:.0f} ms" + (f" · {target}" if target else "")



@dataclass
class ParticleDot:
    x: float
    y: float
    r: float
    opacity: float
    color: str = "#6BD9FF"

# ════════════════════════════════════════════════════════════════
#  状态
# ════════════════════════════════════════════════════════════════
@dataclass
class CatState:
    rise_progress: float = 1.0
    expression:    str   = "default"
    look_x:        float = 0.0
    look_y:        float = 0.0
    blink:         float = 0.0
    bob:           float = 0.0
    show_excl:     float = 0.0
    show_anger:    float = 0.0

    cat_offset_x:  float = 0.0
    cat_offset_y:  float = 0.0
    cat_tilt_deg:  float = 0.0

    cat_alpha:     float = 1.0
    quantum_phase: str   = "none"
    quantum_u:     float = 0.0
    ghost_sep:     float = 0.0
    ghost_opacity: float = 0.0
    flash_radius:  float = 0.0
    flash_opacity: float = 0.0
    spike_opacity: float = 0.0
    particles:     list  = field(default_factory=list)

    cat_scale:     float = 1.0
    cleanup_phase: str   = "none"
    cleanup_u:     float = 0.0
    cleanup_ring_radius:  float = 0.0
    cleanup_ring_opacity: float = 0.0
    cleanup_text:         str   = ""
    cleanup_text_opacity: float = 0.0

    message_text:    str   = ""
    message_opacity: float = 0.0
    message_kind:    str   = "info"

    dock_edge:     str   = ""
    dock_progress: float = 0.0


# ════════════════════════════════════════════════════════════════
#  Catmull-Rom -> 三次贝塞尔, 平滑通过给定点 (闭合)
# ════════════════════════════════════════════════════════════════
def catmull_rom_to_path(qpts, closed=True):
    path = QPainterPath()
    if len(qpts) < 2:
        return path
    if closed:
        ext = [qpts[-1]] + list(qpts) + [qpts[0], qpts[1]]
    else:
        ext = [qpts[0]]  + list(qpts) + [qpts[-1]]
    path.moveTo(ext[1])
    for i in range(1, len(ext) - 2):
        p0, p1, p2, p3 = ext[i-1], ext[i], ext[i+1], ext[i+2]
        b1 = QPointF(p1.x() + (p2.x() - p0.x()) / 6.0,
                     p1.y() + (p2.y() - p0.y()) / 6.0)
        b2 = QPointF(p2.x() - (p3.x() - p1.x()) / 6.0,
                     p2.y() - (p3.y() - p1.y()) / 6.0)
        path.cubicTo(b1, b2, p2)
    if closed:
        path.closeSubpath()
    return path


# ════════════════════════════════════════════════════════════════
#  渲染器
# ════════════════════════════════════════════════════════════════
class CatRenderer:
    def __init__(self, scale=SCALE_PX_PER_UNIT):
        self.scale = scale
        self.margin = 12
        w_design = (DESIGN_X_MAX - DESIGN_X_MIN)
        h_design = (DESIGN_Y_MAX - DESIGN_Y_MIN)
        self.w = int(w_design * scale) + 2 * self.margin
        self.h = int(h_design * scale) + 2 * self.margin
        self.cx = self.margin + (-DESIGN_X_MIN) * scale
        self.cy = self.margin + DESIGN_Y_MAX * scale

    def D(self, x, y):
        """design (y-up) -> widget QPointF (y-down)"""
        return QPointF(self.cx + x * self.scale, self.cy - y * self.scale)

    def Dlen(self, v):
        return v * self.scale

    def design_rect(self, cx, cy, w, h):
        x_left = cx - w / 2
        y_top  = cy + h / 2
        tl = self.D(x_left, y_top)
        return QRectF(tl.x(), tl.y(), self.Dlen(w), self.Dlen(h))

    # ── 顶层 ──────────────────────────────────────────────
    def paint(self, p: QPainter, st: CatState):
        p.setRenderHint(QPainter.Antialiasing, True)
        p.setRenderHint(QPainter.SmoothPixmapTransform, True)

        dock_progress = clamp01(getattr(st, "dock_progress", 0.0))
        if getattr(st, "dock_edge", "") and dock_progress >= 0.82:
            self._draw_edge_dock_badge(p, st)
            return

        self._draw_box(p)

        # 量子粒子先画一层，像从猫身上溢出的辉光。
        self._draw_quantum_particles(p, st)

        # 主猫本体可以在爆散阶段渐隐、在坍缩阶段渐显。
        if st.cat_alpha > 0.01:
            p.save()
            p.setOpacity(clamp01(st.cat_alpha))
            self._draw_cat(p, st)
            self._draw_symbols(p, st)
            p.restore()

        # 生 / 死幽灵小猫、坍缩尖峰、闪光画在最上层。
        self._draw_ghosts(p, st)
        self._draw_quantum_spike(p, st)
        self._draw_flash(p, st)
        self._draw_cleanup_status(p, st)
        self._draw_message_bubble(p, st)
        self._draw_edge_dock_badge(p, st)


    # ── v9 贴边收纳绘制 ─────────────────────────────────────
    def _draw_edge_dock_badge(self, p, st: CatState):
        """收纳后只显示一个完整的弹出键，不再依赖字体显示箭头。"""
        edge = getattr(st, "dock_edge", "")
        progress = clamp01(getattr(st, "dock_progress", 0.0))
        if not edge or progress <= 0.02:
            return

        p.save()
        p.setOpacity(0.45 + 0.55 * progress)

        # 与 CatPet._edge_dock_visible_px 配合：按钮厚度始终小于露出的边缘宽度。
        tab_t = min(42, max(34, int(self.Dlen(0.95))))
        tab_len = max(62, int(self.Dlen(2.18)))
        tab_len = min(tab_len, max(42, self.h - 8))
        radius = max(12, int(tab_t * 0.42))
        inset = 3

        if edge == "left":
            rect = QRectF(self.w - tab_t - inset, self.h / 2 - tab_len / 2, tab_t, tab_len)
        elif edge == "right":
            rect = QRectF(inset, self.h / 2 - tab_len / 2, tab_t, tab_len)
        elif edge == "top":
            tab_len = min(tab_len, max(42, self.w - 8))
            rect = QRectF(self.w / 2 - tab_len / 2, self.h - tab_t - inset, tab_len, tab_t)
        elif edge == "bottom":
            tab_len = min(tab_len, max(42, self.w - 8))
            rect = QRectF(self.w / 2 - tab_len / 2, inset, tab_len, tab_t)
        else:
            p.restore()
            return

        bg = QColor("#1A1A2E")
        bg.setAlphaF(0.88)
        border = QColor("#6BD9FF")
        border.setAlphaF(0.95)
        p.setPen(QPen(border, max(2, int(self.Dlen(0.045)))))
        p.setBrush(bg)
        p.drawRoundedRect(rect, radius, radius)

        # 小爪印：用几何图形画，避免字体缺字或被裁剪。
        paw = QColor("#A8FFD0")
        paw.setAlphaF(0.95)
        p.setBrush(paw)
        c = rect.center()
        if edge in ("left", "right"):
            paw_cx, paw_cy = c.x(), c.y() - tab_len * 0.16
            arrow_cx, arrow_cy = c.x(), c.y() + tab_len * 0.20
        else:
            paw_cx, paw_cy = c.x() - tab_len * 0.16, c.y()
            arrow_cx, arrow_cy = c.x() + tab_len * 0.20, c.y()

        p.drawEllipse(QPointF(paw_cx, paw_cy + tab_t * 0.07), tab_t * 0.13, tab_t * 0.11)
        for dx, dy in [(-0.13, -0.10), (0.0, -0.16), (0.13, -0.10)]:
            p.drawEllipse(QPointF(paw_cx + tab_t * dx, paw_cy + tab_t * dy), tab_t * 0.055, tab_t * 0.055)

        # 弹出方向箭头：左/右/上/下边缘分别指向屏幕内部。
        arrow = QColor("#FFFFFF")
        arrow.setAlphaF(0.96)
        p.setPen(QPen(arrow, max(2, int(tab_t * 0.08)), Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.setBrush(Qt.NoBrush)
        s = tab_t * 0.22
        path = QPainterPath()
        if edge == "right":      # 在右边缘，向左弹出
            path.moveTo(QPointF(arrow_cx + s * 0.55, arrow_cy - s))
            path.lineTo(QPointF(arrow_cx - s * 0.55, arrow_cy))
            path.lineTo(QPointF(arrow_cx + s * 0.55, arrow_cy + s))
        elif edge == "left":     # 在左边缘，向右弹出
            path.moveTo(QPointF(arrow_cx - s * 0.55, arrow_cy - s))
            path.lineTo(QPointF(arrow_cx + s * 0.55, arrow_cy))
            path.lineTo(QPointF(arrow_cx - s * 0.55, arrow_cy + s))
        elif edge == "top":      # 在上边缘，向下弹出
            path.moveTo(QPointF(arrow_cx - s, arrow_cy - s * 0.55))
            path.lineTo(QPointF(arrow_cx, arrow_cy + s * 0.55))
            path.lineTo(QPointF(arrow_cx + s, arrow_cy - s * 0.55))
        elif edge == "bottom":   # 在下边缘，向上弹出
            path.moveTo(QPointF(arrow_cx - s, arrow_cy + s * 0.55))
            path.lineTo(QPointF(arrow_cx, arrow_cy - s * 0.55))
            path.lineTo(QPointF(arrow_cx + s, arrow_cy + s * 0.55))
        p.drawPath(path)
        p.restore()


    # ── v3 量子特效绘制 ─────────────────────────────────────
    def _draw_quantum_particles(self, p, st: CatState):
        if not EFFECT_PARTICLES_ENABLED or not st.particles:
            return
        p.save()
        p.setPen(Qt.NoPen)
        for dot in st.particles:
            if dot.opacity <= 0.01 or dot.r <= 0:
                continue
            col = QColor(dot.color)
            col.setAlphaF(clamp01(dot.opacity))
            # 先画淡淡外圈，再画亮核心。
            glow = QColor(col)
            glow.setAlphaF(clamp01(dot.opacity * 0.18))
            p.setBrush(glow)
            p.drawEllipse(self.D(dot.x, dot.y), self.Dlen(dot.r * 2.2), self.Dlen(dot.r * 2.2))
            p.setBrush(col)
            p.drawEllipse(self.D(dot.x, dot.y), self.Dlen(dot.r), self.Dlen(dot.r))
        p.restore()

    def _draw_ghosts(self, p, st: CatState):
        if st.ghost_opacity <= 0.01:
            return
        base_y = 0.05 + st.bob
        sep = st.ghost_sep
        self._draw_ghost_cat_head(p, -sep, base_y, "#5BFF8F", "alive", st.ghost_opacity)
        self._draw_ghost_cat_head(p,  sep, base_y, "#FF6B6B", "dead",  st.ghost_opacity)

    def _draw_ghost_cat_head(self, p, cx, cy, color_hex, expression, opacity):
        """桌宠版 build_ghost_cat_head：绿色活猫 / 红色死猫。"""
        p.save()
        p.setOpacity(clamp01(opacity))
        ghost = QColor(color_hex)

        # 耳朵 + 头部，不画内耳，避免半透明重叠过脏。
        ear_l = [(cx + x, cy + y) for (x, y) in EAR_OUTER_LEFT]
        ear_r = [(cx - x, cy + y) for (x, y) in EAR_OUTER_LEFT]
        self._draw_smooth_polygon(p, ear_l, ghost, ghost, 0)
        self._draw_smooth_polygon(p, ear_r, ghost, ghost, 0)

        p.setPen(Qt.NoPen)
        p.setBrush(ghost)
        p.drawEllipse(self.design_rect(cx + HEAD_CENTER[0], cy + HEAD_CENTER[1], HEAD_W, HEAD_H))

        if expression == "alive":
            # 双正常眼 + 微笑
            for ex in (-0.72, 0.72):
                p.setPen(Qt.NoPen)
                p.setBrush(C_EYE_WHITE)
                p.drawEllipse(self.D(cx + ex, cy + 0.30), self.Dlen(0.30), self.Dlen(0.30))
                p.setBrush(C_PUPIL)
                p.drawEllipse(self.D(cx + ex, cy + 0.30), self.Dlen(0.12), self.Dlen(0.12))
            self._draw_arc_between(
                p,
                (cx - 0.32, cy - 0.55),
                (cx + 0.32, cy - 0.55),
                math.pi / 1.2,
                C_LINE_STROKE,
                2,
            )
        else:
            # 双 X 眼 + 锯齿嘴
            for ex in (-0.72, 0.72):
                self._draw_line(p, (cx + ex - 0.20, cy + 0.06), (cx + ex + 0.20, cy + 0.54), C_LINE_STROKE, 2)
                self._draw_line(p, (cx + ex - 0.20, cy + 0.54), (cx + ex + 0.20, cy + 0.06), C_LINE_STROKE, 2)
            pts = [
                (cx - 0.48, cy - 0.62), (cx - 0.32, cy - 0.78),
                (cx - 0.16, cy - 0.62), (cx + 0.00, cy - 0.78),
                (cx + 0.16, cy - 0.62), (cx + 0.32, cy - 0.78),
                (cx + 0.48, cy - 0.62),
            ]
            path = QPainterPath()
            path.moveTo(self.D(*pts[0]))
            for pt in pts[1:]:
                path.lineTo(self.D(*pt))
            p.setPen(QPen(C_LINE_STROKE, 2, Qt.SolidLine, Qt.RoundCap))
            p.setBrush(Qt.NoBrush)
            p.drawPath(path)

        p.restore()

    def _draw_quantum_spike(self, p, st: CatState):
        if st.spike_opacity <= 0.01:
            return
        u = clamp01(st.quantum_u)
        # Dirac δ 逼近：宽度收窄、高度升高、震荡变密。
        sigma = 1.35 * math.exp(-3.8 * u) + 0.055
        height = 0.20 + 1.35 * (u ** 2.3)
        freq = 5.0 + 34.0 * (u ** 1.7)
        osc_mix = max(0.0, 1.0 - u ** 2.8)
        center_y = -0.10 + st.bob * 0.25

        path = QPainterPath()
        N = 120
        for i in range(N):
            x = -2.35 + 4.70 * i / (N - 1)
            env = height * math.exp(-(x * x) / (2 * sigma * sigma))
            y = center_y + env * (0.35 + 0.65 * math.cos(freq * x) * osc_mix)
            pt = self.D(x, y)
            (path.moveTo if i == 0 else path.lineTo)(pt)

        col = QColor("#DDF7FF" if u > 0.58 else "#6BD9FF")
        col.setAlphaF(clamp01(st.spike_opacity))
        p.save()
        p.setPen(QPen(col, max(2, int(self.Dlen(0.08))), Qt.SolidLine, Qt.RoundCap))
        p.setBrush(Qt.NoBrush)
        p.drawPath(path)
        p.restore()

    def _draw_flash(self, p, st: CatState):
        if st.flash_opacity <= 0.01 or st.flash_radius <= 0.01:
            return
        p.save()
        col = QColor("#FFFFFF")
        col.setAlphaF(clamp01(st.flash_opacity))
        p.setPen(Qt.NoPen)
        p.setBrush(col)
        p.drawEllipse(self.D(0.0, -0.10 + st.bob * 0.25),
                      self.Dlen(st.flash_radius), self.Dlen(st.flash_radius))
        p.restore()


    def _draw_message_bubble(self, p, st: CatState):
        """通用提示气泡：自动换行、压缩高度并避免被窗口上沿裁剪。"""
        if (not st.message_text
                or st.message_opacity <= 0.01
                or (st.cleanup_text and st.cleanup_text_opacity > 0.08)):
            return

        p.save()
        text = str(st.message_text).strip()
        opacity = clamp01(st.message_opacity)

        font_size_pt = max(7, int(self.Dlen(0.25)))
        font = QFont("Microsoft YaHei", font_size_pt, QFont.Bold)
        p.setFont(font)
        fm = p.fontMetrics()

        safe_margin = max(6.0, self.margin * 0.65)
        pad_x = max(7.0, self.Dlen(0.24))
        pad_y = max(5.0, self.Dlen(0.15))
        max_rect_w = max(48.0, self.w - safe_margin * 2)
        max_w = max(24.0, max_rect_w - pad_x * 2)
        max_lines = 3

        def append_ellipsis(s):
            ell = "…"
            s = s.rstrip()
            while s and fm.horizontalAdvance(s + ell) > max_w:
                s = s[:-1].rstrip()
            return (s + ell) if s else ell

        # 按字符换行，对中文、英文路径、反斜杠路径都稳定。
        lines = []
        cur = ""
        overflow = False
        for ch in text:
            if ch in "\r\n":
                if cur:
                    lines.append(cur)
                    cur = ""
                if len(lines) >= max_lines:
                    overflow = True
                    break
                continue

            test = cur + ch
            if cur and fm.horizontalAdvance(test) > max_w:
                lines.append(cur)
                cur = ch
                if len(lines) >= max_lines:
                    overflow = True
                    break
            else:
                cur = test

        if not overflow and cur:
            lines.append(cur)

        if len(lines) > max_lines:
            lines = lines[:max_lines]
            overflow = True

        if overflow and lines:
            lines[-1] = append_ellipsis(lines[-1])
        elif not lines:
            lines = [""]

        line_h = fm.height()
        tw = max(fm.horizontalAdvance(line) for line in lines) if lines else 0

        rect_w = min(max_rect_w, tw + pad_x * 2)
        rect_h = line_h * len(lines) + pad_y * 2.0

        # 放在小猫头顶上方，但不允许超出窗口顶部。
        desired_top = self.D(0.0, 2.92).y()
        rect_top = max(safe_margin, desired_top)
        rect_left = (self.w - rect_w) / 2
        rect_left = max(safe_margin, min(self.w - safe_margin - rect_w, rect_left))

        rect = QRectF(rect_left, rect_top, rect_w, rect_h)

        bg = QColor("#1A1A2E")
        bg.setAlphaF(0.78 * opacity)
        border_map = {
            "ok": QColor("#5BFF8F"),
            "warn": QColor("#FFD166"),
            "bad": QColor("#FF6B6B"),
            "tip": QColor("#6BD9FF"),
            "info": QColor("#DDF7FF"),
        }
        border = border_map.get(st.message_kind, QColor("#DDF7FF"))
        border.setAlphaF(0.86 * opacity)

        p.setPen(QPen(border, max(1, int(self.Dlen(0.035)))))
        p.setBrush(bg)
        p.drawRoundedRect(rect, self.Dlen(0.12), self.Dlen(0.12))

        col = QColor("#FFFFFF")
        col.setAlphaF(opacity)
        p.setPen(col)

        y = rect.top() + pad_y + fm.ascent()
        for line in lines:
            x = rect.left() + (rect.width() - fm.horizontalAdvance(line)) / 2
            p.drawText(QPointF(x, y), line)
            y += line_h

        p.restore()

    def _draw_cleanup_status(self, p, st: CatState):
        """清理内存 / 测量网速共用的状态环 + 状态文字。"""
        if (st.cleanup_ring_opacity <= 0.01
                and st.cleanup_text_opacity <= 0.01
                and not st.cleanup_text):
            return

        p.save()
        center = self.D(0.0, -0.12 + st.bob * 0.20)

        if st.cleanup_ring_opacity > 0.01:
            ring = QColor("#6BD9FF")
            ring.setAlphaF(clamp01(st.cleanup_ring_opacity))
            p.setPen(QPen(ring, max(2, int(self.Dlen(0.055))), Qt.SolidLine, Qt.RoundCap))
            p.setBrush(Qt.NoBrush)
            rr = self.Dlen(st.cleanup_ring_radius)
            p.drawEllipse(center, rr, rr)

            inner = QColor("#5BFF8F")
            inner.setAlphaF(clamp01(st.cleanup_ring_opacity * 0.45))
            p.setPen(QPen(inner, max(1, int(self.Dlen(0.035))), Qt.DashLine, Qt.RoundCap))
            p.drawEllipse(center, max(1, rr * 0.62), max(1, rr * 0.62))

        if st.cleanup_text and st.cleanup_text_opacity > 0.01:
            font_size_pt = max(9, int(self.Dlen(0.33)))
            font = QFont("Microsoft YaHei", font_size_pt, QFont.Bold)
            p.setFont(font)
            fm = p.fontMetrics()
            tw = fm.horizontalAdvance(st.cleanup_text)
            pos = self.D(0.0, 2.70)

            bg = QColor("#1A1A2E")
            bg.setAlphaF(clamp01(st.cleanup_text_opacity * 0.70))
            pad_x = self.Dlen(0.18)
            pad_y = self.Dlen(0.10)
            bg_rect = QRectF(
                pos.x() - tw / 2 - pad_x,
                pos.y() - fm.ascent() - pad_y * 0.6,
                tw + pad_x * 2,
                fm.height() + pad_y,
            )
            p.setPen(Qt.NoPen)
            p.setBrush(bg)
            p.drawRoundedRect(bg_rect, self.Dlen(0.10), self.Dlen(0.10))

            col = QColor("#FFFFFF")
            col.setAlphaF(clamp01(st.cleanup_text_opacity))
            p.setPen(col)
            p.drawText(QPointF(pos.x() - tw / 2, pos.y()), st.cleanup_text)

        p.restore()

    # ── 箱子 ──────────────────────────────────────────────
    def _draw_box(self, p: QPainter):
        # 盒子主题：默认单色；“博士红（银领）”使用黑红主体 + 银领装饰，但保留原有图案与公式窗口。
        is_doctoral = (CURRENT_BOX_THEME_NAME == "doctoral_red")

        body_rect = self.design_rect(*BOX_BODY_CENTER, BOX_BODY_W, BOX_BODY_H)
        top_rect = self.design_rect(*BOX_TOP_CENTER, BOX_TOP_W, BOX_TOP_H)

        # 主箱体
        p.setPen(QPen(C_BOX_BORDER, 4))
        p.setBrush(C_BOX_YELLOW)
        p.drawRect(body_rect)

        if is_doctoral:
            p.setPen(Qt.NoPen)

            # 下沿酒红饰带
            lower_band = QRectF(
                body_rect.left(),
                body_rect.bottom() - body_rect.height() * 0.18,
                body_rect.width(),
                body_rect.height() * 0.18,
            )
            p.setBrush(C_BOX_SECONDARY)
            p.drawRect(lower_band)

            # 顶部细银带：代表“银领”
            upper_band = QRectF(
                body_rect.left(),
                body_rect.top(),
                body_rect.width(),
                body_rect.height() * 0.08,
            )
            p.setBrush(C_BOX_PANEL)
            p.drawRect(upper_band)

            # 左右领片：根据学科颜色，模仿学位服领饰，避开左侧辐射标志和右侧公式窗口
            collar_color = C_BOX_PANEL
            # 根据主色动态计算阴影色
            r, g, b, a = collar_color.getRgb()
            # 降低亮度约25%来制造阴影
            collar_shadow = QColor(
                max(0, int(r * 0.75)),
                max(0, int(g * 0.75)),
                max(0, int(b * 0.75))
            )

            left_collar = QPolygonF([
                QPointF(body_rect.left() + body_rect.width() * 0.36, body_rect.top() + body_rect.height() * 0.10),
                QPointF(body_rect.left() + body_rect.width() * 0.46, body_rect.top() + body_rect.height() * 0.10),
                QPointF(body_rect.left() + body_rect.width() * 0.54, body_rect.top() + body_rect.height() * 0.42),
                QPointF(body_rect.left() + body_rect.width() * 0.48, body_rect.top() + body_rect.height() * 0.42),
            ])
            right_collar = QPolygonF([
                QPointF(body_rect.left() + body_rect.width() * 0.54, body_rect.top() + body_rect.height() * 0.10),
                QPointF(body_rect.left() + body_rect.width() * 0.64, body_rect.top() + body_rect.height() * 0.10),
                QPointF(body_rect.left() + body_rect.width() * 0.52, body_rect.top() + body_rect.height() * 0.42),
                QPointF(body_rect.left() + body_rect.width() * 0.46, body_rect.top() + body_rect.height() * 0.42),
            ])
            p.setBrush(collar_shadow)
            p.drawPolygon(left_collar.translated(0, body_rect.height() * 0.012))
            p.drawPolygon(right_collar.translated(0, body_rect.height() * 0.012))

            p.setBrush(collar_color)
            p.drawPolygon(left_collar)
            p.drawPolygon(right_collar)

            # 领片细描边
            p.setPen(QPen(QColor("#F8FAFC"), 1.2))
            p.setBrush(Qt.NoBrush)
            p.drawPolygon(left_collar)
            p.drawPolygon(right_collar)
            p.setPen(Qt.NoPen)

            # 左右小红角，强化黑红主调
            side_w = body_rect.width() * 0.10
            p.setBrush(C_BOX_SECONDARY)
            p.drawRect(QRectF(body_rect.left(), body_rect.top(), side_w, body_rect.height() * 0.30))
            p.drawRect(QRectF(body_rect.right() - side_w, body_rect.top(), side_w, body_rect.height() * 0.30))

        # 原有辐射标志保留
        self._draw_radioactive(p, *RADIO_CENTER)

        # 顶盖与两侧盖板：博士红使用酒红，更像博士服主色
        p.setPen(QPen(C_BOX_BORDER, 4))
        p.setBrush(C_BOX_YELLOW if not is_doctoral else C_BOX_SECONDARY)
        p.drawRect(top_rect)

        left_fill = C_BOX_YELLOW if not is_doctoral else C_BOX_SECONDARY
        self._fill_polygon(p, LID_LEFT_PTS, left_fill, C_BOX_BORDER, 4)
        right_pts = [(-x, y) for (x, y) in LID_LEFT_PTS]
        self._fill_polygon(p, right_pts, left_fill, C_BOX_BORDER, 4)

        if is_doctoral:
            # 盖子加一条银色中线，呼应“银领”
            p.setPen(QPen(C_BOX_PANEL, 2.2))
            p.drawLine(
                QPointF(top_rect.left() + top_rect.width() * 0.08, top_rect.center().y()),
                QPointF(top_rect.right() - top_rect.width() * 0.08, top_rect.center().y()),
            )

        # 锁，必须在所有装饰之后绘制
        p.setPen(Qt.NoPen)
        p.setBrush(C_LOCK)
        p.drawRect(self.design_rect(*LOCK_CENTER, LOCK_W, LOCK_H))
        p.setBrush(C_LOCK_HOLE)
        p.drawEllipse(self.D(*LOCK_CENTER), self.Dlen(LOCK_HOLE_R), self.Dlen(LOCK_HOLE_R))

        # 量子态窗口和公式，必须保留且绘制在最上层
        p.setPen(QPen(C_BOX_BORDER, 2))
        p.setBrush(C_QS_BG)
        rect = self.design_rect(*QS_CENTER, QS_W, QS_H)
        p.drawRoundedRect(rect, self.Dlen(QS_R), self.Dlen(QS_R))
        self._draw_qs_text(p, *QS_CENTER)

    def _draw_radioactive(self, p, cx, cy):
        center = self.D(cx, cy)
        p.setPen(QPen(C_BOX_BORDER, 2)); p.setBrush(C_RADIO_BG)
        p.drawEllipse(center, self.Dlen(RADIO_BG_R), self.Dlen(RADIO_BG_R))
        p.setPen(Qt.NoPen); p.setBrush(C_RADIO_BLADE)
        for i in range(3):
            t0 = math.pi/3 + i * 2*math.pi/3
            self._fill_annular_sector(p, cx, cy,
                                       RADIO_BLADE_IN, RADIO_BLADE_OUT,
                                       t0, math.pi/3)
        p.setBrush(C_RADIO_BLADE)
        p.drawEllipse(center, self.Dlen(RADIO_CENTER_R), self.Dlen(RADIO_CENTER_R))

    def _fill_annular_sector(self, p, cx_d, cy_d, r_in, r_out, t0, dt):
        path = QPainterPath()
        N = 24
        for i in range(N + 1):
            t = t0 + dt * i / N
            pt = self.D(cx_d + r_out*math.cos(t), cy_d + r_out*math.sin(t))
            (path.moveTo if i == 0 else path.lineTo)(pt)
        for i in range(N + 1):
            t = t0 + dt * (1 - i / N)
            path.lineTo(self.D(cx_d + r_in*math.cos(t),
                                cy_d + r_in*math.sin(t)))
        path.closeSubpath()
        p.drawPath(path)

    def _draw_qs_text(self, p, cx, cy):
        size_pt = max(7, int(self.Dlen(0.36)))
        font = QFont("Arial", size_pt, QFont.Bold)
        p.setFont(font)
        fm = p.fontMetrics()
        center = self.D(cx, cy)
        s_left, s_plus, s_right = "|0⟩", " + ", "|1⟩"
        total_w = (fm.horizontalAdvance(s_left)
                   + fm.horizontalAdvance(s_plus)
                   + fm.horizontalAdvance(s_right))
        x = center.x() - total_w / 2
        y = center.y() + fm.ascent() / 2 - 2
        p.setPen(C_QS_KET0)
        p.drawText(QPointF(x, y), s_left); x += fm.horizontalAdvance(s_left)
        p.setPen(C_QS_TEXT)
        p.drawText(QPointF(x, y), s_plus); x += fm.horizontalAdvance(s_plus)
        p.setPen(C_QS_KET1)
        p.drawText(QPointF(x, y), s_right)

    # ── 猫 ──────────────────────────────────────────────────
    def _draw_cat(self, p: QPainter, st: CatState):
        p.save()
        clip_widget_y = self.D(0, CLIP_Y).y()
        p.setClipRect(QRectF(0, 0, self.w, clip_widget_y))

        cat_scale = max(0.08, float(getattr(st, "cat_scale", 1.0)))
        if abs(cat_scale - 1.0) > 0.001:
            anchor = self.D(0.0, -0.12 + st.bob * 0.20)
            p.translate(anchor)
            p.scale(cat_scale, cat_scale)
            p.translate(-anchor)

        cat_dx = float(getattr(st, "cat_offset_x", 0.0))
        cat_dy = float(getattr(st, "cat_offset_y", 0.0))
        cat_tilt = float(getattr(st, "cat_tilt_deg", 0.0))
        if abs(cat_tilt) > 0.001:
            anchor = self.D(0.0, st.bob)
            p.translate(anchor)
            p.rotate(cat_tilt)
            p.translate(-anchor)
        if abs(cat_dx) > 0.001 or abs(cat_dy) > 0.001:
            p.translate(self.Dlen(cat_dx), -self.Dlen(cat_dy))

        rise_dy = -(1.0 - st.rise_progress) * RISE_AMOUNT
        dy_total = rise_dy + st.bob

        ear_outer_l = [(x, y + dy_total) for (x, y) in EAR_OUTER_LEFT]
        ear_outer_r = [(-x, y) for (x, y) in ear_outer_l]
        self._draw_smooth_polygon(p, ear_outer_l, C_HEAD_GREY, C_BOX_BORDER, 3)
        self._draw_smooth_polygon(p, ear_outer_r, C_HEAD_GREY, C_BOX_BORDER, 3)

        ear_inner_l = [(x, y + dy_total) for (x, y) in EAR_INNER_LEFT]
        ear_inner_r = [(-x, y) for (x, y) in ear_inner_l]
        self._draw_smooth_polygon(p, ear_inner_l, C_INNER_EAR, C_INNER_EAR, 0)
        self._draw_smooth_polygon(p, ear_inner_r, C_INNER_EAR, C_INNER_EAR, 0)

        p.setPen(QPen(C_BOX_BORDER, 3)); p.setBrush(C_HEAD_GREY)
        p.drawEllipse(self.design_rect(
            HEAD_CENTER[0], HEAD_CENTER[1] + dy_total, HEAD_W, HEAD_H))

        nose_pts = [(x, y + dy_total) for (x, y) in NOSE_PTS]
        self._fill_polygon(p, nose_pts, C_NOSE, C_BOX_BORDER, 2)

        a, b = NOSE_MOUTH_LINE
        self._draw_line(p, (a[0], a[1] + dy_total), (b[0], b[1] + dy_total),
                        C_BOX_BORDER, 1.5)

        for s_pt, e_pt, ang in WHISKER_DATA:
            self._draw_arc_between(p,
                (s_pt[0], s_pt[1] + dy_total),
                (e_pt[0], e_pt[1] + dy_total),
                ang, C_BOX_BORDER, 3)

        if st.expression == "dead":
            self._draw_dead_face(p, dy_total)
        elif st.expression == "dazed":
            self._draw_dazed_face(p, st, dy_total)
        elif st.expression == "yawn":
            self._draw_yawn_face(p, st, dy_total)
        elif st.expression == "teaser":
            self._draw_teaser_face(p, st, dy_total)
        elif st.expression == "sleep":
            self._draw_sleep_face(p, st, dy_total)
        elif st.expression == "sneeze":
            self._draw_sneeze_face(p, st, dy_total)
        elif st.expression == "stretch":
            self._draw_stretch_face(p, st, dy_total)
        elif st.expression == "shy":
            self._draw_shy_face(p, st, dy_total)
        elif st.expression == "dizzy":
            self._draw_dizzy_face(p, st, dy_total)
        elif st.expression == "sparkle":
            self._draw_sparkle_face(p, st, dy_total)
        elif st.expression == "wink":
            self._draw_wink_face(p, st, dy_total)
        elif st.expression == "lick":
            self._draw_lick_face(p, st, dy_total)
        elif st.expression == "purr":
            self._draw_purr_face(p, st, dy_total)
        else:
            for s_pt, e_pt in RIGHT_EYE_X:
                self._draw_line(p,
                    (s_pt[0], s_pt[1] + dy_total),
                    (e_pt[0], e_pt[1] + dy_total),
                    C_BOX_BORDER, 3)

            # 嘴 (按表情)
            if st.expression == "default":
                (sx, sy), (ex, ey), ang = MOUTH_DEFAULT
                self._draw_arc_between(p,
                    (sx, sy + dy_total), (ex, ey + dy_total),
                    ang, C_BOX_BORDER, 2)
            elif st.expression == "surprise":
                p.setPen(QPen(C_BOX_BORDER, 2)); p.setBrush(Qt.NoBrush)
                cx_, cy_ = MOUTH_SURPRISE_C
                p.drawEllipse(self.D(cx_, cy_ + dy_total),
                              self.Dlen(MOUTH_SURPRISE_R),
                              self.Dlen(MOUTH_SURPRISE_R))
            else:  # angry
                pts = [(x, y + dy_total) for (x, y) in MOUTH_ANGRY_PTS]
                path = QPainterPath()
                path.moveTo(self.D(*pts[0]))
                for pt in pts[1:]:
                    path.lineTo(self.D(*pt))
                p.setPen(QPen(C_BOX_BORDER, 2)); p.setBrush(Qt.NoBrush)
                p.drawPath(path)

            self._draw_left_eye(p, st, dy_total)
        p.restore()

    def _draw_eye_x(self, p, cx, cy, dy_total, size=0.22, sw=3):
        y = cy + dy_total
        self._draw_line(p, (cx - size, y - size), (cx + size, y + size), C_BOX_BORDER, sw)
        self._draw_line(p, (cx - size, y + size), (cx + size, y - size), C_BOX_BORDER, sw)

    def _draw_wavy_mouth(self, p, cx, cy, dy_total, width=0.88, amp=0.055, waves=2.0, sw=2):
        path = QPainterPath()
        steps = 44
        for i in range(steps + 1):
            t = i / steps
            x = cx - width / 2 + width * t
            y = cy + dy_total + amp * math.sin(t * 2 * math.pi * waves)
            pt = self.D(x, y)
            if i == 0:
                path.moveTo(pt)
            else:
                path.lineTo(pt)
        p.setPen(QPen(C_BOX_BORDER, sw, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.setBrush(Qt.NoBrush)
        p.drawPath(path)

    def _draw_dead_face(self, p, dy_total):
        # 参考量子分身爆散里的“死”小猫：双 X 眼 + 波浪嘴。
        self._draw_eye_x(p, -0.72, 0.30, dy_total, size=0.23, sw=3)
        self._draw_eye_x(p,  0.72, 0.30, dy_total, size=0.23, sw=3)
        self._draw_wavy_mouth(p, 0.0, -0.70, dy_total, width=0.92, amp=0.07, waves=2.5, sw=2)

    def _draw_dazed_face(self, p, st: CatState, dy_total):
        # 发呆：半睁眼、小瞳孔、轻微波浪嘴，全部用几何图形画在本体脸上。
        p.save()
        p.setPen(QPen(C_BOX_BORDER, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.setBrush(C_EYE_WHITE)
        for cx in (-0.72, 0.72):
            cy = 0.30 + dy_total
            p.drawEllipse(self.D(cx, cy), self.Dlen(0.30), self.Dlen(0.105))
            p.setBrush(C_PUPIL)
            px = cx + 0.035 * math.sin(st.bob * 30.0 + cx)
            p.drawEllipse(self.D(px, cy - 0.005), self.Dlen(0.055), self.Dlen(0.055))
            p.setBrush(C_EYE_WHITE)

        # 压一条上眼皮，让它看起来是真的“发呆”而不是贴字。
        lid_col = QColor(C_HEAD_GREY)
        p.setPen(QPen(lid_col, max(2, int(self.Dlen(0.055))), Qt.SolidLine, Qt.RoundCap))
        for cx in (-0.72, 0.72):
            y = 0.41 + dy_total
            p.drawLine(self.D(cx - 0.26, y), self.D(cx + 0.26, y))

        self._draw_wavy_mouth(p, 0.0, -0.67, dy_total, width=0.54, amp=0.025, waves=1.0, sw=2)
        p.restore()

    def _draw_yawn_face(self, p, st: CatState, dy_total):
        # 打哈欠：困倦眼 + 张大的椭圆嘴，直接画在本体上。
        p.save()
        p.setPen(QPen(C_BOX_BORDER, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.setBrush(Qt.NoBrush)

        # 两只困倦的半闭眼
        for cx in (-0.72, 0.72):
            self._draw_arc_between(
                p,
                (cx - 0.26, 0.30 + dy_total),
                (cx + 0.26, 0.30 + dy_total),
                -math.pi / 3.4,
                C_BOX_BORDER,
                2,
            )
            p.drawLine(self.D(cx - 0.20, 0.36 + dy_total), self.D(cx + 0.20, 0.36 + dy_total))

        # 哈欠大嘴
        mouth_center = self.D(0.0, -0.78 + dy_total)
        p.setBrush(QColor("#1F2937"))
        p.setPen(QPen(C_BOX_BORDER, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.drawEllipse(mouth_center, self.Dlen(0.23), self.Dlen(0.31))

        # 一点舌头颜色
        p.setBrush(QColor("#F59E9E"))
        p.setPen(Qt.NoPen)
        p.drawEllipse(self.D(0.0, -0.86 + dy_total), self.Dlen(0.10), self.Dlen(0.08))
        p.restore()

    def _draw_teaser_face(self, p, st: CatState, dy_total):
        # 逗猫棒：双眼都出现并追逐小球，避免看起来像残留上一个表情。
        p.save()
        p.setPen(Qt.NoPen)

        gx = GAZE_COEFF * st.look_x
        gy = GAZE_COEFF * st.look_y

        for cx in (-0.72, 0.72):
            cy = 0.30 + dy_total
            p.setBrush(C_EYE_WHITE)
            p.drawEllipse(self.D(cx, cy), self.Dlen(0.33), self.Dlen(0.33))
            p.setBrush(C_PUPIL)
            p.drawEllipse(self.D(cx + gx, cy + gy), self.Dlen(0.14), self.Dlen(0.14))
            p.setBrush(C_EYE_WHITE)
            p.drawEllipse(self.D(cx + gx - 0.03, cy + gy + 0.07), self.Dlen(0.04), self.Dlen(0.04))

        # 专注时的小 O 嘴
        p.setPen(QPen(C_BOX_BORDER, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(self.D(0.0, -0.73 + dy_total), self.Dlen(0.12), self.Dlen(0.16))
        p.restore()

    def _draw_star_shape(self, p, cx, cy, r_outer=0.24, r_inner=0.10, fill=None, stroke=None, sw=2):
        path = QPainterPath()
        for i in range(10):
            a = math.pi / 2 + i * math.pi / 5
            r = r_outer if i % 2 == 0 else r_inner
            pt = self.D(cx + r * math.cos(a), cy + r * math.sin(a))
            if i == 0:
                path.moveTo(pt)
            else:
                path.lineTo(pt)
        path.closeSubpath()
        p.setPen(QPen(stroke or C_BOX_BORDER, sw, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.setBrush(fill or C_EYE_WHITE)
        p.drawPath(path)

    def _draw_spiral_eye(self, p, cx, cy, dy_total, radius=0.28, turns=2.1, sw=2):
        path = QPainterPath()
        steps = 56
        for i in range(steps + 1):
            t = i / steps
            a = t * turns * 2 * math.pi
            r = radius * t
            pt = self.D(cx + r * math.cos(a), cy + dy_total + r * math.sin(a))
            if i == 0:
                path.moveTo(pt)
            else:
                path.lineTo(pt)
        p.setPen(QPen(C_BOX_BORDER, sw, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.setBrush(Qt.NoBrush)
        p.drawPath(path)

    def _draw_sleep_face(self, p, st: CatState, dy_total):
        # 睡觉：闭眼 + 小小安稳嘴，环境 Zzz 由覆盖层画在脸外。
        p.save()
        for cx in (-0.72, 0.72):
            self._draw_arc_between(
                p,
                (cx - 0.28, 0.28 + dy_total),
                (cx + 0.28, 0.28 + dy_total),
                -math.pi / 3.2,
                C_BOX_BORDER,
                2,
            )
        self._draw_arc_between(
            p,
            (-0.22, -0.66 + dy_total),
            (0.22, -0.66 + dy_total),
            math.pi / 1.45,
            C_BOX_BORDER,
            2,
        )
        p.restore()

    def _draw_sneeze_face(self, p, st: CatState, dy_total):
        # 打喷嚏：眯眼 + “>”形嘴，配合覆盖层喷嚏线。
        p.save()
        for cx in (-0.72, 0.72):
            self._draw_arc_between(
                p,
                (cx - 0.26, 0.32 + dy_total),
                (cx + 0.26, 0.32 + dy_total),
                math.pi / 3.8,
                C_BOX_BORDER,
                2,
            )
        path = QPainterPath()
        pts = [(-0.17, -0.67 + dy_total), (0.08, -0.77 + dy_total), (-0.17, -0.87 + dy_total)]
        path.moveTo(self.D(*pts[0]))
        for pt in pts[1:]:
            path.lineTo(self.D(*pt))
        p.setPen(QPen(C_BOX_BORDER, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.setBrush(Qt.NoBrush)
        p.drawPath(path)
        p.restore()

    def _draw_stretch_face(self, p, st: CatState, dy_total):
        # 伸懒腰：开心闭眼 + 大笑嘴，身体上浮由状态推进控制。
        p.save()
        for cx in (-0.72, 0.72):
            self._draw_arc_between(
                p,
                (cx - 0.28, 0.30 + dy_total),
                (cx + 0.28, 0.30 + dy_total),
                -math.pi / 2.6,
                C_BOX_BORDER,
                2,
            )
        self._draw_arc_between(
            p,
            (-0.42, -0.62 + dy_total),
            (0.42, -0.62 + dy_total),
            math.pi / 1.15,
            C_BOX_BORDER,
            2,
        )
        p.restore()

    def _draw_shy_face(self, p, st: CatState, dy_total):
        # 害羞：半闭眼 + 腮红 + 小笑。
        p.save()
        p.setPen(QPen(C_BOX_BORDER, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.setBrush(Qt.NoBrush)
        for cx in (-0.72, 0.72):
            self._draw_arc_between(
                p,
                (cx - 0.24, 0.32 + dy_total),
                (cx + 0.24, 0.32 + dy_total),
                -math.pi / 3.0,
                C_BOX_BORDER,
                2,
            )

        blush = QColor("#FFB6C1")
        blush.setAlphaF(0.70)
        p.setPen(Qt.NoPen)
        p.setBrush(blush)
        p.drawEllipse(self.D(-1.10, -0.28 + dy_total), self.Dlen(0.18), self.Dlen(0.08))
        p.drawEllipse(self.D(1.10, -0.28 + dy_total), self.Dlen(0.18), self.Dlen(0.08))

        self._draw_arc_between(
            p,
            (-0.24, -0.66 + dy_total),
            (0.24, -0.66 + dy_total),
            math.pi / 1.35,
            C_BOX_BORDER,
            2,
        )
        p.restore()

    def _draw_dizzy_face(self, p, st: CatState, dy_total):
        # 转圈晕：双螺旋眼 + 波浪嘴。
        p.save()
        self._draw_spiral_eye(p, -0.72, 0.30, dy_total, radius=0.30, turns=2.2, sw=2)
        self._draw_spiral_eye(p, 0.72, 0.30, dy_total, radius=0.30, turns=2.2, sw=2)
        self._draw_wavy_mouth(p, 0.0, -0.70, dy_total, width=0.72, amp=0.055, waves=2.0, sw=2)
        p.restore()

    def _draw_sparkle_face(self, p, st: CatState, dy_total):
        # 星星眼：眼睛本身变成星星，不是贴图覆盖。
        p.save()
        star_fill = QColor("#FFF3A3")
        for cx in (-0.72, 0.72):
            self._draw_star_shape(p, cx, 0.30 + dy_total, r_outer=0.28, r_inner=0.12, fill=star_fill, stroke=C_BOX_BORDER, sw=2)
        self._draw_arc_between(
            p,
            (-0.34, -0.64 + dy_total),
            (0.34, -0.64 + dy_total),
            math.pi / 1.20,
            C_BOX_BORDER,
            2,
        )
        p.restore()

    def _draw_wink_face(self, p, st: CatState, dy_total):
        # 眨一只眼：一只眼正常，一只眼闭上，直接画在本体脸上。
        p.save()
        p.setPen(Qt.NoPen)
        p.setBrush(C_EYE_WHITE)
        p.drawEllipse(self.D(-0.72, 0.30 + dy_total), self.Dlen(0.34), self.Dlen(0.34))
        p.setBrush(C_PUPIL)
        p.drawEllipse(self.D(-0.72 + 0.04 * math.sin(self._safe_time(st)), 0.30 + dy_total), self.Dlen(0.13), self.Dlen(0.13))

        self._draw_arc_between(
            p,
            (0.48, 0.31 + dy_total),
            (0.96, 0.31 + dy_total),
            -math.pi / 2.6,
            C_BOX_BORDER,
            3,
        )
        self._draw_arc_between(
            p,
            (-0.34, -0.64 + dy_total),
            (0.34, -0.64 + dy_total),
            math.pi / 1.2,
            C_BOX_BORDER,
            2,
        )
        p.restore()

    def _draw_lick_face(self, p, st: CatState, dy_total):
        # 舔鼻子：眯眼 + 小舌头，舌头也画在脸部几何里。
        p.save()
        for cx in (-0.72, 0.72):
            self._draw_arc_between(
                p,
                (cx - 0.26, 0.30 + dy_total),
                (cx + 0.26, 0.30 + dy_total),
                -math.pi / 3.0,
                C_BOX_BORDER,
                2,
            )

        self._draw_arc_between(
            p,
            (-0.18, -0.66 + dy_total),
            (0.18, -0.66 + dy_total),
            math.pi / 1.4,
            C_BOX_BORDER,
            2,
        )
        tongue = QColor("#F59E9E")
        p.setPen(QPen(C_BOX_BORDER, 1, Qt.SolidLine, Qt.RoundCap))
        p.setBrush(tongue)
        p.drawEllipse(self.D(0.04, -0.52 + dy_total), self.Dlen(0.11), self.Dlen(0.16))
        p.restore()

    def _draw_purr_face(self, p, st: CatState, dy_total):
        # 咕噜开心：闭眼笑 + 腮红。
        p.save()
        for cx in (-0.72, 0.72):
            self._draw_arc_between(
                p,
                (cx - 0.27, 0.31 + dy_total),
                (cx + 0.27, 0.31 + dy_total),
                -math.pi / 2.8,
                C_BOX_BORDER,
                2,
            )

        blush = QColor("#FFB6C1")
        blush.setAlphaF(0.62)
        p.setPen(Qt.NoPen)
        p.setBrush(blush)
        p.drawEllipse(self.D(-1.10, -0.28 + dy_total), self.Dlen(0.18), self.Dlen(0.075))
        p.drawEllipse(self.D(1.10, -0.28 + dy_total), self.Dlen(0.18), self.Dlen(0.075))

        self._draw_arc_between(
            p,
            (-0.38, -0.62 + dy_total),
            (0.38, -0.62 + dy_total),
            math.pi / 1.10,
            C_BOX_BORDER,
            2,
        )
        p.restore()

    def _safe_time(self, st):
        # Renderer 没有全局时钟，借用 bob 的微小变化即可避免完全静态。
        return float(getattr(st, "bob", 0.0)) * 30.0

    def _draw_left_eye(self, p, st: CatState, dy_total):
        cfg = EYE_CFG[st.expression]
        cx, cy = cfg["c"]
        cy = cy + dy_total
        gx = GAZE_COEFF * st.look_x
        gy = GAZE_COEFF * st.look_y

        sq = max(0.05, 1.0 - 0.95 * st.blink)
        wr_x = cfg["white_r"]
        wr_y = cfg["white_r"] * cfg["w_squash"] * sq
        pr_x = cfg["pupil_r"]
        pr_y = cfg["pupil_r"] * cfg["p_squash"] * sq
        hr_x = cfg["hl_r"]
        hr_y = cfg["hl_r"] * sq

        p.setPen(Qt.NoPen); p.setBrush(C_EYE_WHITE)
        p.drawEllipse(self.D(cx, cy), self.Dlen(wr_x), self.Dlen(wr_y))

        p.setBrush(C_PUPIL)
        p.drawEllipse(self.D(cx + gx, cy + gy),
                      self.Dlen(pr_x), self.Dlen(pr_y))

        hl_dx, hl_dy = cfg["hl_offset"]
        p.setBrush(C_EYE_WHITE)
        p.drawEllipse(self.D(cx + gx + hl_dx, cy + gy + hl_dy),
                      self.Dlen(hr_x), self.Dlen(hr_y))

    # ── 符号 (惊叹号 / 愤怒) ────────────────────────────────
    def _draw_symbols(self, p, st: CatState):
        if st.rise_progress < 0.5:
            return
        if st.show_excl < 0.05 and st.show_anger < 0.05:
            return
        rise_dy = -(1.0 - st.rise_progress) * RISE_AMOUNT
        sym_x = 0.4
        # baseline 紧贴耳尖上方 (耳尖 y=2.08, baseline 在 2.18)
        sym_y = 2.08 + 0.10 + rise_dy + st.bob

        if st.show_excl > 0.05:
            font_size_pt = max(11, int(self.Dlen(0.85)))
            font = QFont("Arial", font_size_pt, QFont.Bold)
            p.setFont(font)
            col = QColor(C_RED_SYMBOL); col.setAlphaF(min(1.0, st.show_excl))
            p.setPen(col)
            text = "!"
            fm = p.fontMetrics()
            tw = fm.horizontalAdvance(text)
            base = self.D(sym_x, sym_y)
            p.drawText(QPointF(base.x() - tw / 2, base.y()), text)

        if st.show_anger > 0.05:
            font_size_pt = max(11, int(self.Dlen(0.75)))
            font = QFont("Arial", font_size_pt, QFont.Bold)
            p.setFont(font)
            col = QColor(C_RED_SYMBOL); col.setAlphaF(min(1.0, st.show_anger))
            p.setPen(col)
            text = "💢"
            fm = p.fontMetrics()
            tw = fm.horizontalAdvance(text)
            base = self.D(sym_x, sym_y)
            p.drawText(QPointF(base.x() - tw / 2, base.y()), text)

    # ── 通用工具 ──────────────────────────────────────────
    def _fill_polygon(self, p, pts, fill, stroke, sw):
        path = QPainterPath()
        path.moveTo(self.D(*pts[0]))
        for x, y in pts[1:]:
            path.lineTo(self.D(x, y))
        path.closeSubpath()
        p.setPen(QPen(stroke, sw) if sw > 0 else Qt.NoPen)
        p.setBrush(fill)
        p.drawPath(path)

    def _draw_smooth_polygon(self, p, pts, fill, stroke, sw):
        if len(pts) >= 2 and pts[0] == pts[-1]:
            pts = pts[:-1]
        qpts = [self.D(x, y) for (x, y) in pts]
        path = catmull_rom_to_path(qpts, closed=True)
        p.setPen(QPen(stroke, sw) if sw > 0 else Qt.NoPen)
        p.setBrush(fill)
        p.drawPath(path)

    def _draw_line(self, p, pa, pb, color, sw):
        p.setPen(QPen(color, sw, Qt.SolidLine, Qt.RoundCap))
        p.setBrush(Qt.NoBrush)
        p.drawLine(self.D(*pa), self.D(*pb))

    def _draw_arc_between(self, p, start, end, angle, color, sw):
        """复刻 manim ArcBetweenPoints(start, end, angle):
           正 angle → 弧鼓向 chord 方向 (start→end) 的"右侧" (在 y-up
           坐标里, 即 chord 方向旋转 -90° 的方向)。

           v2 修正: 圆心偏移和 sweep 方向都翻了号, 之前是反的。
        """
        sx, sy = start
        ex, ey = end
        mx, my = (sx + ex) / 2, (sy + ey) / 2
        dx, dy = ex - sx, ey - sy
        L = math.hypot(dx, dy)
        if L < 1e-7 or abs(angle) < 1e-7:
            self._draw_line(p, start, end, color, sw)
            return
        R = L / (2 * math.sin(abs(angle) / 2))
        d_chord = R * math.cos(abs(angle) / 2)
        sign = 1 if angle > 0 else -1
        # 圆心: 位于 chord 的"另一侧" (远离弧鼓起方向)
        cx_ = mx + sign * d_chord * (-dy / L)
        cy_ = my + sign * d_chord * ( dx / L)
        a_start = math.atan2(sy - cy_, sx - cx_)
        sweep = angle
        N = 28
        path = QPainterPath()
        path.moveTo(self.D(sx, sy))
        for i in range(1, N + 1):
            t = i / N
            a = a_start + sweep * t
            x = cx_ + R * math.cos(a)
            y = cy_ + R * math.sin(a)
            path.lineTo(self.D(x, y))
        p.setPen(QPen(color, sw, Qt.SolidLine, Qt.RoundCap))
        p.setBrush(Qt.NoBrush)
        p.drawPath(path)


# ════════════════════════════════════════════════════════════════
#  桌宠主窗口
# ════════════════════════════════════════════════════════════════

HOTKEY_ACTION_LABELS = {
    "command_palette": "打开命令面板",
    "toggle_pet": "显示 / 隐藏小猫",
    "clean_memory": "清理运行内存",
    "speed_test": "测量网速",
    "organize_downloads": "整理下载文件夹",
    "quantum": "量子分裂 / 坍缩",
}

DEFAULT_HOTKEYS = {
    # 使用 Ctrl + 数字，简单好记。
    "command_palette": "Ctrl+1",
    "toggle_pet": "Ctrl+2",
    "clean_memory": "Ctrl+3",
    "speed_test": "Ctrl+4",
    "organize_downloads": "Ctrl+5",
    "quantum": "Ctrl+6",
}

OLD_DEFAULT_HOTKEYS = {
    "command_palette": "Ctrl+Alt+O",
    "toggle_pet": "Ctrl+Alt+P",
    "clean_memory": "Ctrl+Alt+C",
    "speed_test": "Ctrl+Alt+S",
    "organize_downloads": "Ctrl+Alt+D",
    "quantum": "Ctrl+Alt+Q",
}

OLD_DEFAULT_HOTKEYS_V53 = {
    "command_palette": "Ctrl+Alt+Shift+F7",
    "toggle_pet": "Ctrl+Alt+Shift+F8",
    "clean_memory": "Ctrl+Alt+Shift+F9",
    "speed_test": "Ctrl+Alt+Shift+F10",
    "organize_downloads": "Ctrl+Alt+Shift+F11",
    "quantum": "Ctrl+Alt+Shift+F12",
}


AUTO_FUN_ACTION_LABELS = {
    "pat": "摸摸头",
    "teaser": "逗猫棒",
    "lookaround": "左看右看",
    "lookup": "抬头看天",
    "lookdown": "低头看看",
    "tilt": "歪头卖萌",
    "nod": "点头",
    "shake": "摇头",
    "think": "思考",
    "peek": "偷看",
    "startled": "吓一跳",
    "nuzzle": "蹭盒子",
    "napwake": "打盹惊醒",
    "search": "找东西",
    "earwiggle": "耳朵抖",
    "wink": "眨一只眼",
    "lick": "舔鼻子",
    "happybounce": "开心蹦一下",
    "purr": "咕噜开心",
    "yawn": "打哈欠",
    "dazed": "发呆",
    "sleep": "睡觉",
    "sneeze": "打喷嚏",
    "stretch": "伸懒腰",
    "shy": "害羞",
    "dizzy": "转圈晕",
    "sparkle": "星星眼",
    "dead": "装死",
}

AUTO_FUN_ACTION_SPECS = {
    "pat": {"duration": 3.4, "expression": "default"},
    "teaser": {"duration": 5.0, "expression": "teaser"},
    "lookaround": {"duration": 4.2, "expression": "default"},
    "lookup": {"duration": 3.4, "expression": "default"},
    "lookdown": {"duration": 3.4, "expression": "default"},
    "tilt": {"duration": 3.6, "expression": "default"},
    "nod": {"duration": 2.8, "expression": "default"},
    "shake": {"duration": 2.8, "expression": "default"},
    "think": {"duration": 4.0, "expression": "dazed"},
    "peek": {"duration": 4.0, "expression": "surprise"},
    "startled": {"duration": 2.2, "expression": "surprise"},
    "nuzzle": {"duration": 3.5, "expression": "default"},
    "napwake": {"duration": 4.5, "expression": "sleep"},
    "search": {"duration": 4.4, "expression": "surprise"},
    "earwiggle": {"duration": 2.6, "expression": "default"},
    "wink": {"duration": 3.0, "expression": "wink"},
    "lick": {"duration": 2.8, "expression": "lick"},
    "happybounce": {"duration": 3.4, "expression": "default"},
    "purr": {"duration": 4.0, "expression": "purr"},
    "yawn": {"duration": 3.8, "expression": "yawn"},
    "dazed": {"duration": 4.0, "expression": "dazed"},
    "sleep": {"duration": 5.2, "expression": "sleep"},
    "sneeze": {"duration": 2.6, "expression": "sneeze"},
    "stretch": {"duration": 3.6, "expression": "stretch"},
    "shy": {"duration": 3.8, "expression": "shy"},
    "dizzy": {"duration": 3.4, "expression": "dizzy"},
    "sparkle": {"duration": 3.6, "expression": "sparkle"},
    "dead": {"duration": 3.2, "expression": "dead"},
}


def _normalize_auto_fun_actions(value):
    """清洗“随时间自动好玩动作”配置。默认让所有好玩动作都参与。"""
    result = {name: True for name in AUTO_FUN_ACTION_LABELS}

    if isinstance(value, dict):
        for name in AUTO_FUN_ACTION_LABELS:
            if name in value:
                result[name] = bool(value.get(name))
        return result

    if isinstance(value, (list, tuple, set)):
        enabled = {str(x).strip() for x in value}
        return {name: name in enabled for name in AUTO_FUN_ACTION_LABELS}

    return result


def _normalize_hotkeys(value):
    result = dict(DEFAULT_HOTKEYS)
    if isinstance(value, dict):
        for key in DEFAULT_HOTKEYS:
            saved = str(value.get(key, result[key])).strip()
            # 若配置里仍是旧版默认快捷键，自动迁移到 Ctrl + 数字；
            # 若用户已经改成自己的快捷键，则保留用户设置。
            if saved in (OLD_DEFAULT_HOTKEYS.get(key), OLD_DEFAULT_HOTKEYS_V53.get(key)):
                saved = DEFAULT_HOTKEYS[key]
            result[key] = saved
    return result


def _vk_for_key_name(name):
    name = str(name or "").strip().upper()
    if not name:
        return None
    if len(name) == 1 and "A" <= name <= "Z":
        return ord(name)
    if len(name) == 1 and "0" <= name <= "9":
        return ord(name)
    if name.startswith("F"):
        try:
            n = int(name[1:])
            if 1 <= n <= 12:
                return 0x70 + n - 1
        except Exception:
            return None
    return {
        "SPACE": 0x20, "TAB": 0x09, "ESC": 0x1B, "ESCAPE": 0x1B,
        "ENTER": 0x0D, "RETURN": 0x0D, "BACKSPACE": 0x08,
        "UP": 0x26, "DOWN": 0x28, "LEFT": 0x25, "RIGHT": 0x27,
        "HOME": 0x24, "END": 0x23, "PAGEUP": 0x21, "PAGEDOWN": 0x22,
        "INSERT": 0x2D, "DELETE": 0x2E,
    }.get(name)


def _parse_hotkey_sequence(seq):
    seq = str(seq or "").strip()
    if not seq:
        return None
    parts = [p.strip() for p in seq.replace("＋", "+").split("+") if p.strip()]
    keys = []
    for part in parts:
        up = part.upper()
        if up in ("CTRL", "CONTROL"):
            keys.append(0x11)
        elif up == "ALT":
            keys.append(0x12)
        elif up == "SHIFT":
            keys.append(0x10)
        elif up in ("WIN", "WINDOWS", "META"):
            keys.append(0x5B)
        else:
            vk = _vk_for_key_name(up)
            if vk is None:
                return None
            keys.append(vk)
    return tuple(dict.fromkeys(keys))


def _is_hotkey_pressed(seq):
    if not sys.platform.startswith("win"):
        return False
    keys = _parse_hotkey_sequence(seq)
    if not keys:
        return False
    try:
        user32 = ctypes.windll.user32
        return all(user32.GetAsyncKeyState(int(vk)) & 0x8000 for vk in keys)
    except Exception:
        return False


def _is_ctrl_pressed_global():
    """即使小猫处于鼠标穿透状态，也能通过轮询检测 Ctrl 是否按下。"""
    try:
        if sys.platform.startswith("win"):
            return bool(ctypes.windll.user32.GetAsyncKeyState(0x11) & 0x8000)
        return bool(QApplication.keyboardModifiers() & Qt.ControlModifier)
    except Exception:
        return False


class NetworkTargetEditDialog(QDialog):
    """新增 / 编辑网络检测目标。"""

    def __init__(self, parent=None, target=None, title="网络检测目标"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(480, 180)

        target = target or {}
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("例如：Baidu / GitHub / Router")
        self.name_edit.setText(str(target.get("name", "")))

        self.host_edit = QLineEdit()
        self.host_edit.setPlaceholderText("例如：www.baidu.com 或 1.1.1.1")
        self.host_edit.setText(str(target.get("host", "")))

        self.port_spin = NoWheelSpinBox()
        self.port_spin.setRange(1, 65535)
        self.port_spin.setValue(int(target.get("port", 443) or 443))

        form.addRow("显示名称", self.name_edit)
        form.addRow("主机 / IP", self.host_edit)
        form.addRow("端口", self.port_spin)
        layout.addLayout(form)

        hint = QLabel("说明：网络检测使用 TCP 连接测试。常用端口：DNS 53，HTTPS 443，HTTP 80。")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._accept_checked)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _accept_checked(self):
        host = self.host_edit.text().strip()
        if not host:
            QMessageBox.warning(self, "主机不能为空", "请填写要检测的域名或 IP。")
            return
        if not self.name_edit.text().strip():
            self.name_edit.setText(host)
        self.accept()

    def target_data(self):
        return {
            "name": self.name_edit.text().strip(),
            "host": self.host_edit.text().strip(),
            "port": int(self.port_spin.value()),
        }


class CommandPaletteDialog(QDialog):
    """命令面板：用搜索快速执行桌宠功能、快捷工具和常用软件。"""

    def __init__(self, pet):
        super().__init__(pet)
        self.pet = pet
        self.setWindowTitle("命令面板")
        self.resize(560, 520)
        self._all_commands = []
        self._build_ui()
        self.refresh_commands()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(10)

        title = QLabel("命令面板")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        desc = QLabel("输入关键词快速执行功能、打开工具或启动常用软件。双击项目或按“执行”。")
        desc.setWordWrap(True)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("例如：清理、测速、网络、设置、下载...")
        self.search_edit.textChanged.connect(self._filter_commands)

        self.command_list = QListWidget()
        self.command_list.itemDoubleClicked.connect(lambda _item: self._run_selected())

        row = QHBoxLayout()
        self.btn_run = QPushButton("执行")
        self.btn_refresh = QPushButton("刷新列表")
        self.btn_close = QPushButton("关闭")
        self.btn_run.clicked.connect(self._run_selected)
        self.btn_refresh.clicked.connect(self.refresh_commands)
        self.btn_close.clicked.connect(self.close)
        row.addWidget(self.btn_run)
        row.addWidget(self.btn_refresh)
        row.addStretch(1)
        row.addWidget(self.btn_close)

        root.addWidget(title)
        root.addWidget(desc)
        root.addWidget(self.search_edit)
        root.addWidget(self.command_list, 1)
        root.addLayout(row)

    def refresh_commands(self):
        pet = self.pet
        cmds = [
            {"title": "查看电脑状态", "group": "功能", "keywords": "cpu 内存 状态 电脑", "type": "method", "name": "status"},
            {"title": "清理运行内存", "group": "功能", "keywords": "清理 内存 ram memory", "type": "method", "name": "clean"},
            {"title": "测量网速", "group": "功能", "keywords": "网速 speed 下载 测速", "type": "method", "name": "speed"},
            {"title": "检查网络状态", "group": "功能", "keywords": "网络 ping 连通 延迟", "type": "method", "name": "network"},
            {"title": "整理下载文件夹", "group": "功能", "keywords": "下载 整理 文件夹 分类", "type": "method", "name": "organize"},
            {"title": "清空回收站", "group": "功能", "keywords": "回收站 垃圾 trash recycle", "type": "method", "name": "recycle"},
            {"title": "打开设置界面", "group": "设置", "keywords": "设置 配置 setting", "type": "method", "name": "settings"},
            {"title": "沉箱再跳出", "group": "动作", "keywords": "动画 沉箱 跳出", "type": "method", "name": "sink"},
            {"title": "量子分裂 / 坍缩", "group": "动作", "keywords": "量子 分裂 坍缩 动画", "type": "method", "name": "quantum"},
            {"title": "收纳 / 弹出边缘", "group": "动作", "keywords": "边缘 收纳 弹出 dock", "type": "method", "name": "dock"},
            {"title": "隐藏到托盘", "group": "系统", "keywords": "隐藏 托盘 hide", "type": "method", "name": "hide"},
        ]

        for item in pet._quick_tools:
            if not item.get("show_in_palette", True):
                continue
            title = str(item.get("name", "未命名工具")).strip() or "未命名工具"
            cmds.append({
                "title": title,
                "group": "快捷工具",
                "keywords": title + " 工具 快捷",
                "type": "launch",
                "item": dict(item),
            })

        for item in pet._custom_apps:
            if not item.get("show_in_palette", True):
                continue
            title = str(item.get("name", "未命名软件")).strip() or "未命名软件"
            cmds.append({
                "title": title,
                "group": "常用软件",
                "keywords": title + " 软件 app program",
                "type": "launch",
                "item": dict(item),
            })

        self._all_commands = cmds
        self._filter_commands()

    def _filter_commands(self):
        query = self.search_edit.text().strip().lower()
        tokens = [t for t in query.split() if t]
        self.command_list.clear()

        for cmd in self._all_commands:
            hay = f"{cmd.get('title', '')} {cmd.get('group', '')} {cmd.get('keywords', '')}".lower()
            if tokens and not all(t in hay for t in tokens):
                continue
            row = QListWidgetItem(f"{cmd.get('title')}    [{cmd.get('group')}]")
            if cmd.get("type") == "launch":
                icon = launch_item_icon(cmd.get("item", {}))
                if not icon.isNull():
                    row.setIcon(icon)
            row.setData(Qt.UserRole, dict(cmd))
            self.command_list.addItem(row)

        if self.command_list.count() > 0:
            self.command_list.setCurrentRow(0)

    def _run_selected(self):
        item = self.command_list.currentItem()
        if item is None:
            return
        cmd = item.data(Qt.UserRole) or {}
        self.run_command(cmd)

    def run_command(self, cmd):
        pet = self.pet
        ctype = cmd.get("type")
        name = cmd.get("name")

        if ctype == "launch":
            pet._open_launch_item(cmd.get("item", {}))
            return

        if name == "status":
            pet._start_system_status_check(show_always=True)
        elif name == "clean":
            pet._start_cleanup_effect()
        elif name == "speed":
            pet._start_speedtest_effect()
        elif name == "network":
            pet._start_network_check(show_always=True)
        elif name == "organize":
            pet._organize_downloads_action()
        elif name == "recycle":
            pet._empty_recycle_bin_action()
        elif name == "settings":
            pet._open_settings_panel()
        elif name == "sink":
            pet.trigger_sink_pop()
        elif name == "quantum":
            pet._start_quantum_effect()
        elif name == "dock":
            if pet._edge_dock_visual_edge:
                pet._edge_dock_hover_reveal = True
                pet._undock_from_edge()
            else:
                edge, _dist = pet._nearest_screen_edge()
                pet._dock_to_edge(edge)
        elif name == "hide":
            pet.hide()
        else:
            pet._show_message("未知命令", "warn", 1.6)


class DownloadRuleEditDialog(QDialog):
    """新增 / 编辑下载整理规则。"""

    def __init__(self, parent=None, rule=None, title="整理规则"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(560, 190)

        rule = rule or {}
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.ext_edit = QLineEdit()
        self.ext_edit.setPlaceholderText("例如：.py .js .json，或 * 表示其他文件")
        self.ext_edit.setText(str(rule.get("extensions", "")))

        self.folder_edit = QLineEdit()
        self.folder_edit.setPlaceholderText("例如：Code，多个候选用 | 分隔，如 Images|Pictures")
        self.folder_edit.setText(str(rule.get("folders", rule.get("folder", ""))))

        form.addRow("文件后缀", self.ext_edit)
        form.addRow("目标文件夹", self.folder_edit)
        layout.addLayout(form)

        hint = QLabel("说明：目标文件夹必须已经存在；程序不会自动新建文件夹。多个后缀用空格分隔。")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._accept_checked)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _accept_checked(self):
        if not self.ext_edit.text().strip():
            QMessageBox.warning(self, "后缀不能为空", "请填写文件后缀，例如 .py .js。")
            return
        if not self.folder_edit.text().strip():
            QMessageBox.warning(self, "目标文件夹不能为空", "请填写已有目标文件夹名称。")
            return
        self.accept()

    def rule_data(self):
        return {
            "extensions": self.ext_edit.text().strip(),
            "folders": self.folder_edit.text().strip(),
        }


class LaunchItemEditDialog(QDialog):
    """新增 / 编辑自定义启动项。"""

    def __init__(self, parent=None, item=None, title="启动项"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(520, 180)

        item = item or {}
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("例如：微信 / VS Code / 我的工具")
        self.name_edit.setText(str(item.get("name", "")))

        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText(r"例如：D:\Apps\xxx\xxx.exe")
        self.path_edit.setText(str(item.get("path", "")))

        path_row = QHBoxLayout()
        path_row.addWidget(self.path_edit, 1)
        btn_browse = QPushButton("浏览...")
        btn_browse.clicked.connect(self._browse)
        path_row.addWidget(btn_browse)

        self.args_edit = QLineEdit()
        self.args_edit.setPlaceholderText("可选，大多数软件不用填")
        self.args_edit.setText(str(item.get("args", "")))

        self.category_edit = QLineEdit()
        self.category_edit.setPlaceholderText("例如：系统维护 / 搜索工具 / 自定义")
        self.category_edit.setText(str(item.get("category", "默认")))

        self.cb_show_menu = QCheckBox("显示在右键菜单")
        self.cb_show_menu.setChecked(bool(item.get("show_in_menu", True)))
        self.cb_show_palette = QCheckBox("显示在命令面板")
        self.cb_show_palette.setChecked(bool(item.get("show_in_palette", True)))
        self.cb_run_admin = QCheckBox("以管理员身份运行")
        self.cb_run_admin.setChecked(bool(item.get("run_as_admin", False)))

        form.addRow("显示名称", self.name_edit)
        form.addRow("程序 / 文件夹路径", path_row)
        form.addRow("启动参数", self.args_edit)
        form.addRow("分类", self.category_edit)
        form.addRow("右键菜单", self.cb_show_menu)
        form.addRow("命令面板", self.cb_show_palette)
        form.addRow("权限", self.cb_run_admin)

        layout.addLayout(form)

        hint = QLabel("说明：可以选择 exe，也可以填写文件夹路径。路径有空格或中文也可以。")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._accept_checked)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "选择程序",
            "",
            "Programs (*.exe);;All files (*.*)",
        )
        if not path:
            directory = QFileDialog.getExistingDirectory(self, "或选择文件夹")
            path = directory

        if path:
            self.path_edit.setText(path)
            if not self.name_edit.text().strip():
                self.name_edit.setText(Path(path).stem or Path(path).name)

    def _accept_checked(self):
        name = self.name_edit.text().strip()
        path = self.path_edit.text().strip().strip('"')
        if not name:
            QMessageBox.warning(self, "名称不能为空", "请填写右键/设置界面中显示的名称。")
            return
        if not path:
            QMessageBox.warning(self, "路径不能为空", "请填写或选择程序路径。")
            return
        self.accept()

    def item_data(self):
        return {
            "name": self.name_edit.text().strip(),
            "type": "path",
            "path": self.path_edit.text().strip().strip('"'),
            "args": self.args_edit.text().strip(),
            "category": self.category_edit.text().strip() or "默认",
            "show_in_menu": self.cb_show_menu.isChecked(),
            "show_in_palette": self.cb_show_palette.isChecked(),
            "run_as_admin": self.cb_run_admin.isChecked(),
        }


SETTING_CENTER_ACCENTS = {
    "cyan": {"label": "量子青", "accent": "#00D4FF", "accent_soft": "#1E293B", "switch": "#1463FF", "focus": "#00D4FF"},
    "blue": {"label": "星河蓝", "accent": "#3B82F6", "accent_soft": "#172554", "switch": "#2563EB", "focus": "#60A5FA"},
    "purple": {"label": "量子紫", "accent": "#A78BFA", "accent_soft": "#2E214F", "switch": "#7C3AED", "focus": "#C4B5FD"},
    "pink": {"label": "樱花粉", "accent": "#F472B6", "accent_soft": "#4A1932", "switch": "#DB2777", "focus": "#F9A8D4"},
    "green": {"label": "薄荷绿", "accent": "#34D399", "accent_soft": "#123524", "switch": "#10B981", "focus": "#6EE7B7"},
    "orange": {"label": "暖阳橙", "accent": "#F59E0B", "accent_soft": "#3A2412", "switch": "#EA580C", "focus": "#FBBF24"},
    "red": {"label": "危险红", "accent": "#F87171", "accent_soft": "#3B1115", "switch": "#DC2626", "focus": "#FCA5A5"},
    "mono": {"label": "银灰极简", "accent": "#CBD5E1", "accent_soft": "#29313D", "switch": "#64748B", "focus": "#E2E8F0"},
}

_SETTINGS_CENTER_ACCENT_NAME = "cyan"


def settings_center_accent_palette(name=None):
    key = name or _SETTINGS_CENTER_ACCENT_NAME
    return SETTING_CENTER_ACCENTS.get(key) or SETTING_CENTER_ACCENTS["cyan"]


def set_settings_center_accent(name):
    global _SETTINGS_CENTER_ACCENT_NAME
    if name not in SETTING_CENTER_ACCENTS:
        name = "cyan"
    _SETTINGS_CENTER_ACCENT_NAME = name
    return name


class ModernSwitch(QCheckBox):
    """现代化开关控件：蓝色开启、深色关闭，适配设置中心深色 Fluent 风格。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("")
        self.setCursor(Qt.PointingHandCursor)
        # 稍微放大开关，实际点击区域也跟着变大。
        self.setFixedSize(68, 36)
        self.setFocusPolicy(Qt.StrongFocus)

    def sizeHint(self):
        return QSize(68, 36)

    def minimumSizeHint(self):
        return QSize(68, 36)

    def hitButton(self, pos):
        # QCheckBox 在某些样式下只把 indicator 当作有效点击区。
        # 这里强制整个控件矩形都可点击。
        return self.rect().contains(pos)

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)

        w = self.width()
        h = self.height()
        margin = 2
        track = QRectF(margin, margin, w - margin * 2, h - margin * 2)
        radius = track.height() / 2

        checked = self.isChecked()
        enabled = self.isEnabled()

        pal = settings_center_accent_palette()
        switch_color = pal.get("switch", "#1463FF")

        if checked:
            track_color = QColor(switch_color) if enabled else QColor("#385A9A")
            knob_color = QColor("#FFFFFF") if enabled else QColor("#CBD5E1")
        else:
            track_color = QColor("#2B2F3A") if enabled else QColor("#1E222A")
            knob_color = QColor("#94A3B8") if enabled else QColor("#64748B")

        border_color = QColor(switch_color) if checked else QColor("#3B404D")
        if not enabled:
            border_color = QColor("#2B2F3A")

        p.setPen(QPen(border_color, 1))
        p.setBrush(track_color)
        p.drawRoundedRect(track, radius, radius)

        knob_d = h - 9
        knob_y = (h - knob_d) / 2
        knob_x = w - knob_d - 5 if checked else 5

        # 轻微阴影感：先画一层半透明暗影，再画按钮。
        shadow = QColor("#000000")
        shadow.setAlpha(45 if enabled else 20)
        p.setPen(Qt.NoPen)
        p.setBrush(shadow)
        p.drawEllipse(QRectF(knob_x, knob_y + 1.2, knob_d, knob_d))

        p.setBrush(knob_color)
        p.drawEllipse(QRectF(knob_x, knob_y, knob_d, knob_d))
        p.end()


class SwitchField(QWidget):
    """开关设置行右侧区域：不只开关本体，右侧整片区域都可以点击切换。"""

    def __init__(self, switch, parent=None):
        super().__init__(parent)
        self._switch = switch
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(max(44, switch.height() + 8))
        self.setToolTip("点击此区域可切换开关")

        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)
        row.addStretch(1)
        row.addWidget(switch, 0, Qt.AlignRight | Qt.AlignVCenter)

    def mouseReleaseEvent(self, ev):
        if ev.button() == Qt.LeftButton:
            try:
                pos = ev.position().toPoint()
            except Exception:
                pos = ev.pos()

            # 如果点在子开关控件自身上，交给 ModernSwitch 默认处理；
            # 如果点在开关周围空白区域，则这里代为切换。
            if not self._switch.geometry().contains(pos):
                self._switch.toggle()
                ev.accept()
                return

        super().mouseReleaseEvent(ev)



class CustomCalendarWidget(QCalendarWidget):
    """自定义日历控件，用不同颜色标记今天和选中日期"""
    def __init__(self, parent=None, accent="#8B5CF6", focus="#C4B5FD"):
        super().__init__(parent)
        self.today_qdate = QDate.currentDate()
        self.setGridVisible(False)
        self.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.setNavigationBarVisible(True)
        self.accent = accent
        self.focus = focus
    
    def setColors(self, accent, focus):
        """更新主题颜色"""
        self.accent = accent
        self.focus = focus
        self.update()
    
    def paintCell(self, painter, rect, date):
        """重写单元格绘制方法，用不同颜色标记今天和选中日期"""
        # 获取日期信息
        is_today = date == self.today_qdate
        is_selected = date == self.selectedDate()
        
        painter.save()
        
        # 先让父类绘制基础内容
        super().paintCell(painter, rect, date)
        
        # 再在上面绘制我们的标记
        if is_selected:
            # 选中日期：主题色背景
            accent_color = QColor(self.accent)
            accent_color.setAlpha(200)
            painter.setBrush(accent_color)
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(rect.adjusted(3, 3, -3, -3), 8, 8)
        elif is_today:
            # 今天：主题色边框
            focus_color = QColor(self.focus)
            painter.setBrush(Qt.NoBrush)
            painter.setPen(QPen(focus_color, 3))
            painter.drawRoundedRect(rect.adjusted(3, 3, -3, -3), 8, 8)
        
        painter.restore()


class NoWheelSpinBox(QSpinBox):
    """禁用鼠标滚轮的 SpinBox，避免误触"""
    def wheelEvent(self, event):
        event.ignore()


class PetCalendarDialog(QDialog):
    """小猫日历：精致卡片式日历，显示阳历、农历和节日 / 生日信息。"""

    def _apply_calendar_style(self):
        """日历窗口样式，渐变色跟随设置中心主题色。"""
        pal = settings_center_accent_palette(getattr(self.pet, "_settings_center_accent_name", "cyan"))
        accent = self.accent
        focus = self.focus
        accent_soft = pal.get("accent_soft", "rgba(139, 92, 246, 0.22)")

        self.setStyleSheet(f"""
            QDialog#PetCalendarDialog {{
                background-color: #0F172A;
                color: #F8FAFC;
                font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
            }}
            QLabel {{ color: #F8FAFC; background: transparent; }}
            QLabel#CalendarTitle {{
                font-size: 25px;
                font-weight: 900;
                letter-spacing: 0.5px;
            }}
            QLabel#CalendarSubTitle {{
                color: #9CA3AF;
                font-size: 13px;
            }}
            QFrame#TopCard {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {accent}, stop:0.55 {focus}, stop:1 {accent});
                border: 1px solid rgba(255,255,255,0.14);
                border-radius: 24px;
            }}
            QLabel#DateCardMain {{
                color: #FFFFFF;
                font-size: 20px;
                font-weight: 900;
            }}
            QLabel#DateCardSub {{
                color: #E0E7FF;
                font-size: 14px;
                font-weight: 750;
            }}
            QCalendarWidget {{
                background-color: rgba(15, 23, 42, 0.85);
                border: 1px solid rgba(148, 163, 184, 0.25);
                border-radius: 22px;
                padding: 10px;
                selection-background-color: {accent};
                selection-color: #FFFFFF;
            }}
            QCalendarWidget QWidget {{
                background-color: transparent;
                alternate-background-color: rgba(255, 255, 255, 0.05);
                color: #E5E7EB;
            }}
            QCalendarWidget QToolButton {{
                color: #FFFFFF;
                background-color: {accent};
                border: 2px solid {focus};
                border-radius: 12px;
                padding: 8px 12px;
                margin: 2px;
                font-size: 13px;
                font-weight: 900;
            }}
            QCalendarWidget QToolButton:hover {{
                background-color: {focus};
                border-color: #FFFFFF;
            }}
            QCalendarWidget QSpinBox {{
                background-color: rgba(2, 6, 23, 0.6);
                color: #F8FAFC;
                border: 1px solid rgba(148, 163, 184, 0.3);
                border-radius: 10px;
                padding: 5px;
            }}
            QCalendarWidget QMenu {{
                background-color: #1E293B;
                color: #F8FAFC;
                border: 1px solid rgba(148, 163, 184, 0.3);
            }}
            QCalendarWidget QAbstractItemView {{
                background-color: transparent;
                color: #E5E7EB;
                selection-background-color: {accent};
                selection-color: #FFFFFF;
                outline: none;
                border: none;
                gridline-color: rgba(148, 163, 184, 0.1);
                font-size: 14px;
                font-weight: 650;
            }}
            QLabel#InfoCard {{
                background-color: rgba(255, 255, 255, 0.06);
                border: 1px solid rgba(148, 163, 184, 0.2);
                border-radius: 18px;
                padding: 15px 17px;
                color: #E5E7EB;
                font-size: 13px;
                line-height: 1.45;
            }}
            QLabel#SpecialCard {{
                background-color: rgba(251, 191, 36, 0.13);
                border: 1px solid rgba(251, 191, 36, 0.42);
                border-radius: 18px;
                padding: 13px 15px;
                color: #FEF3C7;
                font-size: 13px;
                font-weight: 850;
            }}
            QPushButton {{
                min-height: 40px;
                border-radius: 16px;
                padding: 8px 18px;
                font-weight: 900;
                font-size: 15px;
                color: #FFFFFF;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4B5563, stop:1 #374151);
                border: 2px solid #6B7280;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #6B7280, stop:1 #4B5563);
                border-color: #9CA3AF;
            }}
            QPushButton#PrimaryButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {accent}, stop:1 {focus});
                border-color: {focus};
                border-width: 2px;
                color: #FFFFFF;
            }}
            QPushButton#PrimaryButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {focus}, stop:1 {accent});
                border-color: #FFFFFF;
            }}
        """)
    def __init__(self, pet):
        super().__init__(None)
        self.pet = pet
        self.setObjectName("PetCalendarDialog")
        self.setWindowTitle("小猫日历 · v1.0.0")
        self.resize(520, 600)
        self.setMinimumSize(480, 540)
        self.setWindowFlags(
            Qt.Window
            | Qt.WindowTitleHint
            | Qt.WindowSystemMenuHint
            | Qt.WindowCloseButtonHint
        )
        # 先获取主题色
        pal = settings_center_accent_palette(getattr(self.pet, "_settings_center_accent_name", "cyan"))
        self.accent = pal.get("accent", "#8B5CF6")
        self.focus = pal.get("focus", "#C4B5FD")
        
        self._apply_calendar_style()

        root = QVBoxLayout(self)
        root.setContentsMargins(22, 22, 22, 22)
        root.setSpacing(14)

        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(4)
        title = QLabel("📅 小猫日历")
        title.setObjectName("CalendarTitle")
        subtitle = QLabel("查看阳历、农历、生日与节日祝福日")
        subtitle.setObjectName("CalendarSubTitle")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header.addLayout(title_box)
        header.addStretch(1)
        root.addLayout(header)

        top_card = QFrame()
        top_card.setObjectName("TopCard")
        top_layout = QVBoxLayout(top_card)
        top_layout.setContentsMargins(18, 16, 18, 16)
        top_layout.setSpacing(6)
        self.lbl_date_main = QLabel("")
        self.lbl_date_main.setObjectName("DateCardMain")
        self.lbl_date_sub = QLabel("")
        self.lbl_date_sub.setObjectName("DateCardSub")
        top_layout.addWidget(self.lbl_date_main)
        top_layout.addWidget(self.lbl_date_sub)
        root.addWidget(top_card)

        self.calendar = CustomCalendarWidget(accent=self.accent, focus=self.focus)
        root.addWidget(self.calendar, 1)

        # 时间间隔显示
        self.lbl_interval = QLabel("")
        self.lbl_interval.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(59, 130, 246, 0.3), stop:1 rgba(168, 85, 247, 0.3));
                border: 2px solid rgba(147, 197, 253, 0.5);
                border-radius: 18px;
                padding: 14px 18px;
                color: #E0E7FF;
                font-size: 16px;
                font-weight: 800;
            }
        """)
        self.lbl_interval.setWordWrap(True)
        root.addWidget(self.lbl_interval)

        self.lbl_info = QLabel("")
        self.lbl_info.setObjectName("InfoCard")
        self.lbl_info.setWordWrap(True)
        root.addWidget(self.lbl_info)

        self.lbl_special = QLabel("")
        self.lbl_special.setObjectName("SpecialCard")
        self.lbl_special.setWordWrap(True)
        self.lbl_special.hide()
        root.addWidget(self.lbl_special)

        # 订日历事件部分
        events_label = QLabel("📝 订日历事件")
        events_label.setStyleSheet("font-weight: bold; font-size: 15px; color: #E5E7EB; margin-top: 8px;")
        root.addWidget(events_label)
        
        self.events_list = QListWidget()
        self.events_list.setStyleSheet("""
            QListWidget {
                background-color: rgba(15, 23, 42, 0.7);
                border: 2px solid rgba(55, 65, 81, 0.8);
                border-radius: 16px;
                padding: 8px;
                color: #E5E7EB;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 10px 12px;
                border-radius: 12px;
                margin: 3px 0px;
                background-color: rgba(55, 65, 81, 0.5);
            }
            QListWidget::item:hover {
                background-color: rgba(75, 85, 99, 0.7);
            }
            QListWidget::item:selected {
                background-color: rgba(139, 92, 246, 0.4);
                border: 2px solid rgba(196, 181, 255, 0.7);
            }
        """)
        self.events_list.setMaximumHeight(150)
        self.events_list.setSelectionMode(QListWidget.SingleSelection)
        self.events_list.setSelectionBehavior(QListWidget.SelectItems)
        root.addWidget(self.events_list)

        row = QHBoxLayout()
        btn_today = QPushButton("今天")
        btn_add_event = QPushButton("➕ 订日历")
        btn_add_event.setObjectName("PrimaryButton")
        btn_delete_event = QPushButton("🗑️ 删除")
        btn_settings = QPushButton("祝福设置")
        btn_close = QPushButton("关闭")
        btn_today.clicked.connect(self._go_today)
        btn_add_event.clicked.connect(self._add_event)
        btn_delete_event.clicked.connect(self._delete_event)
        btn_settings.clicked.connect(self.pet.open_birthday_settings)
        btn_close.clicked.connect(self.close)
        row.addWidget(btn_today)
        row.addWidget(btn_add_event)
        row.addWidget(btn_delete_event)
        row.addWidget(btn_settings)
        row.addStretch(1)
        row.addWidget(btn_close)
        root.addLayout(row)

        self.calendar.selectionChanged.connect(self._refresh_info)
        self._refresh_info()

    def _go_today(self):
        self.calendar.setSelectedDate(self.calendar.selectedDate().currentDate())
        self._refresh_info()

    def _refresh_info(self):
        qd = self.calendar.selectedDate()
        d = date(qd.year(), qd.month(), qd.day())
        lunar = solar_to_lunar_info(d)
        lunar_text = format_lunar_info(lunar)

        weekday_names = ["一", "二", "三", "四", "五", "六", "日"]
        weekday = weekday_names[d.weekday()]
        self.lbl_date_main.setText(f"{d:%Y 年 %m 月 %d 日} · 星期{weekday}")
        self.lbl_date_sub.setText(f"农历：{lunar_text}")

        # 计算时间间隔
        today = date.today()
        delta = d - today
        if delta.days == 0:
            interval_text = "📅 就是今天！"
        elif delta.days > 0:
            interval_text = f"📅 还有 {delta.days} 天到达"
        else:
            interval_text = f"📅 已过去 {abs(delta.days)} 天"
        self.lbl_interval.setText(interval_text)

        mode_label = BIRTHDAY_MODE_LABELS.get(getattr(self.pet, "_birthday_mode", "both"), "阳历和农历都提醒")
        birthday_text = getattr(self.pet, "_birthday_solar_date", "") or "未设置"
        birthday_lunar = format_lunar_info(getattr(self.pet, "_birthday_lunar_info", None)) if birthday_text != "未设置" else "未设置"

        self.lbl_info.setText(
            f"生日设置：{birthday_text}\n"
            f"生日农历：{birthday_lunar}\n"
            f"生日提醒方式：{mode_label}\n"
            f"节日祝福：元旦 {'开启' if getattr(self.pet, '_holiday_new_year_enabled', True) else '关闭'} / "
            f"农历新年 {'开启' if getattr(self.pet, '_holiday_lunar_new_year_enabled', True) else '关闭'}"
        )

        notes = []
        birthday_hit = self.pet._birthday_match_for_date(d) if hasattr(self.pet, "_birthday_match_for_date") else ""
        if birthday_hit:
            notes.append(f"🎂 这一天会弹出：生日快乐！")
        holiday_hit = holiday_greeting_match_for_date(
            d,
            getattr(self.pet, "_holiday_new_year_enabled", True),
            getattr(self.pet, "_holiday_lunar_new_year_enabled", True),
        )
        if holiday_hit:
            notes.append(f"🎉 {holiday_hit}会弹出：新年快乐")

        if notes:
            self.lbl_special.setText("\n".join(notes))
            self.lbl_special.show()
        else:
            self.lbl_special.hide()
        
        self._refresh_events_list()

    def _refresh_events_list(self):
        """刷新事件列表，显示当前选中日期的所有事件。"""
        self.events_list.clear()
        qd = self.calendar.selectedDate()
        d = date(qd.year(), qd.month(), qd.day())
        date_str = d.isoformat()
        
        events = getattr(self.pet, "_calendar_events", [])
        found = False
        for event in events:
            if event.get("date") == date_str:
                found = True
                title = event.get("title", "未命名")
                note = event.get("note", "")
                reminder_freq = event.get("reminder_freq", 0)
                reminder_label = "当天只提醒一次" if reminder_freq == 0 else f"每 {reminder_freq} 小时一次"
                
                item_text = f"📌 {title}"
                if note:
                    item_text += f" | {note}"
                item_text += f" | {reminder_label}"
                
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, event.get("id"))
                self.events_list.addItem(item)
        
        if not found:
            empty_item = QListWidgetItem("暂无事件")
            empty_item.setFlags(empty_item.flags() & ~Qt.ItemIsEnabled)
            self.events_list.addItem(empty_item)

    def _add_event(self):
        """添加日历事件对话框。"""
        qd = self.calendar.selectedDate()
        d = date(qd.year(), qd.month(), qd.day())
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"订日历 - {d.isoformat()}")
        dialog.setMinimumSize(400, 300)
        dialog.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel("标题：")
        title_edit = QLineEdit()
        title_edit.setPlaceholderText("请输入事件标题...")
        title_edit.setStyleSheet("""
            QLineEdit {
                min-height: 36px;
                padding: 8px 12px;
                border-radius: 12px;
                background-color: rgba(255, 255, 255, 0.07);
                border: 1px solid rgba(148, 163, 184, 0.16);
                color: #F8FAFC;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #C4B5FD;
                background-color: rgba(255, 255, 255, 0.10);
            }
        """)
        
        # 备注
        note_label = QLabel("备注：")
        note_edit = QTextEdit()
        note_edit.setPlaceholderText("可选，添加备注信息...")
        note_edit.setMaximumHeight(100)
        note_edit.setStyleSheet("""
            QTextEdit {
                padding: 8px 12px;
                border-radius: 12px;
                background-color: rgba(255, 255, 255, 0.07);
                border: 1px solid rgba(148, 163, 184, 0.16);
                color: #F8FAFC;
                font-size: 13px;
            }
            QTextEdit:focus {
                border-color: #C4B5FD;
                background-color: rgba(255, 255, 255, 0.10);
            }
        """)
        
        # 提醒频率
        freq_label = QLabel("提醒频率：")
        freq_combo = QComboBox()
        for mins, label in CALENDAR_EVENT_REMINDER_OPTIONS:
            freq_combo.addItem(label, mins)
        
        # 按钮
        btn_layout = QHBoxLayout()
        btn_ok = QPushButton("添加")
        btn_ok.setObjectName("PrimaryButton")
        btn_cancel = QPushButton("取消")
        
        btn_ok.clicked.connect(dialog.accept)
        btn_cancel.clicked.connect(dialog.reject)
        btn_layout.addStretch(1)
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_ok)
        
        layout.addWidget(title_label)
        layout.addWidget(title_edit)
        layout.addWidget(note_label)
        layout.addWidget(note_edit)
        layout.addWidget(freq_label)
        layout.addWidget(freq_combo)
        layout.addLayout(btn_layout)
        
        dialog.setStyleSheet("""
            QDialog {
                background-color: #0B1020;
                color: #F8FAFC;
                font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
            }
            QLabel {
                color: #F8FAFC;
                font-size: 13px;
                font-weight: 650;
            }
            QPushButton {
                min-height: 36px;
                border-radius: 12px;
                padding: 7px 18px;
                font-weight: 700;
                color: #F8FAFC;
                background-color: rgba(255,255,255,0.08);
                border: 1px solid rgba(148, 163, 184, 0.18);
            }
            QPushButton:hover {
                background-color: rgba(139, 92, 246, 0.22);
                border-color: #C4B5FD;
            }
            QPushButton#PrimaryButton {
                background-color: #8B5CF6;
                border-color: #C4B5FD;
            }
            QComboBox {
                min-height: 36px;
                padding: 6px 12px;
                border-radius: 12px;
                background-color: rgba(255, 255, 255, 0.07);
                border: 1px solid rgba(148, 163, 184, 0.16);
                color: #F8FAFC;
                font-size: 13px;
            }
            QComboBox::drop-down {
                border: none;
                width: 24px;
            }
            QComboBox::down-arrow {
                width: 14px;
                height: 14px;
            }
            QComboBox QAbstractItemView {
                background-color: #0F172A;
                border: 1px solid rgba(148, 163, 184, 0.20);
                border-radius: 10px;
                padding: 4px;
                selection-background-color: rgba(139, 92, 246, 0.22);
                selection-color: #FFFFFF;
            }
        """)
        
        if dialog.exec() == QDialog.Accepted:
            title = title_edit.text().strip()
            if not title:
                self.pet._show_message("请输入事件标题", "warn", 1.5)
                return
            
            event = {
                "id": getattr(self.pet, "_calendar_events_next_id", 1),
                "date": d.isoformat(),
                "title": title,
                "note": note_edit.toPlainText().strip(),
                "reminder_freq": freq_combo.currentData(),
                "last_shown_t": 0.0,
            }
            events = getattr(self.pet, "_calendar_events", [])
            events.append(event)
            self.pet._calendar_events = events
            self.pet._calendar_events_next_id = getattr(self.pet, "_calendar_events_next_id", 1) + 1
            self.pet._save_user_config()
            self._refresh_events_list()
            self.pet._show_message(f"已添加事件：{title}", "ok", 1.5)

    def _delete_event(self):
        """删除选中的日历事件。"""
        current_item = self.events_list.currentItem()
        if not current_item:
            self.pet._show_message("请先选择要删除的事件", "warn", 1.5)
            return
        
        event_id = current_item.data(Qt.UserRole)
        if event_id is None:
            self.pet._show_message("无法删除此项目", "warn", 1.5)
            return
        
        events = getattr(self.pet, "_calendar_events", [])
        new_events = [e for e in events if e.get("id") != event_id]
        
        if len(new_events) < len(events):
            self.pet._calendar_events = new_events
            self.pet._save_user_config()
            self._refresh_events_list()
            self.pet._show_message("已删除事件", "ok", 1.5)


class PetSettingsDialog(QDialog):
    """桌宠可视化设置界面。"""

    def __init__(self, pet):
        # 不使用桌宠小猫作为窗口父级，避免继承小猫的置顶 / Tool 窗口层级。
        # 设置中心是普通窗口：可以被其他窗口遮挡；只有桌宠本体保持强制置顶。
        super().__init__(None)
        self.pet = pet
        self.setWindowTitle("桌宠设置 · v1.0.0")
        self.setModal(False)

        # 设置中心是普通窗口，不置顶；但必须显式保留系统菜单和关闭按钮。
        # 否则在部分 Windows / Qt 样式下，标题栏 X 会显示但不可点击。
        self.setWindowFlags(
            Qt.Window
            | Qt.WindowTitleHint
            | Qt.WindowSystemMenuHint
            | Qt.WindowMinimizeButtonHint
            | Qt.WindowMaximizeButtonHint
            | Qt.WindowCloseButtonHint
        )
        self.setAttribute(Qt.WA_DeleteOnClose, False)

        # 默认 4:3；窗口可自由缩放。内容显示不全时由页面滚动条处理。
        self.resize(960, 720)
        self.setMinimumSize(720, 540)
        self.setSizeGripEnabled(True)

        self._build_ui()
        self.refresh_from_pet()

    def reject(self):
        self.close()

    def closeEvent(self, event):
        # 关闭设置中心只隐藏窗口，不销毁桌宠，也不影响小猫置顶。
        self.hide()
        event.ignore()

    def _apply_settings_style(self):
        """现代设置中心样式：深色商业软件风格。"""
        name = getattr(self.pet, "_settings_center_accent_name", "cyan")
        pal = settings_center_accent_palette(name)
        accent = pal["accent"]
        accent_soft = pal["accent_soft"]
        focus = pal["focus"]

        self.setObjectName("SettingsDialog")
        self.setStyleSheet(f"""
            QDialog#SettingsDialog {{
                background-color: #0B1020;
                color: #F8FAFC;
                font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
            }}
            QLabel {{
                color: #F8FAFC;
                background: transparent;
                font-size: 13px;
            }}
            QLabel#SettingsTitle {{
                font-size: 25px;
                font-weight: 900;
                color: #F8FAFC;
                letter-spacing: 0.6px;
            }}
            QLabel#SettingsDesc {{
                color: #9CA3AF;
                font-size: 13px;
            }}
            QFrame#SettingsShell {{
                background-color: #0F172A;
                border: 1px solid rgba(148, 163, 184, 0.16);
                border-radius: 24px;
            }}
            QFrame#SettingsHeader {{
                background-color: rgba(255, 255, 255, 0.035);
                border: 1px solid rgba(148, 163, 184, 0.12);
                border-radius: 22px;
            }}
            QFrame#SettingsNavFrame {{
                background-color: rgba(15, 23, 42, 0.74);
                border: 1px solid rgba(148, 163, 184, 0.12);
                border-radius: 22px;
            }}
            QFrame#ContentFrame {{
                background-color: rgba(15, 23, 42, 0.72);
                border: 1px solid rgba(148, 163, 184, 0.12);
                border-radius: 22px;
            }}
            QLineEdit#SettingsSearch {{
                min-height: 38px;
                padding: 7px 13px;
                border-radius: 14px;
                background-color: rgba(255, 255, 255, 0.07);
                border: 1px solid rgba(148, 163, 184, 0.16);
                color: #F8FAFC;
                selection-background-color: {accent};
                font-size: 13px;
            }}
            QLineEdit#SettingsSearch:focus {{
                border-color: {focus};
                background-color: rgba(255, 255, 255, 0.10);
            }}
            QListWidget#SettingsNav {{
                background: transparent;
                border: none;
                outline: none;
                padding: 8px;
                color: #CBD5E1;
            }}
            QListWidget#SettingsNav::item {{
                min-height: 40px;
                padding: 11px 14px;
                margin: 3px 0px;
                border-radius: 14px;
                color: #94A3B8;
                font-size: 13px;
                font-weight: 700;
            }}
            QListWidget#SettingsNav::item:hover {{
                background-color: rgba(255, 255, 255, 0.07);
                color: #F8FAFC;
            }}
            QListWidget#SettingsNav::item:selected {{
                background-color: {accent_soft};
                color: #FFFFFF;
                border: 1px solid {focus};
            }}
            QScrollArea {{
                background: transparent;
                border: none;
            }}
            QGroupBox {{
                color: #E5E7EB;
                font-size: 14px;
                font-weight: 900;
                border: 1px solid rgba(148, 163, 184, 0.16);
                border-radius: 18px;
                margin-top: 16px;
                padding: 18px 16px 16px 16px;
                background-color: rgba(255, 255, 255, 0.045);
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 14px;
                padding: 0px 8px;
                color: {focus};
                background-color: #0F172A;
            }}
            QLineEdit, QComboBox, QSpinBox {{
                min-height: 34px;
                border-radius: 12px;
                padding: 6px 11px;
                color: #F8FAFC;
                background-color: rgba(2, 6, 23, 0.50);
                border: 1px solid rgba(148, 163, 184, 0.20);
                selection-background-color: {accent};
                font-size: 13px;
            }}
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus {{
                border-color: {focus};
                background-color: rgba(15, 23, 42, 0.88);
            }}
            QComboBox::drop-down {{
                width: 28px;
                border: none;
            }}
            QComboBox QAbstractItemView {{
                background-color: #111827;
                color: #F8FAFC;
                border: 1px solid rgba(148, 163, 184, 0.20);
                selection-background-color: {accent};
                outline: none;
            }}
            QCheckBox {{
                color: #F8FAFC;
                font-size: 13px;
                spacing: 9px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 6px;
                border: 1px solid rgba(148, 163, 184, 0.34);
                background-color: rgba(2, 6, 23, 0.45);
            }}
            QCheckBox::indicator:checked {{
                background-color: {accent};
                border-color: {focus};
            }}
            QPushButton {{
                min-height: 34px;
                border-radius: 13px;
                padding: 7px 15px;
                font-weight: 800;
                color: #F8FAFC;
                background-color: rgba(255, 255, 255, 0.075);
                border: 1px solid rgba(148, 163, 184, 0.18);
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.115);
                border-color: {focus};
            }}
            QPushButton#PrimaryButton {{
                background-color: {accent};
                border-color: {focus};
                color: #FFFFFF;
            }}
            QPushButton#PrimaryButton:hover {{
                background-color: {focus};
                color: #0F172A;
            }}

            QListWidget#SettingsSearchResults {{
                background-color: rgba(15, 23, 42, 0.96);
                border: 1px solid rgba(148, 163, 184, 0.18);
                border-radius: 18px;
                padding: 8px;
                color: #E5E7EB;
                outline: none;
            }}
            QListWidget#SettingsSearchResults::item {{
                min-height: 34px;
                padding: 8px 12px;
                margin: 2px 0px;
                border-radius: 12px;
                color: #CBD5E1;
                font-size: 13px;
            }}
            QListWidget#SettingsSearchResults::item:hover {{
                background-color: rgba(255,255,255,0.08);
                color: #FFFFFF;
            }}
            QListWidget#SettingsSearchResults::item:selected {{
                background-color: {accent_soft};
                color: #FFFFFF;
                border: 1px solid {focus};
            }}
        """)


    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(14)

        shell = QFrame(self)
        shell.setObjectName("SettingsShell")
        shell_layout = QVBoxLayout(shell)
        shell_layout.setContentsMargins(18, 18, 18, 18)
        shell_layout.setSpacing(14)
        root.addWidget(shell, 1)

        header = QFrame(shell)
        header.setObjectName("SettingsHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(18, 16, 18, 16)
        header_layout.setSpacing(14)

        logo = QLabel("🐱")
        logo.setStyleSheet(
            "min-width:46px; max-width:46px; min-height:46px; max-height:46px;"
            "border-radius:16px; background-color:rgba(255,255,255,0.08); font-size:26px;"
        )
        logo.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(logo)

        title_col = QVBoxLayout()
        title_col.setSpacing(3)
        title = QLabel("薛定谔的小猫 · v1.0.0")
        title.setObjectName("SettingsTitle")
        desc = QLabel("管理桌宠外观、动作、提醒、工具与系统功能。")
        desc.setObjectName("SettingsDesc")
        title_col.addWidget(title)
        title_col.addWidget(desc)
        header_layout.addLayout(title_col, 1)

        self.search_edit = QLineEdit()
        self.search_edit.setObjectName("SettingsSearch")
        self.search_edit.setPlaceholderText("搜索设置：生日 / 主题 / 番茄钟 / 下载 / 网络 / 快捷键...")
        self.search_edit.textChanged.connect(self._search_settings)
        self.search_edit.setMinimumWidth(300)
        header_layout.addWidget(self.search_edit, 0, Qt.AlignVCenter)
        shell_layout.addWidget(header)

        self.search_results = QListWidget(self)
        self.search_results.setObjectName("SettingsSearchResults")
        self.search_results.setMaximumHeight(178)
        self.search_results.setSpacing(4)
        self.search_results.hide()
        self.search_results.itemClicked.connect(self._on_search_result_clicked)
        self.search_results.setSelectionMode(QListWidget.SingleSelection)
        self.search_results.setSelectionBehavior(QListWidget.SelectItems)
        shell_layout.addWidget(self.search_results)

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(14)

        nav_frame = QFrame(shell)
        nav_frame.setObjectName("SettingsNavFrame")
        nav_layout = QVBoxLayout(nav_frame)
        nav_layout.setContentsMargins(8, 8, 8, 8)
        nav_layout.setSpacing(8)

        nav_title = QLabel("设置")
        nav_title.setStyleSheet("color:#94A3B8; font-size:12px; font-weight:900; padding:6px 10px;")
        nav_layout.addWidget(nav_title)

        self.nav = QListWidget()
        self.nav.setObjectName("SettingsNav")
        self.nav.setFixedWidth(174)
        self.nav.setSpacing(5)
        self.nav.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.nav.setIconSize(QSize(18, 18))
        self.nav.setSelectionMode(QListWidget.SingleSelection)
        nav_layout.addWidget(self.nav, 1)
        body.addWidget(nav_frame)

        content_frame = QFrame(shell)
        content_frame.setObjectName("ContentFrame")
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        self.tabs = QStackedWidget(self)
        self._settings_page_items = []
        content_layout.addWidget(self.tabs)
        body.addWidget(content_frame, 1)

        shell_layout.addLayout(body, 1)

        self._build_overview_tab()
        self._build_theme_tab()
        self._build_general_tab()
        self._build_tools_tab()
        self._build_hotkeys_tab()
        self._build_pomodoro_tab()
        self._build_files_network_tab()
        self._build_history_tab()
        self._build_advanced_tab()

        self._rebuild_settings_search_index()
        self.nav.currentRowChanged.connect(self.tabs.setCurrentIndex)
        if self.nav.count() > 0:
            self.nav.setCurrentRow(0)

        btn_row = QDialogButtonBox(self)
        self.btn_apply = btn_row.addButton("保存并应用", QDialogButtonBox.ApplyRole)
        self.btn_close = btn_row.addButton("关闭", QDialogButtonBox.RejectRole)
        self.btn_apply.clicked.connect(self.apply_to_pet)
        self.btn_close.clicked.connect(self.close)
        shell_layout.addWidget(btn_row)

    def _add_settings_page(self, page, title, icon_text="", keywords=""):
        item = QListWidgetItem((icon_text + "  " if icon_text else "") + title)
        item.setToolTip(title)
        item.setData(Qt.UserRole, {
            "title": title,
            "keywords": str(keywords or ""),
            "search_text": (title + " " + str(keywords or "")).lower(),
            "row": self.nav.count(),
        })
        self.nav.addItem(item)
        self._settings_page_items.append(item)

        # 每个页面单独放进滚动区域：
        # - 纵向内容过多时出现上下滚动；
        # - 窗口缩得较窄时出现左右滚动。
        page.setMinimumWidth(680)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setWidget(page)

        self.tabs.addWidget(scroll)

    def _widget_search_text(self, widget):
        """实时搜索索引：扫描页面真实控件文字，不依赖预设关键词。"""
        parts = []

        def add_text(value):
            value = str(value or "").strip()
            if value:
                parts.append(value)

        for child in widget.findChildren(QWidget):
            try:
                if isinstance(child, QLabel):
                    add_text(child.text())
                elif isinstance(child, QGroupBox):
                    add_text(child.title())
                elif isinstance(child, QPushButton):
                    add_text(child.text())
                elif isinstance(child, QCheckBox):
                    add_text(child.text())
                elif isinstance(child, QLineEdit):
                    add_text(child.placeholderText())
                    add_text(child.text())
                elif isinstance(child, QComboBox):
                    add_text(child.currentText())
                    for i in range(child.count()):
                        add_text(child.itemText(i))
                elif isinstance(child, QSpinBox):
                    add_text(child.toolTip())
                elif isinstance(child, QListWidget):
                    for i in range(child.count()):
                        add_text(child.item(i).text())
            except Exception:
                pass

        return " ".join(parts)

    def _rebuild_settings_search_index(self):
        self._settings_search_index = []
        for row in range(self.nav.count()):
            item = self.nav.item(row)
            data = item.data(Qt.UserRole)
            if isinstance(data, dict):
                title = data.get("title", item.text())
                base_keywords = data.get("keywords", "")
            else:
                title = item.text()
                base_keywords = str(data or "")

            page_text = ""
            try:
                scroll = self.tabs.widget(row)
                page = scroll.widget() if hasattr(scroll, "widget") else scroll
                page_text = self._widget_search_text(page)
            except Exception:
                page_text = ""

            clean_title = re.sub(r"^[^\\w\\u4e00-\\u9fff]+\\s*", "", str(title)).strip()
            hay = f"{clean_title} {base_keywords} {page_text}".lower()

            self._settings_search_index.append({
                "row": row,
                "title": clean_title or str(title),
                "display": item.text(),
                "text": hay,
            })

            if isinstance(data, dict):
                data["search_text"] = hay
                data["row"] = row
                item.setData(Qt.UserRole, data)

    def _search_score(self, query, page):
        q = query.lower().strip()
        if not q:
            return 0
        text = page.get("text", "")
        title = page.get("title", "").lower()

        score = 0
        if q in title:
            score += 120
        if q in text:
            score += 50

        tokens = [x for x in re.split(r"\\s+", q) if x]
        for token in tokens:
            if token in title:
                score += 80
            if token in text:
                score += 20

        # 中文短查询按字符做一点模糊匹配，避免必须完全命中词组。
        if len(q) >= 2:
            matched_chars = sum(1 for ch in q if ch.strip() and ch in text)
            score += matched_chars * 3

        # 页面标题不再靠硬编码别名抢结果，只根据实际内容排序。
        return score

    def _search_settings(self, text):
        query = str(text or "").strip()
        if not hasattr(self, "search_results"):
            return

        self.search_results.clear()

        if not query:
            self.search_results.hide()
            return

        self._rebuild_settings_search_index()

        results = []
        for page in self._settings_search_index:
            score = self._search_score(query, page)
            if score > 0:
                results.append((score, page))

        results.sort(key=lambda x: x[0], reverse=True)

        for score, page in results[:8]:
            item = QListWidgetItem(f"{page['display']}    ·    匹配设置")
            item.setToolTip("点击跳转到该设置页面")
            item.setData(Qt.UserRole, int(page["row"]))
            self.search_results.addItem(item)

        if self.search_results.count() > 0:
            self.search_results.show()
            self.search_results.setCurrentRow(0)
        else:
            none_item = QListWidgetItem("未找到相关设置")
            none_item.setFlags(Qt.NoItemFlags)
            self.search_results.addItem(none_item)
            self.search_results.show()

    def _on_search_result_clicked(self, item):
        row = item.data(Qt.UserRole)
        if row is None:
            return
        try:
            row = int(row)
        except Exception:
            return
        if 0 <= row < self.nav.count():
            self.nav.setCurrentRow(row)
            self.search_results.hide()

    def _switch_field(self, switch):
        """把开关放在字段区域右侧，形成“文字说明 → 开关”的现代设置行。"""
        return SwitchField(switch, self)


    def _build_overview_tab(self):
        page = QWidget(self)
        layout = QVBoxLayout(page)
        layout.setSpacing(12)

        group = QGroupBox("状态总览", page)
        form = QFormLayout(group)
        self.overview_labels = {}
        for key, label in [
            ("theme", "当前主题"), ("scale", "小猫尺寸"), ("config", "保存位置"),
            ("downloads", "下载文件夹"), ("network", "网络监控"), ("pomodoro", "番茄钟"),
            ("startup", "开机自启动"), ("apps", "常用软件"), ("hotkeys", "快捷键"),
            ("auto_fun", "自动好玩动作"), ("birthday", "生日提醒"),
        ]:
            val = QLabel("--")
            val.setWordWrap(True)
            self.overview_labels[key] = val
            form.addRow(label, val)

        row = QHBoxLayout()
        btn_refresh = QPushButton("刷新总览")
        btn_refresh.clicked.connect(self.refresh_overview)
        row.addWidget(btn_refresh)
        row.addStretch(1)
        layout.addWidget(group)
        layout.addLayout(row)
        layout.addStretch(1)
        self._add_settings_page(page, "总览", "🏠", "总览 首页 概览 状态总览")

    def refresh_overview(self):
        if not hasattr(self, "overview_labels"):
            return
        pet = self.pet
        theme = THEME_PALETTES.get(pet._theme_name, {}).get("label", pet._theme_name)
        box = BOX_COLOR_PALETTES.get(pet._box_theme_name, {}).get("label", pet._box_theme_name)
        head = CAT_HEAD_PALETTES.get(pet._cat_head_theme_name, {}).get("label", pet._cat_head_theme_name)
        self.overview_labels["theme"].setText(f"{theme} / {box} / {head}")
        self.overview_labels["scale"].setText(f"{pet.SCALE_OPTIONS[pet._scale_idx]} px / 单位")
        self.overview_labels["config"].setText(str(_pet_data_dir()))
        self.overview_labels["downloads"].setText(str(pet._downloads_path))
        self.overview_labels["network"].setText("开启" if pet._network_monitor_enabled else "关闭")
        if pet._pomodoro_enabled:
            phase = "专注" if pet._pomodoro_phase == "work" else "休息" if pet._pomodoro_phase == "break" else "待机"
            self.overview_labels["pomodoro"].setText(f"开启 · {phase}")
        else:
            self.overview_labels["pomodoro"].setText("关闭")
        self.overview_labels["startup"].setText("开启" if is_startup_enabled() else "关闭")
        self.overview_labels["apps"].setText(f"{len(pet._custom_apps)} 个常用软件，{len(pet._quick_tools)} 个快捷工具")
        self.overview_labels["hotkeys"].setText(("开启" if pet._hotkeys_enabled else "关闭") + f" · {len(pet._hotkeys)} 个动作")
        enabled_fun = [AUTO_FUN_ACTION_LABELS.get(name, name) for name, enabled in pet._auto_fun_actions.items() if enabled]
        if pet._auto_expression_enabled and pet._auto_fun_enabled and enabled_fun:
            self.overview_labels["auto_fun"].setText(f"开启 · {pet._auto_fun_chance_percent}% · " + "、".join(enabled_fun))
        elif pet._auto_expression_enabled and pet._auto_fun_enabled:
            self.overview_labels["auto_fun"].setText("开启，但未选择动作")
        else:
            self.overview_labels["auto_fun"].setText("关闭")

        if "birthday" in self.overview_labels:
            if getattr(pet, "_birthday_enabled", False) and getattr(pet, "_birthday_solar_date", ""):
                mode_label = BIRTHDAY_MODE_LABELS.get(getattr(pet, "_birthday_mode", "both"), "阳历和农历都提醒")
                lunar_text = format_lunar_info(getattr(pet, "_birthday_lunar_info", None))
                self.overview_labels["birthday"].setText(f"{pet._birthday_solar_date} / {lunar_text} / {mode_label}")
            else:
                self.overview_labels["birthday"].setText("关闭或未设置")

    def _build_hotkeys_tab(self):
        page = QWidget(self)
        layout = QVBoxLayout(page)
        layout.setSpacing(12)
        group = QGroupBox("桌宠动作快捷键", page)
        form = QFormLayout(group)
        form.setLabelAlignment(Qt.AlignLeft)
        form.setFormAlignment(Qt.AlignTop)
        form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

        self.cb_hotkeys_enabled = ModernSwitch()
        form.addRow("启用快捷键", self._switch_field(self.cb_hotkeys_enabled))
        self.hotkey_edits = {}
        for action, label in HOTKEY_ACTION_LABELS.items():
            edit = QLineEdit()
            edit.setPlaceholderText("例如：Ctrl+Alt+C；留空表示禁用")
            self.hotkey_edits[action] = edit
            form.addRow(label, edit)

        hint = QLabel("说明：默认使用 Ctrl + 1~6。格式支持 Ctrl / Alt / Shift / Win + 字母、数字或 F1-F12。若与其他软件冲突，可在这里自行修改。")
        hint.setWordWrap(True)
        form.addRow("", hint)
        layout.addWidget(group)
        layout.addStretch(1)
        self._add_settings_page(page, "快捷键", "⌨", "快捷键 热键 hotkey ctrl alt 清理 网速 命令面板 隐藏")


    def _make_calendar_field_card(self, title_text, widget, hint_text=""):
        card = QFrame()
        card.setObjectName("BirthdayFieldCard")
        card.setStyleSheet("""
            QFrame#BirthdayFieldCard {
                background-color: rgba(15, 23, 42, 0.70);
                border: 1px solid rgba(148, 163, 184, 0.15);
                border-radius: 16px;
            }
            QLabel#BirthdayFieldTitle {
                color: #DDD6FE;
                font-size: 13px;
                font-weight: 900;
            }
            QLabel#BirthdayFieldHint {
                color: #7C8AA3;
                font-size: 12px;
                line-height: 1.35;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 13, 16, 13)
        card_layout.setSpacing(8)

        title = QLabel(title_text)
        title.setObjectName("BirthdayFieldTitle")
        card_layout.addWidget(title)
        card_layout.addWidget(widget)

        if hint_text:
            hint = QLabel(hint_text)
            hint.setObjectName("BirthdayFieldHint")
            hint.setWordWrap(True)
            card_layout.addWidget(hint)

        return card
    def _apply_greeting_card_style(self):
        """祝福卡片样式，渐变色实时跟随当前设置中心主题色。"""
        if not hasattr(self, "greeting_hero_card"):
            return
        accent_name = None
        if hasattr(self, "combo_settings_accent"):
            accent_name = self.combo_settings_accent.currentData()
        if not accent_name:
            accent_name = getattr(self.pet, "_settings_center_accent_name", "cyan")

        pal = settings_center_accent_palette(accent_name)
        accent = pal.get("accent", "#8B5CF6")
        focus = pal.get("focus", "#C4B5FD")
        accent_soft = pal.get("accent_soft", "rgba(139, 92, 246, 0.22)")

        self.greeting_hero_card.setStyleSheet(f"""
            QFrame#BirthdayHeroCard {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {accent}, stop:0.55 {focus}, stop:1 {accent});
                border: 1px solid rgba(255,255,255,0.16);
                border-radius: 22px;
            }}
            QLabel#PreviewCard {{
                color: #FFFFFF;
                font-size: 14px;
                font-weight: 850;
                line-height: 1.5;
            }}
            QLabel#PreviewBadge {{
                color: #FFFFFF;
                background-color: rgba(255,255,255,0.16);
                border: 1px solid rgba(255,255,255,0.20);
                border-radius: 999px;
                padding: 5px 11px;
                font-size: 12px;
                font-weight: 900;
            }}
            QLabel#LunarResult {{
                color: #EDE9FE;
                font-size: 13px;
                font-weight: 800;
                padding: 9px 11px;
                border-radius: 12px;
                background-color: {accent_soft};
                border: 1px solid {focus};
            }}
        """)
    def _build_calendar_birthday_section(self, parent_layout):
        """在原有“个性化”页面中加入生日 / 节日祝福设置。"""
        section = QGroupBox("生日与节日祝福")
        outer = QVBoxLayout(section)
        outer.setSpacing(14)

        self.greeting_hero_card = QFrame()
        hero_card = self.greeting_hero_card
        hero_card.setObjectName("BirthdayHeroCard")
        self._apply_greeting_card_style()
        hero_layout = QHBoxLayout(hero_card)
        hero_layout.setContentsMargins(18, 16, 18, 16)
        hero_layout.setSpacing(14)

        emoji = QLabel("🎂")
        emoji.setStyleSheet("font-size: 34px; background: transparent;")
        hero_layout.addWidget(emoji, 0, Qt.AlignTop)

        hero_text = QVBoxLayout()
        hero_text.setSpacing(8)
        self.lbl_birthday_preview_card = QLabel("")
        self.lbl_birthday_preview_card.setObjectName("PreviewCard")
        self.lbl_birthday_preview_card.setWordWrap(True)
        self.lbl_birthday_badge = QLabel("提醒未设置")
        self.lbl_birthday_badge.setObjectName("PreviewBadge")
        self.lbl_birthday_badge.setAlignment(Qt.AlignCenter)
        hero_text.addWidget(self.lbl_birthday_preview_card)
        hero_text.addWidget(self.lbl_birthday_badge, 0, Qt.AlignLeft)
        hero_layout.addLayout(hero_text, 1)
        outer.addWidget(hero_card)

        grid = QGridLayout()
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(12)

        self.cb_birthday_enabled = ModernSwitch()
        self.cb_birthday_enabled.toggled.connect(lambda _checked: self._refresh_birthday_preview_card())
        grid.addWidget(self._make_calendar_field_card("生日祝福", self._switch_field(self.cb_birthday_enabled), "生日当天弹出“生日快乐！🎂”。"), 0, 0)

        self.combo_birthday_mode = QComboBox()
        for key, label in BIRTHDAY_MODE_LABELS.items():
            self.combo_birthday_mode.addItem(label, key)
        self.combo_birthday_mode.currentIndexChanged.connect(lambda _idx: self._refresh_birthday_preview_card())
        grid.addWidget(self._make_calendar_field_card("生日匹配方式", self.combo_birthday_mode, "选择只按阳历、只按农历，或两者都提醒。"), 0, 1)

        self.edit_birthday_solar = QLineEdit()
        self.edit_birthday_solar.setPlaceholderText("例如：1998-05-20")
        self.edit_birthday_solar.textChanged.connect(lambda _text: self._refresh_birthday_lunar_preview())
        grid.addWidget(self._make_calendar_field_card("阳历生日", self.edit_birthday_solar, "请输入公历日期，格式为 yyyy-mm-dd。"), 1, 0)

        self.lbl_birthday_lunar = QLabel("农历：未设置")
        self.lbl_birthday_lunar.setObjectName("LunarResult")
        self.lbl_birthday_lunar.setWordWrap(True)
        grid.addWidget(self._make_calendar_field_card("自动匹配农历", self.lbl_birthday_lunar, "农历换算需要 lunardate 依赖。"), 1, 1)

        self.cb_holiday_new_year = ModernSwitch()
        self.cb_holiday_new_year.toggled.connect(lambda _checked: self._refresh_birthday_preview_card())
        grid.addWidget(self._make_calendar_field_card("元旦祝福", self._switch_field(self.cb_holiday_new_year), "每年 1 月 1 日弹出“新年快乐”，并播放烟花效果。"), 2, 0)

        self.cb_holiday_lunar_new_year = ModernSwitch()
        self.cb_holiday_lunar_new_year.toggled.connect(lambda _checked: self._refresh_birthday_preview_card())
        grid.addWidget(self._make_calendar_field_card("农历新年祝福", self._switch_field(self.cb_holiday_lunar_new_year), "农历正月初一弹出“新年快乐”，并播放烟花效果。"), 2, 1)

        self.combo_greeting_frequency = QComboBox()
        for minutes, label in GREETING_FREQUENCY_OPTIONS:
            self.combo_greeting_frequency.addItem(label, minutes)
        self.combo_greeting_frequency.currentIndexChanged.connect(lambda _idx: self._refresh_birthday_preview_card())
        grid.addWidget(self._make_calendar_field_card("当天祝福频率", self.combo_greeting_frequency, "控制生日 / 元旦 / 农历新年在当天的重复祝福频率。"), 3, 0, 1, 2)

        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        outer.addLayout(grid)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_save = QPushButton("保存祝福设置")
        btn_save.setObjectName("PrimaryButton")
        btn_calendar = QPushButton("打开日历")
        btn_test = QPushButton("测试生日祝福")
        btn_new_year = QPushButton("测试新年祝福")
        btn_save.clicked.connect(self._save_birthday_settings)
        btn_calendar.clicked.connect(self.pet.open_calendar_dialog)
        btn_test.clicked.connect(self._test_birthday_effect)
        btn_new_year.clicked.connect(lambda: self.pet._show_new_year_greeting_effect(manual=True))
        btn_row.addWidget(btn_save)
        btn_row.addWidget(btn_calendar)
        btn_row.addWidget(btn_test)
        btn_row.addWidget(btn_new_year)
        btn_row.addStretch(1)
        outer.addLayout(btn_row)

        hint = QLabel("生日祝福和节日祝福每天只会自动弹出一次；修改设置后会重新计算。")
        hint.setWordWrap(True)
        outer.addWidget(hint)

        parent_layout.addWidget(section)

    def _refresh_birthday_lunar_preview(self):
        d = parse_solar_date_text(self.edit_birthday_solar.text())
        if not d:
            self.lbl_birthday_lunar.setText("农历：日期格式不正确，请输入 yyyy-mm-dd")
            return None
        lunar = solar_to_lunar_info(d)
        self.lbl_birthday_lunar.setText(f"农历：{format_lunar_info(lunar)}")
        self._refresh_birthday_preview_card()
        return lunar

    def _refresh_birthday_preview_card(self):
        if not hasattr(self, "lbl_birthday_preview_card"):
            return

        d = parse_solar_date_text(self.edit_birthday_solar.text()) if hasattr(self, "edit_birthday_solar") else None
        enabled = self.cb_birthday_enabled.isChecked() if hasattr(self, "cb_birthday_enabled") else False
        mode = self.combo_birthday_mode.currentData() if hasattr(self, "combo_birthday_mode") else "both"
        mode_label = BIRTHDAY_MODE_LABELS.get(mode, "阳历和农历都提醒")
        ny = self.cb_holiday_new_year.isChecked() if hasattr(self, "cb_holiday_new_year") else getattr(self.pet, "_holiday_new_year_enabled", True)
        lny = self.cb_holiday_lunar_new_year.isChecked() if hasattr(self, "cb_holiday_lunar_new_year") else getattr(self.pet, "_holiday_lunar_new_year_enabled", True)
        freq = self.combo_greeting_frequency.currentData() if hasattr(self, "combo_greeting_frequency") else getattr(self.pet, "_greeting_frequency_minutes", 0)
        freq_label = next((label for minutes, label in GREETING_FREQUENCY_OPTIONS if int(minutes) == int(freq or 0)), "当天只提醒一次")

        lines = []
        if d:
            lunar = solar_to_lunar_info(d)
            lunar_text = format_lunar_info(lunar)
            lines.extend([
                f"生日祝福：{'开启' if enabled else '关闭'}",
                f"阳历生日：{d:%Y-%m-%d}",
                f"农历生日：{lunar_text}",
                f"生日匹配：{mode_label}",
            ])
        else:
            lines.extend([
                "生日祝福：未设置",
                "请输入阳历生日，系统会自动匹配农历。",
            ])

        lines.append(f"元旦祝福：{'开启' if ny else '关闭'}")
        lines.append(f"农历新年祝福：{'开启' if lny else '关闭'}")
        lines.append(f"当天祝福频率：{freq_label}")

        self.lbl_birthday_preview_card.setText("\n".join(lines))

        if hasattr(self, "lbl_birthday_badge"):
            if enabled or ny or lny:
                self.lbl_birthday_badge.setText("个性化祝福已配置")
            else:
                self.lbl_birthday_badge.setText("个性化祝福未开启")
    def _save_birthday_settings(self):
        d = parse_solar_date_text(self.edit_birthday_solar.text())
        if not d:
            QMessageBox.warning(self, "个性化祝福", "请按 yyyy-mm-dd 格式输入阳历生日。")
            return

        lunar = solar_to_lunar_info(d)
        if self.combo_birthday_mode.currentData() in ("lunar", "both") and lunar is None:
            QMessageBox.warning(self, "个性化祝福", "农历换算不可用。请先安装：pip install lunardate")
            return

        self.pet._birthday_enabled = self.cb_birthday_enabled.isChecked()
        self.pet._birthday_mode = str(self.combo_birthday_mode.currentData() or "both")
        self.pet._birthday_solar_date = f"{d:%Y-%m-%d}"
        self.pet._birthday_lunar_info = lunar
        self.pet._birthday_last_shown_key = ""
        self.pet._holiday_new_year_enabled = bool(self.cb_holiday_new_year.isChecked())
        self.pet._holiday_lunar_new_year_enabled = bool(self.cb_holiday_lunar_new_year.isChecked())
        self.pet._greeting_frequency_minutes = int(self.combo_greeting_frequency.currentData() or 0)
        self.pet._holiday_last_shown_key = ""
        self.pet._save_user_config()

        self._refresh_birthday_lunar_preview()
        self._refresh_birthday_preview_card()
        if getattr(self.pet, "_calendar_dialog", None) is not None:
            self.pet._calendar_dialog._refresh_info()
        self.pet._show_message("设置已保存", "ok", 2.0, "default")
        self.refresh_overview()

    def _test_birthday_effect(self):
        self.pet._show_message("生日快乐！🎂", "tip", 5.0, "default")
        if hasattr(self.pet, "_start_birthday_fun_effect"):
            self.pet._start_birthday_fun_effect()


    def _build_general_tab(self):
        page = QWidget(self)
        layout = QVBoxLayout(page)
        layout.setSpacing(12)

        group_basic = QGroupBox("基础行为", page)
        basic_form = QFormLayout(group_basic)
        basic_form.setLabelAlignment(Qt.AlignLeft)
        basic_form.setFormAlignment(Qt.AlignTop)
        basic_form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

        self.cb_gaze = ModernSwitch()
        basic_form.addRow("视线跟随", self._switch_field(self.cb_gaze))

        self.cb_remember_position = ModernSwitch()
        basic_form.addRow("记住位置", self._switch_field(self.cb_remember_position))

        self.cb_remember_dock = ModernSwitch()
        basic_form.addRow("记住收纳", self._switch_field(self.cb_remember_dock))

        self.cb_dnd = ModernSwitch()
        basic_form.addRow("免打扰模式", self._switch_field(self.cb_dnd))

        self.cb_startup = ModernSwitch()
        basic_form.addRow("开机自启动", self._switch_field(self.cb_startup))

        self.cb_status_auto = ModernSwitch()
        basic_form.addRow("状态自动提示", self._switch_field(self.cb_status_auto))

        self.cb_daily_tip = ModernSwitch()
        basic_form.addRow("每日一句", self._switch_field(self.cb_daily_tip))

        self.cb_click_through = ModernSwitch()
        basic_form.addRow("鼠标穿透", self._switch_field(self.cb_click_through))

        self.cb_auto_avoid_edge = ModernSwitch()
        basic_form.addRow("边缘自动避让", self._switch_field(self.cb_auto_avoid_edge))

        hint = QLabel("说明：开关现在可以点击右侧整片区域切换，不必精确点到圆点。鼠标穿透开启后，小猫不会挡住点击；需要操作小猫时，按住 Ctrl 再左键拖动，或 Ctrl+右键打开菜单。菜单打开后可正常移动鼠标选择。")
        hint.setWordWrap(True)
        basic_form.addRow("", hint)

        group_display = QGroupBox("显示与提示", page)
        display_form = QFormLayout(group_display)
        display_form.setLabelAlignment(Qt.AlignLeft)
        display_form.setFormAlignment(Qt.AlignTop)
        display_form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

        self.combo_scale = QComboBox()
        for s in self.pet.SCALE_OPTIONS:
            self.combo_scale.addItem(f"{s} px / 单位", s)
        display_form.addRow("默认尺寸", self.combo_scale)

        self.spin_opacity = NoWheelSpinBox()
        self.spin_opacity.setRange(35, 100)
        self.spin_opacity.setSingleStep(5)
        self.spin_opacity.setSuffix(" %")
        display_form.addRow("桌宠透明度", self.spin_opacity)

        self.cb_hover_full_opacity = ModernSwitch()
        display_form.addRow("悬停高亮", self._switch_field(self.cb_hover_full_opacity))

        self.cb_dnd_dim = ModernSwitch()
        display_form.addRow("免打扰变淡", self._switch_field(self.cb_dnd_dim))

        self.spin_dnd_opacity = NoWheelSpinBox()
        self.spin_dnd_opacity.setRange(25, 100)
        self.spin_dnd_opacity.setSingleStep(5)
        self.spin_dnd_opacity.setSuffix(" %")
        display_form.addRow("免打扰透明度", self.spin_dnd_opacity)

        self.combo_performance = QComboBox()
        self.combo_performance.addItem("流畅模式（约 60 FPS）", "smooth")
        self.combo_performance.addItem("标准模式（约 40 FPS）", "balanced")
        self.combo_performance.addItem("省电模式（约 25 FPS）", "powersave")
        display_form.addRow("性能模式", self.combo_performance)

        self.cb_particles_enabled = ModernSwitch()
        display_form.addRow("粒子效果", self._switch_field(self.cb_particles_enabled))

        self.cb_scheduled_cleanup = ModernSwitch()
        display_form.addRow("定时清理内存", self._switch_field(self.cb_scheduled_cleanup))

        self.spin_scheduled_cleanup_min = NoWheelSpinBox()
        self.spin_scheduled_cleanup_min.setRange(10, 1440)
        self.spin_scheduled_cleanup_min.setSingleStep(10)
        self.spin_scheduled_cleanup_min.setSuffix(" 分钟")
        display_form.addRow("清理间隔", self.spin_scheduled_cleanup_min)

        self.spin_tip_min = NoWheelSpinBox()
        self.spin_tip_min.setRange(10, 240)
        self.spin_tip_min.setSuffix(" 分钟")
        self.spin_tip_max = NoWheelSpinBox()
        self.spin_tip_max.setRange(10, 240)
        self.spin_tip_max.setSuffix(" 分钟")

        row = QHBoxLayout()
        row.addWidget(self.spin_tip_min)
        row.addWidget(QLabel("到"))
        row.addWidget(self.spin_tip_max)
        row.addStretch(1)
        tips_wrap = QWidget()
        tips_wrap.setLayout(row)
        display_form.addRow("每日一句间隔", tips_wrap)

        self.cb_auto_expression = ModernSwitch()
        display_form.addRow("表情随时间变化", self._switch_field(self.cb_auto_expression))

        self.spin_expression_seconds = NoWheelSpinBox()
        self.spin_expression_seconds.setRange(10, 3600)
        self.spin_expression_seconds.setSingleStep(10)
        self.spin_expression_seconds.setSuffix(" 秒")
        display_form.addRow("表情变化间隔", self.spin_expression_seconds)

        self.btn_expression_now = QPushButton("立即切换一次")
        self.btn_expression_now.clicked.connect(self._preview_expression_change)
        display_form.addRow("测试表情变化", self.btn_expression_now)

        self.cb_auto_fun = ModernSwitch()
        self.cb_auto_fun_field = self._switch_field(self.cb_auto_fun)
        display_form.addRow("好玩动作参与变化", self.cb_auto_fun_field)

        self.spin_auto_fun_chance = NoWheelSpinBox()
        self.spin_auto_fun_chance.setRange(0, 100)
        self.spin_auto_fun_chance.setSingleStep(5)
        self.spin_auto_fun_chance.setSuffix(" %")
        display_form.addRow("好玩动作触发概率", self.spin_auto_fun_chance)

        self.auto_fun_action_checks = {}
        self.auto_fun_action_fields = {}
        for action_name, action_label in AUTO_FUN_ACTION_LABELS.items():
            sw = ModernSwitch()
            field = self._switch_field(sw)
            self.auto_fun_action_checks[action_name] = sw
            self.auto_fun_action_fields[action_name] = field
            display_form.addRow(f"允许自动{action_label}", field)

        self.btn_auto_fun_now = QPushButton("立即试一个好玩动作")
        self.btn_auto_fun_now.clicked.connect(self._preview_auto_fun_action)
        display_form.addRow("测试好玩动作", self.btn_auto_fun_now)

        fun_hint = QLabel("说明：开启后，表情随时间变化时会按概率自动执行“好玩”动作；新增动作也会自动出现在这里；自动触发不会弹出提示气泡。")
        fun_hint.setWordWrap(True)
        display_form.addRow("", fun_hint)

        self.cb_auto_expression.toggled.connect(self._sync_expression_controls)
        self.cb_auto_fun.toggled.connect(self._sync_expression_controls)

        self.btn_dock = QPushButton("收纳到最近屏幕边缘")
        self.btn_dock.clicked.connect(self._toggle_dock_state)
        display_form.addRow("边缘收纳", self.btn_dock)

        note = QLabel("这些设置会保存到本机配置文件，下次启动自动恢复。")
        note.setWordWrap(True)
        display_form.addRow("", note)

        layout.addWidget(group_basic)
        layout.addWidget(group_display)
        layout.addStretch(1)

        self._add_settings_page(page, "常规", "⚙", "视线 位置 收纳 免打扰 开机 自启动 状态 每日一句 尺寸 透明度 性能 粒子 表情 好玩 动作 鼠标穿透 边缘避让 定时清理")

    def _sync_expression_controls(self):
        enabled = self.cb_auto_expression.isChecked()
        self.spin_expression_seconds.setEnabled(enabled)
        self.btn_expression_now.setEnabled(enabled)

        if hasattr(self, "cb_auto_fun"):
            self.cb_auto_fun.setEnabled(enabled)
            if hasattr(self, "cb_auto_fun_field"):
                self.cb_auto_fun_field.setEnabled(enabled)

            fun_enabled = bool(enabled and self.cb_auto_fun.isChecked())
            self.spin_auto_fun_chance.setEnabled(fun_enabled)
            self.btn_auto_fun_now.setEnabled(fun_enabled)
            for sw in self.auto_fun_action_checks.values():
                sw.setEnabled(fun_enabled)
            for field in self.auto_fun_action_fields.values():
                field.setEnabled(fun_enabled)

    def _build_tools_tab(self):
        page = QWidget(self)
        layout = QVBoxLayout(page)
        layout.setSpacing(12)

        self.tools_list = QListWidget()
        self.apps_list = QListWidget()
        self.tools_list.setIconSize(QSize(24, 24))
        self.apps_list.setIconSize(QSize(24, 24))
        self.tools_list.setAlternatingRowColors(True)
        self.apps_list.setAlternatingRowColors(True)
        self.tools_list.setIconSize(QSize(24, 24))
        self.apps_list.setIconSize(QSize(24, 24))
        self.tools_list.setAlternatingRowColors(True)
        self.apps_list.setAlternatingRowColors(True)
        for lw in (self.tools_list, self.apps_list):
            lw.setDragDropMode(QListWidget.InternalMove)
            lw.setDefaultDropAction(Qt.MoveAction)
            lw.model().rowsMoved.connect(self._sync_launch_order_from_lists)

        tools_group = self._make_launch_group(
            title="快捷工具",
            list_widget=self.tools_list,
            category="tools",
            explain="可以删除默认工具，也可以添加自己的 exe 或文件夹入口。",
        )
        apps_group = self._make_launch_group(
            title="常用软件",
            list_widget=self.apps_list,
            category="apps",
            explain="可以添加自己的软件；以后可以直接输入路径新增软件。",
        )

        layout.addWidget(tools_group)
        layout.addWidget(apps_group)
        layout.addStretch(1)

        self._add_settings_page(page, "工具软件", "🧰", "快捷工具 常用软件 exe 文件夹 添加 删除 排序 拖拽 插件 管理员 右键 命令面板")

    def _build_pomodoro_tab(self):
        page = QWidget(self)
        layout = QVBoxLayout(page)
        layout.setSpacing(12)

        group = QGroupBox("番茄钟 / 休息提醒", page)
        form = QFormLayout(group)
        form.setLabelAlignment(Qt.AlignLeft)
        form.setFormAlignment(Qt.AlignTop)
        form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

        self.cb_pomodoro = ModernSwitch()
        form.addRow("启用番茄钟", self._switch_field(self.cb_pomodoro))

        self.spin_pomo_work = NoWheelSpinBox()
        self.spin_pomo_work.setRange(1, 180)
        self.spin_pomo_work.setSuffix(" 分钟")
        form.addRow("专注时长", self.spin_pomo_work)

        self.spin_pomo_break = NoWheelSpinBox()
        self.spin_pomo_break.setRange(1, 60)
        self.spin_pomo_break.setSuffix(" 分钟")
        form.addRow("休息时长", self.spin_pomo_break)

        self.lbl_pomodoro_status = QLabel("未开始")
        form.addRow("当前状态", self.lbl_pomodoro_status)

        row = QHBoxLayout()
        self.btn_pomodoro_start = QPushButton("开始 / 重新开始")
        self.btn_pomodoro_stop = QPushButton("停止")
        self.btn_pomodoro_start.clicked.connect(self._start_pomodoro_from_ui)
        self.btn_pomodoro_stop.clicked.connect(self._stop_pomodoro_from_ui)
        row.addWidget(self.btn_pomodoro_start)
        row.addWidget(self.btn_pomodoro_stop)
        row.addStretch(1)
        row_wrap = QWidget()
        row_wrap.setLayout(row)
        form.addRow("操作", row_wrap)

        note = QLabel("到点后小猫会弹出提示，并自动在专注 / 休息之间循环。")
        note.setWordWrap(True)
        form.addRow("", note)

        layout.addWidget(group)
        layout.addStretch(1)
        self._add_settings_page(page, "番茄钟", "⏱", "专注 休息 番茄钟 时间")

    def _build_files_network_tab(self):
        page = QWidget(self)
        layout = QVBoxLayout(page)
        layout.setSpacing(12)

        file_group = QGroupBox("文件整理", page)
        file_layout = QVBoxLayout(file_group)
        file_note = QLabel("整理下载文件夹会把文件移动到下载目录下已有的分类文件夹中；不会自动新建文件夹。")
        file_note.setWordWrap(True)

        path_row = QHBoxLayout()
        self.downloads_path_edit = QLineEdit()
        self.downloads_path_edit.setPlaceholderText(r"例如：C:\Users\YourName\Downloads"")
        btn_browse_downloads = QPushButton("浏览...")
        btn_browse_downloads.clicked.connect(self._browse_downloads_folder)
        btn_open_downloads = QPushButton("打开")
        btn_open_downloads.clicked.connect(self._open_configured_downloads_folder)
        btn_reset_downloads = QPushButton("恢复默认")
        btn_reset_downloads.clicked.connect(self._reset_downloads_folder)
        path_row.addWidget(self.downloads_path_edit, 1)
        path_row.addWidget(btn_browse_downloads)
        path_row.addWidget(btn_open_downloads)
        path_row.addWidget(btn_reset_downloads)

        self.cb_organize_preview = ModernSwitch()
        preview_row = QHBoxLayout()
        preview_row.addWidget(QLabel("整理前预览结果"))
        preview_row.addStretch(1)
        preview_row.addWidget(self.cb_organize_preview)

        self.btn_organize_preview = QPushButton("预览整理结果")
        self.btn_organize_preview.clicked.connect(self._preview_downloads_organize_from_ui)

        self.btn_organize_downloads = QPushButton("整理下载文件夹")
        self.btn_organize_downloads.clicked.connect(self._organize_configured_downloads_folder)
        self.btn_undo_organize = QPushButton("撤销上一次整理")
        self.btn_undo_organize.clicked.connect(lambda: self.pet._undo_last_organize_action())
        file_layout.addWidget(file_note)
        file_layout.addWidget(QLabel("下载文件夹路径"))
        file_layout.addLayout(path_row)
        file_layout.addLayout(preview_row)
        file_layout.addWidget(self.btn_organize_preview)
        file_layout.addWidget(self.btn_organize_downloads)
        file_layout.addWidget(self.btn_undo_organize)

        rules_group = QGroupBox("下载整理规则", page)
        rules_layout = QVBoxLayout(rules_group)
        rules_tip = QLabel("规则格式：后缀 → 已有目标文件夹。多个后缀用空格分隔；多个候选文件夹用 | 分隔。")
        rules_tip.setWordWrap(True)
        self.download_rules_list = QListWidget()
        self.download_rules_list.setMinimumHeight(120)
        self.download_rules_list.setSelectionMode(QListWidget.SingleSelection)
        self.download_rules_list.setSelectionBehavior(QListWidget.SelectItems)

        rules_btn_row = QHBoxLayout()
        btn_rule_add = QPushButton("添加规则")
        btn_rule_edit = QPushButton("编辑规则")
        btn_rule_remove = QPushButton("删除规则")
        btn_rule_reset = QPushButton("恢复默认规则")
        btn_rule_add.clicked.connect(self._add_download_rule)
        btn_rule_edit.clicked.connect(self._edit_download_rule)
        btn_rule_remove.clicked.connect(self._remove_download_rule)
        btn_rule_reset.clicked.connect(self._reset_download_rules)
        for btn in (btn_rule_add, btn_rule_edit, btn_rule_remove, btn_rule_reset):
            rules_btn_row.addWidget(btn)
        rules_btn_row.addStretch(1)

        rules_layout.addWidget(rules_tip)
        rules_layout.addWidget(self.download_rules_list)
        rules_layout.addLayout(rules_btn_row)

        net_group = QGroupBox("网络监控增强", page)
        net_form = QFormLayout(net_group)
        net_form.setLabelAlignment(Qt.AlignLeft)
        net_form.setFormAlignment(Qt.AlignTop)
        net_form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

        self.cb_network_monitor = ModernSwitch()
        net_form.addRow("网络监控", self._switch_field(self.cb_network_monitor))

        self.spin_network_interval = NoWheelSpinBox()
        self.spin_network_interval.setRange(30, 3600)
        self.spin_network_interval.setSingleStep(30)
        self.spin_network_interval.setSuffix(" 秒")
        net_form.addRow("检查间隔", self.spin_network_interval)

        self.lbl_network_status = QLabel("尚未检测")
        net_form.addRow("当前网络", self.lbl_network_status)

        self.btn_network_check = QPushButton("立即检查网络")
        self.btn_network_check.clicked.connect(lambda: self.pet._start_network_check(show_always=True))
        net_form.addRow("手动检测", self.btn_network_check)

        targets_group = QGroupBox("网络检测目标", page)
        targets_layout = QVBoxLayout(targets_group)
        targets_tip = QLabel("会按列表顺序检测，任意一个目标连接成功即认为网络可用。")
        targets_tip.setWordWrap(True)
        self.network_targets_list = QListWidget()
        self.network_targets_list.setMinimumHeight(110)
        self.network_targets_list.setSelectionMode(QListWidget.SingleSelection)
        self.network_targets_list.setSelectionBehavior(QListWidget.SelectItems)

        targets_btn_row = QHBoxLayout()
        btn_target_add = QPushButton("添加目标")
        btn_target_edit = QPushButton("编辑目标")
        btn_target_remove = QPushButton("删除目标")
        btn_target_reset = QPushButton("恢复默认目标")
        btn_target_add.clicked.connect(self._add_network_target)
        btn_target_edit.clicked.connect(self._edit_network_target)
        btn_target_remove.clicked.connect(self._remove_network_target)
        btn_target_reset.clicked.connect(self._reset_network_targets)
        for btn in (btn_target_add, btn_target_edit, btn_target_remove, btn_target_reset):
            targets_btn_row.addWidget(btn)
        targets_btn_row.addStretch(1)

        targets_layout.addWidget(targets_tip)
        targets_layout.addWidget(self.network_targets_list)
        targets_layout.addLayout(targets_btn_row)

        layout.addWidget(file_group)
        layout.addWidget(rules_group)
        layout.addWidget(net_group)
        layout.addWidget(targets_group)
        layout.addStretch(1)
        self._add_settings_page(page, "文件网络", "🌐", "下载 整理 预览 撤销 规则 网络 监控 目标 路径")

    def _populate_network_targets(self):
        if not hasattr(self, "network_targets_list"):
            return
        self.network_targets_list.clear()
        for target in self.pet._network_targets:
            name = str(target.get("name", target.get("host", "")))
            host = str(target.get("host", ""))
            port = int(target.get("port", 53))
            self.network_targets_list.addItem(QListWidgetItem(f"{name}\n{host}:{port}"))

    def _selected_network_target_index(self):
        if not hasattr(self, "network_targets_list"):
            return -1
        row = self.network_targets_list.currentRow()
        if row < 0 or row >= len(self.pet._network_targets):
            return -1
        return row

    def _add_network_target(self):
        dlg = NetworkTargetEditDialog(self, title="添加网络检测目标")
        if dlg.exec() != QDialog.Accepted:
            return
        self.pet._network_targets.append(dlg.target_data())
        self.pet._save_user_config()
        self._populate_network_targets()
        self.pet._show_message("网络检测目标已添加", "ok", 1.6)

    def _edit_network_target(self):
        idx = self._selected_network_target_index()
        if idx < 0:
            QMessageBox.information(self, "请选择目标", "请先选择要编辑的网络检测目标。")
            return
        dlg = NetworkTargetEditDialog(self, target=self.pet._network_targets[idx], title="编辑网络检测目标")
        if dlg.exec() != QDialog.Accepted:
            return
        self.pet._network_targets[idx] = dlg.target_data()
        self.pet._save_user_config()
        self._populate_network_targets()
        self.pet._show_message("网络检测目标已更新", "ok", 1.6)

    def _remove_network_target(self):
        idx = self._selected_network_target_index()
        if idx < 0:
            QMessageBox.information(self, "请选择目标", "请先选择要删除的网络检测目标。")
            return
        ret = QMessageBox.question(
            self,
            "删除网络检测目标",
            "确定要删除这个网络检测目标吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if ret != QMessageBox.Yes:
            return
        del self.pet._network_targets[idx]
        self.pet._save_user_config()
        self._populate_network_targets()
        self.pet._show_message("网络检测目标已删除", "info", 1.5)

    def _reset_network_targets(self):
        ret = QMessageBox.question(
            self,
            "恢复默认目标",
            "确定要恢复默认网络检测目标吗？当前自定义目标会被替换。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if ret != QMessageBox.Yes:
            return
        self.pet._network_targets = _make_default_network_targets()
        self.pet._save_user_config()
        self._populate_network_targets()
        self.pet._show_message("已恢复默认网络检测目标", "info", 1.5)

    def _populate_download_rules(self):
        if not hasattr(self, "download_rules_list"):
            return
        self.download_rules_list.clear()
        for rule in self.pet._download_rules:
            exts = str(rule.get("extensions", ""))
            folders = str(rule.get("folders", ""))
            item = QListWidgetItem(f"{exts}\n→ {folders}")
            item.setData(Qt.UserRole, dict(rule))
            self.download_rules_list.addItem(item)

    def _selected_download_rule_index(self):
        if not hasattr(self, "download_rules_list"):
            return -1
        row = self.download_rules_list.currentRow()
        if row < 0 or row >= len(self.pet._download_rules):
            return -1
        return row

    def _add_download_rule(self):
        dlg = DownloadRuleEditDialog(self, title="添加下载整理规则")
        if dlg.exec() != QDialog.Accepted:
            return
        self.pet._download_rules.append(dlg.rule_data())
        self.pet._save_user_config()
        self._populate_download_rules()
        self.pet._show_message("整理规则已添加", "ok", 1.6)

    def _edit_download_rule(self):
        idx = self._selected_download_rule_index()
        if idx < 0:
            QMessageBox.information(self, "请选择规则", "请先选择要编辑的整理规则。")
            return
        dlg = DownloadRuleEditDialog(self, rule=self.pet._download_rules[idx], title="编辑下载整理规则")
        if dlg.exec() != QDialog.Accepted:
            return
        self.pet._download_rules[idx] = dlg.rule_data()
        self.pet._save_user_config()
        self._populate_download_rules()
        self.pet._show_message("整理规则已更新", "ok", 1.6)

    def _remove_download_rule(self):
        idx = self._selected_download_rule_index()
        if idx < 0:
            QMessageBox.information(self, "请选择规则", "请先选择要删除的整理规则。")
            return
        ret = QMessageBox.question(
            self,
            "删除整理规则",
            "确定要删除这条整理规则吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if ret != QMessageBox.Yes:
            return
        del self.pet._download_rules[idx]
        self.pet._save_user_config()
        self._populate_download_rules()
        self.pet._show_message("整理规则已删除", "info", 1.5)

    def _reset_download_rules(self):
        ret = QMessageBox.question(
            self,
            "恢复默认规则",
            "确定要恢复默认整理规则吗？当前自定义规则会被替换。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if ret != QMessageBox.Yes:
            return
        self.pet._download_rules = _make_default_download_rules()
        self.pet._save_user_config()
        self._populate_download_rules()
        self.pet._show_message("已恢复默认整理规则", "info", 1.5)

    def _browse_downloads_folder(self):
        start = self.downloads_path_edit.text().strip() or str(get_downloads_folder_path())
        path = QFileDialog.getExistingDirectory(self, "选择下载文件夹", start)
        if path:
            self.downloads_path_edit.setText(path)

    def _commit_downloads_path_from_ui(self):
        path_text = self.downloads_path_edit.text().strip().strip('"')
        if not path_text:
            path_text = str(get_downloads_folder_path())
            self.downloads_path_edit.setText(path_text)
        self.pet._downloads_path = path_text
        self.pet._save_user_config()
        return path_text

    def _open_configured_downloads_folder(self):
        self._commit_downloads_path_from_ui()
        ok, msg = open_downloads_folder_tool()
        self.pet._show_message(msg, "ok" if ok else "warn", 2.4)

    def _reset_downloads_folder(self):
        default_path = str(get_downloads_folder_path(None))
        self.downloads_path_edit.setText(default_path)
        self.pet._downloads_path = default_path
        self.pet._save_user_config()
        self.pet._show_message("下载文件夹路径已恢复默认", "info", 1.8)

    def _organize_configured_downloads_folder(self):
        self._commit_downloads_path_from_ui()
        self.pet._organize_preview_enabled = self.cb_organize_preview.isChecked()
        self.pet._organize_downloads_action()

    def _preview_downloads_organize_from_ui(self):
        self._commit_downloads_path_from_ui()
        ok, msg, _moves = preview_downloads_organization(self.pet._downloads_path, self.pet._download_rules)
        QMessageBox.information(self, "预览整理结果" if ok else "预览失败", msg)

    def _build_theme_tab(self):
        page = QWidget(self)
        layout = QVBoxLayout(page)
        layout.setSpacing(12)

        group = QGroupBox("小猫皮肤 / 主题", page)
        form = QFormLayout(group)

        self.combo_theme = QComboBox()
        for key, palette in THEME_PALETTES.items():
            self.combo_theme.addItem(palette.get("label", key), key)
        self.combo_theme.currentIndexChanged.connect(self._preview_theme)
        form.addRow("整体主题", self.combo_theme)

        self.combo_box_theme = QComboBox()
        for key, palette in BOX_COLOR_PALETTES.items():
            self.combo_box_theme.addItem(palette.get("label", key), key)
        self.combo_box_theme.currentIndexChanged.connect(self._preview_theme)
        form.addRow("盒子颜色", self.combo_box_theme)
        
        self.combo_doctoral_discipline = QComboBox()
        for key, palette in DOCTORAL_DISCIPLINES.items():
            self.combo_doctoral_discipline.addItem(palette.get("label", key), key)
        self.combo_doctoral_discipline.currentIndexChanged.connect(self._preview_theme)
        form.addRow("博士学科（仅博士红主题）", self.combo_doctoral_discipline)

        self.combo_cat_head_theme = QComboBox()
        for key, palette in CAT_HEAD_PALETTES.items():
            self.combo_cat_head_theme.addItem(palette.get("label", key), key)
        self.combo_cat_head_theme.currentIndexChanged.connect(self._preview_theme)
        form.addRow("猫头颜色", self.combo_cat_head_theme)

        self.cb_academic_cat = ModernSwitch()
        self.cb_academic_cat.setChecked(bool(getattr(self.pet, "_academic_cat_enabled", False)))
        self.cb_academic_cat.toggled.connect(lambda checked: self.pet.set_academic_cat_enabled(checked))
        form.addRow("学术猫主题（博士帽）", self._switch_field(self.cb_academic_cat))

        self.combo_settings_accent = QComboBox()
        for key, palette in SETTING_CENTER_ACCENTS.items():
            self.combo_settings_accent.addItem(palette.get("label", key), key)
        self.combo_settings_accent.currentIndexChanged.connect(self._preview_settings_accent)
        form.addRow("设置中心主题色", self.combo_settings_accent)

        self.btn_theme_preview = QPushButton("预览主题")
        self.btn_theme_preview.clicked.connect(self._preview_theme)
        form.addRow("预览", self.btn_theme_preview)

        preset_row = QHBoxLayout()
        btn_export_preset = QPushButton("导出主题预设")
        btn_import_preset = QPushButton("导入主题预设")
        btn_export_preset.clicked.connect(self._export_theme_preset)
        btn_import_preset.clicked.connect(self._import_theme_preset)
        preset_row.addWidget(btn_export_preset)
        preset_row.addWidget(btn_import_preset)
        preset_row.addStretch(1)
        preset_wrap = QWidget()
        preset_wrap.setLayout(preset_row)
        form.addRow("主题预设", preset_wrap)

        note = QLabel("整体主题会改变量子窗口、辐射标志等氛围色；盒子、猫头和设置中心主题色都可以独立选择。猫头默认是“英短灰”。应用后会保存到配置文件。")
        note.setWordWrap(True)
        form.addRow("", note)

        layout.addWidget(group)
        self._build_calendar_birthday_section(layout)
        layout.addStretch(1)
        self._add_settings_page(page, "个性化", "🎨", "主题 皮肤 颜色 猫头 盒子 设置中心 预设 导入 导出 个性化 祝福 日历 生日 农历 阳历 元旦 新年 春节 birthday calendar")

    def _current_theme_preset_data(self):
        return {
            "theme_name": self.combo_theme.currentData(),
            "box_theme_name": self.combo_box_theme.currentData(),
            "cat_head_theme_name": self.combo_cat_head_theme.currentData(),
            "settings_center_accent_name": self.combo_settings_accent.currentData(),
            "doctoral_discipline": self.combo_doctoral_discipline.currentData(),
        }

    def _export_theme_preset(self):
        path, _ = QFileDialog.getSaveFileName(self, "导出主题预设", "schrodinger_pet_theme.json", "JSON files (*.json);;All files (*.*)")
        if not path:
            return
        try:
            Path(path).write_text(json.dumps(self._current_theme_preset_data(), ensure_ascii=False, indent=2), encoding="utf-8")
            self.pet._show_message("主题预设已导出", "ok", 1.6)
        except Exception as exc:
            QMessageBox.warning(self, "导出失败", str(exc) or exc.__class__.__name__)

    def _import_theme_preset(self):
        path, _ = QFileDialog.getOpenFileName(self, "导入主题预设", "", "JSON files (*.json);;All files (*.*)")
        if not path:
            return
        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError("主题预设格式不正确")
            for combo, key in [
                (self.combo_theme, "theme_name"),
                (self.combo_box_theme, "box_theme_name"),
                (self.combo_cat_head_theme, "cat_head_theme_name"),
                (self.combo_settings_accent, "settings_center_accent_name"),
                (self.combo_doctoral_discipline, "doctoral_discipline"),
            ]:
                idx = combo.findData(str(data.get(key, "")))
                if idx >= 0:
                    combo.setCurrentIndex(idx)
            self._preview_theme()
            self.pet._show_message("主题预设已导入", "ok", 1.6)
        except Exception as exc:
            QMessageBox.warning(self, "导入失败", str(exc) or exc.__class__.__name__)

    def _build_history_tab(self):
        page = QWidget(self)
        layout = QVBoxLayout(page)
        layout.setSpacing(12)

        group = QGroupBox("通知与操作历史", page)
        group_layout = QVBoxLayout(group)

        note = QLabel("这里记录最近的提示、状态检测、网络检测、整理结果等信息，方便回看刚刚发生了什么。")
        note.setWordWrap(True)
        self.history_list = QListWidget()
        self.history_list.setMinimumHeight(220)
        self.history_list.setSelectionMode(QListWidget.SingleSelection)
        self.history_list.setSelectionBehavior(QListWidget.SelectItems)

        row = QHBoxLayout()
        btn_refresh = QPushButton("刷新")
        btn_copy = QPushButton("复制选中")
        btn_delete = QPushButton("删除选中")
        btn_clear = QPushButton("清空历史")
        btn_refresh.clicked.connect(self.refresh_history_list)
        btn_copy.clicked.connect(self._copy_selected_history)
        btn_delete.clicked.connect(self._delete_selected_history)
        btn_clear.clicked.connect(self._clear_history)
        row.addWidget(btn_refresh)
        row.addWidget(btn_copy)
        row.addWidget(btn_delete)
        row.addWidget(btn_clear)
        row.addStretch(1)

        group_layout.addWidget(note)
        group_layout.addWidget(self.history_list, 1)
        group_layout.addLayout(row)

        layout.addWidget(group)
        layout.addStretch(1)
        self._add_settings_page(page, "通知历史", "📝", "历史 通知 复制 删除 清空")

    def refresh_history_list(self):
        if not hasattr(self, "history_list"):
            return
        self.history_list.clear()
        history = self.pet._message_history[-120:]
        for original_index, item in reversed(list(enumerate(history))):
            ts = item.get("time", "")
            kind = item.get("kind", "info")
            text = item.get("text", "")
            row = QListWidgetItem(f"[{ts}] [{kind}] {text}")
            row.setData(Qt.UserRole, original_index)
            self.history_list.addItem(row)

    def _copy_selected_history(self):
        item = self.history_list.currentItem() if hasattr(self, "history_list") else None
        if item is None:
            QMessageBox.information(self, "请选择记录", "请先选择要复制的历史记录。")
            return
        QApplication.clipboard().setText(item.text())
        self.pet._show_message("已复制历史记录", "ok", 1.4)

    def _delete_selected_history(self):
        item = self.history_list.currentItem() if hasattr(self, "history_list") else None
        if item is None:
            QMessageBox.information(self, "请选择记录", "请先选择要删除的历史记录。")
            return
        idx = item.data(Qt.UserRole)
        try:
            del self.pet._message_history[int(idx)]
        except Exception:
            return
        self.pet._save_user_config()
        self.refresh_history_list()
        self.pet._show_message("已删除选中历史", "info", 1.4)

    def _clear_history(self):
        self.pet._message_history.clear()
        self.pet._save_user_config()
        self.refresh_history_list()
        self.pet._show_message("通知历史已清空", "info", 1.6)


    def _build_advanced_tab(self):
        page = QWidget(self)
        layout = QVBoxLayout(page)
        layout.setSpacing(12)

        group = QGroupBox("配置文件", page)
        form = QFormLayout(group)

        self.lbl_data_dir = QLabel(str(_pet_data_dir()))
        self.lbl_data_dir.setWordWrap(True)
        form.addRow("保存位置", self.lbl_data_dir)

        self.lbl_config_path = QLabel(str(_pet_config_path()))
        self.lbl_config_path.setWordWrap(True)
        form.addRow("当前配置", self.lbl_config_path)

        self.lbl_archive_path = QLabel(str(_pet_archive_dir()))
        self.lbl_archive_path.setWordWrap(True)
        form.addRow("存档目录", self.lbl_archive_path)

        location_row = QHBoxLayout()
        self.data_dir_edit = QLineEdit()
        self.data_dir_edit.setPlaceholderText("选择配置、存档等文件的保存文件夹")
        btn_browse_data = QPushButton("浏览...")
        btn_migrate_data = QPushButton("迁移到此位置")
        btn_default_data = QPushButton("恢复默认位置")
        btn_browse_data.clicked.connect(self._browse_data_dir)
        btn_migrate_data.clicked.connect(self._migrate_data_dir_from_ui)
        btn_default_data.clicked.connect(self._restore_default_data_dir)
        location_row.addWidget(self.data_dir_edit, 1)
        location_row.addWidget(btn_browse_data)
        location_row.addWidget(btn_migrate_data)
        location_row.addWidget(btn_default_data)
        location_wrap = QWidget()
        location_wrap.setLayout(location_row)
        form.addRow("修改保存位置", location_wrap)

        btn_row = QHBoxLayout()
        btn_export = QPushButton("导出配置")
        btn_import = QPushButton("导入配置")
        btn_open_dir = QPushButton("打开配置位置")
        btn_open_log = QPushButton("打开日志位置")

        btn_export.clicked.connect(self._export_config)
        btn_import.clicked.connect(self._import_config)
        btn_open_dir.clicked.connect(self._open_config_folder)
        btn_open_log.clicked.connect(self._open_log_folder)

        for btn in (btn_export, btn_import, btn_open_dir, btn_open_log):
            btn_row.addWidget(btn)
        btn_row.addStretch(1)

        wrap = QWidget()
        wrap.setLayout(btn_row)
        form.addRow("文件操作", wrap)

        archive_group = QGroupBox("设置存档", page)
        archive_layout = QVBoxLayout(archive_group)

        archive_note = QLabel("存档会把当前设置保存到本机存档目录，之后可以一键恢复。适合在大改主题、路径、工具列表前先备份。")
        archive_note.setWordWrap(True)
        archive_layout.addWidget(archive_note)

        archive_row = QHBoxLayout()
        btn_save_archive = QPushButton("存档当前设置")
        btn_restore_archive = QPushButton("恢复存档设置")
        btn_open_archive = QPushButton("打开存档位置")

        btn_save_archive.clicked.connect(self._save_settings_archive)
        btn_restore_archive.clicked.connect(self._restore_settings_archive)
        btn_open_archive.clicked.connect(self._open_archive_folder)

        for btn in (btn_save_archive, btn_restore_archive, btn_open_archive):
            archive_row.addWidget(btn)
        archive_row.addStretch(1)
        archive_layout.addLayout(archive_row)

        reset_group = QGroupBox("恢复初始设置", page)
        reset_layout = QVBoxLayout(reset_group)

        reset_note = QLabel("一键恢复会立即把桌宠恢复到初始默认设置，包括主题、工具、网络目标、番茄钟、尺寸、透明度和下载整理规则。当前配置会被覆盖。")
        reset_note.setWordWrap(True)
        reset_layout.addWidget(reset_note)

        reset_row = QHBoxLayout()
        btn_reset_now = QPushButton("一键恢复初始设置")
        btn_reset_now.clicked.connect(self._restore_initial_settings_now)
        reset_row.addWidget(btn_reset_now)
        reset_row.addStretch(1)
        reset_layout.addLayout(reset_row)

        note = QLabel("配置包含常用软件、快捷工具、下载整理规则、主题、提示频率、番茄钟和设置中心主题色等。功能太多时，可以用右键里的“命令面板”快速搜索执行。")
        note.setWordWrap(True)

        layout.addWidget(group)
        layout.addWidget(archive_group)
        layout.addWidget(reset_group)
        layout.addWidget(note)
        layout.addStretch(1)
        self._add_settings_page(page, "高级", "🛠", "配置 保存位置 存档 恢复 初始 日志 崩溃 导入 导出")

    def _refresh_storage_labels(self):
        if hasattr(self, "lbl_data_dir"):
            self.lbl_data_dir.setText(str(_pet_data_dir()))
        if hasattr(self, "lbl_config_path"):
            self.lbl_config_path.setText(str(_pet_config_path()))
        if hasattr(self, "lbl_archive_path"):
            self.lbl_archive_path.setText(str(_pet_archive_dir()))
        if hasattr(self, "data_dir_edit"):
            self.data_dir_edit.setText(str(_pet_data_dir()))

    def _browse_data_dir(self):
        start = self.data_dir_edit.text().strip() if hasattr(self, "data_dir_edit") else str(_pet_data_dir())
        if not start:
            start = str(_pet_data_dir())
        path = QFileDialog.getExistingDirectory(self, "选择保存位置", start)
        if path:
            self.data_dir_edit.setText(path)

    def _migrate_data_dir_from_ui(self):
        if not hasattr(self, "data_dir_edit"):
            return
        new_dir = self.data_dir_edit.text().strip().strip('"')
        if not new_dir:
            QMessageBox.warning(self, "保存位置不能为空", "请选择或输入新的保存文件夹。")
            return

        ret = QMessageBox.question(
            self,
            "迁移保存位置",
            "确定要把当前配置、存档等文件迁移到新的保存位置吗？\n\n"
            f"当前：{_pet_data_dir()}\n\n"
            f"新位置：{new_dir}\n\n"
            "迁移完成后，后续配置和存档都会保存到新位置。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if ret != QMessageBox.Yes:
            return

        try:
            # 先把设置界面里的改动保存到当前目录，再复制迁移，避免丢失未应用的修改。
            self.apply_to_pet()
            ok, msg, target = migrate_pet_data_dir(new_dir)
            if not ok:
                QMessageBox.warning(self, "迁移失败", msg)
                return

            self.pet.reload_config_from_disk(reset_first=True)
            self._refresh_storage_labels()
            self.refresh_from_pet()
            self.pet._show_message("保存位置已迁移", "ok", 2.2)
            QMessageBox.information(self, "迁移完成", msg)
        except Exception as exc:
            QMessageBox.warning(self, "迁移失败", str(exc) or exc.__class__.__name__)

    def _restore_default_data_dir(self):
        default_dir = _default_pet_data_dir()
        self.data_dir_edit.setText(str(default_dir))
        self._migrate_data_dir_from_ui()

    def _export_config(self):
        self.apply_to_pet()
        default_name = "schrodinger_pet_config.json"
        path, _ = QFileDialog.getSaveFileName(self, "导出配置", default_name, "JSON files (*.json);;All files (*.*)")
        if not path:
            return
        try:
            cfg_path = _pet_config_path()
            if cfg_path.exists():
                data = cfg_path.read_text(encoding="utf-8")
            else:
                data = json.dumps(load_pet_config(), ensure_ascii=False, indent=2)
            Path(path).write_text(data, encoding="utf-8")
            self.pet._show_message("配置已导出", "ok", 1.8)
        except Exception as exc:
            QMessageBox.warning(self, "导出失败", str(exc) or exc.__class__.__name__)

    def _import_config(self):
        path, _ = QFileDialog.getOpenFileName(self, "导入配置", "", "JSON files (*.json);;All files (*.*)")
        if not path:
            return
        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError("配置文件格式不正确")
            ok = save_pet_config(data)
            if not ok:
                raise RuntimeError("写入配置文件失败")
            self.pet.reload_config_from_disk(reset_first=True)
            self.pet._show_message("配置已导入", "ok", 1.8)
            self.refresh_from_pet()
        except Exception as exc:
            QMessageBox.warning(self, "导入失败", str(exc) or exc.__class__.__name__)

    def _open_config_folder(self):
        folder = _pet_config_path().parent
        try:
            folder.mkdir(parents=True, exist_ok=True)
            if sys.platform.startswith("win"):
                os.startfile(str(folder))
            elif sys.platform == "darwin":
                _popen_detached(["open", str(folder)])
            else:
                _popen_detached(["xdg-open", str(folder)])
        except Exception as exc:
            QMessageBox.warning(self, "打开失败", str(exc) or exc.__class__.__name__)

    def _open_log_folder(self):
        folder = _pet_log_dir()
        try:
            folder.mkdir(parents=True, exist_ok=True)
            if sys.platform.startswith("win"):
                os.startfile(str(folder))
            elif sys.platform == "darwin":
                _popen_detached(["open", str(folder)])
            else:
                _popen_detached(["xdg-open", str(folder)])
        except Exception as exc:
            QMessageBox.warning(self, "打开失败", str(exc) or exc.__class__.__name__)

    def _open_archive_folder(self):
        folder = _pet_archive_dir()
        try:
            folder.mkdir(parents=True, exist_ok=True)
            if sys.platform.startswith("win"):
                os.startfile(str(folder))
            elif sys.platform == "darwin":
                _popen_detached(["open", str(folder)])
            else:
                _popen_detached(["xdg-open", str(folder)])
        except Exception as exc:
            QMessageBox.warning(self, "打开失败", str(exc) or exc.__class__.__name__)

    def _save_settings_archive(self):
        try:
            # 先应用当前界面里的未保存改动，再存档。
            self.apply_to_pet()

            archive_dir = _pet_archive_dir()
            archive_dir.mkdir(parents=True, exist_ok=True)
            archive_path = archive_dir / _settings_archive_name()

            cfg_path = _pet_config_path()
            if cfg_path.exists():
                data = cfg_path.read_text(encoding="utf-8")
            else:
                data = json.dumps(load_pet_config(), ensure_ascii=False, indent=2)

            archive_path.write_text(data, encoding="utf-8")
            self.pet._show_message("设置已存档", "ok", 1.8)
            QMessageBox.information(self, "存档完成", f"设置已存档到：\n\n{archive_path}")
        except Exception as exc:
            QMessageBox.warning(self, "存档失败", str(exc) or exc.__class__.__name__)

    def _restore_settings_archive(self):
        archive_dir = _pet_archive_dir()
        archive_dir.mkdir(parents=True, exist_ok=True)

        path, _ = QFileDialog.getOpenFileName(
            self,
            "恢复存档设置",
            str(archive_dir),
            "JSON files (*.json);;All files (*.*)",
        )
        if not path:
            return

        ret = QMessageBox.question(
            self,
            "恢复存档设置",
            "确定要用所选存档覆盖当前设置吗？\n\n建议先点击“存档当前设置”备份现在的配置。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if ret != QMessageBox.Yes:
            return

        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError("存档文件格式不正确")
            ok = save_pet_config(data)
            if not ok:
                raise RuntimeError("写入配置文件失败")

            self.pet.reload_config_from_disk(reset_first=True)
            self.pet._show_message("已恢复存档设置", "ok", 2.0)
            self.refresh_from_pet()
        except Exception as exc:
            QMessageBox.warning(self, "恢复失败", str(exc) or exc.__class__.__name__)

    def _restore_initial_settings_now(self):
        ret = QMessageBox.question(
            self,
            "一键恢复初始设置",
            "确定要恢复到初始默认设置吗？\n\n当前配置会被覆盖。建议先点击“存档当前设置”备份。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if ret != QMessageBox.Yes:
            return

        try:
            self.pet.restore_initial_settings()
            self.pet._show_message("已恢复初始设置", "ok", 2.0)
            self.refresh_from_pet()
        except Exception as exc:
            QMessageBox.warning(self, "恢复失败", str(exc) or exc.__class__.__name__)

    def _reset_config_file(self):
        # 保留旧函数名，兼容旧连接；现在直接执行即时恢复，不再要求重启。
        self._restore_initial_settings_now()


    def _make_launch_group(self, title, list_widget, category, explain):
        group = QGroupBox(title)
        outer = QVBoxLayout(group)

        label = QLabel(explain)
        label.setWordWrap(True)
        outer.addWidget(label)

        list_widget.setMinimumHeight(120)
        outer.addWidget(list_widget, 1)

        row = QHBoxLayout()
        btn_open = QPushButton("打开")
        btn_add = QPushButton("添加")
        btn_edit = QPushButton("编辑")
        btn_remove = QPushButton("删除")
        btn_up = QPushButton("上移")
        btn_down = QPushButton("下移")
        btn_reset = QPushButton("恢复默认")

        btn_open.clicked.connect(lambda: self._launch_selected(category))
        btn_add.clicked.connect(lambda: self._add_launch_item(category))
        btn_edit.clicked.connect(lambda: self._edit_launch_item(category))
        btn_remove.clicked.connect(lambda: self._remove_launch_item(category))
        btn_up.clicked.connect(lambda: self._move_launch_item(category, -1))
        btn_down.clicked.connect(lambda: self._move_launch_item(category, 1))
        btn_reset.clicked.connect(lambda: self._reset_launch_items(category))

        for btn in (btn_open, btn_add, btn_edit, btn_remove, btn_up, btn_down, btn_reset):
            row.addWidget(btn)
        row.addStretch(1)
        outer.addLayout(row)

        return group

    def _sync_launch_order_from_lists(self, *args):
        if not hasattr(self, "tools_list") or not hasattr(self, "apps_list"):
            return
        try:
            self.pet._quick_tools = [
                dict(self.tools_list.item(i).data(Qt.UserRole))
                for i in range(self.tools_list.count())
                if self.tools_list.item(i).data(Qt.UserRole)
            ]
            self.pet._custom_apps = [
                dict(self.apps_list.item(i).data(Qt.UserRole))
                for i in range(self.apps_list.count())
                if self.apps_list.item(i).data(Qt.UserRole)
            ]
            self.pet._save_user_config()
            if self.pet._command_palette is not None and self.pet._command_palette.isVisible():
                self.pet._command_palette.refresh_commands()
        except Exception:
            log_exception("sync launch order failed")

    def _move_launch_item(self, category, delta):
        items = self._items_for_category(category)
        list_widget = self._list_for_category(category)
        row = list_widget.currentRow()
        if row < 0:
            return
        new_row = max(0, min(len(items) - 1, row + int(delta)))
        if new_row == row:
            return
        items[row], items[new_row] = items[new_row], items[row]
        self.pet._save_user_config()
        self.refresh_launch_lists()
        list_widget.setCurrentRow(new_row)

    def _items_for_category(self, category):
        return self.pet._quick_tools if category == "tools" else self.pet._custom_apps

    def _list_for_category(self, category):
        return self.tools_list if category == "tools" else self.apps_list

    def _populate_launch_list(self, list_widget, items):
        list_widget.clear()
        for item in items:
            name = str(item.get("name", "未命名"))
            if item.get("type") == "builtin":
                detail = "内置工具"
            else:
                detail = str(item.get("path", ""))
            category = str(item.get("category", "默认"))
            flags = []
            if not item.get("show_in_menu", True):
                flags.append("隐藏右键")
            if not item.get("show_in_palette", True):
                flags.append("隐藏命令")
            if item.get("run_as_admin", False):
                flags.append("管理员")
            suffix = (" · " + " / ".join(flags)) if flags else ""
            row = QListWidgetItem(f"{name}  [{category}]{suffix}\n{detail}")
            icon = launch_item_icon(item)
            if not icon.isNull():
                row.setIcon(icon)
            row.setData(Qt.UserRole, dict(item))
            list_widget.addItem(row)

    def _selected_index(self, category):
        list_widget = self._list_for_category(category)
        row = list_widget.currentRow()
        if row < 0 or row >= len(self._items_for_category(category)):
            return -1
        return row

    def _selected_item(self, category):
        idx = self._selected_index(category)
        if idx < 0:
            return None
        return self._items_for_category(category)[idx]

    def _add_launch_item(self, category):
        dlg = LaunchItemEditDialog(self, title="添加启动项")
        if dlg.exec() != QDialog.Accepted:
            return
        self._items_for_category(category).append(dlg.item_data())
        self.pet._save_user_config()
        self.refresh_launch_lists()
        self.pet._show_message("启动项已添加", "ok", 1.6)

    def _edit_launch_item(self, category):
        idx = self._selected_index(category)
        if idx < 0:
            QMessageBox.information(self, "请选择项目", "请先选择要编辑的项目。")
            return

        items = self._items_for_category(category)
        item = items[idx]
        if item.get("type") == "builtin":
            QMessageBox.information(self, "内置工具", "内置工具不能编辑路径；可以删除它，或用“添加”创建新的路径入口。")
            return

        dlg = LaunchItemEditDialog(self, item=item, title="编辑启动项")
        if dlg.exec() != QDialog.Accepted:
            return
        items[idx] = dlg.item_data()
        self.pet._save_user_config()
        self.refresh_launch_lists()
        self.pet._show_message("启动项已更新", "ok", 1.6)

    def _remove_launch_item(self, category):
        idx = self._selected_index(category)
        if idx < 0:
            QMessageBox.information(self, "请选择项目", "请先选择要删除的项目。")
            return

        item = self._items_for_category(category)[idx]
        name = str(item.get("name", "该项目"))
        ret = QMessageBox.question(
            self,
            "删除启动项",
            f"确定要删除“{name}”吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if ret != QMessageBox.Yes:
            return

        del self._items_for_category(category)[idx]
        self.pet._save_user_config()
        self.refresh_launch_lists()
        self.pet._show_message("启动项已删除", "info", 1.5)

    def _reset_launch_items(self, category):
        ret = QMessageBox.question(
            self,
            "恢复默认",
            "确定要恢复这一组的默认启动项吗？当前自定义项目会被替换。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if ret != QMessageBox.Yes:
            return

        if category == "tools":
            self.pet._quick_tools = _make_default_quick_tools()
        else:
            self.pet._custom_apps = _make_default_custom_apps()

        self.pet._save_user_config()
        self.refresh_launch_lists()
        self.pet._show_message("已恢复默认启动项", "info", 1.5)

    def _launch_selected(self, category):
        item = self._selected_item(category)
        if item is None:
            QMessageBox.information(self, "请选择项目", "请先选择要打开的项目。")
            return
        self.pet._open_launch_item(item)

    def refresh_launch_lists(self):
        self._populate_launch_list(self.tools_list, self.pet._quick_tools)
        self._populate_launch_list(self.apps_list, self.pet._custom_apps)

    def _auto_fun_actions_from_ui(self):
        if not hasattr(self, "auto_fun_action_checks"):
            return _normalize_auto_fun_actions(None)
        return {
            action_name: bool(sw.isChecked())
            for action_name, sw in self.auto_fun_action_checks.items()
        }

    def _preview_expression_change(self):
        pet = self.pet
        pet._auto_expression_enabled = self.cb_auto_expression.isChecked()
        pet._expression_change_seconds = max(10, int(self.spin_expression_seconds.value()))
        pet._auto_fun_enabled = self.cb_auto_fun.isChecked()
        pet._auto_fun_chance_percent = max(0, min(100, int(self.spin_auto_fun_chance.value())))
        pet._auto_fun_actions = _normalize_auto_fun_actions(self._auto_fun_actions_from_ui())
        pet._advance_auto_expression_once()
        pet._save_user_config()
        self.refresh_from_pet()

    def _preview_auto_fun_action(self):
        pet = self.pet
        pet._auto_fun_enabled = self.cb_auto_fun.isChecked()
        pet._auto_fun_chance_percent = max(0, min(100, int(self.spin_auto_fun_chance.value())))
        pet._auto_fun_actions = _normalize_auto_fun_actions(self._auto_fun_actions_from_ui())
        choices = pet._enabled_auto_fun_actions()
        if not choices:
            QMessageBox.information(self, "好玩动作", "请至少开启一个可自动参与的好玩动作。")
            return
        pet._start_auto_fun_action(random.choice(choices))
        pet._schedule_next_expression_change()
        pet._save_user_config()
        self.refresh_from_pet()

    def _preview_theme(self):
        self.pet.apply_theme(
            self.combo_theme.currentData(),
            self.combo_box_theme.currentData(),
            self.combo_cat_head_theme.currentData(),
            self.combo_doctoral_discipline.currentData(),
        )
        self.pet.apply_settings_center_accent(self.combo_settings_accent.currentData())
        if hasattr(self, "cb_academic_cat"):
            self.pet.set_academic_cat_enabled(self.cb_academic_cat.isChecked())
        self.pet._save_user_config()
        self._apply_settings_style()

    def _preview_settings_accent(self):
        if not hasattr(self, "combo_settings_accent"):
            return
        self.pet.apply_settings_center_accent(self.combo_settings_accent.currentData())
        self._apply_settings_style()
        if hasattr(self, "_apply_greeting_card_style"):
            self._apply_greeting_card_style()
        if getattr(self.pet, "_calendar_dialog", None) is not None:
            self.pet._calendar_dialog._apply_calendar_style()

    def _start_pomodoro_from_ui(self):
        self.apply_to_pet()
        self.pet.start_pomodoro()
        self.refresh_runtime_status()

    def _stop_pomodoro_from_ui(self):
        self.pet.stop_pomodoro()
        self.refresh_runtime_status()

    def refresh_runtime_status(self):
        if hasattr(self, "lbl_pomodoro_status"):
            self.lbl_pomodoro_status.setText(self.pet.pomodoro_status_text())
        if hasattr(self, "lbl_network_status"):
            self.lbl_network_status.setText(self.pet.network_status_text())

    def refresh_from_pet(self):
        pet = self.pet
        self.cb_gaze.setChecked(pet._gaze_track)
        self.cb_remember_position.setChecked(pet._remember_position)
        self.cb_remember_dock.setChecked(pet._remember_dock_state)
        self.cb_dnd.setChecked(pet._dnd_enabled)
        self.cb_startup.setChecked(is_startup_enabled())
        self.cb_status_auto.setChecked(pet._status_auto_hint)
        self.cb_daily_tip.setChecked(pet._daily_tip_enabled)
        self.cb_click_through.setChecked(pet._click_through_enabled)
        self.cb_auto_avoid_edge.setChecked(pet._auto_avoid_edge_enabled)
        self.cb_auto_expression.setChecked(pet._auto_expression_enabled)
        self.cb_auto_fun.setChecked(pet._auto_fun_enabled)
        self.spin_auto_fun_chance.setValue(max(0, min(100, int(pet._auto_fun_chance_percent))))
        for action_name, sw in self.auto_fun_action_checks.items():
            sw.setChecked(bool(pet._auto_fun_actions.get(action_name, False)))
        self._sync_expression_controls()

        scale_idx = max(0, min(len(pet.SCALE_OPTIONS) - 1, pet._scale_idx))
        self.combo_scale.setCurrentIndex(scale_idx)

        self.spin_opacity.setValue(max(35, min(100, int(round(pet._base_opacity * 100)))))
        self.cb_hover_full_opacity.setChecked(pet._hover_full_opacity)
        self.cb_dnd_dim.setChecked(pet._dnd_dim_enabled)
        self.spin_dnd_opacity.setValue(max(25, min(100, int(round(pet._dnd_dim_opacity * 100)))))
        perf_idx = self.combo_performance.findData(pet._performance_mode)
        self.combo_performance.setCurrentIndex(max(0, perf_idx))
        self.cb_particles_enabled.setChecked(pet._particles_enabled)
        self.cb_scheduled_cleanup.setChecked(pet._scheduled_cleanup_enabled)
        self.spin_scheduled_cleanup_min.setValue(max(10, int(pet._scheduled_cleanup_interval_minutes)))

        self.spin_tip_min.setValue(max(10, int(round(pet._daily_tip_min_seconds / 60))))
        self.spin_tip_max.setValue(max(10, int(round(pet._daily_tip_max_seconds / 60))))
        self.spin_expression_seconds.setValue(max(10, int(round(pet._expression_change_seconds))))

        self.cb_pomodoro.setChecked(pet._pomodoro_enabled)
        self.spin_pomo_work.setValue(max(1, int(pet._pomodoro_work_minutes)))
        self.spin_pomo_break.setValue(max(1, int(pet._pomodoro_break_minutes)))

        self.cb_network_monitor.setChecked(pet._network_monitor_enabled)
        self.spin_network_interval.setValue(max(30, int(pet._network_monitor_interval_seconds)))
        self.downloads_path_edit.setText(str(pet._downloads_path))
        self.cb_organize_preview.setChecked(pet._organize_preview_enabled)

        theme_idx = self.combo_theme.findData(pet._theme_name)
        self.combo_theme.setCurrentIndex(max(0, theme_idx))

        box_idx = self.combo_box_theme.findData(pet._box_theme_name)
        self.combo_box_theme.setCurrentIndex(max(0, box_idx))

        cat_head_idx = self.combo_cat_head_theme.findData(pet._cat_head_theme_name)
        self.combo_cat_head_theme.setCurrentIndex(max(0, cat_head_idx))

        if hasattr(self, "combo_doctoral_discipline"):
            disc_idx = self.combo_doctoral_discipline.findData(getattr(pet, "_doctoral_discipline", "silver"))
            self.combo_doctoral_discipline.setCurrentIndex(max(0, disc_idx))

        if hasattr(self, "cb_academic_cat"):
            self.cb_academic_cat.setChecked(bool(getattr(self.pet, "_academic_cat_enabled", False)))

        accent_idx = self.combo_settings_accent.findData(pet._settings_center_accent_name)
        self.combo_settings_accent.setCurrentIndex(max(0, accent_idx))
        self._apply_settings_style()

        if pet._edge_dock_visual_edge:
            self.btn_dock.setText("从边缘弹出")
        else:
            self.btn_dock.setText("收纳到最近屏幕边缘")

        if hasattr(self, "cb_hotkeys_enabled"):
            self.cb_hotkeys_enabled.setChecked(pet._hotkeys_enabled)
            for action, edit in self.hotkey_edits.items():
                edit.setText(pet._hotkeys.get(action, DEFAULT_HOTKEYS.get(action, "")))

        self.refresh_overview()
        self.refresh_launch_lists()
        self._populate_download_rules()
        self._populate_network_targets()
        self._refresh_storage_labels()
        self.refresh_runtime_status()
        self.refresh_history_list()

        if hasattr(self, "cb_birthday_enabled"):
            self.cb_birthday_enabled.setChecked(bool(getattr(self.pet, "_birthday_enabled", False)))
            self.edit_birthday_solar.setText(str(getattr(self.pet, "_birthday_solar_date", "") or ""))
            idx = self.combo_birthday_mode.findData(str(getattr(self.pet, "_birthday_mode", "both") or "both"))
            self.combo_birthday_mode.setCurrentIndex(idx if idx >= 0 else 3)
            if hasattr(self, "cb_holiday_new_year"):
                self.cb_holiday_new_year.setChecked(bool(getattr(self.pet, "_holiday_new_year_enabled", True)))
            if hasattr(self, "cb_holiday_lunar_new_year"):
                self.cb_holiday_lunar_new_year.setChecked(bool(getattr(self.pet, "_holiday_lunar_new_year_enabled", True)))
            if hasattr(self, "combo_greeting_frequency"):
                freq_idx = self.combo_greeting_frequency.findData(int(getattr(self.pet, "_greeting_frequency_minutes", 0)))
                self.combo_greeting_frequency.setCurrentIndex(freq_idx if freq_idx >= 0 else 0)
            if getattr(self.pet, "_birthday_solar_date", ""):
                self.lbl_birthday_lunar.setText(f"农历：{format_lunar_info(getattr(self.pet, '_birthday_lunar_info', None))}")
            else:
                self.lbl_birthday_lunar.setText("农历：未设置")
            self._refresh_birthday_preview_card()

    def _toggle_dock_state(self):
        pet = self.pet
        if pet._edge_dock_visual_edge:
            pet._edge_dock_hover_reveal = True
            pet._undock_from_edge()
        else:
            edge, _dist = pet._nearest_screen_edge()
            pet._dock_to_edge(edge)
        self.refresh_from_pet()

    def _validate_hotkeys_from_ui(self):
        if not hasattr(self, "hotkey_edits"):
            return True
        seen = {}
        invalid = []
        duplicates = []
        for action, edit in self.hotkey_edits.items():
            seq = edit.text().strip()
            if not seq:
                continue
            if _parse_hotkey_sequence(seq) is None:
                invalid.append(f"{HOTKEY_ACTION_LABELS.get(action, action)}：{seq}")
                continue
            norm = "+".join(part.strip().upper() for part in seq.replace("＋", "+").split("+") if part.strip())
            if norm in seen:
                duplicates.append(f"{HOTKEY_ACTION_LABELS.get(seen[norm], seen[norm])} 与 {HOTKEY_ACTION_LABELS.get(action, action)}：{seq}")
            else:
                seen[norm] = action
        if invalid or duplicates:
            msg = []
            if invalid:
                msg.append("以下快捷键格式无效：\n" + "\n".join(invalid))
            if duplicates:
                msg.append("以下快捷键重复：\n" + "\n".join(duplicates))
            QMessageBox.warning(self, "快捷键冲突检测", "\n\n".join(msg))
            return False
        return True

    def apply_to_pet(self):
        pet = self.pet

        if not self._validate_hotkeys_from_ui():
            return

        pet._gaze_track = self.cb_gaze.isChecked()
        if pet._gaze_track:
            pet._last_cursor_pos = QCursor.pos()
            pet._last_cursor_move_t = pet._t

        pet._remember_position = self.cb_remember_position.isChecked()
        pet._remember_dock_state = self.cb_remember_dock.isChecked()

        pet._dnd_enabled = self.cb_dnd.isChecked()
        pet._click_through_enabled = self.cb_click_through.isChecked()
        pet._auto_avoid_edge_enabled = self.cb_auto_avoid_edge.isChecked()

        ok, msg = set_startup_enabled(self.cb_startup.isChecked())
        if not ok and self.cb_startup.isChecked():
            pet._show_message(msg, "warn", 2.6)

        pet._status_auto_hint = self.cb_status_auto.isChecked()
        if pet._status_auto_hint:
            pet._next_status_check_t = pet._t + 2.0

        tip_min = int(self.spin_tip_min.value())
        tip_max = int(self.spin_tip_max.value())
        if tip_min > tip_max:
            tip_min, tip_max = tip_max, tip_min
            self.spin_tip_min.setValue(tip_min)
            self.spin_tip_max.setValue(tip_max)

        pet._hover_full_opacity = self.cb_hover_full_opacity.isChecked()
        pet._dnd_dim_enabled = self.cb_dnd_dim.isChecked()
        pet._dnd_dim_opacity = max(0.25, min(1.0, self.spin_dnd_opacity.value() / 100.0))
        pet.set_base_opacity(self.spin_opacity.value() / 100.0)
        pet.apply_performance_mode(self.combo_performance.currentData())
        pet.set_particles_enabled(self.cb_particles_enabled.isChecked())
        pet._scheduled_cleanup_enabled = self.cb_scheduled_cleanup.isChecked()
        pet._scheduled_cleanup_interval_minutes = max(10, int(self.spin_scheduled_cleanup_min.value()))
        if pet._scheduled_cleanup_enabled and pet._next_scheduled_cleanup_t <= pet._t:
            pet._next_scheduled_cleanup_t = pet._t + pet._scheduled_cleanup_interval_minutes * 60

        pet._daily_tip_enabled = self.cb_daily_tip.isChecked()
        pet._daily_tip_min_seconds = tip_min * 60
        pet._daily_tip_max_seconds = tip_max * 60
        if pet._daily_tip_enabled:
            pet._schedule_next_daily_tip()

        pet._auto_expression_enabled = self.cb_auto_expression.isChecked()
        pet._expression_change_seconds = max(10, int(self.spin_expression_seconds.value()))
        pet._auto_fun_enabled = self.cb_auto_fun.isChecked()
        pet._auto_fun_chance_percent = max(0, min(100, int(self.spin_auto_fun_chance.value())))
        pet._auto_fun_actions = _normalize_auto_fun_actions(self._auto_fun_actions_from_ui())
        if pet._auto_expression_enabled:
            pet._schedule_next_expression_change()

        pet._pomodoro_enabled = self.cb_pomodoro.isChecked()
        pet._pomodoro_work_minutes = max(1, int(self.spin_pomo_work.value()))
        pet._pomodoro_break_minutes = max(1, int(self.spin_pomo_break.value()))
        if not pet._pomodoro_enabled:
            pet.stop_pomodoro(show_message=False)

        pet._network_monitor_enabled = self.cb_network_monitor.isChecked()
        pet._network_monitor_interval_seconds = max(30, int(self.spin_network_interval.value()))
        if pet._network_monitor_enabled:
            pet._next_network_check_t = pet._t + 2.0

        path_text = self.downloads_path_edit.text().strip().strip('"')
        if not path_text:
            path_text = str(get_downloads_folder_path())
            self.downloads_path_edit.setText(path_text)
        pet._downloads_path = path_text
        pet._organize_preview_enabled = self.cb_organize_preview.isChecked()

        if hasattr(self, "cb_hotkeys_enabled"):
            pet._hotkeys_enabled = self.cb_hotkeys_enabled.isChecked()
            for action, edit in self.hotkey_edits.items():
                pet._hotkeys[action] = edit.text().strip()
            pet._hotkey_down_state = {}

        pet.apply_theme(
            self.combo_theme.currentData(),
            self.combo_box_theme.currentData(),
            self.combo_cat_head_theme.currentData(),
        )
        pet.apply_settings_center_accent(self.combo_settings_accent.currentData())
        self._apply_settings_style()
        pet.set_scale_index(self.combo_scale.currentIndex())
        pet.apply_click_through(pet._click_through_enabled)
        pet._save_user_config()
        pet._show_message("设置已应用", "info", 1.5)
        self.refresh_from_pet()


class CatPet(QWidget):
    SCALE_OPTIONS = [14, 18, 22, 26, 30, 36, 42, 50]

    def __init__(self):
        super().__init__()

        # 日历 / 生日提醒。
        self._birthday_enabled = False
        self._birthday_mode = "both"   # off / solar / lunar / both
        self._birthday_solar_date = "" # yyyy-mm-dd
        self._birthday_lunar_info = None
        self._birthday_last_shown_key = ""
        self._holiday_new_year_enabled = True
        self._holiday_lunar_new_year_enabled = True
        self._holiday_last_shown_key = ""
        self._greeting_frequency_minutes = 0
        self._calendar_dialog = None
        self._new_year_fireworks = []
        self._new_year_fireworks_until_t = 0.0
        self._academic_cat_enabled = False
        # 订日历事件
        self._calendar_events = []  # list of dict: {id, date, title, note, reminder_freq, last_shown_t}
        self._calendar_events_next_id = 1

        try:
            self._scale_idx = self.SCALE_OPTIONS.index(SCALE_PX_PER_UNIT)
        except ValueError:
            self._scale_idx = 2
        self._build_renderer()
        self.state = CatState()

        self._quantum_phase = None
        self._quantum_t = 0.0
        self._quantum_particles_model = []

        self._cleanup_phase = None
        self._cleanup_t = 0.0
        self._cleanup_particles_model = []
        self._cleanup_result = None
        self._cleanup_worker_started = False
        self._quantum_cleanup_mode = False

        self._speedtest_active = False
        self._speedtest_result = None
        self._speedtest_worker_started = False
        self._speedtest_display_t = 0.0

        self._ui_events = queue.Queue()
        self._message_until_t = 0.0
        self._message_fade_seconds = 0.28
        self._message_history = []
        self._status_auto_hint = True
        self._status_checking = False
        self._next_status_check_t = 8.0

        # 每日一句 / 随机小提示：自动弹出，右键菜单只负责开启 / 关闭。
        # 为了不打扰，间隔在 30~60 分钟之间随机浮动。
        self._daily_tip_enabled = True
        self._daily_tip_min_seconds = 30 * 60
        self._daily_tip_max_seconds = 60 * 60
        self._next_daily_tip_t = random.uniform(
            self._daily_tip_min_seconds,
            self._daily_tip_max_seconds,
        )

        # 免打扰模式：暂停自动提示、自动表情和网络自动弹窗。
        self._dnd_enabled = False
        self._click_through_enabled = False
        # 鼠标穿透开启时，按住 Ctrl 并把鼠标移到小猫上方，可临时恢复鼠标操作。
        self._click_through_ctrl_bypass = False
        self._auto_avoid_edge_enabled = False

        # 番茄钟。
        self._pomodoro_enabled = False
        self._pomodoro_work_minutes = 25
        self._pomodoro_break_minutes = 5
        self._pomodoro_phase = "idle"
        self._pomodoro_end_t = 0.0

        # 网络监控。
        self._network_monitor_enabled = False
        self._network_monitor_interval_seconds = 180
        self._network_targets = _make_default_network_targets()
        self._network_checking = False
        self._network_last_online = None
        self._network_last_text = "尚未检测"
        self._next_network_check_t = 20.0

        # 下载文件夹整理路径与规则，可在设置界面修改。
        self._downloads_path = str(get_downloads_folder_path())
        self._download_rules = _make_default_download_rules()
        self._organize_preview_enabled = True

        # 显示与性能。
        self._base_opacity = 1.0
        self._hover_full_opacity = True
        self._mouse_inside_window = False
        self._dnd_dim_enabled = True
        self._dnd_dim_opacity = 0.65
        self._particles_enabled = True
        self._scheduled_cleanup_enabled = False
        self._scheduled_cleanup_interval_minutes = 120
        self._next_scheduled_cleanup_t = 0.0
        self._performance_mode = "balanced"
        self._timer_interval_ms = 25

        # 小猫皮肤 / 主题。
        self._theme_name = "classic"
        self._box_theme_name = "theme"
        self._cat_head_theme_name = "british_shorthair"
        self._settings_center_accent_name = "cyan"
        apply_pet_theme(self._theme_name, self._box_theme_name, self._cat_head_theme_name)
        set_settings_center_accent(self._settings_center_accent_name)

        # 表情自动变化：默认开启，可在设置界面关闭或调整间隔。
        self._auto_expression_enabled = True
        self._expression_change_seconds = 30
        self._next_expression_change_t = self._expression_change_seconds
        self._auto_fun_enabled = True
        self._auto_fun_chance_percent = 30
        self._auto_fun_actions = _normalize_auto_fun_actions(None)

        # 可视化设置界面 / 命令面板句柄：按需创建，避免占用启动时间。
        self._settings_dialog = None
        self._command_palette = None

        # 桌宠动作快捷键：Windows 下支持全局轮询。
        self._hotkeys_enabled = False
        self._hotkeys = dict(DEFAULT_HOTKEYS)
        self._hotkey_down_state = {}
        self._next_hotkey_poll_t = 0.0
        self._context_menu_open = False
        self._last_status_text = "电脑状态：未检测"
        self._next_dashboard_update_t = 0.0
        self._dashboard_opacity = 0.0
        self._dashboard_status_checking = False
        self._dashboard_network_checking = False
        self._dashboard_next_status_t = 0.0
        self._dashboard_next_latency_t = 0.0
        self._dashboard_next_speed_t = 0.0
        self._dashboard_net_sample = None
        self._dashboard_net_speed_text = "网速 ↓ --  ↑ --"
        self._last_organize_moves = []

        # 右键“好玩”动作状态：头部动作 + 表情动作两类；全部可参与随时间自动变化。
        self._fun_action_name = None
        self._fun_action_start_t = 0.0
        self._fun_action_duration = 0.0

        self.setWindowFlags(Qt.FramelessWindowHint
                            | Qt.WindowStaysOnTopHint
                            | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowTitle("Schrödinger's Cat")

        self._dragging = False
        self._drag_offset = QPoint()
        self._click_start_pos = QPoint()
        self._gaze_track = True

        # 位置记忆：默认开启，下次启动恢复上次位置，也可恢复边缘收纳状态。
        self._remember_position = True
        self._remember_dock_state = True
        self._saved_pos_x = None
        self._saved_pos_y = None
        self._saved_dock_edge = ""
        self._saved_docked = False

        # 鼠标静止 3 秒后，小猫停止盯着鼠标，视线慢慢回正；鼠标再次移动后恢复跟随。
        self._gaze_idle_seconds = 3.0
        self._last_cursor_pos = QCursor.pos()
        self._last_cursor_move_t = 0.0

        # 右键菜单手动收纳到屏幕边缘，只留一个干净的弹出键；左键按下弹出键才展开。
        self._edge_dock_enabled = True
        self._edge_dock_visual_edge = ""
        self._edge_dock_target_progress = 0.0
        self._edge_dock_progress = 0.0
        self._edge_dock_visible_px = 46
        self._edge_dock_threshold_px = 2
        self._edge_dock_hover_reveal = False
        self._edge_dock_suppress_hover = False
        self._edge_dock_hover_cooldown_until = 0.0
        self._edge_dock_reveal_ignore_leave_until = 0.0

        self._t = 0.0
        self._next_blink_t = random.uniform(3.0, 7.0)
        self._blink_phase = None
        self._next_action_t = random.uniform(12.0, 22.0)
        self._sink_phase = None

        # 可编辑快捷工具 / 常用软件，支持配置文件持久化。
        self._quick_tools = _make_default_quick_tools()
        self._custom_apps = _make_default_custom_apps()
        self._ensure_holiday_defaults()
        self._load_user_config()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(self._timer_interval_ms)

        self._build_tray()

        self._restore_saved_position()

    def _build_renderer(self):
        scale = self.SCALE_OPTIONS[self._scale_idx]
        self.renderer = CatRenderer(scale=scale)
        self.setFixedSize(self.renderer.w, self.renderer.h)

    def _effective_base_opacity(self):
        if self._hover_full_opacity and self._mouse_inside_window:
            return 1.0
        if self._dnd_enabled and self._dnd_dim_enabled:
            return max(0.25, min(self._base_opacity, self._dnd_dim_opacity))
        return self._base_opacity

    def set_base_opacity(self, value):
        try:
            value = float(value)
        except Exception:
            value = 1.0
        self._base_opacity = max(0.35, min(1.0, value))
        self._apply_current_opacity()

    def _apply_current_opacity(self):
        eased = ease_smooth(self._edge_dock_progress) if self._edge_dock_visual_edge else 0.0
        self.setWindowOpacity(self._effective_base_opacity() * (1.0 - 0.22 * eased))

    def set_particles_enabled(self, enabled):
        global EFFECT_PARTICLES_ENABLED
        self._particles_enabled = bool(enabled)
        EFFECT_PARTICLES_ENABLED = self._particles_enabled

    def apply_performance_mode(self, mode):
        mode = str(mode or "balanced")
        intervals = {
            "smooth": 16,
            "balanced": 25,
            "powersave": 40,
        }
        if mode not in intervals:
            mode = "balanced"
        self._performance_mode = mode
        self._timer_interval_ms = intervals[mode]
        if hasattr(self, "timer") and self.timer is not None:
            self.timer.start(self._timer_interval_ms)

    def _add_message_history(self, text, kind="info"):
        text = str(text).strip()
        if not text:
            return
        entry = {
            "time": time.strftime("%H:%M:%S"),
            "kind": str(kind or "info"),
            "text": text,
        }
        self._message_history.append(entry)
        if len(self._message_history) > 120:
            self._message_history = self._message_history[-120:]
        if self._settings_dialog is not None and self._settings_dialog.isVisible():
            self._settings_dialog.refresh_history_list()

    def _restore_saved_position(self):
        scr = QGuiApplication.primaryScreen().availableGeometry()
        default_pos = QPoint(scr.right() - self.width() - 40,
                             scr.bottom() - self.height() - 60)

        if not self._remember_position:
            self.move(default_pos)
            return

        try:
            if self._saved_pos_x is None or self._saved_pos_y is None:
                self.move(default_pos)
            else:
                x = int(self._saved_pos_x)
                y = int(self._saved_pos_y)
                x = max(scr.left(), min(scr.right() - self.width() + 1, x))
                y = max(scr.top(), min(scr.bottom() - self.height() + 1, y))
                self.move(x, y)
        except Exception:
            self.move(default_pos)

        # 恢复“已收纳到边缘”的状态。恢复失败时不会影响正常显示。
        if self._remember_dock_state and self._saved_docked and self._saved_dock_edge:
            edge = str(self._saved_dock_edge)
            if edge in ("left", "right", "top", "bottom"):
                self._edge_dock_visual_edge = edge
                self._edge_dock_target_progress = 1.0
                self._edge_dock_progress = 1.0
                self.state.dock_edge = edge
                self.state.dock_progress = 1.0
                self.move(self._dock_pos_for_edge(edge, hidden=True))
                self._apply_current_opacity()

    def _remember_current_position(self):
        if not getattr(self, "_remember_position", True):
            return
        self._saved_pos_x = int(self.x())
        self._saved_pos_y = int(self.y())
        self._save_user_config()

    def closeEvent(self, ev):
        self._remember_current_position()
        super().closeEvent(ev)

    def apply_theme(self, theme_name, box_theme_name=None, cat_head_theme_name=None, doctoral_discipline=None):
        if theme_name not in THEME_PALETTES:
            theme_name = "classic"
        if box_theme_name not in BOX_COLOR_PALETTES:
            box_theme_name = self._box_theme_name if self._box_theme_name in BOX_COLOR_PALETTES else "theme"
        if cat_head_theme_name not in CAT_HEAD_PALETTES:
            cat_head_theme_name = self._cat_head_theme_name if self._cat_head_theme_name in CAT_HEAD_PALETTES else "british_shorthair"
        if doctoral_discipline not in DOCTORAL_DISCIPLINES and doctoral_discipline is not None:
            doctoral_discipline = self._doctoral_discipline if hasattr(self, "_doctoral_discipline") else "silver"

        self._theme_name = theme_name
        self._box_theme_name = box_theme_name
        self._cat_head_theme_name = cat_head_theme_name
        if doctoral_discipline is not None:
            self._doctoral_discipline = doctoral_discipline
        elif not hasattr(self, "_doctoral_discipline"):
            self._doctoral_discipline = "silver"
        apply_pet_theme(theme_name, box_theme_name, cat_head_theme_name, self._doctoral_discipline)
        self.update()

    def apply_settings_center_accent(self, accent_name):
        if accent_name not in SETTING_CENTER_ACCENTS:
            accent_name = "cyan"
        self._settings_center_accent_name = set_settings_center_accent(accent_name)
        if self._settings_dialog is not None and self._settings_dialog.isVisible():
            self._settings_dialog._apply_settings_style()
            if hasattr(self._settings_dialog, "_apply_greeting_card_style"):
                self._settings_dialog._apply_greeting_card_style()
        if getattr(self, "_calendar_dialog", None) is not None:
            self._calendar_dialog._apply_calendar_style()

    def _reset_runtime_defaults(self):
        """把当前运行状态重置为程序初始默认值，不销毁窗口和托盘。"""
        try:
            default_scale_idx = self.SCALE_OPTIONS.index(SCALE_PX_PER_UNIT)
        except ValueError:
            default_scale_idx = 2

        self._scale_idx = default_scale_idx
        self._build_renderer()
        self.state = CatState()

        self._quantum_phase = None
        self._quantum_t = 0.0
        self._quantum_particles_model = []

        self._cleanup_phase = None
        self._cleanup_t = 0.0
        self._cleanup_particles_model = []
        self._cleanup_result = None
        self._cleanup_worker_started = False
        self._quantum_cleanup_mode = False

        self._speedtest_active = False
        self._speedtest_result = None
        self._speedtest_worker_started = False
        self._speedtest_display_t = 0.0

        self._message_until_t = 0.0
        self._message_fade_seconds = 0.28
        self._message_history = []
        self._status_auto_hint = True
        self._status_checking = False
        self._next_status_check_t = 8.0

        self._daily_tip_enabled = True
        self._daily_tip_min_seconds = 30 * 60
        self._daily_tip_max_seconds = 60 * 60
        self._next_daily_tip_t = self._t + random.uniform(
            self._daily_tip_min_seconds,
            self._daily_tip_max_seconds,
        )

        self._dnd_enabled = False
        self._click_through_enabled = False
        self._click_through_ctrl_bypass = False
        self._auto_avoid_edge_enabled = False

        self._pomodoro_enabled = False
        self._pomodoro_work_minutes = 25
        self._pomodoro_break_minutes = 5
        self._pomodoro_phase = "idle"
        self._pomodoro_end_t = 0.0

        self._network_monitor_enabled = False
        self._network_monitor_interval_seconds = 180
        self._network_targets = _make_default_network_targets()
        self._network_checking = False
        self._network_last_online = None
        self._network_last_text = "尚未检测"
        self._next_network_check_t = self._t + 20.0

        self._downloads_path = str(get_downloads_folder_path())
        self._download_rules = _make_default_download_rules()
        self._organize_preview_enabled = True

        self._base_opacity = 1.0
        self._hover_full_opacity = True
        self._mouse_inside_window = False
        self._dnd_dim_enabled = True
        self._dnd_dim_opacity = 0.65
        self._particles_enabled = True
        self._scheduled_cleanup_enabled = False
        self._scheduled_cleanup_interval_minutes = 120
        self._next_scheduled_cleanup_t = self._t + self._scheduled_cleanup_interval_minutes * 60
        self._performance_mode = "balanced"
        self.set_particles_enabled(True)
        self.apply_performance_mode("balanced")

        self._theme_name = "classic"
        self._box_theme_name = "theme"
        self._cat_head_theme_name = "british_shorthair"
        self._settings_center_accent_name = "cyan"
        apply_pet_theme(self._theme_name, self._box_theme_name, self._cat_head_theme_name)
        set_settings_center_accent(self._settings_center_accent_name)

        self._auto_expression_enabled = True
        self._expression_change_seconds = 30
        self._next_expression_change_t = self._t + self._expression_change_seconds
        self._auto_fun_enabled = True
        self._auto_fun_chance_percent = 30
        self._auto_fun_actions = _normalize_auto_fun_actions(None)

        self._gaze_track = True
        self._remember_position = True
        self._remember_dock_state = True
        self._saved_pos_x = None
        self._saved_pos_y = None
        self._saved_dock_edge = ""
        self._saved_docked = False

        self._last_cursor_pos = QCursor.pos()
        self._last_cursor_move_t = self._t

        self._edge_dock_enabled = True
        self._edge_dock_visual_edge = ""
        self._edge_dock_target_progress = 0.0
        self._edge_dock_progress = 0.0
        self._edge_dock_hover_reveal = False
        self._edge_dock_suppress_hover = False
        self._edge_dock_hover_cooldown_until = 0.0
        self._edge_dock_reveal_ignore_leave_until = 0.0

        self._next_blink_t = self._t + random.uniform(3.0, 7.0)
        self._blink_phase = None
        self._next_action_t = self._t + random.uniform(12.0, 22.0)
        self._sink_phase = None

        self._quick_tools = _make_default_quick_tools()
        self._custom_apps = _make_default_custom_apps()

        self._hotkeys_enabled = False
        self._hotkeys = dict(DEFAULT_HOTKEYS)
        self._hotkey_down_state = {}
        self._next_hotkey_poll_t = 0.0
        self._context_menu_open = False
        self._last_status_text = "电脑状态：未检测"
        self._next_dashboard_update_t = 0.0
        self._dashboard_opacity = 0.0
        self._dashboard_status_checking = False
        self._dashboard_network_checking = False
        self._dashboard_next_status_t = 0.0
        self._dashboard_next_latency_t = 0.0
        self._dashboard_next_speed_t = 0.0
        self._dashboard_net_sample = None
        self._dashboard_net_speed_text = "网速 ↓ --  ↑ --"
        self._last_organize_moves = []

        self._fun_action_name = None
        self._fun_action_start_t = 0.0
        self._fun_action_duration = 0.0

        self._clear_edge_dock_state()
        self._apply_current_opacity()
        self._restore_saved_position()
        self.update()

    def reload_config_from_disk(self, reset_first=True):
        """重新读取配置文件，并刷新当前运行状态。"""
        if reset_first:
            self._reset_runtime_defaults()
        self._load_user_config()
        self._restore_saved_position()
        self._apply_current_opacity()
        self.update()
        if self._settings_dialog is not None and self._settings_dialog.isVisible():
            self._settings_dialog.refresh_from_pet()
        if self._command_palette is not None and self._command_palette.isVisible():
            self._command_palette.refresh_commands()

    def restore_initial_settings(self):
        """一键恢复初始设置：立即生效并写回默认配置。"""
        cfg_path = _pet_config_path()
        try:
            if cfg_path.exists():
                cfg_path.unlink()
        except Exception:
            pass

        self._reset_runtime_defaults()
        self._save_user_config()

        if self._settings_dialog is not None and self._settings_dialog.isVisible():
            self._settings_dialog.refresh_from_pet()
        if self._command_palette is not None and self._command_palette.isVisible():
            self._command_palette.refresh_commands()


    def _ensure_builtin_custom_app(self, name, path):
        """把新版本内置的常用软件补到已有配置中；用户之后仍可在设置里删除。"""
        try:
            exists = False
            for item in self._custom_apps:
                if str(item.get("name", "")).strip().lower() == name.lower():
                    exists = True
                    break
                if str(item.get("path", "")).strip().strip('"').lower() == str(path).lower():
                    exists = True
                    break
            if not exists:
                self._custom_apps.append({
                    "name": name,
                    "type": "path",
                    "path": path,
                    "args": "",
                })
        except Exception:
            pass


    def _ensure_holiday_defaults(self):
        """确保节日祝福字段存在，兼容旧配置和旧对象状态。"""
        if not hasattr(self, "_holiday_new_year_enabled"):
            self._holiday_new_year_enabled = True
        if not hasattr(self, "_holiday_lunar_new_year_enabled"):
            self._holiday_lunar_new_year_enabled = True
        if not hasattr(self, "_holiday_last_shown_key"):
            self._holiday_last_shown_key = ""
        if not hasattr(self, "_greeting_frequency_minutes"):
            self._greeting_frequency_minutes = 0


    def _load_user_config(self):
        self._ensure_holiday_defaults()
        cfg = load_pet_config()

        self._quick_tools = _normalize_launch_items(
            cfg.get("quick_tools"),
            _make_default_quick_tools(),
        )
        self._custom_apps = _normalize_launch_items(
            cfg.get("custom_apps"),
            _make_default_custom_apps(),
        )

        try:
            scale_idx = int(cfg.get("scale_idx", self._scale_idx))
            if 0 <= scale_idx < len(self.SCALE_OPTIONS):
                self.set_scale_index(scale_idx)
        except Exception:
            pass

        self._birthday_enabled = bool(cfg.get("birthday_enabled", self._birthday_enabled))
        self._birthday_mode = str(cfg.get("birthday_mode", self._birthday_mode))
        if self._birthday_mode not in BIRTHDAY_MODE_LABELS:
            self._birthday_mode = "both"
        self._birthday_solar_date = str(cfg.get("birthday_solar_date", self._birthday_solar_date)).strip()
        saved_lunar = cfg.get("birthday_lunar_info")
        self._birthday_lunar_info = saved_lunar if isinstance(saved_lunar, dict) else None
        bd = parse_solar_date_text(self._birthday_solar_date)
        if bd:
            self._birthday_lunar_info = solar_to_lunar_info(bd) or self._birthday_lunar_info
        self._birthday_last_shown_key = str(cfg.get("birthday_last_shown_key", self._birthday_last_shown_key))
        self._holiday_new_year_enabled = bool(cfg.get("holiday_new_year_enabled", getattr(self, "_holiday_new_year_enabled", True)))
        self._holiday_lunar_new_year_enabled = bool(cfg.get("holiday_lunar_new_year_enabled", getattr(self, "_holiday_lunar_new_year_enabled", True)))
        self._holiday_last_shown_key = str(cfg.get("holiday_last_shown_key", getattr(self, "_holiday_last_shown_key", "")))
        self._greeting_frequency_minutes = int(cfg.get("greeting_frequency_minutes", getattr(self, "_greeting_frequency_minutes", 0)))

        self._gaze_track = bool(cfg.get("gaze_track", self._gaze_track))
        self._message_history = list(cfg.get("message_history", self._message_history))[-120:]
        self._hover_full_opacity = bool(cfg.get("hover_full_opacity", self._hover_full_opacity))
        self._dnd_dim_enabled = bool(cfg.get("dnd_dim_enabled", self._dnd_dim_enabled))
        self._dnd_dim_opacity = max(0.25, min(1.0, float(cfg.get("dnd_dim_opacity", self._dnd_dim_opacity))))
        self.set_base_opacity(float(cfg.get("base_opacity", self._base_opacity)))
        self.apply_performance_mode(str(cfg.get("performance_mode", self._performance_mode)))
        self.set_particles_enabled(bool(cfg.get("particles_enabled", self._particles_enabled)))
        self._scheduled_cleanup_enabled = bool(cfg.get("scheduled_cleanup_enabled", self._scheduled_cleanup_enabled))
        self._scheduled_cleanup_interval_minutes = max(10, int(cfg.get("scheduled_cleanup_interval_minutes", self._scheduled_cleanup_interval_minutes)))
        self._next_scheduled_cleanup_t = self._t + self._scheduled_cleanup_interval_minutes * 60
        self._remember_position = bool(cfg.get("remember_position", self._remember_position))
        self._remember_dock_state = bool(cfg.get("remember_dock_state", self._remember_dock_state))
        self._saved_pos_x = cfg.get("pos_x", self._saved_pos_x)
        self._saved_pos_y = cfg.get("pos_y", self._saved_pos_y)
        self._saved_dock_edge = str(cfg.get("dock_edge", self._saved_dock_edge))
        self._saved_docked = bool(cfg.get("docked", self._saved_docked))
        self._dnd_enabled = bool(cfg.get("dnd_enabled", self._dnd_enabled))
        self._click_through_enabled = bool(cfg.get("click_through_enabled", self._click_through_enabled))
        self._auto_avoid_edge_enabled = bool(cfg.get("auto_avoid_edge_enabled", self._auto_avoid_edge_enabled))
        self._status_auto_hint = bool(cfg.get("status_auto_hint", self._status_auto_hint))
        self._daily_tip_enabled = bool(cfg.get("daily_tip_enabled", self._daily_tip_enabled))
        self._auto_expression_enabled = bool(cfg.get("auto_expression_enabled", self._auto_expression_enabled))
        self._auto_fun_enabled = bool(cfg.get("auto_fun_enabled", self._auto_fun_enabled))
        self._auto_fun_chance_percent = max(0, min(100, int(cfg.get("auto_fun_chance_percent", self._auto_fun_chance_percent))))
        self._auto_fun_actions = _normalize_auto_fun_actions(cfg.get("auto_fun_actions", self._auto_fun_actions))

        self._pomodoro_enabled = bool(cfg.get("pomodoro_enabled", self._pomodoro_enabled))
        self._pomodoro_work_minutes = max(1, int(cfg.get("pomodoro_work_minutes", self._pomodoro_work_minutes)))
        self._pomodoro_break_minutes = max(1, int(cfg.get("pomodoro_break_minutes", self._pomodoro_break_minutes)))

        self._network_monitor_enabled = bool(cfg.get("network_monitor_enabled", self._network_monitor_enabled))
        self._network_monitor_interval_seconds = max(30, int(cfg.get("network_monitor_interval_seconds", self._network_monitor_interval_seconds)))
        self._network_targets = _normalize_network_targets(cfg.get("network_targets", self._network_targets))
        self._downloads_path = str(get_downloads_folder_path(cfg.get("downloads_path", self._downloads_path)))
        self._download_rules = _normalize_download_rules(cfg.get("download_rules"))
        self._organize_preview_enabled = bool(cfg.get("organize_preview_enabled", self._organize_preview_enabled))
        self._hotkeys_enabled = bool(cfg.get("hotkeys_enabled", self._hotkeys_enabled))
        self._hotkeys = _normalize_hotkeys(cfg.get("hotkeys", self._hotkeys))

        self._academic_cat_enabled = bool(cfg.get("academic_cat_enabled", getattr(self, "_academic_cat_enabled", False)))
        self._doctoral_discipline = str(cfg.get("doctoral_discipline", getattr(self, "_doctoral_discipline", "silver")))
        # 订日历事件
        self._calendar_events = list(cfg.get("calendar_events", []))
        self._calendar_events_next_id = int(cfg.get("calendar_events_next_id", 1))

        self.apply_theme(
            str(cfg.get("theme_name", self._theme_name)),
            str(cfg.get("box_theme_name", self._box_theme_name)),
            str(cfg.get("cat_head_theme_name", self._cat_head_theme_name)),
            self._doctoral_discipline,
        )
        self.apply_settings_center_accent(str(cfg.get("settings_center_accent_name", self._settings_center_accent_name)))
        self.apply_click_through(self._click_through_enabled)

        try:
            expr_seconds = int(cfg.get("expression_change_seconds", self._expression_change_seconds))
            self._expression_change_seconds = max(10, expr_seconds)
            self._schedule_next_expression_change()
        except Exception:
            pass

        try:
            tip_min = int(cfg.get("daily_tip_min_seconds", self._daily_tip_min_seconds))
            tip_max = int(cfg.get("daily_tip_max_seconds", self._daily_tip_max_seconds))
            self._daily_tip_min_seconds = max(10 * 60, tip_min)
            self._daily_tip_max_seconds = max(self._daily_tip_min_seconds, tip_max)
            self._schedule_next_daily_tip()
        except Exception:
            pass

    def _save_user_config(self):
        data = {
            "scale_idx": int(self._scale_idx),
            "gaze_track": bool(self._gaze_track),
            "base_opacity": float(self._base_opacity),
            "hover_full_opacity": bool(self._hover_full_opacity),
            "dnd_dim_enabled": bool(self._dnd_dim_enabled),
            "dnd_dim_opacity": float(self._dnd_dim_opacity),
            "performance_mode": str(self._performance_mode),
            "particles_enabled": bool(self._particles_enabled),
            "scheduled_cleanup_enabled": bool(self._scheduled_cleanup_enabled),
            "scheduled_cleanup_interval_minutes": int(self._scheduled_cleanup_interval_minutes),
            "message_history": list(self._message_history[-120:]),
            "remember_position": bool(self._remember_position),
            "remember_dock_state": bool(self._remember_dock_state),
            "pos_x": int(self.x()),
            "pos_y": int(self.y()),
            "dock_edge": str(self._edge_dock_visual_edge or self._saved_dock_edge or ""),
            "docked": bool(self._edge_dock_visual_edge and self._edge_dock_target_progress >= 0.5),
            "dnd_enabled": bool(self._dnd_enabled),
            "click_through_enabled": bool(self._click_through_enabled),
            "auto_avoid_edge_enabled": bool(self._auto_avoid_edge_enabled),
            "status_auto_hint": bool(self._status_auto_hint),
            "daily_tip_enabled": bool(self._daily_tip_enabled),
            "daily_tip_min_seconds": int(self._daily_tip_min_seconds),
            "daily_tip_max_seconds": int(self._daily_tip_max_seconds),
            "auto_expression_enabled": bool(self._auto_expression_enabled),
            "expression_change_seconds": int(self._expression_change_seconds),
            "auto_fun_enabled": bool(self._auto_fun_enabled),
            "auto_fun_chance_percent": int(self._auto_fun_chance_percent),
            "auto_fun_actions": dict(self._auto_fun_actions),
            "pomodoro_enabled": bool(self._pomodoro_enabled),
            "pomodoro_work_minutes": int(self._pomodoro_work_minutes),
            "pomodoro_break_minutes": int(self._pomodoro_break_minutes),
            "network_monitor_enabled": bool(self._network_monitor_enabled),
            "network_monitor_interval_seconds": int(self._network_monitor_interval_seconds),
            "network_targets": _clone_network_targets(self._network_targets),
            "downloads_path": str(self._downloads_path),
            "download_rules": _clone_download_rules(self._download_rules),
            "organize_preview_enabled": bool(self._organize_preview_enabled),
            "hotkeys_enabled": bool(self._hotkeys_enabled),
            "hotkeys": dict(self._hotkeys),
            "theme_name": str(self._theme_name),
            "box_theme_name": str(self._box_theme_name),
            "cat_head_theme_name": str(self._cat_head_theme_name),
            "settings_center_accent_name": str(self._settings_center_accent_name),
            "academic_cat_enabled": bool(getattr(self, "_academic_cat_enabled", False)),
            "doctoral_discipline": str(getattr(self, "_doctoral_discipline", "silver")),
            "calendar_events": list(getattr(self, "_calendar_events", [])),
            "calendar_events_next_id": int(getattr(self, "_calendar_events_next_id", 1)),
            "birthday_enabled": bool(self._birthday_enabled),
            "birthday_mode": str(self._birthday_mode),
            "birthday_solar_date": str(self._birthday_solar_date),
            "birthday_lunar_info": self._birthday_lunar_info,
            "birthday_last_shown_key": str(self._birthday_last_shown_key),
            "holiday_new_year_enabled": bool(getattr(self, "_holiday_new_year_enabled", True)),
            "holiday_lunar_new_year_enabled": bool(getattr(self, "_holiday_lunar_new_year_enabled", True)),
            "holiday_last_shown_key": str(getattr(self, "_holiday_last_shown_key", "")),
            "greeting_frequency_minutes": int(getattr(self, "_greeting_frequency_minutes", 0)),
            "quick_tools": _clone_launch_items(self._quick_tools),
            "custom_apps": _clone_launch_items(self._custom_apps),
        }
        return save_pet_config(data)

    def _open_launch_item(self, item):
        try:
            ok, msg = run_launch_item(item)
            self._show_message(msg, "ok" if ok else "warn", 2.4)
        except Exception as exc:
            self._show_message("打开失败：" + (str(exc) or exc.__class__.__name__), "bad", 2.8, "surprise")

    def set_scale_index(self, new_idx):
        if not (0 <= int(new_idx) < len(self.SCALE_OPTIONS)):
            return
        new_idx = int(new_idx)
        if new_idx == self._scale_idx:
            return

        was_docked = bool(self._edge_dock_visual_edge and self._edge_dock_target_progress >= 0.5)
        dock_edge = self._edge_dock_visual_edge
        self._scale_idx = new_idx
        old_pos = self.pos()
        self._build_renderer()
        self.move(old_pos)
        if was_docked and dock_edge:
            self.move(self._dock_pos_for_edge(dock_edge, hidden=True))
        self.update()

    def _move_settings_panel_to_top_side(self):
        """把设置中心移动到当前屏幕顶侧并置前。"""
        dlg = self._settings_dialog
        if dlg is None:
            return

        try:
            # 优先使用小猫所在屏幕；如果拿不到，再用鼠标所在屏幕。
            screen = self.screen() or QGuiApplication.screenAt(QCursor.pos()) or QGuiApplication.primaryScreen()
            geom = screen.availableGeometry() if screen else self._screen_available_geometry()

            # show 后再取尺寸，避免隐藏窗口 width/height 不准。
            if not dlg.isVisible():
                dlg.show()

            w = max(1, dlg.frameGeometry().width() or dlg.width())
            h = max(1, dlg.frameGeometry().height() or dlg.height())

            x = geom.left() + (geom.width() - w) // 2
            y = geom.top() + 24

            # 防止窗口超出当前屏幕。
            x = max(geom.left() + 8, min(x, geom.right() - w - 8))
            y = max(geom.top() + 8, min(y, geom.bottom() - h - 8))

            dlg.move(int(x), int(y))
            dlg.showNormal()
            dlg.raise_()
            dlg.activateWindow()
            dlg.setFocus()
        except Exception:
            pass

    def _open_settings_panel(self):
        if self._settings_dialog is None:
            self._settings_dialog = PetSettingsDialog(self)

        self._settings_dialog.refresh_from_pet()
        self._settings_dialog.showNormal()
        self._settings_dialog.raise_()
        self._settings_dialog.activateWindow()
        self._settings_dialog.setFocus()

        # 每次点击“设置中心”都移动到顶侧；用 singleShot 等窗口显示/刷新后再取准确尺寸。
        QTimer.singleShot(0, self._move_settings_panel_to_top_side)

    def _open_command_palette(self):
        if self._command_palette is None:
            self._command_palette = CommandPaletteDialog(self)
        self._command_palette.refresh_commands()
        self._command_palette.show()
        self._command_palette.raise_()
        self._command_palette.activateWindow()
        self._command_palette.search_edit.setFocus()
        self._command_palette.search_edit.selectAll()


    def _toggle_visible_from_tray(self):
        """托盘智能显示/隐藏：可见时隐藏，不可见时显示。"""
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.raise_()
            self.activateWindow()



    def _refresh_tray_visible_action(self):
        if hasattr(self, "a_tray_visible_toggle"):
            self.a_tray_visible_toggle.setText("隐藏" if self.isVisible() else "显示")


    def _build_tray(self):
        pix = QPixmap(32, 32); pix.fill(Qt.transparent)
        pp = QPainter(pix)
        pp.setRenderHint(QPainter.Antialiasing)
        pp.setBrush(C_BOX_YELLOW); pp.setPen(QPen(QColor("#333"), 2))
        pp.drawRect(4, 12, 24, 16)
        pp.setBrush(C_HEAD_GREY); pp.setPen(Qt.NoPen)
        pp.drawEllipse(QPointF(16, 10), 7, 6)
        pp.end()

        self.tray = QSystemTrayIcon(QIcon(pix), self)
        m = QMenu()
        a_settings = QAction("设置中心", self); a_settings.triggered.connect(self._open_settings_panel)
        a_palette = QAction("命令面板", self); a_palette.triggered.connect(self._open_command_palette)
        a_click_off = QAction("关闭鼠标穿透", self); a_click_off.triggered.connect(self._disable_click_through_from_tray)
        self.a_tray_visible_toggle = QAction("隐藏" if self.isVisible() else "显示", self)
        self.a_tray_visible_toggle.triggered.connect(self._toggle_visible_from_tray)
        a_quit = QAction("退出", self); a_quit.triggered.connect(QApplication.quit)

        # 智能显示/隐藏项放在原来“隐藏”的位置；不再同时出现“显示”和“隐藏”。
        m.addAction(a_settings)
        m.addAction(a_palette)
        m.addAction(a_click_off)
        m.addAction(self.a_tray_visible_toggle)
        m.addSeparator()
        m.addAction(a_quit)

        m.aboutToShow.connect(self._refresh_tray_visible_action)
        self.tray.setContextMenu(m)
        self.tray.setToolTip("Schrödinger's Cat v1.0.0")
        self.tray.activated.connect(self._on_tray)
        self.tray.show()

    def _disable_click_through_from_tray(self):
        self._click_through_ctrl_bypass = False
        self.apply_click_through(False)
        self._save_user_config()
        self._show_message("鼠标穿透已关闭", "info", 1.8)

    def _on_tray(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            if self.isVisible():
                self.hide()
            else:
                self.show()

    # ── 主时钟 ──────────────────────────────────────────────
    def _set_effective_click_through(self, enabled):
        """设置当前窗口是否真正鼠标穿透。"""
        enabled = bool(enabled)
        try:
            current = bool(getattr(self, "_effective_click_through", False))
            if current == enabled:
                return

            self._effective_click_through = enabled
            self.setAttribute(Qt.WA_TransparentForMouseEvents, enabled)
            if hasattr(Qt, "WindowTransparentForInput"):
                was_visible = self.isVisible()
                self.setWindowFlag(Qt.WindowTransparentForInput, enabled)
                if was_visible:
                    self.show()
        except Exception:
            pass

    def apply_click_through(self, enabled):
        self._click_through_enabled = bool(enabled)
        if not self._click_through_enabled:
            self._click_through_ctrl_bypass = False
        self._set_effective_click_through(
            self._click_through_enabled and not self._click_through_ctrl_bypass
        )

    def _update_click_through_ctrl_bypass(self):
        """鼠标穿透开启时，按住 Ctrl 并把鼠标放到小猫区域，可临时恢复鼠标操作。"""
        if not self._click_through_enabled:
            if self._click_through_ctrl_bypass:
                self._click_through_ctrl_bypass = False
                self._set_effective_click_through(False)
            return

        ctrl_pressed = _is_ctrl_pressed_global()
        cursor_over_cat = self._cursor_inside_self(padding=8)
        # 拖动中即使松开 Ctrl，也先保持可操作，避免拖到一半突然重新穿透。
        # 右键菜单打开期间也必须保持可操作，否则鼠标移到菜单上时会恢复穿透，菜单容易消失。
        should_bypass = bool(
            getattr(self, "_context_menu_open", False)
            or (ctrl_pressed and cursor_over_cat)
            or self._dragging
        )

        if should_bypass != self._click_through_ctrl_bypass:
            self._click_through_ctrl_bypass = should_bypass
            self._set_effective_click_through(
                self._click_through_enabled and not self._click_through_ctrl_bypass
            )
            if should_bypass:
                self._mouse_inside_window = True
                self._dashboard_opacity = max(self._dashboard_opacity, 0.35)
                self.update()
            else:
                self._mouse_inside_window = False
                self.update()

    def _dashboard_active(self):
        return bool(
            self._mouse_inside_window
            and self.isVisible()
            and not self._edge_dock_visual_edge
            and not getattr(self, "_effective_click_through", False)
        )

    def _start_dashboard_status_refresh(self):
        if self._dashboard_status_checking:
            return
        self._dashboard_status_checking = True

        def worker():
            res = get_system_status()
            self._ui_events.put(("dashboard_status_result", res))

        threading.Thread(target=worker, daemon=True).start()

    def _start_dashboard_network_refresh(self):
        if self._dashboard_network_checking:
            return
        self._dashboard_network_checking = True

        def worker():
            res = check_network_status(timeout_s=1.2, targets=self._network_targets)
            self._ui_events.put(("dashboard_network_result", res))

        threading.Thread(target=worker, daemon=True).start()

    def _update_dashboard_net_speed(self):
        sample = _get_network_io_totals()
        now = time.perf_counter()
        if not sample:
            self._dashboard_net_speed_text = "网速 ↓ --  ↑ --"
            self._dashboard_net_sample = None
            return

        sent, recv = sample
        if self._dashboard_net_sample is None:
            self._dashboard_net_sample = (now, sent, recv)
            self._dashboard_net_speed_text = "网速 ↓ 0B/s  ↑ 0B/s"
            return

        prev_t, prev_sent, prev_recv = self._dashboard_net_sample
        dt = max(0.1, now - prev_t)
        # 32 位计数可能溢出，出现负数时本轮不计算。
        down = recv - prev_recv
        up = sent - prev_sent
        if down < 0 or up < 0:
            self._dashboard_net_sample = (now, sent, recv)
            self._dashboard_net_speed_text = "网速 ↓ --  ↑ --"
            return

        self._dashboard_net_sample = (now, sent, recv)
        self._dashboard_net_speed_text = f"网速 ↓ {_format_bytes_rate(down / dt)}  ↑ {_format_bytes_rate(up / dt)}"

    def _maybe_refresh_dashboard_metrics(self):
        """鼠标悬停时刷新仪表盘数据；离开后停止高频读取，避免额外占用。"""
        if not self._dashboard_active():
            return

        if self._t >= self._dashboard_next_status_t:
            self._dashboard_next_status_t = self._t + 1.0
            self._start_dashboard_status_refresh()

        if self._t >= self._dashboard_next_speed_t:
            self._dashboard_next_speed_t = self._t + 1.0
            self._update_dashboard_net_speed()

        if self._t >= self._dashboard_next_latency_t:
            self._dashboard_next_latency_t = self._t + 10.0
            self._start_dashboard_network_refresh()

    def _build_dashboard_text(self):
        """仪表盘文本尽量短行显示，避免在小窗口里被截断。"""
        lines = []

        status = str(self._last_status_text or "").strip()
        if status.startswith("电脑状态："):
            status = status.replace("电脑状态：", "", 1).strip()
        if status and status != "未检测":
            lines.append(status)
        else:
            lines.append("CPU --   内存 --")

        lines.append(str(self._dashboard_net_speed_text or "网速 ↓ --  ↑ --"))

        net = str(self._network_last_text or "尚未检测").strip()
        # 原始格式类似：网络正常  延迟 27 ms · AliDNS
        if "·" in net:
            main, target = net.split("·", 1)
            main = main.strip()
            target = target.strip()
        else:
            main, target = net, ""

        main = main.replace("网络正常  延迟", "延迟")
        main = main.replace("网络正常 延迟", "延迟")
        main = main.replace("网络连接异常", "网络异常")
        main = main.replace(" ms", "ms")
        main = main.strip()
        lines.append(main if main else "延迟 --")
        if target:
            lines.append("目标：" + target)

        if self._pomodoro_enabled and self._pomodoro_phase in ("work", "break"):
            remain = max(0, int(self._pomodoro_end_t - self._t))
            mm, ss = divmod(remain, 60)
            phase = "专注" if self._pomodoro_phase == "work" else "休息"
            lines.append(f"番茄钟：{phase} {mm:02d}:{ss:02d}")
        else:
            lines.append("番茄钟：未运行")

        if self._click_through_enabled:
            if self._click_through_ctrl_bypass:
                lines.append("鼠标穿透：Ctrl 临时操作中")
            else:
                lines.append("鼠标穿透：按住 Ctrl 可左/右键操作")

        return "\n".join(lines)

    def _update_dashboard_tooltip(self):
        # 不再使用系统 tooltip，避免和自绘仪表盘重复显示。
        if self.toolTip():
            self.setToolTip("")
        if self._t < self._next_dashboard_update_t:
            return
        self._next_dashboard_update_t = self._t + 2.0

    def _maybe_scheduled_cleanup(self, special_active):
        if self._dnd_enabled or not self._scheduled_cleanup_enabled:
            return
        if special_active or not self.isVisible():
            return
        if self._t < self._next_scheduled_cleanup_t:
            return
        self._next_scheduled_cleanup_t = self._t + max(10, int(self._scheduled_cleanup_interval_minutes)) * 60
        self._show_message("定时清理运行内存...", "info", 1.5)
        self._start_cleanup_effect()

    def _maybe_avoid_screen_edges(self):
        if not self._auto_avoid_edge_enabled:
            return
        if self._dragging or self._edge_dock_visual_edge or self._edge_dock_target_progress > 0:
            return
        scr = self._screen_available_geometry()
        pos = self.pos()
        margin = 8
        push = 32
        nx, ny = pos.x(), pos.y()
        if self.x() - scr.left() <= margin:
            nx = scr.left() + push
        elif scr.right() - (self.x() + self.width()) <= margin:
            nx = scr.right() - self.width() - push
        if self.y() - scr.top() <= margin:
            ny = scr.top() + push
        elif scr.bottom() - (self.y() + self.height()) <= margin:
            ny = scr.bottom() - self.height() - push
        if nx != pos.x() or ny != pos.y():
            self.move(nx, ny)

    def _start_fun_action(self, name, duration=3.0, message=None, expression=None):
        if self._quantum_phase is not None or self._cleanup_phase is not None or self._speedtest_active:
            self._show_message("小猫正在忙，等一下再玩～", "info", 1.8)
            return

        if self._edge_dock_visual_edge:
            self._edge_dock_hover_reveal = True
            self._undock_from_edge()

        self._fun_action_name = str(name)
        self._fun_action_start_t = self._t
        self._fun_action_duration = max(0.8, float(duration))
        self._sink_phase = None

        if expression:
            self.state.expression = expression
        self.state.show_excl = 0.0
        self.state.show_anger = 0.0

        if message:
            self._show_message(message, "tip", min(4.0, max(1.4, duration * 0.75)))

    def _advance_fun_action(self, dt):
        name = self._fun_action_name
        if not name:
            return

        duration = max(0.1, self._fun_action_duration)
        u = (self._t - self._fun_action_start_t) / duration
        st = self.state

        if u >= 1.0:
            self._fun_action_name = None
            self._fun_action_duration = 0.0
            st.blink = 0.0
            st.look_x *= 0.5
            st.look_y *= 0.5
            st.cat_offset_x = 0.0
            st.cat_offset_y = 0.0
            st.cat_tilt_deg = 0.0
            st.rise_progress = 1.0
            if st.expression not in ("angry",):
                st.expression = "default"
            return

        if name == "pat":
            st.expression = "default"
            st.blink = max(st.blink, 0.35 + 0.35 * math.sin(self._t * 6.0) ** 2)
            st.bob += 0.025 * math.sin(self._t * 8.0)
        elif name == "teaser":
            st.expression = "teaser"
            dot_x = 1.35 * math.cos(self._t * 3.6)
            dot_y = 1.15 + 0.38 * math.sin(self._t * 5.2)
            st.look_x += (max(-1.0, min(1.0, dot_x / 1.45)) - st.look_x) * 0.35
            st.look_y += (max(-1.0, min(1.0, dot_y / 1.60)) - st.look_y) * 0.35
            st.blink = 0.0
            st.show_excl = 0.0
            st.show_anger = 0.0

        elif name == "lookup":
            st.expression = "default"
            lift = math.sin(math.pi * clamp01(u))
            st.cat_offset_y = 0.08 * lift
            st.cat_tilt_deg = -5.0 + 2.0 * math.sin(self._t * 1.8)
            st.look_x = 0.0
            st.look_y = 0.85
            st.blink = 0.0
            st.show_excl = 0.0
            st.show_anger = 0.0

        elif name == "lookdown":
            st.expression = "default"
            dip = math.sin(math.pi * clamp01(u))
            st.cat_offset_y = -0.12 * dip
            st.cat_tilt_deg = 4.0
            st.look_x = 0.0
            st.look_y = -0.85
            st.blink = 0.0
            st.show_excl = 0.0
            st.show_anger = 0.0

        elif name == "tilt":
            st.expression = "default"
            tilt = 11.0 * math.sin(math.pi * clamp01(u))
            st.cat_tilt_deg = tilt
            st.cat_offset_x = 0.04 * math.sin(self._t * 2.0)
            st.look_x = 0.30
            st.look_y = 0.05
            st.blink = max(st.blink, 0.18 * math.sin(math.pi * clamp01(u)) ** 2)
            st.show_excl = 0.0
            st.show_anger = 0.0

        elif name == "lookaround":
            st.expression = "default"
            phase = math.sin(u * math.pi * 4.0)
            st.cat_offset_x = 0.30 * phase
            st.cat_tilt_deg = -5.0 * phase
            st.look_x = max(-1.0, min(1.0, phase * 0.95))
            st.look_y = 0.04 * math.cos(u * math.pi * 2.0)
            st.blink = 0.0
            st.show_excl = 0.0
            st.show_anger = 0.0

        elif name == "nod":
            st.expression = "default"
            nod = math.sin(u * math.pi * 6.0)
            st.cat_offset_y = -0.11 * nod
            st.cat_tilt_deg = 2.2 * nod
            st.look_y = -0.10 * abs(nod)
            st.blink = max(st.blink, 0.12 * abs(nod))
            st.show_excl = 0.0
            st.show_anger = 0.0

        elif name == "shake":
            st.expression = "default"
            shake = math.sin(u * math.pi * 7.0)
            st.cat_offset_x = 0.24 * shake
            st.cat_tilt_deg = 7.5 * shake
            st.look_x = -0.55 * shake
            st.look_y = 0.0
            st.blink = 0.0
            st.show_excl = 0.0
            st.show_anger = 0.0

        elif name == "think":
            st.expression = "dazed"
            st.cat_tilt_deg = -7.0 + 2.5 * math.sin(self._t * 2.0)
            st.cat_offset_x = -0.06
            st.look_x = 0.15
            st.look_y = 0.55
            st.blink = 0.0
            st.show_excl = 0.0
            st.show_anger = 0.0

        elif name == "peek":
            st.expression = "surprise"
            wave = math.sin(u * math.pi * 4.0)
            # 半藏进盒子，只露头观察，然后慢慢回到正常高度。
            st.rise_progress = 0.62 + 0.38 * ease_smooth(u)
            st.cat_offset_x = 0.23 * wave
            st.cat_tilt_deg = -5.0 * wave
            st.look_x = max(-1.0, min(1.0, wave))
            st.look_y = 0.10
            st.blink = 0.0
            st.show_excl = 0.0
            st.show_anger = 0.0

        elif name == "startled":
            st.expression = "surprise"
            jump = math.sin(math.pi * clamp01(u))
            jitter = math.sin(self._t * 55.0) * (1.0 - clamp01(u))
            st.cat_offset_y = 0.36 * jump
            st.cat_offset_x = 0.035 * jitter
            st.cat_tilt_deg = 3.5 * jitter
            st.look_x = 0.0
            st.look_y = 0.25
            st.blink = 0.0
            st.show_excl = max(st.show_excl, 1.0 - 0.7 * clamp01(u))
            st.show_anger = 0.0

        elif name == "nuzzle":
            st.expression = "default"
            rub = math.sin(u * math.pi * 6.0)
            st.cat_offset_x = 0.18 * rub
            st.cat_offset_y = -0.04 * abs(rub)
            st.cat_tilt_deg = 5.5 * rub
            st.look_x = 0.25 * rub
            st.look_y = -0.05
            st.blink = max(st.blink, 0.28 + 0.20 * abs(rub))
            st.show_excl = 0.0
            st.show_anger = 0.0

        elif name == "napwake":
            if u < 0.58:
                st.expression = "sleep"
                st.cat_offset_y = -0.06
                st.look_x = 0.0
                st.look_y = -0.12
                st.blink = 0.0
                st.show_excl = 0.0
            else:
                w = clamp01((u - 0.58) / 0.42)
                bounce = math.sin(math.pi * w)
                st.expression = "surprise"
                st.cat_offset_y = 0.28 * bounce
                st.cat_tilt_deg = -6.0 * math.sin(math.pi * 2.0 * w) * (1.0 - w)
                st.look_x = 0.0
                st.look_y = 0.35
                st.blink = 0.0
                st.show_excl = max(st.show_excl, 1.0 - w)
            st.show_anger = 0.0

        elif name == "search":
            st.expression = "surprise"
            phase = math.sin(u * math.pi * 5.0)
            st.cat_offset_x = 0.30 * phase
            st.cat_tilt_deg = -6.0 * phase
            st.look_x = max(-1.0, min(1.0, phase))
            st.look_y = -0.12 + 0.08 * math.sin(self._t * 3.0)
            st.blink = 0.0
            st.show_excl = 0.0
            st.show_anger = 0.0

        elif name == "earwiggle":
            st.expression = "default"
            wiggle = math.sin(self._t * 28.0) * (1.0 - 0.35 * clamp01(u))
            st.cat_tilt_deg = 3.0 * wiggle
            st.cat_offset_x = 0.035 * wiggle
            st.look_x = 0.20 * math.sin(self._t * 4.0)
            st.look_y = 0.05
            st.blink = 0.0
            st.show_excl = 0.0
            st.show_anger = 0.0

        elif name == "wink":
            st.expression = "wink"
            st.blink = 0.0
            st.look_x = 0.0
            st.look_y = 0.0
            st.cat_tilt_deg = 4.0 * math.sin(math.pi * clamp01(u))
            st.show_excl = 0.0
            st.show_anger = 0.0

        elif name == "lick":
            st.expression = "lick"
            st.blink = 0.0
            st.look_x = 0.0
            st.look_y = -0.10
            st.cat_tilt_deg = -2.0 * math.sin(math.pi * clamp01(u))
            st.show_excl = 0.0
            st.show_anger = 0.0

        elif name == "happybounce":
            st.expression = "default"
            bounce = abs(math.sin(u * math.pi * 4.0))
            st.cat_offset_y = 0.18 * bounce
            st.cat_tilt_deg = 2.5 * math.sin(u * math.pi * 4.0)
            st.look_x = 0.0
            st.look_y = 0.15
            st.blink = max(st.blink, 0.12 * bounce)
            st.show_excl = 0.0
            st.show_anger = 0.0

        elif name == "purr":
            st.expression = "purr"
            st.blink = 0.0
            st.look_x = 0.0
            st.look_y = -0.06
            st.cat_offset_y = 0.025 * math.sin(self._t * 7.0)
            st.cat_tilt_deg = 2.0 * math.sin(self._t * 3.0)
            st.show_excl = 0.0
            st.show_anger = 0.0

        elif name == "yawn":
            st.expression = "yawn"
            st.blink = 0.25 + 0.65 * clamp01(u)
            st.look_x *= 0.65
            st.look_y = -0.08 * clamp01(u)
            st.show_excl = 0.0
            st.show_anger = 0.0

        elif name == "dazed":
            st.expression = "dazed"
            st.blink = 0.0
            st.look_x = 0.10 * math.sin(self._t * 0.7)
            st.look_y = -0.08 + 0.03 * math.sin(self._t * 0.5)
            st.show_excl = 0.0
            st.show_anger = 0.0

        elif name == "sleep":
            st.expression = "sleep"
            st.blink = 0.0
            st.look_x *= 0.55
            st.look_y = -0.10
            st.show_excl = 0.0
            st.show_anger = 0.0
            st.bob += 0.018 * math.sin(self._t * 2.0)

        elif name == "sneeze":
            st.expression = "sneeze"
            st.blink = 0.0
            shake = math.sin(self._t * 48.0) * (1.0 - clamp01(u))
            st.look_x = 0.0
            st.look_y = 0.0
            st.bob += 0.030 * shake
            st.show_excl = 0.0
            st.show_anger = 0.0

        elif name == "stretch":
            st.expression = "stretch"
            st.blink = 0.0
            st.look_x *= 0.65
            st.look_y = 0.08
            lift = math.sin(math.pi * clamp01(u))
            st.bob += 0.115 * lift
            st.show_excl = 0.0
            st.show_anger = 0.0

        elif name == "shy":
            st.expression = "shy"
            st.blink = 0.0
            st.look_x = -0.25 + 0.05 * math.sin(self._t * 2.2)
            st.look_y = -0.08
            st.show_excl = 0.0
            st.show_anger = 0.0

        elif name == "dizzy":
            st.expression = "dizzy"
            st.blink = 0.0
            st.look_x = 0.18 * math.sin(self._t * 7.5)
            st.look_y = 0.12 * math.cos(self._t * 6.5)
            st.bob += 0.025 * math.sin(self._t * 11.0)
            st.show_excl = 0.0
            st.show_anger = 0.0

        elif name == "sparkle":
            st.expression = "sparkle"
            st.blink = 0.0
            st.look_x = 0.0
            st.look_y = 0.0
            st.bob += 0.020 * math.sin(self._t * 5.0)
            st.show_excl = 0.0
            st.show_anger = 0.0

        elif name == "dead":
            st.expression = "dead"
            st.blink = 0.0
            st.look_x = 0.0
            st.look_y = 0.0
            st.show_excl = 0.0
            st.show_anger = 0.0

    def _fun_pat_head(self):
        self._start_fun_action("pat", 3.4, "喵～摸摸头，好舒服！", "default")

    def _fun_teaser(self):
        self._start_fun_action("teaser", 5.0, "逗猫棒启动！", "teaser")

    def _fun_lookaround(self):
        self._start_fun_action("lookaround", 4.2, "小猫左看右看...", "default")

    def _fun_lookup(self):
        self._start_fun_action("lookup", 3.4, "小猫抬头看天...", "default")

    def _fun_lookdown(self):
        self._start_fun_action("lookdown", 3.4, "小猫低头看看...", "default")

    def _fun_tilt(self):
        self._start_fun_action("tilt", 3.6, "小猫歪头卖萌。", "default")

    def _fun_nod(self):
        self._start_fun_action("nod", 2.8, "小猫点点头。", "default")

    def _fun_shake(self):
        self._start_fun_action("shake", 2.8, "小猫摇摇头。", "default")

    def _fun_think(self):
        self._start_fun_action("think", 4.0, "小猫正在思考...", "dazed")

    def _fun_peek(self):
        self._start_fun_action("peek", 4.0, "小猫偷偷观察中...", "surprise")

    def _fun_startled(self):
        self._start_fun_action("startled", 2.2, "小猫吓了一跳！", "surprise")

    def _fun_nuzzle(self):
        self._start_fun_action("nuzzle", 3.5, "小猫蹭蹭盒子～", "default")

    def _fun_napwake(self):
        self._start_fun_action("napwake", 4.5, "小猫打盹又惊醒了。", "sleep")

    def _fun_search(self):
        self._start_fun_action("search", 4.4, "小猫正在找东西...", "surprise")

    def _fun_earwiggle(self):
        self._start_fun_action("earwiggle", 2.6, "小猫耳朵抖了抖。", "default")

    def _fun_wink(self):
        self._start_fun_action("wink", 3.0, "小猫眨了一只眼。", "wink")

    def _fun_lick(self):
        self._start_fun_action("lick", 2.8, "小猫舔舔鼻子。", "lick")

    def _fun_happybounce(self):
        self._start_fun_action("happybounce", 3.4, "小猫开心蹦了一下！", "default")

    def _fun_purr(self):
        self._start_fun_action("purr", 4.0, "小猫咕噜咕噜很开心。", "purr")

    def _fun_yawn(self):
        self._start_fun_action("yawn", 3.8, "哈啊～有点困了...", "yawn")

    def _fun_dazed(self):
        self._start_fun_action("dazed", 4.0, "小猫发呆中...", "dazed")

    def _fun_sleep(self):
        self._start_fun_action("sleep", 5.2, "小猫睡着了... 呼噜～", "sleep")

    def _fun_sneeze(self):
        self._start_fun_action("sneeze", 2.6, "阿嚏！", "sneeze")

    def _fun_stretch(self):
        self._start_fun_action("stretch", 3.6, "小猫伸了个懒腰～", "stretch")

    def _fun_shy(self):
        self._start_fun_action("shy", 3.8, "小猫害羞了。", "shy")

    def _fun_dizzy(self):
        self._start_fun_action("dizzy", 3.4, "小猫转晕了...", "dizzy")

    def _fun_sparkle(self):
        self._start_fun_action("sparkle", 3.6, "小猫眼睛亮晶晶！", "sparkle")

    def _fun_play_dead(self):
        self._start_fun_action("dead", 3.2, "小猫装死中... 3、2、1！", "dead")

    def _fun_fortune(self):
        self.state.expression = random.choice(["default", "surprise"])
        self._show_message(random.choice(FORTUNE_TIPS), "tip", 4.2)

    def _fun_tell_time(self):
        lt = time.localtime()
        hh = int(lt.tm_hour)
        mm = int(lt.tm_min)
        remark = TIME_REMARKS[-1][1]
        for limit, text in TIME_REMARKS:
            if hh < limit:
                remark = text
                break
        self._show_message(f"现在是 {hh:02d}:{mm:02d}\n{remark}", "info", 4.0)

    def _fun_decision(self):
        text, ok = QInputDialog.getText(
            self,
            "抽签 / 选择困难症",
            "输入选项，用逗号、空格或换行分隔：\n例如：火锅 烧烤 面条",
        )
        if not ok:
            return
        raw = str(text).strip()
        if not raw:
            self._show_message("没有选项，小猫也选不出来～", "warn", 2.2)
            return

        parts = []
        for token in raw.replace("，", ",").replace("、", ",").replace("；", ",").replace(";", ",").replace("\n", ",").split(","):
            for sub in token.split():
                sub = sub.strip()
                if sub:
                    parts.append(sub)

        if not parts:
            self._show_message("没有有效选项，小猫选择睡觉。", "warn", 2.4)
            return

        choice = random.choice(parts)
        self.state.expression = "surprise"
        self.state.show_excl = 1.0
        self._show_message(f"小猫选：{choice}", "tip", 3.6)


    def _fun_random_action(self):
        choices = [
            self._fun_pat_head,
            self._fun_teaser,
            self._fun_lookaround,
            self._fun_lookup,
            self._fun_lookdown,
            self._fun_tilt,
            self._fun_nod,
            self._fun_shake,
            self._fun_think,
            self._fun_peek,
            self._fun_startled,
            self._fun_nuzzle,
            self._fun_napwake,
            self._fun_search,
            self._fun_earwiggle,
            self._fun_wink,
            self._fun_lick,
            self._fun_happybounce,
            self._fun_purr,
            self._fun_yawn,
            self._fun_dazed,
            self._fun_sleep,
            self._fun_sneeze,
            self._fun_stretch,
            self._fun_shy,
            self._fun_dizzy,
            self._fun_sparkle,
            self._fun_play_dead,
            self._fun_fortune,
            self._fun_tell_time,
            self.trigger_sink_pop,
            self._start_quantum_effect,
        ]
        random.choice(choices)()

    def _execute_hotkey_action(self, action):
        if action == "command_palette":
            self._open_command_palette()
        elif action == "toggle_pet":
            self.setVisible(not self.isVisible())
        elif action == "clean_memory":
            self._start_cleanup_effect()
        elif action == "speed_test":
            self._start_speedtest_effect()
        elif action == "organize_downloads":
            self._organize_downloads_action()
        elif action == "quantum":
            self._start_quantum_effect()

    def _handle_hotkeys(self):
        if not self._hotkeys_enabled or not sys.platform.startswith("win"):
            return
        if self._t < self._next_hotkey_poll_t:
            return
        self._next_hotkey_poll_t = self._t + 0.12
        for action, seq in self._hotkeys.items():
            pressed = _is_hotkey_pressed(seq)
            was = bool(self._hotkey_down_state.get(action))
            self._hotkey_down_state[action] = pressed
            if pressed and not was:
                self._execute_hotkey_action(action)

    def _tick(self):
        dt = max(0.010, min(0.060, getattr(self, "_timer_interval_ms", 25) / 1000.0))
        self._t += dt
        self._update_new_year_fireworks(dt)
        self._handle_hotkeys()
        self._update_click_through_ctrl_bypass()
        self._maybe_refresh_dashboard_metrics()
        self._update_dashboard_tooltip()

        # 小猫状态仪表盘使用自绘卡片，而不是系统 tooltip。
        # 鼠标移入后淡入，移出后淡出；收纳/穿透时不显示。
        dashboard_target = 1.0 if (
            self._mouse_inside_window
            and not self._edge_dock_visual_edge
            and not getattr(self, "_effective_click_through", False)
        ) else 0.0
        self._dashboard_opacity += (dashboard_target - self._dashboard_opacity) * 0.18
        if abs(self._dashboard_opacity - dashboard_target) < 0.015:
            self._dashboard_opacity = dashboard_target

        st = self.state
        quantum_active = self._quantum_phase is not None
        cleanup_active = self._cleanup_phase is not None
        speedtest_active = self._speedtest_active
        fun_active = self._fun_action_name is not None
        special_active = quantum_active or cleanup_active or speedtest_active or fun_active
        self._maybe_scheduled_cleanup(special_active)
        self._maybe_avoid_screen_edges()

        st.bob = 0.04 * math.sin(self._t * 1.7)
        st.cat_offset_x = 0.0
        st.cat_offset_y = 0.0
        st.cat_tilt_deg = 0.0

        cur = QCursor.pos()
        if (cur - self._last_cursor_pos).manhattanLength() >= 2:
            self._last_cursor_pos = QPoint(cur)
            self._last_cursor_move_t = self._t

        cursor_recently_moved = (self._t - self._last_cursor_move_t) <= self._gaze_idle_seconds

        if self._gaze_track and cursor_recently_moved and self.isVisible():
            head_w = self.renderer.D(*HEAD_CENTER)
            head_screen = self.mapToGlobal(
                QPoint(int(head_w.x()), int(head_w.y())))
            ddx = cur.x() - head_screen.x()
            ddy = cur.y() - head_screen.y()
            d = math.hypot(ddx, ddy)
            R_FOLLOW = 600
            if d < R_FOLLOW:
                tgt_x = max(-1.0, min(1.0, ddx / 250.0))
                tgt_y = max(-1.0, min(1.0, -ddy / 250.0))
            else:
                tgt_x = tgt_y = 0.0
            st.look_x += (tgt_x - st.look_x) * 0.12
            st.look_y += (tgt_y - st.look_y) * 0.12
        else:
            st.look_x *= 0.94
            st.look_y *= 0.94

        # 眨眼
        if self._blink_phase is None and self._t >= self._next_blink_t:
            self._blink_phase = ("down", self._t, 0.08)
        if self._blink_phase is not None:
            phase, t0, dur = self._blink_phase
            tl = self._t - t0
            if phase == "down":
                if tl >= dur:
                    self._blink_phase = ("up", self._t, 0.10)
                    st.blink = 1.0
                else:
                    st.blink = tl / dur
            else:
                if tl >= dur:
                    st.blink = 0.0
                    self._blink_phase = None
                    self._next_blink_t = self._t + random.uniform(3.0, 7.0)
                else:
                    st.blink = 1.0 - tl / dur

        self._advance_fun_action(dt)

        # 沉箱 → 跳出；网速测量复用这一段动画，并在盒内 hold 阶段后台测速。
        if (not special_active) and self._sink_phase is None and self._t >= self._next_action_t:
            self._sink_phase = ("sink", self._t, 0.55)
        if self._sink_phase is not None:
            phase, t0, dur = self._sink_phase
            tl = self._t - t0
            if phase == "sink":
                if tl >= dur:
                    self._sink_phase = ("hold", self._t, 0.35)
                    st.rise_progress = 0.0
                    if speedtest_active:
                        self._start_speedtest_worker()
                else:
                    st.rise_progress = 1.0 - (tl / dur)
            elif phase == "hold":
                st.rise_progress = 0.0
                if speedtest_active:
                    self._start_speedtest_worker()
                    # 至少沉在盒子里停一下；结果没回来时继续留在盒内。
                    if self._speedtest_result is None:
                        if tl >= 0.80:
                            self._sink_phase = ("hold", self._t, 0.35)
                    elif tl >= dur:
                        self._sink_phase = ("rise", self._t, 0.55)
                elif tl >= dur:
                    self._sink_phase = ("rise", self._t, 0.55)
            else:
                if tl >= dur:
                    st.rise_progress = 1.0
                    self._sink_phase = None
                    self._next_action_t = self._t + random.uniform(15.0, 30.0)
                    if speedtest_active:
                        self._speedtest_display_t = 0.0
                else:
                    u = tl / dur
                    st.rise_progress = 1.0 - (1.0 - u) ** 3

        if quantum_active:
            self._advance_quantum_effect(dt)
        elif cleanup_active:
            self._advance_cleanup_effect(dt)
        elif speedtest_active:
            self._advance_speedtest_effect(dt)
        else:
            fade_step = 1.125 * dt
            st.show_excl  = max(0.0, st.show_excl  - fade_step)
            st.show_anger = max(0.0, st.show_anger - fade_step)
            st.cat_scale = 1.0
            st.cleanup_phase = "none"
            st.cleanup_u = 0.0
            st.cleanup_ring_radius = 0.0
            st.cleanup_ring_opacity = 0.0
            st.cleanup_text = ""
            st.cleanup_text_opacity = 0.0

        self._drain_ui_events()
        self._advance_message(dt)
        self._advance_pomodoro()
        self._maybe_start_auto_status_check(special_active)
        self._maybe_show_birthday_effect(special_active)
        self._maybe_show_holiday_greeting_effect(special_active)
        self._maybe_show_calendar_events(special_active)
        self._maybe_show_auto_daily_tip(special_active)
        self._maybe_auto_change_expression(special_active)
        self._maybe_start_network_monitor(special_active)

        self._advance_edge_dock(dt)
        if self._settings_dialog is not None and self._settings_dialog.isVisible():
            self._settings_dialog.refresh_runtime_status()
        self.update()

    def trigger_sink_pop(self):
        if (self._quantum_phase is None
                and self._cleanup_phase is None
                and not self._speedtest_active
                and self._sink_phase is None):
            self._sink_phase = ("sink", self._t, 0.55)


    # ── v12 测量网速：复用“沉箱 → 抬起”动画 ───────────────
    def _start_speedtest_effect(self):
        if (self._quantum_phase is not None
                or self._cleanup_phase is not None
                or self._speedtest_active
                or self._sink_phase is not None):
            return

        if self._edge_dock_visual_edge:
            self._edge_dock_hover_reveal = True
            self._undock_from_edge()

        self._speedtest_active = True
        self._speedtest_result = None
        self._speedtest_worker_started = False
        self._speedtest_display_t = 0.0
        self._sink_phase = ("sink", self._t, 0.55)

        st = self.state
        st.expression = "surprise"
        st.show_excl = 1.0
        st.show_anger = 0.0
        st.cleanup_phase = "speedtest"
        st.cleanup_text = "准备测速..."
        st.cleanup_text_opacity = 1.0
        st.cleanup_ring_radius = 0.62
        st.cleanup_ring_opacity = 0.45

    def _start_speedtest_worker(self):
        if self._speedtest_worker_started:
            return
        self._speedtest_worker_started = True

        def worker():
            self._speedtest_result = measure_download_speed()

        threading.Thread(target=worker, daemon=True).start()

    def _format_speedtest_result_text(self):
        res = self._speedtest_result
        if not res:
            return "测速中..."
        if not res.get("ok"):
            return "测速失败，请检查网络"
        mbps = float(res.get("mbps", 0.0))
        mBps = float(res.get("mBps", 0.0))
        if mbps >= 100:
            return f"下载 {mbps:.0f} Mbps ({mBps:.1f} MB/s)"
        if mbps >= 10:
            return f"下载 {mbps:.1f} Mbps ({mBps:.1f} MB/s)"
        return f"下载 {mbps:.2f} Mbps ({mBps:.2f} MB/s)"

    def _advance_speedtest_effect(self, dt):
        st = self.state
        st.cleanup_phase = "speedtest"
        st.show_anger = 0.0
        st.cat_scale = 1.0

        phase = self._sink_phase[0] if self._sink_phase is not None else "done"
        if phase == "sink":
            st.expression = "surprise"
            st.show_excl = max(st.show_excl, 0.55)
            st.cleanup_text = "准备测速..."
            st.cleanup_text_opacity = 1.0
            st.cleanup_ring_radius = 0.55 + 0.10 * math.sin(self._t * 10.0)
            st.cleanup_ring_opacity = 0.45
        elif phase == "hold":
            st.expression = "surprise"
            st.show_excl = 0.0
            st.cleanup_text = "盒内测速中..." if self._speedtest_result is None else self._format_speedtest_result_text()
            st.cleanup_text_opacity = 1.0
            st.cleanup_ring_radius = 0.72 + 0.12 * math.sin(self._t * 16.0)
            st.cleanup_ring_opacity = 0.78
        elif phase == "rise":
            st.expression = "default"
            st.show_excl = 0.0
            st.cleanup_text = self._format_speedtest_result_text()
            st.cleanup_text_opacity = 1.0
            st.cleanup_ring_radius = 1.10
            st.cleanup_ring_opacity = 0.42
        else:
            self._speedtest_display_t += dt
            u = clamp01(self._speedtest_display_t / 2.2)
            st.expression = "default"
            st.show_excl = 0.0
            st.cleanup_text = self._format_speedtest_result_text()
            st.cleanup_text_opacity = 1.0 - u
            st.cleanup_ring_radius = 1.05 + 0.10 * u
            st.cleanup_ring_opacity = 0.30 * (1.0 - u)
            if u >= 1.0:
                self._finish_speedtest_effect()

    def _finish_speedtest_effect(self):
        self._speedtest_active = False
        self._speedtest_result = None
        self._speedtest_worker_started = False
        self._speedtest_display_t = 0.0
        st = self.state
        st.cleanup_phase = "none"
        st.cleanup_text = ""
        st.cleanup_text_opacity = 0.0
        st.cleanup_ring_radius = 0.0
        st.cleanup_ring_opacity = 0.0
        self._next_action_t = self._t + random.uniform(15.0, 30.0)

    # ── v15 通用提示 / 电脑状态 / 快捷工具 ─────────────────
    def _show_message(self, text, kind="info", duration=3.0, expression=None):
        self._add_message_history(text, kind)
        st = self.state
        st.message_text = str(text)
        st.message_kind = kind
        st.message_opacity = 1.0
        self._message_until_t = self._t + max(0.8, float(duration))

        if expression and self._quantum_phase is None and self._cleanup_phase is None and not self._speedtest_active:
            st.expression = expression
            if expression == "surprise":
                st.show_excl = 1.0
                st.show_anger = 0.0
            elif expression == "angry":
                st.show_anger = 1.0
                st.show_excl = 0.0

    def _advance_message(self, dt):
        st = self.state
        if not st.message_text:
            st.message_opacity = 0.0
            return

        if self._t <= self._message_until_t:
            st.message_opacity = min(1.0, st.message_opacity + dt / self._message_fade_seconds)
        else:
            st.message_opacity = max(0.0, st.message_opacity - dt / self._message_fade_seconds)
            if st.message_opacity <= 0.01:
                st.message_text = ""
                st.message_kind = "info"
                st.message_opacity = 0.0

    def _drain_ui_events(self):
        while True:
            try:
                event = self._ui_events.get_nowait()
            except queue.Empty:
                break

            kind = event[0]
            if kind == "message":
                _kind, text, msg_kind, duration = event
                self._show_message(text, msg_kind, duration)
            elif kind == "status_result":
                _kind, res, show_always = event
                self._status_checking = False
                self._handle_system_status_result(res, show_always)
            elif kind == "network_result":
                _kind, res, show_always = event
                self._network_checking = False
                self._handle_network_result(res, show_always)
            elif kind == "dashboard_status_result":
                _kind, res = event
                self._dashboard_status_checking = False
                self._last_status_text = "电脑状态：" + format_system_status_text(res)
                self.update()
            elif kind == "dashboard_network_result":
                _kind, res = event
                self._dashboard_network_checking = False
                self._network_last_text = format_network_status_text(res)
                self.update()
            elif kind == "organize_result":
                if len(event) >= 4:
                    _kind, ok, msg, moves = event
                    self._last_organize_moves = list(moves or [])
                else:
                    _kind, ok, msg = event
                self._show_message(msg, "ok" if ok else "warn", 3.0)

    def _start_system_status_check(self, show_always=True):
        if self._status_checking:
            if show_always:
                self._show_message("正在读取电脑状态...", "info", 1.2)
            return

        self._status_checking = True
        if show_always:
            self._show_message("正在读取电脑状态...", "info", 1.2)

        def worker():
            res = get_system_status()
            self._ui_events.put(("status_result", res, show_always))

        threading.Thread(target=worker, daemon=True).start()

    def _maybe_start_auto_status_check(self, special_active):
        if self._dnd_enabled or not self._status_auto_hint:
            return
        if special_active or self._status_checking or not self.isVisible():
            return
        if self._t < self._next_status_check_t:
            return
        self._next_status_check_t = self._t + 45.0
        self._start_system_status_check(show_always=False)

    def _handle_system_status_result(self, res, show_always):
        text = format_system_status_text(res)
        level = res.get("overall_level") if res else "unknown"

        if level == "bad":
            kind = "bad"
            expression = "angry"
        elif level == "warn":
            kind = "warn"
            expression = "surprise"
        else:
            kind = "ok"
            expression = None

        self._last_status_text = "电脑状态：" + text
        self._update_dashboard_tooltip()

        if show_always:
            self._show_message(text, kind, 3.8, expression)
        elif level in ("warn", "bad"):
            self._show_message(text, kind, 3.6, expression)

    def _set_expression_for_auto(self, expr):
        st = self.state
        st.expression = expr
        if expr == "surprise":
            st.show_excl = 1.0
            st.show_anger = 0.0
        elif expr == "angry":
            # 自动变成愤怒时只显示愤怒表情，不自动触发量子分裂。
            st.show_anger = 1.0
            st.show_excl = 0.0
        else:
            st.show_excl = 0.0
            st.show_anger = 0.0

    def _schedule_next_expression_change(self, delay=None):
        if delay is None:
            delay = max(10.0, float(self._expression_change_seconds))
        self._next_expression_change_t = self._t + max(5.0, float(delay))

    def _enabled_auto_fun_actions(self):
        actions = getattr(self, "_auto_fun_actions", {})
        return [
            name for name in AUTO_FUN_ACTION_LABELS
            if bool(actions.get(name, False))
        ]

    def _start_auto_fun_action(self, action_name):
        spec = AUTO_FUN_ACTION_SPECS.get(action_name)
        if not spec:
            return False
        self._start_fun_action(
            action_name,
            float(spec.get("duration", 3.0)),
            None,
            str(spec.get("expression", "default")),
        )
        return True

    def _advance_auto_expression_once(self):
        enabled_fun_actions = self._enabled_auto_fun_actions()
        fun_chance = max(0.0, min(100.0, float(getattr(self, "_auto_fun_chance_percent", 0)))) / 100.0

        if (getattr(self, "_auto_fun_enabled", False)
                and enabled_fun_actions
                and random.random() < fun_chance):
            if self._start_auto_fun_action(random.choice(enabled_fun_actions)):
                self._schedule_next_expression_change()
                return

        order = ["default", "surprise", "angry"]
        try:
            idx = order.index(self.state.expression)
        except ValueError:
            idx = -1
        self._set_expression_for_auto(order[(idx + 1) % len(order)])
        self._schedule_next_expression_change()

    def _maybe_auto_change_expression(self, special_active):
        if self._dnd_enabled or not self._auto_expression_enabled:
            return
        if self._t < self._next_expression_change_t:
            return

        # 正在执行功能 / 动画、沉箱、隐藏、边缘收纳时先延后，避免打断当前行为。
        if (special_active
                or self._sink_phase is not None
                or not self.isVisible()
                or self._edge_dock_visual_edge):
            self._schedule_next_expression_change(delay=8.0)
            return

        self._advance_auto_expression_once()

    def _show_random_tip(self):
        tip = random.choice(RANDOM_TIPS)
        self._show_message(tip, "tip", 4.2, None)

    def _schedule_next_daily_tip(self, delay=None):
        if delay is None:
            delay = random.uniform(self._daily_tip_min_seconds, self._daily_tip_max_seconds)
        self._next_daily_tip_t = self._t + max(10.0, float(delay))


    def open_calendar_dialog(self):
        if self._calendar_dialog is None:
            self._calendar_dialog = PetCalendarDialog(self)
        self._calendar_dialog.show()
        self._calendar_dialog.raise_()
        self._calendar_dialog.activateWindow()

    def open_birthday_settings(self):
        self._open_settings_panel()
        dlg = getattr(self, "_settings_dialog", None)
        if dlg is None or not hasattr(dlg, "nav"):
            return
        for row in range(dlg.nav.count()):
            item = dlg.nav.item(row)
            if item and ("个性化" in item.text()):
                dlg.nav.setCurrentRow(row)
                return

    def _greeting_slot_key(self, today, match_text):
        """当天祝福频率控制：0 表示当天只提醒一次，否则按分钟切分时间段。"""
        freq = int(getattr(self, "_greeting_frequency_minutes", 0) or 0)
        base = f"{today:%Y-%m-%d}:{match_text}"
        if freq <= 0:
            return base
        now = datetime.now()
        slot = (now.hour * 60 + now.minute) // max(1, freq)
        return f"{base}:slot{slot}"
    def _birthday_match_for_date(self, today):
        if not getattr(self, "_birthday_enabled", False):
            return ""
        if getattr(self, "_birthday_mode", "both") == "off":
            return ""
        bd = parse_solar_date_text(getattr(self, "_birthday_solar_date", ""))
        if not bd:
            return ""
        hits = []
        if self._birthday_mode in ("solar", "both") and today.month == bd.month and today.day == bd.day:
            hits.append("阳历生日")
        if self._birthday_mode in ("lunar", "both"):
            saved_lunar = self._birthday_lunar_info or solar_to_lunar_info(bd)
            self._birthday_lunar_info = saved_lunar
            today_lunar = solar_to_lunar_info(today)
            if saved_lunar and today_lunar and is_same_lunar_day(saved_lunar, today_lunar):
                hits.append("农历生日")
        return " / ".join(hits)

    def _start_birthday_fun_effect(self):
        for action_name in ("happybounce", "purr", "sparkle"):
            try:
                if hasattr(self, "_start_auto_fun_action") and self._start_auto_fun_action(action_name):
                    return True
            except Exception:
                pass
        for method_name in ("_fun_happybounce", "_fun_purr", "_fun_sparkle"):
            try:
                if hasattr(self, method_name):
                    getattr(self, method_name)()
                    return True
            except Exception:
                pass
        return False

    def _maybe_show_birthday_effect(self, special_active=False):
        if getattr(self, "_dnd_enabled", False):
            return
        if special_active or not self.isVisible():
            return
        today = date.today()
        match_text = self._birthday_match_for_date(today)
        if not match_text:
            return
        key = self._greeting_slot_key(today, f"birthday:{match_text}")
        if getattr(self, "_birthday_last_shown_key", "") == key:
            return
        self._birthday_last_shown_key = key
        self._save_user_config()
        self._show_message("生日快乐！🎂", "tip", 6.0, "default")
        self._start_birthday_fun_effect()

    def _calendar_event_slot_key(self, today, event_id):
        """事件提醒频率控制：0 表示当天只提醒一次，否则按分钟切分时间段。"""
        event = None
        for e in getattr(self, "_calendar_events", []):
            if e.get("id") == event_id:
                event = e
                break
        if not event:
            return ""
        freq = int(event.get("reminder_freq", 0) or 0)
        base = f"{today:%Y-%m-%d}:event{event_id}"
        if freq <= 0:
            return base
        now = datetime.now()
        slot = (now.hour * 60 + now.minute) // max(1, freq)
        return f"{base}:slot{slot}"

    def _maybe_show_calendar_events(self, special_active=False):
        """检查并显示今天的日历事件提醒。"""
        if getattr(self, "_dnd_enabled", False):
            return
        if special_active or not self.isVisible():
            return
        
        today = date.today()
        today_str = today.isoformat()
        events = getattr(self, "_calendar_events", [])
        need_save = False
        
        for event in events:
            if event.get("date") != today_str:
                continue
            
            event_id = event.get("id")
            key = self._calendar_event_slot_key(today, event_id)
            last_shown = event.get("last_shown_key", "")
            
            if key and key != last_shown:
                event["last_shown_key"] = key
                need_save = True
                
                title = event.get("title", "未命名")
                note = event.get("note", "")
                msg = f"📌 日历提醒：{title}"
                if note:
                    msg += f"\n{note}"
                
                self._show_message(msg, "tip", 5.0, "default")
        
        if need_save:
            self._save_user_config()



    def _start_new_year_fireworks(self, duration=5.0):
        """启动新年烟花：多层爆点、星形光芒和拖尾。"""
        self._new_year_fireworks_until_t = self._t + float(duration)
        self._new_year_fireworks = []

        colors = ["#FDE047", "#FB7185", "#60A5FA", "#34D399", "#C084FC", "#F97316", "#FFFFFF", "#A7F3D0"]
        w = max(280, self.width())
        h = max(280, self.height())

        for burst in range(9):
            cx = random.uniform(w * 0.14, w * 0.86)
            cy = random.uniform(h * 0.05, h * 0.45)
            delay = burst * 0.22
            base_color = QColor(random.choice(colors))

            count = 48
            for ring, speed_scale in enumerate((1.0, 0.58)):
                for i in range(count if ring == 0 else 24):
                    ang = (math.tau * i / (count if ring == 0 else 24)) + random.uniform(-0.08, 0.08)
                    spd = random.uniform(72.0, 170.0) * speed_scale
                    self._new_year_fireworks.append({
                        "kind": "dot",
                        "x": cx,
                        "y": cy,
                        "vx": math.cos(ang) * spd,
                        "vy": math.sin(ang) * spd,
                        "delay": delay + ring * 0.08,
                        "life": random.uniform(1.25, 2.20),
                        "age": 0.0,
                        "color": QColor(base_color if random.random() > 0.35 else QColor(random.choice(colors))),
                        "r": random.uniform(2.8, 6.2 if ring == 0 else 4.6),
                    })

            for kind, life, rr in (("flash", 0.46, 26.0), ("ring", 0.85, 34.0), ("star", 0.95, 14.0)):
                self._new_year_fireworks.append({
                    "kind": kind,
                    "x": cx,
                    "y": cy,
                    "vx": 0.0,
                    "vy": 0.0,
                    "delay": delay,
                    "life": life,
                    "age": 0.0,
                    "color": QColor("#FFFFFF" if kind == "flash" else base_color),
                    "r": random.uniform(rr * 0.75, rr * 1.25),
                })

        self.update()

    def _show_new_year_greeting_effect(self, manual=False):
        self._show_message("新年快乐", "tip", 6.0 if not manual else 5.0, "default")
        self._start_new_year_fireworks(5.4 if not manual else 4.6)
        self._start_birthday_fun_effect()
        self.update()

    def _update_new_year_fireworks(self, dt):
        if not getattr(self, "_new_year_fireworks", None):
            return

        alive = []
        for p in self._new_year_fireworks:
            if p["delay"] > 0:
                p["delay"] -= dt
                alive.append(p)
                continue

            p["age"] += dt
            if p["age"] <= p["life"]:
                if p.get("kind") == "dot":
                    p["x"] += p["vx"] * dt
                    p["y"] += p["vy"] * dt
                    p["vy"] += 42.0 * dt
                    p["vx"] *= 0.988
                    p["vy"] *= 0.988
                alive.append(p)

        self._new_year_fireworks = alive
        if alive:
            self.update()

    def _draw_new_year_fireworks(self, p):
        if not getattr(self, "_new_year_fireworks", None):
            return

        p.save()
        p.setRenderHint(QPainter.Antialiasing)

        for fw in self._new_year_fireworks:
            if fw.get("delay", 0) > 0:
                continue

            life = max(0.001, fw.get("life", 1.0))
            age = fw.get("age", 0.0)
            progress = max(0.0, min(1.0, age / life))
            alpha = max(0.0, 1.0 - progress)
            base = QColor(fw["color"])

            if fw.get("kind") == "flash":
                r0 = fw.get("r", 24.0) * (1.0 + progress * 1.9)
                col = QColor(base)
                col.setAlphaF(max(0.0, 0.46 * (1.0 - progress)))
                p.setPen(Qt.NoPen)
                p.setBrush(col)
                p.drawEllipse(QPointF(fw["x"], fw["y"]), r0, r0)
                continue

            if fw.get("kind") == "ring":
                r0 = fw.get("r", 34.0) * (0.35 + progress * 2.15)
                col = QColor(base)
                col.setAlphaF(max(0.0, 0.72 * (1.0 - progress)))
                p.setBrush(Qt.NoBrush)
                p.setPen(QPen(col, max(1.2, 3.2 * (1.0 - progress)), Qt.SolidLine, Qt.RoundCap))
                p.drawEllipse(QPointF(fw["x"], fw["y"]), r0, r0)
                continue

            if fw.get("kind") == "star":
                col = QColor(base)
                col.setAlphaF(max(0.0, 0.82 * (1.0 - progress)))
                p.setPen(QPen(col, max(1.2, 2.3 * (1.0 - progress)), Qt.SolidLine, Qt.RoundCap))
                length = fw.get("r", 14.0) * (0.8 + progress * 1.6)
                center = QPointF(fw["x"], fw["y"])
                p.drawLine(QPointF(center.x() - length, center.y()), QPointF(center.x() + length, center.y()))
                p.drawLine(QPointF(center.x(), center.y() - length), QPointF(center.x(), center.y() + length))
                p.drawLine(QPointF(center.x() - length * 0.7, center.y() - length * 0.7), QPointF(center.x() + length * 0.7, center.y() + length * 0.7))
                p.drawLine(QPointF(center.x() - length * 0.7, center.y() + length * 0.7), QPointF(center.x() + length * 0.7, center.y() - length * 0.7))
                continue

            r0 = fw.get("r", 4.0) * (0.85 + 0.65 * alpha)
            col = QColor(base)
            col.setAlphaF(min(1.0, alpha * 0.98))
            p.setPen(Qt.NoPen)
            p.setBrush(col)
            p.drawEllipse(QPointF(fw["x"], fw["y"]), r0, r0)

            tail = QColor(base)
            tail.setAlphaF(min(0.58, alpha * 0.52))
            p.setPen(QPen(tail, max(1.4, r0 * 0.62), Qt.SolidLine, Qt.RoundCap))
            p.drawLine(
                QPointF(fw["x"], fw["y"]),
                QPointF(fw["x"] - fw.get("vx", 0) * 0.06, fw["y"] - fw.get("vy", 0) * 0.06)
            )

        p.restore()


    def _maybe_show_holiday_greeting_effect(self, special_active=False):
        if getattr(self, "_dnd_enabled", False):
            return
        if special_active or not self.isVisible():
            return

        today = date.today()
        match_text = holiday_greeting_match_for_date(
            today,
            getattr(self, "_holiday_new_year_enabled", True),
            getattr(self, "_holiday_lunar_new_year_enabled", True),
        )
        if not match_text:
            return

        key = self._greeting_slot_key(today, f"holiday:{match_text}")
        if getattr(self, "_holiday_last_shown_key", "") == key:
            return

        self._holiday_last_shown_key = key
        self._save_user_config()
        self._show_new_year_greeting_effect(manual=False)


    def _maybe_show_auto_daily_tip(self, special_active):
        if self._dnd_enabled or not self._daily_tip_enabled:
            return
        if self._t < self._next_daily_tip_t:
            return

        # 正在执行动画 / 功能、隐藏到托盘、边缘收纳、已有提示时，都先延后一点。
        if (special_active
                or not self.isVisible()
                or self._edge_dock_visual_edge
                or self.state.message_text
                or self.state.message_opacity > 0.05):
            self._schedule_next_daily_tip(delay=60.0)
            return

        self._show_random_tip()
        self._schedule_next_daily_tip()

    # ── 番茄钟 / 网络监控 / 下载整理 ─────────────────────
    def pomodoro_status_text(self):
        if self._pomodoro_phase == "idle":
            return "未开始"
        remaining = max(0, int(self._pomodoro_end_t - self._t))
        mm, ss = divmod(remaining, 60)
        phase = "专注中" if self._pomodoro_phase == "work" else "休息中"
        return f"{phase}  剩余 {mm:02d}:{ss:02d}"

    def start_pomodoro(self):
        self._pomodoro_enabled = True
        self._pomodoro_phase = "work"
        self._pomodoro_end_t = self._t + max(1, int(self._pomodoro_work_minutes)) * 60
        self._show_message("番茄钟开始：专注时间", "info", 2.2, "default")
        self._save_user_config()

    def stop_pomodoro(self, show_message=True):
        self._pomodoro_phase = "idle"
        self._pomodoro_end_t = 0.0
        if show_message:
            self._show_message("番茄钟已停止", "info", 1.8)
        self._save_user_config()

    def _advance_pomodoro(self):
        if not self._pomodoro_enabled or self._pomodoro_phase == "idle":
            return
        if self._t < self._pomodoro_end_t:
            return

        if self._pomodoro_phase == "work":
            self._pomodoro_phase = "break"
            self._pomodoro_end_t = self._t + max(1, int(self._pomodoro_break_minutes)) * 60
            self._show_message("专注结束，休息一下吧", "tip", 4.0, "surprise")
        else:
            self._pomodoro_phase = "work"
            self._pomodoro_end_t = self._t + max(1, int(self._pomodoro_work_minutes)) * 60
            self._show_message("休息结束，开始下一轮专注", "info", 4.0, "default")

    def network_status_text(self):
        return self._network_last_text or "尚未检测"

    def _start_network_check(self, show_always=True):
        if self._network_checking:
            if show_always:
                self._show_message("正在检查网络...", "info", 1.2)
            return
        self._network_checking = True
        if show_always:
            self._show_message("正在检查网络...", "info", 1.2)

        def worker():
            res = check_network_status(targets=self._network_targets)
            self._ui_events.put(("network_result", res, show_always))

        threading.Thread(target=worker, daemon=True).start()

    def _maybe_start_network_monitor(self, special_active):
        if self._dnd_enabled or not self._network_monitor_enabled:
            return
        if special_active or self._network_checking or not self.isVisible():
            return
        if self._t < self._next_network_check_t:
            return
        self._next_network_check_t = self._t + max(30, int(self._network_monitor_interval_seconds))
        self._start_network_check(show_always=False)

    def _handle_network_result(self, res, show_always):
        text = format_network_status_text(res)
        online = bool(res and res.get("online"))
        level = (res or {}).get("level", "bad")
        self._network_last_text = text

        changed = (self._network_last_online is None or self._network_last_online != online)
        self._network_last_online = online

        if level == "bad":
            kind, expression = "bad", "surprise"
        elif level == "warn":
            kind, expression = "warn", None
        else:
            kind, expression = "ok", None

        if show_always or changed or level in ("warn", "bad"):
            self._show_message(text, kind, 3.2, expression)

    def _organize_downloads_action(self):
        downloads = get_downloads_folder_path(self._downloads_path)
        if self._organize_preview_enabled:
            ok, preview_msg, _moves = preview_downloads_organization(self._downloads_path, self._download_rules)
            if not ok:
                QMessageBox.warning(self, "整理预览失败", preview_msg)
                return
            ret = QMessageBox.question(
                self,
                "预览整理结果",
                preview_msg + "\n\n确定执行整理吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
        else:
            ret = QMessageBox.question(
                self,
                "整理下载文件夹",
                f"将以下文件夹中的文件移动到已有分类文件夹中，不会新建文件夹。\n\n{downloads}\n\n确定继续吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
        if ret != QMessageBox.Yes:
            return

        self._show_message("正在整理下载文件夹...", "info", 1.6)

        def worker():
            ok, msg, moves = organize_downloads_folder_with_undo(self._downloads_path, self._download_rules)
            self._ui_events.put(("organize_result", ok, msg, moves))

        threading.Thread(target=worker, daemon=True).start()

    def _start_system_screen_recording_action(self):
        """调用截图工具录屏。短延迟是为了等右键菜单完全关闭。"""
        if sys.platform.startswith("win"):
            self._show_message("正在打开截图工具录屏...", "info", 1.4)

            def trigger():
                ok, msg = open_system_screen_recording_tool()
                tip = msg
                if ok:
                    tip += "；请选择录制区域后开始"
                self._show_message(tip, "ok" if ok else "warn", 3.5)

            QTimer.singleShot(350, trigger)
            return

        ok, msg = open_system_screen_recording_tool()
        self._show_message(msg, "ok" if ok else "warn", 3.2)

    def _undo_last_organize_action(self):
        if not self._last_organize_moves:
            self._show_message("没有可撤销的整理记录", "warn", 2.0)
            return
        ret = QMessageBox.question(
            self,
            "撤销上一次整理",
            f"将尝试把 {len(self._last_organize_moves)} 个文件移回原位置。\n\n确定继续吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if ret != QMessageBox.Yes:
            return

        restored = 0
        failed = 0
        for new_path, old_path in reversed(self._last_organize_moves):
            try:
                src = Path(new_path)
                if not src.exists():
                    failed += 1
                    continue
                dst = _unique_destination_path(Path(old_path))
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), str(dst))
                restored += 1
            except Exception:
                failed += 1

        self._last_organize_moves = []
        msg = f"已撤销 {restored} 个文件"
        if failed:
            msg += f"，失败 {failed} 个"
        self._show_message(msg, "ok" if restored else "warn", 2.8)

    def _open_tool_action(self, func):
        try:
            ok, msg = func()
            self._show_message(msg, "ok" if ok else "warn", 2.4)
        except Exception as exc:
            self._show_message("打开失败：" + (str(exc) or exc.__class__.__name__), "bad", 2.8, "surprise")

    def _clean_temp_files_action(self):
        self._show_message("正在清理临时文件...", "info", 1.6)

        def worker():
            ok, msg = clean_temp_files()
            self._ui_events.put(("message", msg, "ok" if ok else "warn", 3.2))

        threading.Thread(target=worker, daemon=True).start()

    def _empty_recycle_bin_action(self):
        ret = QMessageBox.question(
            self,
            "清空回收站",
            "确定要清空回收站吗？此操作不可撤销。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if ret != QMessageBox.Yes:
            return

        self._show_message("正在清空回收站...", "warn", 1.4)

        def worker():
            ok, msg = empty_recycle_bin()
            self._ui_events.put(("message", msg, "ok" if ok else "bad", 3.0))

        threading.Thread(target=worker, daemon=True).start()


    # ── 贴边手动收纳 ─────────────────────────────────────
    def _screen_available_geometry(self):
        screen = QGuiApplication.screenAt(self.frameGeometry().center())
        if screen is None:
            screen = QGuiApplication.primaryScreen()
        return screen.availableGeometry()

    @staticmethod
    def _clamp_int(v, lo, hi):
        if lo > hi:
            return int(lo)
        return int(max(lo, min(hi, v)))

    def _nearest_screen_edge(self):
        geom = self._screen_available_geometry()
        fg = self.frameGeometry()
        distances = {
            "left": abs(fg.left() - geom.left()),
            "right": abs(fg.right() - geom.right()),
            "top": abs(fg.top() - geom.top()),
            "bottom": abs(fg.bottom() - geom.bottom()),
        }
        return min(distances, key=distances.get), min(distances.values())

    def _touching_screen_edge(self):
        """窗口实际碰到屏幕工作区边缘时返回边缘名；否则返回空字符串。"""
        geom = self._screen_available_geometry()
        fg = self.frameGeometry()
        tol = self._edge_dock_threshold_px

        hits = []
        if fg.left() <= geom.left() + tol:
            hits.append(("left", abs(fg.left() - geom.left())))
        if fg.right() >= geom.right() - tol:
            hits.append(("right", abs(fg.right() - geom.right())))
        if fg.top() <= geom.top() + tol:
            hits.append(("top", abs(fg.top() - geom.top())))
        if fg.bottom() >= geom.bottom() - tol:
            hits.append(("bottom", abs(fg.bottom() - geom.bottom())))

        if not hits:
            return ""
        return min(hits, key=lambda item: item[1])[0]

    def _cursor_inside_self(self, padding=12):
        g = self.frameGeometry().adjusted(-padding, -padding, padding, padding)
        return g.contains(QCursor.pos())

    def _dock_pos_for_edge(self, edge, hidden):
        geom = self._screen_available_geometry()
        visible = self._edge_dock_visible_px
        gap = 6
        x = self.x()
        y = self.y()

        if edge == "left":
            x = geom.left() - self.width() + visible if hidden else geom.left() + gap
            y = self._clamp_int(y, geom.top() + gap, geom.bottom() - self.height() - gap + 1)
        elif edge == "right":
            x = geom.right() - visible + 1 if hidden else geom.right() - self.width() - gap + 1
            y = self._clamp_int(y, geom.top() + gap, geom.bottom() - self.height() - gap + 1)
        elif edge == "top":
            y = geom.top() - self.height() + visible if hidden else geom.top() + gap
            x = self._clamp_int(x, geom.left() + gap, geom.right() - self.width() - gap + 1)
        elif edge == "bottom":
            y = geom.bottom() - visible + 1 if hidden else geom.bottom() - self.height() - gap + 1
            x = self._clamp_int(x, geom.left() + gap, geom.right() - self.width() - gap + 1)

        return QPoint(int(x), int(y))

    def _dock_to_edge(self, edge):
        if not self._edge_dock_enabled or not edge:
            return
        self._edge_dock_visual_edge = edge
        self._edge_dock_target_progress = 1.0
        self._edge_dock_hover_reveal = False
        self.state.dock_edge = edge
        self._remember_current_position()

    def _undock_from_edge(self):
        if not self._edge_dock_visual_edge:
            return
        self._edge_dock_target_progress = 0.0
        # 弹出动画期间忽略一次由于窗口移动造成的 leaveEvent，防止来回跳。
        self._edge_dock_reveal_ignore_leave_until = self._t + 0.42

    def _clear_edge_dock_state(self):
        self._edge_dock_visual_edge = ""
        self._edge_dock_target_progress = 0.0
        self._edge_dock_progress = 0.0
        self._edge_dock_hover_reveal = False
        self._edge_dock_suppress_hover = False
        self._edge_dock_hover_cooldown_until = 0.0
        self._edge_dock_reveal_ignore_leave_until = 0.0
        self.state.dock_edge = ""
        self.state.dock_progress = 0.0
        self._apply_current_opacity()

    def _maybe_dock_after_drag(self):
        # 已改为右键菜单手动收纳；拖动到屏幕边缘不再自动收纳。
        return False

    def _advance_edge_dock(self, dt):
        edge = self._edge_dock_visual_edge
        if not edge:
            self.state.dock_edge = ""
            self.state.dock_progress = 0.0
            self._apply_current_opacity()
            return

        if self._edge_dock_target_progress > self._edge_dock_progress:
            self._edge_dock_progress = min(1.0, self._edge_dock_progress + dt / 0.34)
        elif self._edge_dock_target_progress < self._edge_dock_progress:
            self._edge_dock_progress = max(0.0, self._edge_dock_progress - dt / 0.24)

        hidden = self._edge_dock_target_progress >= 0.5
        target = self._dock_pos_for_edge(edge, hidden=hidden)
        cur = self.pos()
        nx = cur.x() + (target.x() - cur.x()) * 0.24
        ny = cur.y() + (target.y() - cur.y()) * 0.24
        if abs(target.x() - cur.x()) <= 1 and abs(target.y() - cur.y()) <= 1:
            self.move(target)
        else:
            self.move(QPoint(int(nx), int(ny)))

        eased = ease_smooth(self._edge_dock_progress)
        self.state.dock_edge = edge
        self.state.dock_progress = eased
        self._apply_current_opacity()

        # 鼠标悬停弹出时，只在鼠标确实离开窗口后再收回；
        # 并避开弹出过程中的 enter/leave 抖动。
        if (self._edge_dock_hover_reveal
                and self._edge_dock_target_progress <= 0.0
                and self._t >= self._edge_dock_reveal_ignore_leave_until
                and not self._cursor_inside_self(padding=14)):
            self._edge_dock_hover_reveal = False
            self._edge_dock_target_progress = 1.0
            self._edge_dock_hover_cooldown_until = self._t + 0.35

        if self._edge_dock_target_progress <= 0.0 and self._edge_dock_progress <= 0.001:
            # 悬停弹出时保留贴边状态，这样鼠标离开后还能稳定收回；
            # 只有用户真正拖走时才清除贴边状态。
            if not self._edge_dock_hover_reveal:
                self._clear_edge_dock_state()


    # ── v5 清理运行内存：复用原量子动画 ─────────────────────
    def _start_cleanup_effect(self):
        """清理运行内存：复用原有“愤怒 → 分裂 → 爆散 → 坍缩到微小”动画。"""
        if (self._quantum_phase is not None
                or self._cleanup_phase is not None
                or self._speedtest_active):
            return

        self._cleanup_result = None
        self._cleanup_worker_started = False
        self._quantum_cleanup_mode = True

        # 直接进入原 v3 量子动画；不再使用 v4 自定义缩小动画。
        self._start_quantum_effect(cleanup_mode=True)

        st = self.state
        st.cleanup_phase = "quantum_cleanup"
        st.cleanup_u = 0.0
        st.cleanup_ring_radius = 0.0
        st.cleanup_ring_opacity = 0.0
        st.cleanup_text = "准备清理内存..."
        st.cleanup_text_opacity = 1.0

    def _make_cleanup_particles(self, n=90):
        model = []
        palette = ["#6BD9FF", "#86F0FF", "#5BFF8F", "#DDF7FF"]
        for _ in range(n):
            ang = random.uniform(0.0, 2 * math.pi)
            ro = random.uniform(1.05, 2.35)
            origin = (ro * math.cos(ang), -0.05 + ro * math.sin(ang) * 0.68)

            rt = random.uniform(0.02, 0.22)
            ta = random.uniform(0.0, 2 * math.pi)
            target = (rt * math.cos(ta), -0.12 + rt * math.sin(ta) * 0.55)

            model.append({
                "origin": origin,
                "target": target,
                "r": random.uniform(0.030, 0.065),
                "color": random.choice(palette),
                "phase": random.uniform(0, 2 * math.pi),
            })
        return model

    def _cleanup_particle_state(self, phase, u):
        dots = []
        eu = ease_smooth(u)
        t = self._t
        for m in self._cleanup_particles_model:
            ox, oy = m["origin"]
            tx, ty = m["target"]
            wob = 0.05 * math.sin(t * 15.0 + m["phase"])
            if phase in ("cleanup_angry", "cleanup_shrink"):
                pull = eu if phase == "cleanup_shrink" else 0.0
                x = lerp(ox, tx, pull)
                y = lerp(oy, ty, pull) + wob * (1.0 - pull)
                op = 0.58 if phase == "cleanup_angry" else 0.72 * (1.0 - 0.20 * u)
            elif phase == "cleanup_clean":
                spin = t * 7.0 + m["phase"]
                rad = 0.20 + 0.10 * math.sin(t * 5.0 + m["phase"])
                x = tx + rad * math.cos(spin)
                y = ty + rad * math.sin(spin) * 0.60
                op = 0.78
            elif phase == "cleanup_restore":
                spread = ease_out_cubic(u)
                x = lerp(tx, ox * 0.42, spread)
                y = lerp(ty, oy * 0.42, spread)
                op = 0.50 * (1.0 - u)
            elif phase == "cleanup_done":
                x, y = tx, ty
                op = 0.25 * (1.0 - u)
            else:
                continue
            dots.append(ParticleDot(
                x=x, y=y, r=m["r"], opacity=clamp01(op), color=m["color"]
            ))
        return dots

    def _start_memory_cleanup_worker(self):
        if self._cleanup_worker_started:
            return
        self._cleanup_worker_started = True

        def worker():
            try:
                result = clean_running_memory()
            except Exception as exc:
                result = {
                    "method": "failed",
                    "freed_mb": None,
                    "trimmed_processes": 0,
                    "collected_objects": 0,
                    "error": str(exc),
                }
            self._cleanup_result = result

        threading.Thread(target=worker, daemon=True).start()

    def _format_cleanup_result_text(self):
        result = self._cleanup_result or {}
        freed = result.get("freed_mb")
        trimmed = result.get("trimmed_processes", 0) or 0
        if result.get("error"):
            return "清理已尝试完成"
        if freed is not None and freed >= 1:
            return f"已释放约 {freed:.0f} MB"
        if trimmed:
            return f"已整理 {trimmed} 个进程"
        return "清理完成"

    def _set_cleanup_phase(self, phase):
        self._cleanup_phase = phase
        self._cleanup_t = 0.0
        self.state.cleanup_phase = phase
        self.state.cleanup_u = 0.0

    def _finish_cleanup_effect(self):
        st = self.state
        self._cleanup_phase = None
        self._cleanup_t = 0.0
        self._cleanup_particles_model = []
        self._cleanup_worker_started = False
        self._quantum_cleanup_mode = False

        st.expression = "default"
        st.rise_progress = 1.0
        st.cat_alpha = 1.0
        st.cat_scale = 1.0
        st.show_excl = 0.0
        st.show_anger = 0.0
        st.cleanup_phase = "none"
        st.cleanup_u = 0.0
        st.cleanup_ring_radius = 0.0
        st.cleanup_ring_opacity = 0.0
        st.cleanup_text = ""
        st.cleanup_text_opacity = 0.0
        st.particles = []
        self._next_action_t = self._t + random.uniform(15.0, 30.0)

    def _advance_cleanup_effect(self, dt):
        if self._cleanup_phase is None:
            return

        durations = {
            "cleanup_angry": 0.46,
            "cleanup_shrink": 0.92,
            "cleanup_clean": 0.70,
            "cleanup_restore": 0.72,
            "cleanup_done": 1.10,
        }
        order = [
            "cleanup_angry",
            "cleanup_shrink",
            "cleanup_clean",
            "cleanup_restore",
            "cleanup_done",
        ]

        phase = self._cleanup_phase
        dur = durations[phase]
        self._cleanup_t += dt
        u = clamp01(self._cleanup_t / dur)
        eu = ease_smooth(u)
        st = self.state

        st.cleanup_phase = phase
        st.cleanup_u = u
        st.rise_progress = 1.0
        st.cat_alpha = 1.0
        st.cat_scale = 1.0
        st.show_excl = 0.0

        if phase == "cleanup_angry":
            st.expression = "angry"
            st.cat_scale = 1.0
            st.show_anger = 1.0
            st.cleanup_text = "准备清理内存..."
            st.cleanup_text_opacity = 1.0
            st.cleanup_ring_radius = 0.72 + 0.08 * math.sin(self._t * 16.0)
            st.cleanup_ring_opacity = 0.20 + 0.30 * u
            st.particles = self._cleanup_particle_state(phase, u)

        elif phase == "cleanup_shrink":
            st.expression = "angry"
            # 这就是“愤怒 → 微小”段：猫逐步缩到箱口，粒子同步被吸入。
            st.cat_scale = lerp(1.0, 0.18, eu)
            st.show_anger = max(0.0, 1.0 - u)
            st.cleanup_text = "吸收占用中..."
            st.cleanup_text_opacity = 1.0
            st.cleanup_ring_radius = lerp(1.28, 0.34, eu)
            st.cleanup_ring_opacity = 0.70
            st.particles = self._cleanup_particle_state(phase, u)

        elif phase == "cleanup_clean":
            st.expression = "angry"
            st.cat_scale = 0.18
            st.show_anger = 0.0
            st.cleanup_text = "清理内存中..."
            st.cleanup_text_opacity = 1.0
            st.cleanup_ring_radius = 0.28 + 0.05 * math.sin(self._t * 22.0)
            st.cleanup_ring_opacity = 0.95
            st.particles = self._cleanup_particle_state(phase, u)
            self._start_memory_cleanup_worker()

            # 内存整理还没回结果时，短暂保持在“微小”状态，避免文字提前跳完成。
            if self._cleanup_result is None and self._cleanup_t >= dur:
                self._cleanup_t = dur * 0.96
                return

        elif phase == "cleanup_restore":
            st.expression = "default"
            st.cat_scale = lerp(0.18, 1.0, ease_out_cubic(u))
            st.show_anger = 0.0
            st.cleanup_text = self._format_cleanup_result_text()
            st.cleanup_text_opacity = 1.0
            st.cleanup_ring_radius = lerp(0.35, 1.15, ease_out_cubic(u))
            st.cleanup_ring_opacity = 0.55 * (1.0 - u)
            st.particles = self._cleanup_particle_state(phase, u)

        elif phase == "cleanup_done":
            st.expression = "default"
            st.cat_scale = 1.0
            st.show_anger = 0.0
            st.cleanup_text = self._format_cleanup_result_text()
            st.cleanup_text_opacity = max(0.0, 1.0 - u)
            st.cleanup_ring_radius = 0.0
            st.cleanup_ring_opacity = 0.0
            st.particles = self._cleanup_particle_state(phase, u)

        if self._cleanup_t >= dur:
            idx = order.index(phase)
            if idx >= len(order) - 1:
                self._finish_cleanup_effect()
            else:
                self._set_cleanup_phase(order[idx + 1])


    # ── v3 量子分裂 / 坍缩特效 ─────────────────────────────
    def _start_quantum_effect(self, cleanup_mode=False):
        """进入：愤怒停顿 → 生死小猫分裂 → 粒子爆散 → 坍缩回默认开心。

        cleanup_mode=True 时，同一段动画会作为“清理运行内存”的视觉效果，
        真正的清理动作在坍缩到微小/闪光阶段执行。
        """
        if self._cleanup_phase is not None or self._speedtest_active:
            return
        self._quantum_cleanup_mode = bool(cleanup_mode)
        self._sink_phase = None
        self._quantum_phase = "angry_hold"
        self._quantum_t = 0.0
        self._quantum_particles_model = self._make_quantum_particles()

        st = self.state
        st.expression = "angry"
        st.rise_progress = 1.0
        st.cat_alpha = 1.0
        st.cat_scale = 1.0
        st.show_anger = 1.0
        st.show_excl = 0.0
        if not cleanup_mode:
            st.cleanup_phase = "none"
            st.cleanup_text = ""
            st.cleanup_text_opacity = 0.0
        st.quantum_phase = "angry_hold"
        st.quantum_u = 0.0
        st.ghost_sep = 0.0
        st.ghost_opacity = 0.0
        st.flash_radius = 0.0
        st.flash_opacity = 0.0
        st.spike_opacity = 0.0
        st.particles = []

    def _make_quantum_particles(self, n=120):
        if not EFFECT_PARTICLES_ENABLED:
            return []
        model = []
        palette = ["#6BD9FF", "#86F0FF", "#5BFF8F", "#DDF7FF", "#7A4CE0"]
        for i in range(n):
            ang = 2 * math.pi * i / n + random.uniform(-0.08, 0.08)
            # 原点：猫头周围一圈
            ro = random.uniform(0.80, 1.24)
            ox = ro * math.cos(ang)
            oy = 0.02 + ro * math.sin(ang) * 0.78

            # 爆散终点：更大半径，略偏上，形成“炸开”的圆云
            rb = random.uniform(1.85, 2.95)
            bx = rb * math.cos(ang) + random.uniform(-0.12, 0.12)
            by = -0.05 + rb * math.sin(ang) * 0.76 + random.uniform(-0.12, 0.12)

            # 坍缩终点：回到箱口附近
            rt = random.uniform(0.02, 0.28)
            ta = random.uniform(0, 2 * math.pi)
            tx = rt * math.cos(ta)
            ty = -0.10 + rt * math.sin(ta) * 0.65

            model.append({
                "origin": (ox, oy),
                "burst":  (bx, by),
                "target": (tx, ty),
                "r": random.uniform(0.035, 0.075),
                "color": random.choice(palette),
                "phase": random.uniform(0, 2 * math.pi),
            })
        return model

    def _set_quantum_phase(self, phase):
        self._quantum_phase = phase
        self._quantum_t = 0.0
        self.state.quantum_phase = phase
        self.state.quantum_u = 0.0

    def _finish_quantum_effect(self):
        st = self.state
        cleanup_mode = bool(getattr(self, "_quantum_cleanup_mode", False))
        cleanup_text = self._format_cleanup_result_text() if cleanup_mode else ""

        self._quantum_phase = None
        self._quantum_t = 0.0
        self._quantum_particles_model = []

        st.expression = "default"
        st.rise_progress = 1.0
        st.cat_alpha = 1.0
        st.cat_scale = 1.0
        st.show_excl = 0.0
        st.show_anger = 0.0
        st.quantum_phase = "none"
        st.quantum_u = 0.0
        st.ghost_sep = 0.0
        st.ghost_opacity = 0.0
        st.flash_radius = 0.0
        st.flash_opacity = 0.0
        st.spike_opacity = 0.0
        st.particles = []

        if cleanup_mode:
            # 量子动画结束后只保留结果文字短暂淡出。
            self._quantum_cleanup_mode = False
            self._cleanup_phase = "cleanup_done"
            self._cleanup_t = 0.0
            self._cleanup_particles_model = []
            st.cleanup_phase = "cleanup_done"
            st.cleanup_u = 0.0
            st.cleanup_ring_radius = 0.0
            st.cleanup_ring_opacity = 0.0
            st.cleanup_text = cleanup_text
            st.cleanup_text_opacity = 1.0
        else:
            self._quantum_cleanup_mode = False
            st.cleanup_phase = "none"
            st.cleanup_text = ""
            st.cleanup_text_opacity = 0.0

        self._next_action_t = self._t + random.uniform(15.0, 30.0)

    def _particle_state_for_phase(self, phase, u):
        dots = []
        eu = ease_smooth(u)
        t = self._t
        for i, m in enumerate(self._quantum_particles_model):
            ox, oy = m["origin"]
            bx, by = m["burst"]
            tx, ty = m["target"]
            ph = m["phase"]
            r = m["r"]
            color = m["color"]

            if phase == "split":
                appear = clamp01((u * len(self._quantum_particles_model) - i) / 18.0)
                wob = 0.045 * math.sin(t * 18.0 + ph)
                x = ox * (0.86 + 0.05 * math.sin(t * 8.0 + ph))
                y = oy + wob
                op = 0.70 * appear
            elif phase == "explode":
                rush = ease_out_cubic(u)
                x = lerp(ox, bx, rush)
                y = lerp(oy, by, rush) + 0.05 * math.sin(t * 16.0 + ph) * (1.0 - u)
                op = 0.78 * (1.0 - 0.20 * u)
            elif phase == "collapse":
                pull = ease_smooth(u)
                x = lerp(bx, tx, pull)
                y = lerp(by, ty, pull)
                op = 0.82 * (1.0 - max(0.0, u - 0.82) / 0.18)
            elif phase == "restore":
                x, y = tx, ty
                op = 0.35 * (1.0 - u)
            else:
                continue

            dots.append(ParticleDot(x=x, y=y, r=r, opacity=clamp01(op), color=color))
        return dots

    def _advance_quantum_effect(self, dt):
        if self._quantum_phase is None:
            return

        durations = {
            "angry_hold": 0.72,
            "split":      1.05,
            "explode":    0.78,
            "collapse":   1.08,
            "restore":    0.58,
        }
        order = ["angry_hold", "split", "explode", "collapse", "restore"]

        phase = self._quantum_phase
        dur = durations[phase]
        self._quantum_t += dt
        u = clamp01(self._quantum_t / dur)
        eu = ease_smooth(u)

        st = self.state
        st.quantum_phase = phase
        st.quantum_u = u
        st.rise_progress = 1.0
        st.show_excl = 0.0

        cleanup_mode = bool(getattr(self, "_quantum_cleanup_mode", False))
        if cleanup_mode:
            st.cleanup_phase = "quantum_cleanup"
            st.cleanup_u = u
            st.cleanup_ring_radius = 0.0
            st.cleanup_ring_opacity = 0.0
            st.cleanup_text_opacity = 1.0
            if phase in ("angry_hold", "split"):
                st.cleanup_text = "准备清理内存..."
            elif phase == "explode":
                st.cleanup_text = "吸收占用中..."
            elif phase == "collapse":
                st.cleanup_text = "清理内存中..." if self._cleanup_result is None else self._format_cleanup_result_text()
            elif phase == "restore":
                st.cleanup_text = self._format_cleanup_result_text()

        if phase == "angry_hold":
            st.expression = "angry"
            st.cat_alpha = 1.0
            st.show_anger = max(st.show_anger, 1.0 - 0.35 * u)
            st.ghost_sep = 0.0
            st.ghost_opacity = 0.0
            st.flash_radius = 0.0
            st.flash_opacity = 0.0
            st.spike_opacity = 0.0
            st.particles = []
        elif phase == "split":
            st.expression = "angry"
            st.cat_alpha = 1.0
            st.show_anger = max(0.0, 0.65 * (1.0 - u))
            st.ghost_sep = 1.15 * eu
            st.ghost_opacity = 0.48 * eu
            st.flash_radius = 0.0
            st.flash_opacity = 0.0
            st.spike_opacity = 0.0
            st.particles = self._particle_state_for_phase(phase, u)
        elif phase == "explode":
            st.expression = "angry"
            st.cat_alpha = max(0.0, 1.0 - u ** 1.45)
            st.show_anger = 0.0
            st.ghost_sep = 1.15 + 0.18 * u
            st.ghost_opacity = 0.48 * (1.0 - u)
            st.flash_radius = 0.0
            st.flash_opacity = 0.0
            st.spike_opacity = 0.0
            st.particles = self._particle_state_for_phase(phase, u)
        elif phase == "collapse":
            st.expression = "default"
            st.cat_alpha = 0.0
            st.show_anger = 0.0
            st.ghost_sep = 0.0
            st.ghost_opacity = 0.0
            st.particles = self._particle_state_for_phase(phase, u)

            # Dirac δ 尖峰：前半段显现并收窄，后半段进入白色闪爆。
            if u < 0.70:
                st.spike_opacity = 0.18 + 0.74 * ease_smooth(u / 0.70)
                st.flash_radius = 0.0
                st.flash_opacity = 0.0
            else:
                fu = clamp01((u - 0.70) / 0.30)
                st.spike_opacity = 0.92 * (1.0 - fu)
                st.flash_radius = 0.10 + 1.55 * (fu ** 0.55)
                st.flash_opacity = 0.90 * (1.0 - fu ** 0.45)

            if cleanup_mode and u >= 0.70:
                self._start_memory_cleanup_worker()
                if self._cleanup_result is None and self._quantum_t >= dur:
                    self._quantum_t = dur * 0.96
                    return
        elif phase == "restore":
            st.expression = "default"
            st.cat_alpha = ease_out_cubic(u)
            st.show_anger = 0.0
            st.ghost_sep = 0.0
            st.ghost_opacity = 0.0
            st.spike_opacity = 0.0
            st.flash_radius = 0.95 * (1.0 - u)
            st.flash_opacity = 0.16 * (1.0 - u)
            st.particles = self._particle_state_for_phase(phase, u)

        if self._quantum_t >= dur:
            idx = order.index(phase)
            if idx >= len(order) - 1:
                self._finish_quantum_effect()
            else:
                self._set_quantum_phase(order[idx + 1])

    # ── 绘制 ───────────────────────────────────────────────
    def paintEvent(self, _ev):
        p = QPainter(self)
        self.renderer.paint(p, self.state)
        self._draw_academic_hat_theme(p)
        self._draw_fun_overlay(p)
        self._draw_dashboard_overlay(p)
        self._draw_new_year_fireworks(p)


    def _draw_academic_hat_theme(self, p):
        """持久外观主题：博士帽。与猫头同显示判定，兼容量子坍缩、沉箱、跳跃等动作。"""
        if not getattr(self, "_academic_cat_enabled", False):
            return

        st = self.state
        r = self.renderer

        cat_alpha = float(getattr(st, "cat_alpha", 1.0))
        rise_progress = float(getattr(st, "rise_progress", 1.0))
        if cat_alpha <= 0.01 or rise_progress <= 0.04:
            return

        p.save()
        p.setRenderHint(QPainter.Antialiasing, True)
        p.setOpacity(max(0.0, min(1.0, cat_alpha)))

        clip_widget_y = r.D(0, CLIP_Y).y()
        p.setClipRect(QRectF(0, 0, r.w, clip_widget_y))

        cat_scale = max(0.08, float(getattr(st, "cat_scale", 1.0)))
        if abs(cat_scale - 1.0) > 0.001:
            scale_anchor = r.D(0.0, -0.12 + st.bob * 0.20)
            p.translate(scale_anchor)
            p.scale(cat_scale, cat_scale)
            p.translate(-scale_anchor)

        cat_tilt = float(getattr(st, "cat_tilt_deg", 0.0))
        if abs(cat_tilt) > 0.001:
            tilt_anchor = r.D(0.0, st.bob)
            p.translate(tilt_anchor)
            p.rotate(cat_tilt)
            p.translate(-tilt_anchor)

        cat_dx = float(getattr(st, "cat_offset_x", 0.0))
        cat_dy = float(getattr(st, "cat_offset_y", 0.0))
        if abs(cat_dx) > 0.001 or abs(cat_dy) > 0.001:
            p.translate(r.Dlen(cat_dx), -r.Dlen(cat_dy))

        rise_dy = -(1.0 - rise_progress) * RISE_AMOUNT
        dy = rise_dy + float(getattr(st, "bob", 0.0))

        # 帽体
        top = r.D(0.0, 2.06 + dy)
        right = r.D(1.15, 1.77 + dy)
        bottom = r.D(0.0, 1.48 + dy)
        left = r.D(-1.15, 1.77 + dy)

        cap = QPainterPath()
        cap.moveTo(top)
        cap.lineTo(right)
        cap.lineTo(bottom)
        cap.lineTo(left)
        cap.closeSubpath()

        shadow = QPainterPath(cap)
        shadow.translate(0, r.Dlen(0.05))
        shadow_col = QColor("#020617")
        shadow_col.setAlpha(120)
        p.setPen(Qt.NoPen)
        p.setBrush(shadow_col)
        p.drawPath(shadow)

        p.setPen(QPen(QColor("#F8FAFC"), max(1, int(r.Dlen(0.030)))))
        p.setBrush(QColor("#0B1020"))
        p.drawPath(cap)

        p.setPen(QPen(QColor("#334155"), max(1, int(r.Dlen(0.018)))))
        p.drawLine(r.D(-1.04, 1.77 + dy), r.D(1.04, 1.77 + dy))
        # 中间竖线已移除：只保留帽面横向分割线和金扣。

        brim_rect = QRectF(r.D(-0.82, 1.43 + dy), r.D(0.82, 1.63 + dy))
        brim_shadow = QRectF(r.D(-0.82, 1.47 + dy), r.D(0.82, 1.67 + dy))
        p.setBrush(shadow_col)
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(brim_shadow, r.Dlen(0.085), r.Dlen(0.085))

        p.setBrush(QColor("#111827"))
        p.setPen(QPen(QColor("#F8FAFC"), max(1, int(r.Dlen(0.024)))))
        p.drawRoundedRect(brim_rect, r.Dlen(0.085), r.Dlen(0.085))

        # 流苏：金色只允许出现在帽面正中心的一个小固定扣上。
        # 连接绳和穗子全部使用红色系，避免再次出现浅金色长条。
        sway = 0.040 * math.sin(self._t * 4.2)
        anchor_x = 0.00
        anchor_y = 1.82 + dy

        # 更鲜艳的红色系
        red = QColor("#E61E4D")
        red_mid = QColor("#C4183E")
        red_dark = QColor("#9E1432")
        red_shadow = QColor("#5A0B1D")
        gold = QColor("#FFD700")

        # 正中间小金色固定扣：无描边、无金色路径、半径更小，只是一个扣点。
        # 使用独立的 save/restore 块，完全隔离金扣的绘制状态，防止污染
        p.save()
        anchor_pt = r.D(anchor_x, anchor_y)
        p.setPen(Qt.NoPen)
        p.setBrush(gold)
        p.drawEllipse(anchor_pt, max(2.4, r.Dlen(0.030)), max(2.4, r.Dlen(0.030)))
        p.restore()

        # 红色绳线从金扣下方略偏右开始，先沿帽面轻微弯曲，再自然下垂（更靠右、更短一些，不挡眼睛）。
        # 这里不再让任何金色笔刷/画笔参与 drawPath。
        cord_start = r.D(anchor_x + 0.15, anchor_y - 0.040)
        main_c1 = r.D(0.35 + sway * 0.10, 1.80 + dy)
        main_c2 = r.D(0.55 + sway * 0.18, 1.72 + dy)
        mid_pt = r.D(0.70 + sway * 0.28, 1.68 + dy)
        main_c3 = r.D(0.85 + sway * 0.55, 1.58 + dy)
        tassel_end_x = 0.95 + sway * 0.95
        tassel_end_y = 1.30 + dy
        end_pt = r.D(tassel_end_x, tassel_end_y)

        cord = QPainterPath()
        cord.moveTo(cord_start)
        cord.cubicTo(main_c1, main_c2, mid_pt)
        cord.cubicTo(r.D(0.80 + sway * 0.38, 1.60 + dy), main_c3, end_pt)

        # 深红外缘 + 主红主体。没有高光，没有金色描边。
        # 确保没有画刷残留，只绘制线条不填充
        p.setBrush(Qt.NoBrush)
        p.setPen(QPen(red_shadow, max(1, int(r.Dlen(0.030))), Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.drawPath(cord)
        p.setPen(QPen(red, max(1, int(r.Dlen(0.021))), Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.drawPath(cord)

        # 小束口
        collar_rect = QRectF(
            end_pt.x() - r.Dlen(0.040),
            end_pt.y() - r.Dlen(0.010),
            r.Dlen(0.080),
            r.Dlen(0.055),
        )
        p.setBrush(red_dark)
        p.setPen(QPen(red_shadow, max(1, int(r.Dlen(0.010)))))
        p.drawRoundedRect(collar_rect, r.Dlen(0.012), r.Dlen(0.012))

        # 末端穗子：只用红色系，中心更长、两侧略短（更短一些）。
        strand_specs = [
            (-0.105, 0.20, red_shadow),
            (-0.082, 0.23, red_dark),
            (-0.058, 0.26, red_mid),
            (-0.030, 0.29, red_dark),
            (0.000, 0.32, red),
            (0.030, 0.29, red_dark),
            (0.058, 0.26, red_mid),
            (0.082, 0.23, red_dark),
            (0.105, 0.20, red_shadow),
        ]
        for i, (dx, drop, col) in enumerate(strand_specs):
            local_sway = 0.010 * math.sin(self._t * 5.0 + i * 0.7)
            start = r.D(tassel_end_x + dx * 0.15, tassel_end_y - 0.014)
            end = r.D(tassel_end_x + dx + local_sway, tassel_end_y - drop)
            p.setPen(QPen(col, max(1, int(r.Dlen(0.013))), Qt.SolidLine, Qt.RoundCap))
            p.drawLine(start, end)

        p.restore()

    def set_academic_cat_enabled(self, enabled):
        self._academic_cat_enabled = bool(enabled)
        self._save_user_config()
        self.update()

    def _draw_fun_overlay(self, p):
        """右键“好玩”动作的轻量动画覆盖层。"""
        name = self._fun_action_name
        if not name:
            return

        duration = max(0.1, float(self._fun_action_duration or 0.1))
        u = clamp01((self._t - self._fun_action_start_t) / duration)
        fade = min(1.0, u / 0.15, (1.0 - u) / 0.18 if u > 0.82 else 1.0)
        if fade <= 0.01:
            return

        r = self.renderer
        p.save()
        p.setRenderHint(QPainter.Antialiasing, True)
        p.setOpacity(fade)
        if name == "pat":
            font = QFont("Microsoft YaHei", max(12, int(r.Dlen(0.36))), QFont.Bold)
            p.setFont(font)
            for i in range(6):
                phase = self._t * 2.6 + i * 0.9
                x = -1.30 + i * 0.52 + 0.08 * math.sin(phase)
                y = 1.38 + 0.40 * u + 0.10 * math.sin(phase * 1.4)
                col = QColor("#FF6FAE" if i % 2 == 0 else "#FF9FCE")
                col.setAlphaF(0.95 * fade)
                p.setPen(col)
                p.drawText(r.D(x, y), "♥")

        elif name == "teaser":
            # 逗猫棒：画一条线和一个移动小球，小猫视线会跟随。
            dot_x = 1.35 * math.cos(self._t * 3.6)
            dot_y = 1.15 + 0.38 * math.sin(self._t * 5.2)
            start = r.D(1.90, 2.35)
            dot = r.D(dot_x, dot_y)
            p.setPen(QPen(QColor("#FDE68A"), max(2, int(r.Dlen(0.045)))))
            p.drawLine(start, dot)
            p.setBrush(QColor("#FB7185"))
            p.setPen(QPen(QColor("#FFFFFF"), max(1, int(r.Dlen(0.025)))))
            rr = max(5.0, r.Dlen(0.13))
            p.drawEllipse(QRectF(dot.x() - rr, dot.y() - rr, rr * 2, rr * 2))

        elif name in ("search", "lookup", "lookdown"):
            # 观察类：只画几条视线/搜索线，不覆盖脸。
            col = QColor("#A8FFD0")
            col.setAlphaF(0.65 * fade)
            p.setPen(QPen(col, max(1, int(r.Dlen(0.03))), Qt.SolidLine, Qt.RoundCap))
            if name == "lookup":
                p.drawLine(r.D(-0.30, 1.55), r.D(-0.55, 2.05))
                p.drawLine(r.D(0.30, 1.55), r.D(0.55, 2.05))
            elif name == "lookdown":
                p.drawLine(r.D(-0.45, -0.05), r.D(-0.80, -0.45))
                p.drawLine(r.D(0.45, -0.05), r.D(0.80, -0.45))
            else:
                p.drawLine(r.D(-1.45, 0.90), r.D(-1.05, 1.03))
                p.drawLine(r.D(1.45, 0.90), r.D(1.05, 1.03))

        elif name in ("happybounce", "purr"):
            # 开心类：脸外飘心心/小光点，不贴脸。
            font = QFont("Microsoft YaHei", max(10, int(r.Dlen(0.28))), QFont.Bold)
            p.setFont(font)
            for i in range(5):
                col = QColor("#FF9FCE" if i % 2 == 0 else "#FFF3A3")
                col.setAlphaF(0.75 * fade)
                p.setPen(col)
                x = -1.30 + i * 0.65 + 0.05 * math.sin(self._t * 3 + i)
                y = 1.25 + 0.32 * u + 0.06 * math.sin(self._t * 2.5 + i)
                p.drawText(r.D(x, y), "♥" if i % 2 == 0 else "✦")

        elif name == "earwiggle":
            # 耳朵抖：耳尖外侧的抖动线。
            col = QColor("#DDEBFF")
            col.setAlphaF(0.75 * fade)
            p.setPen(QPen(col, max(1, int(r.Dlen(0.035))), Qt.SolidLine, Qt.RoundCap))
            for x in (-1.35, 1.35):
                p.drawLine(r.D(x, 1.85), r.D(x + (0.18 if x > 0 else -0.18), 2.10))
                p.drawLine(r.D(x, 1.65), r.D(x + (0.20 if x > 0 else -0.20), 1.78))

        elif name == "think":
            # 思考：头顶问号/小灯泡是环境特效，不覆盖脸。
            font = QFont("Microsoft YaHei", max(12, int(r.Dlen(0.36))), QFont.Bold)
            p.setFont(font)
            col = QColor("#DDEBFF")
            col.setAlphaF(0.85 * fade)
            p.setPen(col)
            p.drawText(r.D(0.82, 1.65 + 0.08 * math.sin(self._t * 2.0)), "?")
            p.setPen(QPen(QColor("#FDE68A"), max(2, int(r.Dlen(0.035))), Qt.SolidLine, Qt.RoundCap))
            p.setBrush(QColor("#FFF3A3"))
            c = r.D(1.25, 1.80 + 0.06 * math.sin(self._t * 2.2))
            rr = max(4.0, r.Dlen(0.09))
            p.drawEllipse(QRectF(c.x() - rr, c.y() - rr, rr * 2, rr * 2))

        elif name == "startled":
            # 吓一跳：只画头顶惊叹线。
            col = QColor("#FF6B6B")
            col.setAlphaF(0.90 * fade)
            p.setPen(QPen(col, max(2, int(r.Dlen(0.045))), Qt.SolidLine, Qt.RoundCap))
            for x in (-0.42, 0.0, 0.42):
                p.drawLine(r.D(x, 1.58), r.D(x * 1.15, 2.10))

        elif name == "peek":
            # 偷看：画两条小小观察线，脸部和升降由本体完成。
            col = QColor("#A8FFD0")
            col.setAlphaF(0.70 * fade)
            p.setPen(QPen(col, max(1, int(r.Dlen(0.035))), Qt.SolidLine, Qt.RoundCap))
            p.drawLine(r.D(-1.50, 0.95), r.D(-1.15, 1.07))
            p.drawLine(r.D(1.50, 0.95), r.D(1.15, 1.07))

        elif name == "napwake":
            # 打盹惊醒：前半段睡泡泡，后半段惊醒线。
            if u < 0.58:
                bubble_col = QColor("#DDEBFF")
                bubble_col.setAlphaF(0.62 * fade)
                p.setPen(QPen(QColor("#FFFFFF"), max(1, int(r.Dlen(0.02)))))
                p.setBrush(bubble_col)
                for i in range(2):
                    c = r.D(1.04 + 0.28 * i, 1.30 + 0.26 * i + 0.04 * math.sin(self._t * 2 + i))
                    rr = max(4.0, r.Dlen(0.08 + 0.035 * i))
                    p.drawEllipse(QRectF(c.x() - rr, c.y() - rr, rr * 2, rr * 2))
            else:
                col = QColor("#FF6B6B")
                col.setAlphaF(0.85 * fade)
                p.setPen(QPen(col, max(2, int(r.Dlen(0.04))), Qt.SolidLine, Qt.RoundCap))
                p.drawLine(r.D(0.00, 1.58), r.D(0.00, 2.05))
                p.drawLine(r.D(-0.32, 1.52), r.D(-0.50, 1.92))
                p.drawLine(r.D(0.32, 1.52), r.D(0.50, 1.92))

        elif name == "yawn":
            pass

        elif name == "sleep":
            # 睡觉：只在脸外画小睡泡泡，不贴脸。
            bubble_col = QColor("#DDEBFF")
            bubble_col.setAlphaF(0.70 * fade)
            p.setPen(QPen(QColor("#FFFFFF"), max(1, int(r.Dlen(0.025)))))
            p.setBrush(bubble_col)
            for i in range(3):
                phase = u * 2.0 + i * 0.36
                bx = 1.00 + 0.26 * i + 0.04 * math.sin(self._t * 2.0 + i)
                by = 1.25 + 0.35 * phase
                rr = max(4.0, r.Dlen(0.07 + 0.03 * i))
                p.drawEllipse(QRectF(r.D(bx, by).x() - rr, r.D(bx, by).y() - rr, rr * 2, rr * 2))

        elif name == "sneeze":
            # 打喷嚏：喷嚏线和小水滴从嘴边飞出。
            col = QColor("#DDF7FF")
            col.setAlphaF(0.85 * fade)
            p.setPen(QPen(col, max(2, int(r.Dlen(0.04))), Qt.SolidLine, Qt.RoundCap))
            origin = r.D(0.25, -0.70)
            for i, ang in enumerate([-0.45, -0.15, 0.15, 0.43]):
                length = r.Dlen(0.45 + 0.18 * i)
                end = QPointF(origin.x() + length, origin.y() + math.sin(ang) * length * 0.7)
                p.drawLine(origin, end)
            p.setPen(Qt.NoPen)
            p.setBrush(col)
            for i in range(4):
                drop = r.D(0.80 + 0.23 * i, -0.58 + 0.12 * math.sin(self._t * 8 + i))
                rr = max(2.5, r.Dlen(0.045))
                p.drawEllipse(QRectF(drop.x() - rr, drop.y() - rr, rr * 2, rr * 2))

        elif name == "stretch":
            # 伸懒腰：耳朵旁上升的拉伸线。
            col = QColor("#FDE68A")
            col.setAlphaF(0.85 * fade)
            p.setPen(QPen(col, max(2, int(r.Dlen(0.04))), Qt.SolidLine, Qt.RoundCap))
            for x in (-1.35, 1.35):
                base = 1.38 + 0.12 * math.sin(self._t * 5 + x)
                p.drawLine(r.D(x, base), r.D(x, base + 0.55))
                p.drawLine(r.D(x - 0.10, base + 0.44), r.D(x, base + 0.58))
                p.drawLine(r.D(x + 0.10, base + 0.44), r.D(x, base + 0.58))

        elif name == "shy":
            # 害羞：脸外飘一点小心心，脸上的腮红由本体表情绘制。
            font = QFont("Microsoft YaHei", max(10, int(r.Dlen(0.28))), QFont.Bold)
            p.setFont(font)
            for i in range(4):
                col = QColor("#FF9FCE")
                col.setAlphaF(0.75 * fade)
                p.setPen(col)
                x = -1.35 + i * 0.90 + 0.04 * math.sin(self._t * 3 + i)
                y = 1.15 + 0.30 * u + 0.06 * math.sin(self._t * 2.5 + i)
                p.drawText(r.D(x, y), "♥")

        elif name == "dizzy":
            # 转圈晕：头顶环绕小星星。
            col = QColor("#FFF3A3")
            col.setAlphaF(0.88 * fade)
            p.setPen(QPen(QColor("#FFFFFF"), max(1, int(r.Dlen(0.02)))))
            p.setBrush(col)
            for i in range(5):
                a = self._t * 3.2 + i * 2 * math.pi / 5
                x = 0.0 + 1.15 * math.cos(a)
                y = 1.65 + 0.24 * math.sin(a)
                path = QPainterPath()
                for k in range(10):
                    aa = math.pi / 2 + k * math.pi / 5
                    rr = r.Dlen(0.10 if k % 2 == 0 else 0.045)
                    pt = QPointF(r.D(x, y).x() + rr * math.cos(aa), r.D(x, y).y() - rr * math.sin(aa))
                    if k == 0:
                        path.moveTo(pt)
                    else:
                        path.lineTo(pt)
                path.closeSubpath()
                p.drawPath(path)

        elif name == "sparkle":
            # 星星眼：脸外再闪一点几何光，不贴脸。
            for i in range(6):
                a = i * math.pi / 3 + self._t * 0.8
                x = 1.45 * math.cos(a)
                y = 1.00 + 0.55 * math.sin(a)
                col = QColor("#FFF3A3" if i % 2 == 0 else "#A8FFD0")
                col.setAlphaF(0.85 * fade)
                p.setPen(QPen(col, max(1, int(r.Dlen(0.025))), Qt.SolidLine, Qt.RoundCap))
                c = r.D(x, y)
                s = r.Dlen(0.10 + 0.03 * math.sin(self._t * 4 + i))
                p.drawLine(QPointF(c.x() - s, c.y()), QPointF(c.x() + s, c.y()))
                p.drawLine(QPointF(c.x(), c.y() - s), QPointF(c.x(), c.y() + s))

        elif name in ("dead", "dazed"):
            pass

        p.restore()

    def _draw_dashboard_overlay(self, p):
        """鼠标悬停时显示轻量状态仪表盘。"""
        opacity = clamp01(getattr(self, "_dashboard_opacity", 0.0))
        if opacity <= 0.02:
            return
        if self._edge_dock_visual_edge or getattr(self, "_effective_click_through", False):
            return

        raw_lines = [line.strip() for line in self._build_dashboard_text().splitlines() if line.strip()]
        if not raw_lines:
            return

        p.save()
        p.setRenderHint(QPainter.Antialiasing, True)

        # 字号略降一点，避免状态卡片过大。
        font_size = max(8, int(self.renderer.Dlen(0.27)))
        font = QFont("Microsoft YaHei", font_size, QFont.Bold)
        p.setFont(font)
        fm = p.fontMetrics()

        pad_x = max(8.0, self.renderer.Dlen(0.24))
        pad_y = max(6.0, self.renderer.Dlen(0.16))
        line_h = fm.height() + max(1, int(self.renderer.Dlen(0.03)))

        max_w = max(140.0, self.width() - 18.0)
        max_text_w = max(80.0, max_w - pad_x * 2)

        def wrap_line(line):
            if fm.horizontalAdvance(line) <= max_text_w:
                return [line]

            parts = []
            current = ""
            for ch in line:
                candidate = current + ch
                if current and fm.horizontalAdvance(candidate) > max_text_w:
                    parts.append(current.rstrip())
                    current = ch.lstrip()
                else:
                    current = candidate
            if current:
                parts.append(current.rstrip())
            return parts or [line]

        lines = []
        for line in raw_lines:
            lines.extend(wrap_line(line))

        text_w = max(fm.horizontalAdvance(line) for line in lines)
        rect_w = min(max_w, text_w + pad_x * 2)
        rect_h = line_h * len(lines) + pad_y * 2

        # 水平居中，固定在顶部，保证不会像系统 tooltip 那样延迟或被系统主题吞掉。
        x = (self.width() - rect_w) / 2
        y = 8.0
        if y + rect_h > self.height() - 6:
            y = max(6.0, self.height() - rect_h - 6.0)

        rect = QRectF(x, y, rect_w, rect_h)

        bg = QColor("#111827")
        bg.setAlphaF(0.82 * opacity)
        border = QColor("#6BD9FF")
        border.setAlphaF(0.85 * opacity)
        p.setPen(QPen(border, max(1, int(self.renderer.Dlen(0.035)))))
        p.setBrush(bg)
        p.drawRoundedRect(rect, self.renderer.Dlen(0.16), self.renderer.Dlen(0.16))

        # 第一行作为主状态，稍微亮一点。
        y_text = rect.top() + pad_y + fm.ascent()
        for i, line in enumerate(lines):
            col = QColor("#FFFFFF" if i == 0 else "#DDEBFF")
            col.setAlphaF(opacity if i == 0 else 0.90 * opacity)
            p.setPen(col)
            p.drawText(QPointF(rect.left() + pad_x, y_text), line)
            y_text += line_h

        p.restore()

    # ── 鼠标交互 ────────────────────────────────────────────
    def enterEvent(self, ev):
        # 贴边收纳后不再悬停自动弹出，必须左键按下弹出键才展开。
        self._mouse_inside_window = True
        self.setToolTip("")
        self._dashboard_opacity = max(self._dashboard_opacity, 0.35)
        self._apply_current_opacity()
        self.update()

        # 鼠标悬停时立即刷新仪表盘；之后在 _tick 中按频率实时刷新。
        self._dashboard_next_status_t = 0.0
        self._dashboard_next_speed_t = 0.0
        self._dashboard_next_latency_t = 0.0
        self._maybe_refresh_dashboard_metrics()

        super().enterEvent(ev)

    def leaveEvent(self, ev):
        self._mouse_inside_window = False
        self._apply_current_opacity()
        if (self._edge_dock_visual_edge
                and self._edge_dock_hover_reveal
                and not self._dragging):
            if self._t >= self._edge_dock_reveal_ignore_leave_until:
                self._edge_dock_hover_reveal = False
                self._edge_dock_target_progress = 1.0
                self._edge_dock_hover_cooldown_until = self._t + 0.35
        super().leaveEvent(ev)

    def mousePressEvent(self, ev):
        if ev.button() == Qt.LeftButton:
            # 收纳完成后，只有左键按下弹出键才展开；悬停不会展开。
            if (self._edge_dock_visual_edge
                    and self._edge_dock_target_progress >= 1.0
                    and self._edge_dock_progress >= 0.96):
                self._edge_dock_hover_reveal = True
                self._edge_dock_suppress_hover = False
                self._undock_from_edge()
                self._edge_dock_reveal_ignore_leave_until = self._t + 0.28
                return

            if self._edge_dock_visual_edge:
                self._edge_dock_hover_reveal = False
                self._edge_dock_suppress_hover = False
                self._undock_from_edge()

            self._dragging = True
            gp = ev.globalPosition().toPoint()
            self._drag_offset = gp - self.frameGeometry().topLeft()
            self._click_start_pos = gp
        elif ev.button() == Qt.RightButton:
            self._show_menu(ev.globalPosition().toPoint())

    def mouseMoveEvent(self, ev):
        if self._dragging and (ev.buttons() & Qt.LeftButton):
            if self._edge_dock_visual_edge:
                self._clear_edge_dock_state()
                gp = ev.globalPosition().toPoint()
                self._drag_offset = QPoint(self.width() // 2, self.height() // 2)
                self._click_start_pos = gp

            # 只负责拖动；不再因为接触屏幕边缘而自动收纳。
            self.move(ev.globalPosition().toPoint() - self._drag_offset)

    def mouseReleaseEvent(self, ev):
        if ev.button() == Qt.LeftButton and self._dragging:
            self._dragging = False
            end = ev.globalPosition().toPoint()
            if (end - self._click_start_pos).manhattanLength() < 5:
                self._on_click()
            else:
                self._remember_current_position()
            self._update_click_through_ctrl_bypass()
        elif ev.button() == Qt.LeftButton:
            # 点按弹出键后释放，不立即收回；鼠标离开展开后的小猫窗口再收回。
            self._edge_dock_suppress_hover = False
            self._edge_dock_hover_cooldown_until = max(self._edge_dock_hover_cooldown_until, self._t + 0.20)
            self._update_click_through_ctrl_bypass()

    def _on_click(self):
        if (self._quantum_phase is not None
                or self._cleanup_phase is not None
                or self._speedtest_active):
            return

        if self._auto_expression_enabled:
            self._schedule_next_expression_change()

        order = ["default", "surprise", "angry"]
        idx = order.index(self.state.expression)
        new_expr = order[(idx + 1) % 3]
        self.state.expression = new_expr

        if new_expr == "surprise":
            self.state.show_excl = 1.0
        elif new_expr == "angry":
            self.state.show_anger = 1.0
            self._start_quantum_effect()
        else:
            self.state.show_excl = 0.0
            self.state.show_anger = 0.0

    # ── 右键菜单 ────────────────────────────────────────────
    def _show_menu(self, gpos):
        """右键菜单：主菜单只保留大类，具体功能放进子菜单，避免菜单过长。"""
        m = QMenu(self)

        # 高频入口放最上面。
        a_command_palette = m.addAction("命令面板")

        # 收纳到屏幕边缘是高频动作，按要求放在主菜单第二个。
        if self._edge_dock_visual_edge:
            a_edge_dock = m.addAction("从边缘弹出")
        else:
            a_edge_dock = m.addAction("收纳到屏幕边缘")
        
        # 日历放在收纳到屏幕边缘下面
        a_calendar = m.addAction("日历")

        # 好玩类，按要求放在主菜单第三个。
        fun_menu = m.addMenu("好玩")
        head_fun_menu = fun_menu.addMenu("头部动作")
        a_lookaround = head_fun_menu.addAction("左看右看")
        a_lookup = head_fun_menu.addAction("抬头看天")
        a_lookdown = head_fun_menu.addAction("低头看看")
        a_tilt = head_fun_menu.addAction("歪头卖萌")
        a_nod = head_fun_menu.addAction("点头")
        a_shake = head_fun_menu.addAction("摇头")
        a_think = head_fun_menu.addAction("思考")
        a_peek = head_fun_menu.addAction("偷看")
        a_startled = head_fun_menu.addAction("吓一跳")
        a_nuzzle = head_fun_menu.addAction("蹭盒子")
        a_napwake = head_fun_menu.addAction("打盹惊醒")
        a_search = head_fun_menu.addAction("找东西")
        a_earwiggle = head_fun_menu.addAction("耳朵抖")

        expression_fun_menu = fun_menu.addMenu("表情动作")
        a_pat_head = expression_fun_menu.addAction("摸摸头")
        a_teaser = expression_fun_menu.addAction("逗猫棒")
        a_wink = expression_fun_menu.addAction("眨一只眼")
        a_lick = expression_fun_menu.addAction("舔鼻子")
        a_happybounce = expression_fun_menu.addAction("开心蹦一下")
        a_purr = expression_fun_menu.addAction("咕噜开心")
        a_yawn = expression_fun_menu.addAction("打哈欠")
        a_dazed = expression_fun_menu.addAction("发呆")
        a_sleep = expression_fun_menu.addAction("睡觉")
        a_sneeze = expression_fun_menu.addAction("打喷嚏")
        a_stretch = expression_fun_menu.addAction("伸懒腰")
        a_shy = expression_fun_menu.addAction("害羞")
        a_dizzy = expression_fun_menu.addAction("转圈晕")
        a_sparkle = expression_fun_menu.addAction("星星眼")
        a_play_dead = expression_fun_menu.addAction("装死")
        fun_menu.addSeparator()
        a_random_fun = fun_menu.addAction("随机动作")
        a_fortune = fun_menu.addAction("今日运势")
        a_decision = fun_menu.addAction("抽签 / 选择困难症")
        a_tell_time = fun_menu.addAction("小猫报时")

        # 表情与动作合并，按要求放在主菜单第四个。
        expr_action_menu = m.addMenu("表情与动作")
        a1 = expr_action_menu.addAction("默认（微笑）")
        a2 = expr_action_menu.addAction("惊讶")
        a3 = expr_action_menu.addAction("愤怒")
        expr_action_menu.addSeparator()
        a_pop = expr_action_menu.addAction("沉箱再跳出")
        a_quantum = expr_action_menu.addAction("量子分裂 / 坍缩")

        # 电脑维护类。
        maintain_menu = m.addMenu("电脑维护")
        a_clean = maintain_menu.addAction("清理运行内存")
        a_temp_clean = maintain_menu.addAction("清理临时文件")
        a_flush_dns = maintain_menu.addAction("刷新 DNS 缓存")
        a_recycle = maintain_menu.addAction("清空回收站")

        # 网络与文件类。
        net_file_menu = m.addMenu("网络与文件")
        a_speed = net_file_menu.addAction("测量网速")
        a_network = net_file_menu.addAction("检查网络状态")
        a_organize = net_file_menu.addAction("整理下载文件夹")
        a_undo_organize = net_file_menu.addAction("撤销上一次整理")

        # 快捷工具。
        tool_actions = []
        tools_menu = m.addMenu("快捷工具")
        a_screenshot = tools_menu.addAction("系统截图")
        a_screen_record = tools_menu.addAction("系统录屏")
        a_lock_screen = tools_menu.addAction("一键锁屏")
        tools_menu.addSeparator()

        visible_tools = [x for x in self._quick_tools if x.get("show_in_menu", True)]
        if visible_tools:
            for item in visible_tools:
                name = str(item.get("name", "未命名工具")).strip() or "未命名工具"
                act = tools_menu.addAction(name)
                icon = launch_item_icon(item)
                if not icon.isNull():
                    act.setIcon(icon)
                tool_actions.append((act, dict(item)))
        else:
            empty = tools_menu.addAction("暂无快捷工具")
            empty.setEnabled(False)

        # 常用软件。
        app_actions = []
        apps_menu = m.addMenu("常用软件")
        visible_apps = [x for x in self._custom_apps if x.get("show_in_menu", True)]
        if visible_apps:
            for item in visible_apps:
                name = str(item.get("name", "未命名软件")).strip() or "未命名软件"
                act = apps_menu.addAction(name)
                icon = launch_item_icon(item)
                if not icon.isNull():
                    act.setIcon(icon)
                app_actions.append((act, dict(item)))
        else:
            empty = apps_menu.addAction("暂无常用软件")
            empty.setEnabled(False)

        # 设置与系统。
        m.addSeparator()
        a_panel = m.addAction("设置中心")

        system_menu = m.addMenu("系统")
        a_hide = system_menu.addAction("隐藏到托盘")
        a_quit = system_menu.addAction("退出")

        self._context_menu_open = True
        if self._click_through_enabled:
            self._click_through_ctrl_bypass = True
            self._set_effective_click_through(False)

        try:
            chosen = m.exec(gpos)
        finally:
            self._context_menu_open = False
            # 菜单关闭后，根据 Ctrl 是否仍按住、鼠标是否还在小猫上，恢复真实穿透状态。
            self._update_click_through_ctrl_bypass()

        if chosen is None:
            return

        for act, item in tool_actions + app_actions:
            if chosen == act:
                self._open_launch_item(item)
                return

        if chosen == a_command_palette:
            self._open_command_palette()
        elif chosen == a_calendar:
            self.open_calendar_dialog()
        elif chosen == a1:
            self.state.expression = "default"
            if self._auto_expression_enabled:
                self._schedule_next_expression_change()
        elif chosen == a2:
            self.state.expression = "surprise"
            self.state.show_excl = 1.0
            if self._auto_expression_enabled:
                self._schedule_next_expression_change()
        elif chosen == a3:
            self.state.expression = "angry"
            self.state.show_anger = 1.0
            if self._auto_expression_enabled:
                self._schedule_next_expression_change()
            self._start_quantum_effect()
        elif chosen == a_pop:
            self.trigger_sink_pop()
        elif chosen == a_quantum:
            self._start_quantum_effect()
        elif chosen == a_pat_head:
            self._fun_pat_head()
        elif chosen == a_teaser:
            self._fun_teaser()
        elif chosen == a_lookaround:
            self._fun_lookaround()
        elif chosen == a_lookup:
            self._fun_lookup()
        elif chosen == a_lookdown:
            self._fun_lookdown()
        elif chosen == a_tilt:
            self._fun_tilt()
        elif chosen == a_nod:
            self._fun_nod()
        elif chosen == a_shake:
            self._fun_shake()
        elif chosen == a_think:
            self._fun_think()
        elif chosen == a_peek:
            self._fun_peek()
        elif chosen == a_startled:
            self._fun_startled()
        elif chosen == a_nuzzle:
            self._fun_nuzzle()
        elif chosen == a_napwake:
            self._fun_napwake()
        elif chosen == a_search:
            self._fun_search()
        elif chosen == a_earwiggle:
            self._fun_earwiggle()
        elif chosen == a_wink:
            self._fun_wink()
        elif chosen == a_lick:
            self._fun_lick()
        elif chosen == a_happybounce:
            self._fun_happybounce()
        elif chosen == a_purr:
            self._fun_purr()
        elif chosen == a_yawn:
            self._fun_yawn()
        elif chosen == a_dazed:
            self._fun_dazed()
        elif chosen == a_sleep:
            self._fun_sleep()
        elif chosen == a_sneeze:
            self._fun_sneeze()
        elif chosen == a_stretch:
            self._fun_stretch()
        elif chosen == a_shy:
            self._fun_shy()
        elif chosen == a_dizzy:
            self._fun_dizzy()
        elif chosen == a_sparkle:
            self._fun_sparkle()
        elif chosen == a_play_dead:
            self._fun_play_dead()
        elif chosen == a_random_fun:
            self._fun_random_action()
        elif chosen == a_fortune:
            self._fun_fortune()
        elif chosen == a_decision:
            self._fun_decision()
        elif chosen == a_tell_time:
            self._fun_tell_time()
        elif chosen == a_edge_dock:
            if self._edge_dock_visual_edge:
                self._edge_dock_hover_reveal = True
                self._undock_from_edge()
            else:
                edge, _dist = self._nearest_screen_edge()
                self._dock_to_edge(edge)
        elif chosen == a_clean:
            self._start_cleanup_effect()
        elif chosen == a_temp_clean:
            self._clean_temp_files_action()
        elif chosen == a_flush_dns:
            self._open_tool_action(flush_dns_cache_tool)
        elif chosen == a_recycle:
            self._empty_recycle_bin_action()
        elif chosen == a_speed:
            self._start_speedtest_effect()
        elif chosen == a_network:
            self._start_network_check(show_always=True)
        elif chosen == a_organize:
            self._organize_downloads_action()
        elif chosen == a_undo_organize:
            self._undo_last_organize_action()
        elif chosen == a_panel:
            self._open_settings_panel()
        elif chosen == a_screenshot:
            self._open_tool_action(open_system_screenshot_tool)
        elif chosen == a_screen_record:
            self._start_system_screen_recording_action()
        elif chosen == a_lock_screen:
            self._open_tool_action(lock_screen_tool)
        elif chosen == a_hide:
            self.hide()
        elif chosen == a_quit:
            QApplication.quit()


# ════════════════════════════════════════════════════════════════
#  入口
# ════════════════════════════════════════════════════════════════
def main():
    install_crash_protection()
    try:
        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)
        pet = CatPet()
        pet.show()
        log_message("Application started")
        sys.exit(app.exec())
    except Exception:
        log_exception("Fatal error in main")
        raise


if __name__ == "__main__":
    main()
