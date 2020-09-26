# srt = "Knives.Out.2019.DVDScr.XVID.AC3.HQ.Hive-CM8TGx.srt"
import numpy as np
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.editor import VideoFileClip
from datetime import datetime
import pandas as pd
import csv
import re
import os

def is_int(s):
    r = False
    try:
        n = int(s)
        r = True
    except:
        pass
    return r

def clean(s):
    s = s.replace("\n" , " ")
    s = s.replace("<i>" , " ")
    s = s.replace("</i>" , " ")
    s = s.replace("<b>" , " ")
    s = s.replace("</b>" , " ")
    s = re.sub(r'[^\w]', ' ', s)
    return s

def inbox(srt):
    file = open(srt, 'r')
    save = []
    v = file.__next__()
    n = 0
    text = ""
    data = []
    
    while True:
        
        if is_int(v) or n != 0:
            n = int(v)
            
            if n >= 0 and n < 51:
                
                temp = [file.__next__().replace("\n" , " ")]
                s = ""
                v = file.__next__()
                
                while not is_int(v):
                    s += v
                    v = file.__next__()
                    
                temp.append(clean(s))
                save.append(temp)
                    
            else:
                break
                
        else:
            v = file.__next__()
            
    sen = np.array(save)[: , 1]
    num = 0
    for x in range(49):
        temp = list(list(filter(None, sen[x].split(" "))))
        data.append([save[x][0].split("-->")[0] , num] )
        num += len(temp)
        text += " ".join(temp)
        text += " "
        
    return (text , data)


def get_sec(time_str , offset = 0):
    time_str, mil = time_str.split(",")
    # print(time_str, mil)
    """Get Seconds from time."""
    h, m, s = time_str.split(':')
    return float(int(h) * 3600 + int(m) * 60 + int(s)) + float(int(mil)/1000) + offset


def clip(last, movie, cut , audio, offset = 30):

    # ffmpeg_extract_subclip("full.mp4", start_seconds, end_seconds, targetname="cut.mp4")

    end = get_sec(last , offset = offset)

    ffmpeg_extract_subclip(movie, 0, int(end), targetname=cut)
    clip = VideoFileClip(cut)
    clip.audio.write_audiofile(audio)


def json_to_csv(obj , out = "out.csv"):
    
    df = pd.read_json(obj)
    f = csv.writer(open(out, "w"))

    for x in df['words']:
        if x['case'] == 'success':
            # print([x['start'],x['word']])
            f.writerow([x['start'],x['word']])
        else:
            f.writerow([0,x['case']])


def string_to_txt(str , out = "out.txt"):
    file1 = open(out,"w") 
    file1.write(str)
    file1.close


def reject_outliers(data, m=2):
    return data[abs(data - np.mean(data)) < m * np.std(data)]


def check(out, data):
    f = csv.reader(open(out, "r"))
    l = []
    for x in f:
        l.append(x)
        
    li = []
    for x , y in data:
        if l[y][0] != '0':
#             print(get_sec(x) - float(l[y][0])) 
            li.append(get_sec(x) - float(l[y][0]))
            
    li = np.array(li)
    ll = reject_outliers(li, m=2)
    return round(np.mean(ll), 3)
    

def modif(s, delay = 0):
    m , n = s.split("-->")
    m = get_sec(m) + delay
    n = get_sec(n) + delay
    m = get_time(m)
    n = get_time(n)
    
    return " --> ".join([m,n]) + '\n'
    

def get_time(s):
    h = s//3600
    s = s - h*3600
    m = s//60
    s = s-m*60
    ms = s - float(int(s))
    return "{:02d}:{:02d}:{:02d},{:03d}".format(int(h), int(m), int(s), int(round(ms,3)*1000))


def outbox(srt, new = 'new.srt', delay = 0):
    file = open(srt, 'r')
    file2 = open(new, 'w')
    
    v = file.__next__()
    
    while True:
        
        if is_int(v):
            file2.writelines(v)
            file2.writelines(modif(file.__next__() , delay = delay))
            
            v = file.__next__()

            while not is_int(v):
                file2.writelines(v)
                try:
                    v = file.__next__()
                except:
                    file2.close
                    return
                
        else:
            file2.writelines(v)
            v = file.__next__()
            
    file2.close

def cleaning():
    os.system("rm audio.mp3 cut.mkv out.csv out.json out.txt")
    print("done!")