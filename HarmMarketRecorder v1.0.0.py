import os
import requests
import json
from numba import jit
from datetime import datetime
from time import time
import pandas

headers = {
    'User-Agent'      : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36', 
    'Accept'          : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 
    'Accept-Language' : 'en-US,en;q=0.5',
    'DNT'             : '1',
    'Connection'      : 'close'
}

@jit
def worldmarkettickerlist(MarketName): #input(MarketName) output(StockReutersCodeList, StockSymbolCodeList)
    RequestURL = ("https://api.stock.naver.com/stock/exchange/%s/marketValue?page=1&pageSize=1"
                  %MarketName)
    XHRpage = requests.get(RequestURL, headers=headers, timeout=5)
    XHR = XHRpage.text
    jsonXHR = json.loads(XHR)

    TickerTotalCount = int(jsonXHR['totalCount'])
    PageCount = TickerTotalCount // 60 + 1
    StockReutersCodeList = []
    StockSymbolCodeList = []

    for A in range(PageCount) :
        RequestURL = ("https://api.stock.naver.com/stock/exchange/%s/marketValue?page=%s&pageSize=60"
        %(MarketName, A + 1))

        XHRpage = requests.get(RequestURL, headers=headers, timeout=5)
        XHR = XHRpage.text
        jsonXHR = json.loads(XHR)

        StockCount = len(jsonXHR['stocks'])
        for B in range(StockCount):
            StockReutersCodeList.append(jsonXHR['stocks'][B]['reutersCode'])
            StockSymbolCodeList.append(jsonXHR['stocks'][B]['symbolCode'])

    return(StockReutersCodeList, StockSymbolCodeList)

@jit
def worldstockrequestURLmaker(StockReutersCodeList): #input(StockReutersCodeList) output(RequestURL)
    for A in range(len(StockReutersCodeList)):
        if A == 0:
            RequestURL = "https://polling.finance.naver.com/api/realtime/worldstock/stock/" + StockReutersCodeList[0]
        else:
            RequestURL = RequestURL + "%2C" + StockReutersCodeList[A]

    return(RequestURL)

