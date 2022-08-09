#! coding: utf-8
from __future__ import annotations
from email.mime import image
from ntpath import join
from re import A
from turtle import color
#from typing_extensions import Self
from unittest import result
from xml.sax.handler import feature_namespace_prefixes
import numpy as np
from sklearn import svm
from sklearn.metrics import confusion_matrix
from sklearn import preprocessing

from numpy import append
import mediapipe as mp
import cv2
import os
import copy
import math
import time
import win32gui
import win32con



class VideoCut():
    def __init__(self):
        self.cap = None
        self.video_Path = None
        self.video_fps = None
        self.video_width = None
        self.video_height = None
        self.video_totalFrame = None
        self.keyframe = []
        self.keyframe_interval = None # keyframe カット間隔
        self.frame_image = None
        self.all_hand_result = []
        self.all_landmark = []
        self.all_detected_label = []


    # videoパス取得
    def set_video(self):

        while True:
            self.video_Path = input("読み込む動画ファイルへのパスを入力") # C:/Users/root/Desktop/hisa_reserch/hand_motion_search/video/aiueo.mp4
            self.video_Path = "C:/Users/root/Desktop/hisa_reserch/hand_motion_search/shuwa_video_sample/5kyu/mp4/VTS_06_1.mpeg"
            ''' video path memo
            C:/Users/root/Desktop/hisa_reserch/hand_motion_search/shuwa_video_sample/5kyu/mp4/VTS_06_1.mpeg
            C:/Users/root/Desktop/hisa_reserch/hand_motion_search/video/aiueo.mp4
            C:/Users/root/Desktop/hisa_reserch/hand_motion_search/shuwa_video_sample/5kyu/mp4/hands_video0.mp4
            '''
            self.cap = cv2.VideoCapture(self.video_Path)
            self.cap.set(cv2.CAP_PROP_FPS, 10)
            if (self.cap.isOpened()== False):  
                print("指定したパスのファイルを開けません") 
            else:
                break

    #ビデオの情報を取得
    def videoParameters(self):
        self.video_fps = int(self.cap.get(cv2.CAP_PROP_FPS))                    # 映像のFPSを取得
        self.video_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))              # 映像の横幅を取得
        self.video_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))             # カ映像の縦幅を取得
        self.video_totalFrame = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

        print("\n######### Currently set of ###########")
        print("fps:{}".format(self.video_fps))
        print("frame width:{}".format(self.video_width))
        print("frame height:{}".format(self.video_height))
        print("total frame:{}".format(self.video_totalFrame))
        print("Frame spacing to cut:{}".format(self.keyframe_interval))
        print("######################################")
        input("Start with keystroke")
    
    # 全フレームのランドマークをまとめたリストを作成
    def get_all_landmark(self):
        cnt = 0
        while True:
            cnt = cnt + 1
            print(cnt)
            ret, frame = self.cap.read()
            if ret == True:
                frame_RGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                hand_results = hands.process(frame_RGB)

                #self.all_landmark.append([hand_results.multi_hand_landmarks])

                self.addLandmarkList(hand_results)

                self.all_hand_result.append(hand_results)

                #self.addLabelList()
                
            else:
                break
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0) # 繰り返し再生

    def addLandmarkList(self, hand_results):
        multi_landmark_list = []
        multi_label_list = []
        if hand_results.multi_hand_landmarks == None:
            self.all_landmark.append([[None]])
            self.all_detected_label.append([[None]])

        else:

            for landmark in hand_results.multi_hand_landmarks:
                one_landmark_list = []
                isFast = True
                for index in landmark.landmark:
                    if isFast == True:
                        isFast = False
                        basis_x = index.x
                        basis_y = index.y
                        basis_z = index.z
                    else:
                        one_landmark_list.append(index.x - basis_x)
                        one_landmark_list.append(index.y - basis_y)
                        one_landmark_list.append(index.z - basis_z)

                multi_landmark_list.append(one_landmark_list)
                #print(len(one_landmark_list))
                multi_label_list.append([clf.predict([np.array(one_landmark_list)])])

            self.all_landmark.append(multi_landmark_list)
            self.all_detected_label.append(multi_label_list)

    
    def desplay(self):
        frame_num = 0
        while True:
            time.sleep(1/self.video_fps) # 再生速度制御

            ret, frame = self.cap.read()

            # 最前面に表示
            cv2.namedWindow("movie", cv2.WINDOW_NORMAL)
            hwnd = win32gui.FindWindow(None, "movie")
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

            if ret == True:
                frame_RGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                hand_results = self.all_hand_result[frame_num]
                

                if hand_results.multi_hand_landmarks is not None:
                    for landmarks_hand in hand_results.multi_hand_landmarks:
                        
                        mp_drawing.draw_landmarks(
                            image=frame,
                            landmark_list=landmarks_hand,
                            connections=mp_hands.HAND_CONNECTIONS,
                            landmark_drawing_spec=drawing_spec,
                            connection_drawing_spec=drawing_spec) # 特徴点の描画
                    #cv2.putText(frame,text=self.all_detected_label[frame_num])
                    print(self.all_detected_label[frame_num])
                        
                        
                cv2.imshow("movie", frame)
                #cv2.moveWindow("movie", 0, 0)
                #cv2.flip(frame, 1)
            else:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0) # 繰り返し再生
                frameNum = 0
            
            frame_num = frame_num + 1
                    
            key = cv2.waitKey(1)
            if key & 0xFF == ord('q'):
                break
                


        

    def detection(self):
        self.set_video()

        self.videoParameters()

        self.get_all_landmark()

        self.desplay()

        self.cap.release()
        cv2.destroyAllWindows()
                



    def get_keyframe(self):
        self.set_video()

        self.videoParameters()

        self.get_all_landmark()

        print(self.all_detected_label)
        

        cv2.destroyAllWindows()

