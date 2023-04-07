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



def execute():
    
    while True:
        use_spring = UseSpring()
        X = []
        Y = []
        indexNum = 1 # 0~41
        isSide = 'r' # l or r
        dataNum = 33

        

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


    def plot_path(self):
        paths = self.paths
        costs = self.costs

        a = self.search_data
        b = self.target_data
        #D = self.dataDist.T # グラフ背景に使用する行列
        D = (self.dataCost.T)

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
            frame_end = self.search_data_usedFrames[path[0][0]]
            print("frame : "+ str(frame_start) +" ~ "+ str(frame_end) + " | cost : " + str(costs[pathNum]))
        print("total detected path : "+ str(totalPathNum))
        print("max cost is : "+ str(maxcost))