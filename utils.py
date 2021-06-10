import numpy as np
import cv2

# 計算關節角度
def get_joint_angel(skeleton3D):

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

    # 定義個關節
    skeleton = {'SHOULDER_LEFT':skeleton3D[5], 'ELBOW_LEFT':skeleton3D[6], 'WRIST_LEFT':skeleton3D[7]}
    # 計算關節角度
    angel = calculate_angle(skeleton['SHOULDER_LEFT'], skeleton['ELBOW_LEFT'], skeleton['WRIST_LEFT'])
    angel = round(angel, 1) # 四捨五入

    return angel

# 將關節角度顯示在輸出影像
def show_angel_on_2Dimage(skeleton2D, joint_angel, combined_image):
    center_joint = 'ELBOW_LEFT'

    joints_position = {'SHOULDER_LEFT':skeleton2D.joints2D[5].position,
                        'ELBOW_LEFT':skeleton2D.joints2D[6].position,
                        'WRIST_LEFT':skeleton2D.joints2D[7].position}

    coordinate_x = int(joints_position[center_joint].xy.x)
    coordinate_y = int(joints_position[center_joint].xy.y)
    cv2.putText(combined_image, str(joint_angel), (coordinate_x,coordinate_y+20), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)

    return combined_image

# 顯示3維關節座標在輸出影像上
def show_coordinate_on_2Dimage(skeleton2D, skeleton3D, combined_image):
    joints_coordinate = {'SHOULDER_LEFT':skeleton2D.joints2D[5].position,
                    'ELBOW_LEFT':skeleton2D.joints2D[6].position,
                    'WRIST_LEFT':skeleton2D.joints2D[7].position}
    joints_position = {'SHOULDER_LEFT':skeleton3D[5],
                    'ELBOW_LEFT':skeleton3D[6],
                    'WRIST_LEFT':skeleton3D[7]}
    for key in joints_position:
        coordinate = (int(joints_coordinate[key].xy.x),int(joints_coordinate[key].xy.y))
        text = '({:.1f}, {:.1f}, {:.1f})'.format(joints_position[key].x, joints_position[key].y, joints_position[key].z)
        cv2.putText(combined_image, text, coordinate, cv2.FONT_HERSHEY_COMPLEX, 0.35, (0, 255, 0), 1, cv2.LINE_AA)
