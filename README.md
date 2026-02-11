# PicToAF - 图片和视频转ADOFai关卡工具

## 项目概述

PicToAF是一个用于将图片和视频转换为ADOFai（A Dance of Fire and Ice）关卡文件的工具集。该项目包含两个主要工具：

1. **图片转ADOFai工具**：将静态图片转换为ADOFai关卡文件
2. **视频转ADOFai工具**：将视频文件转换为ADOFai关卡文件，支持逐帧处理

## 项目结构

```
PicToAF/
├── common/            # 共用文件
│   ├── Logger.py      # 日志工具
│   ├── Parser.py      # 解析工具
│   └── __init__.py
├── image_tool/        # 图片工具实现
│   ├── __init__.py
│   ├── adofai_generator.py  # ADOFai关卡生成器
│   └── image_processor.py   # 图片处理器
├── video_tool/        # 视频工具实现
│   ├── __init__.py
│   ├── torch_video_processor.py  # PyTorch视频处理器
│   ├── video_processor.py        # 传统视频处理器
│   └── video_to_adofai.py        # 视频转ADOFai工具
├── output/            # 产物文件夹
├── main.py            # 图片工具入口
├── video_main.py      # 视频工具入口
├── .gitignore         # Git忽略文件
└── README.md          # 项目说明
```

## 功能特点

### 图片转ADOFai工具
- 支持多种图片格式（PNG、JPG、JPEG、BMP、GIF）
- 可调整最大像素数，控制关卡复杂度
- 自动将图片转换为ADOFai关卡格式
- 生成包含颜色信息的关卡文件

### 视频转ADOFai工具
- 支持多种视频格式（MP4、AVI、MOV、WMV、MKV）
- 提供两种处理引擎：
  - PyTorch引擎（GPU加速，处理速度更快）
  - 传统引擎（CPU处理，兼容性更好）
- 可调整目标帧率、颜色差异阈值、最大帧数等参数
- 支持视频预览功能
- 生成包含动画效果的关卡文件

## 安装说明

### 依赖项

项目依赖以下Python库：

- Python 3.7+
- ttkbootstrap （UI界面）
- PIL/Pillow （图像处理）
- OpenCV （视频处理）
- PyTorch （可选，用于GPU加速）

### 安装步骤

1. 克隆或下载项目到本地

2. 安装依赖：
   ```bash
   pip install ttkbootstrap Pillow opencv-python
   # 可选，安装PyTorch以启用GPU加速
   pip install torch torchvision
   ```

## 使用方法

### 图片转ADOFai工具

1. 运行图片工具：
   ```bash
   python main.py
   ```

2. 在界面中：
   - 点击"浏览"按钮选择要转换的图片
   - 设置最大像素数（默认300000）
   - 选择输出文件路径
   - 点击"开始转换"按钮

3. 转换完成后，会显示转换结果信息，并在指定路径生成ADOFai关卡文件

### 视频转ADOFai工具

1. 运行视频工具：
   ```bash
   python video_main.py
   ```

2. 在界面中：
   - 点击"浏览"按钮选择要转换的视频
   - 选择处理引擎（PyTorch或传统）
   - 设置视频参数（目标帧率、颜色差异阈值、最大帧数）
   - 设置图像参数（最大像素数）
   - 选择输出文件路径
   - 可选：点击"预览第一帧"查看视频首帧效果
   - 点击"开始转换"按钮

3. 转换过程中会显示进度条和当前状态

4. 转换完成后，会显示转换结果信息，并在指定路径生成ADOFai关卡文件

## 注意事项

1. **性能考虑**：
   - 处理高分辨率图片或长视频可能需要较长时间
   - 使用PyTorch引擎需要安装PyTorch库，且需要支持CUDA的GPU以获得最佳性能

2. **文件大小**：
   - 生成的关卡文件大小会根据输入图片/视频的复杂度而变化
   - 长时间视频转换可能会生成非常大的关卡文件，请注意存储空间

3. **兼容性**：
   - 确保安装了所有必要的依赖项
   - 对于视频转换，建议使用较短的视频片段进行测试，以评估转换效果和性能

## 联系方式

如有问题或建议，请通过以下方式联系：

- [Bilibili空间](https://space.bilibili.com/616045770)
- QQ群 132292540