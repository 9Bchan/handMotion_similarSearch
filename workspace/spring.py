import glob
import csv
from natsort import natsorted
import os
import sys
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import pandas as pd

FRAME_WIDTH = 1920
FRAME_HEIGHT = 1036

class SearchData():
    def __init__(self):
        self.Velocity_TShandData_L = None # Velocity_TShandData_L[データ名][フレーム][要素(0~41)]
        self.Velocity_TShandData_R = None
        self.usedFrames =None

# 検索対象データ登録用クラス
class TargetDataBase():
    def __init__(self):
        self.AllVelocity_TShandData_L = [] # AllVelocity_TShandData_L[データ名][フレーム][要素(0~41)]
        self.AllVelocity_TShandData_R = []
        self.AllDataNum = []
        self.labels = None

    # データのグラフを表示
    def plt_originalData(): 
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


# csvデータ処理用クラス
class Treat_timeSeriesHandData():
    def __init__(self):
        self.totalFrame= None # 総フレーム数
        self.totalIndex = None # 単位フレームにおけるデータの要素数
        self.usedFrames =[]
        self.position_TShandData_L = [] # 位置データ推移
        self.position_TShandData_R = []
        self.velocity_TShandData_L = [] # 速度データ推移
        self.velocity_TShandData_R = []
        self.labels = None
        self.frameWidth = FRAME_WIDTH
        self.frameHeight = FRAME_HEIGHT

    def arrangement(self, handData_filePath): # 問い合わせ用csvデータ読み込み
        with open(handData_filePath, newline='') as f:
            csvreader = csv.reader(f)
            timeSeries_handData = [row for row in csvreader] # 一行目:ラベル 二行目以降:フレーム毎の左右のハンドデータ

            labelsData = timeSeries_handData[0] 
            if self.labels is None:
                self.labels = labelsData

            for frame_TShandData in timeSeries_handData[1:]:
                frame_data = frame_TShandData[:1]
                frame_handData_L = frame_TShandData[1:21*2+1] # 単位フレームにおけるハンドデータを左右に分割
                frame_handData_R = frame_TShandData[21*2+1:]
                
                
                if frame_handData_L[0] != 'None' and  frame_handData_R[0] != 'None': #そのフレームにおいて両手が検出されていればリストに追加
                    frame_handData_L_float = [float(i) for i in frame_handData_L] # 要素をstrからfloatに変換
                    frame_handData_R_float = [float(i) for i in frame_handData_R]
                    self.usedFrames.append(int(frame_data[0]))
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
                    #　正規化値をピクセル値に直すための係数
                    if index_num/2 :
                        frame_coef = self.frameWidth
                    else:
                        frame_coef = self.frameHeight

                    velocity_handData_L.append(self.position_TShandData_L[frame_num][index_num]*frame_coef - self.position_TShandData_L[frame_num - 1 ][index_num]*frame_coef)
                    velocity_handData_R.append(self.position_TShandData_R[frame_num][index_num]*frame_coef - self.position_TShandData_R[frame_num - 1 ][index_num]*frame_coef)
                self.velocity_TShandData_L.append(velocity_handData_L)
                self.velocity_TShandData_R.append(velocity_handData_R)
    
    

