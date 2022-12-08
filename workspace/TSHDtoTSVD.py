import csv
import numpy as np


def HandDataToVelocityData(TimeSeriesHandDataPath):
    with open(TimeSeriesHandDataPath, newline='') as f:
        csvreader = csv.reader(f)
        TimeSeries_HandData = [row for row in csvreader]

        labels = TimeSeries_HandData[0]
        frameDataLength = len(labels)
        print(len(labels))
        prevFrameData = [None]
        outputData = []

        for frameData in TimeSeries_HandData[1:]:
            if prevFrameData[0] is not None:
                output_low =[]
                for indexNum in range(frameDataLength):
                    label = labels[indexNum]
                    if label == "左" or label == "右":
                        output_low.append("")
                    if label == "wrist_x" or label == "wrist_y":
                        output_low.append(float(frameData[indexNum]) - float(prevFrameData[indexNum]))
                output_low.append("")
                sumOfSquares = output_low[1]*output_low[1] + output_low[2]*output_low[2]
                output_low.append(sumOfSquares)
                sumOfSquares = output_low[4]*output_low[4] + output_low[5]*output_low[5]
                output_low.append(sumOfSquares)
                outputData.append(output_low)
                
                    
            prevFrameData = frameData

        print(outputData)

        outputFile = open("C:/Users/root/Desktop/hisa_reserch/HandMotion_SimilarSearch/TimeSeries_HandData/TimeSeries_WristVelocity.csv", 'w', newline='')
        writer = csv.writer(outputFile)
        writer.writerows(outputData)
        outputFile.close()





if __name__ == "__main__":
    tango_videoPath_dir = "C:/Users/root/Desktop/hisa_reserch/HandMotion_SimilarSearch/TimeSeries_HandData/tango/"
    output_dir = "C:/Users/root/Desktop/hisa_reserch/HandMotion_SimilarSearch/TimeSeries_VelocityData/tango/"

    #MediaPipe周辺設定
   
    all_waveform_handdata = []



    isDraw = True
    isVecsum = True
    isCam = False

    #waveform_handdata("C:/Users/root/Desktop/hisa_reserch/HandMotion_SimilarSearch/edited_video/bunsyo/1.mp4", "1")
    HandDataToVelocityData("C:/Users/root/Desktop/hisa_reserch/HandMotion_SimilarSearch/TimeSeries_HandData/tango/1.csv")

    print("ended")