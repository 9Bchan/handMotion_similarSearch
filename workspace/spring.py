import glob
import csv
from natsort import natsorted
import os
import sys
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import pandas as pd



# 検索対象データ登録用クラス
class TargetDataBase():
    def __init__(self):
        self.AllVelocity_TShandData_L = [] # AllVelocity_TShandData_L[データ名][フレーム][要素(0~41)]
        self.AllVelocity_TShandData_R = []
        self.AllDataNum = []
        self.labels = None

class SearchData():
    def __init__(self):
        self.Velocity_TShandData_L = None # Velocity_TShandData_L[データ名][フレーム][要素(0~41)]
        self.Velocity_TShandData_R = None

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

class Spring():
    def __init__(self):
        self.search_data = None # search data
        self.target_data = None # target data
        self.path = None        
        self.dataDist = None
        self.dtwDist = None
        self.costMatrix = None
    
    # 距離計算
    def dist(self,x,y):
        return (x-y)**2

    # 最小値返却
    def get_min(self, m0, m1, m2, i, j):
        if m0 < m1:
            if m0 < m2:
                return i - 1, j, m0
            else:
                return i - 1, j - 1, m2
        else:
            if m1 < m2:
                return i, j - 1, m1
            else:
                return i - 1, j - 1, m2

    def dtw(self):
        x = self.search_data
        y = self.target_data
        self.dataDist = np.array(x).reshape(1, -1)**2 + np.array(y).reshape(-1, 1)**2

        len_x = len(x)
        len_y = len(y)

        print(len_x)
        print(len_y)

        costM = np.zeros((len_x, len_y))                   # コスト行列(x と y のある2点間の距離を保存
        distM = np.zeros((len_x, len_y, 2), int) # 距離行列(x と y の最短距離を保存)

        costM[0, 0] = self.dist(x[0], y[0])

        for i in range(len_x):
            costM[i,0] = costM[i - 1, 0] + self.dist(x[i], y[0])
            distM[i, 0] = [i-1, 0]

        for j in range(1, len_y):
            costM[0, j] = costM[0, j - 1] + self.dist(x[0], y[j])
            distM[0, j] = [0, j - 1]

        for i in range(1, len_x):
            for j in range(1, len_y):
                pi, pj, m = self.get_min(costM[i - 1, j],
                                    costM[i, j - 1],
                                    costM[i - 1, j - 1],
                                    i, j)
                costM[i, j] = self.dist(x[i], y[j]) + m
                distM[i, j] = [pi, pj]

        cost = costM[-1, -1]
        
        path = [[len_x - 1, len_y - 1]]
        i = len_x - 1
        j = len_y - 1

        while ((distM[i, j][0] != 0) or (distM[i, j][1] != 0)):
            path.append(distM[i, j])
            i, j = distM[i, j].astype(int)
        path.append([0,0])

        self.path = np.array(path)
        self.dtwDist = cost
        self.costMatrix = costM

    def partial_dtw(self):
        x = self.search_data
        y = self.target_data
        self.dataDist = np.array(x).reshape(1, -1)**2 + np.array(y).reshape(-1, 1)**2

        len_x = len(x)
        len_y = len(y)

        costM = np.zeros((len_x, len_y))
        distM = np.zeros((len_x, len_y, 2), int)

        costM[0, 0] = self.dist(x[0], y[0])
        for i in range(len_x):
            costM[i, 0] = self.dist(x[i], y[0])
            distM[i, 0] = [0, 0]

        for j in range(1, len_y):
            costM[0, j] = costM[0, j - 1] + self.dist(x[0], y[j])
            distM[0, j] = [0, j - 1]

        for i in range(1, len_x):
            for j in range(1, len_y):
                pi, pj, m = self.get_min(costM[i - 1, j],
                                    costM[i, j - 1],
                                    costM[i - 1, j - 1],
                                    i, j)
                costM[i, j] = self.dist(x[i], y[j]) + m
                distM[i, j] = [pi, pj]
        t_end = np.argmin(costM[:,-1])
        cost = costM[t_end, -1]
        
        path = [[t_end, len_y - 1]]
        i = t_end
        j = len_y - 1

        while (distM[i, j][0] != 0 or distM[i, j][1] != 0):
            path.append(distM[i, j])
            i, j = distM[i, j].astype(int)

        self.path = np.array(path)
        self.dtwDist = cost

    def plot_path(self):
        paths = [np.array(self.path)]
        A = self.search_data
        B = self.target_data
        D = self.dataDist

        plt.figure(figsize=(5,5))
        gs = gridspec.GridSpec(2, 2,
                        width_ratios=[1,5],
                        height_ratios=[5,1]
                        )
        ax1 = plt.subplot(gs[0])
        ax2 = plt.subplot(gs[1])
        ax4 = plt.subplot(gs[3])

        ax2.pcolor(D, cmap=plt.cm.Blues)
        ax2.get_xaxis().set_ticks([])
        ax2.get_yaxis().set_ticks([])
        
        for path in paths:
            ax2.plot(path[:,0]+0.5, path[:,1]+0.5, c="C3")
        
        ax4.plot(A)
        ax4.set_xlabel("$X$")
        ax1.invert_xaxis()
        ax1.plot(B, range(len(B)), c="C1")
        ax1.set_ylabel("$Y$")

        ax2.set_xlim(0, len(A))
        ax2.set_ylim(0, len(B))
        plt.show()

    def plot_connection(self):
        X = self.search_data
        Y = self.target_data
        for line in self.path:
            plt.plot(line, [X[line[0]], Y[line[1]]], linewidth=0.8, c="gray")
        plt.plot(X)
        plt.plot(Y)
        #plt.plot(self.path[:,0], X[self.path[:,0]], c="C2")
        plt.show()


