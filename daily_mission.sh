#!/bin/bash

# ================= 配置区域 (请修改这里) =================

# 1. 项目所在的绝对路径 (在终端输入 pwd 可以查看)
PROJECT_DIR="/Users/renzhiyuan/Projects/python/Open-AutoGLM"

# 2. Python 的绝对路径 (非常重要！)
# 在你的 Conda 环境下输入 `which python` 获取
PYTHON_EXEC="/opt/anaconda3/envs/python3.11/bin/python"

# 3. ADB 的绝对路径
# 在终端输入 `which adb` 获取，通常是这个，如果不是请修改
ADB_EXEC="/opt/homebrew/bin/adb" # 或者 /opt/homebrew/bin/adb

# 4. 设置环境变量 (连接你的本地 Ollama)
# export OPENAI_API_BASE="https://ollama.edulearn.cn/v1"
# export OPENAI_API_KEY="rrrrrzy"

# =======================================================

# 进入项目目录
cd "$PROJECT_DIR" || exit

echo "[$(date)] 开始执行每日任务..." #>> run.log

# 1. 唤醒手机 (防止黑屏无法操作)
# 模拟按下电源键唤醒
"$ADB_EXEC" shell input keyevent 224
sleep 2
# 模拟上滑解锁 (参数：x1 y1 x2 y2 持续时间ms)
"$ADB_EXEC" shell input swipe 500 1500 500 500 300
sleep 2

# 2. 执行 AutoGLM
# 使用绝对路径的 Python 运行 main.py
# "$PYTHON_EXEC" main.py \
#     --model "hf.co/mradermacher/AutoGLM-Phone-9B-GGUF:Q8_0" \
#     "打开网易云音乐并播放每日推荐" >> run.log 2>&1
"$PYTHON_EXEC" main.py \
    --base-url https://open.bigmodel.cn/api/paas/v4 --model "autoglm-phone" --apikey "REMOVED_KEY \
    "步骤1：打开米游社，进入原神频道，点击签到福利
    步骤2：如果打开时就**没有**右上角显示红点的卡片，说明**不需要再签到了**，直接进入步骤5
    步骤3：点击右上角有红点的卡片图标，完成每日签到
    步骤4：签完后你需要重复确认，是否还存在有红点的卡片，如果还有，说明签到失败，需要重试；
    步骤5：最后，请把手机返回到桌面。" \
    >> run.log 2>&1

# 用 adb 结束米游社进程

# adb 锁定屏幕

echo "[$(date)] 任务结束" >> run.log