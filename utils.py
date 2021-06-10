import numpy as np
import cv2
class Util:
    def __init__(self, skeleton2D, skeleton3D, combined_image):
        self.skeleton2D = skeleton2D
        self.combined_image = combined_image
        self.joints_2d = {'SHOULDER_LEFT':skeleton2D.joints2D[5].position,
                                'ELBOW_LEFT':skeleton2D.joints2D[6].position,
                                'WRIST_LEFT':skeleton2D.joints2D[7].position}
        self.joints_3d = {'SHOULDER_LEFT':skeleton3D[5],
                                'ELBOW_LEFT':skeleton3D[6],
                                'WRIST_LEFT':skeleton3D[7]}

    # 顯示3維關節座標在輸出影像上
    def show_coordinate_on_2Dimage(self):
        for key in self.joints_2d:
            coordinate = (int(self.joints_2d[key].xy.x),int(self.joints_2d[key].xy.y))
            text = '({:.1f}, {:.1f}, {:.1f})'.format(self.joints_3d[key].x, self.joints_3d[key].y, self.joints_3d[key].z)
            cv2.putText(self.combined_image, text, coordinate, cv2.FONT_HERSHEY_COMPLEX, 0.35, (0, 255, 0), 1, cv2.LINE_AA)


    # 將關節角度顯示在輸出影像
    def show_angel_on_2Dimage(self, abc_joint):

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

        # 計算關節角度
        angel = calculate_angle(self.joints_3d[abc_joint[0]], self.joints_3d[abc_joint[1]], self.joints_3d[abc_joint[2]])
        angel = round(angel, 1) # 四捨五入

        center_joint = abc_joint[1]
        coordinate_x = int(self.joints_2d[center_joint].xy.x)
        coordinate_y = int(self.joints_2d[center_joint].xy.y)
        cv2.putText(self.combined_image, str(angel), (coordinate_x,coordinate_y+20), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)

