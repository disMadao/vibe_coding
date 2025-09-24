import os
import argparse
from PIL import Image, ImageDraw, ImageFont
from PIL.ExifTags import TAGS
import piexif
from datetime import datetime

def get_exif_date(image_path):
    """
    从图片的EXIF信息中提取拍摄日期
    """
    try:
        # 使用piexif库读取EXIF信息
        exif_dict = piexif.load(image_path)

        # 尝试从EXIF中获取拍摄时间
        # 不同相机可能使用不同的标签
        date_tags = [
            piexif.ExifIFD.DateTimeOriginal,  # 36867
            piexif.ImageIFD.DateTime,         # 306
            piexif.ExifIFD.DateTimeDigitized  # 36868
        ]

        for tag in date_tags:
            if tag in exif_dict["Exif"]:
                date_str = exif_dict["Exif"][tag].decode('utf-8')
                # 将日期字符串转换为datetime对象
                date_obj = datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
                # 返回年月日格式
                return date_obj.strftime('%Y-%m-%d')

        # 如果找不到EXIF日期信息，返回None
        return None
    except Exception as e:
        print(f"读取 {image_path} 的EXIF信息时出错: {e}")
        return None

def add_watermark(image_path, output_path, watermark_text, font_size, color, position):
    """
    为图片添加水印
    """
    try:
        # 打开图片
        image = Image.open(image_path)

        # 创建绘图对象
        draw = ImageDraw.Draw(image)

        # 尝试加载字体，如果失败则使用默认字体
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()

        # 计算文本尺寸
        text_bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        # 计算水印位置
        img_width, img_height = image.size

        if position == "top-left":
            x = 10
            y = 10
        elif position == "top-right":
            x = img_width - text_width - 10
            y = 10
        elif position == "bottom-left":
            x = 10
            y = img_height - text_height - 10
        elif position == "bottom-right":
            x = img_width - text_width - 10
            y = img_height - text_height - 10
        elif position == "center":
            x = (img_width - text_width) // 2
            y = (img_height - text_height) // 2
        else:
            x = img_width - text_width - 10
            y = img_height - text_height - 10

        # 添加水印
        draw.text((x, y), watermark_text, font=font, fill=color)

        # 保存图片
        image.save(output_path)
        print(f"已添加水印: {output_path}")

    except Exception as e:
        print(f"处理图片 {image_path} 时出错: {e}")

def process_directory(input_dir, font_size, color, position):
    """
    处理目录中的所有图片文件
    """
    # 创建输出目录
    output_dir = os.path.join(input_dir, f"{os.path.basename(input_dir)}_watermark")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 支持的图片格式
    supported_formats = ('.jpg', '.jpeg', '.png', '.tiff', '.bmp')

    # 遍历目录中的文件
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(supported_formats):
            input_path = os.path.join(input_dir, filename)

            # 获取EXIF日期信息
            date_str = get_exif_date(input_path)

            if date_str:
                watermark_text = date_str
            else:
                watermark_text = "无日期信息"

            # 生成输出路径
            name, ext = os.path.splitext(filename)
            output_filename = f"{name}_watermarked{ext}"
            output_path = os.path.join(output_dir, output_filename)

            # 添加水印
            add_watermark(input_path, output_path, watermark_text, font_size, color, position)

def main():
    """
    主函数，解析命令行参数并执行程序
    """
    parser = argparse.ArgumentParser(description='为图片添加基于EXIF拍摄时间的水印')
    parser.add_argument('input_dir', help='输入图片目录路径')
    parser.add_argument('-s', '--size', type=int, default=20, help='字体大小（默认20）')
    parser.add_argument('-c', '--color', default='white', help='水印颜色（默认白色）')
    parser.add_argument('-p', '--position',
                        choices=['top-left', 'top-right', 'bottom-left', 'bottom-right', 'center'],
                        default='bottom-right',
                        help='水印位置（默认右下角）')

    args = parser.parse_args()
    print(args.__str__())
    print(args)
    # 检查输入目录是否存在
    if not os.path.isdir(args.input_dir):
        print(f"错误: 目录 '{args.input_dir}' 不存在")
        return

    # 处理目录
    process_directory(args.input_dir, args.size, args.color, args.position)
    print("水印添加完成！")

"""
运行示例：
python image_watermark.py -s 40 -c black -p "center" D:\code_2\vibe_coding\
或者
python image_watermark.py D:\code_2\vibe_coding\

图片位置参数一定要带上，其他参数可以按需添加。
"""
if __name__ == "__main__":
    main()
