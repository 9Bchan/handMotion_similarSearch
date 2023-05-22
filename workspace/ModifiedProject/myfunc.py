import inspect
import os

def printline(contents):
    frame = inspect.currentframe().f_back
    frame_name = os.path.basename(frame.f_code.co_filename)
    if len(frame_name) > 10:
        frame_name = frame_name[:10] + "..."
    frame_line = frame.f_lineno
    print("{:<13} : {:<4} : ".format(frame_name[:13], frame_line), end="")
    print(contents)

def printlist(contents):
    frame = inspect.currentframe().f_back
    frame_name = os.path.basename(frame.f_code.co_filename)
    if len(frame_name) > 10:
        frame_name = frame_name[:10] + "..."
    frame_line = frame.f_lineno
    print("{:<13} : {:<4} : ".format(frame_name[:13], frame_line))
    print(contents)
