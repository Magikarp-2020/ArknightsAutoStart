# ArknightsAutoStart

明日方舟自动点击开始脚本。

通过 python openCV & adb 获取手机屏幕从而实现自动战斗的目的。

只支持自动点击开始，暂不支持理智药、换班等。

TODO:

- [x] 自动使用理智药，未经测试，慎用

# Usage

本项目需要使用到 adb，请确认已安装

```bash
adb devices
```

需要使用 python3 & opencv

```bash
pip install opencv-python
```

```bash
python main.py
```
