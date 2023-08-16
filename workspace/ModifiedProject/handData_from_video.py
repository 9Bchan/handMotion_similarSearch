import mediapipe as mp
import cv2
import csv
import glob
import os
import PySimpleGUI as sg
from pathlib import Path

import my_functions as my

ALL_JOINT_NUM = 21

def pickPositionsData(hand_L, hand_R, pose):
    handPositions_L = []
    handPositions_R = []
    bodyPosition_center = []

    if hand_L is not None:
        for joint in hand_L:
            handPositions_L.append(str(joint.x))
            handPositions_L.append(str(joint.y))
    else:
        for _ in range(ALL_JOINT_NUM*2):
            handPositions_L.append('None')
    if hand_R is not None:
        for joint in hand_R:
            handPositions_R.append(str(joint.x))
            handPositions_R.append(str(joint.y))
    else:
        for _ in range(ALL_JOINT_NUM*2):
            handPositions_R.append('None')
    if pose is not None: # 一部が映った時点で全体が推測される
        shoulder_L = pose[mp_holistic.PoseLandmark.LEFT_SHOULDER]
        shoulder_R = pose[mp_holistic.PoseLandmark.RIGHT_SHOULDER]
        center_x = (shoulder_L.x + shoulder_R.x) / 2
        center_y = (shoulder_L.y + shoulder_R.y) / 2
        bodyPosition_center.append(str(center_x))
        bodyPosition_center.append(str(center_y))
    else:
        bodyPosition_center.append('None')
        bodyPosition_center.append('None')
    
    
    return handPositions_L, handPositions_R, bodyPosition_center

# 動画の全フレームの関節データのリストを取得
def Get_hand_joint_data(videoPath):
    cap = cv2.VideoCapture(videoPath)
    frame_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    frame_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

    TimeSeries_HandData =[] # TimeSeries_HandData[ フレーム番号 ][ 左or右 ][ ベクトル(0~20) <- 0は手首座標 ][ 成分(x,y) ]

    frameNum = 1

    while True:
        ret, frame = cap.read()

        hand_L = None
        hand_R = None
        if ret:
            frame_RGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            holistic_results = holistic.process(frame_RGB)

            
            if holistic_results.left_hand_landmarks is not None:
                hand_L = holistic_results.left_hand_landmarks.landmark
            if holistic_results.right_hand_landmarks is not None:
                hand_R = holistic_results.right_hand_landmarks.landmark
            if holistic_results.pose_landmarks is not None:
                pose = holistic_results.pose_landmarks.landmark

            """
            mp_data.MPdataOrganization(hand_results.multi_handedness,
                                        hand_results.multi_hand_landmarks)"""
            #手首座標系データ作成"""
            #mp_data.WristCoordinateSystem()

            handPositions_L, handPositions_R , bodyPosition_center = pickPositionsData(hand_L, hand_R, pose)

            

            frameData = []
            frameData.append(str(frameNum))
            frameData.extend(handPositions_L)
            frameData.extend(handPositions_R)
            frameData.extend(bodyPosition_center)

            TimeSeries_HandData.append(frameData)


            frameNum = frameNum + 1
            """
            #描画関連処理
            if isDraw:
                #手の関節描画
                mp_drawing.draw_landmarks(
                    frame, holistic_results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
                mp_drawing.draw_landmarks(
                    frame, holistic_results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
                #左右描画の追加(LR)
                if mp_data.hand_L is not None:
                    cv2.putText(frame,
                        text='L',
                        org=(int(mp_data.hand_L[0].x*frame_width), int(mp_data.hand_L[0].y*frame_height)),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=1.0,
                        color=(255, 100, 0),
                        thickness=6,
                        lineType=cv2.LINE_4)
                if mp_data.hand_R is not None:
                    cv2.putText(frame,
                        text='R',
                        org=(int(mp_data.hand_R[0].x*frame_width), int(mp_data.hand_R[0].y*frame_height)),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=1.0,
                        color=(0, 100, 255),
                        thickness=6,
                        lineType=cv2.LINE_4)
            
                cv2.imshow("linedFrame", frame)
                cv2.moveWindow("linedFrame", 0, 0)
                key = cv2.waitKey(1)
                if key & 0xFF == ord('q'):
                    os.sys.exit()
                    break
            """
        else:
            break
    cap.release()
    #cv2.destroyAllWindows()

    return TimeSeries_HandData

