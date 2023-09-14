import glob
import csv
import os
import my_functions as my
import pandas as pd
import re
from tqdm import tqdm

# pandas ターミナル出力設定
#pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
#pd.set_option("display.width", 300)

def get_syuwaFeature(path):
    jointPosition_perFrame = pd.read_csv(path, header=0, index_col=0, dtype=str)
    print(jointPosition_perFrame)


if __name__ == '__main__':
    get_syuwaFeature("C:/Users/root/Desktop/hisa_reserch/HandMotion_SimilarSearch/workspace/NewProject/joint/key/4.csv")