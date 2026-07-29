import os
import time
import random
import cv2
import numpy as np
import joblib
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

import dotenv, re
from datetime import datetime, timedelta

# .env 파일 로드
dotenv.load_dotenv()

# ==================================================
# 1. 글로벌 설정 값 (데이터 그림파일, 여백 제거, 폴더 경로)
# ==================================================
# .env 파일 로드
from common.env_config import get_env_int, get_env_str
IMG_WIDTH = get_env_int("IMG_WIDTH", 130)
IMG_HEIGHT = get_env_int("IMG_HEIGHT", 35)
NUMBER_WIDTH_L = get_env_int("DEL_WIDTH_L", 8) # 숫자가 시작하는 픽셀 (좌여백 제거용)
NUMBER_WIDTH_R = IMG_WIDTH - get_env_int("DEL_WIDTH_R", 14) # 숫자가 끝나는 픽셀 (우여백 제거용)
NUMBER_WIDTH = NUMBER_WIDTH_R - NUMBER_WIDTH_L # IMG_LENGTH = 6 나누기 위해 6의 배수 맞춤
NUMBER_HEIGHT = IMG_HEIGHT - get_env_int("DEL_WIDTH_B", 9) # (하여백 제거용)
IMG_LENGTH = get_env_int("COUNT_OF_NUMBER", 6) # 글자수
MODEL_PATH = get_env_str("MODEL_PATH", "./model/captcha_ml_model.pkl")
# 최종 정답 데이터가 저장될 폴더
LEARNING_DIR = get_env_str("IMG_FOLDER_PATH", "./data/learning")

# ==================================================
# 2. URL 자동 생성 (Today +30D)
# ==================================================
# 1) 날짜 계산
bg_date = (datetime.now() + timedelta(days=30)).strftime("%Y%m%d")
ed_date = (datetime.now() + timedelta(days=31)).strftime("%Y%m%d")
base_url = os.getenv("BASE_URL")
# 2) 정규식 패턴으로 날짜 교체
new_url = re.sub(r"srchRsrvtBgDt=\d{8}", f"srchRsrvtBgDt={bg_date}", base_url)
new_url = re.sub(r"srchRsrvtEdDt=\d{8}", f"srchRsrvtEdDt={ed_date}", new_url)
TARGET_URL = new_url
TOTAL_IMAGES_TO_COLLECT = int(os.getenv("AUTO_DATA_TO_COLLECT",'10')) # # 한 세션에 레이블링할 이미지 개수

# ==========================================
# 2. 이미지 전처리 함수 (파일 경로 대신 바이너리 데이터 직접 처리)
# ==========================================
def preprocess_captcha_from_bytes(img_bytes):
    """셀레니움이 캡처한 이미지 바이트 데이터를 메모리 상에서 바로 전처리"""
    # 바이트 배열을 OpenCV 이미지 객체로 디코딩
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    
    if img is None:
        return None
    
    # 기존 여백 제거 로직 적용
    img = cv2.resize(img, (IMG_WIDTH, IMG_HEIGHT))
    img = img[:NUMBER_HEIGHT, NUMBER_WIDTH_L : NUMBER_WIDTH_R]
    img = img.astype(np.float32) / 255.0
    
    char_width = NUMBER_WIDTH // IMG_LENGTH
    char_images = []
    
    for i in range(IMG_LENGTH):
        start_x = i * char_width
        end_x = start_x + char_width
        char_img = img[:, start_x:end_x]
        char_images.append(char_img.flatten())
        
    return np.array(char_images)


