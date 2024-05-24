from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

# Chrome 드라이버 설정
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

def fetch_image_urls(base_url, start_page, end_page):
    image_urls = []
    for page in range(start_page, end_page + 1):
        url = f"{base_url}?ref=pagination&page={page}"
        driver.get(url)
        time.sleep(2)  # 페이지 로딩 대기
        # 이미지 URL 추출
        images = driver.find_elements(By.CSS_SELECTOR, "img")
        for image in images:
            src = image.get_attribute('src')
            if src:
                image_urls.append(src)
        time.sleep(1)  # 서버 부하 방지를 위한 딜레이
    return image_urls

# URL 설정
base_url = 'https://www.etsy.com/c/art-and-collectibles'

# 페이지 순회하면서 데이터 가져오기
image_urls = fetch_image_urls(base_url, 1, 250)

# Selenium 드라이버 종료
driver.quit()

# URL을 DataFrame으로 변환 후 Excel 파일로 저장
df = pd.DataFrame(image_urls, columns=['Image URL'])
df.to_excel('etsy_image_urls.xlsx', index=False)

print("크롤링이 완료되었으며 데이터가 'etsy_image_urls_art_and_collectibles.xlsx' 파일에 저장되었습니다.")
