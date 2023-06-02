import glob
import csv
from natsort import natsorted
import os
import sys
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import pandas as pd
import time

FRAME_WIDTH = 1920
FRAME_HEIGHT = 1036

class SearchData():
    def __init__(self):
        self.Velocity_TShandData_L = None # Velocity_TShandData_L[データ名][フレーム][要素(0~41)]
        self.Velocity_TShandData_R = None
        self.wristVelAndJointPos_TShandData_L = None
        self.wristVelAndJointPos_TShandData_R = None
        self.usedFrames = None # 処理に利用されたフレームを記録 (検出が不十分なフレームは除外される)
        self.totalFrame = None
        self.totalElem = None # データの要素数

# 検索対象データ登録用クラス
class TargetDataBase():
    def __init__(self):
        self.AllVelocity_TShandData_L = [] # AllVelocity_TShandData_L[データ名][フレーム][要素(0~41)]
        self.AllVelocity_TShandData_R = []
        self.AllwristVelAndJointPos_TShandData_L = []
        self.AllwristVelAndJointPos_TShandData_R = []
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
        self.partTotalFrame= None # 総フレーム数
        self.totalIndex = None # 単位フレームにおけるデータの要素数
        self.usedFrames =[] # 処理に利用されたフレームを記録 (検出が不十分なフレームは除外される)
        self.position_TShandData_L = [] # 位置データ推移
        self.position_TShandData_R = []
        self.velocity_TShandData_L = [] # 速度データ推移
        self.velocity_TShandData_R = []
        self.wristVelAndJointPos_TShandData_L = [] 
        self.wristVelAndJointPos_TShandData_R = [] 
        self.skippedFrameNums = []
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

            self.totalFrame = len(timeSeries_handData[1:])
            skpCnt = 1
            for frame_TShandData in timeSeries_handData[1:]:
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
            
            #self.totalFrame = len(self.position_TShandData_L)
            self.totalIndex = len(self.position_TShandData_L[0])
    
    def arrangement2(self, handData_filePath): # 問い合わせ用csvデータ読み込み
        with open(handData_filePath, newline='') as f:
            csvreader = csv.reader(f)
            timeSeries_handData = [row for row in csvreader] # 一行目:ラベル 二行目以降:フレーム毎の左右のハンドデータ

            NUMOF_CUTFRAME_ST = 1
            NUMOF_CUTFRAME_ED = 1
            #NUMOF_CUTFRAME_ST = 20
            #NUMOF_CUTFRAME_ED = 30

            labelsData = timeSeries_handData[0] 
            if self.labels is None:
                self.labels = labelsData

            self.totalFrame = len(timeSeries_handData[1:])
            self.partTotalFrame = len(timeSeries_handData[NUMOF_CUTFRAME_ST + 1 : -NUMOF_CUTFRAME_ED]) # 動画の最初と最後を一部カット
            
            skpCnt = 1
            for frame_TShandData in timeSeries_handData[NUMOF_CUTFRAME_ST + 1 : -NUMOF_CUTFRAME_ED]:
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
                
    
    def calc_frameDifference(self): # フレームの差をとりデータのフレーム速度推移を求める
        for frame_num in range(len(self.usedFrames)): # 左右のpositionリストの大きさは同じ フレーム数分ループ
            if not frame_num == 0: # 最初のフレームのみ除外
                velocity_handData_L = []
                velocity_handData_R = []
                for index_num in range(self.totalIndex): # 単位フレームのデータ要素数分ループ
                    #　正規化値をピクセル値に直すための係数
                    if index_num%2 :
                        frame_coef = self.frameWidth
                    else:
                        frame_coef = self.frameHeight

                    velocity_handData_L.append(self.position_TShandData_L[frame_num][index_num]*frame_coef - self.position_TShandData_L[frame_num - 1 ][index_num]*frame_coef)
                    velocity_handData_R.append(self.position_TShandData_R[frame_num][index_num]*frame_coef - self.position_TShandData_R[frame_num - 1 ][index_num]*frame_coef)
                self.velocity_TShandData_L.append(velocity_handData_L)
                self.velocity_TShandData_R.append(velocity_handData_R)


    def make_FeatureData(self):
        #print(self.position_TShandData_R)
        for frame_num in range(len(self.usedFrames)): # 左右のpositionリストの大きさは同じ フレーム数分ループ
            if not frame_num == 0: # 最初のフレームのみ除外
                wristVelAndJointPos_handData_L = []
                wristVelAndJointPos_handData_R = []
                for index_num in range(self.totalIndex): # 単位フレームのデータ要素数分ループ
                    xORy = 0 # x:0 y:1
                    #　正規化値をピクセル値に直すための係数
                    if index_num%2: # 奇数
                        xORy = 1
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

        self.pathsAndCostData = [] # [パス開始フレーム, パス終了フレーム, コスト]*パス数 のデータセットを保存
    
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


    def dtw(self):
        x = self.search_data
        y = self.target_data
        self.dataDist = np.sqrt((np.array(x).reshape(1, -1) - np.array(y).reshape(-1, 1))**2)

        Tx = len(x)
        Ty = len(y)

        C = np.zeros((Tx, Ty))
        B = np.zeros((Tx, Ty, 2), int)

        C[0, 0] = self.get_dist(x[0], y[0])
        for i in range(Tx):
            C[i, 0] = C[i - 1, 0] + self.get_dist(x[i], y[0])
            B[i, 0] = [i-1, 0]

        for j in range(1, Ty):
            C[0, j] = C[0, j - 1] + self.get_dist(x[0], y[j])
            B[0, j] = [0, j - 1]

        for i in range(1, Tx):
            for j in range(1, Ty):
                pi, pj, m = self.get_min(C[i - 1, j],
                                    C[i, j - 1],
                                    C[i - 1, j - 1],
                                    i, j)
                C[i, j] = self.get_dist(x[i], y[j]) + m
                B[i, j] = [pi, pj]
        cost = C[-1, -1]
        
        path = [[Tx - 1, Ty - 1]]
        i = Tx - 1
        j = Ty - 1

        while ((B[i, j][0] != 0) or (B[i, j][1] != 0)):
            path.append(B[i, j])
            i, j = B[i, j].astype(int)
        path.append([0,0])

        self.paths.append(np.array(path))
        self.costs.append(cost)
        self.dataCost = C

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
        a = self.search_data
        b = self.target_data
        self.dataDist = np.sqrt((np.array(a).reshape(1, -1) - np.array(b).reshape(-1, 1))**2)

        len_a = len(a)
        len_b = len(b)

        D = np.zeros((len_a, len_b)) # コスト行列
        S = np.zeros((len_a, len_b), int) # パス開始点伝搬行列 (フレーム番号)

        D_link = np.zeros((len_a, len_b, 2), int) # コスト行列要素行列 コスト計算時の際，参照された要素を記録
        paths_st = [0] # 出力予定のパスのフレーム位置を記録

        D[0, 0] = self.get_dist(a[0], b[0])

        for j in range(1, len_b):
            D[0, j] = D[0, j - 1] + self.get_dist(a[0], b[j])
            D_link[0, j] = [0, j - 1]
            #S[0, j] = S[0, j - 1]

        for t in range(1, len_a):
            D[t, 0] = self.get_dist(a[t], b[0])
            D_link[t, 0] = [0, 0]
            S[t, 0] = t

            for j in range(1, len_b):
                    mt, mj, m = self.get_min(D[t - 1, j],
                                        D[t, j - 1],
                                        D[t - 1, j - 1],
                                        t, j)
                    D[t, j] = self.get_dist(a[t], b[j]) + m
                    D_link[t, j] = [mt, mj]
                    S[t, j] = S[mt, mj]

            #''' 出力パス制限ルート 1
            # 開始地点が重複するパスのうち最小コストであるパスを選定
            if S[t, -1] == S[paths_st[-1], -1] and D[t, -1] < D[paths_st[-1], -1]: # paths_stに最後に登録されているパスについて、開始地点が同じかつ、コストがより低いパスがあればpaths_stを更新
                paths_st[-1] = t
            if S[t, -1] != S[paths_st[-1], -1]:
                paths_st.append(t)
            #'''

            

            ''' 出力パス制限ルート 2
            # 同じ開始点を持つパスのうち、他のパスと区間が被らず、最小コストのパスを求める 
            if S[paths_st[-1], -1] != S[t, -1]: # 異なる開始点を持つパスの切り替わりを検知
                intervalEnd = S[t, -1]
            elif t == len_a - 1: # 最終フレームを検知 (異なる開始点を持つパスの切り替わりを検知、では最後の走査が行われないため)
                intervalEnd = t
            else:
                continue
            for pt in range(S[paths_st[-1], -1], intervalEnd): # 前回出力されたパスの終点位置から現在見ているパスの開始点-1(もしくは最終フレーム位置)までを走査
                if D[pt, -1] < D[paths_st[-1], -1]: 
                    paths_st[-1] = pt
            if not t == len_a - 1:   # 最終フレームでは必要ない
                paths_st.append(t) # 異なる開始点を持つパスの切り替わり直後の、パスの終了点を入れておく
            '''









        #''' 出力パス制限ルート
        for t in paths_st[1:]:
            path_cost = D[t,-1]
            path_lenF = t - S[t, -1]
            if path_cost > self.PATH_TH: # パスのコストが閾値より低ければ以降の処理を実行
                continue
            if path_lenF < self.FRAME_TH:
                continue

            relativeCost = float(self.PATH_TH) - float(path_cost) # 閾値基準の相対コスト
            #print("#")
            
            t_link = t
            j_link = len_b - 1
            path = [[t_link, j_link]]
            while(D_link[t_link, j_link][0] != 0 or D_link[t_link, j_link][1] != 0):
                path.append(D_link[t_link, j_link])
                t_link, j_link = D_link[t_link, j_link].astype(int)

            self.paths.append(np.array(path))
            self.costs.append(relativeCost)
        #'''

        ''' 全パス出力ルート
        for t in range(0, len_x):
            path_cost = D[t,-1]
            path_lenF = t - S[t, -1]
            #print(S[t, -1])

            if not path_cost < self.PATH_TH:
                continue
            #if not path_lenF < self.:
            #    continue
            
            t_link = t
            j_link = len_y - 1
            path = [[t_link, j_link]]
            while(D_link[t_link, j_link][0] != 0 or D_link[t_link, j_link][1] != 0):
                path.append(D_link[t_link, j_link])
                t_link, j_link = D_link[t_link, j_link].astype(int)

            self.paths.append(np.array(path))
            self.costs.append(path_cost)
            #print(self.paths)
        '''
        self.dataCost = D

    def make_pathsAndCostData(self):
        paths = self.paths
        costs = self.costs

        a = self.search_data
        b = self.target_data
        #D = self.dataDist.T # グラフ背景に使用する行列
        D = (self.dataCost.T)

        totalPathNum = 0
        maxcost = 0


        for pathNum, path in enumerate(paths):
            path_start = path[0]
            path_end = path[len(path) - 1]

            totalPathNum = totalPathNum + 1

            springPathLen = len(path)
            if maxcost < costs[pathNum]:
                maxcost = costs[pathNum] 

            frame_start = self.search_data_usedFrames[path[springPathLen-1][0]]
            frame_end = self.search_data_usedFrames[path[0][0]+1]

            self.pathsAndCostData.append([frame_start, frame_end, costs[pathNum]])
            #print("frame : "+ str(frame_start) +" ~ "+ str(frame_end) + " | cost : " + str(costs[pathNum]))
        #print("total detected path : "+ str(totalPathNum))
        #print("max cost is : "+ str(maxcost))
        #print("##########################")



    def plot_path(self):
        paths = self.paths
        costs = self.costs

        a = self.search_data
        b = self.target_data
        D = self.dataDist # グラフ背景に使用する行列
        #D = (self.dataCost.T)

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
        
        totalPathNum = 0
        maxcost = 0
        for pathNum, path in enumerate(paths):
            path_start = path[0]
            path_end = path[len(path) - 1]

            totalPathNum = totalPathNum + 1

            ax2.plot(path[:,0]+0.5, path[:,1]+0.5, c="C3")
            springPathLen = len(path)
            if maxcost < costs[pathNum]:
                maxcost = costs[pathNum] 

            frame_start = self.search_data_usedFrames[path[springPathLen-1][0]]
            frame_end = self.search_data_usedFrames[path[0][0]+1] # フレーム速度位置からフレーム位置に直すため+1
            print("frame : "+ str(frame_start) +" ~ "+ str(frame_end) + " | cost : " + str(costs[pathNum]))
        print("total detected path : "+ str(totalPathNum))
        print("max cost is : "+ str(maxcost))

        ax4.plot(a)
        ax4.set_xlabel("$X$")

        ax1.invert_xaxis()
        ax1.plot(b, range(len(b)), c="C1")
        ax1.set_ylabel("$Y$")

        ax2.set_xlim(0, len(a))
        ax2.set_ylim(0, len(b))

        plt.show()

    def plot_connection(self):
        X = self.search_data
        B = self.target_data
        for path in self.paths:
            for line in path:
                plt.plot(line, [X[line[0]], B[line[1]]], linewidth=0.8, c="gray")
            plt.plot(X)
            plt.plot(B)
            #plt.plot(path[:,0], X[path[:,0]], c="C2")
            plt.show()