def use_mediapipe(cap):
    print("#####################")
    print(" change play mode <t>")
    print(" end mediapipe    <q>")
    print("#####################")
    isclick = False
    key = None
    # 最前面に表示
    cv2.namedWindow("linedFrame", cv2.WINDOW_NORMAL)
    hwnd = win32gui.FindWindow(None, "linedFrame")
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

    while(True):      
        ret, frame = cap.read()
        if ret == True:
            results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            

            if results.multi_hand_landmarks is not None:
                for landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        image=frame,
                        landmark_list=landmarks,
                        connections=mp_hands.HAND_CONNECTIONS,
                        landmark_drawing_spec=drawing_spec,
                        connection_drawing_spec=drawing_spec) # 特徴点の描画

            cv2.imshow("linedFrame", frame)
            cv2.moveWindow("linedFrame", 0, 0)
            print("#########")
            print(frame)
            print(frame[0])
            print(frame[0][0])


        if isclick: 
            key = cv2.waitKey(0)
        else:   
            key = cv2.waitKey(1)

        if key & 0xFF == ord('q'):
            break

        # 再生方法切り替え
        if key & 0xFF == ord('t'):
            isclick = not isclick
        

def deinterlacing(src):
    pass



if __name__ == "__main__":
    # Mediapipe の設定
    mp_drawing = mp.solutions.drawing_utils
    drawing_spec = mp_drawing.DrawingSpec(color=[0, 255, 0], thickness=2, circle_radius=4) # 描画設定
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        max_num_hands=2,                # 1フレーム中からの手の検出数
        min_detection_confidence=0.5,   # しきい値1
        min_tracking_confidence=0.5,    # しきい値2
    )

    # svm 用学習データの呼び出し
    sample = np.loadtxt('learning_data2.csv', delimiter=',', dtype = "unicode")
    sample_labels = sample[:,60] # ラベル格納　['0' '0' '0' ... '41' '0' '0']
    sample_data = sample[:,0:60] # サンプルランドマーク格納 サンプル数 * (3*20)個    


    # svm 呼び出し
    clf = svm.SVC(gamma="scale")
    # 学習
    print("learning SVM...")
    clf.fit(sample_data, sample_labels)

    execution = VideoCut()


    while True:
        print("\n### select mode ###")
        print(" detection     <1>")
        print(" get keyframe  <2>")
        print(" use mediapipe <3>")
        print(" end           <q>")
        print("###################")
        selection = input("->")

        if "1" == selection:
            execution.detection()

        if "2" == selection:
            execution.get_keyframe()

        if "3" == selection:
            execution.set_video()
            execution.videoParameters()
            use_mediapipe(execution.cap)

        if "q" == selection:
            break

        

        cv2.destroyAllWindows()

    print("end")