import time
import random
import subprocess
import logging
import cv2

SCREENSHOT_PATH = 'buffer/_screenshot.png'

# 地图开始任务
MAP_START_BUTTON_PATH = 'resources/map_start.png'
READED_MAP_START_BUTTON = cv2.imread(MAP_START_BUTTON_PATH)

# 队伍开始任务
TEAM_START_BUTTON_PATH = 'resources/team_start.png'
READED_TEAM_START_BUTTON = cv2.imread(TEAM_START_BUTTON_PATH)

# 任务成功
MISSING_RESULTS_BUTTON_PATH = 'resources/missing_results.png'
READED_MISSING_RESULTS_BUTTON = cv2.imread(MISSING_RESULTS_BUTTON_PATH)


def get_phone_screenshot():
    logging.info('开始获取手机屏幕')
    process = subprocess.Popen(
        'adb shell screencap -p', shell=True, stdout=subprocess.PIPE)
    binary_screenshot = process.stdout.read()
    logging.info('手机屏幕获取完成')

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
    if (max_val < 0.99):
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

    logging.info('寻找开始行动按钮结束，结果为: %s', startButtonResult)

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
    return find_and_click_button(READED_MAP_START_BUTTON, 'READED_MAP_START_BUTTON')


def click_team_start():
    return find_and_click_button(READED_TEAM_START_BUTTON, 'READED_TEAM_START_BUTTON')


def click_missing_result():
    # 假设是 720P 屏幕，获取 X, Y
    x = random.randint(200, 1080)
    y = random.randint(200, 500)

    return find_and_click_button(READED_MISSING_RESULTS_BUTTON, 'READED_TEAM_START_BUTTON', x, y, random.randint(3, 10))


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


globalRunTime = 0


def main():
    logging.info('start click map start')
    mapStartStatus = click_map_start()

    if (not mapStartStatus):
        return None

    logging.info('start click team start')

    timeStartStatus = do_wait_finish(click_team_start, 10, 1, 3)

    logging.info('timeStartStatus: %s', timeStartStatus)

    if (not timeStartStatus):
        return None

    logging.info('wait complete and click missing results')

    # 最多等待 5 分钟，每 1 - 3 秒检查一次
    checkMissingResultStatus = do_wait_finish(
        click_missing_result, 5 * 60, 1, 3)
    logging.info('checkMissingResultStatus: %s', checkMissingResultStatus)

    if (not checkMissingResultStatus):
        return None

    nextSleepTime = random.randint(10, 15)
    globalRunTime += 1

    logging.info('globalRunTime %s', globalRunTime)

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
main()
