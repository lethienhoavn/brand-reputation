import time
import pickle
import random
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc

# === STEP 1: Setup ===
options = uc.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")

driver = uc.Chrome(options=options)

# === STEP 2: Mở TikTok và login thủ công lần đầu ===
driver.get("https://www.tiktok.com/login")
print("⏳ Hãy đăng nhập TikTok thủ công, xong nhấn Enter...")
input("👉 Khi đăng nhập xong, nhấn Enter để lưu cookies!")

# === STEP 3: Lưu cookies ===
print("driver.get_cookies(): ", driver.get_cookies())
pickle.dump(driver.get_cookies(), open("../cookies/tiktok_cookies.pkl", "wb"))
print("✅ Đã lưu cookies thành tiktok_cookies.pkl")

driver.quit()