class UseSpring():
    def __init__(self):
        self.search_data = None # search data
        self.search_data_usedFrames = None # search data
        self.target_data = None # target data 

        self.paths = []   
        self.costs = [] 
        self.dataDist = None
        self.dtwDist = None
        self.costMatrix = None
        self.PATH_TH = None
        self.FRAME_TH = None
        self.dataCost = None
    
    # 距離計算
    def get_dist(self,x,y):
        return np.sqrt((x-y)**2)

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


    def spring(self):
        x = self.search_data
        y = self.target_data
        #self.dataDist = np.array(x).reshape(1, -1)**2 + np.array(y).reshape(-1, 1)**2
        self.dataDist = np.sqrt((np.array(x).reshape(1, -1) - np.array(y).reshape(-1, 1))**2)

        len_x = len(x)
        len_y = len(y)
        #print(len_y)

        costM = np.zeros((len_x, len_y))            # 合計距離行列 各点におけるパス開始点までの最短合計コストを保存
        linkM = np.zeros((len_x, len_y, 2), int)    # パス連結行列 各点において，その点を通るパスのひとつ前の点を保存
        sectM = np.zeros((len_x, len_y), int)       # パス開始点行列 各点において，その点を通るパスの開始点を保存


        costM[0, 0] = self.get_dist(x[0], y[0])

        for j in range(1, len_y):
            costM[0, j] = costM[0, j - 1] + self.get_dist(x[0], y[j])
            linkM[0, j] = [0, j - 1]
            sectM[0, j] = sectM[0, j - 1]

        for i in range(1, len_x):
            costM[i, 0] = self.get_dist(x[i], y[0])
            linkM[i, 0] = [0, 0]
            sectM[i, 0] = i



            for j in range(1, len_y):
                pi, pj, m = self.get_min(costM[i - 1, j],
                                    costM[i, j - 1],
                                    costM[i - 1, j - 1],
                                    i, j)
                costM[i, j] = self.get_dist(x[i], y[j]) + m
                linkM[i, j] = [pi, pj]
                sectM[i, j] = sectM[pi,pj]

            imin = np.argmin(costM[:(i+1), -1])
            #print(imin)

            dmin = costM[imin, -1]

            if dmin > self.PATH_TH: # 累算コストしきい値より小さい場合のみ　以降のパス出力コードを実行
                continue

            for j in range(1, len_y):
                if (costM[i,j] < dmin) and (sectM[i, j] < imin):
                    break
            else: # 直前のfor内でbreakが使用されなかった場合とforが実行されなかった場合処理される
                path = [[imin, len_y - 1]]
                temp_i = imin
                temp_j = len_y - 1

                while (linkM[temp_i, temp_j][0] != 0 or linkM[temp_i, temp_j][1] != 0):
                    path.append(linkM[temp_i, temp_j])
                    temp_i, temp_j = linkM[temp_i, temp_j].astype(int)
                
                #costM[sectM <= imin] = 10000000
                #for ci in range(imin):
                #    costM[ci, -1] = 10000000
                #costM[sectM <= imin] = 10000000

                
                original_path = np.array(path)

                path_head = original_path[0]
                #print(len(original_path))
                #print(len_y - 1)

                path_tail = original_path[len(original_path) - 1]
                #path_tail = original_path[len_y - 1]
                #print(len_y)

                #print((path_head[0] - path_tail[0]))

                #if int((path_head[0] - path_tail[0])) > self.FRAME_TH: # パスが指定フレーム数をまたがないときは出力しない
                self.paths.append(np.array(path))
                self.costs.append(dmin)
        self.dataCost = costM



    def mySpring(self):
        x = self.search_data
        y = self.target_data
        self.dataDist = np.sqrt((np.array(x).reshape(1, -1) - np.array(y).reshape(-1, 1))**2)

        len_x = len(x)
        len_y = len(y)

        D = np.zeros((len_x, len_y)) # コスト行列
        S = np.zeros((len_x, len_y), int) # パス開始点伝搬行列 (フレーム番号)

        D_link = np.zeros((len_x, len_y, 2), int) # コスト行列要素行列 コスト計算時の際，参照された要素を記録

        D[0, 0] = self.get_dist(x[0], y[0])

        for j in range(1, len_y):
            D[0, j] = D[0, j - 1] + self.get_dist(x[0], y[j])
            D_link[0, j] = [0, j - 1]
            #S[0, j] = S[0, j - 1]

        for t in range(1, len_x):
            D[t, 0] = self.get_dist(x[t], y[0])
            D_link[t, 0] = [0, 0]
            S[t, 0] = t

            for j in range(1, len_y):
                    pi, pj, m = self.get_min(D[t - 1, j],
                                        D[t, j - 1],
                                        D[t - 1, j - 1],
                                        t, j)
                    D[t, j] = self.get_dist(x[t], y[j]) + m
                    D_link[t, j] = [pi, pj]
                    S[t, j] = S[pi,pj]

            path_st = S[t, -1]

        D_cp = D.copy()

        for t in range(0, len_x):
            path_cost = D[t,-1]
            path_lenF = t - S[t, -1]
            #print(S[t, -1])

            

            if not path_cost < self.PATH_TH:
                continue
            #if not path_lenF < self.:
            #    continue
            
            ぱすのせんてい・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・
            t_link = t
            j_link = len_y - 1
            path = [[t_link, j_link]]
            while(D_link[t_link, j_link][0] != 0 or D_link[t_link, j_link][1] != 0):
                path.append(D_link[t_link, j_link])
                t_link, j_link = D_link[t_link, j_link].astype(int)

            self.paths.append(np.array(path))
            self.costs.append(path_cost)
            #print(self.paths)
        self.dataCost = D


    def plot_spring(self):
        X = self.search_data
        Y = self.target_data
        for path in self.paths:
            for line in path:
                plt.plot(line, [X[line[0]], Y[line[1]]], linewidth=0.8, c="gray")
            plt.plot(X)
            plt.plot(Y)
            plt.plot(path[:,0], X[path[:,0]], C="C2")
            plt.show()

    def plot_path(self):
        paths = self.paths
        costs = self.costs

        x = self.search_data
        y = self.target_data
        D = self.dataDist
        print(len(D))
        print("\n\n")
        D = (self.dataCost.T)
        print(len(D))


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
        
        printPathNum = 0
        maxcost = 0
        for pathNum, path in enumerate(paths):
            path_start = path[0]
            path_end = path[len(path) - 1]
            #if int((path_head[0] - path_tail[0])) > self.FRAME_TH:
            #print(path_start)
            #print(path_end)
            printPathNum = printPathNum + 1
            #print(path)
            ax2.plot(path[:,0]+0.5, path[:,1]+0.5, c="C3")
            springPathLen = len(path)
            if maxcost < costs[pathNum]:
                maxcost = costs[pathNum] 

            frame_start = self.search_data_usedFrames[path[springPathLen-1][0]]
            frame_end = self.search_data_usedFrames[path[0][0]]

            print("frame : "+ str(frame_start) +" ~ "+ str(frame_end) + " | cost : " + str(costs[pathNum]))
            
            
        print("total detected path : "+ str(printPathNum))
        print("max cost is : "+ str(maxcost))
        
        ax4.plot(x)
        ax4.set_xlabel("$X$")
        ax1.invert_xaxis()
        ax1.plot(y, range(len(y)), c="C1")
        ax1.set_ylabel("$Y$")

        ax2.set_xlim(0, len(x))
        ax2.set_ylim(0, len(y))
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

        
        search_Data.usedFrames = treat_TShandData.usedFrames
        search_Data.Velocity_TShandData_L = treat_TShandData.velocity_TShandData_L
        search_Data.Velocity_TShandData_R = treat_TShandData.velocity_TShandData_R

