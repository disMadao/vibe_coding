# 图片水印工具

一个简单的命令行工具，用于给图片添加基于EXIF拍摄日期的水印。

## 功能特点

- 读取图片的EXIF信息，提取拍摄日期作为水印
- 支持自定义字体大小、颜色和位置
- 可以处理单个图片文件或整个目录下的所有图片
- 自动保存带水印的图片到原目录的子目录中

## 安装说明

### 前提条件
- Python 3.6 或更高版本
- pip 包管理器

### 安装依赖

1. 克隆或下载本项目到本地
2. 进入项目目录
3. 安装所需依赖：

```bash
pip install -r requirements.txt
```

## 使用方法

### 基本语法

```bash
python image_watermark.py [图片文件或目录路径] [选项]
```

### 命令行参数

- `image_path`：必需，图片文件路径或包含图片的目录路径
- `--font-size`：可选，水印字体大小，默认为20
- `--color`：可选，水印颜色，可以是颜色名称（如"white"、"black"、"red"等）或RGB值（如"255,255,255"），默认为"white"
- `--position`：可选，水印位置，可选值："top_left"、"top_right"、"bottom_left"、"bottom_right"、"center"，默认为"bottom_right"

### 示例

1. 处理单个图片文件：

```bash
python image_watermark.py example.jpg
```

2. 处理整个目录：

```bash
python image_watermark.py photos_folder/
```

3. 自定义水印样式：

```bash
python image_watermark.py example.jpg --font-size 30 --color "red" --position "center"
```

## 输出说明

- 处理后的图片会保存在原目录下名为`[原目录名]_watermark`的子目录中
- 保留原文件的目录结构

## 依赖库

- Pillow：用于图像处理和水印绘制
- exifread：用于读取图片的EXIF信息

## 注意事项

- 程序会尝试从图片的EXIF信息中获取拍摄日期，如果无法获取，将使用当前日期
- 支持的图片格式：jpg、jpeg、png、bmp、gif、tiff
- 在不同操作系统上，可用的默认字体可能有所不同