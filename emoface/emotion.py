import cv2
from deepface import DeepFace

class Emotion():
    def __init__(self):
        super(Emotion, self).__init__()
        self.webcam_id = 1
        # self.vc = cv2.VideoCapture(self.webcam_id)
        self.valid_emotions = ['angry', 'happy', 'sad', 'surprise']

    def detect(self):
        if self.vc.isOpened():
            rval, frame = self.vc.read()
            try:
                result = DeepFace.analyze(frame, actions=['emotion'])['emotion']
                max_prob = None
                max_emo = None
                for e in result.keys():
                    if (e in self.valid_emotions) and (max_emo == None or result[e] > max_prob):
                        max_emo = e
                        max_prob = result[e]
                if max_emo == 'surprise':
                    max_emo += 'd'
                return max_emo
            except ValueError as e:
                return "happy"
        else:
            return "happy"

    def start_camera(self):
        if self.vc == None:
            self.vc = cv2.VideoCapture(self.webcam_id)

    def stop_camera(self):
        if self.vc != None:
            self.vc.release()
            self.vc = None