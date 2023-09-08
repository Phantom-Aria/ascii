import argparse
import subprocess
import os
import shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def do_turn(file_input, FPS):
    # 按帧切割图片，以及分离音频
    os.makedirs("tempfile/cut/", exist_ok=True)
    shell_vedio = f"ffmpeg -i {file_input} -r {FPS} -qscale:v 2 ./tempfile/cut/%05d.jpg"
    shell_voice = f"ffmpeg -i {file_input} ./tempfile/out.mp3"
    subprocess.run(shell_vedio, shell=True)
    subprocess.run(shell_voice, shell=True)
    list_p = os.listdir("./tempfile/cut/")
    count = len(list_p) # 切割的图片数量

    cwd = os.getcwd()
    os.mkdir("./tempfile/new/")
    process = 1
    symbols = np.array(list(" .-vM@"))  # 定义使用的字符
    font = ImageFont.truetype("DejaVuSans-Bold", size=20)
    # 处理切割的每张图片，重新定义大小
    for id in list_p:
        img_path = os.path.join(cwd, 'tempfile/cut', id)
        im = Image.open(img_path)
        rate = 0.1  # 只取原像素点数目的0.1倍
        aspect_ratio = font.getsize("x")[0] / font.getsize("x")[1]  # 字符长宽比
        new_im_size = np.array([im.size[0] * rate, im.size[1] * rate * aspect_ratio]).astype(int)
        im = im.resize(new_im_size)
        im = np.array(im.convert("L"))  # 转灰阶图
        # 整张图只有一种亮度的区分
        if im.max() == im.min():
            if im.max() > 0:
                im = (im / im) * (symbols.size - 1)
            else:
                im[np.isnan(im)] = 0
        else:
            im = (im - im.min()) / (im.max() - im.min()) * (symbols.size - 1)   # 根据亮度选择对应的字符
        # 定义输出字符大小，背景等
        ascii = symbols[im.astype(int)]
        letter_size = font.getsize("x")
        im_out_size = new_im_size * letter_size
        im_out = Image.new("RGB", tuple(im_out_size), "black")
        draw = ImageDraw.Draw(im_out)
        # 保存图片
        y = 0
        for m in ascii:
            for j, n in enumerate(m):
                draw.text((letter_size[0] * j, y), n, font=font)
            y += letter_size[1]
        im_out.save(f"./tempfile/new/{id}.png")
        print(f"{img_path}转换成功！当前进度：{process}/{count}")
        process += 1

    print("转换成功！开始生成视频，请稍候......")
    # 按帧合并图片，并合并音频
    outvedio = f"ffmpeg -r {FPS} -i ./tempfile/new/%05d.jpg.png ./tempfile/out.mp4"
    subprocess.run(outvedio, shell=True)
    final_vedio = "ffmpeg -i ./tempfile/out.mp4 -i ./tempfile/out.mp3 final.mp4"
    subprocess.run(final_vedio, shell=True)
    shutil.rmtree("./tempfile")
    print("字符动画final.mp4已生成！已移除临时文件夹")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file_input", help="输入文件")
    parser.add_argument("FPS", help="帧率")
    args = parser.parse_args()

    do_turn(args.file_input, args.FPS)


if __name__ == "__main__":
    main()
