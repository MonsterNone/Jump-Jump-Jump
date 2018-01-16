from time import sleep
from PIL import Image
from math import sqrt, pow
from os import system as shell

# 定义一些参数
me_color = (50, 50, 75)  # 小人的基准颜色值
k = 1.368  # 跳跃系数


# 判断颜色是否在指定颜色的指定范围内, 返回值为布尔型
# 参数说明：
#     rgb [tuple] -- images.pixel()直接的返回值
#     trgb [tuple] -- 目标颜色
#     tolerance [int] -- 像素点颜色与目标颜色三位差值绝对值之和的允许范围
def compare_color(rgb, trgb, tolerance):
    t = abs(rgb[0] - trgb[0]) + abs(rgb[1] - trgb[1]) + abs(rgb[2] - trgb[2])
    if t <= tolerance:
        return True
    else:
        return False


def get_screen_shot():
    adb_command = "adb shell screencap -p /sdcard/1.png && adb pull /sdcard/1.png"
    shell(adb_command)


# 在图像中模糊寻找指定颜色(从左向右(从下到上)),返回值为(x,y)
# 参数说明：
#     w_left, w_right, h_top, h_bottom [int] -- 指定搜索区域
#     trgb [tuple] -- 目标颜色
#     tolerance [int] -- 像素点颜色与目标颜色三位差值绝对值之和的允许范围
def find_color_from_left(w_left, w_right, h_top, h_bottom, trgb, tolerance):
    pixel = img.load()  # 加载图像

    result = (0, 0)  # 初始化结果

    flag = 0  # 结果标识

    for x in range(w_left, w_right):
        y = h_bottom
        while y > h_top:
            rgb = pixel[x, y][:3]  # 获取(x,y)处的rgb值，去除alpha通道
            if compare_color(rgb, trgb, tolerance):
                flag = 1
                result = (x, y)
                break
            y = y - 1
        if flag == 1:
            break

    # 根据找到与否返回值
    if flag == 1:
        return result
    else:
        return False


# 在图像中模糊寻找指定颜色(从右向左(从下到上)),返回值为(x,y)
# 参数说明：
#     w_left, w_right, h_top, h_bottom [int] -- 指定搜索区域
#     trgb [tuple] -- 目标颜色
#     tolerance [int] -- 像素点颜色与目标颜色三位差值绝对值之和的允许范围
def find_color_from_right(w_left, w_right, h_top, h_bottom, trgb, tolerance):
    pixel = img.load()  # 加载图像

    result = (0, 0)  # 初始化结果

    flag = 0  # 结果标识

    x = w_right

    while x > w_left:
        y = h_bottom
        while y > h_top:
            rgb = pixel[x, y][:3]  # 获取(x,y)处的rgb值，去除alpha通道
            if compare_color(rgb, trgb, tolerance):
                flag = 1
                result = (x, y)
                break
            y = y - 1
        if flag == 1:
            break
        x = x - 1

    # 根据找到与否返回值
    if flag == 1:
        return result
    else:
        return False


# 在图像中模糊寻找不同的颜色(从上到下(从左向右)),返回值为((x,y), (r, g, b))
# 参数说明：
#     w_left, w_right, h_top, h_bottom [int] -- 指定搜索区域
#     trgb [tuple] -- 背景颜色
#     tolerance [int] -- 像素点颜色与背景颜色三位差值绝对值之和的允许范围
def find_different_color(w_left, w_right, h_top, h_bottom, trgb, tolerance):
    pixel = img.load()  # 加载图像

    result = ((0, 0), (0, 0, 0))  # 初始化结果

    flag = 0  # 结果标识

    for y in range(h_top, h_bottom):
        for x in range(w_left, w_right):
            rgb = pixel[x, y][:3]  # 获取(x,y)处的rgb值，去除alpha通道
            if not compare_color(rgb, trgb, tolerance):
                flag = 1
                result = ((x, y), rgb)
                break
        if flag == 1:
            break

    # 根据找到与否返回值
    if flag == 1:
        return result
    else:
        return False


