import glob
import csv
import os
import myfunc
import pandas as pd

FRAME_WIDTH = 1920
FRAME_HEIGHT = 1036

'''
#userDir = "C:/Users/hisa/Desktop/research/"
userDir = "C:/Users/root/Desktop/hisa_reserch/"
keyData_dirPath = userDir + "HandMotion_SimilarSearch/workspace/TimeSeries_HandPositionData/tango/"
tgtData_dirPath = userDir + "HandMotion_SimilarSearch/workspace/TimeSeries_HandPositionData/bunsyo/"
'''

# データ保存用クラス
class HandDataBase():
    def __init__(self):
        self.AllwristVelAndJointPos_L = [] # 手の情報（手首速度+手首からの手指関節）　[データ名][フレーム][要素(0~41)]　
        self.AllwristVelAndJointPos_R = []
        self.AllusedFrames = []
        self.AllDataNum = []
        self.labels = None

class Process_handData():
    def __init__(self):
        self.totalFrame= None # 総フレーム数
        self.partTotalFrame= None # フレーム範囲指定後の総フレーム数
        self.totalIndex = None # 単位フレームにおけるデータの要素数
        self.usedFrames =[] # 処理に利用されたフレームを記録 (検出が不十分なフレームは除外される)
        self.position_TShandData_L = [] # 位置データ推移
        self.position_TShandData_R = []
        self.wristVelAndJointPos_TShandData_L = [] 
        self.wristVelAndJointPos_TShandData_R = [] 
        self.skippedFrameNums = []
        self.labels = None 
        self.frameWidth = FRAME_WIDTH
        self.frameHeight = FRAME_HEIGHT
    
    def load_HandData(self, path):
        posInImg_df = pd.read_csv(path) # 画像中の手の関節位置データ取得
        # 行名:時系列順番号 列名:以下
        posInImg_df.columns = ['frame', '0x_L', '0y_L', '1x_L', '1y_L', '2x_L', '2y_L', '3x_L', '3y_L', '4x_L', '4y_L', '5x_L', '5y_L', '6x_L', '6y_L', '7x_L', '7y_L', '8x_L', '8y_L', '9x_L', '9y_L',
                    '10x_L', '10y_L', '11x_L', '11y_L', '12x_L', '12y_L', '13x_L', '13y_L', '14x_L', '14y_L', '15x_L', '15y_L', '16x_L', '16y_L', '17x_L', '17y_L', '18x_L', '18y_L', '19x_L', '19y_L', '20x_L', '20y_L',
                    '0x_R', '0y_R', '1x_R', '1y_R', '2x_R', '2y_R', '3x_R', '3y_R', '4x_R', '4y_R', '5x_R', '5y_R', '6x_R', '6y_R', '7x_R', '7y_R', '8x_R', '8y_R', '9x_R', '9y_R',
                    '10x_R', '10y_R', '11x_R', '11y_R', '12x_R', '12y_R', '13x_R', '13y_R', '14x_R', '14y_R', '15x_R', '15y_R', '16x_R', '16y_R', '17x_R', '17y_R', '18x_R', '18y_R', '19x_R', '19y_R', '20x_R', '20y_R']
        posInImg_excNone_df = posInImg_df[(~posInImg_df['0x_L'].str.contains('None')) & (~posInImg_df['0x_R'].str.contains('None'))] # Noneを含む行を排除
        #myfunc.printlist(posInImg_excNone_df)
        posInImg_excNone_df = posInImg_excNone_df.reset_index(drop=True) # index番号降り直し
        posInImg_excNone_df_colSize = posInImg_excNone_df.shape[0] - 1 # 0からカウントした列サイズ
        
        # フレーム毎手首位置移動量計算
        wrist_list = ['0x_L', '0y_L', '0x_R', '0y_R']
        """ # 次の処理と等価
        posInImg_excNone_df_part = (posInImg_excNone_df.loc[1:posInImg_excNone_df_colSize, wrist_list]).astype(float) # 指定した列名（手首情報）の列を取得
        posInImg_excNone_df_prev = (posInImg_excNone_df.loc[0:posInImg_excNone_df_colSize - 1, wrist_list]).astype(float) # 指定した列名（手首情報）の列を1フレームずらして取得
        vel_excNone_df = posInImg_excNone_df_part.reset_index(drop=True) - posInImg_excNone_df_prev.reset_index(drop=True) # 一つ前のフレームからの移動量を計算　(index番号をそろえて行列差を取る)
        vel_excNone_df.index = vel_excNone_df.index + 1 # index番号をフレーム番号に対応させてる
        """
        posInImg_excNone_df_part = (posInImg_excNone_df.loc[1:posInImg_excNone_df_colSize, wrist_list]).astype(float) # 指定した列名（手首情報）の列を取得
        vel_excNone_df = (posInImg_excNone_df_part.diff()).loc[1:posInImg_excNone_df_colSize,:] # 一つ前のフレームからの移動量を計算　(行間の差)（0フレーム目は計算できないためカット）
        #myfunc.printlist(vel_excNone_df)

        # 手首からのベクトル計算
        frameNum_excNone_df_part = (posInImg_excNone_df.loc[0:posInImg_excNone_df_colSize, 'frame']).astype(int) # 指定した列名（フレーム）の列を取得
        joint_x_L_list = ['1x_L', '2x_L', '3x_L', '4x_L', '5x_L', '6x_L', '7x_L', '8x_L', '9x_L', '10x_L', '11x_L', '12x_L', '13x_L', '14x_L', '15x_L', '16x_L', '17x_L', '18x_L', '19x_L', '20x_L'] # 手首を除いた手指関節ラベル
        posInImg_excNone_x_L_df = posInImg_excNone_df.loc[1:posInImg_excNone_df_colSize, joint_x_L_list].astype(float) # （手首速度行列とサイズを合わせるため0フレーム目はカット）
        posFrmWrist_excNone_x_L_df = posInImg_excNone_x_L_df.copy()
        for jointLabel in joint_x_L_list:
            posFrmWrist_excNone_x_L_df[jointLabel] = posInImg_excNone_x_L_df[jointLabel] - posInImg_excNone_df_part['0x_L']
        joint_y_L_list = ['1y_L', '2y_L', '3y_L', '4y_L', '5y_L', '6y_L', '7y_L', '8y_L', '9y_L', '10y_L', '11y_L', '12y_L', '13y_L', '14y_L', '15y_L', '16y_L', '17y_L', '18y_L', '19y_L', '20y_L'] # 手首を除いた手指関節ラベル
        posInImg_excNone_y_L_df = posInImg_excNone_df.loc[1:posInImg_excNone_df_colSize, joint_y_L_list].astype(float) # （手首速度行列とサイズを合わせるため0フレーム目はカット）
        posFrmWrist_excNone_y_L_df = posInImg_excNone_y_L_df.copy()
        for jointLabel in joint_y_L_list:
            posFrmWrist_excNone_y_L_df[jointLabel] = posInImg_excNone_y_L_df[jointLabel] - posInImg_excNone_df_part['0y_L']
        joint_x_R_Rist = ['1x_R', '2x_R', '3x_R', '4x_R', '5x_R', '6x_R', '7x_R', '8x_R', '9x_R', '10x_R', '11x_R', '12x_R', '13x_R', '14x_R', '15x_R', '16x_R', '17x_R', '18x_R', '19x_R', '20x_R'] # 手首を除いた手指関節ラベル
        posInImg_excNone_x_R_df = posInImg_excNone_df.loc[1:posInImg_excNone_df_colSize, joint_x_R_Rist].astype(float) # （手首速度行列とサイズを合わせるため0フレーム目はカット）
        posFrmWrist_excNone_x_R_df = posInImg_excNone_x_R_df.copy()
        for jointLabel in joint_x_R_Rist:
            posFrmWrist_excNone_x_R_df[jointLabel] = posInImg_excNone_x_R_df[jointLabel] - posInImg_excNone_df_part['0x_R']
        joint_y_R_Rist = ['1y_R', '2y_R', '3y_R', '4y_R', '5y_R', '6y_R', '7y_R', '8y_R', '9y_R', '10y_R', '11y_R', '12y_R', '13y_R', '14y_R', '15y_R', '16y_R', '17y_R', '18y_R', '19y_R', '20y_R'] # 手首を除いた手指関節ラベル
        posInImg_excNone_y_R_df = posInImg_excNone_df.loc[1:posInImg_excNone_df_colSize, joint_y_R_Rist].astype(float) # （手首速度行列とサイズを合わせるため0フレーム目はカット）
        posFrmWrist_excNone_y_R_df = posInImg_excNone_y_R_df.copy()
        for jointLabel in joint_y_R_Rist:
            posFrmWrist_excNone_y_R_df[jointLabel] = posInImg_excNone_y_R_df[jointLabel] - posInImg_excNone_df_part['0y_R']
        
        

        myfunc.printlist(frameNum_excNone_df_part)


        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!





        #print(posInImg_excNone_df)
        #print(posInImg_excNone_df.columns.str.contains('L'))
        #print(posInImg_excNone_df.loc[:, posInImg_excNone_df.columns.str.contains('L')]) # 特定の文字列を列名に含む列を取得
        os.sys.exit()


    def arrangement(self, handData_filePath): # 問い合わせ用csvデータ読み込み
        with open(handData_filePath, newline='') as f:
            csvreader = csv.reader(f)
            timeSeries_handData = [row for row in csvreader] # 一行目:ラベル 二行目以降:フレーム毎の左右のハンドデータ

            NUMOF_CUTFRAME_ST = 0
            NUMOF_CUTFRAME_ED = 0
            #NUMOF_CUTFRAME_ST = 20
            #NUMOF_CUTFRAME_ED = 30

            labelsData = timeSeries_handData[0] 
            if self.labels is None:
                self.labels = labelsData

            self.totalFrame = len(timeSeries_handData[1:])
            self.partTotalFrame = len(timeSeries_handData[NUMOF_CUTFRAME_ST + 1 : -(NUMOF_CUTFRAME_ED + 1)]) # 動画の最初と最後を一部カット
            
            skpCnt = 1 # 手未検出のフレームの連続数を記録
            for frame_TShandData in timeSeries_handData[NUMOF_CUTFRAME_ST + 1 : -(NUMOF_CUTFRAME_ED + 1)]:
                frame_data = frame_TShandData[:1] # 先頭データにはフレーム番号
                frame_handData_L = frame_TShandData[1:21*2+1] # 単位フレームにおけるハンドデータを左右に分割
                frame_handData_R = frame_TShandData[21*2+1:]
                
                
                if frame_handData_L[0] != 'None' and  frame_handData_R[0] != 'None': #そのフレームにおいて両手が検出されていればリストに追加
                    frame_handData_L_float = [float(i) for i in frame_handData_L] # 要素をstrからfloatに変換
                    frame_handData_R_float = [float(i) for i in frame_handData_R]
                    self.usedFrames.append(int(frame_data[0]))
                    self.position_TShandData_L.append(frame_handData_L_float)
                    self.position_TShandData_R.append(frame_handData_R_float)
                    self.skippedFrameNums.append(skpCnt)
                    skpCnt = 1
                else:
                    skpCnt = skpCnt + 1 
            
            #self.totalFrame = len(self.position_TShandData_L) 0.6695 - 0.73
            self.totalIndex = len(self.position_TShandData_L[0])
            #os.sys.exit()

