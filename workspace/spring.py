import glob
import csv
from natsort import natsorted
import os
import sys
import matplotlib.pyplot as plt




# 問い合わせデータ登録用クラス
class QueryDataBase():
    def __init__(self):
        self.AllVelocity_TShandData_L = [] # AllVelocity_TShandData_L[データ名][フレーム][要素(0~41)]
        self.AllVelocity_TShandData_R = []
        self.AllDataNum = []
        self.labels = None

# csvデータ処理用クラス
class Treat_timeSeriesHandData():
    def __init__(self):
        self.totalFrame= None # 総フレーム数
        self.totalIndex = None # 単位フレームにおけるデータの要素数
        self.position_TShandData_L = [] # 位置データ推移
        self.position_TShandData_R = []
        self.velocity_TShandData_L = [] # 速度データ推移
        self.velocity_TShandData_R = []
        self.labels = None

    def arrangement(self, handData_filePath): # 問い合わせ用csvデータ読み込み
        with open(handData_filePath, newline='') as f:
            csvreader = csv.reader(f)
            timeSeries_handData = [row for row in csvreader] # 一行目:ラベル 二行目以降:フレーム毎の左右のハンドデータ

            labelsData = timeSeries_handData[0] 
            if self.labels is None:
                self.labels = labelsData

            for frame_TShandData in timeSeries_handData[1:]:
                frame_handData_L = frame_TShandData[:21*2] # 単位フレームにおけるハンドデータを左右に分割
                frame_handData_R = frame_TShandData[21*2:]
                
                if not frame_handData_L[0] == 'None' and not frame_handData_R[0] == 'None': #そのフレームにおいて両手が検出されていればリストに追加
                    frame_handData_L_float = [float(i) for i in frame_handData_L] # 要素をstrからfloatに変換
                    frame_handData_R_float = [float(i) for i in frame_handData_R]
                    self.position_TShandData_L.append(frame_handData_L_float)
                    self.position_TShandData_R.append(frame_handData_R_float)
            
            self.totalFrame = len(self.position_TShandData_L)
            self.totalIndex = len(self.position_TShandData_L[0])
                
    
    def calc_frameDifference(self): # フレームの差をとりデータのフレーム速度推移を求める
        for frame_num in range(self.totalFrame): # 左右のpositionリストの大きさは同じ フレーム数分ループ
            if not frame_num == 0: # 最初のフレームのみ除外
                velocity_handData_L = []
                velocity_handData_R = []
                for index_num in range(self.totalIndex): # 単位フレームのデータ要素数分ループ
                    velocity_handData_L.append(self.position_TShandData_L[frame_num][index_num] - self.position_TShandData_L[frame_num][index_num - 1])
                    velocity_handData_R.append(self.position_TShandData_R[frame_num][index_num] - self.position_TShandData_R[frame_num][index_num - 1])
                self.velocity_TShandData_L.append(velocity_handData_L)
                self.velocity_TShandData_R.append(velocity_handData_R)
                

# 問い合わせデータの読み込み
def load_queryData(queryData_dirPath):
    print("Start loading query data")
    queryData_filePath_list = glob.glob(queryData_dirPath +"*") # データのパス取得

    if queryData_filePath_list is not None:
        for filePath in natsorted(queryData_filePath_list): # ファイルを番号順に読み込むためにnatsortedを使用
            treat_TShandData = Treat_timeSeriesHandData()
            treat_TShandData.arrangement(filePath)
            treat_TShandData.calc_frameDifference()

            fileName = os.path.splitext(os.path.basename(filePath))[0]

            # データベース登録
            query_DataBase.AllVelocity_TShandData_L.append(treat_TShandData.velocity_TShandData_L)
            query_DataBase.AllVelocity_TShandData_R.append(treat_TShandData.velocity_TShandData_R)
            query_DataBase.AllDataNum.append(fileName)
            query_DataBase.labels = treat_TShandData.labels
    
    print("Completed loading query data")

# 指定したデータのプロットを表示
def ctrl_plt(): 
    print("Displays a plot of the specified data")
    isCont = True
    baseLabel = 0 # ラベル指定の調整用(左右について)

    while isCont:
        try:
            # データ指定フロー
            isSide = input("Left of Right <l/r> -> ")
            if not isSide == "l" and not isSide == "r":
                print(1/0) # 例外判定用

            dataNum = int(input("The data number is -> "))
            if isSide == "l":
                velocity_TShandData = query_DataBase.AllVelocity_TShandData_L[dataNum]
            if isSide == "r":
                baseLabel = 42
                velocity_TShandData= query_DataBase.AllVelocity_TShandData_R[dataNum]

            indexNum = int(input("The index number is <0~41> -> "))
            if not 0 <= indexNum <= 41:
                print(1/0) # 例外判定用

            # プロット用データ処理
            x = []
            y = []
            for frameNum, velocity_handData in enumerate(velocity_TShandData):
                x.append(frameNum)
                y.append(velocity_handData[indexNum])

            plt.figure("data["+ str(dataNum) +"] | hand["+ isSide +"] | label["+ query_DataBase.labels[indexNum + baseLabel] + "]")
            plt.plot(x, y, color="steelblue")
            plt.show()

        except:
            print("Invalid value entered")

        # 継続判定
        while True:
            ans = str(input("Do you want to run again? <y/n> ->"))
            if ans  == 'y':
                break
            if ans == 'n':
                print("exit the [ctrl_plot]")
                isCont = False
                break 



if __name__ == "__main__":
    userDir = "C:/Users/hisa/Desktop/research/"
    # "C:/Users/root/Desktop/hisa_reserch/"
    tango_data_dirPath = userDir + "HandMotion_SimilarSearch/TimeSeries_HandData_part/tango/"
    bunsyo_data_dirPath = userDir + "HandMotion_SimilarSearch/TimeSeries_HandData_part/tango/"

    query_DataBase = QueryDataBase() # データベース用意

    load_queryData(tango_data_dirPath)
    ctrl_plt()