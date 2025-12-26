# Phone Agent UI Module

图形化用户界面模块，用于 Phone Agent AI 手机自动化工具。

## 功能特性 (Features)

- **设置管理**: 配置 API 端点、模型名称、API 密钥等
- **任务执行**: 输入任务描述并执行
- **默认提示词**: 保存常用任务描述
- **定时执行**: 支持按设置的时间间隔自动执行任务
- **多设备支持**: 支持 Android (ADB)、HarmonyOS (HDC)、iOS 设备
- **持久化设置**: 自动保存和加载用户配置

## 安装 (Installation)

```bash
pip install PyQt6
```

或者安装完整依赖：

```bash
pip install -r requirements.txt
```

## 使用方法 (Usage)

### 启动 UI 模式

```bash
python main.py --ui
```

### UI 界面说明

1. **设置区域 (Settings)**
   - Base URL: 模型 API 地址
   - Model: 模型名称
   - API Key: API 密钥（显示为密码）
   - Max Steps: 最大执行步数
   - Language: 系统提示语言 (cn/en)
   - Device Type: 设备类型 (adb/hdc/ios)
   - Device ID: 设备 ID（留空自动检测）
   - WDA URL: iOS 设备的 WebDriverAgent 地址

2. **任务区域 (Task)**
   - 默认提示词: 设置默认任务描述
   - 当前任务: 输入要执行的任务
   - 执行任务按钮: 点击执行任务

3. **定时执行 (Scheduled Execution)**
   - 启用定时执行: 勾选后启动定时器
   - 间隔: 设置任务执行间隔（分钟）

4. **输出区域 (Output)**
   - 显示任务执行日志和结果
   - 清空输出按钮: 清除输出内容

### 使用流程

1. 启动 UI：`python main.py --ui`
2. 配置设置（首次使用）
3. 点击"保存设置"按钮
4. 输入任务描述或使用默认提示词
5. 点击"执行任务"
6. 查看输出区域的执行结果

### 定时任务

1. 在"默认提示词"中输入要定时执行的任务
2. 设置执行间隔（分钟）
3. 勾选"启用定时执行"
4. 系统将按设置的间隔自动执行任务

## 模块结构 (Module Structure)

```
ui/
├── __init__.py          # 模块初始化
├── main_window.py       # 主窗口实现
├── settings.py          # 设置管理器
├── scheduler.py         # 定时任务调度器
└── README.md           # 本文档
```

## 技术实现 (Technical Details)

- **PyQt6**: 图形界面框架
- **QSettings**: 持久化存储用户配置
- **QTimer**: 定时任务调度
- **QThread**: 多线程执行，防止 UI 冻结

## 示例 (Examples)

### 1. 基础使用

```bash
# 启动 UI
python main.py --ui

# 在 UI 中配置：
# Base URL: http://localhost:8000/v1
# Model: autoglm-phone-9b
# Task: 打开微信并发送消息给张三：今天开会时间改到下午3点
```

### 2. iOS 设备

```bash
# 启动 UI
python main.py --ui

# 在 UI 中配置：
# Device Type: ios
# WDA URL: http://localhost:8100
# Task: Open Safari and search for Python tutorials
```

### 3. 定时任务

```bash
# 启动 UI
python main.py --ui

# 在 UI 中配置：
# 默认提示词: 检查微信未读消息
# 间隔: 30 分钟
# 勾选"启用定时执行"
```

## 注意事项 (Notes)

1. 首次使用需要配置设置并保存
2. 定时任务将使用"默认提示词"或"当前任务"中的内容
3. 任务执行期间按钮会被禁用，防止重复执行
4. 设置会自动保存到本地，下次启动时自动加载
5. 关闭窗口时会自动停止定时任务

## 故障排除 (Troubleshooting)

### PyQt6 未安装

```
Error: PyQt6 is not installed.
Please install it using: pip install PyQt6
```

**解决方法**: 运行 `pip install PyQt6`

### 任务执行失败

检查输出区域的错误信息，确保：
- API 地址正确且可访问
- 设备已连接并授权
- 模型名称正确

### 定时任务不执行

确保：
- 已勾选"启用定时执行"
- 间隔时间设置合理（>= 1 分钟）
- "默认提示词"或"当前任务"中有内容

## 开发 (Development)

### 扩展 UI 功能

修改 `ui/main_window.py` 添加新控件或功能。

### 添加新设置项

1. 在 `ui/settings.py` 中添加 getter/setter 方法
2. 在 `ui/main_window.py` 中添加对应的 UI 控件
3. 更新 `load_settings()` 和 `save_settings()` 方法

### 调试

```bash
# 直接运行 UI 模块（使用示例执行函数）
python -m ui.main_window
```
