
import cv2
import mediapipe as mp
import numpy as np
import os
from typing import List, Dict
from enum import IntEnum
import base64

#landmark indices
class PoseLandmark(IntEnum):
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_ELBOW = 13
    RIGHT_ELBOW = 14
    LEFT_WRIST = 15
    RIGHT_WRIST = 16
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_KNEE = 25
    RIGHT_KNEE = 26
    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28

#init mediapipe tasks
BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

MODEL_PATH = os.path.join(os.path.dirname(__file__), "pose_landmarker.task") #landmark file

def proccess_frame(data: str) -> np.ndarray:
    """ Mobile receives data as base64 string but we want raw img bytes,
    Process frame does this and gives the information to a np array """

    img_bytes = base64.b64decode(data)
    np_arr = np.frombuffer(img_bytes, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    return frame

def calc_angles(a, b, c) -> int:
    """
    calculate angles between two vectors
    """

    #body landmarks
    a = np.array(a)
    b = np.array(b) #joints
    c = np.array(c)

    #arctan2 converts the vectors into angles in radians
    vec_ba = np.arctan2(a[1] - b[1], a[0] - b[0])  # angle from joint to point a
    vec_bc = np.arctan2(c[1] - b[1], c[0] - b[0])  # angle from joint to point c
    radians = vec_bc - vec_ba # angle between 2 limbs @ joint b

    #radians -> degrees since easier to work with degrees
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180:
        angle = angle - 360 #cant use 360 angle not a real thing so it will flip the angle

    return angle

def conv_frame(frame) -> np.ndarray:
    """color conversion using opencv"""
    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

def extract_landmarks(landmarker, frame, timestamp) -> List[PoseLandmarker] | None:
    """This runs MediaPipe on a frame and returns landmarks"""
    rgb = conv_frame(frame)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    detection = landmarker.detect_async(mp_image, timestamp)
    if detection.pose_landmarks:
        return detection.pose_landmarks[0]
    return None

def get_joint_pos(landmarks) -> Dict:
    """Pulls joint coordinates from landmarks"""
    return {
        'l_shoulder': [landmarks[PoseLandmark.LEFT_SHOULDER].x,
                       landmarks[PoseLandmark.LEFT_SHOULDER].y],
        'r_shoulder': [landmarks[PoseLandmark.RIGHT_SHOULDER].x,
                       landmarks[PoseLandmark.RIGHT_SHOULDER].y],
        'l_elbow': [landmarks[PoseLandmark.LEFT_ELBOW].x,
                    landmarks[PoseLandmark.LEFT_ELBOW].y],
        'r_elbow': [landmarks[PoseLandmark.RIGHT_ELBOW].x,
                    landmarks[PoseLandmark.RIGHT_ELBOW].y],
        'l_wrist': [landmarks[PoseLandmark.LEFT_WRIST].x,
                    landmarks[PoseLandmark.LEFT_WRIST].y],
        'r_wrist': [landmarks[PoseLandmark.RIGHT_WRIST].x,
                    landmarks[PoseLandmark.RIGHT_WRIST].y],
        'l_hip': [landmarks[PoseLandmark.LEFT_HIP].x,
                  landmarks[PoseLandmark.LEFT_HIP].y],
        'r_hip': [landmarks[PoseLandmark.RIGHT_HIP].x,
                  landmarks[PoseLandmark.RIGHT_HIP].y],
        'l_knee': [landmarks[PoseLandmark.LEFT_KNEE].x,
                   landmarks[PoseLandmark.LEFT_KNEE].y],
        'r_knee': [landmarks[PoseLandmark.RIGHT_KNEE].x,
                   landmarks[PoseLandmark.RIGHT_KNEE].y],
        'l_ankle': [landmarks[PoseLandmark.LEFT_ANKLE].x,
                    landmarks[PoseLandmark.LEFT_ANKLE].y],
        'r_ankle': [landmarks[PoseLandmark.RIGHT_ANKLE].x,
                    landmarks[PoseLandmark.RIGHT_ANKLE].y],
    }


def create_landmarker(x) -> PoseLandmarker:
    options = PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=MODEL_PATH),
        running_mode=VisionRunningMode.LIVE_STREAM, min_pose_detection_confidence=0.5, result_callback=x)

    return PoseLandmarker.create_from_options(options)

