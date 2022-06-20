from dataproc import DataProcessing
import time

dataProc = DataProcessing()
while True:
    tic = time.time()
    dataProc.refresh()
    toc = tic - time.time()
    time.sleep(600-toc)
