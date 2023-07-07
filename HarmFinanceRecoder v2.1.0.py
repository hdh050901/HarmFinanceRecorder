import os
import requests
import json
from datetime import datetime
import pandas

headers = {
    'User-Agent'      : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36', 
    'Accept'          : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 
    'Accept-Language' : 'en-US,en;q=0.5',
    'DNT'             : '1',
    'Connection'      : 'close'
}

MarketSelectTF = False
TickerSelectTF = False
while MarketSelectTF == False:
    print("KOSPI / KOSDAQ : 1\nNYSE / AMEX : 2\nNASDAQ : 3")
    MarketSelect = int(input("Market   : "))

    if MarketSelect == 1:
        while TickerSelectTF == False:
            InputTicker = input('ticker   : ')
            RequestUrl = "https://polling.finance.naver.com/api/realtime/domestic/stock/" + InputTicker

            XHRpage = requests.get(RequestUrl, headers=headers, timeout=5)
            PageResponseCode = XHRpage.status_code
            XHR = XHRpage.text
            jsonXHR = json.loads(XHR)

            if len(jsonXHR['datas']) == 0:
                print("items that do not exist")
            else:
                TickerSelectTF = True
        MarketSelectTF = True
    elif MarketSelect == 2:
        while TickerSelectTF == False:
            InputTicker = input('ticker   : ').upper()
            RequestUrl = "https://polling.finance.naver.com/api/realtime/worldstock/stock/" + InputTicker

            XHRpage = requests.get(RequestUrl, headers=headers, timeout=5)
            PageResponseCode = XHRpage.status_code
            XHR = XHRpage.text
            jsonXHR = json.loads(XHR)

            if len(jsonXHR['datas']) == 0:
                print("items that do not exist")
            else:
                TickerSelectTF = True
        MarketSelectTF = True
    elif MarketSelect == 3:
        while TickerSelectTF == False:
            InputTicker = input('ticker   : ').upper()
            RequestUrl = "https://polling.finance.naver.com/api/realtime/worldstock/stock/" + InputTicker + ".O"

            XHRpage = requests.get(RequestUrl, headers=headers, timeout=5)
            PageResponseCode = XHRpage.status_code
            XHR = XHRpage.text
            jsonXHR = json.loads(XHR)

            if len(jsonXHR['datas']) == 0:
                print("items that do not exist")
            else:
                TickerSelectTF = True
        MarketSelectTF = True
    else:
        print("unavailable market")

Interval = int(input("interval : "))
PreviousAccumulatedTradingVolume = 0

