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
while MarketSelectTF == False:
    print("KOSPI / KOSDAQ : 1\nNYSE / AMEX : 2\nNASDAQ : 3")
    MarketSelect = int(input(" : "))

    if MarketSelect == 1:
        ticker = input('ticker : ')
        RequestUrl = "https://polling.finance.naver.com/api/realtime/domestic/stock/" + ticker
        MarketSelectTF = True
    elif MarketSelect == 2:
        ticker = input('ticker : ').upper()
        RequestUrl = "https://polling.finance.naver.com/api/realtime/worldstock/stock/" + ticker
        MarketSelectTF = True
    elif MarketSelect == 3:
        ticker = input('ticker : ').upper()
        RequestUrl = "https://polling.finance.naver.com/api/realtime/worldstock/stock/" + ticker + ".O"
        MarketSelectTF = True
    else:
        print("unavailable market")

Interval = int(input("interval : "))

while 1:
    if Interval == 1:
        TimeMax = -1
        while datetime.utcnow().microsecond > TimeMax:
            TimeMax = datetime.utcnow().microsecond - 1
    else:
        while datetime.utcnow().second % Interval == 0:
            1
        while datetime.utcnow().second % Interval != 0:
            1

    if MarketSelect == 1:
        if (datetime.utcnow().hour > 0) and (datetime.utcnow().hour < 4 or (datetime.utcnow().hour == 4 and datetime.utcnow().minute < 20)):
            MarketOpen = True
        else:
            MarketOpen = False
    elif MarketSelect == 2 or 3:
        if (datetime.utcnow().hour > 15 or (datetime.utcnow().hour == 14 and datetime.utcnow().minute >= 30)) and (datetime.utcnow().hour < 21):
            MarketOpen = True
        else:
            MarketOpen = False

    if MarketOpen == True:
        XHRpage = requests.get(RequestUrl, headers=headers, timeout=5)
        PageResponseCode = XHRpage.status_code
        XHR = XHRpage.text
        jsonXHR = json.loads(XHR)
        
        Time = ("(UTC±0)%s" %datetime.utcnow())

        DataFrame = {'Time' :  [Time], 'ticker' : [ticker], 'marketprice' : [jsonXHR['datas'][0]['closePrice']]}
        df = pandas.DataFrame(DataFrame)
        if not os.path.exists('financerecorde\%s_pricerecord_%04d-%02d-%02d.csv' %(ticker,datetime.utcnow().year,datetime.utcnow().month,datetime.utcnow().day)):
            if not os.path.exists('financerecorde'):
                os.mkdir("financerecorde")
                df.to_csv(('financerecorde\%s_pricerecord_%04d-%02d-%02d.csv' %(ticker,datetime.utcnow().year,datetime.utcnow().month,datetime.utcnow().day)), index=False, mode='w', encoding='utf-8-sig')
            else:
                df.to_csv(('financerecorde\%s_pricerecord_%04d-%02d-%02d.csv' %(ticker,datetime.utcnow().year,datetime.utcnow().month,datetime.utcnow().day)), index=False, mode='w', encoding='utf-8-sig')
        else:
            df.to_csv(('financerecorde\%s_pricerecord_%04d-%02d-%02d.csv' %(ticker,datetime.utcnow().year,datetime.utcnow().month,datetime.utcnow().day)), index=False, mode='a', encoding='utf-8-sig', header=False)

        print("\n\nTime        : %s\nTicker      : %s\nMarketprice : %s" %(Time,ticker,jsonXHR['datas'][0]['closePrice']))
    else:
        print("market is close")