# 検索対象データの読み込み
def load_targetData(targetData_dirPath):
    print("Start loading target data")
    targetData_filePath_list = glob.glob(targetData_dirPath +"*") # データのパス取得

    if targetData_filePath_list is not None:
        for filePath in natsorted(targetData_filePath_list): # ファイルを番号順に読み込むためにnatsortedを使用
            treat_TShandData = Treat_timeSeriesHandData()
            treat_TShandData.arrangement2(filePath)
            treat_TShandData.make_FeatureData()

            fileName = os.path.splitext(os.path.basename(filePath))[0]

            # データベース登録
            target_DataBase.AllwristVelAndJointPos_TShandData_L.append(treat_TShandData.wristVelAndJointPos_TShandData_L)
            target_DataBase.AllwristVelAndJointPos_TShandData_R.append(treat_TShandData.wristVelAndJointPos_TShandData_R)
            target_DataBase.AllDataNum.append(fileName)
            target_DataBase.labels = treat_TShandData.labels
    
    print(target_DataBase.AllDataNum)
    print("Completed loading target data")

# 検索データの読み込み
def load_searchData(searchData_Path):
    print("Start loading search data")
    if searchData_Path is not None:
        treat_TShandData = Treat_timeSeriesHandData()
        treat_TShandData.arrangement2(searchData_Path)
        treat_TShandData.make_FeatureData()

        search_Data.totalElem = len(treat_TShandData.labels)
        search_Data.totalFrame = treat_TShandData.partTotalFrame
        search_Data.usedFrames = treat_TShandData.usedFrames
        search_Data.wristVelAndJointPos_TShandData_L = treat_TShandData.wristVelAndJointPos_TShandData_L
        search_Data.wristVelAndJointPos_TShandData_R = treat_TShandData.wristVelAndJointPos_TShandData_R
    print("Completed loading search data")

