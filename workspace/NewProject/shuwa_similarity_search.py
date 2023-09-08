import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.cm as cm
import seaborn as sns
import pandas as pd
import numpy as np
import os
from tqdm import tqdm
import PySimpleGUI as sg
import shutil
import time


# my code
import partial_match_DTW
import load_handData
import my_functions as my

MAX_DIST = 2



class Similarity_search():
    def __init__(self):
        self.keyDataNum = 0
        self.tgtDataNum = 0
        self.tgt_len = None
        self.key_len = None
        self.indexLabel = 'posFromWrist_1y_R'
        self.feature_labels = None  # 手話の特徴データラベル
        self.feature_labels_L1 = []
        # 中身忘れそうだから辞書型で書いてる
        self.weights_dict = {}
        """
        self.weights_dict = {'0x_L':1, '0y_L':3, '1x_L':1, '1y_L':1, '2x_L':1, '2y_L':1, '3x_L':1, '3y_L':1, '4x_L':1, '4y_L':1, '5x_L':1, '5y_L':1, '6x_L':1, '6y_L':1, '7x_L':1, '7y_L':1, '8x_L':1, '8y_L':1, '9x_L':1, '9y_L':1,
            '10x_L':1, '10y_L':1, '11x_L':1, '11y_L':1, '12x_L':1, '12y_L':1, '13x_L':1, '13y_L':1, '14x_L':1, '14y_L':1, '15x_L':1, '15y_L':1, '16x_L':1, '16y_L':1, '17x_L':1, '17y_L':1, '18x_L':1, '18y_L':1, '19x_L':1, '19y_L':1, '20x_L':1, '20y_L':1,
            '0x_R':1, '0y_R':3, '1x_R':1, '1y_R':1, '2x_R':1, '2y_R':1, '3x_R':1, '3y_R':1, '4x_R':1, '4y_R':1, '5x_R':1, '5y_R':1, '6x_R':1, '6y_R':1, '7x_R':1, '7y_R':1, '8x_R':1, '8y_R':1, '9x_R':1, '9y_R':1,
            '10x_R':1, '10y_R':1, '11x_R':1, '11y_R':1, '12x_R':1, '12y_R':1, '13x_R':1, '13y_R':1, '14x_R':1, '14y_R':1, '15x_R':1, '15y_R':1, '16x_R':1, '16y_R':1, '17x_R':1, '17y_R':1, '18x_R':1, '18y_R':1, '19x_R':1, '19y_R':1, '20x_R':1, '20y_R':1}
        """
        self.costThreshold = 10
        self.frameThreshold = 0
        self.all_path_Xrange_list = []
        self.scoreData_plt = None
        self.path_plt_list = []
        self.all_path_Xrange_list = []

    def set_values(self):
        try:
            self.keyDataNum = int(input("key data number is (0~153):"))
            self.tgtDataNum = int(input("target data number is (0~4):"))
            print("select joint name in >>> ", end="")
            print(self.feature_labels[1:])
            indexLabel = str(input("Please enter :"))
            #costThreshold = int(input("path threshold is :"))
            #costThreshold = int(input("frame threshold is :"))
        except:
            input("something is wrong")
            

    #　一つの手の情報要素についてパスを計算，結果を表示
    def calcPath_handFeatures(self):
        self.key_len = len(keyDataBase.AllHandData_df[self.keyDataNum][self.feature_labels[1]].tolist())
        self.tgt_len = len(tgtDataBase.AllHandData_df[self.tgtDataNum][self.feature_labels[1]].tolist())

        calc_partialDtw = partial_match_DTW.Calc_PartialDtw()
        key_data = keyDataBase.AllHandData_df[self.keyDataNum][self.indexLabel].tolist()
        tgt_data = tgtDataBase.AllHandData_df[self.tgtDataNum][self.indexLabel].tolist()
        calc_partialDtw.key_data = key_data
        calc_partialDtw.tgt_data = tgt_data
        calc_partialDtw.COST_TH = self.costThreshold # 出力パスの最大合計スコア
        calc_partialDtw.FRAME_TH = self.frameThreshold # 出力パスの最低経由フレーム数
        
        calc_partialDtw.create_matrix()
        
        path_list, path_Xrange_list = calc_partialDtw.select_path_topThree()
        if path_Xrange_list == []:
            my.printline("path is not founded")
        else:
            #self.print_path(path_Xrange_list)
            self.plt_path(calc_partialDtw.costMatrix, path_list, path_Xrange_list, self.indexLabel, tgt_data, key_data)

    #　全ての手の情報要素についてパスを計算，all_path_Xrange_list に結果を保存
    def calcPath_allHandFeatures(self):
        self.key_len = len(keyDataBase.AllHandData_df[self.keyDataNum][self.feature_labels[1]].tolist())
        self.tgt_len = len(tgtDataBase.AllHandData_df[self.tgtDataNum][self.feature_labels[1]].tolist())


        for indexLabel in tqdm(self.feature_labels[1:], bar_format="{l_bar}{bar:10}{r_bar}{bar:-10b}", colour='green'):
        #for indexLabel in labels[1:]:
            calc_partialDtw = partial_match_DTW.Calc_PartialDtw()
            key_data = keyDataBase.AllHandData_df[self.keyDataNum][indexLabel].tolist()
            tgt_data = tgtDataBase.AllHandData_df[self.tgtDataNum][indexLabel].tolist()
            calc_partialDtw.key_data = key_data
            calc_partialDtw.tgt_data = tgt_data
            calc_partialDtw.COST_TH = self.costThreshold # 出力パスの最大合計スコア
            calc_partialDtw.FRAME_TH = self.frameThreshold # 出力パスの最低経由フレーム数
        
            calc_partialDtw.create_matrix()

            path_list, path_Xrange_list = calc_partialDtw.select_path_topThree()
            #my.printline(path_Xrange_list)
            
            self.plt_path(calc_partialDtw.costMatrix, path_list, path_Xrange_list, indexLabel, tgt_data, key_data)
            
            # 保存
            if isSave_path_plt:
                my.save_2dData_csv(indexLabel, output_dir + 'path/', path_Xrange_list)

            self.all_path_Xrange_list.append(path_Xrange_list)

    #　全ての手の情報要素についてパスを計算，（関節情報一つをマンハッタン距離で計算）
    def calcPath_allHandFeatures_L1norm(self):
        self.key_len = len(keyDataBase.AllHandData_df[self.keyDataNum][self.feature_labels[1]].tolist())
        self.tgt_len = len(tgtDataBase.AllHandData_df[self.tgtDataNum][self.feature_labels[1]].tolist())

        # 特徴ごとにラベルをまとめたリスト作成
        posFromWrist_label = [item for item in self.feature_labels[1:] if "posFromWrist" in item]
        posFromBody_label = [item for item in self.feature_labels[1:] if "posFromBody" in item]
        vel_label = [item for item in self.feature_labels[1:] if "vel" in item]

        for x_label, y_label in tqdm(zip(posFromWrist_label[::2], posFromWrist_label[1::2]), total=len(posFromWrist_label)//2, bar_format="{l_bar}{bar:10}{r_bar}{bar:-10b}", colour='green'):
            calc_partialDtw = partial_match_DTW.Calc_PartialDtw()
            
            key_x = keyDataBase.AllHandData_df[self.keyDataNum][x_label].tolist()
            key_y = keyDataBase.AllHandData_df[self.keyDataNum][y_label].tolist()

            tgt_x = tgtDataBase.AllHandData_df[self.tgtDataNum][x_label].tolist()
            tgt_y = tgtDataBase.AllHandData_df[self.tgtDataNum][y_label].tolist()

            key_L1norm = [abs(x - y) for (x, y) in zip(key_x, key_y)]
            tgt_L1norm = [abs(x - y) for (x, y) in zip(tgt_x, tgt_y)]

            calc_partialDtw.key_data = key_L1norm
            calc_partialDtw.tgt_data = tgt_L1norm
            calc_partialDtw.COST_TH = self.costThreshold # 出力パスの最大合計スコア
            calc_partialDtw.FRAME_TH = self.frameThreshold # 出力パスの最低経由フレーム数
        
            calc_partialDtw.create_matrix()

            path_list, path_Xrange_list = calc_partialDtw.select_path_topThree()
            #my.printline(path_Xrange_list)
            
            fileName = x_label + '+' + y_label
            self.feature_labels_L1.append(fileName)
            self.plt_path(calc_partialDtw.costMatrix, path_list, path_Xrange_list, fileName, tgt_L1norm, key_L1norm)
            
            # 保存
            if isSave_path_plt:
                my.save_2dData_csv(fileName, output_dir + 'path/', path_Xrange_list)

            self.all_path_Xrange_list.append(path_Xrange_list)
        
        for indexLabel in tqdm(posFromBody_label, bar_format="{l_bar}{bar:10}{r_bar}{bar:-10b}", colour='green'):
        #for indexLabel in labels[1:]:
            calc_partialDtw = partial_match_DTW.Calc_PartialDtw()
            key_data = keyDataBase.AllHandData_df[self.keyDataNum][indexLabel].tolist()
            tgt_data = tgtDataBase.AllHandData_df[self.tgtDataNum][indexLabel].tolist()
            calc_partialDtw.key_data = key_data
            calc_partialDtw.tgt_data = tgt_data
            calc_partialDtw.COST_TH = self.costThreshold # 出力パスの最大合計スコア
            calc_partialDtw.FRAME_TH = self.frameThreshold # 出力パスの最低経由フレーム数
        
            calc_partialDtw.create_matrix()

            path_list, path_Xrange_list = calc_partialDtw.select_path_topThree()
            #my.printline(path_Xrange_list)
            
            self.feature_labels_L1.append(indexLabel)
            self.plt_path(calc_partialDtw.costMatrix, path_list, path_Xrange_list, indexLabel, tgt_data, key_data)
            
            # 保存
            if isSave_path_plt:
                my.save_2dData_csv(indexLabel, output_dir + 'path/', path_Xrange_list)

            self.all_path_Xrange_list.append(path_Xrange_list)

        for indexLabel in tqdm(vel_label, bar_format="{l_bar}{bar:10}{r_bar}{bar:-10b}", colour='green'):
        #for indexLabel in labels[1:]:
            calc_partialDtw = partial_match_DTW.Calc_PartialDtw()
            key_data = keyDataBase.AllHandData_df[self.keyDataNum][indexLabel].tolist()
            tgt_data = tgtDataBase.AllHandData_df[self.tgtDataNum][indexLabel].tolist()
            calc_partialDtw.key_data = key_data
            calc_partialDtw.tgt_data = tgt_data
            calc_partialDtw.COST_TH = self.costThreshold # 出力パスの最大合計スコア
            calc_partialDtw.FRAME_TH = self.frameThreshold # 出力パスの最低経由フレーム数
        
            calc_partialDtw.create_matrix()

            path_list, path_Xrange_list = calc_partialDtw.select_path_topThree()
            #my.printline(path_Xrange_list)
            
            self.feature_labels_L1.append(indexLabel)
            self.plt_path(calc_partialDtw.costMatrix, path_list, path_Xrange_list, indexLabel, tgt_data, key_data)
            
            # 保存
            if isSave_path_plt:
                my.save_2dData_csv(indexLabel, output_dir + 'path/', path_Xrange_list)

            self.all_path_Xrange_list.append(path_Xrange_list)



    
    # パスをグラフに描画して表示
    def plt_path(self, list_2d, path_list, path_Xrange_list, label, tgt_data, key_data):

        aspectRatio = self.tgt_len/self.key_len # 縦横比

        graphWindowSizeBase = 5
        plt.figure(figsize=(graphWindowSizeBase*aspectRatio, graphWindowSizeBase)) # ウィンドウサイズ

        gs = gridspec.GridSpec(2, 2, width_ratios=[1, 5*aspectRatio], height_ratios=[5, 1]) # グラフの個数，サイズ定義
        ax1 = plt.subplot(gs[0])
        ax2 = plt.subplot(gs[1])
        ax4 = plt.subplot(gs[3])

        # ヒートマップ作成操作
        list_2d = np.transpose(list_2d) # 転置
        sns.heatmap(list_2d, square=False, cmap='Greys', xticklabels=50, yticklabels=50, cbar=False, ax=ax2)
        ax2.invert_yaxis()  # 上下反転

        # ヒートマップにパスを描画
        if not path_list == []:
            for i, path in enumerate(path_list):
                cost = path_Xrange_list[i][2]
                color = cm.Reds(1-cost) # コストの値に応じて色変更
                path_np = np.array(path)
                ax2.plot(path_np[:,0], path_np[:,1], c=color)

        
        if isPlt_similar_section:
            self.plt_similar_section(ax2, similar_section_file)

        ax4.plot(tgt_data)
        ax4.set_xlabel("$X$")

        ax1.plot(key_data, range(len(key_data)), c="C1")
        ax1.set_ylabel("$Y$")
        
        # 保存，出力の選択
        if isSave_path_plt:
            plt.savefig(output_dir + 'path/' + label + '.png')
        if isShow_path_plt:
            plt.show()

        plt.clf()
        plt.close()

    # 設定した類似区間に矢印を描画
    def plt_similar_section(self, ax, sections_file):
        with open(sections_file) as f:
            section_list = []
            for line in f.readlines():
                head, end = line.split(',')
                head =int(head)
                end = int(end)
                '''
                section_list.append([int(head),int(end)])
                similar_sect_path = []
                for j in range(int(head), int(end)+1):
                    similar_sect_path.append([0,j])
                similar_sect_path_np = np.array(similar_sect_path)
                ax.plot(similar_sect_path_np[:,1], similar_sect_path_np[:,0], c="b")
                '''
                arrow_props = dict(arrowstyle="->", mutation_scale=10, color="blue", linewidth=1)
                ax.annotate("", xy=[head, 0], xytext=[end-5, 0], arrowprops=arrow_props)
                ax.annotate("", xy=[end, 0], xytext=[head+5, 0], arrowprops=arrow_props)



    
    def plt_scoreData(self):
        totalNum_frame_tgt = tgtDataBase.originallyTotalFrame_list[self.tgtDataNum]

        # all_path_Xrange_listを展開，関節要素についてパスとスコアの情報を取得，時系列スコアデータを行列計算
        scoreM = np.zeros((totalNum_frame_tgt, len(self.all_path_Xrange_list)), float)

        for j, path_Xrange_list in enumerate(self.all_path_Xrange_list):
            #label = self.feature_labels[1+j]
            label = self.feature_labels_L1[j]
            weight = self.weights_dict[label]
            for path_Xrange in path_Xrange_list:
                
                path_head = (tgtDataBase.AllHandData_df[self.tgtDataNum]['frame'][path_Xrange[0] + 1])
                path_end = (tgtDataBase.AllHandData_df[self.tgtDataNum]['frame'][path_Xrange[1] + 1])
                path_cost = path_Xrange[2]

                #maxPathScore = (len_Y + ((path_end - path_head))) * MAX_DIST
                #maxPathScore =  (len_Y + (len_Y * 1.5)) * MAX_DIST

                path_score = (self.costThreshold - path_cost)*weight # スコアに変換（スコア : 値が大きいほど類似度高い）
                for i in range(path_head, (path_end)): # path_head ~ path_end の値をiに代入
                    if scoreM[i][j] == 0: # スコアが入ってなければスコアを代入
                        scoreM[i][j] = path_score
                    elif scoreM[i][j] < path_score: # すでにスコアが入っているなら比較して代入
                        scoreM[i][j] = path_score
        


        frame_nums = list(range(0, totalNum_frame_tgt))
        frame_score = np.sum(scoreM, axis=1)
        plt.plot(frame_nums, frame_score, c="r") # 点列(x,y)を黒線で繋いだプロット
        #print(np.sum(scoreM, axis=1))

        if isPlt_similar_section:
            self.plt_similar_section(plt, similar_section_file)

        # 保存，出力の選択
        if isSave_scoreData_plt:
            plt.savefig(output_dir + 'scoreData.png')
        if isShow_scoreData_plt:
            plt.show()

        plt.clf()
        plt.close()

    # コンソールにパスをプリント
    def print_path(self, path_Xrange_list):
        for path_Xrange in path_Xrange_list:
            #my.printline(path_Xrange[0])
            #my.printline(tgtDataBase.AllHandData_df[keyDataNum]['frame'])
            path_head = tgtDataBase.AllHandData_df[self.tgtDataNum]['frame'][path_Xrange[0] + 1]
            path_end = tgtDataBase.AllHandData_df[self.tgtDataNum]['frame'][path_Xrange[1] + 1]
            path_cost = path_Xrange[2]
            #my.printline("range -> {} ~ {} | cost -> {} ".format(path_Xrange[0], path_Xrange[1], path_cost)) # グラフ中のパスの範囲
            my.printline("range -> {} ~ {} | cost -> {} ".format(path_head, path_end, path_cost))  # グラフ中のパスの範囲に対応する，元のデータでのフレーム範囲

def select_file_gui():
    '''
    ファイルを選択して読み込む
    '''
    # GUIのレイアウト
    layout = [
        [
            sg.Text("単語データ"),
            sg.InputText(),
            sg.FileBrowse(key="keyData_file")
        ],
        [
            sg.Text("文章データ"),
            sg.InputText(),
            sg.FileBrowse(key="tgtData_file")
        ],
        [sg.Submit(key="submit"), sg.Cancel("Exit")]
    ]
    # WINDOWの生成
    window = sg.Window("ファイル選択", layout)

    # イベントループ
    while True:
        event, values = window.read(timeout=100)
        if event == 'Exit' or event == sg.WIN_CLOSED:
            os.sys.exit()
        elif event == 'submit':
            if values['keyData_file'] == "":
                keyData_filePath = "handData/key/154_part33.csv"
            else:
                keyData_filePath = values['keyData_file']
            if values['tgtData_file'] == "":
                tgtData_filePath = "handData/target/4.csv"
            else:
                tgtData_filePath = values['tgtData_file']
            break
    window.close()
    
    return keyData_filePath, tgtData_filePath


# リザルト保存情報
isSave_path_plt = True
isSave_scoreData_plt = True
isSave_params = True

isShow_path_plt = False
isShow_scoreData_plt = True

isPlt_similar_section = True

output_dir = 'result/'
similar_section_file = 'similar_sections/tgt4_key33.txt'
weight_file = "params/weights.txt"


if __name__ == '__main__':
    # データベース空箱
    keyDataBase = load_handData.HandDataBase() 
    tgtDataBase = load_handData.HandDataBase()

    """
    # 検索キーと検索対象の位置データ読み込み（key:target=多:1）
    keyData_dirPath = "handData/key"
    tgtData_dirPath = "handData/target"
    load_handData.loadToDataBase(keyData_dirPath, keyDataBase, 'key')
    load_handData.loadToDataBase(tgtData_dirPath, tgtDataBase, 'target')
    """

    #"""
    # 検索キーと検索対象の位置データ読み込み（key:target=1:1）
    keyData_filePath, tgtData_filePath = select_file_gui()
    load_handData.loadToDataBase_one(keyDataBase, 'key', keyData_filePath)
    load_handData.loadToDataBase_one(tgtDataBase, 'target', tgtData_filePath)
    #"""

    # 類似検索実行クラス
    similarity_search = Similarity_search()

    # 設定したパラメータの読み込み -----------------------------------------------------------------------
    similarity_search.costThreshold = 1
    similarity_search.frameThreshold = 10
    with open("params/feature_labels.txt", "r", encoding="utf-8") as f:
        similarity_search.feature_labels = f.read().split('\n')
    with open(weight_file) as f:
        for line in f.readlines():
            key, val = line.split(',')
            similarity_search.weights_dict[key] = float(val)
    
    # -------------------------------------------------------------------------------------------------

    # 使用したパラメータをresultに保存
    shutil.copyfile(weight_file, "result/params/weights.txt")
    with open('result/params/threshold.txt', 'w') as f:
        f.write('path cost : ' + str(similarity_search.costThreshold) + '\n')
        f.write('frame range : ' + str(similarity_search.frameThreshold) + '\n')
    with open('result/params/files.txt', 'w') as f:
        f.write('key file : ' + str(keyData_filePath) + '\n')
        f.write('target file : ' + str(tgtData_filePath) + '\n')
    
    #similarity_search.calc_handElementPath()
    similarity_search.calcPath_allHandFeatures()
    #similarity_search.calcPath_allHandFeatures_L1norm()
    similarity_search.plt_scoreData()
    
    # 全てのkeyについて検索する関数は未作成


