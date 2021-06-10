import numpy as np

def get_joint_angel(skeleton3D):

    # 計算3維向量夾角
    def calculate_angle(a, b, c):
        vec_a = np.array([a.x-b.x,a.y-b.y,a.z-b.z])
        vec_b = np.array([c.y-b.y,c.y-b.y,c.z-b.z])
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

    return angel