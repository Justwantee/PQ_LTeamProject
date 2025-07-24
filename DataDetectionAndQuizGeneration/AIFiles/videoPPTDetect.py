import cv2
import os
import numpy as np
from skimage.metrics import structural_similarity as ssim
def extract_frames(video_path, output_folder, frame_interval=1):
    # 创建输出文件夹（如果不存在）
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    # 打开视频文件
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("无法打开视频文件")
        return
    frame_count = 0
    saved_frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_count % frame_interval == 0:
            output_path = os.path.join(output_folder, f"frame_{saved_frame_count:04d}.jpg")
            cv2.imwrite(output_path, frame)
            saved_frame_count += 1

        frame_count += 1

    cap.release()
    print(f"共抽取并保存了 {saved_frame_count} 帧到 {output_folder}")
def phash(image, shape=(32, 32)):
    """
    计算图像的感知哈希值。
    参数:
        image: 输入图像。
        shape: 缩放后的图像尺寸，默认为 32x32。
    返回:
        哈希值（十六进制字符串）。
    """
    # 缩放图像
    resized = cv2.resize(image, shape, interpolation=cv2.INTER_AREA)
    # 转换为灰度图
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    # 计算 DCT
    dct = cv2.dct(np.float32(gray))
    # 取左上角 8x8 的 DCT 系数
    dct_low_frequency = dct[:8, :8]
    # 计算平均值
    avg = np.mean(dct_low_frequency)
    # 生成哈希值
    hash_str = ''.join(['1' if pixel >= avg else '0' for pixel in dct_low_frequency.flatten()])
    # 转换为十六进制
    return ''.join([f'{int(hash_str[i:i+4], 2):x}' for i in range(0, len(hash_str), 4)])

def find_similar_images(image_paths, threshold=0.95):
    """
    检测大体上重复的图片。
    参数:
        image_paths: 图片路径列表。
        threshold: SSIM 相似度阈值，默认为 0.95。
    返回:
        相似图片的索引对列表。
    """
    similar_pairs = []
    num_images = len(image_paths)

    for i in range(num_images):
        img1 = cv2.imread(image_paths[i])
        if img1 is None:
            print(f"无法加载图片 {image_paths[i]}")
            continue

        for j in range(i + 1, num_images):
            img2 = cv2.imread(image_paths[j])
            if img2 is None:
                print(f"无法加载图片 {image_paths[j]}")
                continue

            # 计算 SSIM
            gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
            similarity, _ = ssim(gray1, gray2, full=True)

            if similarity >= threshold:
                similar_pairs.append((i, j))

    return similar_pairs

def remove_duplicate_images(image_paths, threshold=0.95):
    """
    删除重复度较高的图片，只保留重复度较低的图片。
    参数:
        image_paths: 图片路径列表。
        threshold: SSIM 相似度阈值。
    """
    similar_pairs = find_similar_images(image_paths, threshold)

    if not similar_pairs:
        print("未发现重复或相似的图片，无需删除。")
        return

    # 创建一个集合来记录需要删除的图片索引
    to_delete_indices = set()
    for pair in similar_pairs:
        to_delete_indices.add(pair[1])  # 保留索引较小的图片，删除索引较大的图片

    # 删除重复度较高的图片
    for index in sorted(to_delete_indices, reverse=True):  # 从大到小删除，避免索引变化
        os.remove(image_paths[index])
        print(f"已删除图片：{image_paths[index]}")

def process(file_path):
 video_path = file_path  # 替换视频文件路径
 output_folder = "inputFiles"  # 替换为保存帧的文件夹路径
 frame_interval = 30  # 每30帧抽取一次
 extract_frames(video_path, output_folder, frame_interval)
 generated = []
 generated.append('inputFiles')
 return generated
# 示例用法
folder_path = "testFiles"  # 替换为你的图片文件夹路径
image_paths = [os.path.join(folder_path, filename) for filename in os.listdir(folder_path) if filename.lower().endswith(('.png', '.jpg', '.jpeg'))]
remove_duplicate_images(image_paths, threshold=0.8)#调阈值，越高判定越严格，越不会轻易删图
