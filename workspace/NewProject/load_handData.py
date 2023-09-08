import glob
import csv
import os
import my_functions as my
import pandas as pd
import re
from tqdm import tqdm

FRAME_WIDTH = 1920
FRAME_HEIGHT = 1036

'''
#userDir = "C:/Users/hisa/Desktop/research/"
userDir = "C:/Users/root/Desktop/hisa_reserch/"
keyData_dirPath = userDir + "HandMotion_SimilarSearch/workspace/TimeSeries_HandPositionData/tango/"
tgtData_dirPath = userDir + "HandMotion_SimilarSearch/workspace/TimeSeries_HandPositionData/bunsyo/"
'''

# pandas 出力条件
#pd.set_option('display.max_rows', 500)
#pd.set_option('display.max_columns', 100)

# グローバル変数
position_labels = ['frame', '0x_L', '0y_L', '1x_L', '1y_L', '2x_L', '2y_L', '3x_L', '3y_L', '4x_L', '4y_L', '5x_L', '5y_L', '6x_L', '6y_L', '7x_L', '7y_L', '8x_L', '8y_L', '9x_L', '9y_L',
            '10x_L', '10y_L', '11x_L', '11y_L', '12x_L', '12y_L', '13x_L', '13y_L', '14x_L', '14y_L', '15x_L', '15y_L', '16x_L', '16y_L', '17x_L', '17y_L', '18x_L', '18y_L', '19x_L', '19y_L', '20x_L', '20y_L',
            '0x_R', '0y_R', '1x_R', '1y_R', '2x_R', '2y_R', '3x_R', '3y_R', '4x_R', '4y_R', '5x_R', '5y_R', '6x_R', '6y_R', '7x_R', '7y_R', '8x_R', '8y_R', '9x_R', '9y_R',
            '10x_R', '10y_R', '11x_R', '11y_R', '12x_R', '12y_R', '13x_R', '13y_R', '14x_R', '14y_R', '15x_R', '15y_R', '16x_R', '16y_R', '17x_R', '17y_R', '18x_R', '18y_R', '19x_R', '19y_R', '20x_R', '20y_R',
            'x_Body', 'y_Body']

# データ保存用クラス
class HandDataBase():
    def __init__(self):
        self.AllHandData_df = []
        self.AllFileNames = []
        self.position_labels = None
        self.originallyTotalFrame_list = []

