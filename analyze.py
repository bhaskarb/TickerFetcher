import logging
import os 
import re 
import string 

def convertStrToIn(numstr):
    sign = 1;
    num = 0;
    power = -1;
    for c in numstr:
        if c == '(':
            sign = -1
        elif c in string.digits:
            num = num*10 + ord(c) - ord('0')
            if(power > -1):
                power = power + 1;
        elif c == '.':
            power = 0
    return (num*sign)/float(pow(10, power))

def findPrice(fname, data):
    ticker = fname.replace(".html", "").replace("valid/","")
    tid = "yfs_l84_"
    sstart = data.find(tid)
    if sstart == -1:
        return 0
    db = data.find(">", sstart)
    if db == -1:
        return 0
    de = data.find("</span>", db)
    if de == -1:
        return 0
    return convertStrToIn(data[db +1 :de]) 

def analyzeFile(fname):
    with open(fname, 'rb') as dfile:
        data = dfile.read();
        price = findPrice(fname, data)
        teqloc = data.find("Total Stockholder Equity")
        endloc = data.find("/TABLE")
        if teqloc == -1 or endloc == -1:
            return
        numstr = data[teqloc:endloc]
        sstart = numstr.find("<strong>", 0) 
        send = numstr.find("</strong>", sstart)
        equity = True
        sequity, count, eqav, asav = 0, 0, 0, 0
        fs, fa = 0, 0
        while (sstart != -1 and send != -1):
            substr = numstr[sstart+8:send]
            sstart = numstr.find("<strong>", send)
            send = numstr.find("</strong>", sstart)
            if(substr.find("Tangible Assets") == -1):
                m = re.match("[\s]*([0-9,\(\)]*).*", substr)
                nstr = m.group(1)
                numval = convertStrToIn(nstr)
                sequity += numval
                count += 1
                if(fs == 0):
                    fs = numval
                if(not equity and fa == 0):
                    fa = numval
            else:
                equity = False
                if count == 0:
                    eqav = -1
                else:
                    eqav=sequity/count
                sequity = 0
                count = 0
        if count == 0:
            asav = -1
        else :
            asav = sequity/count
        return (fname, eqav, asav, fs, fa, price)

def writeAnalysisHtml(ticklist):
    with open("analysis.html", "wb") as wfile:
        wfile.write("<html><head><title>Analyzed list</title></head><body><table><thead><tr>")
        wfile.write("<td>File name</td>\n")
        wfile.write("<td>Stockholder Equity(av)</td>\n")
        wfile.write("<td>Asset Value(av)</td>\n")
        wfile.write("<td>Current Equity</td>\n")
        wfile.write("<td>Current Asset</td>\n")
        wfile.write("<td>Price</td>\n")
        wfile.write("</tr></thead><tbody>")
        for tick in ticklist:
            ticker = tick[0].replace("valid/", "").replace(".html","")
            wfile.write('<tr>')
            wfile.write('<td><a href="http://finance.yahoo.com/q?s=%s">%s</a></td>' %(ticker, tick[0]))
            wfile.write('<td>%d</td><td>%d</td>' %(tick[1], tick[2]))
            wfile.write('<td>%d</td><td>%d</td><td>%5f</td>' %(tick[3], tick[4], tick[5]))
            wfile.write('</tr>')
        wfile.write("</tbody></table></body>")

def cleanTicklist(ticklist):
    viewlist = []
    for tick in ticklist:
        if(tick[3]>0 and tick[5]> 0 and tick[5] < 5):
            viewlist.append(tick)
    return viewlist 

if __name__ == "__main__":
    dirlist = os.listdir("valid")
#    dirlist = ['AABB.html', 'AACS.html']
    ticklist = []
    for fname in dirlist:
        loc = os.path.join("valid", fname)
        tup = analyzeFile(loc)
        ticklist.append(tup)
    ticklist.sort(key = lambda eq: eq[3], reverse=True)
    viewlist = cleanTicklist(ticklist)
    writeAnalysisHtml(viewlist)

