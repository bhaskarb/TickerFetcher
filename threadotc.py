import csv
import threading
import Queue
import logging
import time 
import crawler
import worker 

#This is the url fetcher class which encapsulates the loading and parsing as a bunch of threads
#The User can specify the number of threads he wants to use for the same
class UrlFetcher:
    def __init__(self, num_threads, num_workers):
        self.logger = logging.getLogger("thread_ticker")
        self.inq = Queue.Queue()
        self.outq = Queue.Queue()
        self.fetcher = [];
        self.worker = [];
        self.logger.debug("Starting URL Fetcher with %d threads" %(num_threads))
        for i in range(num_threads):
            t = crawler.UrlFetcherThread(self.inq, self.outq)
            t.setDaemon(True)
            self.fetcher.append(t)
        for i in range(num_workers):
            t = worker.ThreadedWorker(self.outq)
            t.setDaemon(True)
            self.worker.append(t)

    def addtoQueue(self, tlist):
        for t in tlist:
            self.logger.debug("Added ticker to queue %s" %(t))
            self.inq.put(t)
    
    def start(self, tlist):
        for t in self.fetcher:
            t.start()
        for t in self.worker:
            t.start()
        self.addtoQueue(tlist)
        self.inq.join()
        self.logger.debug("Completed in queue")
        self.outq.join()
        self.logger.debug("Completed out queue")

def loadOtcFile(fname):
    filelist = []
    with(open(fname, 'r')) as csvf:
        csvreader = csv.reader(csvf, delimiter=',', quotechar='"')
        for row in csvreader:
            filelist.append(row[0])
    return filelist

if __name__=="__main__":
    logger = logging.getLogger("thread_ticker")
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler("debug.log")
    logger.addHandler(fh)
   
    logger.debug("======================Starting========================")
    flist = loadOtcFile("symbol_info.csv")
    urlfetch = UrlFetcher(5, 5)
    start = time.time()
    urlfetch.start(flist)
    logger.debug("Total runtime is %f sec" %(time.time()- start))
    print "Total runtime is %f sec" %(time.time()- start)
    logger.debug("======================Ending========================")