# 指定したデータのプロットを表示



def calc_tangoCost(dataNum):
    totalElemNum = search_Data.totalElem - 1 # フレーム番号を除いたデータの全要素数

    PACdata_L = []
    PACdata_R = []

    costPerFrame = [0 for i in range(search_Data.totalFrame)]
    cntPerFrame = [0 for i in range(search_Data.totalFrame)]
    cntP = 0
    frameNums = [i for i in range(search_Data.totalFrame)]

    for elemNum in range(int(totalElemNum/2)): # LR を同時に処理
        #print("element : "+ str(elemNum))
        # 時系列ハンドデータから指定した要素のみの時系列データを抽出

        #''' 左手　%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        A_L = []
        velocity_TShandData = search_Data.wristVelAndJointPos_TShandData_L
        for velocity_handData in velocity_TShandData: # 全時系列データから特定のインデックスのみを時系列順に取り出す
            A_L.append(velocity_handData[elemNum]) # handのelement
        B_L = []
        velocity_TShandData = target_DataBase.AllwristVelAndJointPos_TShandData_L[dataNum] # targetデータではデータ番号が必要
        for velocity_handData in velocity_TShandData:
            B_L.append(velocity_handData[elemNum])
        
        
        use_spring_L = UseSpring() #初期化
        use_spring_L.PATH_TH = 2000
        use_spring_L.FRAME_TH = 10
        use_spring_L.search_data_usedFrames = search_Data.usedFrames
        use_spring_L.target_data = B_L
        use_spring_L.search_data = A_L
        use_spring_L.mySpring()
        use_spring_L.make_pathsAndCostData()
        #PACdata_L.append(use_spring.pathsAndCostData)
        for frameNum in frameNums:
            cost_max = 0 
            for pathsAndCost in use_spring_L.pathsAndCostData:
                path_start = pathsAndCost[0]
                path_end = pathsAndCost[1]
                path_cost = pathsAndCost[2]
                if path_start <= frameNum <= path_end and cost_max < path_cost:
                    cost_max = path_cost
            costPerFrame[frameNum] = costPerFrame[frameNum] + cost_max
            if not cost_max == 0:
                cntPerFrame[frameNum] = cntPerFrame[frameNum] + 1

        #左手　%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% '''

                
        ''' ルート2
        for pathsAndCost in use_spring_L.pathsAndCostData:
            path_start = pathsAndCost[0]
            path_end = pathsAndCost[1]
            path_cost = pathsAndCost[2]
            for frameNum in range(path_start, path_end):
                costPerFrame[frameNum] = costPerFrame[frameNum] + path_cost
                cntPerFrame[frameNum] = cntPerFrame[frameNum] + 1
                if frameNum == 300:
                    cntP = cntP + 1
        ''' 

        #''' 右手　%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

        A_R = []
        velocity_TShandData = search_Data.wristVelAndJointPos_TShandData_R
        for velocity_handData in velocity_TShandData: # 全時系列データから特定のインデックスのみを時系列順に取り出す
            A_R.append(velocity_handData[elemNum]) # handのelement
        B_R = []
        velocity_TShandData = target_DataBase.AllwristVelAndJointPos_TShandData_R[dataNum]
        for velocity_handData in velocity_TShandData:
            B_R.append(velocity_handData[elemNum])

        use_spring_R = UseSpring()
        use_spring_R.PATH_TH = 2000
        use_spring_R.FRAME_TH = 10
        use_spring_R.search_data_usedFrames = search_Data.usedFrames
        use_spring_R.target_data = B_R
        use_spring_R.search_data = A_R
        use_spring_R.mySpring()
        use_spring_R.make_pathsAndCostData()

        for frameNum in frameNums:
            cost_max = 0 
            for pathsAndCost in use_spring_R.pathsAndCostData:
                path_start = pathsAndCost[0]
                path_end = pathsAndCost[1]
                path_cost = pathsAndCost[2]
                if path_start <= frameNum <= path_end and cost_max < path_cost:
                    cost_max = path_cost
            costPerFrame[frameNum] = costPerFrame[frameNum] + cost_max
            if not cost_max == 0:
                cntPerFrame[frameNum] = cntPerFrame[frameNum] + 1

        #右手　%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% '''

        ''' ルート2
        for pathsAndCost in use_spring_R.pathsAndCostData:
            path_start = pathsAndCost[0]
            path_end = pathsAndCost[1]
            path_cost = pathsAndCost[2]
            for frameNum in range(path_start, path_end):
                costPerFrame[frameNum] = costPerFrame[frameNum] + path_cost
                cntPerFrame[frameNum] = cntPerFrame[frameNum] + 1
                if frameNum == 300:
                    cntP = cntP + 1
        '''
    #print("total execution time : " + str(time.perf_counter() - time_start))
    #print("calclation time : " + str(time.perf_counter() - time_calc))
    #print(cntP)
    
    
    plt.plot(frameNums, costPerFrame, color="k") # 点列(x,y)を黒線で繋いだプロット
    plt.show() # プロットを表示

    return costPerFrame

