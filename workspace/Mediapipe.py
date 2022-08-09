from __future__ import annotations
from email.mime import image
from ntpath import join
from turtle import color
#from typing_extensions import Self
from unittest import result
import mediapipe as mp
import cv2
import os
import copy
import math

F_WIDTH = 600
F_HEIGHT = 600

cap = cv2.VideoCapture(0)



def useMediaPipe():
    canvas = cv2.imread('canvas.jpeg')
    canvas = cv2.resize(canvas, [600,600])
    while(True):      
        ret, frame = cap.read()
        frame = cv2.resize(frame, (F_WIDTH, F_HEIGHT))
        frame_RGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        soloImage = canvas.copy()
        resizeImage = canvas.copy()
        if ret == True:
            #hand_results = hands.process(frame_RGB)
            pose_results = pose.process(frame_RGB)



            """
            if hand_results.multi_hand_landmarks is not None:
                for landmarks_hand in hand_results.multi_hand_landmarks:

                    #print(landmarks.landmark)
                    '''
                    [x:***
                    y:***
                    z:***
                    , ...(*21個)]

                    *** = 0~1 正規化されている
                    
                    '''
                    
                    #drawHand(copy.deepcopy(landmarks_hand.landmark), frame)

                    drawHand_centar(copy.deepcopy(landmarks_hand.landmark), soloImage)

                    drawHand_resize(copy.deepcopy(landmarks_hand.landmark), resizeImage)

                    '''
                    mp_drawing.draw_landmarks(
                        image=frame,
                        landmark_list=landmarks,
                        connections=mp_hands.HAND_CONNECTIONS,
                        landmark_drawing_spec=drawing_spec,
                        connection_drawing_spec=drawing_spec) # 特徴点の描画
                    '''
            """
            
            if pose_results.pose_landmarks is not None:
                mp_drawing.draw_landmarks(
                    frame,
                    pose_results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=mp.solutions.drawing_styles.get_default_pose_landmarks_style())



            # window arrangementS
            cv2.flip(frame, 1)
            cv2.imshow("linedFrame", frame)
            cv2.moveWindow("linedFrame", 0, 0)
            cv2.flip(soloImage, 1)
            cv2.imshow("soloImage", soloImage)
            cv2.moveWindow("soloImage", F_WIDTH, 0)
            cv2.flip(soloImage, 1)
            cv2.imshow("resizeImage", resizeImage)
            cv2.moveWindow("resizeImage", F_WIDTH*2, 0)
            
            key = cv2.waitKey(1)

            if key & 0xFF == ord('q'):
                break

def drawHand_centar(landmark, image):
    center_x = 300 - landmark[9].x * F_WIDTH
    center_y = 300 - landmark[9].y * F_HEIGHT
    tipnNum = (4,8,12,16,20)
    rootNum = (5,9,13,17)
    sideNum = (5,17)
    x0 = int(float(landmark[0].x) * F_WIDTH) + int(center_x)
    y0 = int(float(landmark[0].y) * F_HEIGHT) + int(center_y)
    '''
    for joint_num in range(21):
        x = int(float(landmark[joint_num].x) * F_WIDTH) + int(center_x)
        y = int(float(landmark[joint_num].y) * F_HEIGHT) + int(center_y)
        cv2.circle(image, (x, y), 5, (0, 0, 255), thickness=2, lineType=cv2.LINE_8, shift=0)'''
    for joint_num in range(21):
        # 関節の描画
        x = int(float(landmark[joint_num].x) * F_WIDTH) + int(center_x)
        y = int(float(landmark[joint_num].y) * F_HEIGHT) + int(center_y)
        cv2.circle(image, (x, y), 5, (255,0,0), thickness=2, lineType=cv2.LINE_8, shift=0)
        # 関節をつなぐ線の描画
        if not joint_num in tipnNum: # 指の先端からの描画を除外
            x_ = int(float(landmark[joint_num + 1].x) * F_WIDTH) + int(center_x)
            y_ = int(float(landmark[joint_num + 1].y) * F_HEIGHT) + int(center_y)
            cv2.line(image, (x, y), (x_, y_), (250,206,135), thickness=2, lineType=cv2.LINE_4)
            if joint_num in rootNum and joint_num != 17: # 親指以外の指の付け根同士を結ぶ
                x__ = int(float(landmark[joint_num + 4].x) * F_WIDTH) + int(center_x)
                y__ = int(float(landmark[joint_num + 4].y) * F_HEIGHT) + int(center_y)
                cv2.line(image, (x, y), (x__, y__), (250,206,135), thickness=2, lineType=cv2.LINE_4)
        if joint_num in sideNum: # 親指小指の付け根と手首を結ぶ
            x_ = int(float(landmark[joint_num].x) * F_WIDTH) + int(center_x)
            y_ = int(float(landmark[joint_num].y) * F_HEIGHT) + int(center_y)
            cv2.line(image, (x0, y0), (x_, y_), (250,206,135), thickness=2, lineType=cv2.LINE_4)