# データ読込用クラス
class Treat_TimeSeriesHandData():
    def __init__(self):
        self.totalFrame= None # 総フレーム数
        self.partTotalFrame= None # フレーム範囲指定後の総フレーム数
        self.totalIndex = None # 単位フレームにおけるデータの要素数
        self.usedFrames =[] # 処理に利用されたフレームを記録 (検出が不十分なフレームは除外される)
        self.position_TShandData_L = [] # 位置データ推移
        self.position_TShandData_R = []
        self.wristVelAndJointPos_TShandData_L = [] 
        self.wristVelAndJointPos_TShandData_R = [] 
        self.skippedFrameNums = []
        self.labels = None 
        self.frameWidth = FRAME_WIDTH
        self.frameHeight = FRAME_HEIGHT
    
    def arrangement(self, handData_filePath): # 問い合わせ用csvデータ読み込み
        with open(handData_filePath, newline='') as f:
            csvreader = csv.reader(f)
            timeSeries_handData = [row for row in csvreader] # 一行目:ラベル 二行目以降:フレーム毎の左右のハンドデータ

            NUMOF_CUTFRAME_ST = 0
            NUMOF_CUTFRAME_ED = 0
            #NUMOF_CUTFRAME_ST = 20
            #NUMOF_CUTFRAME_ED = 30

            labelsData = timeSeries_handData[0] 
            if self.labels is None:
                self.labels = labelsData

            self.totalFrame = len(timeSeries_handData[1:])
            self.partTotalFrame = len(timeSeries_handData[NUMOF_CUTFRAME_ST + 1 : -(NUMOF_CUTFRAME_ED + 1)]) # 動画の最初と最後を一部カット
            
            skpCnt = 1 # 手未検出のフレームの連続数を記録
            for frame_TShandData in timeSeries_handData[NUMOF_CUTFRAME_ST + 1 : -(NUMOF_CUTFRAME_ED + 1)]:
                frame_data = frame_TShandData[:1] # 先頭データにはフレーム番号
                frame_handData_L = frame_TShandData[1:21*2+1] # 単位フレームにおけるハンドデータを左右に分割
                frame_handData_R = frame_TShandData[21*2+1:]
                
                
                if frame_handData_L[0] != 'None' and  frame_handData_R[0] != 'None': #そのフレームにおいて両手が検出されていればリストに追加
                    frame_handData_L_float = [float(i) for i in frame_handData_L] # 要素をstrからfloatに変換
                    frame_handData_R_float = [float(i) for i in frame_handData_R]
                    self.usedFrames.append(int(frame_data[0]))
                    self.position_TShandData_L.append(frame_handData_L_float)
                    self.position_TShandData_R.append(frame_handData_R_float)
                    self.skippedFrameNums.append(skpCnt)
                    skpCnt = 1
                else:
                    skpCnt = skpCnt + 1 
            
            #self.totalFrame = len(self.position_TShandData_L) 0.6695 - 0.73
            self.totalIndex = len(self.position_TShandData_L[0])
            #os.sys.exit()

    def make_FeatureData(self):
        #myfunc.printline(self.position_TShandData_R)
        for frame_num in range(len(self.usedFrames)): # 左右のpositionリストの大きさは同じ フレーム数分ループ
            if not frame_num == 0: # 最初のフレームのみ除外
                wristVelAndJointPos_handData_L = []
                wristVelAndJointPos_handData_R = []
                for index_num in range(self.totalIndex): # 単位フレームのデータ要素数分ループ
                    xORy = 0 
                    #　正規化値をピクセル値に直すための係数
                    if index_num%2: # 奇数
                        xORy = 1 # x:0 y:1
                        #frame_coef = self.frameWidth
                        frame_coef = self.frameHeight
                    else:   # 偶数
                        xORy = 0
                        #frame_coef = self.frameHeight
                        frame_coef = self.frameWidth
                    
                    if index_num == 0 or index_num == 1: # 手首要素は速度情報
                        #myfunc.printline(self.skippedFrameNums)
                        wristVelAndJointPos_handData_L.append((self.position_TShandData_L[frame_num][index_num]*frame_coef - self.position_TShandData_L[frame_num - 1][index_num]*frame_coef)/self.skippedFrameNums[frame_num])
                        wristVelAndJointPos_handData_R.append((self.position_TShandData_R[frame_num][index_num]*frame_coef - self.position_TShandData_R[frame_num - 1][index_num]*frame_coef)/self.skippedFrameNums[frame_num])
                    else: #それ以外は手首からの相対座標
                        wristVelAndJointPos_handData_L.append(self.position_TShandData_L[frame_num][index_num]*frame_coef - self.position_TShandData_L[frame_num][xORy]*frame_coef)
                        wristVelAndJointPos_handData_R.append(self.position_TShandData_R[frame_num][index_num]*frame_coef - self.position_TShandData_R[frame_num][xORy]*frame_coef)

                self.wristVelAndJointPos_TShandData_L.append(wristVelAndJointPos_handData_L)
                self.wristVelAndJointPos_TShandData_R.append(wristVelAndJointPos_handData_R)

