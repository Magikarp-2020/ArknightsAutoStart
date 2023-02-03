import time
import os
import random
import subprocess
import logging
import cv2

# 获取脚本所在目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 生成路径方法


def generate_path(*args):
    return os.path.join(BASE_DIR, *args)


SCREENSHOT_PATH = generate_path('buffer/_screenshot.png')

# 地图开始任务
MAP_START_PATH = generate_path('resources/map_start.png')
READED_MAP_START = cv2.imread(MAP_START_PATH)

# 队伍开始任务
TEAM_START_PATH = generate_path('resources/team_start.png')
READED_TEAM_START = cv2.imread(TEAM_START_PATH)

# 任务成功
MISSING_RESULTS_PATH = generate_path('resources/missing_results.png')
READED_MISSING_RESULTS = cv2.imread(MISSING_RESULTS_PATH)

# 补充理智
REPLENISH_PATH = generate_path('resources/replenish.png')
READED_REPLENISH = cv2.imread(REPLENISH_PATH)

# 石头
STONE_PATH = generate_path('resources/stone.png')
READED_STONE = cv2.imread(STONE_PATH)

# 确定
CONFIRM_PATH = generate_path('resources/confirm.png')
READED_CONFIRM = cv2.imread(CONFIRM_PATH)

# 取消
CANCEL_PATH = generate_path('resources/cancel.png')
READED_CANCEL = cv2.imread(CANCEL_PATH)

globalRunTimes = 0
globalReplenishTimes = 0


def get_phone_screenshot():
    logging.info('开始获取手机屏幕')
    process = subprocess.Popen(
        'adb shell screencap -p', shell=True, stdout=subprocess.PIPE)
    binary_screenshot = process.stdout.read()
    logging.info('手机屏幕获取完成')

    if (len(binary_screenshot) < 1000):
        logging.error('获取手机屏幕失败')
        raise Exception('获取手机屏幕失败，请检查 adb 连接')

    logging.info('开始存储手机屏幕')
    f = open(SCREENSHOT_PATH, 'wb')
    f.write(binary_screenshot)
    f.close()
    time.sleep(0.5)
    logging.info('手机屏幕存储完成')


def find_button(target, template, debugger=False):
    result = cv2.matchTemplate(target, template, cv2.TM_CCOEFF_NORMED)
    (min_val, max_val, min_loc, max_loc) = cv2.minMaxLoc(result)

    (startX, startY) = max_loc
    endX = startX + template.shape[1]
    endY = startY + template.shape[0]
    # 输出 min_val
    logging.info('min_val: %s, max_val: %s', min_val, max_val)
    if (max_val < 0.94):
        logging.warn('未找到对应按钮')
        return None

    cv2.rectangle(target, (startX, startY), (endX, endY), (0, 0, 255), 3)

    if (debugger):
        cv2.imshow('result__'+str(min_val), target)
        cv2.waitKey()

    return (
        (startX, startY),
        (endX, endY)
    )


def find_and_click_button(template, key, outerClickX=0, outerClickY=0, clickDelayTime=0.5):
    get_phone_screenshot()
    logging.info('获取手机屏幕方法结束')

    logging.info('开始对比图片')

    logging.info('开始寻找 %s', key)

    startButtonResult = find_button(cv2.imread(SCREENSHOT_PATH), template)

    logging.info('开始寻找按钮 [%s]，结果为: %s', key, startButtonResult)

    if (startButtonResult):
        logging.info('开始点击 %s', key)
        clickX = outerClickX or random.randint(
            startButtonResult[0][0], startButtonResult[1][0])
        clickY = outerClickY or random.randint(
            startButtonResult[0][1], startButtonResult[1][1])

        logging.info('clickX: %s, clickY: %s', clickX, clickY)

        click_cmd = 'adb shell input tap %s %s' % (clickX, clickY)

        logging.info('click_cmd: %s', click_cmd)
        # 点击开始行动按钮
        time.sleep(clickDelayTime)

        logging.info('clickDelayTime: %s', clickDelayTime)

        subprocess.call(click_cmd, shell=True)
        logging.info('点击 %s 结束', key)

        return True
    else:
        logging.warn('未找到 %s', key)

        return False


def click_map_start():
    return find_and_click_button(READED_MAP_START, 'READED_MAP_START_BUTTON')


def click_team_start():
    return find_and_click_button(READED_TEAM_START, 'READED_TEAM_START_BUTTON')


def click_replenish():
    return find_and_click_button(READED_REPLENISH, 'READED_REPLENISH')