def drawHand_resize(landmark, image):
    basesize = 200 # pixel 
    center_x = 300 - landmark[9].x * F_WIDTH
    center_y = 300 - landmark[9].y * F_HEIGHT
    tipnNum = (4,8,12,16,20)
    rootNum = (5,9,13,17)
    sideNum = (5,17)

    x_vec = float(landmark[0].x)* F_WIDTH - float(landmark[9].x)* F_WIDTH
    y_vec = float(landmark[0].y)* F_HEIGHT - float(landmark[9].y)* F_HEIGHT
    handsize =  math.sqrt(x_vec**2+y_vec**2)
    sizeRatio = handsize/basesize




    x0 = int(float(landmark[0].x) * F_WIDTH) + int(center_x)
    y0 = int(float(landmark[0].y) * F_HEIGHT) + int(center_y)
    x0,y0 = vecResize(x0, y0, sizeRatio)

    '''
    for joint_num in range(21):
        x = int(float(landmark[joint_num].x) * F_WIDTH) + int(center_x)
        y = int(float(landmark[joint_num].y) * F_HEIGHT) + int(center_y)
        cv2.circle(image, (x, y), 5, (0, 0, 255), thickness=2, lineType=cv2.LINE_8, shift=0)'''
    for joint_num in range(21):
        # 関節の描画
        x = int(float(landmark[joint_num].x) * F_WIDTH) + int(center_x)
        y = int(float(landmark[joint_num].y) * F_HEIGHT) + int(center_y)
        x,y =  vecResize(x, y, sizeRatio)
        cv2.circle(image, (x, y), 5, (255,0,0), thickness=2, lineType=cv2.LINE_8, shift=0)
        # 関節をつなぐ線の描画
        if not joint_num in tipnNum: # 指の先端からの描画を除外
            x_ = int(float(landmark[joint_num + 1].x) * F_WIDTH) + int(center_x)
            y_ = int(float(landmark[joint_num + 1].y) * F_HEIGHT) + int(center_y)
            x_,y_ = vecResize(x_, y_, sizeRatio)
            cv2.line(image, (x, y), (x_, y_), (250,206,135), thickness=2, lineType=cv2.LINE_4)
            if joint_num in rootNum and joint_num != 17: # 親指以外の指の付け根同士を結ぶ
                x__ = int(float(landmark[joint_num + 4].x) * F_WIDTH) + int(center_x)
                y__ = int(float(landmark[joint_num + 4].y) * F_HEIGHT) + int(center_y)
                x__,y__ = vecResize(x__, y__, sizeRatio)
                cv2.line(image, (x, y), (x__, y__), (250,206,135), thickness=2, lineType=cv2.LINE_4)
        if joint_num in sideNum: # 親指小指の付け根と手首を結ぶ
            x_ = int(float(landmark[joint_num].x) * F_WIDTH) + int(center_x)
            y_ = int(float(landmark[joint_num].y) * F_HEIGHT) + int(center_y)
            x_,y_ = vecResize(x_, y_, sizeRatio)
            cv2.line(image, (x0, y0), (x_, y_), (250,206,135), thickness=2, lineType=cv2.LINE_4)


def vecResize(x, y, sizeRatio):
    x_vec = int((x - 300)/sizeRatio)
    y_vec = int((y - 300)/sizeRatio)
    x = x_vec + 300
    y = y_vec + 300
    return x,y

def drawHand(landmark, image):
    tipnNum = (4,8,12,16,20)
    rootNum = (5,9,13,17)
    sideNum = (5,17)
    x0 = int(float(landmark[0].x) * F_WIDTH)
    y0 = int(float(landmark[0].y) * F_HEIGHT)
    for joint_num in range(21):
        # 関節の描画
        x = int(float(landmark[joint_num].x) * F_WIDTH)
        y = int(float(landmark[joint_num].y) * F_HEIGHT)
        cv2.circle(image, (x, y), 5, (255,0,0), thickness=2, lineType=cv2.LINE_8, shift=0)
        # 関節をつなぐ線の描画
        if not joint_num in tipnNum: # 指の先端からの描画を除外
            x_ = int(float(landmark[joint_num + 1].x) * F_WIDTH)
            y_ = int(float(landmark[joint_num + 1].y) * F_HEIGHT)
            cv2.line(image, (x, y), (x_, y_), (250,206,135), thickness=2, lineType=cv2.LINE_4)
            if joint_num in rootNum and joint_num != 17: # 親指以外の指の付け根同士を結ぶ
                x__ = int(float(landmark[joint_num + 4].x) * F_WIDTH)
                y__ = int(float(landmark[joint_num + 4].y) * F_HEIGHT)
                cv2.line(image, (x, y), (x__, y__), (250,206,135), thickness=2, lineType=cv2.LINE_4)
        if joint_num in sideNum: # 親指小指の付け根と手首を結ぶ
            x_ = int(float(landmark[joint_num].x) * F_WIDTH)
            y_ = int(float(landmark[joint_num].y) * F_HEIGHT)
            cv2.line(image, (x0, y0), (x_, y_), (250,206,135), thickness=2, lineType=cv2.LINE_4)
            


if __name__ == "__main__":

    mp_drawing = mp.solutions.drawing_utils
    drawing_spec = mp_drawing.DrawingSpec(color=[0, 255, 0], thickness=2, circle_radius=4)

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        max_num_hands=2,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(
        #upper_body_only=True,
        model_complexity=1,
        enable_segmentation=True,
        min_detection_confidence=0.5,
        #min_tracking_confidence=0.5,
    )




    useMediaPipe()


    print("ended")
    cap.release()
    cv2.destroyAllWindows()