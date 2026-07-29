import os
import cv2
import numpy as np
import joblib
from common.env_config import (
    IMG_WIDTH,
    IMG_HEIGHT,
    NUMBER_WIDTH_L,
    NUMBER_WIDTH_R,
    NUMBER_WIDTH,
    NUMBER_HEIGHT,
    IMG_LENGTH,    
    MODEL_PATH
)

def main():
    for i in range(1, 11):
        target_path = f'./data/target/target_{i:03d}.png'
        try:
            print(f"[{target_path}] Prediction Result: {result_img(target_path)}")
        except FileNotFoundError as e:
            print(f"Error processing {target_path}: {e}")
            
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

# [가중치로 결과 도출] 저장된 모델로 텍스트 예측
def result_img(img_path):
    target_img_path = img_path
    
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"⚠️ 학습된 모델 파일({MODEL_PATH})이 없습니다! learn_img()를 먼저 실행해 주세요.")
    if not os.path.exists(target_img_path):
        raise FileNotFoundError(f"⚠️ 타겟 이미지 파일({target_img_path})이 존재하지 않습니다.")

    # 저장된 머신러닝 모델을 순식간에 로드 (딥러닝 가중치 로드보다 압도적으로 빠름)
    model = joblib.load(MODEL_PATH)
    
    # 타겟 이미지 슬라이싱 및 전처리
    char_features = preprocess_captcha(target_img_path)
    
    # 6개 글자 각각 예측 수행
    predictions = model.predict(char_features)
    
    # 문자 리스트를 하나의 문자열로 결합하여 반환
    return "".join(predictions)

if __name__ == "__main__":
    main()