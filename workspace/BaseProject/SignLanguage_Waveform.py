import mediapipe as mp
import cv2
import csv
import glob
import os

#Mediapipe検出データ処理
class MPdata():
    def __init__(self):
        self.hand_L = None
        self.hand_R = None
        self.fromWrist_L = []
        self.fromWrist_R = []
        self.fixedSize_L = []
        self.fixedSize_R = []
        self.HandPosition_L = None
        self.HandPosition_R = None
        self.fromWrist_Nones = [[None,None],[None,None],[None,None],[None,None],[None,None],
                                [None,None],[None,None],[None,None],[None,None],[None,None],
                                [None,None],[None,None],[None,None],[None,None],[None,None],
                                [None,None],[None,None],[None,None],[None,None],[None,None],[None,None]]

    #Mediapipe検出データの梱包を解いて扱いやすいように再整理
    def MPdataOrganization(self, hands_info, hands_landmarks):
        index = 0
        if hands_info is not None:
            for hand_info in hands_info:
                hand_label = hand_info.classification[0].label      #検出した手の左右情報取得
                if hand_label == "Left":
                    self.hand_L = hands_landmarks[index].landmark    #landmarksリストと左右情報を関連づけて整理
                if hand_label == "Right":
                    self.hand_R = hands_landmarks[index].landmark
                index = index + 1


    #手首基準の相対座標系に変換
    def WristCoordinateSystem(self):
        if self.hand_L is not None:
            isFirst = True
            wrist_joint = None
            for joint in self.hand_L:
                if isFirst:
                    wrist_joint = [joint.x, joint.y]
                    self.HandPosition_L = wrist_joint
                    isFirst = False
                    self.fromWrist_L.append([wrist_joint[0], wrist_joint[1]])
                else:
                    self.fromWrist_L.append([joint.x - wrist_joint[0], joint.y - wrist_joint[1]])
        if self.hand_R is not None:
            isFirst = True
            wrist_joint = None
            for joint in self.hand_R:
                if isFirst:
                    wrist_joint = [joint.x, joint.y]
                    self.HandPosition_R = wrist_joint
                    isFirst = False
                    self.fromWrist_R.append([wrist_joint[0], wrist_joint[1]])
                else:
                    self.fromWrist_R.append([joint.x - wrist_joint[0], joint.y - wrist_joint[1]])
    



# 動画の全フレームの関節データのリストを取得
def waveform_handdata(videoPath, videoName):
    cap = cv2.VideoCapture(videoPath)
    frame_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    frame_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

    TimeSeries_HandData =[] # TimeSeries_HandData[ フレーム番号 ][ 左or右 ][ ベクトル(0~20) <- 0は手首座標 ][ 成分(x,y) ]

    while True:
        mp_data = MPdata()
        ret, frame = cap.read()
        

        if ret:
            frame_flip = cv2.flip(frame, 1) # 左右反転 mediapipeの検出結果に対応させる為
            frame_flip_RGB = cv2.cvtColor(frame_flip, cv2.COLOR_BGR2RGB)
            hand_results = hands.process(frame_flip_RGB)

            mp_data.MPdataOrganization(hand_results.multi_handedness,
                                        hand_results.multi_hand_landmarks)
            #手首座標系データ作成
            mp_data.WristCoordinateSystem()


            

            frameData = []
            if mp_data.hand_L is not None:
                frameData.append(mp_data.fromWrist_L)
            else:
                frameData.append(mp_data.fromWrist_Nones)

            if mp_data.hand_R is not None:
                frameData.append(mp_data.fromWrist_R)
            else:
                frameData.append(mp_data.fromWrist_Nones)
            
            TimeSeries_HandData.append(frameData)


            #print(frameData)
            #print("\n")


            #描画関連処理
            if isDraw:
                #手の関節描画
                if hand_results.multi_hand_landmarks is not None:
                    for landmarks_hand in hand_results.multi_hand_landmarks:
                        mp_drawing.draw_landmarks(
                            image=frame_flip,
                            landmark_list=landmarks_hand,
                            connections=mp_hands.HAND_CONNECTIONS,
                            landmark_drawing_spec=drawing_spec,
                            connection_drawing_spec=drawing_spec) # 特徴点の描画
                    #左右描画の追加(LR)
                    if mp_data.hand_L is not None:
                        cv2.putText(frame_flip,
                            text='L',
                            org=(int(mp_data.hand_L[0].x*frame_width), int(mp_data.hand_L[0].y*frame_height)),
                            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                            fontScale=1.0,
                            color=(255, 100, 0),
                            thickness=6,
                            lineType=cv2.LINE_4)
                    if mp_data.hand_R is not None:
                        cv2.putText(frame_flip,
                            text='R',
                            org=(int(mp_data.hand_R[0].x*frame_width), int(mp_data.hand_R[0].y*frame_height)),
                            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                            fontScale=1.0,
                            color=(0, 100, 255),
                            thickness=6,
                            lineType=cv2.LINE_4)

            cv2.imshow("linedFrame", frame_flip)
            cv2.moveWindow("linedFrame", 0, 0)

            #キーボード入力処理
            key = cv2.waitKey(1)
            if key & 0xFF == ord('q'):
                break
        
        else:
            break
    
    #cap.release()
    cv2.destroyAllWindows()

    #print("start output")
    outputCsv_TimeSeries_HandData(videoName, TimeSeries_HandData)

