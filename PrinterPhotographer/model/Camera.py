import cv2


class Camera:
    def __init__(self, cam, w,h):
        self.cap = None
        self.last_frame = None
        self.cam_num = cam
        self.resolution_w = w
        self.resolution_h = h

    def initialize(self):
        self.cap = cv2.VideoCapture(self.cam_num, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FPS, 40)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution_w)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution_h)

    def get_frame(self):
        ret, self.last_frame = self.cap.read()
        return self.last_frame

    def close_camera(self):
        self.cap.release()

    def __str__(self):
        return 'OpenCV Camera {}'.format(self.cam_num)