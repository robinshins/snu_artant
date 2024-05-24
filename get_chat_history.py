import os
import pandas as pd
from google.cloud import firestore
from google.auth.credentials import AnonymousCredentials
from openpyxl import Workbook

# Firestore 초기화
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "artant-d3a1pi-firebase-adminsdk-20uvl-9020e85b24.json"
db = firestore.Client()

def fetch_and_save_chatrooms_to_excel():
    # Firestore에서 new_chatrooms 컬렉션의 문서 가져오기
    chatrooms_ref = db.collection('new_chatrooms')
    chatrooms = chatrooms_ref.stream()

    # 엑셀 파일 작성
    writer = pd.ExcelWriter('chatrooms.xlsx', engine='openpyxl')

    for chatroom in chatrooms:
        chatroom_id = chatroom.id
        messages_ref = chatrooms_ref.document(chatroom_id).collection('new_messages')
        
        # new_messages 컬렉션에서 문서들 가져오기
        messages = messages_ref.order_by('timestamp').stream()

        # 데이터프레임에 메시지 저장
        data = []
        for message in messages:
            message_data = message.to_dict()
            # 타임스탬프를 UTC로 변환하고 시간대 정보를 제거
            timestamp = message_data.get('timestamp')
            if timestamp is not None:
                timestamp = timestamp.replace(tzinfo=None)
            
            # search_url을 쉼표로 구분된 문자열로 변환
            search_urls = message_data.get('search_url', [])
            search_urls_str = ', '.join(search_urls) if search_urls else ''

            data.append({
                'timestamp': timestamp,
                'content': message_data.get('content'),
                'is_search': message_data.get('is_search'),
                'role': message_data.get('role'),
                'search_url': search_urls_str
            })
        
        df = pd.DataFrame(data)

        # 각 chatroom_id로 시트 작성
        df.to_excel(writer, sheet_name=chatroom_id[:31], index=False)

    writer.close()

# 실행
fetch_and_save_chatrooms_to_excel()