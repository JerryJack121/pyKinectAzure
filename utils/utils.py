import numpy as np
import cv2
import time
import datetime


class Util:
    def __init__(self, width, height, _time, exercise_mode=None, side = None):  # (寬，高，遊戲時間，運動種類，左/右半身)
        
        self.Joint_ID = {'PELVIS':0, 'SPINE_NAVAL':1, 'SPINE_CHEST':2, 'NECK':3, 'CLAVICLE_LEFT':4, 'SHOULDER_LEFT':5,
                    'ELBOW_LEFT':6, 'WRIST_LEFT':7, 'HAND_LEFT':8, 'HANDTIP_LEFT':9, 'THUMB_LEFT':10,
                    'CLAVICLE_RIGHT':11, 'SHOULDER_RIGHT':12, 'ELBOW_RIGHT':13, 'WRIST_RIGHT':14, 'HAND_RIGHT':15,
                    'HANDTIP_RIGHT':16, 'THUMB_RIGHT':17, 'HIP_LEFT':18, 'KNEE_LEFT':19, 'ANKLE_LEFT':20,
                    'FOOT_LEFT':21, 'HIP_RIGHT':22, 'KNEE_RIGHT':23, 'ANKLE_RIGHT':24, 'FOOT_RIGHT':25,
                    'HEAD':26, 'NOSE':27, 'EYE_LEFT':28, 'EAR_LEFT':29, 'EYE_RIGHT':30, 'EAR_RIGHT':31}

        self.width = width
        self.height = height

        self.exercise_mode = exercise_mode  # 運動模式
        self.side = side    # 左半身/右半身(若有分的話)
        self.stage = None   # 運動狀態
        self.counter = 0    # 運動完成次數

        self.game_start = False
        self.game_stop = False
        self.game_start_time = None # 遊戲開始時間
        self.game_time = datetime.timedelta(seconds=_time)   # 遊戲持續時間

    def update(self, skeleton2D, skeleton3D):

        self.joints_2d = {}
        self.joints_3d = {}
        for key, value in self.Joint_ID.items():
            self.joints_2d[key] = skeleton2D.joints2D[value].position
            self.joints_3d[key] = skeleton3D[value]

    # 顯示3維關節座標在輸出影像上
    def show_coordinate_on_2Dimage(self, joints):
        for joint in joints:
            coordinate = (int(self.joints_2d[joint].xy.x),int(self.joints_2d[joint].xy.y))
            text = '({:.1f}, {:.1f}, {:.1f})'.format(self.joints_3d[joint].x, self.joints_3d[joint].y, self.joints_3d[joint].z)
            cv2.putText(self.combined_image, text, coordinate, cv2.FONT_HERSHEY_COMPLEX, 0.35, (0, 255, 0), 1, cv2.LINE_AA)


    # 計算關節角度並輸出在影像上
    def show_angel_on_2Dimage(self, abc_joint):

        # 計算關節角度
        angel = calculate_angle(self.joints_3d[abc_joint[0]], self.joints_3d[abc_joint[1]], self.joints_3d[abc_joint[2]])
        angel = round(angel, 1) # 四捨五入

        center_joint = abc_joint[1]
        coordinate_x = int(self.joints_2d[center_joint].xy.x)
        coordinate_y = int(self.joints_2d[center_joint].xy.y)
        cv2.putText(self.combined_image, str(angel), (coordinate_x,coordinate_y+20), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 1, cv2.LINE_AA)

        return angel



    # 計算動作完成次數
    def cal_exercise(self):

        if self.exercise_mode == 'Lift_Dumbbells':

            if self.side == 'Right':
                abc_joint = ['SHOULDER_RIGHT', 'ELBOW_RIGHT', 'WRIST_RIGHT']
            elif self.side == 'Left':
                abc_joint = ['SHOULDER_LEFT', 'ELBOW_LEFT', 'WRIST_LEFT']
            
            # 計算關節角度並輸出在影像上
            angel = self.show_angel_on_2Dimage(abc_joint)

            if angel >= 110:
                self.stage = 'Down'
            if angel <= 70 and self.stage == 'Down':
                self.stage = 'Up'
                self.counter += 1
        
        elif self.exercise_mode == 'Stand_Sit':

            abc_joint1  = ['HIP_LEFT', 'KNEE_LEFT', 'ANKLE_LEFT']
            abc_joint2  = ['HIP_RIGHT', 'KNEE_RIGHT', 'ANKLE_RIGHT']

            # 計算關節角度並輸出在影像上
            angel1 = self.show_angel_on_2Dimage(abc_joint1)
            angel2 = self.show_angel_on_2Dimage(abc_joint2)

            if angel1 <= 100 and angel2 <= 100:
                self.stage = 'Sit'
            if angel1 >= 140 and angel2 >= 140 and self.stage == 'Sit':
                self.stage = 'Stand'
                self.counter += 1

    # 於畫面中顯示遊戲狀態  
    def show_info(self):
        
        left_time = self.game_left_time()

        # 文字底圖
        cv2.rectangle(self.combined_image, (self.width-200, 0), (self.width, 80), (245, 117, 16), -1)
        cv2.putText(self.combined_image, 'Time: {}s'.format(left_time.seconds), (self.width-180,30), cv2.FONT_HERSHEY_COMPLEX, 0.8, (255, 255, 255), 1, cv2.LINE_AA)  
        # 顯示完成次數
        cv2.putText(self.combined_image, '{} {}'.format(self.counter, self.stage), (self.width-180,65), cv2.FONT_HERSHEY_COMPLEX, 0.8, (255, 255, 255), 1, cv2.LINE_AA) 



    # 偵測到人後倒數3秒鐘進入遊戲
    def game_ready(self):

        if self.game_start_time == None:
            self.game_start_time = time.time()

        center = (int(self.width/2), int(self.height/2))
        cv2.circle(self.combined_image, center, 50, (0, 255, 0), -1)
        if (time.time() - self.game_start_time) <= 3:
            text = str(int(4 - (time.time() - self.game_start_time)))
            self.put_text_in_center(center, text, 1.5, (0, 0, 255), 2)        

        elif (time.time() - self.game_start_time) <= 4:
            text = 'Go!'
            self.put_text_in_center(center, text, 1.5, (0, 0, 255), 2)

        else:
            self.game_start = True
            self.game_start_time = datetime.datetime.now()
            self.game_end_time = self.game_start_time + self.game_time


    # 計算遊戲剩餘時間
    def game_left_time(self):

        if datetime.datetime.now() <= self.game_end_time:
            left_time =  (self.game_end_time - datetime.datetime.now())
        else:
            left_time = datetime.timedelta(seconds=0)
            self.game_stop = True

        return left_time



    # 文字置中
    def put_text_in_center(self, center, TEXT, TEXT_SCALE, TEXT_BGR, TEXT_THICKNESS):   

        TEXT_FACE = cv2.FONT_HERSHEY_COMPLEX
        text_size, _ = cv2.getTextSize(TEXT, TEXT_FACE, TEXT_SCALE, TEXT_THICKNESS)
        cv2.putText(self.combined_image, TEXT, (int(center[0] - text_size[0]/2), int(center[1] + text_size[1]/2)), TEXT_FACE, TEXT_SCALE, TEXT_BGR, TEXT_THICKNESS, cv2.LINE_AA)  

            


# 計算3維向量夾角
def calculate_angle(a, b, c):
    vec_a = np.array([a.x-b.x,a.y-b.y,a.z-b.z])
    vec_b = np.array([c.x-b.x,c.y-b.y,c.z-b.z])
    a_norm = np.sqrt(np.sum(vec_a * vec_a))
    b_norm = np.sqrt(np.sum(vec_b * vec_b))
    cos_value = np.dot(vec_a, vec_b) / (a_norm * b_norm)
    arc_value = np.arccos(cos_value)
    angle = arc_value * 180 / np.pi

    return angle

