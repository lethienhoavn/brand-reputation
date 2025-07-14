import undetected_chromedriver as uc
import pickle

driver = uc.Chrome()
driver.get("https://www.facebook.com/login")

print("Vui lòng đăng nhập Facebook thủ công, xong nhấn Enter...")
input()

pickle.dump(driver.get_cookies(), open("../cookies/fb_cookies.pkl", "wb"))
print("Đã lưu cookies thành fb_cookies.pkl")

driver.quit()