# 検索対象データの読み込み
def load_targetData(targetData_dirPath):
    print("Start loading target data")
    targetData_filePath_list = glob.glob(targetData_dirPath +"*") # データのパス取得

    if targetData_filePath_list is not None:
        for filePath in natsorted(targetData_filePath_list): # ファイルを番号順に読み込むためにnatsortedを使用
            treat_TShandData = Treat_timeSeriesHandData()
            treat_TShandData.arrangement(filePath)
            treat_TShandData.calc_frameDifference()

            fileName = os.path.splitext(os.path.basename(filePath))[0]

            # データベース登録
            target_DataBase.AllVelocity_TShandData_L.append(treat_TShandData.velocity_TShandData_L)
            target_DataBase.AllVelocity_TShandData_R.append(treat_TShandData.velocity_TShandData_R)
            target_DataBase.AllDataNum.append(fileName)
            target_DataBase.labels = treat_TShandData.labels
    
    print("Completed loading target data")

# 検索データの読み込み
def load_searchData(searchData_Path):
    if searchData_Path is not None:
        treat_TShandData = Treat_timeSeriesHandData()
        treat_TShandData.arrangement(searchData_Path)
        treat_TShandData.calc_frameDifference()

        search_Data.Velocity_TShandData_L = treat_TShandData.velocity_TShandData_L
        search_Data.Velocity_TShandData_R = treat_TShandData.velocity_TShandData_R

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
                velocity_TShandData = target_DataBase.AllVelocity_TShandData_L[dataNum]
            if isSide == "r":
                baseLabel = 42
                velocity_TShandData= target_DataBase.AllVelocity_TShandData_R[dataNum]

            indexNum = int(input("The index number is <0~41> -> "))
            if not 0 <= indexNum <= 41:
                print(1/0) # 例外判定用

            # プロット用データ処理
            x = []
            y = []
            for frameNum, velocity_handData in enumerate(velocity_TShandData):
                x.append(frameNum)
                y.append(velocity_handData[indexNum])

            plt.figure("data["+ str(dataNum) +"] | hand["+ isSide +"] | label["+ target_DataBase.labels[indexNum + baseLabel] + "]")
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


def test():
    spring = Spring()

    """
    Cdata = pd.read_csv("./Cdata.csv", header=None)[1].values
    
    print(len(Cdata))

    X = Cdata
    Y = Cdata[100:500]

    print(X)
    print(Y)

    """
    X = []
    Y = []
    indexNum = 0

    velocity_TShandData = search_Data.Velocity_TShandData_R
    for frameNum, velocity_handData in enumerate(velocity_TShandData):
        X.append(velocity_handData[indexNum])
    
    dataNum = 21
    velocity_TShandData = target_DataBase.AllVelocity_TShandData_R[dataNum]
    for frameNum, velocity_handData in enumerate(velocity_TShandData):
        Y.append(velocity_handData[indexNum])

    spring.target_data = Y
    spring.search_data = X
    
    

    spring.partial_dtw()

    springPathLen = len(spring.path)
    print("frame : "+ str(spring.path[springPathLen-1][0]) +" ~ "+ str(spring.path[0][0]))

    spring.plot_path()
    #spring.plot_connection()



if __name__ == "__main__":
    #userDir = "C:/Users/hisa/Desktop/research/"
    userDir = "C:/Users/root/Desktop/hisa_reserch/"
    tango_data_dirPath = userDir + "HandMotion_SimilarSearch/TimeSeries_HandData_part/tango/"
    bunsyo_data_dirPath = userDir + "HandMotion_SimilarSearch/TimeSeries_HandData_part/bunsyo/"

    target_DataBase = TargetDataBase() # データベース用意
    search_Data = SearchData()

    load_targetData(tango_data_dirPath)
    load_searchData(bunsyo_data_dirPath + "4.csv")

    test()

    #ctrl_plt()

    #a