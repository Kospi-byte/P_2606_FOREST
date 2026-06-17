0. '26.6/6 숲나들e 캡챠 자동화
    배경 : https://gam860720.tistory.com/532

1. collect.py 학습데이터 수집하기 
1) TARGET_URL, TOTAL_IMAGES_TO_COLLECT 수정
   접속가능 URL 찾는법 - 숲나들e 메인에서 추첨신청 or 일반예약
   추첨신청은 안되는 기간이 있어서 그때는 일반예약   
2) 중간에 로그인 직접 해야함 (10초)

2. learning.py 학습하기

3. validation.py 검증하기
1) data/target 데이터로 성능검증
2) TARGET_PATH = './data/target/target_001.png' 수정

4. 4active_learning.py 반자동 데이터 레이블링
1) TARGET_URL, TOTAL_IMAGES_TO_COLLECT 수정   
2) 중간에 로그인 직접 해야함 (10초)

5. main.py 작동시키기

99. 기타
1) old/learning.py & main.py 는 데이터 그림 전체 (130*35) 로 학습과 실행
2) 성능 저하 이슈로 배경은 삭제하고 숫자 영역만 사용하는 코드로 변경