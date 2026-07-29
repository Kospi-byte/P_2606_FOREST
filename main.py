# CLI
from common.make_url import get_url
import argparse

import os
import joblib
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# 분리된 커스텀 모듈에서 가져오기
from common.env_config import MODEL_PATH
from common.image_utils import predict_captcha
from common.web_utils import process_reservation_step

def main():
    # 1. 인자 파서 생성
    parser = argparse.ArgumentParser(description="P_2606_FOREST CLI 실행 프로그램")

    # 2. CLI 플래그 옵션 추가 (action="store_true"는 해당 옵션을 붙이면 True가 됨)
    parser.add_argument("--draw", action="store_true", help="draw 함수를 실행합니다.")
    parser.add_argument("--first", action="store_true", help="first 함수를 실행합니다.")

    # 3. 입력된 인자 파싱
    args = parser.parse_args()

    # 4. 입력된 인자에 따라 해당 함수 실행
    if args.draw:
        TARGET_URL = get_url('draw')
    if args.first:
        TARGET_URL = get_url('first')
    # 옵션을 둘 다 안 적었을 경우 안내 메시지 출력
    if not args.draw and not args.first:
        print("⚠️ 실행할 옵션을 입력해주세요.")
        parser.print_help()  # 도움말 출력    
        return
    
    # 2. 메인 루프 진행
    print("======= 숲나들e 자동 추첨 신청 시스템 (무한루프 버전) =======")    
    if not os.path.exists(MODEL_PATH):
        print(f"⚠️ 학습된 모델 파일({MODEL_PATH})이 존재하지 않습니다!")
        return
        
    print("💾 머신러닝 최적화 모델 로딩 중...")
    model = joblib.load(MODEL_PATH)
    
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1200,1000")
    # 1. 자동화 표시 및 경고창 제거
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    # 2. 실행 완료 후 브라우저 유지
    chrome_options.add_experimental_option("detach", True)
    # 3. 알림 팝업 차단 및 User-Agent 설정
    # chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")    
    
    print("🌐 브라우저를 구동합니다...")
    driver = webdriver.Chrome(options=chrome_options)    
    # 4. 봇 감지 스크립트 무력화 (드라이버 생성 바로 다음 호출)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"})
    
    try:
        # 대상 URL 접속
        driver.get(TARGET_URL)
        # 60자가 넘으면 앞 60자만 보여주고 뒤에 ... 붙이기
        short_url = TARGET_URL[:60] + "..." if len(TARGET_URL) > 60 else TARGET_URL
        print(f"🔗 접속 완료: {short_url}")
        print("\n💡 [안내] 로그인 및 신청 페이지 세팅을 완료해 주세요.")
        
        loop_count = 1
        
        # 🔄 무한 루프 시작
        while True:
            print("\n" + "-" * 50)
            print(f"🔄 [시도 횟수: {loop_count}회째] 매크로 대기 중...")
            print("= [Enter] : 즉시 캡차 풀고 자동 신청 진행")
            print("= [q + Enter] : 프로그램 안전하게 종료")
            print("-" * 50)
            
            user_command = input("👉 명령을 입력하세요: ").strip().lower()
            
            if user_command == 'q':
                print("\n👋 사용자가 종료를 요청했습니다. 프로그램을 안전하게 종료합니다.")
                break
                
            print("\n🚀 자동 신청 시퀀스 즉시 가동!")
            
            try:
                # 1) 캡차 스크린샷 및 모델 예측
                captcha_element = driver.find_element(By.ID, "captchaImg")
                img_bytes = captcha_element.screenshot_as_png
                
                pred_text = predict_captcha(model, img_bytes)
                if not pred_text:
                    print("❌ 캡차 이미지를 로드하는 데 실패했습니다. 다시 시도해 주세요.")
                    continue
                    
                print(f"🤖 AI 예측 결과 👉 [{pred_text}]")
                
                # 2) 폼 입력, 동의, 클릭, 알림창 확인 자동 수행
                process_reservation_step(driver, pred_text)
                
                loop_count += 1
                
            except Exception as e:
                print(f"⚠️ 이번 시도 중 오류가 발생하여 건너뜁니다. (이유: {e})")
                print("💡 페이지 상태나 로그인 세션을 확인한 뒤 다시 엔터를 눌러주세요.")
                continue

    finally:
        print("🔒 웹 브라우저를 닫는 중...")
        driver.quit()
        print("🏁 매크로 프로그램이 완전히 종료되었습니다.")


if __name__ == "__main__":
    main()