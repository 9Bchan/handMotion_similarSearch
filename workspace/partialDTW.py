import numpy as np


key_data = None # key data
key_data_usedFrames = None # key data
tgt_data = None # tgt data 

paths = []   
costs = [] 
dataDist = None
dtwDist = None
costMatrix = None
PATH_TH = None
FRAME_TH = None
dataCost = None

pathsAndCostData = [] # [パス開始フレーム, パス終了フレーム, コスト]*パス数 のデータセットを保存

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


def spring(tgt_data, key_data):
    x = tgt_data # 検索される対象
    y = key_data # 検索キー
    #dataDist = np.array(x).reshape(1, -1)**2 + np.array(y).reshape(-1, 1)**2
    dataDist = np.sqrt((np.array(x).reshape(1, -1) - np.array(y).reshape(-1, 1))**2)

    len_x = len(x)
    len_y = len(y)

    costM = np.zeros((len_x, len_y))            # 合計距離行列 各点におけるパス開始点までの最短合計コストを保存
    pathM = np.zeros((len_x, len_y, 2), int)    # パス連結行列 各点において，その点を通るパスのひとつ前の点(連結関係)を保存
    headM = np.zeros((len_x, len_y), int)       # パス開始点行列 各点において，その点を通るパスの開始点を保存

    # 0行0列 (原点)
    costM[0, 0] = get_dist(x[0], y[0])

    
    # 0列目
    for j in range(1, len_x):
        costM[0, j] = get_dist(x[0], y[j])
        pathM[0, j] = [0, -1] # パスの先頭（DTW行列の0行目）
        headM[0, j] = headM[0, j - 1]

    # 0行目
    for i in range(1, len_y):
        costM[0, j] = costM[0, j - 1] + get_dist(x[0], y[j])
        pathM[0, j] = [0, -1] # パスの先頭（DTW行列の0行目）
        headM[0, j] = headM[0, j - 1]

    # i列
    for j in range(1, len_x):
        # i列1行
        costM[i, 0] = get_dist(x[i], y[0])
        pathM[i, 0] = [0, 0]
        headM[i, 0] = i


        # i列目走査
        for i in range(1, len_y):
            pi, pj, m = get_min(costM[i - 1, j],
                                costM[i, j - 1],
                                costM[i - 1, j - 1],
                                i, j)
            costM[i, j] = get_dist(x[i], y[j]) + m
            pathM[i, j] = [pi, pj]
            headM[i, j] = headM[pi,pj]

        imin = np.argmin(costM[:(i+1), -1])
        #print(imin)

        dmin = costM[imin, -1]

        if dmin > PATH_TH: # 累算コストしきい値より小さい場合のみ　以降のパス出力コードを実行
            continue

        for j in range(1, len_y):
            if (costM[i,j] < dmin) and (headM[i, j] < imin):
                break
        else: # 直前のfor内でbreakが使用されなかった場合とforが実行されなかった場合処理される
            path = [[imin, len_y - 1]]
            temp_i = imin
            temp_j = len_y - 1

            while (pathM[temp_i, temp_j][0] != 0 or pathM[temp_i, temp_j][1] != 0):
                path.append(pathM[temp_i, temp_j])
                temp_i, temp_j = pathM[temp_i, temp_j].astype(int)
            
            #costM[headM <= imin] = 10000000
            #for ci in range(imin):
            #    costM[ci, -1] = 10000000
            #costM[headM <= imin] = 10000000

            
            original_path = np.array(path)

            path_head = original_path[0]
            #print(len(original_path))
            #print(len_y - 1)

            path_tail = original_path[len(original_path) - 1]
            #path_tail = original_path[len_y - 1]
            #print(len_y)

            #print((path_head[0] - path_tail[0]))

            #if int((path_head[0] - path_tail[0])) > FRAME_TH: # パスが指定フレーム数をまたがないときは出力しない
            paths.append(np.array(path))
            costs.append(dmin)
    dataCost = costM