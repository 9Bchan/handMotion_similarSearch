import glob
import csv
import os

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
        self.AllDataNum = []
        self.labels = None

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
            os.sys.exit()

    def make_FeatureData(self):
        #print(self.position_TShandData_R)
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
                        #print(self.skippedFrameNums)
                        wristVelAndJointPos_handData_L.append((self.position_TShandData_L[frame_num][index_num]*frame_coef - self.position_TShandData_L[frame_num - 1][index_num]*frame_coef)/self.skippedFrameNums[frame_num])
                        wristVelAndJointPos_handData_R.append((self.position_TShandData_R[frame_num][index_num]*frame_coef - self.position_TShandData_R[frame_num - 1][index_num]*frame_coef)/self.skippedFrameNums[frame_num])
                    else: #それ以外は手首からの相対座標
                        wristVelAndJointPos_handData_L.append(self.position_TShandData_L[frame_num][index_num]*frame_coef - self.position_TShandData_L[frame_num][xORy]*frame_coef)
                        wristVelAndJointPos_handData_R.append(self.position_TShandData_R[frame_num][index_num]*frame_coef - self.position_TShandData_R[frame_num][xORy]*frame_coef)

                self.wristVelAndJointPos_TShandData_L.append(wristVelAndJointPos_handData_L)
                self.wristVelAndJointPos_TShandData_R.append(wristVelAndJointPos_handData_R)

# データの読み込み・保存を実行
def load_keyAndTgtData(keyData_dirPath, tgtData_dirPath, keyDataBase, tgtDataBase):
    print("Start loading key data...")
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
            keyDataBase.AllDataNum.append(fileName)
            keyDataBase.labels = treat_handData.labels
    print("Completed")

    print("Start loading target data...")
    handData_filePath_list = glob.glob(tgtData_dirPath +"*") # データのパス取得
    if handData_filePath_list is not None:
        for filePath in sorted(handData_filePath_list): # ファイルを番号順に読み込むためにnaortedを使用
            treat_handData = Treat_TimeSeriesHandData()
            treat_handData.arrangement(filePath)
            treat_handData.make_FeatureData()

            fileName = os.path.splitext(os.path.basename(filePath))[0]

            tgtDataBase.AllwristVelAndJointPos_L.append(treat_handData.wristVelAndJointPos_TShandData_L)
            tgtDataBase.AllwristVelAndJointPos_R.append(treat_handData.wristVelAndJointPos_TShandData_R)
            tgtDataBase.AllDataNum.append(fileName)
            tgtDataBase.labels = treat_handData.labels
    print("Completed")

'''
load_keyAndTgtData(keyData_dirPath, tgtData_dirPath)
keyDataBase = HandDataBase()
tgtDataBase = HandDataBase()
'''


