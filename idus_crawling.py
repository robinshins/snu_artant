from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd

# 설정
chrome_options = Options()
# chrome_options.add_argument("--headless")  # 브라우저 창을 띄우지 않음
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# 드라이버 설치 및 설정
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
url = 'https://www.idus.com/v2/showroom/8129?view=LIST&sort=RECOMMEND'

# 웹 페이지 열기
driver.get(url)
time.sleep(3)  # 페이지 로드 대기

last_height = driver.execute_script("return document.body.scrollHeight")
image_urls = set()

while True:
    # 페이지 하단으로 스크롤
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)  # 페이지 로드 대기

    # 이미지 URL 추출
    images = driver.find_elements(By.TAG_NAME, 'img')
    for image in images:
        src = image.get_attribute('src')
        if src and 'https://image.idus.com/image/files/' in src:
            image_urls.add(src)

    # 새로운 높이 확인
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height



# 드라이버 종료
driver.quit()

# 이미지 URL을 데이터프레임으로 변환
df = pd.DataFrame(list(image_urls), columns=['Image URL'])

# 엑셀 파일로 저장
df.to_excel('image_urls_best_recommend.xlsx', index=False)