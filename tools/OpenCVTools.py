import random
import time

import cv2
import pyautogui
import win32gui

from bo.OpenCvBo import *


def capture_one_third_screen_pyautogui(part=1,cut_number = 1):
    """
    part: 1, 2 或 3，表示截取屏幕的第几部分
    按屏幕宽度划分三块，纵向全高
    """
    screen_w, screen_h = pyautogui.size()
    third_w = screen_w // cut_number

    left = (part - 1) * third_w
    top = 0
    width = third_w
    height = screen_h
    return pyautogui.screenshot(region=(left, top, width, height))
def find_target_img(target_image,part=1,cut_number = 1, confidence=0.8):
    """
    匹配图像
    :param cut_number:
    :param part:
    :param confidence:
    :param target_image: 目标图像路径
    :return:
        success:
                        | 参数名       | 含义               |
            | --------- | ------------------------ |
            | `min_val` | 图像中的最小像素值（minimum value） |
            | `max_val` | 图像中的最大像素值（maximum value） |
            | `min_loc` | 最小值的坐标（tuple: `(x, y)`）  |
            | `max_loc` | 最大值的坐标（tuple: `(x, y)`）  |
        failed:None
    """
    # 截取屏幕
    screenshot = capture_one_third_screen_pyautogui(part=part, cut_number=cut_number)
    # 转换为OpenCV格式（BGR）
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    # 读取目标图片
    template = cv2.imread(target_image, cv2.IMREAD_UNCHANGED)
    # 模板匹配
    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    # 获取匹配区域的位置
    image_matching_result = Cv2MinMaxLocBo(template, *cv2.minMaxLoc(result))
    if image_matching_result.max_val >= confidence:
        # print(f"找到匹配区域，置信度: {max_val:.2f}")
        # 计算中心点坐标
        h, w = image_matching_result.img_template.shape[:2]
        center_x = image_matching_result.max_loc[0] + w // 2
        center_y = image_matching_result.max_loc[1] + h // 2
        return center_x, center_y
    else:
        return None, None


def find_target_img_and_click(target_image=None, coordinate=None, text=None, double_click=False):
    """
    匹配图像并点击
    :param coordinate: 点击坐标
    :param double_click: 点击方式
    :param target_image:目标图像路径
    :param text:填写文本
    :return:
    """
    if target_image is not None:
        center_x, center_y = find_target_img(target_image)
    else:
        center_x, center_y = coordinate
    if center_x is not None and center_y is not None:
        # 判断是否匹配成功
        # 移动鼠标并点击
        pyautogui.moveTo(center_x, center_y, duration=0.1 + random.random() * 0.3)
        # pyautogui.moveTo(center_x, center_y, duration=0.2)
        # 点击方式
        if double_click:
            pyautogui.doubleClick(center_x, center_y)
        else:
            pyautogui.click(center_x, center_y)
        if text is not None:
            # 等待短暂时间（避免误操作）
            time.sleep(1)
            # 输入内容
            pyautogui.write(text, interval=0.05)
        return True
    else:
        return False

def get_window_rect(hwnd):
    rect = win32gui.GetClientRect(hwnd)  # 客户区大小 (width, height)
    left_top = win32gui.ClientToScreen(hwnd, (0, 0))  # 左上角在屏幕的位置
    width = rect[2] - rect[0]
    height = rect[3] - rect[1]
    return left_top[0], left_top[1], width, height

def win_to_android(x_win, y_win, hwnd, android_res=(1080, 1920)):
    """
    将windows坐标转换成andiron坐标
    :param x_win:
    :param y_win:
    :param hwnd:
    :param android_res:
    :return:
    """
    win_left, win_top, win_w, win_h = get_window_rect(hwnd)

    # 相对于客户区的坐标
    local_x = x_win - win_left
    local_y = y_win - win_top

    # 映射到安卓坐标（按比例缩放）
    android_x = int(local_x / win_w * android_res[0])
    android_y = int(local_y / win_h * android_res[1])

    return android_x, android_y
