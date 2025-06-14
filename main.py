import csv
import json
import os
import time
from datetime import datetime
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


def screen_swipe(d, swipe_pixels=600, duration=0.2):
    """
        android滑动屏幕
    :param d:
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

def try_start_instance_with_retry(dnplayer_id, max_retry=3, wait_secs=15):
    """
    尝试拉起雷电实例
        重试机制
    :param dnplayer_id:
    :param max_retry:
    :param wait_secs:
    :return:
    """
    device_list = []
    for attempt in range(max_retry):
        for wait in range(wait_secs):
            time.sleep(1)
            device_list = adbutils.adb.device_list()
            if device_list:
                print(f"✅ 第 {attempt + 1} 次重试中，第 {wait + 1} 秒连接成功")
                return device_list  # 成功
        # 本轮尝试失败，准备重启实例
        print(f"🔄 启动失败，shell_start_雷电重试第 {attempt + 1} 次：", device_list[dnplayer_id] if dnplayer_id < len(device_list) else "无")
        idManager.stop_instance(dnplayer_id)
        idManager.launch_instance(dnplayer_id)
    return []  # 所有重试失败
def try_start_warpcast_app(d, max_retry=3, wait_timeout=20):
    for attempt in range(max_retry):
        print(f"🚀 启动 warpcast 第 {attempt + 1} 次尝试...")
        d.app_start(config.WARPCAST_PACKAGE_NAME)
        if d(description="following").wait(timeout=wait_timeout):
            current_app = d.app_current()
            if current_app.get('package') == config.WARPCAST_PACKAGE_NAME:
                print("✅ warpcast 启动成功")
                return True
        print(f"🔄 warpcast 启动失败（尝试 {attempt + 1}/{max_retry}）")
    return False  # 所有尝试失败



def click_win_to_andrion(target_image, d, row):
    while True:
        time.sleep(1)
        cur_x, cur_y = OpenCVTools.find_target_img(target_image)
        if None not in [cur_x, cur_y]:
            break
        # 向下滑动
        screen_swipe(d)
    h = win32gui.FindWindow(None, row[1])
    # 坐标映射 win2andiron
    android_x, android_y = OpenCVTools.win_to_android(cur_x, cur_y, h)
    d.click(android_x, android_y)


def warpcast_daily_activity():
    """
    warpcast 日活跃
    :return:
    """
    start_time = datetime.now()
    print("🏃‍♀️ 程序开始时间:", start_time.strftime("%Y-%m-%d %H:%M:%S"))
    start_index = load_progress()
    bs = idManager.list_instances()
    reader = list(csv.reader(StringIO(bs.strip())))
    for i in range(start_index, len(reader)):
        print(f"雷电模拟器-{i}")
        row = reader[i]
        dnplayer_id = int(row[0])
        launch_results = idManager.launch_instance(dnplayer_id)
        if launch_results.returncode != 0:
            # 启动命令失败
            continue

        device_list =  try_start_instance_with_retry(dnplayer_id)
        device = device_list[0]
        print(device)
        try:
            d = u2.connect(device.serial)
            print(f"✅ Connected to device: {device.serial}")
        except Exception as e:
            print(f"❌ Failed to connect to device {device.serial}: {e}")
            idManager.stop_instance(dnplayer_id)
            continue
        try_start_warpcast_app(d, max_retry=3, wait_timeout=20)
        click_win_to_andrion(ImgPathConstant.HOME_THUMBS_UP, d, row)
        click_win_to_andrion(ImgPathConstant.HOME_fllow, d, row)
        time.sleep(1)
        device.app_stop(config.WARPCAST_PACKAGE_NAME)
        idManager.stop_instance(dnplayer_id)
    end_time = datetime.now()
    print("🚶‍♀️ 程序结束时间:", end_time.strftime("%Y-%m-%d %H:%M:%S"))
    duration = end_time - start_time
    print(f"总耗时：{duration}（天 时:分:秒.微秒）")


if __name__ == '__main__':
    warpcast_daily_activity()
