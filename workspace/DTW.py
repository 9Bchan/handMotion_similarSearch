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