# 从左边开始找小人的位置，返回小人中心点坐标(x_center,y_center)
# 参数说明：
#     w_left, w_right, h_top, h_bottom [int] -- 指定搜索范围
#     me_tolerance [int] -- 像素点颜色与小人颜色三位差值绝对值之和的允许范围
def find_now_from_left(w_left, w_right, h_top, h_bottom, me_tolerance):
    result = (0, 0)  # 初始化结果

    # 在默认范围内寻找左端点
    left_result = find_color_from_left(w_left, w_right, h_top, h_bottom, me_color, me_tolerance)

    if left_result:
        x_left, y_center_l = left_result
        print("左端点在 ({}, {})".format(x_left, y_center_l))
    else:
        print("获取左端点失败")
        exit(0)

    # 在左端点确定的范围内寻找右端点
    w_left = int(x_left)
    w_right = int(x_left + width / 9)
    h_top = int(y_center_l - 10)
    h_bottom = int(y_center_l + 10)

    right_result = find_color_from_right(w_left, w_right, h_top, h_bottom, me_color, me_tolerance)

    if right_result:
        x_right, y_center_r = right_result
        print("右端点在 ({}, {})".format(x_right, y_center_r))
    else:
        print("获取右端点失败")
        exit(0)

    x_center = (x_left + x_right) / 2
    y_center = (y_center_l + y_center_r) / 2

    result = (x_center, y_center)

    return result


# 从右边开始找小人的位置，返回小人中心点坐标(x_center,y_center)
# 参数说明：
#     w_left, w_right, h_top, h_bottom [int] -- 指定搜索范围
#     me_tolerance [int] -- 像素点颜色与小人颜色三位差值绝对值之和的允许范围
def find_now_from_right(w_left, w_right, h_top, h_bottom, me_tolerance):
    result = (0, 0)  # 初始化结果

    # 在默认范围内寻找右端点
    right_result = find_color_from_right(w_left, w_right, h_top, h_bottom, me_color, me_tolerance)

    if right_result:
        x_right, y_center_r = right_result
        print("右端点在 ({}, {})".format(x_right, y_center_r))
    else:
        print("获取右端点失败")
        exit(0)

    # 在右端点确定的范围内寻找左端点
    w_right = int(x_right)
    w_left = int(x_right - width / 9)
    h_top = int(y_center_r - 10)
    h_bottom = int(y_center_r + 10)

    left_result = find_color_from_left(w_left, w_right, h_top, h_bottom, me_color, me_tolerance)

    if left_result:
        x_left, y_center_l = left_result
        print("左端点在 ({}, {})".format(x_left, y_center_l))
    else:
        print("获取左端点失败")
        exit(0)

    x_center = (x_left + x_right) / 2
    y_center = (y_center_l + y_center_r) / 2

    result = (x_center, y_center)

    return result


