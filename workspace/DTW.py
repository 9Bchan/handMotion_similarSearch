class UseSpring():
    def __init__(self):
        self.search_data = None # search data
        self.target_data = None # target data
        self.path = None    
        self.paths = []   
        self.costs = [] 
        self.dataDist = None
        self.dtwDist = None
        self.costMatrix = None
        self.epsilon = None
    
    # 距離計算
    def get_dist(self,x,y):
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

        costM = np.zeros((len_x, len_y))                   # コスト行列(x と y のある2点間の距離を保存
        distM = np.zeros((len_x, len_y, 2), int) # 距離行列(x と y の最短距離を保存)

        costM[0, 0] = self.get_dist(x[0], y[0])

        for i in range(len_x):
            costM[i,0] = costM[i - 1, 0] + self.get_dist(x[i], y[0])
            distM[i, 0] = [i-1, 0]

        for j in range(1, len_y):
            costM[0, j] = costM[0, j - 1] + self.get_dist(x[0], y[j])
            distM[0, j] = [0, j - 1]

        for i in range(1, len_x):
            for j in range(1, len_y):
                pi, pj, m = self.get_min(costM[i - 1, j],
                                    costM[i, j - 1],
                                    costM[i - 1, j - 1],
                                    i, j)
                costM[i, j] = self.get_dist(x[i], y[j]) + m
                distM[i, j] = [pi, pj]

        cost = costM[-1, -1]
        
        path = [[len_x - 1, len_y - 1]]
        i = len_x - 1
        j = len_y - 1

        while ((distM[i, j][0] != 0) or (distM[i, j][1] != 0)):
            path.append(distM[i, j])
            i, j = distM[i, j].astype(int)
        path.append([0,0])

        self.paths.append(np.array(path))
        self.dtwDist = cost
        self.costMatrix = costM

    def partial_dtw(self):
        x = self.search_data
        y = self.target_data
        self.dataDist = np.array(x).reshape(1, -1)**2 + np.array(y).reshape(-1, 1)**2

        len_x = len(x)
        len_y = len(y)

        costM = np.zeros((len_x, len_y))            # コスト行列 各点におけるデータ同士の距離(コスト)を保存
        distM = np.zeros((len_x, len_y, 2), int)    # 合計距離行列 各点におけるパス開始点までの最短合計距離を保存

        costM[0, 0] = self.get_dist(x[0], y[0])
        for i in range(len_x):
            costM[i, 0] = self.get_dist(x[i], y[0])
            distM[i, 0] = [0, 0]

        for j in range(1, len_y):
            costM[0, j] = costM[0, j - 1] + self.get_dist(x[0], y[j])
            distM[0, j] = [0, j - 1]

        for i in range(1, len_x):
            for j in range(1, len_y):
                pi, pj, m = self.get_min(costM[i - 1, j],
                                    costM[i, j - 1],
                                    costM[i - 1, j - 1],
                                    i, j)
                costM[i, j] = self.get_dist(x[i], y[j]) + m
                distM[i, j] = [pi, pj]
        t_end = np.argmin(costM[:,-1])
        cost = costM[t_end, -1]
        
        path = [[t_end, len_y - 1]]
        i = t_end
        j = len_y - 1

        while (distM[i, j][0] != 0 or distM[i, j][1] != 0):
            path.append(distM[i, j])
            i, j = distM[i, j].astype(int)

        self.paths.append(np.array(path))
        self.dtwDist = cost