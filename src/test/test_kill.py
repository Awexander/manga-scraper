import os
import psutil

PROCNAME = "geckodriver" # or chromedriver or IEDriverServer
for proc in psutil.process_iter():
    print(proc)