# ==========================================
# 3. 실시간 액티브 러닝 코어 함수
# ==========================================
def active_learning_collector(target_url, count=10):
    os.makedirs(LEARNING_DIR, exist_ok=True)
    
    # 1) 가중치 모델 로드
    if not os.path.exists(MODEL_PATH):
        print(f"⚠️ 모델 파일({MODEL_PATH})이 없습니다. 빈 가중치 파일이라도 생성 후 진행하세요.")
        return
    print("💾 머신러닝 모델 로드 완료.")
    model = joblib.load(MODEL_PATH)
    
    # 2) 셀레니움 브라우저 설정 및 시작
    chrome_options = Options()
    # 크롬 상단에 "자동화된 테스트 소프트웨어에 의해 제어되고 있습니다" 문구 숨기기
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # 웹 브라우저(Chrome) 실행
    print("🌐 브라우저를 시작하는 중...")
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # 대상 URL 접속
        driver.get(target_url)
        print(f"🔗 접속 완료: {target_url}")
        print("🆔 캡차 화면이 나오도록 로그인 및 페이지 이동을 완료해 주세요 ...")
        # 직접 로그인
        print("🆔 로그인 해주세요...")
        time.sleep(10) 
        
        print(f"\n🚀 실시간 반자동 레이블링 시작 (목표 수량: {count}개)...")
        print("=" * 70)
        print(" [방법] 예측이 맞으면 [Enter], 틀리면 [6자리 정답 입력], 종료하려면 [q]")
        print("=" * 70)
        
        success_count = 0
        loop_idx = 1
        
        while success_count < count:
            try:
                # 캡차 엘리먼트 가져오기
                captcha_element = driver.find_element(By.ID, "captchaImg")
                
                # 💡 디스크에 임시 저장하지 않고 이미지 바이트를 통째로 가져옴 (속도 향상 및 찌꺼기 방지)
                img_bytes = captcha_element.screenshot_as_png
                
                # 머신러닝 모델 예측을 위한 전처리 수행
                char_features = preprocess_captcha_from_bytes(img_bytes)
                if char_features is None:
                    print("⚠️ 이미지 데이터를 읽을 수 없습니다. 페이지를 새로고침합니다.")
                    driver.refresh()
                    time.sleep(3)
                    continue
                
                # 모델 예측 수행
                predictions = model.predict(char_features)
                pred_text = "".join(predictions)
                
                # 사용자 인터랙션 인터페이스
                print(f"\n🔍 [시도 {loop_idx}] ------------------------------------")
                print(f"🤖 현재 캡차 이미지에 대한 모델 예측 👉 [{pred_text}]")
                user_input = input("정답입니까? (맞으면 [Enter] / 틀리면 [6자리 입력] / 종료 [q]): ").strip()
                
                if user_input.lower() == 'q':
                    print("\n👋 사용자가 작업을 중단했습니다.")
                    break
                
                # 정답 라벨 결정
                if user_input == "":
                    final_label = pred_text
                    print(f"✅ 예측 성공! [{final_label}] 데이터를 저장합니다.")
                else:
                    if len(user_input) != IMG_LENGTH or not user_input.isdigit():
                        print("❌ 입력 오류! 6자리 숫자만 입력 가능합니다. 현재 이미지는 건너뜁니다.")
                        driver.refresh()
                        time.sleep(2)
                        loop_idx += 1
                        continue
                    final_label = user_input
                    print(f"✍️ 수동 수정 완료! 오답 수정 결과 -> [{final_label}]")
                
                # 중복 파일명 방지 처리 및 저장
                file_path = os.path.join(LEARNING_DIR, f"{final_label}.png")
                if os.path.exists(file_path):
                    dup_count = 1
                    while os.path.exists(os.path.join(LEARNING_DIR, f"{final_label}_{dup_count}.png")):
                        dup_count += 1
                    file_path = os.path.join(LEARNING_DIR, f"{final_label}_{dup_count}.png")
                
                # 캡차 이미지 엘리먼트 파일로 최종 확정 저장
                captcha_element.screenshot(file_path)
                success_count += 1
                print(f"📸 학습 데이터 구축 완료 ({success_count}/{count}) -> {file_path}")
                
                # 다음 이미지 수집을 위한 웹페이지 새로고침 및 대기
                driver.refresh()
                loop_idx += 1
                time.sleep(random.randint(2, 4))
                
            except Exception as e:
                print(f"⚠️ 캡차 엘리먼트를 찾지 못했거나 오류 발생. 재시도 중... (로그인 상태 확인 요망)")
                driver.refresh()
                time.sleep(3)
                loop_idx += 1
                
    finally:
        driver.quit()
        print("\n==================================================")
        print(f"🎉 반자동 실시간 수집 완료! 총 {success_count}개의 고품질 데이터 구축.")
        print(f"📂 저장된 폴더: {os.path.abspath(LEARNING_DIR)}")
        print("💡 이제 기존 머신러닝 학습 코드를 돌려 모델 성능을 한 단계 올리세요!")
        print("==================================================")

if __name__ == "__main__":
    active_learning_collector(TARGET_URL, count=TOTAL_IMAGES_TO_COLLECT)