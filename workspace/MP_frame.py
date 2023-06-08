from __future__ import annotations
from asyncio.windows_events import NULL
from email.mime import image
from genericpath import isfile
from ntpath import join
from pydoc import classname
from this import d
from turtle import color
#from typing_extensions import Self
from unittest import result
import mediapipe as mp
import cv2
import os
import copy
import math
import numpy as np
import matplotlib.pyplot as plt

#メディアパイプから取得した関節データに対して整理，処理を試した
#
#
#

class FrameData():
    def __init__(self):
        self.hand_L = None
        self.hand_R = None
        self.pose = None
        self.fromWrist_L = []
        self.fromWrist_R = []
        self.fixedSize_L = []
        self.fixedSize_R = []
        self.HandFramePosition_L = None
        self.HandFramePosition_R = None

    #Mediapipe検出データの梱包を解いて扱いやすいように再整理
    def MPdataOrganization(self, hands_info, hands_landmarks, pose_landmarks):
        index = 0
        if hands_info is not None:
            self.matrix_L = []
            for hand_info in hands_info:
                hand_label = hand_info.classification[0].label      #検出した手の左右情報取得
                if hand_label == "Left":
                    self.hand_L = hands_landmarks[index].landmark    #landmarksリストと左右情報を関連づけて整理
                if hand_label == "Right":
                    self.hand_R = hands_landmarks[index].landmark
                index = index + 1
        if pose_landmarks is not None:
            self.pose = pose_landmarks.landmark

    #手首基準の相対座標系に変換
    def WristCoordinateSystem(self):
        if self.hand_L is not None:
            isFirst = True
            wrist_joint = None
            for joint in self.hand_L:
                if isFirst:
                    wrist_joint = [joint.x, joint.y]
                    self.HandFramePosition_L = wrist_joint
                    isFirst = False
                else:
                    self.fromWrist_L.append([joint.x - wrist_joint[0], joint.y - wrist_joint[1]])
        if self.hand_R is not None:
            isFirst = True
            wrist_joint = None
            for joint in self.hand_R:
                if isFirst:
                    wrist_joint = [joint.x, joint.y]
                    self.HandFramePosition_R = wrist_joint
                    isFirst = False
                else:
                    self.fromWrist_R.append([joint.x - wrist_joint[0], joint.y - wrist_joint[1]])
                    
class PltCtrl():
    def __init__(self): #フレーム軸:x データ軸:y
        self.frame_axis_list = [-14, -13, -12, -11, -10, -9, -8, -7, -6, -5, -4, -3, -2, -1, 0] #フレーム軸(右に行くほど新しい)
        self.data0_axis_list = [   0,  0,   0,   0,   0,  0,  0,  0,  0,  0,  0,  0,  0,  0, 0] #情報
        self.data1_axis_list = [   0,  0,   0,   0,   0,  0,  0,  0,  0,  0,  0,  0,  0,  0, 0] #情報
        self.fig = None
        self.ax = None
        self.data_axis_max = 10
        self.data_axis_min = 0
        self.newData = 0

    #関節ベクトルの大きさの合計値算出
    def VecSizeSum(self, hand_FD, width, height):
        totalSize = 0
        scale = 1
        index = 0
        if hand_FD is not None:
            for joint_FD in hand_FD:
                x = float(joint_FD[0])
                y = float(joint_FD[1])
                x_FrameSize = int(x*width)
                y_FrameSize = int(y*height)
                vec_size = x_FrameSize*x_FrameSize + y_FrameSize*y_FrameSize
                totalSize = totalSize + vec_size
                if index == 4: #指定ベクトルをスケール係数としてscale変数に格納
                    scale = vec_size
                    print(scale)
                    isFirst = False
                index = index + 1
            self.newData = totalSize/scale
        else:
            self.newData = 0

    #グラフ初期設定
    def first_plot(self, data_min, data_max):
        self.fig, self.ax = plt.subplots(1, 1)
        self.data_axis_min = data_min
        self.data_axis_max = data_max
    

    #データリスト更新
    def update_data_list(self, data_list):
        data_listSize = len(data_list)
        for num in range(data_listSize - 1):
            data_list[num] = data_list[num + 1]
        data_list[data_listSize - 1] = self.newData

    def set_plot(self, data_list, color):
        self.update_data_list(data_list)
        self.ax.plot(self.frame_axis_list, data_list, color)


    #表示
    def update_plot(self):
        self.ax.set_ylim(self.data_axis_min, self.data_axis_max) #y軸の下限と上限設定
        plt.grid(axis='y') #補助線
        plt.pause(.01) #更新したグラフを表示
        self.ax.cla() #上書き防止のため初期化
        