def pose_estimation(landmarker, frame, timestamp):
    rgb = conv_frame(frame)

    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

    landmarker.detect_async(mp_image, timestamp)

def midpoint(x, y) -> tuple[float, float]:
    """avg of 2 coordinates"""
    return (x[0] + y[0]) / 2, (x[1] + y[1]) / 2

def calc_hip_angle(joints) -> float:
    """Average hip angle (shoulder-hip-knee) across left and right sides"""
    l_angle = calc_angles(joints["l_shoulder"], joints["l_hip"], joints["l_knee"])
    r_angle = calc_angles(joints["r_shoulder"], joints["r_hip"], joints["r_knee"])
    return (l_angle + r_angle) / 2

def calc_spine_angle(joints) -> float:
    """Angle of shoulder->hip vector vs vertical. 0° = upright, higher = more lean"""
    shoulder_mid = midpoint(joints["l_shoulder"], joints["r_shoulder"])
    hip_mid = midpoint(joints["l_hip"], joints["r_hip"])
    dx = shoulder_mid[0] - hip_mid[0]
    dy = shoulder_mid[1] - hip_mid[1]
    # vertical reference is straight up: (0, -1) in image coords (y increases downward)
    # angle between vector (dx, dy) and vertical (0, -1)
    radians = np.arctan2(abs(dx), abs(dy))
    return float(np.degrees(radians))

def calc_knee_cave(joints) -> float:
    """knee_width / hip_width. < 1.0 means knees are caving inward"""
    knee_width = abs(joints["l_knee"][0] - joints["r_knee"][0])
    hip_width = abs(joints["l_hip"][0] - joints["r_hip"][0])
    if hip_width == 0:
        return 1.0
    return knee_width / hip_width

def extract_frame_features(joints) -> Dict:
    ml_angles = extract_ml_angles(joints)
    l_knee_angle, r_knee_angle = ml_angles[2], ml_angles[3]

    return {
        "l_knee_angle": l_knee_angle,
        "r_knee_angle": r_knee_angle,
        "avg_knee_angle": (l_knee_angle + r_knee_angle) / 2,
        "hip_angle": calc_hip_angle(joints),
        "spine_angle": calc_spine_angle(joints),
        "knee_valgus_ratio": calc_knee_cave(joints),
        "symmetry_diff": abs(l_knee_angle - r_knee_angle),
        "ml_angles": ml_angles,
    }

def extract_ml_angles(joints) -> List[float]:
    """Returns the 8 joint angles in the same order used during ML training.

    Order matches angle_extract.py TRIOS:
      left_elbow, right_elbow, left_knee, right_knee,
      left_hip, right_hip, left_shoulder, right_shoulder
    """
    return [
        float(calc_angles(joints["l_shoulder"], joints["l_elbow"], joints["l_wrist"])),
        float(calc_angles(joints["r_shoulder"], joints["r_elbow"], joints["r_wrist"])),
        float(calc_angles(joints["l_hip"],      joints["l_knee"],  joints["l_ankle"])),
        float(calc_angles(joints["r_hip"],      joints["r_knee"],  joints["r_ankle"])),
        float(calc_angles(joints["l_shoulder"], joints["l_hip"],   joints["l_knee"])),
        float(calc_angles(joints["r_shoulder"], joints["r_hip"],   joints["r_knee"])),
        float(calc_angles(joints["l_elbow"],    joints["l_shoulder"], joints["l_hip"])),
        float(calc_angles(joints["r_elbow"],    joints["r_shoulder"], joints["r_hip"])),
    ]

