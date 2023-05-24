import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
import pandas as pd
import numpy as np
import os
# my code
import partial_DTW
import load_handData
import myfunc



def output_result(list_2d, data_X, data_Y):
    xlen = len(data_X)
    ylen = len(data_Y)

    aspectRatio = xlen/ylen # 縦横比

    graphWindowSizeBase = 5
    plt.figure(figsize=(graphWindowSizeBase*aspectRatio, graphWindowSizeBase)) # ウィンドウサイズ

    gs = gridspec.GridSpec(2, 2, width_ratios=[1, 5*aspectRatio], height_ratios=[5, 1]) # グラフの個数，サイズ定義
    ax1 = plt.subplot(gs[0])
    ax2 = plt.subplot(gs[1])
    ax4 = plt.subplot(gs[3])

    # ヒートマップ作成操作
    list_2d = np.transpose(list_2d) # 転置
    sns.heatmap(list_2d, square=False, cmap="Oranges", xticklabels=50, yticklabels=50, cbar=False, ax=ax2)
    ax2.invert_yaxis()  # 上下反転

    ax4.plot(range(xlen), data_X)
    ax4.set_xlabel("$X$")

    ax1.plot(data_Y, range(ylen), c="C1")
    ax1.set_ylabel("$Y$")

    plt.show()


def handElement_calc():
    isManual = True # コンソールからの入力及びループ実行の有効可
    keyDataNum = 0
    tgtDataNum = 0
    indexLabel = '0x_L'
    pathThreshold = 5000
    frameThreshold = 10

    while True:
        if isManual == True:
            try:
                keyDataNum = int(input("key data number is (0~153):"))
                tgtDataNum = int(input("target data number is (0~4):"))
                print("select joint name in >>> ", end="")
                print(load_handData.frameNumAndjointLabel[1:])
                indexLabel = str(input("Please enter :"))
                #pathThreshold = int(input("path threshold is :"))
                #pathThreshold = int(input("frame threshold is :"))
            except:
                input("something is wrong")
                continue

        calc_partialDtw = partial_DTW.Calc_PartialDtw()
        Y = keyDataBase.AllHandData_df[keyDataNum][indexLabel].tolist()
        X = tgtDataBase.AllHandData_df[tgtDataNum][indexLabel].tolist()
        calc_partialDtw.key_data = Y
        calc_partialDtw.tgt_data = X
        calc_partialDtw.PATH_TH = pathThreshold # 出力パスの最大合計スコア
        calc_partialDtw.FRAME_TH = frameThreshold # 出力パスの最低経由フレーム数
        
        calc_partialDtw.spring()

        #myfunc.printline(calc_partialDtw.costMatrix)
        output_result(calc_partialDtw.costMatrix, X, Y)

        if isManual == True and input('Press <f> to continue : ') == 'f' :
            continue
        break

    #partial_DTW.plot_path()

if __name__ == '__main__':
    userDir = "C:/Users/hisa/Desktop/research/"
    #userDir = "C:/Users/root/Desktop/hisa_reserch/"
    keyData_dirPath = userDir + "HandMotion_SimilarSearch/workspace/TimeSeries_HandPositionData/tango/"
    tgtData_dirPath = userDir + "HandMotion_SimilarSearch/workspace/TimeSeries_HandPositionData/bunsyo/"

    keyDataBase = load_handData.HandDataBase() # データベース空箱
    tgtDataBase = load_handData.HandDataBase()

    # すべてのファイルを読み込み
    #load_handData.loadToDataBase(keyData_dirPath, keyDataBase, 'key')
    #load_handData.loadToDataBase(tgtData_dirPath, tgtDataBase, 'target')

    # 指定ファイルのみ読み込み
    keyData_filePath = keyData_dirPath + '0.csv'
    tgtData_filePath = tgtData_dirPath + '4.csv'
    load_handData.loadToDataBase_one(keyData_dirPath, keyDataBase, 'key', keyData_filePath)
    load_handData.loadToDataBase_one(tgtData_dirPath, tgtDataBase, 'target', tgtData_filePath)

    #myfunc.printlist(tgtDataBase.AllHandData_df)
    #myfunc.printlines(tgtDataBase.AllFileNames)

    #myfunc.printline(keyDataBase.AllwristVelAndJointPos_L)
    handElement_calc()

    