def cam_MP():
    cap = cv2.VideoCapture(0)
    #cap = cv2.VideoCapture("C:/Users/root/Desktop/hisa_reserch/HandMotion_SimilarSearch/shuwa_video/5kyu/mp4/VTS_06_1.mp4")
    frame_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    frame_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    if isVecsum:
        vecsum_plt = PltCtrl()
        vecsum_plt.first_plot(0, 100) #y軸の下限と上限指定
    while True:
        framedata = FrameData()
        ret, frame = cap.read()
        
        if ret: 
            #frame_flip = cv2.flip(frame, 1) # 左右反転 mediapipeの検出結果に対応させる為
            frame_flip =frame
            frame_flip_RGB = cv2.cvtColor(frame_flip, cv2.COLOR_BGR2RGB)
            #MP検出結果取得
            hand_results = hands.process(frame_flip_RGB)
            pose_results = pose.process(frame_flip_RGB)

            #データ整理
            framedata.MPdataOrganization(hand_results.multi_handedness,
                                        hand_results.multi_hand_landmarks,
                                        pose_results.pose_landmarks)
            #手首座標系データ作成
            framedata.WristCoordinateSystem()
            #手の大きさを固定したデータを作成
            #framedata.StandardizeHandSize()
            
            #描画関連処理
            if isDraw:
                
                #体の関節描画
                if pose_results.pose_landmarks is not None:
                    mp_drawing.draw_landmarks(
                        frame_flip,
                        pose_results.pose_landmarks,
                        mp_pose.POSE_CONNECTIONS,
                        landmark_drawing_spec=drawing_spec_pose)
                    print(pose_results.pose_landmarks.landmark)
                #手の関節描画
                if hand_results.multi_hand_landmarks is not None:
                    for landmarks_hand in hand_results.multi_hand_landmarks:
                        mp_drawing.draw_landmarks(
                            image=frame_flip,
                            landmark_list=landmarks_hand,
                            connections=mp_hands.HAND_CONNECTIONS,
                            landmark_drawing_spec=drawing_spec_hand,
                            connection_drawing_spec=drawing_spec_hand) # 特徴点の描画
                    #左右描画の追加(LR)
                    if framedata.hand_L is not None:
                        cv2.putText(frame_flip,
                            text='L',
                            org=(int(framedata.hand_L[0].x*frame_width), int(framedata.hand_L[0].y*frame_height)),
                            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                            fontScale=1.0,
                            color=(255, 100, 0),
                            thickness=6,
                            lineType=cv2.LINE_4)
                    if framedata.hand_R is not None:
                        cv2.putText(frame_flip,
                            text='R',
                            org=(int(framedata.hand_R[0].x*frame_width), int(framedata.hand_R[0].y*frame_height)),
                            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                            fontScale=1.0,
                            color=(0, 100, 255),
                            thickness=6,
                            lineType=cv2.LINE_4)
            
            #framedata.StandardizeHandSize

            if isVecsum:
                #if framedata.fromWrist_L is not None:
                vecsum_plt.VecSizeSum(framedata.fromWrist_L, frame_width, frame_height) #計算
                vecsum_plt.set_plot(data_list=vecsum_plt.data0_axis_list, color="royalblue") #グラフ書き込み
                vecsum_plt.VecSizeSum(framedata.fromWrist_R, frame_width, frame_height)
                vecsum_plt.set_plot(data_list=vecsum_plt.data1_axis_list, color="indianred")
                vecsum_plt.update_plot() #中身が更新されたグラフを表示
                


            cv2.imshow("linedFrame", frame_flip)
            cv2.moveWindow("linedFrame", 0, 0)
            
            #キーボード入力処理
            key = cv2.waitKey(1)
            if key & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":

    #MediaPipe周辺設定
    mp_drawing = mp.solutions.drawing_utils
    drawing_spec_hand = mp_drawing.DrawingSpec(color=[0, 180, 0], thickness=2, circle_radius=4)
    drawing_spec_pose = mp_drawing.DrawingSpec(color=[180, 0, 180], thickness=2, circle_radius=4)
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode= False, 
        max_num_hands=2,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) # 1に近づける程精度向上, 検出時間増加
    
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(
        model_complexity=1,
        min_detection_confidence=0.3,
        min_tracking_confidence=0.5)

    isDraw = True
    isVecsum = True 

    
    #video_MP()
    cam_MP()

    print("ended")