@jit
def worldstockinformationloader(ReutersCodeList): #input(ReutersCodeList) output(StockInformation, LocalTimeInformation, ServerTimeInformation, MarketTimeInformation)
    StockInformation = {}
    LocalTimeInformation = []
    ServerTimeInformation = []
    MarketTimeInformation = []
    for A in range((len(ReutersCodeList) // 300) + 1):
        TempReutersCodeList = ReutersCodeList[A * 300 : (A + 1) * 300]
        RequestURL = worldstockrequestURLmaker(TempReutersCodeList)
        XHRpage = requests.get(RequestURL, headers=headers, timeout=5)
        XHR = XHRpage.text
        jsonXHR = json.loads(XHR)

        LocalTimeInformation.append("(UTC±00:00)%s" %datetime.utcnow())
        ServerTimeInformation.append("(UTC+09:00)%s-%s-%s %s:%s:%s"
                                     %(jsonXHR['time'][0:4]
                                      ,jsonXHR['time'][4:6]
                                      ,jsonXHR['time'][6:8]
                                      ,jsonXHR['time'][8:10]
                                      ,jsonXHR['time'][10:12]
                                      ,jsonXHR['time'][12:14]))
        MarketTimeInformation.append("(UTC%s)%s-%s-%s %s:%s:%s"
                                    %(jsonXHR['datas'][0]['localTradedAt'][19:26]
                                      ,jsonXHR['datas'][0]['localTradedAt'][0:4]
                                      ,jsonXHR['datas'][0]['localTradedAt'][5:7]
                                      ,jsonXHR['datas'][0]['localTradedAt'][8:10]
                                      ,jsonXHR['datas'][0]['localTradedAt'][11:13]
                                      ,jsonXHR['datas'][0]['localTradedAt'][14:16]
                                      ,jsonXHR['datas'][0]['localTradedAt'][17:19]))

        for B in range(len(jsonXHR['datas'])):
            StockInformation['%sClosePrice' %jsonXHR['datas'][B]['symbolCode']] = str(jsonXHR['datas'][B]['closePrice']).replace(',','')
            StockInformation['%sAccumulatedTradingVolume' %jsonXHR['datas'][B]['symbolCode']] = str(jsonXHR['datas'][B]['accumulatedTradingVolume']).replace(',','')
            StockInformation['%sMarketValueFull' %jsonXHR['datas'][B]['symbolCode']] = str(jsonXHR['datas'][B]['marketValueFull']).replace(',','')

    return(StockInformation, LocalTimeInformation, ServerTimeInformation, MarketTimeInformation)

Interval = int(input("interval : "))

WorldMarketList = ['NYSE', 'NASDAQ', 'AMEX']
WorldStockReutersCodeList = {}
WorldStockSymbolCodeList = {}

for A in WorldMarketList:
    TempReutersCodeList, TempSymbolCodeList = worldmarkettickerlist(A)
    WorldStockReutersCodeList[A] = TempReutersCodeList
    WorldStockSymbolCodeList[A] = TempSymbolCodeList

StartTime = int(str(time())[:10])
PrintCount = 0
while 1:
    PrintCount = PrintCount + 1
    TimingTF = False
    while TimingTF == False:
        if ((int(str(time())[:10]) - StartTime) % Interval == 0) or (((int(str(time())[:10]) - StartTime) // Interval) >= PrintCount):
            TimingTF = True
    print("start print %d"%PrintCount)

    for B in WorldMarketList:
        StockInformation, LocalTimeInformation, ServerTimeInformation, MarketTimeInformation = worldstockinformationloader(WorldStockReutersCodeList[B])
        for C in WorldStockSymbolCodeList[B]:
            count = 0
            try:
                LocalTime = LocalTimeInformation[count // 300]
                ServerTime = ServerTimeInformation[count // 300]
                MarketTime = MarketTimeInformation[count // 300]
            except:
                print("Error : code 001 %s"%C)

            try:
                Ticker = C
                ClosePrice = StockInformation['%sClosePrice'%C]
                AccumulatedTradingVolume = StockInformation['%sAccumulatedTradingVolume'%C]
                MarketValueFull = StockInformation['%sMarketValueFull'%C]
            except:
                print("Error : code 002 %s"%C)

            try:
                if B == "NYSE":
                    FileNameTicker = ("NYSE-%s" %C)
                elif B == "NASDAQ":
                    FileNameTicker = ("NASDAQ-%s" %C)
                elif B == "AMEX":
                    FileNameTicker = ("NYSEAMERICAN-%s" %C)
            except:
                print("Error : code 003 %s"%C)

            try:
                DataFrame = {'LocalTime' :  [LocalTime]
                             ,'ServerTime' : [ServerTime]
                             ,'MarketTime' : [MarketTime]
                             ,'Ticker' : [Ticker]
                             ,'Marketprice' : [ClosePrice]
                             ,'AccumulatedTradingVolume' : [AccumulatedTradingVolume]
                             ,'MarketValueFull' : [MarketValueFull]}
                df = pandas.DataFrame(DataFrame)
                count = count + 1
            except:
                print("Error : code 004 %s"%C)

            if PrintCount == 1:
                try:
                    if not os.path.exists('financerecorde'):
                        os.mkdir('financerecorde')
                        os.mkdir('financerecorde\\%s-%s-%s'
                                 %(LocalTime[11:15]
                                   ,LocalTime[16:18]
                                   ,LocalTime[19:21]))
                        df.to_csv('financerecorde\\%s-%s-%s\\pricerecord_%s_%s-%s-%s.csv'
                                  %(LocalTime[11:15]
                                    ,LocalTime[16:18]
                                    ,LocalTime[19:21]
                                    ,FileNameTicker
                                    ,LocalTime[11:15]
                                    ,LocalTime[16:18]
                                    ,LocalTime[19:21])
                                    ,index=False, mode='w', encoding='utf-8-sig')
                    elif not os.path.exists('financerecorde\\%s-%s-%s'
                                            %(LocalTime[11:15]
                                              ,LocalTime[16:18]
                                              ,LocalTime[19:21])):
                        os.mkdir('financerecorde\\%s-%s-%s'
                                 %(LocalTime[11:15]
                                   ,LocalTime[16:18]
                                   ,LocalTime[19:21]))
                        df.to_csv('financerecorde\\%s-%s-%s\\pricerecord_%s_%s-%s-%s.csv'
                                  %(LocalTime[11:15]
                                    ,LocalTime[16:18]
                                    ,LocalTime[19:21]
                                    ,FileNameTicker
                                    ,LocalTime[11:15]
                                    ,LocalTime[16:18]
                                    ,LocalTime[19:21])
                                    ,index=False, mode='w', encoding='utf-8-sig')
                    elif not os.path.exists('financerecorde\\%s-%s-%s\\pricerecord_%s_%s-%s-%s.csv'
                                            %(LocalTime[11:15]
                                              ,LocalTime[16:18]
                                              ,LocalTime[19:21]
                                              ,FileNameTicker
                                              ,LocalTime[11:15]
                                              ,LocalTime[16:18]
                                              ,LocalTime[19:21])):
                        df.to_csv(('financerecorde\\%s-%s-%s\\pricerecord_%s_%s-%s-%s.csv'
                                   %(LocalTime[11:15]
                                     ,LocalTime[16:18]
                                     ,LocalTime[19:21]
                                     ,FileNameTicker
                                     ,LocalTime[11:15]
                                     ,LocalTime[16:18]
                                     ,LocalTime[19:21]))
                                         ,index=False, mode='w', encoding='utf-8-sig')
                    else:
                        df.to_csv('financerecorde\\%s-%s-%s\\pricerecord_%s_%s-%s-%s.csv'
                                  %(LocalTime[11:15]
                                    ,LocalTime[16:18]
                                    ,LocalTime[19:21]
                                    ,FileNameTicker
                                    ,LocalTime[11:15]
                                    ,LocalTime[16:18]
                                    ,LocalTime[19:21])
                                    ,index=False, mode='a', encoding='utf-8-sig', header=False)
                except:
                    print("Error : code 005 %s"%C)
            else:
                try:
                    df.to_csv('financerecorde\\%s-%s-%s\\pricerecord_%s_%s-%s-%s.csv'
                              %(LocalTime[11:15]
                                ,LocalTime[16:18]
                                ,LocalTime[19:21]
                                ,FileNameTicker
                                ,LocalTime[11:15]
                                ,LocalTime[16:18]
                                ,LocalTime[19:21])
                                ,index=False, mode='a', encoding='utf-8-sig', header=False)
                except:
                    print("Error : code 006 %s"%C)
                    if not os.path.exists('financerecorde'):
                        os.mkdir('financerecorde')
                        os.mkdir('financerecorde\\%s-%s-%s'
                                 %(LocalTime[11:15]
                                   ,LocalTime[16:18]
                                   ,LocalTime[19:21]))
                        df.to_csv('financerecorde\\%s-%s-%s\\pricerecord_%s_%s-%s-%s.csv'
                                  %(LocalTime[11:15]
                                    ,LocalTime[16:18]
                                    ,LocalTime[19:21]
                                    ,FileNameTicker
                                    ,LocalTime[11:15]
                                    ,LocalTime[16:18]
                                    ,LocalTime[19:21])
                                    ,index=False, mode='w', encoding='utf-8-sig')
                    elif not os.path.exists('financerecorde\\%s-%s-%s'
                                            %(LocalTime[11:15]
                                              ,LocalTime[16:18]
                                              ,LocalTime[19:21])):
                        os.mkdir('financerecorde\\%s-%s-%s'
                                 %(LocalTime[11:15]
                                   ,LocalTime[16:18]
                                   ,LocalTime[19:21]))
                        df.to_csv('financerecorde\\%s-%s-%s\\pricerecord_%s_%s-%s-%s.csv'
                                  %(LocalTime[11:15]
                                    ,LocalTime[16:18]
                                    ,LocalTime[19:21]
                                    ,FileNameTicker
                                    ,LocalTime[11:15]
                                    ,LocalTime[16:18]
                                    ,LocalTime[19:21])
                                    ,index=False, mode='w', encoding='utf-8-sig')
                    elif not os.path.exists('financerecorde\\%s-%s-%s\\pricerecord_%s_%s-%s-%s.csv'
                                            %(LocalTime[11:15]
                                              ,LocalTime[16:18]
                                              ,LocalTime[19:21]
                                              ,FileNameTicker
                                              ,LocalTime[11:15]
                                              ,LocalTime[16:18]
                                              ,LocalTime[19:21])):
                        df.to_csv(('financerecorde\\%s-%s-%s\\pricerecord_%s_%s-%s-%s.csv'
                                   %(LocalTime[11:15]
                                     ,LocalTime[16:18]
                                     ,LocalTime[19:21]
                                     ,FileNameTicker
                                     ,LocalTime[11:15]
                                     ,LocalTime[16:18]
                                     ,LocalTime[19:21]))
                                         ,index=False, mode='w', encoding='utf-8-sig')
                    else:
                        df.to_csv('financerecorde\\%s-%s-%s\\pricerecord_%s_%s-%s-%s.csv'
                                  %(LocalTime[11:15]
                                    ,LocalTime[16:18]
                                    ,LocalTime[19:21]
                                    ,FileNameTicker
                                    ,LocalTime[11:15]
                                    ,LocalTime[16:18]
                                    ,LocalTime[19:21])
                                    ,index=False, mode='a', encoding='utf-8-sig', header=False)
    print("end print")