from datetime import datetime, timedelta
import os, re

import dotenv
# .env 파일 로드
dotenv.load_dotenv()

def get_url(mode: str) -> str:
    """인자('draw' 또는 'first')에 따라 해당하는 인터넷 주소(url)를 반환하는 함수"""

    # 1. 인자 소문자 변환 및 공백 제거 (입력 실수 방지)
    clean_mode = mode.strip().lower()

    # 2. 인자에 따른 주소 매핑 (예시 주소)
    if clean_mode == "draw":
        url = os.getenv("DRAW_URL")
    elif clean_mode == "first":        
        # ==================================================
        # 2. URL 자동 생성 (Today +30D)
        # ==================================================
        base_url = os.getenv("FIRST_URL")
        # 1) 날짜 계산
        bg_date = (datetime.now() + timedelta(days=30)).strftime("%Y%m%d")
        ed_date = (datetime.now() + timedelta(days=31)).strftime("%Y%m%d")
        # 2) 정규식 패턴으로 날짜 교체
        url = re.sub(r"srchRsrvtBgDt=\d{8}", f"srchRsrvtBgDt={bg_date}", base_url)
        url = re.sub(r"srchRsrvtEdDt=\d{8}", f"srchRsrvtEdDt={ed_date}", url)
    else:
        # 지정된 인자 외의 값이 들어왔을 때 예외 처리
        raise ValueError(
            f"⚠️ 유효하지 않은 인자입니다: '{mode}'. ('draw' 또는 'first'만 가능합니다.)"
        )

    return url