# データの読み込み・保存を実行
def load_keyAndTgtData(keyData_dirPath, tgtData_dirPath, keyDataBase, tgtDataBase):
    myfunc.printline("Start loading key data...")
    handData_filePath_list = glob.glob(keyData_dirPath +"*") # データのパス取得
    if handData_filePath_list is not None:
        for filePath in sorted(handData_filePath_list): # ファイルを番号順に読み込むためにnaortedを使用
            treat_handData = Treat_TimeSeriesHandData()
            treat_handData.arrangement(filePath)
            treat_handData.make_FeatureData()

            fileName = os.path.splitext(os.path.basename(filePath))[0]

            # データベース登録
            keyDataBase.AllwristVelAndJointPos_L.append(treat_handData.wristVelAndJointPos_TShandData_L)
            keyDataBase.AllwristVelAndJointPos_R.append(treat_handData.wristVelAndJointPos_TShandData_R)
            keyDataBase.AllusedFrames.append(treat_handData.usedFrames)
            keyDataBase.AllDataNum.append(fileName)
            keyDataBase.labels = treat_handData.labels

    if keyDataBase.AllwristVelAndJointPos_L == []:
        myfunc.printline("Key data is not defined")
        os.sys.exit()
    myfunc.printline("Completed")

    myfunc.printline("Start loading target data...")
    handData_filePath_list = glob.glob(tgtData_dirPath +"*") # データのパス取得
    if handData_filePath_list is not None:
        for filePath in sorted(handData_filePath_list): # ファイルを番号順に読み込むためにnaortedを使用
            treat_handData = Treat_TimeSeriesHandData()
            treat_handData.arrangement(filePath)
            treat_handData.make_FeatureData()

            fileName = os.path.splitext(os.path.basename(filePath))[0]

            tgtDataBase.AllwristVelAndJointPos_L.append(treat_handData.wristVelAndJointPos_TShandData_L)
            tgtDataBase.AllwristVelAndJointPos_R.append(treat_handData.wristVelAndJointPos_TShandData_R)
            keyDataBase.AllusedFrames.append(treat_handData.usedFrames)
            tgtDataBase.AllDataNum.append(fileName)
            tgtDataBase.labels = treat_handData.labels
    if keyDataBase.AllwristVelAndJointPos_L == []:
        myfunc.printline("Target data is not defined")
        os.sys.exit()
    myfunc.printline("Completed")

'''
load_keyAndTgtData(keyData_dirPath, tgtData_dirPath)
keyDataBase = HandDataBase()
tgtDataBase = HandDataBase()
'''
# テスト用
if __name__ == '__main__':
    userDir = "C:/Users/hisa/Desktop/research/"
    #userDir = "C:/Users/root/Desktop/hisa_reserch/"
    keyData_dirPath = userDir + "HandMotion_SimilarSearch/workspace/TimeSeries_HandPositionData/"
    tgtData_dirPath = userDir + "HandMotion_SimilarSearch/workspace/TimeSeries_HandPositionData/"
    keyData_Path = keyData_dirPath + "test.csv"


    process_handData = Process_handData()
    process_handData.load_HandData(keyData_Path)
