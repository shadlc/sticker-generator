from PIL import Image
import numpy as np
import os
import sys
import cv2

def stroke(image, threshold, stroke_size, colors, padding):
    img = np.asarray(image)
    h, w, _ = img.shape
    alpha = img[:,:,3]
    rgb = img[:,:,0:3]
    bigger_img = cv2.copyMakeBorder(rgb, padding, padding, padding, padding, cv2.BORDER_CONSTANT, value=(0, 0, 0, 0))
    alpha = cv2.copyMakeBorder(alpha, padding, padding, padding, padding, cv2.BORDER_CONSTANT, value=0)
    bigger_img = cv2.merge((bigger_img, alpha))
    h, w, _ = bigger_img.shape
    
    _, alpha_without_shadow = cv2.threshold(alpha, threshold, 255, cv2.THRESH_BINARY)  # threshold=0 in photoshop
    alpha_without_shadow = 255 - alpha_without_shadow
    dist = cv2.distanceTransform(alpha_without_shadow, cv2.DIST_L2, cv2.DIST_MASK_3)  # dist l1 : L1 , dist l2 : l2
    stroked = change_matrix(dist, stroke_size)
    stroke_alpha = (stroked * 255).astype(np.uint8)

    stroke_b = np.full((h, w), colors[0][2], np.uint8)
    stroke_g = np.full((h, w), colors[0][1], np.uint8)
    stroke_r = np.full((h, w), colors[0][0], np.uint8)

    stroke = cv2.merge((stroke_b, stroke_g, stroke_r, stroke_alpha))
    stroke = cv2pil(stroke)
    bigger_img = cv2pil(bigger_img)
    result = Image.alpha_composite(stroke, bigger_img)
    return result

def change_matrix(input_mat, stroke_size):
    stroke_size = stroke_size - 1
    mat = np.ones(input_mat.shape)
    check_size = stroke_size + 1.0
    mat[input_mat > check_size] = 0
    border = (input_mat > stroke_size) & (input_mat <= check_size)
    mat[border] = 1.0 - (input_mat[border] - stroke_size)
    return mat

def cv2pil(cv_img):
    pil_img = Image.fromarray(cv_img.astype("uint8"))
    return pil_img

def resize(img, size=0):
    width, height = img.size
    if not size:
        size =img.size
    resize_img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    scale = min(size / width, size / height)
    offset_x = (size - width * scale) / 2
    offset_y = (size - height * scale) / 2
    img = img.resize((int(width * scale), int(height * scale)), Image.LANCZOS)
    resize_img.paste(img, (int(offset_x), int(offset_y)), img)
    return resize_img

if __name__ == "__main__":

    if not len(sys.argv) >= 3:
        print(
            f"请按照以下格式的脚本调用此程序，且至少需输入源文件夹和目标文件夹：此程序 源文件夹 输出文件夹 图片大小 描边宽度 图片格式"
            "例如使用CMD在本目录如此执行 ./sticker-generator.exe ./input ./output 300 3 png"
        )
        os.system('pause')
        sys.exit()

    input_path = sys.argv[1]
    output_path = sys.argv[2]
    if not os.path.exists(input_path):
        print(f"输入文件夹“{input_path}”不存在")
        os.system('pause')
        sys.exit()
    if not os.path.exists(output_path):
        print(f"输出文件夹“{output_path}”不存在")
        os.system('pause')
        sys.exit()

    img_size = 300
    stroke_size = 3
    img_type = "png"
    img_count = 0
    if len(sys.argv) >= 4:
        img_size = sys.argv[3]
    if not img_size.isdigit():
        print(f"图片大小输入“{input_path}”错误")
        sys.exit()
    if len(sys.argv) >= 5:
        stroke_size = sys.argv[4]
    if not stroke_size.isdigit():
        print(f"描边宽度输入“{input_path}”错误")
        sys.exit()
    if len(sys.argv) >= 6:
        img_type = sys.argv[5]

    for full_image_name in os.listdir(input_path):
        src = os.path.join(input_path, full_image_name)
        image_name = full_image_name.split('.')[0]
        img_count += 1
        image_name_output = f"{image_name}_{img_count}.{img_type}"
        img = Image.open(src)
        img = img.convert('RGBA')
        resized_img = resize(img, size=int(img_size))
        stroked_img = stroke(resized_img, threshold=0, stroke_size=int(stroke_size), colors=((255,255,255),), padding=0)
        stroked_img.save(os.path.join(output_path, image_name_output))
        print(f"图片{image_name_output}已处理完成")
    print(f"已保存全部图片至文件夹“{output_path}”")
    os.system('pause')
