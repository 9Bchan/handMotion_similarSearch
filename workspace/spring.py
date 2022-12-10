import glob
import csv
import sys

def load_queryData(queryData_dirPath):
    treat_TShandData = Treat_timeSeriesHandData()

    queryData_filePath_list = glob.glob(queryData_dirPath +"*")
    #print(queryData_filePath_list)
    treat_TShandData.arrangement(queryData_filePath_list[0])


class Treat_timeSeriesHandData():
    def __init__(self):
        self.position_TShandData_L = None
        self.position_TShandData_R = None

    def arrangement(self, handData_filePath):
        with open(handData_filePath, newline='') as f:
            csvreader = csv.reader(f)
            timeSeries_handData = [row for row in csvreader]

            labels = timeSeries_handData[0]
            print(labels)
            
            for frame_TShandData in timeSeries_handData[1:]:
                frame_handData_L = frame_TShandData[:20*2+1] # カット場所の詳細はcsv参照
                frame_handData_R = frame_TShandData[21*2:]
                
                Noneでーた部分削除及びフレーム差から速度データのリストを作成し利用できるようにする
yes


if __name__ == "__main__":
    tango_data_dirPath = "C:/Users/root/Desktop/hisa_reserch/HandMotion_SimilarSearch/TimeSeries_HandData_part/tango/"
    bunsyo_data_dirPath = "C:/Users/root/Desktop/hisa_reserch/HandMotion_SimilarSearch/TimeSeries_HandData_part/tango/"

    load_queryData(tango_data_dirPath)