def click_confirm():
    return find_and_click_button(READED_CONFIRM, 'READED_CONFIRM')


def click_cancel():
    return find_and_click_button(READED_CANCEL, 'READED_CANCEL')


def start_replenish(maxReplenishTimes=0, useStone=False):
    readedScreenshot = cv2.imread(SCREENSHOT_PATH)
    replenishResult = find_button(readedScreenshot, READED_REPLENISH)
    global globalReplenishTimes

    if (replenishResult):
        canReplenish = globalReplenishTimes <= maxReplenishTimes

        logging.info('进入理智补充判断，当前已补充次数: %s，最大补充次数：%s，当前能否补充：%s',
                     globalReplenishTimes, maxReplenishTimes, canReplenish)

        # 判断是否达到最大次数
        if (canReplenish):
            logging.info('开始补充理智')
            if (find_button(readedScreenshot, READED_STONE) and not useStone):
                logging.info('当前使用石头补充，但未开启石头补充选项，关闭理智补充页面')
                return False

            # 点击确定
            replenishStatus = do_wait_finish(click_confirm, 10, 1, 3)

            if (replenishStatus):
                logging.info('补充理智成功，关闭理智补充页面')
                globalReplenishTimes += 1
                # 确定是否在理智补充页面
                if (find_button(cv2.imread(SCREENSHOT_PATH), READED_REPLENISH)):
                    # 点击取消
                    if (do_wait_finish(click_cancel, 10, 1, 3)):
                        logging.info('关闭理智补充页面成功')
                        return True
                    else:
                        logging.info('关闭理智补充页面失败')
                        return False
                else:
                    logging.warn('未知错误，当前已离开理智补充页面，当做正常逻辑处理')
                    return True
            else:
                logging.info('未知错误，点击确定补充理智失败')
                return False
        else:
            logging.info('已达到最大补充次数，不再补充理智')
            return False
    else:
        logging.info('未找到理智补充按钮')
        return False


def click_missing_result():
    # 假设是 720P 屏幕，获取 X, Y
    x = random.randint(200, 1080)
    y = random.randint(200, 500)

    return find_and_click_button(READED_MISSING_RESULTS, 'READED_TEAM_START_BUTTON', x, y, random.randint(3, 10))


def do_wait_finish(startFunc, totalTime: int, min: int, max: int):
    isSuccess = False

    # 已经运行的时长
    runTime = 0

    while (runTime <= totalTime):
        sleep_time = round(random.uniform(min, max), 2)
        logging.info('sleep time, %s', sleep_time)
        runTime += sleep_time
        logging.info('runTime: %s', runTime)
        time.sleep(sleep_time)
        if (startFunc()):
            isSuccess = True
            break

    logging.info('do_wait_finish complete; runTime: %s, status: %s',
                 runTime, isSuccess)

    return isSuccess


def main(**params):
    # 补充理智次数
    maxReplenishTimes = params.pop('maxReplenishTimes', 0)
    # 是否使用石头
    useStone = params.pop('useStone', False)
    global globalRunTimes

    logging.info('start click map start')
    mapStartStatus = click_map_start()

    if (not mapStartStatus):
        logging.info('当前非地图页面，结束程序')
        return None

    timeStartStatus = do_wait_finish(click_team_start, 10, 1, 3)

    logging.info('timeStartStatus: %s', timeStartStatus)

    if (not timeStartStatus):
        logging.info('开始补充理智判断')
        # 是否为补充理智页面
        if (start_replenish(maxReplenishTimes, useStone)):
            main(params)
            return None
        else:
            logging.info('当前非补充理智页面，结束程序')
            return None

    logging.info('wait complete and click missing results')

    # 最多等待 5 分钟，每 1 - 3 秒检查一次
    checkMissingResultStatus = do_wait_finish(
        click_missing_result, 5 * 60, 1, 3)
    logging.info('checkMissingResultStatus: %s', checkMissingResultStatus)

    if (not checkMissingResultStatus):
        return None

    nextSleepTime = random.randint(10, 15)
    globalRunTimes += 1

    logging.info('globalRunTimes %s', globalRunTimes)

    logging.info(
        'checkMissingResultStatus!! continue, nextSleepTime: %s', nextSleepTime)

    # 任务完成会有动画，等待 10-15 秒
    time.sleep(nextSleepTime)

    main()


print('start')

# 更改日志显示级别
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S',
)
main(maxReplenishTimes=0, useStone=False)

# get_phone_screenshot()

# find_button(cv2.imread('./buffer/_screenshot.png'), READED_REPLENISH, True)
