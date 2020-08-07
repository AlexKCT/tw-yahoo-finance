import time
import requests
import pandas as pd

def create_today_timestamp():
    today = time.strftime("%Y-%m-%d",time.gmtime())
    return int(time.mktime(time.strptime(today, "%Y-%m-%d")))
def create_timestamp_from_today(n):
    today = create_today_timestamp()
    return today + n*24*3600
tomorrow_timestamp = create_timestamp_from_today(1)


def create_tw_stock_info_list():
    res = requests.get("http://isin.twse.com.tw/isin/C_public.jsp?strMode=2")
    df = pd.read_html(res.text)[0]
    df.columns = df.iloc[0]
    df = df.iloc[1:]
    df = df.drop(columns=['備註'])
    df = df[df['CFICode'].str.contains('ESVUFR')]
    df = df.dropna(thresh=3, axis=0).dropna(thresh=3, axis=1)
    # df = df.dropna(how='any')
    df = df.reset_index(drop=True)
    new_df = df['有價證券代號及名稱'].str.replace(u'\u3000',' ').str.split(u' ',expand=True)
    new_df.columns = ['Ticker', 'StockName']
    new_df['Sector'] = df['產業別']
    return new_df

tw_stock_info_df = create_tw_stock_info_list()
tw_stock_info_df

stock_df = pd.DataFrame()
ticker_list = tw_stock_info_df['Ticker']
# ticker_list = tw_stock_info_df['Ticker'].tail(5)
for ticker in ticker_list:
    print('## Info: Download Ticker '+ticker+'!')
    site = "https://query1.finance.yahoo.com/v7/finance/download/"+ticker+".TW?period1=0&period2="+str(tomorrow_timestamp)+"&interval=1d&events=history&crumb=hP2rOschxO0"
    try:
        # response = requests.post(site)
        # tmp_df = pd.read_csv(StringIO(response.text))
        tmp_df = pd.read_csv(site)
        tmp_df['Ticker'] = ticker
        stock_df = pd.concat([stock_df,tmp_df],axis=0)
    except:
        print('## Warning: Ticker '+ticker+' is failed!')
        
stock_df = stock_df.reset_index(drop=True)
stock_df = stock_df[['Date','Ticker','Open','High','Low','Close','Adj Close','Volume']]
# nandf = stock_df[stock_df.isnull().any(axis=1)]
stock_df = stock_df.dropna(how='any')
stock_df.to_csv('stock.csv')
