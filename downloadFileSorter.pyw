# This version executes main program in background
# and is the preferred way to run the program


import os
import pathlib as p
import time as t
import datetime
from sys import exit
# from plyer import notification
# from typing_extensions import runtime
import logging
logging.basicConfig(filename='app.log', format='%(asctime)s - %(message)s', level=logging.INFO)




active = True
# Checks files while true
runtime = 0
# Number of times main loop has run, 5/sec
tToCheck = 10
# Checks for files at 0
cc = 0
# Number of checks the program has done
sh = False
# When true, the program shutdown the next loop
iC = False
# When false, sort all items regardless of when they
# were created. This flag is kept at false unless
# executed via command from secondary application
sortedLog = []
# List consisting of arrays with three fields
# First nmr is rt
# Second nmr is number of files sorted
# Third is files sorted
# Forth is a bool flag if the sorting was automatic or forced


pa = p.Path.home()
tDir = pa / "Downloads"
# C:\Users\CarlJ\Downloads
suffix = [".zip"]


def checkFold():
    dirC=[]
    for i in suffix:
        if p.Path.is_dir(tDir / i[1:]) is False:
            os.mkdir(i[1:])
            dirC.append(tDir / i[1:])
    for j in dirC:
        logging.info(f"{str(j)} was created")

os.chdir(tDir)




def mainloop():
    nFSorted=0
    filesToSort = [f for f in os.listdir(tDir) if p.Path( tDir / f ).is_file()]
    for fil in filesToSort:
        fP=p.Path(tDir / fil)
        fSuffix = fP.suffix
        if(fSuffix not in suffix):
            suffix.append(fSuffix)
        checkFold()
        fts=fP.stat().st_ctime
        fTS=datetime.datetime.fromtimestamp(fts)
        cT=datetime.datetime.today()
        difT = cT - fTS
        if difT.days>3 or iC:
            os.rename(str(fP),str(tDir / fSuffix[1:] / fP.parts[-1]))
            nFSorted+=1
    if nFSorted>0:
        logging.info(f"{nFSorted} files were sorted.")

# rpyc service definition


def toggle(_input):
    global active


    if isinstance(_input, bool) and active != _input:
        active = _input
        if active:
            return("Download sorter resumed work")
        else:
            return("Download sorter paused")
        return("status: " + str(active))
    elif active == _input:
        return ("Status is already set to " + str(active))
    else:
        return active


import rpyc

class MyService(rpyc.Service):
    def exposed_toggleRun(self,_arg):
        global active, sh, sortedLog


        if _arg == "true" or _arg == "false":
            if _arg == "true":
                return(toggle(True))
            elif _arg == "false":
                return(toggle(False))
        else:
            return (active)
    def exposed_runtime(self):
        global active
        return [runtime, cc]
    def exposed_close(self):
        global sh
        # return("Download sorter process aborted")
        sh = True
    def exposed_getLog(self):
        global sortedLog
        return sortedLog

    def exposed_triggerCheck(self):
        global iC
        iC=True
        return("Check triggered")

    def exposed_initConnect(self):
        logging.debug("Connection established")




print("Starting rpyc")
# start the rpyc server
from rpyc.utils.server import ThreadedServer
from threading import Thread
server = ThreadedServer(MyService, port = 12345)
th = Thread(target = server.start)
th.daemon = True
th.start()
logging.debug("rpyc init")
""" 
def sendNot(_text, _time):
    if not isinstance(_time, (float,int)) and _time < 10:
        _time = 10
    notification.notify(title = "Download Sorter", message = _text, timeout = _time)
 """
logging.debug("Download sorter init")
while True:
    if sh:
        exit()
    runtime+=1
    tToCheck-=1
    if (active and tToCheck<=0) or iC:
        mainloop()
        if iC:
            iC=False
        cc+=1
        tToCheck=100
    # active= not active
    t.sleep(5)


# cd Desktop\Projects\python\downloadFileSorter