# 指定したデータのプロットを表示


def execute():
    
    while True:

        

        use_spring = UseSpring()

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
        indexNum = 1 # 0~41
        isSide = 'l' # l or r
        dataNum = 21

        

        if isSide == 'l':
            velocity_TShandData = search_Data.Velocity_TShandData_L
        elif isSide == 'r':
            velocity_TShandData = search_Data.Velocity_TShandData_R
        for frameNum, velocity_handData in enumerate(velocity_TShandData): # 全時系列データから特定のインデックスのみを時系列順に取り出す
            X.append(velocity_handData[indexNum])
        
        if isSide == 'l':
            velocity_TShandData = target_DataBase.AllVelocity_TShandData_L[dataNum]
        elif isSide == 'r':
            velocity_TShandData = target_DataBase.AllVelocity_TShandData_R[dataNum]
        for frameNum, velocity_handData in enumerate(velocity_TShandData):
            Y.append(velocity_handData[indexNum])



    
        try:
            use_spring.PATH_TH = int(input("path th is :"))
        except:
            break
        
        use_spring.search_data_usedFrames = search_Data.usedFrames
        use_spring.target_data = Y
        use_spring.search_data = X
        #use_spring.PATH_TH = 3000 # 出力パスの最大合計スコア
        use_spring.FRAME_TH = -1 # 出力パスの最低経由フレーム数
        

        use_spring.mySpring()


        use_spring.plot_path()
        #use_spring.plot_connection()



if __name__ == "__main__":
    #userDir = "C:/Users/hisa/Desktop/research/"
    userDir = "C:/Users/root/Desktop/hisa_reserch/"
    tango_data_dirPath = userDir + "HandMotion_SimilarSearch/workspace/TimeSeries_HandPositionData/tango/"
    bunsyo_data_dirPath = userDir + "HandMotion_SimilarSearch/workspace/TimeSeries_HandPositionData/bunsyo/"

    target_DataBase = TargetDataBase() # データベース用意
    search_Data = SearchData()

    load_targetData(tango_data_dirPath)
    load_searchData(bunsyo_data_dirPath + "4.csv")

    execute()

    #plt_originalData()
