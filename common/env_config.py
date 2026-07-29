import os
from pathlib import Path
from dotenv import load_dotenv

# 1. 프로젝트 루트 경로 및 .env 파일 위치 자동 탐색
# (common 폴더의 부모 폴더 = 프로젝트 최상위 루트)
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

# 2. .env 파일 강제 로드
load_dotenv(dotenv_path=ENV_PATH)

# -------------------------------------------------------------
# 3. 안전한 타입 변환 헬퍼 함수들 (NoneType / ValueError 방지용)
# -------------------------------------------------------------
def get_env_int(key: str, default: int = 0) -> int:
    val = os.getenv(key)
    try:
        return int(val) if val is not None else default
    except (ValueError, TypeError):
        return default

def get_env_str(key: str, default: str = "") -> str:
    return os.getenv(key, default)

# def _get_int(key: str, default: int = 0) -> int:
#     val = os.getenv(key)
#     try:
#         return int(val) if val is not None else default
#     except (ValueError, TypeError):
#         return default

# def _get_str(key: str, default: str = "") -> str:
#     return os.getenv(key, default)

# def _get_float(key: str, default: float = 0.0) -> float:
#     val = os.getenv(key)
#     try:
#         return float(val) if val is not None else default
#     except (ValueError, TypeError):
#         return default

# def _get_bool(key: str, default: bool = False) -> bool:
#     val = os.getenv(key)
#     if val is None:
#         return default
#     return val.strip().lower() in ("true", "1", "yes")

# -------------------------------------------------------------
# 4. 각 실행 파일에서 가져다 쓸 전역 상수(Config) 정의
# -------------------------------------------------------------

# # [이미지 전처리 및 학습 관련 설정]
# IMG_WIDTH = _get_int("IMG_WIDTH", 130)
# IMG_HEIGHT = _get_int("IMG_HEIGHT", 35)
# NUMBER_WIDTH_L = _get_int("NUMBER_WIDTH_L", 8)
# DEL_WIDTH_R = _get_int("DEL_WIDTH_R", 14)
# DEL_HEIGHT = _get_int("DEL_HEIGHT", 9)
# IMG_LENGTH = _get_int("IMG_LENGTH", 6)

# # [연산된 상수 (코드 내 자동 계산)]
# NUMBER_WIDTH_R = IMG_WIDTH - DEL_WIDTH_R
# NUMBER_WIDTH = NUMBER_WIDTH_R - NUMBER_WIDTH_L
# NUMBER_HEIGHT = IMG_HEIGHT - DEL_HEIGHT

# # [경로 관련 설정]
# IMG_PATH = _get_str("IMG_PATH", "./data/learning/*.png")
# MODEL_FOLDER_PATH = _get_str("MODEL_FOLDER_PATH", "./model")
# MODEL_PATH = _get_str("MODEL_PATH", "./model/captcha_ml_model.pkl")

# # [예약 및 네트워크 관련 설정 (필요시 추가)]
# BASE_URL = _get_str("BASE_URL", "")
# RESERVATION_DAYS_OFFSET = _get_int("RESERVATION_DAYS_OFFSET", 30)
# # HEADLESS = _get_bool("HEADLESS", False)