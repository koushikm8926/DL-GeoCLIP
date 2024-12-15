import os
import shutil
import json
import geopandas as gpd
from shapely.geometry import Point


# 加载西班牙的自治区边界数据
def load_comunidad_boundaries(geojson_file):
    """
    加载西班牙自治区边界数据
    :param geojson_file: GeoJSON 文件路径
    :return: GeoDataFrame 对象
    """
    return gpd.read_file(geojson_file)


# 判断某点是否在西班牙的某自治区内
def get_comunidad(lat, lon, geo_df):
    """
    根据经纬度判断所属的自治区
    :param lat: 纬度
    :param lon: 经度
    :param geo_df: 包含自治区边界的 GeoDataFrame
    :return: 自治区名称（如果找到），否则返回 None
    """
    point = Point(lon, lat)  # 注意顺序：经度在前，纬度在后
    for _, row in geo_df.iterrows():
        if row["geometry"].contains(point):
            return row["region"]  # 假设自治区名称字段为 'region'
    return None


# 主函数
def extract_spain_images(
    image_folder, coords_file, geojson_file, output_folder, output_json
):
    """
    提取属于西班牙的图片并存储到新文件夹，同时生成 JSON
    :param image_folder: 原图片文件夹路径
    :param coords_file: 经纬度 CSV 文件路径
    :param geojson_file: 西班牙自治区 GeoJSON 文件路径
    :param output_folder: 输出图片文件夹路径
    :param output_json: 输出 JSON 文件路径
    """
    # 加载边界数据
    geo_df = load_comunidad_boundaries(geojson_file)

    # 创建输出文件夹
    os.makedirs(output_folder, exist_ok=True)

    # 存储编号和 Comunidad 的映射
    spain_images = {}

    # 逐行处理坐标
    with open(coords_file, "r") as f:
        for idx, line in enumerate(f, start=1):
            lat, lon = map(float, line.strip().split(","))
            comunidad = get_comunidad(lat, lon, geo_df)

            if comunidad:  # 属于西班牙范围
                image_file = os.path.join(image_folder, f"{idx}.png")
                if os.path.exists(image_file):
                    # 复制图片到新文件夹
                    shutil.copy(image_file, output_folder)

                    # 记录到 JSON
                    spain_images[idx] = comunidad

    # 保存 JSON 文件
    with open(output_json, "w", encoding="utf-8") as json_file:
        json.dump(spain_images, json_file, ensure_ascii=False, indent=4)

    print(
        f"处理完成！已提取 {len(spain_images)} 张图片到 {output_folder}，JSON 保存到 {output_json}"
    )


# 参数配置
if __name__ == "__main__":
    image_folder = "dataset"  # 原图片文件夹
    coords_file = "dataset/coords.csv"  # 经纬度文件
    geojson_file = "spain_comunidades.geojson"  # 西班牙自治区边界 GeoJSON
    output_folder = "dataset_spain"  # 输出图片文件夹
    output_json = "comunidad.json"  # 输出 JSON 文件

    # 调用函数
    extract_spain_images(
        image_folder, coords_file, geojson_file, output_folder, output_json
    )