def all_calc():
    all_costPerFrame = []
    vestCost_costPerFrame = [0 for i in range(search_Data.totalFrame)]
    vestTango_costPerFrame = [0 for i in range(search_Data.totalFrame)]
    for target_dataNum in range(len(target_DataBase.AllDataNum)): # ファイル名に数字以外が含まれなければrangeは無くて良い
        target_dataNum = int(target_dataNum)
        print("tango " + str(target_dataNum) + " procces start")
        costPerFrame = calc_tangoCost(target_dataNum)
        all_costPerFrame.append(costPerFrame)
        for frameNum in range(len(vestCost_costPerFrame)):
            if vestCost_costPerFrame[frameNum] < costPerFrame[frameNum]:
                vestCost_costPerFrame[frameNum] = costPerFrame[frameNum]
                vestTango_costPerFrame[frameNum] = target_dataNum
        print("tango " + str(target_dataNum) + " procces ended")
    
    # npを利用して転置
    all_costPerFrame_ = np.array(all_costPerFrame)
    all_costPerFrame = np.array(all_costPerFrame_.T)

    outputFile = open(outputFileName, 'w', newline='')
    writer = csv.writer(outputFile)
    writer.writerows(all_costPerFrame)
    outputFile.close()


    outputFile = open(outputFileName2, 'w', newline='')
    outputFile.writelines(vestTango_costPerFrame)
    outputFile.close()

