from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import re
from typing import Dict, List


class GoogleMapsCoordinatesScraper:
    def __init__(self):
        """初始化瀏覽器設定"""
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # 無頭模式，不顯示瀏覽器視窗
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)

    def get_coordinates(self, address: str) -> Dict:
        """
        從Google Maps獲取地址的經緯度

        Parameters:
            address (str): 要搜尋的地址

        Returns:
            dict: 包含地址和經緯度的字典
        """
        try:
            # 前往Google Maps
            self.driver.get("https://www.google.com/maps")
            time.sleep(2)  # 等待頁面載入

            # 找到搜尋框並輸入地址
            search_box = self.wait.until(
                EC.presence_of_element_located((By.ID, "searchboxinput"))
            )
            search_box.clear()
            search_box.send_keys(address)
            search_box.send_keys(Keys.ENTER)

            # 等待頁面載入並獲取URL
            time.sleep(3)
            current_url = self.driver.current_url

            # 從URL中提取經緯度
            coord_pattern = r"@([-\d.]+),([-\d.]+)"
            match = re.search(coord_pattern, current_url)

            if match:
                return {
                    "address": address,
                    "latitude": float(match.group(1)),
                    "longitude": float(match.group(2)),
                    "status": "success",
                }
            else:
                return {
                    "address": address,
                    "latitude": None,
                    "longitude": None,
                    "status": "coordinates_not_found",
                }

        except Exception as e:
            return {
                "address": address,
                "latitude": None,
                "longitude": None,
                "status": f"error: {str(e)}",
            }

    def batch_process(self, addresses: List[str]) -> pd.DataFrame:
        """
        批次處理多個地址

        Parameters:
            addresses (List[str]): 地址列表

        Returns:
            pd.DataFrame: 包含所有結果的DataFrame
        """
        results = []
        total = len(addresses)

        for i, address in enumerate(addresses, 1):
            print(f"處理地址 {i}/{total}: {address}")
            result = self.get_coordinates(address.strip())
            results.append(result)
            time.sleep(2)  # 避免請求過於頻繁

        return pd.DataFrame(results)

    def close(self):
        """關閉瀏覽器"""
        self.driver.quit()


def save_results(df: pd.DataFrame, output_file: str = "coordinates_results.csv"):
    """將結果保存為CSV檔案"""
    df.to_csv(output_file, index=False, encoding="utf-8-sig")


def main():
    # 讀取地址列表
    try:
        with open("addresses2.txt", "r", encoding="utf-8") as f:
            addresses = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("請將地址列表存為 addresses.txt 檔案")
        return

    # 初始化爬蟲
    scraper = GoogleMapsCoordinatesScraper()

    try:
        print(f"開始處理 {len(addresses)} 個地址...")
        results_df = scraper.batch_process(addresses)

        # 儲存結果
        save_results(results_df)
        print(f"處理完成！結果已儲存至 coordinates_results2.csv")

        # 顯示統計資訊
        success_count = len(results_df[results_df["status"] == "success"])
        print(f"\n處理統計:")
        print(f"成功轉換: {success_count}")
        print(f"失敗數量: {len(addresses) - success_count}")

    finally:
        scraper.close()


if __name__ == "__main__":
    main()