def createAll_waveform_handdata():
    
    tango_videoPath_list = glob.glob(tango_videoPath_dir +"*")
    tango_videoName_list = []
    for tango_videoPath in tango_videoPath_list:
        videoFile = os.path.basename(tango_videoPath)
        videoName, videoExt = os.path.splitext(videoFile)
        tango_videoName_list.append(videoName)

        waveform_handdata(tango_videoPath, videoName)
    

    
        


# TimeSeries_HandData[ フレーム番号 ][ 左or右 ][ ベクトル(0~19) ][ 成分(x,y) ]S
# csv出力用にデータをフレーム毎1行にまとめる
# 縦軸がフレーム，横軸については，手首の画像座標をwrist_x or yとし，それ以降は手首から各関節へのベクトルを表す(1x,1y,2x,2y ...)
# ! パルス的に生じる未検出箇所の穴埋めとして，該当フレームには直前フレームのデータをいれる
# ! 予定　パルス的に生じるLR反転の解決策
def outputCsv_TimeSeries_HandData(videoName ,TimeSeries_HandData):
    outputFile_Path = output_dir + videoName + ".csv"
    outputFile = open(outputFile_Path, 'w', newline='')
    outputData = []
    noneData = None
    historicalData = [[None,None],[None,None],[None,None],[None,None],[None,None],
                    [None,None],[None,None],[None,None],[None,None],[None,None],
                    [None,None],[None,None],[None,None],[None,None],[None,None],
                    [None,None],[None,None],[None,None],[None,None],[None,None],[None,None]]
    labels = ["左","wrist_x","wrist_y","1x","1y","2x","2y","3x","3y","4x","4y","5x","5y","6x","6y","7x","7y","8x","8y","9x","9y","10x","10y","11x","11y","12x","12y","13x","13y","14x","14y","15x","15y","16x","16y","17x","17y","18x","18y","19x","19y","20x","20y",
            "右","wrist_x","wrist_y","1x","1y","2x","2y","3x","3y","4x","4y","5x","5y","6x","6y","7x","7y","8x","8y","9x","9y","10x","10y","11x","11y","12x","12y","13x","13y","14x","14y","15x","15y","16x","16y","17x","17y","18x","18y","19x","19y","20x","20y"]
    outputData.append(labels)
    for frame_HandData in TimeSeries_HandData:
        output_row = ["",] # 位置調整
        for OneHandData in frame_HandData:
            jointNum = 0 # 0 or 1~20
            for jointData in OneHandData:
                axisNum = 0 # 0 or 1
                for axisData in jointData:
                    if axisData is None:
                        output_row.append(str(historicalData[jointNum][axisNum]))
                    else:
                        output_row.append(str(axisData))
                        historicalData[jointNum][axisNum] = axisData
                    axisNum = axisNum + 1
                jointNum = jointNum + 1
            output_row.append("") # 位置調整
        outputData.append(output_row) #フレーム毎に追加
    writer = csv.writer(outputFile)
    writer.writerows(outputData)
    outputFile.close()
    print("saved as " + outputFile_Path)



if __name__ == "__main__":
    tango_videoPath_dir = "C:/Users/root/Desktop/hisa_reserch/HandMotion_SimilarSearch/edited_video/tango/"
    output_dir = "C:/Users/root/Desktop/hisa_reserch/HandMotion_SimilarSearch/TimeSeries_HandData/tango/"

    #MediaPipe周辺設定
    mp_drawing = mp.solutions.drawing_utils
    drawing_spec = mp_drawing.DrawingSpec(color=[0, 180, 0], thickness=2, circle_radius=4)
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode= False, 
        max_num_hands=2,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) # 1に近づける程精度向上, 検出時間増加
    """
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(
        #upper_body_only=True,
        model_complexity=1,
        enable_segmentation=True,
        min_detection_confidence=0.5)"""

    isDraw = True
    isVecsum = True 

    #waveform_handdata()
    createAll_waveform_handdata()

    print("ended")