from ast import Num
import cv2
from cv2 import imshow
import time
import copy
import numpy as np

# 手話のビデオを単語ごとに分割保存しなおすやつ
#
#
#


class Edit_video():
    def __init__(self):
        self.video_path = None
        self.video_fps = None
        self.video_width = None
        self.video_height = None
        self.video_totalFrame = None
        self.cap = None
        pass

    def import_video(self):
        while True:
            #video_path = input("video path? = ")
            video_path = "C:/Users/root/Desktop/hisa_reserch/HandMotion_SimilarSearch/shuwa_video/5kyu/mp4/VTS_02_1.mp4" # ,---------------編集対象
            ''' video path memo
            C:/Users/root/Desktop/hisa_reserch/hand_motion_search/shuwa_video/5kyu/mp4/VTS_02_1.mp4
            '''
            cap = cv2.VideoCapture(video_path)
            if cap.isOpened() == False:
                print("video not found")
                continue
            self.video_path = video_path
            self.cap = cap
            break
    
    #　ただ再生するだけ
    def playback(self):
        # Displayed in the foreground
        cv2.namedWindow("video", cv2.WINDOW_NORMAL)

        while True:
            ret, frame = self.cap.read()

            if ret == True:
                frame_RGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                cv2.imshow("video", frame)

            key = cv2.waitKeyEx(1)
            if key & 0xFF == ord('q'):
                break

            time.sleep(1/self.video_fps)

    # 動画編集用
    def reading(self):
        # Displayed in the foreground
        waitKeyMode = 0 # 連続再生1 フレーム切り替え0 
        isFirst = True
        
        file = None
        makeFileCnt = 0
        
        #reactangleRange_0 = [500, 100] #抽出点調査用
        #reactamgleRange_1 = [reactangleRange_0[0]+20, reactangleRange_0[1]+20]

        saveDir = "C:/Users/root/Desktop/hisa_reserch/HandMotion_SimilarSearch/edited_video/bunsyo/" # <--------------------------保存先

        while True:
            ret, frame = self.cap.read()
            frame_num = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES)) # 現在の再生箇所


            #cv2.rectangle(frame, reactangleRange_0, reactamgleRange_1, (0, 255, 0))

            #print(frame[101][501][2])　#抽出点調査用

            if ret == True:
                frame_RGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                cv2.imshow("video", frame)

                if isVideoSplit == True:
                    frame_bit = frame[101][501][2]
                    if frame_bit < 150:
                        if isFirst == True:
                            isFirst = False
                            fmt = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
                            filePath = saveDir + str(makeFileCnt) +".mp4"
                            frame_rate = self.video_fps
                            size = (self.video_width, self.video_height)
                            writer = cv2.VideoWriter(filePath, fmt, frame_rate, size) # ライター作成
                            makeFileCnt = makeFileCnt + 1
                        writer.write(frame)
                    else:
                        if isFirst == False:
                            isFirst = True
                            writer.release()
            if isFirst == False:
                isFirst = True
                writer.release()



            ## key input ------------------------------------------------------
            key = cv2.waitKeyEx(waitKeyMode)

            if key & 0xFF == ord('q'):
                break
            if key & 0xFF == ord('p'):
                while True:
                    try:
                        frame_num = int(input("select frame number :"))
                        break
                    except:
                        print("Incorrect input")
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num) 
            if key == 2424832:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num-2) 
                #print("left key")
            if key & 0xFF == ord('m'): # 連続再生切り替え
                if waitKeyMode == 0:
                    waitKeyMode = 1
                else:
                    waitKeyMode = 1
                    

            
                




    def video_property(self):
        self.video_fps = int(self.cap.get(cv2.CAP_PROP_FPS))                    # 映像のFPSを取得
        self.video_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))              # 映像の横幅を取得
        self.video_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))             # カ映像の縦幅を取得
        self.video_totalFrame = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print("\n######### Currently set of ###########")
        print("fps:{}".format(self.video_fps))
        print("frame width:{}".format(self.video_width))
        print("frame height:{}".format(self.video_height))
        print("total frame:{}".format(self.video_totalFrame))
        print("######################################")
        input("Start with keystroke")





if __name__ == "__main__":
    isVideoSplit = True

    start_edit = Edit_video()

    start_edit.import_video()

    start_edit.video_property()

    #start_edit.playback()
    start_edit.reading()

    print("end")
