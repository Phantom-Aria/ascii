from PIL import Image, ImageDraw, ImageFont
import subprocess
import sys
import os
import shutil
import numpy as np
import gc

file_input = sys.argv[1]
FPS = sys.argv[2]

def do_turn(file_input, FPS):
    os.makedirs("tempfile/cut/")
    shell_vedio = "ffmpeg -i " + file_input + " -r " + FPS + " -qscale:v 2 ./tempfile/cut/%05d.jpg"
    shell_voice = "ffmpeg -i " + file_input + " ./tempfile/out.mp3"
    subprocess.call(shell_vedio, shell=True)
    subprocess.call(shell_voice, shell=True)
    count =0
    for file in os.listdir("./tempfile/cut/"):
        count += 1
    print("成功分离音频，截图开始转换字符画......" + "共计" + str(count) + "张")

    list_p = os.listdir("./tempfile/cut/")
    cwd = os.getcwd()
    os.mkdir("./tempfile/new/")
    process = 1
    for id in list_p:
        address = str("".join(cwd + '/tempfile/cut/' + id))
        im = Image.open(address)
        font = ImageFont.truetype("DejaVuSans-Bold", size=20)      
        rate = 0.1    
        aspect_ratio = font.getsize("x")[0] / font.getsize("x")[1]   
        new_im_size = np.array([im.size[0] * rate, im.size[1] * rate * aspect_ratio]).astype(int)    
        im = im.resize(new_im_size)   
        im = np.array(im.convert("L"))       
        symbols = np.array(list(" .-vM@"))

        if im.max() == im.min():      
            if im.max() > 0:
                im = (im / im) * (symbols.size - 1)
            else:
                im[np.isnan(im)] = 0         
        else: 
            im = (im - im.min()) / (im.max() - im.min()) * (symbols.size - 1)
        ascii = symbols[im.astype(int)]    
        letter_size = font.getsize("x")   
        im_out_size = new_im_size * letter_size    
        im_out = Image.new("RGB", tuple(im_out_size), "black")  
        draw = ImageDraw.Draw(im_out)

        y = 0 
        for i, m in enumerate(ascii):
            for j, n in enumerate(m): 
                draw.text((letter_size[0] * j, y), n, font=font) 
            y += letter_size[1] 
        im_out.save("./tempfile/new/" + id + ".png")  
        print(address + "转换成功！当前进度：" + str(process) + "/" + str(count))
        process += 1
        gc.collect()
    print("转换成功！开始生成视频，请稍候......")

    outvedio = "ffmpeg -r " + FPS + " -i ./tempfile/new/%05d.jpg.png ./tempfile/out.mp4"
    subprocess.call(outvedio, shell=True)
    final_vedio = "ffmpeg -i ./tempfile/out.mp4 -i ./tempfile/out.mp3 final.mp4"
    subprocess.call(final_vedio, shell=True)
    shutil.rmtree("./tempfile")
    print("字符动画final.mp4已生成!已移除临时文件夹")


def usage():
    print("usage:", sys.argv[0], "<file_input> <FPS>") 
    exit(0)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        usage()
    else:
        do_turn(file_input, FPS)