def outputVest():
    all_costPerFrame = np.loadtxt(outputFileName, delimiter=',')
    all_costPerFrame = np.array(all_costPerFrame.T)

    vestCost_costPerFrame = [0 for i in range(search_Data.totalFrame)]
    vestTango_costPerFrame = [0 for i in range(search_Data.totalFrame)]
    for target_dataNum in range(len(target_DataBase.AllDataNum)): # ファイル名に数字以外が含まれなければrangeは無くて良い
        target_dataNum = int(target_dataNum)
        costPerFrame = all_costPerFrame[target_dataNum]
        for frameNum in range(len(vestCost_costPerFrame)):
            if vestCost_costPerFrame[frameNum] < costPerFrame[frameNum]:
                vestCost_costPerFrame[frameNum] = costPerFrame[frameNum]
                vestTango_costPerFrame[frameNum] = target_dataNum
        print("tango " + str(target_dataNum) + " procces ended")

    np.savetxt(outputFileName2, vestTango_costPerFrame)


def execute():
    
    while True:


        try:
            dataNum = int(input("data number is (0~153):"))
        except:
            break

        try:
            isSide = str(input("r of l:"))
        except:
            break

        try:
            indexNum = int(input("index is (0~41):"))
        except:
            break



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
        #indexNum = 4 # 0~41
        #isSide = 'r' # l or r
        #dataNum = 33

        

        if isSide == 'l':
            velocity_TShandData = search_Data.wristVelAndJointPos_TShandData_L
        elif isSide == 'r':
            velocity_TShandData = search_Data.wristVelAndJointPos_TShandData_R
        for frameNum, velocity_handData in enumerate(velocity_TShandData): # 全時系列データから特定のインデックスのみを時系列順に取り出す
            X.append(velocity_handData[indexNum])
        
        if isSide == 'l':
            velocity_TShandData = target_DataBase.AllwristVelAndJointPos_TShandData_L[dataNum]
        elif isSide == 'r':
            velocity_TShandData = target_DataBase.AllwristVelAndJointPos_TShandData_R[dataNum]
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
        use_spring.FRAME_TH = 10 # 出力パスの最低経由フレーム数
        

        use_spring.mySpring()

        #use_spring.dtw()

        use_spring.plot_path()

        #use_spring.plot_connection()


