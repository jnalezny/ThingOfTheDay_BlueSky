
import logging
import time

import urllib
import datetime
import json
import sys

from apitest import send_post

def parseArgs(argv):
    if len(argv) > 1:
        tmode = False
        if "test" in argv:
            tmode = True
        sFile = argv[1]
        if len(argv) > 2:
            dFile = argv[2]
        else:
            dFile = "country_daily.json"
        return tmode,sFile,dFile
    else:
        return False,"country_secrets.txt","country_daily.json"

trailer = None

def getTodaysData(dFilename,test):
    with open(dFilename) as f:
        DAILYDATA = json.load(f)
        
        d = datetime.date.today()
        d_str = str(d.month) + "/" + str(d.day)
        global trailer
        trailer = DAILYDATA.get("trailer",None)
        
        try:
            todaysData = list(filter(lambda d:(d['date'] == d_str),DAILYDATA["days"]))
        except:
            print("dates threw an exception " +d_str )
        if test:
            for row in DAILYDATA:
                imagefilename = row["image"]
                x = row["text"]
                y = row["date"]
                if imagefilename != "none":
                    with open(imagefilename) as testFile:
                        testFile.close()               
                
        return todaysData


TestMode,SecretFilename,DailyFilename = parseArgs(sys.argv)

todaysData=getTodaysData(DailyFilename,TestMode)

with open(SecretFilename) as f:
    DATA = json.load(f)
    
handle = DATA["handle"]
password = DATA["password"]
base_image_dir = DATA["base_image_dir"]
n = datetime.datetime.now()
print("handle " + handle + " " + str(n))
#print("password " + password)


if len(todaysData):

    for row in todaysData:
        print(row['text'])
        print(row['image'])
        try:
            with open(base_image_dir + '/' + row['image']) as testFile:
                testFile.close()
        except(FileNotFoundError,IOError):
            row['image'] = 'none'
            
        myMsg = row['text']
        if trailer:
            myMsg = myMsg + " " + trailer
        if row.get('year') and len(myMsg) < 280 - 20:
            d = datetime.date.today()
            myMsg += " " + str(d.year - row.get('year')) + " years ago"
        if row.get('alternate'):
            alternate = row.get('alternate')
        else:
            alternate = row['image']
        if not TestMode:
            if row['image'].strip() != 'none':
                send_post(myMsg, base_image_dir + '/' +row['image'], alternate, handle, password)
            else:
                send_post(myMsg, None, None, handle, password)
        
        print("update sent")
        time.sleep(120)
  