# csv出力用にデータをフレーム毎1行にまとめる
# 縦軸がフレーム，横軸については，手首の画像座標をwrist_x or yとし，それ以降は手首から各関節へのベクトルを表す(1x,1y,2x,2y ...)
# ! パルス的に生じる未検出箇所の穴埋めとして，該当フレームにはNoneデータをいれる
def outputCsv_TimeSeries_HandData(videoName, output_dir, TimeSeries_HandData):
    outputFile_Path = output_dir + videoName + ".csv"
    outputFile = open(outputFile_Path, 'w', newline='')
    outputData = []
    """
    labels = ['frame', '0x_L', '0y_L', '1x_L', '1y_L', '2x_L', '2y_L', '3x_L', '3y_L', '4x_L', '4y_L', '5x_L', '5y_L', '6x_L', '6y_L', '7x_L', '7y_L', '8x_L', '8y_L', '9x_L', '9y_L',
            '10x_L', '10y_L', '11x_L', '11y_L', '12x_L', '12y_L', '13x_L', '13y_L', '14x_L', '14y_L', '15x_L', '15y_L', '16x_L', '16y_L', '17x_L', '17y_L', '18x_L', '18y_L', '19x_L', '19y_L', '20x_L', '20y_L',
            '0x_R', '0y_R', '1x_R', '1y_R', '2x_R', '2y_R', '3x_R', '3y_R', '4x_R', '4y_R', '5x_R', '5y_R', '6x_R', '6y_R', '7x_R', '7y_R', '8x_R', '8y_R', '9x_R', '9y_R',
            '10x_R', '10y_R', '11x_R', '11y_R', '12x_R', '12y_R', '13x_R', '13y_R', '14x_R', '14y_R', '15x_R', '15y_R', '16x_R', '16y_R', '17x_R', '17y_R', '18x_R', '18y_R', '19x_R', '19y_R', '20x_R', '20y_R',
            'x_Body', 'y_Body']"""
    outputData.append(labels)
    outputData.extend(TimeSeries_HandData)

    writer = csv.writer(outputFile)
    writer.writerows(outputData)
    outputFile.close()
    my.printline("saved as " + outputFile_Path)

def create_handdata_forAllVideos(load_video_dir, output_dir):
    videoPath_list = glob.glob(load_video_dir +"*")
    videoName_list = []
    all_dataName = []

    # guiレイアウト
    BAR_MAX = len(videoPath_list)
    layout = [[sg.Text('変換中...')],
            [sg.ProgressBar(BAR_MAX, orientation='h', size=(20,20), key='-PROG-')],
            [sg.Cancel()]]
    window = sg.Window('プログレスバー', layout)

    bar_currentNum = 1
    for videoPath in videoPath_list:
        #　gui処理
        event, values = window.read(timeout=10)
        if event == 'Cancel' or event == sg.WIN_CLOSED:
            print("強制的にプログラムを終了しました")
            os.sys.exit()
        window['-PROG-'].update(bar_currentNum)
        bar_currentNum = bar_currentNum + 1


        # 変換処理
        videoFile = os.path.basename(videoPath)
        videoName, videoExt = os.path.splitext(videoFile)
        videoName_list.append(videoName)

        all_dataName.append([videoName]) 
        TimeSeries_HandData = Get_hand_joint_data(videoPath)
        outputCsv_TimeSeries_HandData(videoName, output_dir, TimeSeries_HandData)
    
    '''
    outputFileName = output_dir + "all_dataName.csv"
    outputFile = open(outputFileName, 'w', newline='')
    writer = csv.writer(outputFile)
    writer.writerows(all_dataName)
    outputFile.close()
    '''
    window.close()

def run_gui():
    '''
    ファイルを選択して読み込む
    '''
    # GUIのレイアウト
    layout = [
        [
            sg.Text("動画フォルダ"),
            sg.InputText(),
            sg.FolderBrowse(key="folder_from")
        ],
        [
            sg.Text("出力フォルダ"),
            sg.InputText(),
            sg.FolderBrowse(key="folder_to")
        ],
        [sg.Submit(key="submit"), sg.Cancel("Exit")]
    ]
    # WINDOWの生成
    window = sg.Window("ファイル選択", layout)

    # イベントループ
    while True:
        event, values = window.read(timeout=100)
        if event == 'Exit' or event == sg.WIN_CLOSED:
            os.sys.exit()
        elif event == 'submit':
            if values[0] == "":
                sg.popup("ファイルが入力されていません。")
                event = ""
            else:
                load_video_dir = values['folder_from'] + '/'
                output_dir = values['folder_to'] + '/'

                break
    window.close()
    
    return load_video_dir, output_dir

if __name__ == "__main__":
    
    #load_video_dir = "C:/Users/root/Desktop/hisa_reserch/HandMotion_SimilarSearch/edited_video/bunsyo/"
    #output_dir = "C:/Users/root/Desktop/hisa_reserch/HandMotion_SimilarSearch/TimeSeries_HandData2/bunsyo/"

    #MediaPipe周辺設定
    mp_drawing = mp.solutions.drawing_utils
    drawing_spec = mp_drawing.DrawingSpec(color=[0, 180, 0], thickness=2, circle_radius=4)

    mp_holistic = mp.solutions.holistic
    holistic =  mp_holistic.Holistic(
            static_image_mode=False,        # 静止画:True 動画:False
            #UPPER_BODY_ONLY=True,           # 上半身のみ:True 全身:False
            smooth_landmarks=True,          # ジッターを減らすかどうか
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7)

    isDraw = True
    with open("params/position_labels.txt", "r", encoding="utf-8") as f:
        labels = f.read().split('\n')

    load_video_dir, output_dir = run_gui()

    create_handdata_forAllVideos(load_video_dir, 
                                output_dir)


    my.printline("ended")