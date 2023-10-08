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
import my_functions as my


def select_name(keyName_list, tgtName_list):
    # 名前を昇順にする
    keyName_list = sorted(keyName_list, key=lambda x: (len(x), x))
    tgtName_list = sorted(tgtName_list, key=lambda x: (len(x), x))

    # ウィンドウのレイアウトを定義
    layout = [
        [sg.Text("名前を選んでください:")],
        [sg.Text("単語"), sg.Combo(keyName_list, size=(20, 1), key="-KEYNAME-", default_value="")],
        [sg.Text("文章"), sg.Combo(tgtName_list, size=(20, 1), key="-TGTNAME-", default_value="")],
        [sg.Button("選択"), sg.Button("終了")]
    ]

    # ウィンドウの生成
    window = sg.Window("単語と文章の選択", layout)

    # イベントループ
    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED or event == "終了":
            break
        elif event == "選択":
            keyName = values["-KEYNAME-"]
            tgtName = values["-TGTNAME-"]
            break


    # ウィンドウを閉じる
    window.close()




if __name__ == '__main__':
    keyDataDir = "handData/d3_feature/key/"
    tgtDataDir = "handData/d3_feature/tgt/"

    keyDataBase = p_load_handData.get_handDataBase(keyDataDir)
    tgtDataBase = p_load_handData.get_handDataBase(tgtDataDir)

    keyName = select_name(keyDataBase.handDataName_list, tgtDataBase.handDataName_list)