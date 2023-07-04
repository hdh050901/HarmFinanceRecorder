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

url = 'https://finance.yahoo.com/world-indices'

page = requests.get(url, headers=headers, timeout=5)
print("페이지 응답코드:",page.status_code)

index = -1
indexs = list()
printindex = 0

while 1:
    df = ''
    index = 0
    indexs.clear()
    page = ''
    html = ''
    tds= ''
    tdsindex = 0
    i = 0

    while datetime.utcnow().second % 3 != 2:
        True

    loadstarttime= datetime.utcnow().second

    index = index+1

    page = requests.get(url, headers=headers)

    html = page.text
    soup = BeautifulSoup(html, 'html.parser')

    tdsindex = 0
    tds = soup.findAll('td')

    for td in tds:
        indexs.append(td.text)
        tdsindex = tdsindex + 1

    i =0
    tdsindex = 0
    for i in indexs:
        if tdsindex % 9 == 3:
            indexs[tdsindex] = ''
        elif tdsindex % 9 == 4:
            indexs[tdsindex] = ''
        elif tdsindex % 9 == 5:
            indexs[tdsindex] = ''
        elif tdsindex % 9 == 6:
            indexs[tdsindex] = ''
        elif tdsindex % 9 == 7:
            indexs[tdsindex] = ''
        elif tdsindex % 9 == 8:
            indexs[tdsindex] = ''
        tdsindex = tdsindex + 1

    indexs = list(filter(None, indexs))

    loadendtime = datetime.utcnow().second
    
    time = ('(UTC±00:00)%04d/%02d/%02d-%02d:%02d:%02d.%06d'
            %(datetime.utcnow().year
              ,datetime.utcnow().month
              ,datetime.utcnow().day
              ,datetime.utcnow().hour
              ,datetime.utcnow().minute
              ,datetime.utcnow().second
              ,datetime.utcnow().microsecond))

    if loadendtime >= loadstarttime:
        delaytime = loadendtime - loadstarttime
    else:
        delaytime = loadendtime - loadstarttime + 60

    if delaytime >=3:
        delay = delaytime - 3
    else:
        delay = 0
    i = 0

    time_array = [time]
    dataframe = {'index' : printindex ,'datetime': time_array, 'Delay' : delay}

    for i in range(36):
        market_price = [indexs[i * 3 + 2]]
        dataframe['%s'%indexs[i * 3 + 1]] = market_price
    

    if printindex == 0:
        print('\n')
    else:
        print('\n\n')
    if delay == 0:
        print("index : %07d\ntime : %s\ndelay : N/A" %(printindex,time))
    else:
        print("index : %07d\ntime : %s\ndelay : %ds" %(printindex,time,delay))
    for i in range(36):
        print('%32s : %s'%(indexs[i * 3 + 1],indexs[i * 3 + 2]))


    df = pandas.DataFrame(dataframe)

    if not os.path.exists('stockmarket_indexrecord.csv'):
        df.to_csv(('stockmarket_indexrecord.csv'), index=False, mode='w', encoding='utf-8-sig')
    else:
        df.to_csv(('stockmarket_indexrecord.csv'), index=False, mode='a', encoding='utf-8-sig', header=False)

    printindex = printindex + 1