from ast import Num
import cv2
from cv2 import imshow
import win32gui
import win32con
import time
import copy
import numpy as np

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
            video_path = "C:/Users/root/Desktop/hisa_reserch/hand_motion_search/shuwa_video_sample/5kyu/mp4/VTS_06_1.mpeg"
            ''' video path memo
            C:/Users/root/Desktop/hisa_reserch/hand_motion_search/shuwa_video_sample/5kyu/mp4/VTS_06_1.mpeg
            C:/Users/root/Desktop/hisa_reserch/hand_motion_search/video/aiueo.mp4
            C:/Users/root/Desktop/hisa_reserch/hand_motion_search/shuwa_video_sample/5kyu/mp4/hands_video0.mp4
            '''
            cap = cv2.VideoCapture(video_path)
            if cap.isOpened() == False:
                print("video not found")
                continue
            self.video_path = video_path
            self.cap = cap
            break

    def playback(self):
        # Displayed in the foreground
        cv2.namedWindow("video", cv2.WINDOW_NORMAL)
        hwnd = win32gui.FindWindow(None, "video")
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

        while True:
            ret, frame = self.cap.read()

            if ret == True:
                frame_RGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                cv2.imshow("video", frame)

            key = cv2.waitKeyEx(1)
            if key & 0xFF == ord('q'):
                break

            time.sleep(1/self.video_fps)
    
    def reading(self):
        # Displayed in the foreground

        while True:
            ret, frame = self.cap.read()
            frame_num = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))

            if ret == True:
                frame_RGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                cv2.imshow("video", frame)


            ## key input ------------------------------------------------------
            key = cv2.waitKeyEx(0)

            if key & 0xFF == ord('e'):
                self.frame_edit(frame.copy(), frame_num)
                cv2.waitKeyEx(0)
            if key & 0xFF == ord('s'):
                self.synthesize_frames(frame_num, frame_num -1)
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num) # 再生箇所戻す 
                cv2.waitKeyEx(0)
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

                    
    
    def frame_edit(self, frame, frame_Num):
        column = 0
        frame_lined_odd = np.array(frame)
        black_line = np.zeros((self.video_width,3))
        while True:
            if column % 2:
                try:
                    frame_lined_odd[column] = black_line
                except:
                    break
                
            column = column + 1

        imshow("lineed frame in odd columns <number {}>".format(frame_Num), frame_lined_odd)

        column = 0
        frame_lined_even = np.array(frame)
        while True:
            if not column % 2:
                try:
                    frame_lined_even[column] = black_line
                except:
                    break
                
            column = column + 1

        imshow("lineed frame in even columns <number {}>".format(frame_Num), frame_lined_even)

    def synthesize_frames(self, first_num, second_num):
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, first_num)
        first_ret, first_frame  = self.cap.read()
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, second_num)
        first_ret, second_frame  = self.cap.read()

        column = 0
        synthesized_frame = first_frame.copy()
        while True:
            if column % 2:
                try:
                    synthesized_frame[column] = second_frame[column]
                    
                except:
                    break
            
            column = column + 1

        imshow("synthesized_frame <{} and {}>".format(first_num, second_num), synthesized_frame)






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
    start_edit = Edit_video()

    start_edit.import_video()

    start_edit.video_property()

    #start_edit.playback()
    start_edit.reading()

    print("end")
