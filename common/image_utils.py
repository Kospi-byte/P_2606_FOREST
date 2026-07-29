import cv2
import numpy as np
from common.env_config import (
    IMG_WIDTH,
    IMG_HEIGHT,
    NUMBER_WIDTH_L,
    NUMBER_WIDTH_R,
    NUMBER_WIDTH,
    NUMBER_HEIGHT,
    IMG_LENGTH
)

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


def predict_captcha(model, img_bytes):
    """모델과 바이트 이미지를 전달받아 캡차 문자열 예측 반환"""
    char_features = preprocess_captcha_from_bytes(img_bytes)
    if char_features is None:
        return None
    
    predictions = model.predict(char_features)
    return "".join(predictions)