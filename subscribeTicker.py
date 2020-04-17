import uuid,json,time
from collections import defaultdict
import pandas as pd
import asyncio, websockets, requests
import re
import datetime
import numpy as np
import matplotlib.pyplot as plt

WS_MAX_RETRY_NUM = 1000000
WS_MAX_DELAY_INTERVAL = 60

DERIBIT_WS_URL = 'wss://www.deribit.com/ws/api/v2'
DERIBIT_QUERY_INSTRUMENT_URL = 'https://www.deribit.com/api/v2/public/getinstruments?expired=false'

CLIENT_SUB_ID = 10000

def get_instruments(inst_type,currency):
	r = requests.get(DERIBIT_QUERY_INSTRUMENT_URL).json()
	instruments = [instr['instrumentName'] for instr in r['result'] if instr["kind"] in inst_type and instr["baseCurrency"] in currency]
	return instruments


def change_maturity(mtr):
	month_list = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
	mtr = re.split('([A-Z]+)', mtr)
	month = month_list.index(mtr[1]) + 1
	maturity = datetime.date(int(mtr[2]) + 2000, month, int(mtr[0]))
	return maturity

def initial_vol_df(allinstruments):
	maturity_list = [ins.split('-')[1] for ins in allinstruments ]
	maturity_list = list(set(maturity_list))
	maturity_list.sort()
	strike_list = [float(ins.split('-')[2]) for ins in allinstruments]
	strike_list = list(set(strike_list))
	strike_list.sort()
	df = pd.DataFrame(index= maturity_list, columns= strike_list)
	return df

def OTM_judge(instrument, underlying):
	strike = float(instrument.split('-')[2])
	call_put = instrument.split('-')[3]
	if (call_put == 'C' and strike > underlying) or (call_put == 'P' and strike < underlying) :
		result = True
	else:
		result = False
	return result


async def handle_ticker(data,bid_vol_df, ask_vol_df, mid_vol_df):
	now_time = datetime.datetime.now()
	now_seconds = int(datetime.datetime.now().timestamp())
	rs = json.loads(data)
	if len(rs) == 7:
		pass
	else:
		param = rs['params']
		instrument = param['channel'].split('.')[1]
		instrument_list = instrument.split('-')
		data = param['data']
		time = data['timestamp']
		time = datetime.datetime.fromtimestamp(time/1000)- datetime.timedelta(hours= 8)
		if not OTM_judge(instrument,data['underlying_price']):
			pass
		else:
			bid_vol_df.loc[instrument_list[1], float(instrument_list[2])] = data['bid_iv']
			ask_vol_df.loc[instrument_list[1], float(instrument_list[2])] = data['ask_iv']
			mid_vol_df.loc[instrument_list[1], float(instrument_list[2])] = data['mark_iv']

			localtime = datetime.datetime.now() - datetime.timedelta(hours= 8)
			print("return time:"+str(time) + " local time" + str(localtime) + " time lag:"+ str((localtime- time).total_seconds()))
			if localtime < start_time + datetime.timedelta(seconds=10) :
				pass

			else:
				if (now_seconds % 5 == 0) and (now_seconds not in second_list):
					plt.clf()
					plt.suptitle('Time:' + str(now_time), fontsize=12, y=1)
					mtr_count = 0
					for mtr in list(bid_vol_df.index):
						bid_series = bid_vol_df.loc[mtr,:].replace(0,np.nan).dropna().reset_index()
						ask_series = ask_vol_df.loc[mtr,:].replace(0,np.nan).dropna().reset_index()
						mid_series = mid_vol_df.loc[mtr,:].replace(0,np.nan).dropna().reset_index()
						bid_series = bid_series.sort_values('index')
						ask_series = ask_series.sort_values('index')
						mid_series = mid_series.sort_values('index')
						mtr_graph = plt.subplot(4, 2, mtr_count + 1)
						mtr_graph.set_title('Maturity:' + str(mtr))
						mtr_graph.set_xlabel('Strike')
						mtr_graph.set_ylabel('Vol')
						mtr_graph.plot(bid_series['index'], bid_series[mtr], '.-', label='bid_vol')
						mtr_graph.plot(ask_series['index'], ask_series[mtr], '.-', label='ask_vol')
						mtr_graph.plot(mid_series['index'], mid_series[mtr], '.-', label='mid_vol')
						mtr_graph.legend(loc='best')
						mtr_count += 1
					second_list.append(now_seconds)
					plt.pause(0.01)
					plt.tight_layout()

async def subscribe(subs,url,callback, bid_vol_df,ask_vol_df,mid_vol_df):
    retries = 0
    delay = 1
    while retries <= WS_MAX_RETRY_NUM:
        try:
            async with websockets.connect(url) as websocket:
            	clientID = CLIENT_SUB_ID
            	for topic in subs:
            		topic['id'] = clientID
            		await websocket.send(json.dumps(topic))
            		clientID += 1
            		time.sleep(1/100)
            		print(f"send: {topic}")
            	while True:
            		rsp = await websocket.recv()
            		data = rsp
            		#print(data)
            		rsp = await callback(data, bid_vol_df, ask_vol_df, mid_vol_df)

        except Exception as e:
            #logger.error("%s: encountered an exception, reconnecting", str(e))
            #logger.error(f"websocket retry count:{retries}")
            print("%s: encountered an exception, reconnecting", str(e))
            await asyncio.sleep(delay)
            retries += 1
            if delay <= WS_MAX_DELAY_INTERVAL:
                delay *= 2

if __name__ == "__main__":
	plt.ion()
	plt.rcParams['figure.figsize'] = (12, 12)
	start_time = datetime.datetime.now() - datetime.timedelta(hours=8)
	second_list = []
	symbols = ["BTC"]
	allinstruments = get_instruments(("option"),("BTC"))
	print(allinstruments[:2])
	sub_ticker = []
	for instrument in allinstruments:
		subtopic = {"jsonrpc": "2.0","id": 0,"method": "public/subscribe","params": {"channels": [f"ticker.{instrument}.raw"]}}
		sub_ticker.append(subtopic)
	print(sub_ticker[:2])
	print(len(sub_ticker))
	bid_vol_df = initial_vol_df(allinstruments)
	ask_vol_df = initial_vol_df(allinstruments)
	mid_vol_df = initial_vol_df(allinstruments)
	tickerudpate = asyncio.ensure_future(subscribe(sub_ticker, DERIBIT_WS_URL, handle_ticker, bid_vol_df,ask_vol_df, mid_vol_df))
	loop = asyncio.get_event_loop()
	loop.run_forever()
	plt.ioff()
	plt.show()

