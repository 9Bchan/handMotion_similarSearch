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
import random


# my code
#import partial_match_DTW
import p_load_handData
import p_partial_match_DTW
import p_gui
import my_functions as my


class Search_shuwa():
    def __init__(self):
        self.keyDataBase = None
        self.tgtDataBase = None
        self.cost_TH_dict = {}
        self.weight_dict = {}
        self.frame_TH = 10
        self.feature_label_list = None

        self.keyName = None
        self.tgtName = None
        self.key_len = None
        self.tgt_len = None

    def set_values(self, cost_TH_file, weight_file, keyDataDir, tgtDataDir):
        # コスト閾値
        values_dict = {}
        with open(cost_TH_file, "r") as f:
            for line in f:
                key, value = line.split(":")# 行をコロンで分割してキーと値に分ける
                values_dict[key] = value.strip() # 改行コードを削除するためにstrip()を使う
        self.cost_TH_dict = values_dict
        
        # 重みデータ
        values_dict = {}
        with open(weight_file, "r") as f:
            for line in f:
                key, value = line.split(":")# 行をコロンで分割してキーと値に分ける
                values_dict[key] = value.strip() # 改行コードを削除するためにstrip()を使う
        self.weight_dict = values_dict
        
        # 特徴ラベルリスト
        with open("values/feature_label.txt", "r", encoding="utf-8") as f:
            self.feature_label_list = f.read().split('\n')
        
        self.frame_TH = 10

        my.printline("loading handData..")
        self.keyDataBase = p_load_handData.get_handDataBase(keyDataDir)
        self.tgtDataBase = p_load_handData.get_handDataBase(tgtDataDir)
        my.printline("conpleted")

    def save_dict(self):
        # cost_TH_dict保存
        with open("result/values/cost_TH_dict.txt", "w") as f:
            for key, value in self.cost_TH_dict.items():
                f.write(f"{key}:{value}\n")
        
        with open("result/values/names.txt", "w") as f:
            f.write('key file : ' + str(self.keyName) + '\n')
            f.write('tgt file : ' + str(self.tgtName) + '\n')
    
    def calc_feature(self):
        # gui
        keyName, tgtName = p_gui.select_key_tgt(self.keyDataBase.handDataName_list, self.tgtDataBase.handDataName_list)
        featureName = p_gui.select_feature()

        partial_match_DTW = p_partial_match_DTW.Partial_match_DTW()

        # 指定手話のデータフレームをfloat型で取得
        keyData_df = self.keyDataBase.handData_df_dict[keyName].astype(float)
        tgtData_df = self.tgtDataBase.handData_df_dict[tgtName].astype(float)

        # 指定特徴のデータをリストとして取得
        keyData_feature = keyData_df[featureName].tolist()
        tgtData_feature = tgtData_df[featureName].tolist()

        self.key_len = len(keyData_feature)
        self.tgt_len = len(tgtData_feature)

        #print(keyData_feature)
        print(keyData_feature)

        os.sys.exit()

        partial_match_DTW.set_values(keyData_feature, 
                                    tgtData_feature, 
                                    self.cost_TH_dict[featureName], 
                                    self.frame_TH)

        partial_match_DTW.create_matrix()
        
        path_list, path_Xrange_list = partial_match_DTW.select_path_topThree()
        if path_Xrange_list == []:
            my.printline("path is not founded")
        else:
            #self.print_path(path_Xrange_list)
            self.plt_path(partial_match_DTW.costMatrix, path_list, path_Xrange_list, self.indexLabel, tgt_data, key_data)

    def calc_syuwa(self):
        # gui
        keyName, tgtName = p_gui.select_key_tgt(self.keyDataBase.handDataName_list, self.tgtDataBase.handDataName_list)
        p_gui_progressBar = p_gui.ProgressBar()
        p_gui_progressBar.set_window(len(self.feature_label_list))

        for featureLabel in self.feature_label_list:
            partial_match_DTW = p_partial_match_DTW.Partial_match_DTW()

            # 指定手話のデータフレームをfloat型で取得
            keyData_df = self.keyDataBase.handData_df_dict[keyName].astype(float)
            tgtData_df = self.tgtDataBase.handData_df_dict[tgtName].astype(float)

            # 指定特徴のデータをリストとして取得
            keyData_feature = keyData_df[featureName].tolist()
            tgtData_feature = tgtData_df[featureName].tolist()

            self.key_len = len(keyData_feature)
            self.tgt_len = len(tgtData_feature)

            partial_match_DTW.set_values(keyData_feature, 
                                        tgtData_feature, 
                                        self.cost_TH_dict[featureName], 
                                        self.frame_TH)

            partial_match_DTW.create_matrix()

            #########################
            ########################
            
            path_list, path_Xrange_list = calc_partialDtw.select_path_topThree()

            # gui更新
            p_gui_progressBar.update_window()


        os.sys.exit()

def main():
    keyDataDir = "handData/d3_feature/key/"
    tgtDataDir = "handData/d3_feature/tgt/"

    cost_TH_file = "values/cost_TH_dict.txt"
    weight_file = "values/weight_dict.txt"

    search_shuwa = Search_shuwa()
    search_shuwa.set_values(cost_TH_file, weight_file, keyDataDir, tgtDataDir)
    search_shuwa.calc_syuwa()






if __name__ == '__main__':
    #p_gui.select_feature()

    
    main()