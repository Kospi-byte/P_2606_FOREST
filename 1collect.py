import os
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# 🔗 [수정 필수] 실제 수집하고자 하는 사이트의 로그인 또는 캡차가 표시되는 URL을 입력하세요.
TARGET_URL = "https://www.foresttrip.go.kr/rep/or/sssn/fcfsRsrvtSmplPssblGoodsDetls.do?_csrf=a2366c2c-65ce-4307-b0bd-30f76db51283&netfunnel_key=127A4DC992BD2B1EBF1816E08561DC22C626C9966723C139F0217908BB4DC1D596EB9561A9FD8847A8A00069D4C9459122CE8908AF0A06CA82C614162A2D88E5559C01BA4D3F4CD8C2EA8571C1C80B315E3B57A632317FB5338B22D89E9B8B70B62953366D8F61C3A2F7BAD4E036C81F302C312C302C30&srchInsttArcd=7&srchInsttId=ID02030116&srchRsrvtBgDt=20260715&srchRsrvtEdDt=20260716&srchStngNofpr=1&srchSthngCnt=1&srchWord=&srchUseDt=&houseCampSctin=&rsrvtPssblYn=N&rsrvtWtngSctin=01&srchHouseCharg=&srchCampCharg=&goodsClsscHouseCdArr=&goodsClsscCampCdArr=&srchInsttTpcd=&cmdogYn=N&bbqYn=N&dsprsYn=N&otsdWeterYn=N&wifiYn=N&snowPlaceYn=N&srchMyLtd=&srchMyLng=&srchDstnc=&gNowPage=1&srchGoodsId=&hmpgId=FRIP"
# 수집할 이미지 개수 지정 (우선 테스트용으로 10~20개 먼저 돌려보시는 걸 추천합니다)
TOTAL_IMAGES_TO_COLLECT = 10

def collect_captcha_images(target_url, save_dir='./data/learning', count=100):
    """
    웹 페이지의 캡차 이미지를 화면에 렌더링된 상태 그대로 캡처하여 저장합니다.
    """
    # 저장할 폴더 생성 (기존 학습 코드의 './sample' 폴더와 매칭)
    os.makedirs(save_dir, exist_ok=True)
    
    # 브라우저 옵션 설정
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
        print("💡 캡차 이미지가 완전히 로딩될 때까지 10초간 대기합니다...")
        # 직접 로그인
        print("🆔 로그인 해주세요...")
        time.sleep(10) 
        
        print(f"🚀 캡차 이미지 수집 시작 (목표 수량: {count}개)...")
        
        success_count = 0
        for i in range(1, count + 1):
            try:
                # 1. 캡차 이미지 엘리먼트 탐색 (id="captchaImg")
                captcha_element = driver.find_element(By.ID, "captchaImg")
                
                # 2. 파일명 지정 (나중에 수동으로 정답 숫자로 이름을 바꿀 수 있게 임시 이름 지정)
                # 예: ./sample/temp_0001.png
                file_path = os.path.join(save_dir, f"temp_{i:03d}.png")
                
                # 3. 화면에 보이는 엘리먼트 영역만 정확하게 스크린샷 저장
                captcha_element.screenshot(file_path)
                success_count += 1
                print(f"📸 [{success_count}/{count}] 이미지 저장 완료 -> {file_path}")
                
                # 4. 다음 이미지를 위한 새로고침 처리
                # (사이트에 '새로고침' 버튼이 따로 없다면 전체 페이지를 새로고침합니다)
                driver.refresh()
                
                # 차단 방지를 위해 사람처럼 조금씩 쉬어가며 요청 (2~3초 추천)
                time.sleep(random.randint(1,4))                
                
            except Exception as e:
                print(f"⚠️ {i}번째 수집 중 일시적 오류 발생, 재시도합니다... (오류: 로그인 여부 확인...)")
                # print(f"⚠️ {i}번째 수집 중 일시적 오류 발생, 재시도합니다... (오류: {e})")
                driver.refresh()
                time.sleep(3)
                
    finally:
        # 모든 수집이 끝나면 브라우저를 안전하게 닫음
        driver.quit()
        print("\n==================================================")
        print(f"✅ 수집 프로세스 종료! 총 {success_count}개의 이미지가 수집되었습니다.")
        print(f"📂 저장 경로: {os.path.abspath(save_dir)}")
        print("👉 이제 폴더를 열고 이미지 안의 숫자를 보며 파일명을 정답(예: 123456.png)으로 수정하세요!")
        print("==================================================")

if __name__ == "__main__":
    # # 🔗 [수정 필수] 실제 수집하고자 하는 사이트의 로그인 또는 캡차가 표시되는 URL을 입력하세요.
    # TARGET_URL = "https://www.foresttrip.go.kr/rep/drlts/month/drltsRqestPssblGoodsDetls.do?_csrf=09768238-2956-4d61-9902-447cd36d1040&srchInsttArcd=1&srchInsttId=ID02030031&srchRsrvtBgDt=20260728&srchRsrvtEdDt=20260729&srchStngNofpr=2&srchSthngCnt=1&srchWord=&srchUseDt=26%2F07%2F28%28%ED%99%94%29+-+26%2F07%2F29%28%EC%88%98%29&houseCampSctin=&rsrvtPssblYn=&srchHouseCharg=&srchCampCharg=&goodsClsscHouseCdArr=&goodsClsscCampCdArr=&srchInsttTpcd=&cmdogYn=N&bbqYn=N&dsprsYn=N&otsdWeterYn=N&wifiYn=N&snowPlaceYn=N&srchMyLtd=&srchMyLng=&srchDstnc=&nowPage=1&hmpgId=FRIP&polcySctin=02007&infoFlag=" 
    
    # # 수집할 이미지 개수 지정 (우선 테스트용으로 10~20개 먼저 돌려보시는 걸 추천합니다)
    # TOTAL_IMAGES_TO_COLLECT = 10
    
    collect_captcha_images(TARGET_URL, save_dir='./data/learning', count=TOTAL_IMAGES_TO_COLLECT)