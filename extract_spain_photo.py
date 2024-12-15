from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import pandas as pd
import os
import shutil
import time

# 配置参数
csv_path = "dataset/coords.csv"
images_folder = "dataset"  # 存放图片的文件夹
output_folder = "dataset_spain"  # 输出文件夹

# 创建输出文件夹
os.makedirs(output_folder, exist_ok=True)

# 读取 CSV 文件
coords = pd.read_csv(csv_path, header=None, names=["latitude", "longitude"])

# 初始化 geopy 的 Nominatim
geolocator = Nominatim(user_agent="spain_filter")

# 判断函数：是否在西班牙
def is_in_spain(lat, lon):
    try:
        location = geolocator.reverse((lat, lon), language="en", timeout=10)
        if location and "Spain" in location.address:
            return True
    except GeocoderTimedOut:
        print(f"Timeout for coordinates: ({lat}, {lon}). Retrying...")
        time.sleep(1)
        return is_in_spain(lat, lon)  # 重试一次
    return False

# 筛选出属于西班牙的图片
spain_coords = []
for idx, row in coords.iterrows():
    lat, lon = row["latitude"], row["longitude"]
    if is_in_spain(lat, lon):
        spain_coords.append(idx)
        print(f"Found in Spain: Image {idx + 1} at ({lat}, {lon})")

# 复制西班牙图片到目标文件夹
for idx in spain_coords:
    image_name = f"{idx + 1}.png"  # 假设图片按照行号命名
    src_path = os.path.join(images_folder, image_name)
    dest_path = os.path.join(output_folder, image_name)
    if os.path.exists(src_path):  # 确保图片存在
        shutil.copy(src_path, dest_path)

print(f"筛选完成！共找到 {len(spain_coords)} 张属于西班牙的图片，并保存到 '{output_folder}' 文件夹中。")
