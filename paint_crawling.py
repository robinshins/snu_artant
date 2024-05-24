from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd

# 설정
chrome_options = Options()
chrome_options.add_argument("--headless")  # 브라우저 창을 띄우지 않음
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# 드라이버 설치 및 설정
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

base_url = 'https://www.printbakery.com/product/list.html?cate_no=232&page='
page_num = 1
image_urls = set()

while True:
    url = f"{base_url}{page_num}"
    driver.get(url)
    time.sleep(3)  # 페이지 로드 대기
    
    # 페이지에 제품이 있는지 확인
    lis = driver.find_elements(By.CSS_SELECTOR, 'li.product-item')
    if not lis:
        break  # 제품이 없으면 루프 종료
    
    # 이미지 URL 추출
    for li in lis:
        img = li.find_element(By.CSS_SELECTOR, 'img.product-item-image')
        src = img.get_attribute('src')
        if src and '//www.printbakery.com/web/product/' in src:
            if src.startswith('//'):
                src = 'https:' + src
            image_urls.add(src)
    
    page_num += 1

# 드라이버 종료
driver.quit()

# 이미지 URL을 데이터프레임으로 변환
df = pd.DataFrame(list(image_urls), columns=['Image URL'])

# 엑셀 파일로 저장
df.to_excel('paint_image_urls.xlsx', index=False)

print("이미지 URL이 image_urls.xlsx 파일에 저장되었습니다.")
