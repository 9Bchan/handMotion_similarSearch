import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os
# my code
import partial_DTW
import load_handData
import myfunc

def output_result(list_2d):
    list_2d = list_2d.T
    sns.heatmap(list_2d)
    plt.show()


def handElement_calc():
    isManual = True
    keydataNum = 0
    tgtdataNum = 0
    isSide = "r"
    indexNum = 1
    pathThreshold = 5000
    frameThreshold = 10

    if isManual == False:
        while True:
            try:
                tgtdataNum = int(input("target data number is (0~4):"))
                keydataNum = int(input("key data number is (0~153):"))
                isSide = str(input("r of l:"))
                indexNum = int(input("index is (0~41):"))
                #pathThreshold = int(input("path threshold is :"))
                #pathThreshold = int(input("frame threshold is :"))
            except:
                input("something is wrong")
                break
                
    X = []
    Y = []
    if isSide == 'l':
        wristVelAndJointPos = tgtDataBase.AllwristVelAndJointPos_L[tgtdataNum]
    elif isSide == 'r':
        wristVelAndJointPos = tgtDataBase.AllwristVelAndJointPos_R[tgtdataNum]
    for frameNum, velocity_handData in enumerate(wristVelAndJointPos): # 全時系列データから特定のインデックスのみを時系列順に取り出す
        X.append(velocity_handData[indexNum])
    
    if isSide == 'l':
        wristVelAndJointPos = keyDataBase.AllwristVelAndJointPos_L[keydataNum]
    elif isSide == 'r':
        wristVelAndJointPos = keyDataBase.AllwristVelAndJointPos_R[keydataNum]
    for frameNum, velocity_handData in enumerate(wristVelAndJointPos):
        Y.append(velocity_handData[indexNum])

    myfunc.printline(Y)
    os.sys.exit()

    

    calc_partialDtw = partial_DTW.Calc_PartialDtw()

    calc_partialDtw.key_data = Y
    calc_partialDtw.tgt_data = X
    calc_partialDtw.PATH_TH = pathThreshold # 出力パスの最大合計スコア
    calc_partialDtw.FRAME_TH = frameThreshold # 出力パスの最低経由フレーム数
    
    calc_partialDtw.spring()

    #myfunc.printline(calc_partialDtw.costMatrix)
    output_result(calc_partialDtw.costMatrix)
    #myfunc.printline("as")

    #partial_DTW.plot_path()

if __name__ == '__main__':
    #userDir = "C:/Users/hisa/Desktop/research/"
    userDir = "C:/Users/root/Desktop/hisa_reserch/"
    keyData_dirPath = userDir + "HandMotion_SimilarSearch/workspace/TimeSeries_HandPositionData/tango/"
    tgtData_dirPath = userDir + "HandMotion_SimilarSearch/workspace/TimeSeries_HandPositionData/bunsyo/"

    #tgt_data = 
    #key_data = 

    keyDataBase = load_handData.HandDataBase() # データベース空箱
    tgtDataBase = load_handData.HandDataBase()
    load_handData.load_keyAndTgtData(keyData_dirPath, tgtData_dirPath, keyDataBase, tgtDataBase) # 指定パス内のファイルから値を読み込みデータベースに格納
    

    #myfunc.printline(keyDataBase.AllwristVelAndJointPos_L)
    handElement_calc()

    

