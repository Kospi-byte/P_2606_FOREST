import os
from pathlib import Path
import dotenv

# 1. 프로젝트 루트 경로 및 .env 파일 위치 자동 탐색
# (common 폴더의 부모 폴더 = 프로젝트 최상위 루트)
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

# 2. .env 파일 강제 로드
dotenv.load_dotenv(dotenv_path=ENV_PATH)

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

# --------------------------------------------------
# 4. 글로벌 설정 값 (데이터 그림파일, 여백 제거, 폴더 경로)
# --------------------------------------------------

# [이미지 전처리 및 학습 관련 설정]
IMG_WIDTH = get_env_int("IMG_WIDTH", 130)
IMG_HEIGHT = get_env_int("IMG_HEIGHT", 35)
NUMBER_WIDTH_L = get_env_int("DEL_WIDTH_L", 8) # 숫자가 시작하는 픽셀 (좌여백 제거용)
NUMBER_WIDTH_R = IMG_WIDTH - get_env_int("DEL_WIDTH_R", 14) # 숫자가 끝나는 픽셀 (우여백 제거용)
NUMBER_WIDTH = NUMBER_WIDTH_R - NUMBER_WIDTH_L # IMG_LENGTH = 6 나누기 위해 6의 배수 맞춤
NUMBER_HEIGHT = IMG_HEIGHT - get_env_int("DEL_WIDTH_B", 9) # (하여백 제거용)
IMG_LENGTH = get_env_int("COUNT_OF_NUMBER", 6) # 글자수

# [경로 관련 설정]
IMG_FOLDER_PATH = get_env_str("IMG_FOLDER_PATH", "./data/learning")
IMG_PATH = get_env_str("IMG_PATH", "./data/learning/*.png")
MODEL_FOLDER_PATH = get_env_str("MODEL_FOLDER_PATH", "./model")
MODEL_PATH = get_env_str("MODEL_PATH", "./model/captcha_ml_model.pkl")

# 1collect.py 학습데이터 수집하기
TOTAL_IMAGES_TO_COLLECT = 5
# 4active_learning.py 반자동 데이터 레이블링
AUTO_DATA_TO_COLLECT = 5