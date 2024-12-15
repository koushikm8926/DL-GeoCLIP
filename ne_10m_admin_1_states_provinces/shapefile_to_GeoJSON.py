import geopandas as gpd

# 加载 Shapefile
shp_file = "ne_10m_admin_1_states_provinces.shp"
gdf = gpd.read_file(shp_file)

# 只选择西班牙自治区的数据
spain_gdf = gdf[gdf["admin"] == "Spain"]

# 保存为 GeoJSON
spain_gdf.to_file("spain_comunidades.geojson", driver="GeoJSON")