while 1:
    if Interval == 0:
        1
    elif Interval == 1:
        TimeMax = -1
        while datetime.utcnow().microsecond > TimeMax:
            TimeMax = datetime.utcnow().microsecond - 1
    else:
        while datetime.utcnow().second % Interval == 0:
            1
        while datetime.utcnow().second % Interval != 0:
            1

    if MarketSelect == 1:
        if (datetime.utcnow().hour > 0 or (datetime.utcnow().hour == 23 and datetime.utcnow().minute >= 50)) and (datetime.utcnow().hour < 6 or (datetime.utcnow().hour == 6 and datetime.utcnow().minute <= 30)):
            MarketOpen = True
        else:
            MarketOpen = False
    elif MarketSelect == 2 or 3:
        if (datetime.utcnow().hour > 13 or (datetime.utcnow().hour == 13 and datetime.utcnow().minute >= 20)) and (datetime.utcnow().hour < 21 or (datetime.utcnow().hour == 21 and datetime.utcnow().minute <= 10)):
            MarketOpen = True
        else:
            MarketOpen = False

    if MarketOpen == True:
        XHRpage = requests.get(RequestUrl, headers=headers, timeout=5)
        PageResponseCode = XHRpage.status_code
        XHR = XHRpage.text
        jsonXHR = json.loads(XHR)
        
        LocalTime = ("(UTC±00:00)%s" %datetime.utcnow())
        ServerTime = ("(UTC+09:00)%s-%s-%s %s:%s:%s"
                      %(jsonXHR['time'][0:4]
                        ,jsonXHR['time'][4:6]
                        ,jsonXHR['time'][6:8]
                        ,jsonXHR['time'][8:10]
                        ,jsonXHR['time'][10:12]
                        ,jsonXHR['time'][12:14]))
        MarketTime = ("(UTC%s)%s-%s-%s %s:%s:%s"
                      %(jsonXHR['datas'][0]['localTradedAt'][19:26]
                        ,jsonXHR['datas'][0]['localTradedAt'][0:4]
                        ,jsonXHR['datas'][0]['localTradedAt'][5:7]
                        ,jsonXHR['datas'][0]['localTradedAt'][8:10]
                        ,jsonXHR['datas'][0]['localTradedAt'][11:13]
                        ,jsonXHR['datas'][0]['localTradedAt'][14:16]
                        ,jsonXHR['datas'][0]['localTradedAt'][17:19]))
        
        MarketStatus = jsonXHR['datas'][0]['marketStatus']
        ExchangeCode = jsonXHR['datas'][0]['stockExchangeType']['code']
        ClosePrice = jsonXHR['datas'][0]['closePrice']
        AccumulatedTradingVolume = int(str(jsonXHR['datas'][0]['accumulatedTradingVolume']).replace(',',''))
        UnittimeTradingVolume = AccumulatedTradingVolume - PreviousAccumulatedTradingVolume
        PreviousAccumulatedTradingVolume = AccumulatedTradingVolume

        if ExchangeCode == "KS":
            Ticker = ("KRXKOSPI:%s" %InputTicker)
        elif ExchangeCode == "KQ":
            Ticker = ("KRXKOSDAQ:%s" %InputTicker)
        elif ExchangeCode == "NYS":
            Ticker = ("NYSE:%s" %InputTicker)
        elif ExchangeCode == "NSQ":
            Ticker = ("NASDAQ:%s" %InputTicker)
        elif ExchangeCode == "AMX":
            Ticker = ("NYSEAMERICAN:%s" %InputTicker)
        if ExchangeCode == "KS":
            FileNameTicker = ("KRXKOSPI-%s" %InputTicker)
        elif ExchangeCode == "KQ":
            FileNameTicker = ("KRXKOSDAQ-%s" %InputTicker)
        elif ExchangeCode == "NYS":
            FileNameTicker = ("NYSE-%s" %InputTicker)
        elif ExchangeCode == "NSQ":
            FileNameTicker = ("NASDAQ-%s" %InputTicker)
        elif ExchangeCode == "AMX":
            FileNameTicker = ("NYSEAMERICAN-%s" %InputTicker)

        if LocalTime[28:30] != MarketTime[28:30]:
            if int(LocalTime[28:30]) < int(MarketTime[28:30]):
                DelayTime = int(LocalTime[28:30]) + 60 - int(MarketTime[28:30])
            else:
                DelayTime = int(LocalTime[28:30]) - int(MarketTime[28:30])
        else:
            DelayTime = 0

        if MarketStatus == "OPEN":
            DataFrame = {'LocalTime' :  [LocalTime]
                         ,'ServerTime' : [ServerTime]
                         ,'MarketTime' : [MarketTime]
                         ,'Delay' : [DelayTime]
                         ,'Ticker' : [Ticker]
                         ,'Marketprice' : [ClosePrice]
                         ,'AccumulatedTradingVolume' : [AccumulatedTradingVolume]
                         ,'UnittimeTradingVolume' : [UnittimeTradingVolume]}
            df = pandas.DataFrame(DataFrame)

            if not os.path.exists('financerecorde\\%s-%s-%s\\pricerecord_%s_%s-%s-%s.csv'
                                  %(LocalTime[11:15]
                                    ,LocalTime[16:18]
                                    ,LocalTime[19:21]
                                    ,FileNameTicker
                                    ,LocalTime[11:15]
                                    ,LocalTime[16:18]
                                    ,LocalTime[19:21])):
                if not os.path.exists('financerecorde\\%s-%s-%s'
                                      %(LocalTime[11:15]
                                        ,LocalTime[16:18]
                                        ,LocalTime[19:21])):
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
                    else:
                        os.mkdir('financerecorde\\%s-%s-%s'
                                 %(LocalTime[11:15]
                                   ,LocalTime[16:18]
                                   ,LocalTime[19:21]))
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

        print("\n\n\nSERVERINFORMATION\n  LocalTime    : %s\n  ServerTime   : %s\n  MarketTime   : %s\n  Delay        : %ds"
              %(LocalTime
                ,ServerTime
                ,MarketTime
                ,DelayTime))
        print("MARKETINFORMATION\n  MarketStatus : %s\n  Ticker       : %s\n  Marketprice  : %s\n  AccumulatedTradingVolume : %s\n  UnittimeTradingVolume    : %s"
              %(MarketStatus
                ,Ticker
                ,ClosePrice
                ,format(AccumulatedTradingVolume, ',')
                ,format(UnittimeTradingVolume, ',')))
    else:
        LocalTime = ("(UTC±00:00)%s" %datetime.utcnow())

        print("\n\n\nSERVERINFORMATION\n  LocalTime    : %s\n  ServerTime   : N/A\n  MarketTime   : N/A\n  Delay        : N/A"
              %(LocalTime))
        print("MARKETINFORMATION\n  MarketStatus : CLOSE\n  Ticker       : N/A\n  Marketprice  : N/A\n  AccumulatedTradingVolume : N/A\n  UnittimeTradingVolume    : N/A")