# 获取下一跳位置，返回下一跳坐标(x,y)
def get_next():
    back_tolerance = 48  # 背景颜色允许范围
    next_tolerance = 8  # 下一跳方块颜色允许范围

    # 获取背景颜色
    back_x = width - 20  # 背景颜色的取色点
    back_y = int(height * 2 / 5)  # 背景颜色的取色点
    back_color = img.load()[back_x, back_y][:3]  # 获取背景rgb值，去除alpha通道

    print("背景颜色为 {}，取色点 ({},{})".format(back_color, back_x, back_y))

    result = (0, 0)  # 初始化结果

    # 定义查找范围
    w_left = int(width / 5)
    w_right = int(width * 4 / 5)
    h_top = int(height / 3)
    h_bottom = int(height / 2)

    # 获取下一跳的顶点坐标和颜色
    top_result = find_different_color(w_left, w_right, h_top, h_bottom, back_color, back_tolerance)

    if top_result:
        next_top_x = top_result[0][0]
        next_top_y = top_result[0][1]
        next_color = top_result[1]
    else:
        print("获取下一跳顶点失败")
        exit(0)

    # 小人头高于下一跳顶点
    top_tolerance = 28
    me_top_color = (55, 55, 65)
    while compare_color(next_color, me_top_color, top_tolerance):
        top_result = find_different_color(w_left, w_right, next_top_y + 1, h_bottom, back_color, back_tolerance)

        if top_result:
            next_top_x = top_result[0][0]
            next_top_y = top_result[0][1]
            next_color = top_result[1]
        else:
            print("获取下一跳顶点失败")
            exit(0)

    # 圆形
    if compare_color(img.load()[next_top_x + 1, next_top_y], next_color, 20):
        result = find_color_from_right(next_top_x, next_top_x + int(width / 36), next_top_y - 1, next_top_y, next_color,
                                       20)

        if result:
            next_top_x = int((next_top_x + result[0]) / 2)
        else:
            print("获取圆形顶部最右失败")
            exit(0)

    print("下一跳顶点在 ({},{})，颜色为{}".format(next_top_x, next_top_y, next_color))

    # 根据顶点获取下一跳最低点坐标
    w_left = next_top_x
    w_right = next_top_x + 1
    h_top = int(next_top_y + height / 45)
    h_bottom = int(next_top_y + height / 6)

    bottom_result = find_different_color(w_left, w_right, h_top, h_bottom, next_color, next_tolerance)

    if top_result:
        next_bottom_x = bottom_result[0][0]
        next_bottom_y = bottom_result[0][1]
        next_bottom_color = bottom_result[1]
    else:
        print("获取下一跳最低点失败")
        exit(0)

    # 如果中心白点
    next_center_color = (245, 245, 245)
    while next_bottom_color == next_center_color:
        bottom_result = find_different_color(w_left, w_right, next_bottom_y + 1, h_bottom, next_color, next_tolerance)

        if top_result:
            next_bottom_x = bottom_result[0][0]
            next_bottom_y = bottom_result[0][1]
            next_bottom_color = bottom_result[1]
        else:
            print("获取下一跳最低点失败")
            exit(0)

    print("下一跳最低点点在 ({},{})".format(next_bottom_x, next_bottom_y))

    next_center_x = (next_top_x + next_bottom_x) / 2
    next_center_y = (next_top_y + next_bottom_y) / 2
    result = (next_center_x, next_center_y)

    print("下一跳中心点在 ({},{})".format(next_center_x, next_center_y))

    return result


# 获取当前小人位置，返回小人坐标(x,y)
# 参数说明：
#     method ["left"/"right"] -- 从左/右开始寻找
def get_now(method):
    me_tolerance = 16  # 颜色偏差允许范围

    result = (0, 0)  # 初始化结果

    # 定义查找范围
    w_left = int(width / 8)
    w_right = int(width * 7 / 8)
    h_top = int(height / 4)
    h_bottom = int(height * 3 / 4)

    if method == "left":
        x_center, y_center = find_now_from_left(w_left, w_right, h_top, h_bottom, me_tolerance)
    elif method == "right":
        x_center, y_center = find_now_from_right(w_left, w_right, h_top, h_bottom, me_tolerance)
    else:
        print("获取小人位置method参数错误")
        exit(1)

    result = (x_center, y_center)

    print("小人中心点在 ({},{})".format(x_center, y_center))
    return result


# 利用adb开始跳起来
# 参数说明：
#     now [tuple] -- 小人当前中心点
#     next_jump [tuple] -- 下一跳中心点
def jump(now, next_jump):
    distance_x = abs(now[0] - next_jump[0])
    distance_y = abs(now[1] - next_jump[1])
    distance = sqrt(pow(distance_x, 2) + pow(distance_y, 2))  # 要跳跃的距离
    millisecond = distance * k
    millisecond = round(millisecond)

    adb_command = "adb shell input swipe {} {} {} {} {}".format(now[0], now[1], now[0] + 10, now[1] + 10,
                                                                millisecond)
    if shell(adb_command) != 0:
        print("adb swipe执行失败")
        exit(0)


for i in range(100):
    get_screen_shot()

    img = Image.open("1.png")

    # 获取屏幕分辨率
    width = img.size[0]
    height = img.size[1]

    next_jump = get_next()

    # 根据下一跳顶点位置优化小人寻找方式
    if next_jump[0] > width / 2:
        now_method = "left"
    else:
        now_method = "right"

    print(now_method)
    now = get_now(now_method)

    jump(now, next_jump)
    print("等待1.5秒")
    sleep(1.5)
