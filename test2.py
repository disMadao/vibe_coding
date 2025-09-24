# test.py 原始代码（简化版）
import argparse
import os
import sys

parser = argparse.ArgumentParser()
parser.add_argumnt("input_dir")
# parser.add_argument()
args = parser.parse_args()  # 这里会报错如果未传参数

# # 临时修改：允许参数为空
# if len(sys.argv) == 1:
#     input_dir = input("Enter input directory: ")
#     print("asdfasdfasdf")
# else:
#     args = parser.parse_args()
#     input_dir = args.input_dir
#     print(123)

# 如果input_dir未提供，通过input获取
if not args.input_dir:
    args.input_dir = input("请输入图片目录路径：").strip()
    # 验证路径是否存在
    if not os.path.isdir(args.input_dir):
        print(f"错误：目录 {args.input_dir} 不存在")
        sys.exit(1)
