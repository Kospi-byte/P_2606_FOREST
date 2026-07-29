import os
import glob
import cv2
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier

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
IMG_PATH = get_env_str("IMG_PATH", "./data/learning/*.png")
MODEL_FOLDER_PATH = get_env_str("MODEL_FOLDER_PATH", "./model")
MODEL_PATH = get_env_str("MODEL_PATH", "./model/captcha_ml_model.pkl")

# # ==================================================
# # 1. 글로벌 설정 값 (데이터 그림파일, 여백 제거, 폴더 경로)
# # ==================================================
# IMG_WIDTH = int(os.getenv("IMG_WIDTH", '130'))
# IMG_HEIGHT = int(os.getenv("IMG_HEIGHT", '35'))
# NUMBER_WIDTH_L = int(os.getenv("DEL_WIDTH_L", '8')) # 숫자가 시작하는 픽셀 (좌여백 제거용)
# NUMBER_WIDTH_R = IMG_WIDTH - int(os.getenv("DEL_WIDTH_R", '14')) # 숫자가 끝나는 픽셀 (우여백 제거용)
# NUMBER_WIDTH = NUMBER_WIDTH_R - NUMBER_WIDTH_L # IMG_LENGTH = 6 나누기 위해 6의 배수 맞춤
# NUMBER_HEIGHT = IMG_HEIGHT - int(os.getenv("DEL_WIDTH_B", '9')) # (하여백 제거용)
# IMG_LENGTH = int(os.getenv("COUNT_OF_NUMBER", '6')) # 글자수
# MODEL_PATH = os.getenv("MODEL_PATH", "./model/captcha_ml_model.pkl")

def main():    
    # 1. 학습    
    learn_img(IMG_PATH) 

# 캡차 이미지를 문자 단위로 균등하게 6등분하여 자르고 데이터화하는 함수
def preprocess_captcha(img_path):
    # 흑백 이미지로 읽기
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"⚠️ 이미지를 찾을 수 없습니다: {img_path}")
    
    # 이미지 크기 강제 고정
    img = cv2.resize(img, (IMG_WIDTH, IMG_HEIGHT))
    
    # 이미 (좌우하) 여백 제거 (숫자만 남김)
    img = img[:NUMBER_HEIGHT, NUMBER_WIDTH_L : NUMBER_WIDTH_R]
    
    # 픽셀 값 정규화 (0~1 사이)
    img = img.astype(np.float32) / 255.0
    
    # 가로 길이를 글자 수(6)만큼 등분하여 슬라이싱    
    char_width = NUMBER_WIDTH // IMG_LENGTH
    char_images = []
    
    for i in range(IMG_LENGTH):
        start_x = i * char_width
        end_x = start_x + char_width
        char_img = img[:, start_x:end_x]
        
        # 최신 머신러닝 입력용으로 2차원 이미지를 1차원 배열(픽셀 피처)로 평탄화(Flatten)
        char_images.append(char_img.flatten())
        
    return np.array(char_images)

# [이미지 학습] 머신러닝 모델 생성 및 학습
def learn_img(img_path):
    img_path_list = glob.glob(img_path)
    if not img_path_list:
        print("⚠️ 학습용 샘플 이미지들(./sample/*.png)이 없습니다.")
        return
    
    print(f"📦 {len(img_path_list)}개의 데이터로 머신러닝 학습을 시작합니다...")
    
    X_train = []
    y_train = []
    
    for path in img_path_list:
        label_text = os.path.splitext(os.path.basename(path))[0]
        if len(label_text) != IMG_LENGTH:
            continue
            
        try:
            # 6개로 쪼개진 이미지 픽셀 데이터 배열 가져오기
            char_features = preprocess_captcha(path)
            
            # 각 자리의 문자 추출하여 정답(Label) 리스트에 추가
            for i, char in enumerate(label_text):
                X_train.append(char_features[i])
                y_train.append(char)
        except Exception:
            continue
            
    if not X_train:
        print("⚠️ 유효한 학습 데이터가 데이터셋에 존재하지 않습니다.")
        return

    X_train = np.array(X_train)
    y_train = np.array(y_train)

    # 빠르고 정확한 전통 머신러닝 알고리즘인 'Random Forest' 분류기 사용
    # n_estimators를 조절하여 예측 속도와 정확도의 밸런스를 맞춥니다.
    model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    
    # 모델 저장
    if not os.path.exists(MODEL_FOLDER_PATH):
        os.makedirs(MODEL_FOLDER_PATH)
    
    joblib.dump(model, MODEL_PATH)
    print(f"💾 머신러닝 모델 저장 완료! ({MODEL_PATH})")

if __name__ == "__main__":
    main()