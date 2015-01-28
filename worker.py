import threading
import Queue
import logging
import os 

#This class does the processing of the data coming from the URL
class ThreadedWorker(threading.Thread):
    def __init__(self, queue):
        self.logger = logging.getLogger("thread_ticker")
        threading.Thread.__init__(self)
        self.logger.debug("Starting worker thread")
        self.q = queue

    def __dirloc(self, buff):
        if buff.find("Total Stockholder Equity") == -1:
            return "invalid"
        return "valid"

    def __saveFile(self, ticker, buff):
        dataDir = self.__dirloc(buff) 
        fname = ticker + ".html"
        if not os.path.exists(dataDir):
            os.mkdir(dataDir)
        floc = os.path.join(dataDir, fname)

        if os.path.isfile(floc):
            self.logger.debug("Existing file %s/%s" %(dataDir, fname)) 
            return
        with(open(floc, 'wb')) as wfile:
            wfile.write(buff)

        self.logger.debug("Writing file %s/%s" %(dataDir, fname)) 
 
    def run(self):
        while True:
            name = threading.currentThread().getName()
            self.logger.debug("-Fetching data(thread %s queuesize: %d)" %(name, self.q.qsize())) 
            data = self.q.get()
            self.__saveFile(data[0], data[1])
            self.q.task_done()
            self.logger.info("-Done fetching data(thread %s: queuesize: %d)" %(name, self.q.qsize()))
