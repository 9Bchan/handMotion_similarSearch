import glob
import csv
import sys

def load_queryData(queryData_dirPath):
    treat_TShandData = Treat_timeSeriesHandData()

    queryData_filePath_list = glob.glob(queryData_dirPath +"*")
    #print(queryData_filePath_list)

    if queryData_filePath_list is not None:
        treat_TShandData.arrangement(queryData_filePath_list[0])

    treat_TShandData.calc_frameDifference()


class Treat_timeSeriesHandData():
    def __init__(self):
        self.totalFrame= None # 総フレーム数
        self.totalIndex = None # 単位フレームにおけるデータの要素数
        self.position_TShandData_L = [] # 位置データ推移
        self.position_TShandData_R = []
        self.velocity_TShandData_L = [] # 速度データ推移
        self.velocity_TShandData_R = []

    def arrangement(self, handData_filePath):
        with open(handData_filePath, newline='') as f:
            csvreader = csv.reader(f)
            timeSeries_handData = [row for row in csvreader] # 一行目:ラベル 二行目以降:フレーム毎の左右のハンドデータ

            labels = timeSeries_handData[0] 
            for frame_TShandData in timeSeries_handData[1:]:
                frame_handData_L = frame_TShandData[:20*2+1] # 単位フレームにおけるハンドデータを左右に分割
                frame_handData_R = frame_TShandData[21*2:]
                
                if frame_handData_L[0] is not None and frame_handData_L[0] is not None: #そのフレームにおいて両手が検出されていればリストに追加
                    frame_handData_L_float = [float(i) for i in frame_handData_L] # 要素をstrからfloatに変換
                    frame_handData_R_float = [float(i) for i in frame_handData_R]
                    self.position_TShandData_L.append(frame_handData_L_float)
                    self.position_TShandData_R.append(frame_handData_R_float)
            
            self.totalFrame = len(self.position_TShandData_L)
            self.totalIndex = len(self.position_TShandData_L[0])
                
    
    def calc_frameDifference(self): # フレームの差をとりデータのフレーム速度推移を求める
        
        for frame_num in range(self.totalFrame): # 左右のpositionリストの大きさは同じ フレーム数分ループ
            if not frame_num == 0: # 最初のフレームのみ除外
                for index_num in range(self.totalIndex): # 単位フレームのデータ要素数分ループ
                    self.velocity_TShandData_L.append(self.position_TShandData_L[frame_num][index_num] - self.position_TShandData_L[frame_num][index_num - 1])
                    self.velocity_TShandData_R.append(self.position_TShandData_R[frame_num][index_num] - self.position_TShandData_R[frame_num][index_num - 1])
        
        print(self.velocity_TShandData_L)


全単語のでーたをとうろく、すぷりんぐのじっこう

    


if __name__ == "__main__":
    userDir = "C:/Users/hisa/Desktop/research/"
    # "C:/Users/root/Desktop/hisa_reserch/"
    tango_data_dirPath = userDir + "HandMotion_SimilarSearch/TimeSeries_HandData_part/tango/"
    bunsyo_data_dirPath = userDir + "HandMotion_SimilarSearch/TimeSeries_HandData_part/tango/"

    load_queryData(tango_data_dirPath)