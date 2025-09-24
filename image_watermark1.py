import os
import sys
import argparse
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import exifread


def get_exif_datetime(image_path):
    """从图片中获取EXIF信息中的拍摄时间"""
    try:
        with open(image_path, 'rb') as f:
            tags = exifread.process_file(f)
            # 尝试获取不同格式的日期时间标签
            datetime_tags = [
                'EXIF DateTimeOriginal',
                'EXIF DateTimeDigitized',
                'Image DateTime'
            ]
            
            for tag in datetime_tags:
                if tag in tags:
                    datetime_str = str(tags[tag])
                    # 尝试解析日期时间字符串
                    try:
                        # 常见的EXIF日期格式: 'YYYY:MM:DD HH:MM:SS'
                        if ':' in datetime_str:
                            date_part = datetime_str.split(' ')[0].replace(':', '-')
                        else:
                            # 可能的其他格式
                            date_part = datetime_str[:8]  # 假设格式为'YYYYMMDD'
                            date_part = f"{date_part[:4]}-{date_part[4:6]}-{date_part[6:8]}"
                        return date_part
                    except:
                        continue
            # 如果没有找到有效的日期，返回当前日期
            return datetime.now().strftime('%Y-%m-%d')
    except Exception as e:
        print(f"获取EXIF信息时出错: {e}")
        # 出错时返回当前日期
        return datetime.now().strftime('%Y-%m-%d')


def add_watermark(image_path, output_path, watermark_text, font_size=20, color=(255, 255, 255), position='bottom_right'):
    """给图片添加水印"""
    try:
        # 打开图片
        image = Image.open(image_path).convert('RGBA')
        draw = ImageDraw.Draw(image)
        
        # 获取图片尺寸
        width, height = image.size
        
        # 尝试加载字体，如果失败则使用默认字体
        try:
            # 在Windows上尝试加载系统字体
            if os.name == 'nt':
                font = ImageFont.truetype("Arial.ttf", font_size)
            else:
                # 在其他系统上尝试加载不同的字体
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
        except:
            # 如果无法加载指定字体，使用默认字体
            font = ImageFont.load_default()
        
        # 获取文本尺寸
        try:
            # Pillow 8.0.0+ 支持的方法
            text_width, text_height = draw.textsize(watermark_text, font=font)
        except AttributeError:
            # 较新版本的Pillow使用的方法
            bbox = draw.textbbox((0, 0), watermark_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        
        # 根据位置确定文本的位置
        margin = 10  # 边距
        if position == 'top_left':
            x, y = margin, margin
        elif position == 'top_right':
            x, y = width - text_width - margin, margin
        elif position == 'bottom_left':
            x, y = margin, height - text_height - margin
        elif position == 'center':
            x, y = (width - text_width) // 2, (height - text_height) // 2
        else:  # 默认右下角
            x, y = width - text_width - margin, height - text_height - margin
        
        # 添加文本水印，添加黑色边框以提高可读性
        # 创建一个半透明的文本层
        text_layer = Image.new('RGBA', image.size, (255, 255, 255, 0))
        text_draw = ImageDraw.Draw(text_layer)
        
        # 绘制文本阴影以提高可读性
        shadow_color = (0, 0, 0, 128)  # 半透明黑色
        for offset in [(1, 1), (-1, 1), (1, -1), (-1, -1)]:
            text_draw.text((x + offset[0], y + offset[1]), watermark_text, font=font, fill=shadow_color)
        
        # 绘制主文本
        text_draw.text((x, y), watermark_text, font=font, fill=color + (200,))  # 添加透明度
        
        # 将文本层与原图像合并
        result = Image.alpha_composite(image, text_layer)
        
        # 保存结果
        if result.mode == 'RGBA':
            result = result.convert('RGB')
        result.save(output_path)
        print(f"已保存带水印的图片: {output_path}")
    except Exception as e:
        print(f"处理图片时出错: {e}")


def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='给图片添加基于拍摄日期的水印')
    parser.add_argument('image_path', help='图片文件或目录路径')
    parser.add_argument('--font-size', type=int, default=20, help='水印字体大小')
    parser.add_argument('--color', default='white', help='水印颜色（英文名称或RGB值，如"255,255,255"）')
    parser.add_argument('--position', choices=['top_left', 'top_right', 'bottom_left', 'bottom_right', 'center'],
                        default='bottom_right', help='水印位置')
    
    args = parser.parse_args()
    
    # 解析颜色参数
    if args.color.lower() == 'white':
        color = (255, 255, 255)
    elif args.color.lower() == 'black':
        color = (0, 0, 0)
    elif args.color.lower() == 'red':
        color = (255, 0, 0)
    elif args.color.lower() == 'green':
        color = (0, 255, 0)
    elif args.color.lower() == 'blue':
        color = (0, 0, 255)
    elif ',' in args.color:
        # 尝试解析RGB值
        try:
            r, g, b = map(int, args.color.split(','))
            color = (r, g, b)
        except:
            print("颜色格式错误，使用默认颜色白色")
            color = (255, 255, 255)
    else:
        color = (255, 255, 255)  # 默认白色
    
    # 处理输入路径
    if os.path.isdir(args.image_path):
        # 处理目录
        dir_path = args.image_path
        # 创建输出目录
        output_dir = f"{dir_path}_watermark"
        os.makedirs(output_dir, exist_ok=True)
        
        # 获取目录中的所有图片文件
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff']
        image_files = []
        
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                if any(file.lower().endswith(ext) for ext in image_extensions):
                    image_files.append(os.path.join(root, file))
        
        # 处理每个图片文件
        for image_file in image_files:
            # 相对于原目录的路径
            rel_path = os.path.relpath(image_file, dir_path)
            # 输出路径
            output_file = os.path.join(output_dir, rel_path)
            # 创建输出目录结构
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            # 获取水印文本
            watermark_text = get_exif_datetime(image_file)
            # 添加水印
            add_watermark(image_file, output_file, watermark_text, args.font_size, color, args.position)
    else:
        # 处理单个文件
        if not os.path.isfile(args.image_path):
            print(f"文件不存在: {args.image_path}")
            sys.exit(1)
        
        # 获取目录和文件名
        dir_path = os.path.dirname(args.image_path)
        if not dir_path:
            dir_path = '.'
        
        file_name = os.path.basename(args.image_path)
        
        # 创建输出目录
        output_dir = f"{dir_path}_watermark"
        os.makedirs(output_dir, exist_ok=True)
        
        # 输出文件路径
        output_file = os.path.join(output_dir, file_name)
        
        # 获取水印文本
        watermark_text = get_exif_datetime(args.image_path)
        # 添加水印
        add_watermark(args.image_path, output_file, watermark_text, args.font_size, color, args.position)


if __name__ == '__main__':
    main()