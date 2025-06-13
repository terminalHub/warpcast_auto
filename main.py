import csv
import json
import os
import time
from io import StringIO

import adbutils
import pygetwindow as gw
import uiautomator2 as u2
import win32gui

import Id_manager as idManager
import config.config as config
import constant.ImgPathConstant as ImgPathConstant
from tools import OpenCVTools

'''
     思路分析
         启动三个实例
         对窗口进行排序
         每个放入多线程中进行执行任务，三个线程任务结束后在继续往队列中放入任务
     '''


def window_arr():
    """
    对当前窗口进行排序
    :return:
    """
    # 获取当前打开的所有窗口
    all_windows = gw.getWindowsWithTitle('雷电模拟器')
    sorted_windows = sorted(all_windows, key=lambda w: w.title.split('-')[1], reverse=False)
    default_x = 0
    for window in sorted_windows:
        if '雷电模拟器' not in window.title:
            continue
        print(window.title)
        window.moveTo(default_x, 0)
        default_x += 640


# 从配置文件读取上次处理到的行号
def load_progress():
    if not os.path.exists(config.CONFIG_FILE):
        return 0
    with open(config.CONFIG_FILE, "r") as f:
        return json.load(f).get("current_line", 0)
def screen_swipe(swipe_pixels = 600, duration=0.2):
    """
        android滑动屏幕
    :param swipe_pixels: 像素个数
    :param duration:动作完成时间
    :return:
    """
    width, height = d.window_size()
    # 起点：屏幕中间
    start_x = width // 2
    start_y = height // 2
    # 终点：向上滑动300像素
    end_x = start_x
    end_y = start_y - swipe_pixels
    d.drag(start_x, start_y, end_x, end_y, duration=duration)

if __name__ == '__main__':
    start_index = load_progress()
    bs = idManager.list_instances()
    reader = list(csv.reader(StringIO(bs.strip())))
    for i in range(start_index, len(reader)):
        print(f"雷电模拟器-{i}")
        row = reader[i]
        dnplayer_id = int(row[0])
        # dnplayer_id = 1
        launch_results = idManager.launch_instance(dnplayer_id)
        if launch_results.returncode != 0:
            # 启动命令失败
            continue
        poll_count = 1
        while not (device_list := adbutils.adb.device_list()):
            pass
        device = device_list[0]
        # for device in device_list:
            # t= device.app_start(config.WARPCAST_PACKAGE_NAME)
        d = u2.connect(device.serial)
        d.app_start(config.WARPCAST_PACKAGE_NAME)
        # if current_app["package"] == "com.example.app":
        d(description="following").wait(timeout=20)
        current_app = device.app_current()
        if config.WARPCAST_PACKAGE_NAME != current_app.package:
            idManager.stop_instance(dnplayer_id)
            print(f"warpcast启动失败...")
            continue
        # c = d.dump_hierarchy()
        while True:
            time.sleep(1)
            cur_x, cur_y = OpenCVTools.find_target_img(ImgPathConstant.HOME_THUMBS_UP)
            if None not in [cur_x, cur_y]:
                break
            # 向下滑动
            screen_swipe()
        h = win32gui.FindWindow(None, row[1])
        # 坐标映射 win2andiron
        android_x, android_y = OpenCVTools.win_to_android(cur_x, cur_y, h)
        d.click(android_x, android_y)
        time.sleep(2)
        device.app_stop(config.WARPCAST_PACKAGE_NAME)
        idManager.stop_instance(dnplayer_id)