def test_igo(userDir):
    tango_data_dirPath = userDir + "HandMotion_SimilarSearch/workspace/TimeSeries_HandPositionData/tango/"
    bunsyo_data_filePath = userDir + "HandMotion_SimilarSearch/workspace/TimeSeries_HandPositionData/bunsyo/4.csv" #
    targetNum = 154
    return tango_data_dirPath, bunsyo_data_filePath, targetNum

def test_inu(userDir):
    tango_data_dirPath = userDir + "HandMotion_SimilarSearch/workspace/TimeSeries_HandPositionData/tango/"
    bunsyo_data_filePath = userDir + "HandMotion_SimilarSearch/workspace/TimeSeries_HandPositionData/bunsyo/6.csv" # 父/犬/好き//家/犬/3/世話/(指差し)
    targetNum = 155
    return tango_data_dirPath, bunsyo_data_filePath, targetNum

if __name__ == "__main__":
    time_start = time.perf_counter()
    #userDir = "C:/Users/hisa/Desktop/research/"
    userDir = "C:/Users/root/Desktop/hisa_reserch/"
    #tango_data_dirPath = userDir + "HandMotion_SimilarSearch/workspace/TimeSeries_HandPositionData/tango/"
    #bunsyo_data_dirPath = userDir + "HandMotion_SimilarSearch/workspace/TimeSeries_HandPositionData/bunsyo/"
    outputFileName = userDir + "HandMotion_SimilarSearch/workspace/TimeSeries_HandPositionData/searchResults.csv"
    outputFileName2 = userDir + "HandMotion_SimilarSearch/workspace/TimeSeries_HandPositionData/searchResultsVest.csv"

    target_DataBase = TargetDataBase() # データベース用意
    search_Data = SearchData()

    tango_data_dirPath, bunsyo_data_filePath, targetNum = test_inu(userDir)

    load_targetData(tango_data_dirPath)
    load_searchData(bunsyo_data_filePath)

    time_calc = time.perf_counter()

    #outputVest()
    #all_calc()
    calc_tangoCost(targetNum)
    #execute()

    #plt_originalData()