def calc_handData(path):
        with open("params/feature_labels.txt", "r", encoding="utf-8") as f:
            feature_labels = f.read().split('\n')
        with open("params/position_labels.txt", "r", encoding="utf-8") as f:
            position_labels = f.read().split('\n')


        #print(position_labels)

        posInImg_df = pd.read_csv(path, dtype=str) # 画像中の手の関節位置データ取得
        origioriginallyTotalFrame = posInImg_df.shape[0]
        posInImg_excNone_df = posInImg_df[(~posInImg_df['0x_L'].str.contains('None')) & (~posInImg_df['0x_R'].str.contains('None'))] # None（未検出）を含む行を排除
        posInImg_excNone_df = posInImg_excNone_df.reset_index(drop=True) # index番号降り直し
        posInImg_excNone_df_colSize = posInImg_excNone_df.shape[0] - 1 # 0からカウントした列サイズ
        
        handData_df = pd.DataFrame(columns=feature_labels) # 作成するハンドデータ格納用データフレーム
        handData_df['frame'] = (posInImg_excNone_df.loc[1:posInImg_excNone_df_colSize, 'frame']).astype(int) # 2フレーム以降のフレーム番号を取得（速度情報作成時に1フレーム分情報が減る）

        # フレーム毎手首位置移動量計算
        wrist_labels = ['0x_L', '0y_L', '0x_R', '0y_R']
        posInImg_excNone_wrist_df = (posInImg_excNone_df.loc[0:posInImg_excNone_df_colSize, wrist_labels]).astype(float) # 指定した列名（手首情報）の列を取得
        frameNum_excNone_df = (posInImg_excNone_df.loc[0:posInImg_excNone_df_colSize, 'frame']).astype(int) # 指定した列名（フレーム）の列を取得
        vel_excNone_df = (posInImg_excNone_wrist_df.diff()).loc[1:posInImg_excNone_df_colSize,:] # 一つ前のフレームからの移動量を計算　(行間の差)（0フレーム目は計算できないためカット）
        frameInterval = (frameNum_excNone_df.diff()).loc[1:posInImg_excNone_df_colSize]#どこで何フレームカットされたか取得（Noneデータの場所）（0フレーム目は計算できないためカット）
        vel_excNone_df = vel_excNone_df.apply(lambda x: x / frameInterval) # vel_excNone_df行列をframeInterval列で列ごとに割る（フレームがカットされた箇所は線形的に移動したと考え，割って計算）
        vel_labels = ['vel_0x_L', 'vel_0y_L', 'vel_0x_R', 'vel_0y_R']
        handData_df[vel_labels] = vel_excNone_df[wrist_labels]

        posInImg_excNone_wrist_df = posInImg_excNone_wrist_df.loc[1:posInImg_excNone_df_colSize,:] # 0フレーム目をカット

        # 体中心から左右の手までのベクトル
        joint_body = ['x_Body', 'y_Body']
        posInImg_excNone_body_df = posInImg_excNone_df.loc[1:posInImg_excNone_df_colSize, joint_body].astype(float)
        posFromBody_labels = ['posFromBody_0x_L', 'posFromBody_0y_L', 'posFromBody_0x_R', 'posFromBody_0y_R']
        handData_df['posFromBody_0x_L'] = posInImg_excNone_wrist_df['0x_L'] - posInImg_excNone_body_df['x_Body']
        handData_df['posFromBody_0y_L'] = posInImg_excNone_wrist_df['0y_L'] - posInImg_excNone_body_df['y_Body']
        handData_df['posFromBody_0x_R'] = posInImg_excNone_wrist_df['0x_R'] - posInImg_excNone_body_df['x_Body']
        handData_df['posFromBody_0y_R'] = posInImg_excNone_wrist_df['0y_R'] - posInImg_excNone_body_df['y_Body']

        posFromBody_labels = ['posFromBody_0x_L', 'posFromBody_0y_L', 'posFromBody_0x_R', 'posFromBody_0y_R']
        
        # 手首からのベクトル計算
        joint_x_L_labels = ['1x_L', '2x_L', '3x_L', '4x_L', '5x_L', '6x_L', '7x_L', '8x_L', '9x_L', '10x_L', '11x_L', '12x_L', '13x_L', '14x_L', '15x_L', '16x_L', '17x_L', '18x_L', '19x_L', '20x_L'] # 手首を除いた手指関節ラベル
        posInImg_excNone_x_L_df = posInImg_excNone_df.loc[1:posInImg_excNone_df_colSize, joint_x_L_labels].astype(float) # （手首速度行列とサイズを合わせるため0フレーム目はカット）
        posFrmWrist_excNone_x_L_df = posInImg_excNone_x_L_df.copy()
        for jointLabel in joint_x_L_labels:
            posFrmWrist_excNone_x_L_df[jointLabel] = (posInImg_excNone_x_L_df[jointLabel] - posInImg_excNone_wrist_df['0x_L'])
        posFromWrist_x_L_labels = ['posFromWrist_1x_L', 'posFromWrist_2x_L', 'posFromWrist_3x_L', 'posFromWrist_4x_L', 'posFromWrist_5x_L', 'posFromWrist_6x_L', 'posFromWrist_7x_L', 'posFromWrist_8x_L', 'posFromWrist_9x_L', 'posFromWrist_10x_L', 'posFromWrist_11x_L', 'posFromWrist_12x_L', 'posFromWrist_13x_L', 'posFromWrist_14x_L', 'posFromWrist_15x_L', 'posFromWrist_16x_L', 'posFromWrist_17x_L', 'posFromWrist_18x_L', 'posFromWrist_19x_L', 'posFromWrist_20x_L']
        handData_df[posFromWrist_x_L_labels] = posFrmWrist_excNone_x_L_df[joint_x_L_labels]



        joint_y_L_labels = ['1y_L', '2y_L', '3y_L', '4y_L', '5y_L', '6y_L', '7y_L', '8y_L', '9y_L', '10y_L', '11y_L', '12y_L', '13y_L', '14y_L', '15y_L', '16y_L', '17y_L', '18y_L', '19y_L', '20y_L'] # 手首を除いた手指関節ラベル
        posInImg_excNone_y_L_df = posInImg_excNone_df.loc[1:posInImg_excNone_df_colSize, joint_y_L_labels].astype(float) # （手首速度行列とサイズを合わせるため0フレーム目はカット）
        posFrmWrist_excNone_y_L_df = posInImg_excNone_y_L_df.copy()
        for jointLabel in joint_y_L_labels:
            posFrmWrist_excNone_y_L_df[jointLabel] = (posInImg_excNone_y_L_df[jointLabel] - posInImg_excNone_wrist_df['0y_L'])
        posFromWrist_y_L_labels = ['posFromWrist_1y_L', 'posFromWrist_2y_L', 'posFromWrist_3y_L', 'posFromWrist_4y_L', 'posFromWrist_5y_L', 'posFromWrist_6y_L', 'posFromWrist_7y_L', 'posFromWrist_8y_L', 'posFromWrist_9y_L', 'posFromWrist_10y_L', 'posFromWrist_11y_L', 'posFromWrist_12y_L', 'posFromWrist_13y_L', 'posFromWrist_14y_L', 'posFromWrist_15y_L', 'posFromWrist_16y_L', 'posFromWrist_17y_L', 'posFromWrist_18y_L', 'posFromWrist_19y_L', 'posFromWrist_20y_L']
        handData_df[posFromWrist_y_L_labels] = posFrmWrist_excNone_y_L_df[joint_y_L_labels]


        
        joint_x_R_labels = ['1x_R', '2x_R', '3x_R', '4x_R', '5x_R', '6x_R', '7x_R', '8x_R', '9x_R', '10x_R', '11x_R', '12x_R', '13x_R', '14x_R', '15x_R', '16x_R', '17x_R', '18x_R', '19x_R', '20x_R'] # 手首を除いた手指関節ラベル
        posInImg_excNone_x_R_df = posInImg_excNone_df.loc[1:posInImg_excNone_df_colSize, joint_x_R_labels].astype(float) # （手首速度行列とサイズを合わせるため0フレーム目はカット）
        posFrmWrist_excNone_x_R_df = posInImg_excNone_x_R_df.copy()
        for jointLabel in joint_x_R_labels:
            posFrmWrist_excNone_x_R_df[jointLabel] = (posInImg_excNone_x_R_df[jointLabel] - posInImg_excNone_wrist_df['0x_R'])
        posFromWrist_x_R_labels = ['posFromWrist_1x_R', 'posFromWrist_2x_R', 'posFromWrist_3x_R', 'posFromWrist_4x_R', 'posFromWrist_5x_R', 'posFromWrist_6x_R', 'posFromWrist_7x_R', 'posFromWrist_8x_R', 'posFromWrist_9x_R', 'posFromWrist_10x_R', 'posFromWrist_11x_R', 'posFromWrist_12x_R', 'posFromWrist_13x_R', 'posFromWrist_14x_R', 'posFromWrist_15x_R', 'posFromWrist_16x_R', 'posFromWrist_17x_R', 'posFromWrist_18x_R', 'posFromWrist_19x_R', 'posFromWrist_20x_R']
        handData_df[posFromWrist_x_R_labels] = posFrmWrist_excNone_x_R_df[joint_x_R_labels]
        
        joint_y_R_labels = ['1y_R', '2y_R', '3y_R', '4y_R', '5y_R', '6y_R', '7y_R', '8y_R', '9y_R', '10y_R', '11y_R', '12y_R', '13y_R', '14y_R', '15y_R', '16y_R', '17y_R', '18y_R', '19y_R', '20y_R'] # 手首を除いた手指関節ラベル
        posInImg_excNone_y_R_df = posInImg_excNone_df.loc[1:posInImg_excNone_df_colSize, joint_y_R_labels].astype(float) # （手首速度行列とサイズを合わせるため0フレーム目はカット）
        posFrmWrist_excNone_y_R_df = posInImg_excNone_y_R_df.copy()
        for jointLabel in joint_y_R_labels:
            posFrmWrist_excNone_y_R_df[jointLabel] = (posInImg_excNone_y_R_df[jointLabel] - posInImg_excNone_wrist_df['0y_R'])
        posFromWrist_y_R_labels = ['posFromWrist_1y_R', 'posFromWrist_2y_R', 'posFromWrist_3y_R', 'posFromWrist_4y_R', 'posFromWrist_5y_R', 'posFromWrist_6y_R', 'posFromWrist_7y_R', 'posFromWrist_8y_R', 'posFromWrist_9y_R', 'posFromWrist_10y_R', 'posFromWrist_11y_R', 'posFromWrist_12y_R', 'posFromWrist_13y_R', 'posFromWrist_14y_R', 'posFromWrist_15y_R', 'posFromWrist_16y_R', 'posFromWrist_17y_R', 'posFromWrist_18y_R', 'posFromWrist_19y_R', 'posFromWrist_20y_R']
        handData_df[posFromWrist_y_R_labels] = posFrmWrist_excNone_y_R_df[joint_y_R_labels]

        #!!!!!!!!!!!!!!!!!!!!!!!!!



        #my.printlines(posFrmWrist_excNone_x_L_df)
        #my.printlines(posFrmWrist_excNone_y_L_df)
        #my.printlines(posFrmWrist_excNone_x_R_df)
        #my.printlines(posFrmWrist_excNone_y_R_df)

        
        #vel_labels = ['vel_0x_L', 'vel_0y_L', 'vel_0x_R', 'vel_0y_R']
        #handData_df[vel_labels] = vel_excNone_df[wrist_labels]
        #my.printline(handData_df)
        
        
        return handData_df, origioriginallyTotalFrame

