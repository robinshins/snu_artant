import openai
import openpyxl
from google.cloud import firestore
import pandas as pd
import firebase_admin
from firebase_admin import credentials
import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'artant-d3a1pi-firebase-adminsdk-20uvl-9020e85b24.json'
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv() 



# Firestore 초기화
db = firestore.Client()

def read_image_urls_from_excel(file_path):
    print("엑셀 읽기 시작")
    df = pd.read_excel(file_path)

    # 3행씩 건너띄면서 100개의 URL 추출
    urls = df['Image URL'][::1].head(100).tolist()
    filtered_urls = [url for url in urls if url.startswith('https://')]
    return filtered_urls


def generate_tags(image_url):
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "다음은 예술품의 사진이야. 해당 사진을 통해 예술품의 종류, 카테고리, 질감, 주제, 상황, 스타일, 배경, 색감, 분위기 등을 파악할 수 있는 이미지 태그들을 영어로 30개 뽑아. 다른말하지 말고 태그만 쉼표로 구분해서 뽑아."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url
                        }
                    }
                ]
            }
        ],
    )
    return response.choices[0].message.content

# Firestore에 태그 저장
def save_tags_to_firestore(tags, url):
    doc_ref = db.collection('added_keyword').document('keywords')
    doc = doc_ref.get()

    if doc.exists:
        existing_keywords = doc.to_dict().get('keywords', {})
    else:
        existing_keywords = {}

    new_keywords = tags.split(',')

    for tag in new_keywords:
        if tag in existing_keywords:
            existing_keywords[tag] += 1
        else:
            existing_keywords[tag] = 1

    doc_ref.set({'keywords': existing_keywords})
    
    # Add new document in 'images' collection with 'tags' and 'url'
    image_doc_ref = db.collection('images').document()
    image_doc_ref.set({
        'tags': tags,
        'url': url
    })


# 메인 함수
def main():
    # 엑셀 파일 경로
    excel_file_path = 'crawled_data/paint_image_urls.xlsx'

    # 이미지 URL 읽기
    image_urls = read_image_urls_from_excel(excel_file_path)
    #print(image_urls)

    for url in image_urls:
        if url: 
            try:
                # 태그 생성
                tags = generate_tags(url)
                # Firestore에 태그 저장
                save_tags_to_firestore(tags, url)
                print(f"Tags for {url} are: {tags}")
            except Exception as e:
                print(f"Error processing URL {url}: {e}")

if __name__ == '__main__':
    main()
