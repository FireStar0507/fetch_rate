import os
import csv
import requests
import sys
from datetime import datetime

def fetch_exchange_rates(api_key, base_currency):
    """获取指定货币的汇率数据"""
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{base_currency}"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"API请求失败，状态码：{response.status_code}")
    data = response.json()
    if data["result"] != "success":
        raise Exception(f"API返回错误：{data.get('error-type', '未知错误')}")
    return data

def save_to_csv(base_currency, new_data):
    """将数据保存为CSV，包含格式化日期"""
    filename = f"{base_currency}.csv"
    
    # 生成格式化日期（UTC时间）
    timestamp = new_data["timestamp"]
    date_str = datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
    
    # 动态生成表头
    headers = ["date", "timestamp"] + list(new_data["conversion_rates"].keys())
    
    # 检查重复记录
    existing_timestamps = set()
    if os.path.exists(filename):
        with open(filename, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing_timestamps.add(int(row["timestamp"]))
    
    # 跳过重复数据
    if timestamp in existing_timestamps:
        print(f"[>] {base_currency} 数据已存在，跳过保存")
        return
    
    # 写入数据
    with open(filename, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        # 新文件写入表头
        if not os.path.exists(filename) or os.stat(filename).st_size == 0:
            writer.writeheader()
        
        # 构造行数据
        row_data = {
            "date": date_str,
            "timestamp": timestamp,
            **new_data["conversion_rates"]
        }
        writer.writerow(row_data)

def main():
    api_key = os.getenv("EXCHANGE_RATE_API_KEY")
    if not api_key:
        print("[?]未找到API密钥")
        sys.exit(1)
    
    currencies = sys.argv[1:] if len(sys.argv) > 1 else ["USD", "CNY"]
    
    for currency in currencies:
        try:
            data = fetch_exchange_rates(api_key, currency)
            save_data = {
                "timestamp": data["time_last_update_unix"],
                "conversion_rates": data["conversion_rates"]
            }
            save_to_csv(currency, save_data)
            print(f"[*] {currency} 数据已更新")
        except Exception as e:
            print(f"[!] {currency} 更新失败：{str(e)}")

if __name__ == "__main__":
    main()