def loadToDataBase_all(dirPath, handDataBase, label):
    my.printline("Start loading " + label + " data...")
    handData_filePath_list = glob.glob(dirPath +"*") # データのパス取得
    fileNum = len(handData_filePath_list)
    if fileNum == 0:
        my.printline(label + " data is not defined")
        os.sys.exit()

    if handData_filePath_list is not None:
        for filePath in tqdm(sorted(handData_filePath_list, key=natural_keys), bar_format="{l_bar}{bar:10}{r_bar}{bar:-10b}", colour='green'): # ファイルを番号順に読み込むためにnaortedを使用，進捗の表示にtqdmを使用
            handData_df, origioriginallyTotalFrame = calc_handData(filePath)
            fileName = os.path.splitext(os.path.basename(filePath))[0]
            
            # データベース登録
            handDataBase.AllHandData_df.append(handData_df)
            handDataBase.AllFileNames.append(fileName)
            handDataBase.originallyTotalFrame_list.append(origioriginallyTotalFrame)

            #print(filePath)
            #print(handData_df)
            
    my.printline("Completed")

def loadToDataBase_one(handDataBase, label, data_filePath):
    my.printline("Start loading " + label + " data...")

    handData_df, origioriginallyTotalFrame = calc_handData(data_filePath)
    fileName = os.path.splitext(os.path.basename(data_filePath))[0]
    
    # データベース登録
    handDataBase.AllHandData_df.append(handData_df)
    handDataBase.AllFileNames.append(fileName)
    handDataBase.originallyTotalFrame_list.append(origioriginallyTotalFrame)

    my.printline("Completed")

#　ファイルを番号順に読み込むために使用
def atoi(text):
    return int(text) if text.isdigit() else text
def natural_keys(text):
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]

# テスト用
if __name__ == '__main__':
    userDir = "C:/Users/hisa/Desktop/research/"
    #userDir = "C:/Users/root/Desktop/hisa_reserch/"
    keyData_dirPath = userDir + "HandMotion_SimilarSearch/workspace/TimeSeries_HandPositionData/"
    tgtData_dirPath = userDir + "HandMotion_SimilarSearch/workspace/TimeSeries_HandPositionData/"
    keyData_Path = keyData_dirPath + "test.csv"

    calc_handData('handData/key/0.csv')
