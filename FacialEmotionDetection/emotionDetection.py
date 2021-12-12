from keras.models import load_model
from time import sleep
from keras.preprocessing.image import img_to_array
from keras.preprocessing import image
import cv2
import numpy as np


face_classifier = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
classifier = load_model('model.h5')
emotion_labels = ['enfadat', 'disgust', 'por', 'alegria', 'neutralitat', 'tristesa', 'sorpresa']


def get_emotion(path):
    """Donat un string on contingui el path d'una imatge (he provat amb format jpg) retorna un string;
    una label d'entre les emotion_labels."""
    frame = cv2.imread(path, 0)
    faces = face_classifier.detectMultiScale(frame)
    
    (x,y,w,h) = faces[0]
    cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,255),2)
    roi_gray = frame[y:y+h,x:x+w]
    roi_gray = cv2.resize(roi_gray,(48,48),interpolation=cv2.INTER_AREA)

    if np.sum([roi_gray])!=0:
        roi = roi_gray.astype('float')/255.0
        roi = img_to_array(roi)
        roi = np.expand_dims(roi, axis=0)

        prediction = classifier.predict(roi)[0]
        return emotion_labels[prediction.argmax()], prediction
    raise Exception('No hem pogut extreure emocions :(')
