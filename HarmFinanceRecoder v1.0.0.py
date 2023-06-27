from datetime import datetime
import requests
from bs4 import BeautifulSoup
import pandas
import os

headers = { 
    'User-Agent'      : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36', 
    'Accept'          : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 
    'Accept-Language' : 'en-US,en;q=0.5',
    'DNT'             : '1', # Do Not Track Request Header 
    'Connection'      : 'close'
}

stockSymbol = input('ticker : ').upper()

url = 'https://finance.yahoo.com/quote/'+ stockSymbol + '/key-statistics?p=' + stockSymbol

page = requests.get(url, headers=headers, timeout=5)

print("페이지 응답코드:",page.status_code)

html = page.text

soup = BeautifulSoup(html, 'html.parser')
try:
    cantfind = soup.find('h2', class_='Fz(l) D(ib) Td(inh) Mb(25px) Ell smartphone_Px(20px)').text
    print("error : can\'t find this ticker")
except:
    index = -1

    while 1:
        while datetime.now().second % 3 != 2:
            True

        loadstarttime= datetime.now().second

        index = index+1

        page = requests.get(url, headers=headers)

        html = page.text
        soup = BeautifulSoup(html, 'html.parser')
    
        try:
            market_price = soup.find('fin-streamer', class_='Fw(b) Fz(36px) Mb(-4px) D(ib)').text
        except:
            market_price = "error"

        try:
            premarket_price = soup.find('fin-streamer', class_='C($primaryColor) Fz(24px) Fw(b)').text
        except:
           premarket_price = "error"

        loadendtime = datetime.now().second
    
        time = ('(UTC+09:00)%04d/%02d/%02d-%02d:%02d:%02d.%06d'
                %(datetime.now().year,datetime.now().month ,datetime.now().day
                ,datetime.now().hour,datetime.now().minute,datetime.now().second
                ,datetime.now().microsecond))
    
        if loadendtime >= loadstarttime:
            delaytime = loadendtime - loadstarttime
        else:
            delaytime = loadendtime - loadstarttime + 60

        if delaytime >= 3:
            print('index:%06d  ' %index ,time ,"\tMarketPrice:",market_price,"\tPreMarketPrice:",premarket_price,"\tdelay(%ds)"%(delaytime - 3),sep='')
        else:
            print('index:%06d  ' %index ,time ,"\tMarketPrice:",market_price,"\tPreMarketPrice:",premarket_price,sep='')
    
        time_array = [time]
        market_price_array = [market_price]
        premarket_price_array = [premarket_price]
        if delaytime >=3:
            delay_array = [delaytime - 3]
        else:
            delay_array = [' ']
    
        dataframe = {'datetime': time_array, 'MarketPrice': market_price_array, 'PreMarketPrice' : premarket_price_array, 'Delay' : delay_array}

        df = pandas.DataFrame(dataframe)

        if not os.path.exists('%s_pricerecord.csv' %stockSymbol):
            df.to_csv(('%s_pricerecord.csv' %stockSymbol), index=False, mode='w', encoding='utf-8-sig')
        else:
            df.to_csv(('%s_pricerecord.csv' %stockSymbol), index=False, mode='a', encoding='utf-8-sig', header=False)