import cv2
import base64
import numpy as np
import config

def text (text, H=config.THUMB_HEIGHT, W=config.THUMB_WIDTH):
    image = np.zeros((H, W, 3), np.uint8)
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(image, text, (10, 50), font, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
    return image

def empty (H=config.THUMB_HEIGHT, W=config.THUMB_WIDTH):
    return np.zeros((H, W, 3), np.uint8)


def base64_encode (image):
    buf = cv2.imencode('.png', image)[1].tobytes()
    buf = base64.b64encode(buf)
    return buf.decode('ascii')

def read_base64 (path):
    try:
        with open(path, 'rb') as f:
            return base64.b64encode(f.read()).decode('ascii')
    except Exception as e:        
        return None
    
    