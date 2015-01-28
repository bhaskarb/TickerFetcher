import urllib2 
import threading
import Queue
import logging
import os 

#This class fetches all the tickers in the queue and gets the balance sheets for the same
class UrlFetcherThread(threading.Thread):
    def __init__(self, inqueue, outqueue):
        self.logger = logging.getLogger("thread_ticker")
        threading.Thread.__init__(self)
        self.inq = inqueue;
        self.outq = outqueue;
        self.logger.debug("Creating Thread %s" %(threading.currentThread().getName()))

    def __loadBalanceSheet(self, ticker):
        fname = ticker + ".html"
        floc = os.path.join("valid", fname)
        if os.path.exists("valid") and os.path.isfile(floc):
            self.logger.debug("Not loading existing ticker %s" %(ticker))
            return
        floc = os.path.join("invalid", fname)
        if os.path.exists("invalid") and os.path.isfile(floc):
            self.logger.debug("Not loading existing ticker %s" %(ticker))
            return
        baseurl = "http://finance.yahoo.com/q/bs?s=" + ticker + "+Balance+Sheet&annual"
        self.logger.debug("Loading ticker %s" %(ticker))
        req = urllib2.Request(baseurl)
        resp = urllib2.urlopen(req)
        data = resp.read()
        self.outq.put((ticker, data))

    def run(self):
        while True:
            name = threading.currentThread().getName()
            ticker = self.inq.get()
            self.logger.debug("-Getting ticker(thread :%s queuesize: %d)" %(name, self.inq.qsize()))
            self.__loadBalanceSheet(ticker)
            self.inq.task_done()
            size = self.inq.qsize()
            self.logger.info("-Done getting ticker %s(thread %s: queuesize: %d)" %(ticker, name, size))
            if(size % 100 == 10):
                print "Crawled %d tickers" %(size)

