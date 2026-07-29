from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def process_reservation_step(driver, pred_text):
    """캡차 입력부터 약관 동의, 버튼 클릭, 알림창 확인까지 한 번에 처리"""
    # 1. 캡차 입력
    captcha_input = driver.find_element(By.ID, "atmtcRsrvtPrvntChrct")
    captcha_input.clear()
    captcha_input.send_keys(pred_text)
    
    # 2. 약관 동의 체크
    # 바로가기-통합예약-일반예약 체크박스   #chkAgree
    # 일반예약-선착순예약 의 체크박스       #arr_01
    agree_checkbox = driver.find_element(By.CSS_SELECTOR, '#chkAgree, #arr_01')
    if not agree_checkbox.is_selected():
        agree_checkbox.click()
        
    # 3. 신청 버튼 클릭
    submit_button = driver.find_element(By.ID, "btnRsrvt")
    submit_button.click()
    print("🔘 정보 입력 및 신청 버튼 클릭 완료.")
    
    # 4. 알림창 확인
    print("⏳ 브라우저 알림창 탐지 중...")
    WebDriverWait(driver, 3).until(EC.alert_is_present())
    alert = driver.switch_to.alert
    print(f"💬 알림창 내용: [{alert.text}]")
    alert.accept()
    print("✅ 알림창 [확인] 클릭 완료!")