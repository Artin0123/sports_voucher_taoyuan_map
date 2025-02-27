import folium
import pandas as pd

# 讀取 CSV 檔案
csv_file = "coordinates_results.csv"  # 將此替換為您的 CSV 檔案名稱

data = pd.read_csv(csv_file)

# 建立地圖物件（初始位置設為第一個地址）
start_lat = data.iloc[0]["latitude"]
start_lon = data.iloc[0]["longitude"]
m = folium.Map(location=[start_lat, start_lon], zoom_start=13)

# 在地圖上添加標記
for index, row in data.iterrows():
    folium.Marker(
        location=[row["latitude"], row["longitude"]],
        popup=row["address"],
        tooltip=row["status"],
    ).add_to(m)

# 儲存地圖為 HTML
m.save("map.html")
print("地圖已保存為 map.html，請在瀏覽器中打開查看。")
