import os
import cv2
import numpy as np
import joblib
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ==========================================
# 1. 글로벌 설정 값 (기존 규격 및 여백 제거 로직 유지)
# ==========================================
IMG_WIDTH = 130
IMG_HEIGHT = 35
NUMBER_WIDTH_L = 8
NUMBER_WIDTH_R = IMG_WIDTH - 14
NUMBER_WIDTH = NUMBER_WIDTH_R - NUMBER_WIDTH_L
NUMBER_HEIGHT = IMG_HEIGHT - 9
IMG_LENGTH = 6

MODEL_PATH = './model/captcha_ml_model.pkl'
TARGET_URL = "https://www.foresttrip.go.kr/rep/or/sssn/fcfsRsrvtSmplPssblGoodsDetls.do?_csrf=a2366c2c-65ce-4307-b0bd-30f76db51283&netfunnel_key=127A4DC992BD2B1EBF1816E08561DC22C626C9966723C139F0217908BB4DC1D596EB9561A9FD8847A8A00069D4C9459122CE8908AF0A06CA82C614162A2D88E5559C01BA4D3F4CD8C2EA8571C1C80B315E3B57A632317FB5338B22D89E9B8B70B62953366D8F61C3A2F7BAD4E036C81F302C312C302C30&srchInsttArcd=7&srchInsttId=ID02030116&srchRsrvtBgDt=20260715&srchRsrvtEdDt=20260716&srchStngNofpr=1&srchSthngCnt=1&srchWord=&srchUseDt=&houseCampSctin=&rsrvtPssblYn=N&rsrvtWtngSctin=01&srchHouseCharg=&srchCampCharg=&goodsClsscHouseCdArr=&goodsClsscCampCdArr=&srchInsttTpcd=&cmdogYn=N&bbqYn=N&dsprsYn=N&otsdWeterYn=N&wifiYn=N&snowPlaceYn=N&srchMyLtd=&srchMyLng=&srchDstnc=&gNowPage=1&srchGoodsId=&hmpgId=FRIP"


# ==========================================
# 2. 이미지 전처리 함수
# ==========================================
def preprocess_captcha_from_bytes(img_bytes):
    """셀레니움이 캡처한 이미지 바이트 데이터를 메모리 상에서 바로 전처리"""
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    
    if img is None:
        return None
    
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
# 3. 메인 자동화 프로세스
# ==========================================
def main():
    print("======= 숲나들e 자동 추첨 신청 시스템 (무한루프 버전) =======")
    
    if not os.path.exists(MODEL_PATH):
        print(f"⚠️ 학습된 모델 파일({MODEL_PATH})이 존재하지 않습니다!")
        return
        
    print("💾 머신러닝 최적화 모델 로딩 중...")
    model = joblib.load(MODEL_PATH)
    
    chrome_options = Options()
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    print("🌐 브라우저를 구동합니다...")
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        driver.get(TARGET_URL)
        print(f"🔗 접속 완료: {TARGET_URL}")
        print("\n💡 [안내] 로그인 및 신청 페이지 세팅을 완료해 주세요.")
        
        loop_count = 1
        
        # 🔄 무한 루프 시작
        while True:
            print("\n" + "="*50)
            print(f"🔄 [시도 횟수: {loop_count}회째] 매크로 대기 중...")
            print("= [Enter] : 즉시 캡차 풀고 자동 신청 진행")
            print("= [q + Enter] : 프로그램 안전하게 종료")
            print("="*50)
            
            # 사용자의 입력을 대기
            user_command = input("👉 명령을 입력하세요: ").strip().lower()
            
            # 🛑 'q' 입력 시 무한 루프 탈출 및 브라우저 종료
            if user_command == 'q':
                print("\n👋 사용자가 종료를 요청했습니다. 프로그램을 안전하게 종료합니다.")
                break
                
            print("\n🚀 자동 신청 시퀀스 즉시 가동!")
            
            try:
                # 1) 캡차 이미지 엘리먼트 스크린샷 및 예측
                captcha_element = driver.find_element(By.ID, "captchaImg")
                img_bytes = captcha_element.screenshot_as_png
                
                char_features = preprocess_captcha_from_bytes(img_bytes)
                if char_features is None:
                    print("❌ 캡차 이미지를 로드하는 데 실패했습니다. 다시 시도해 주세요.")
                    continue
                    
                predictions = model.predict(char_features)
                pred_text = "".join(predictions)
                print(f"🤖 AI 예측 결과 👉 [{pred_text}]")
                
                # 2) 예측한 6자리 숫자를 입력창에 입력
                captcha_input = driver.find_element(By.ID, "atmtcRsrvtPrvntChrct")
                captcha_input.clear()
                captcha_input.send_keys(pred_text)
                
                # 3) 약관에 동의합니다 체크 박스 체크하기
                agree_checkbox = driver.find_element(By.ID, "arr_01")
                if not agree_checkbox.is_selected():
                    agree_checkbox.click()
                    
                # 4) 추첨 신청하기 버튼 누르기
                submit_button = driver.find_element(By.ID, "btnRsrvt")
                submit_button.click()
                print("🔘 정보 입력 및 신청 버튼 클릭 완료.")
                
                # 5) '추첨 신청하시겠습니까?' alert/confirm 창 자동 확인
                print("⏳ 브라우저 알림창 탐지 중...")
                WebDriverWait(driver, 3).until(EC.alert_is_present())
                alert = driver.switch_to.alert
                print(f"💬 알림창 내용: [{alert.text}]")
                alert.accept()
                print("✅ 알림창 [확인] 클릭 완료!")
                
                loop_count += 1
                
            except Exception as e:
                # 개별 시도 중 에러가 나더라도 전체 루프가 터지지 않게 예외 처리
                print(f"⚠️ 이번 시도 중 오류가 발생하여 건너뜁니다. (이유: {e})")
                print("💡 페이지 상태나 로그인 세션을 확인한 뒤 다시 엔터를 눌러주세요.")
                continue

    finally:
        # q를 누르거나 에러가 나서 정상 탈출 시 브라우저를 닫음
        print("🔒 웹 브라우저를 닫는 중...")
        driver.quit()
        print("🏁 매크로 프로그램이 완전히 종료되었습니다.")


if __name__ == "__main__":
    main()