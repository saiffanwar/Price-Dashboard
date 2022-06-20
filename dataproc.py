import pandas as pd
import numpy as np 
from datetime import datetime, timedelta
from tqdm import tqdm
import os
import pickle as pck

pd.set_option('display.max_rows', 100)

# def augment(path = '/Users/saifanwar/Documents/OI Volume Dashboard - Copy/data/TAC_Middle_East_NG.E.100393.csv'):

fileDict = {'TAC FE': ['TAC_Pacific_NG.E.84133'], 
    'TAC EU': ['TAC_Europe_NG.E.66167'], 
    'TAC ATL': ['TAC_Atlantic_NG.E.92599'], 
    'TAC ME': ['TAC_Middle_East_NG.E.100393'], 
    'TTF': ['TAC_TTF_USD_NG.E.136495'], 
    'HH': ['HH_NG.A.1064'], 
    'NBP': ['NBPUSD'], 
    'PSV': ['PSVUSD'], 
    'AOC': ['AOCUSD'], 
    'JKM': ['JKM_Broker_NG.E.117899'], 
    'FO': ['TAC LS FO_FO.E.80354'], 
    'GO': ['TAC_GO_0.05_FOB_Singapore_GO.H.71040'], 
    'Ice Brent': ['Ice_Brent_CL.E.70062'], 
    'Pacific174': ['Pacific174_NG.E.123269'], 
    'Atlantic174': ['Atlantic174_NG.E.128633'], 
    'Pacific155': ['Pacific155_NG.E.123277'], 
    'Atlantic155': ['Atlantic155_NG.E.128627'], 
    'Pacific138': ['Pacific138_NG.E.128619'], 
    'Atlantic138': ['Atlantic138_NG.E.128613']
    }
class DataProcessing():
    def augment(self, path):
        
        df = pd.read_csv(os.getcwd()+'/data/'+path+'.csv')


        newdf = pd.DataFrame(columns=['TRADEDATE', 'CONTRACT_DATE', 'Trade Date', 'Contract Month', 'Quarters', 'Calendar', 'Summer/Winter'])

        tradeDates, contractDates, prices = [], [], []
        print('Augmenting Data from '+path)
        for row in range(len(df)):
            for col in df.columns[1:]:
                tradeDates.append(pd.to_datetime(df['Unnamed: 0'].iloc[row],format='%Y-%m-%d'))
                contractDates.append(pd.to_datetime(col,format='%Y-%m-%d'))
                prices.append(df[col].iloc[row])



        newdf['CONTRACT_DATE'] = contractDates
        newdf['TRADEDATE'] = tradeDates
        newdf['Absolute'] = prices
        newdf['Trade Date'] = newdf['TRADEDATE'].dt.strftime('%d-%b-%y')
        newdf['Contract Month'] = newdf['CONTRACT_DATE'].dt.strftime('%b-%y')

        q=[['Jan','Feb','Mar'],['Apr','May','Jun'],['Jul','Aug','Sep'],['Oct','Nov','Dec']]
        newdf['Quarters']=np.select(
                [(newdf['CONTRACT_DATE'].dt.strftime('%b').isin(q[0])),(newdf['CONTRACT_DATE'].dt.strftime('%b').isin(q[1])),
                (newdf['CONTRACT_DATE'].dt.strftime('%b').isin(q[2])),(newdf['CONTRACT_DATE'].dt.strftime('%b').isin(q[3]))],
                [(newdf['CONTRACT_DATE'].dt.strftime('%y'))+'Q1',(newdf['CONTRACT_DATE'].dt.strftime('%y'))+'Q2',
                (newdf['CONTRACT_DATE'].dt.strftime('%y'))+'Q3',(newdf['CONTRACT_DATE'].dt.strftime('%y'))+'Q4']
            )
        # Calendar
        newdf['Calendar']='Cal'+newdf['CONTRACT_DATE'].dt.strftime('%y')
        # Winter/Summer
        season=[['Apr','May','Jun','Jul','Aug','Sep'],['Oct','Nov','Dec'],['Jan','Feb','Mar']]
        newdf['Summer/Winter']=np.select(
            [(newdf['CONTRACT_DATE'].dt.strftime('%b').isin(season[0])),
            (newdf['CONTRACT_DATE'].dt.strftime('%b').isin(season[1])),
            (newdf['CONTRACT_DATE'].dt.strftime('%b').isin(season[2]))
            ],
            ['Summer '+newdf['CONTRACT_DATE'].dt.strftime('%Y'),'Winter '+newdf['CONTRACT_DATE'].dt.strftime('%Y'),'Winter '+newdf['CONTRACT_DATE'].apply(lambda x: str(int(x.year)-1))]
        )

        with open(os.getcwd()+'/data/pickles/'+path+'.pck', 'wb') as file:
            pck.dump(newdf, file)  
        return newdf


    def fetchData(self,type):
        data = pck.load(open(os.getcwd()+'/data/pickles/'+type[0]+'.pck', 'rb'))
        return data
    
    def updateData(self,type):
        self.data = pck.load(open(os.getcwd()+'/data/pickles/'+type[0]+'.pck', 'rb'))
    

    def refresh(self,):
        for i in fileDict.items():
            self.augment(i[1][0])