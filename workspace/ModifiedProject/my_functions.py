import inspect
import os
import csv

def printline(contents):
    frame = inspect.currentframe().f_back
    frame_name = os.path.basename(frame.f_code.co_filename)
    if len(frame_name) > 10:
        frame_name = frame_name[:10] + "..."
    frame_line = frame.f_lineno
    print("{:<13} : {:<4} : ".format(frame_name[:13], frame_line), end="")
    print(contents)

def printlines(contents):
    frame = inspect.currentframe().f_back
    frame_name = os.path.basename(frame.f_code.co_filename)
    if len(frame_name) > 10:
        frame_name = frame_name[:10] + "..."
    frame_line = frame.f_lineno
    print("{:<13} : {:<4} : ".format(frame_name[:13], frame_line))
    print(contents)

def printlist(contents):
    frame = inspect.currentframe().f_back
    frame_name = os.path.basename(frame.f_code.co_filename)
    if len(frame_name) > 10:
        frame_name = frame_name[:10] + "..."
    frame_line = frame.f_lineno
    print("{:<13} : {:<4} : ".format(frame_name[:13], frame_line))
    for index in contents:
        print(index)

def save_2dData_csv(fileName, dirName, data):
    savefile = dirName + fileName + '.csv'
    f = open(savefile, 'w', newline='')
    writer = csv.writer(f)
    writer.writerows(data)
    f.close()