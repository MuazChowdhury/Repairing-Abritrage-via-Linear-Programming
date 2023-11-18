import numpy as np
import pandas as pd
import math as m
from yahoo_fin import options
from datetime import datetime
import yahoo_fin.stock_info as si
import yfinance as yf
import scipy as sp

def option_price_data(ticker):
    today = datetime.today()
    S = si.get_live_price(ticker)
    maturities = options.get_expiration_dates(ticker)
    maturities_frac=[]
    for x in maturities:
        maturities_frac.append((datetime.strptime(x, "%B %d, %Y")-today).days+1)
    maturities_frac = [x for x in maturities_frac if x <= 600]
    
    chain = options.get_options_chain(ticker,maturities[-1])
    calls = chain["calls"]
    strikes=calls["Strike"]

    for i in range(len(maturities)-1,-1,-1):
        chain = options.get_options_chain(ticker,maturities[i])
        calls_n = chain["calls"]
        strikes=set(strikes).intersection(set(calls_n["Strike"]))
        strikes=list(strikes)
    strikes.sort()
    strikes=strikes[5:-5]
    
    option_prices=pd.DataFrame(index=maturities_frac,columns=strikes)
    option_bid=pd.DataFrame(index=maturities_frac,columns=strikes)
    option_ask=pd.DataFrame(index=maturities_frac,columns=strikes)
    
    for i in range(len(maturities_frac)):
        chain = options.get_options_chain(ticker,maturities[i])
        calls_n = chain["calls"]
        calls_n=calls_n[calls_n['Strike'].isin(strikes)]
        option_prices.iloc[i]=(calls_n["Bid"]+calls_n["Ask"])/2
        option_bid.iloc[i]=calls_n["Bid"]
        option_ask.iloc[i]=calls_n["Ask"]
        
    return S, maturities_frac, option_prices, option_bid, option_ask, strikes

def D(T):
    # Function for discounting prices
    risk_free = pd.DataFrame(index=[0,30,91,182,365,730,1825],columns=['r_t','Integrated value'])
    risk_free['r_t']=[0.0483,0.0427,0.05187,0.0476,0.0419,0.03702,0.0331]
    risk_free.iat[0,1]=0

    for i in range(1,len(risk_free.index)):
        t_i = risk_free.index[i]/365
        t_im = risk_free.index[i-1]/365
        a = (risk_free.iat[i,0]-risk_free.iat[i-1,0])/(t_i-t_im)
        b = risk_free.iat[i,0]-a*t_i
        risk_free.iat[i,1] = a*(t_i)**2/2 + b*t_i - a*(t_im)**2/2 - b*t_im + risk_free.iat[i-1,1]
    
    f = sp.interpolate.interp1d(risk_free.index,risk_free['Integrated value'])

    return np.exp(-f(T))

def normaliser(S, maturities_frac, option_prices, option_bids, option_asks, strikes):
    
    option_bid_norm = (option_prices-option_bids).apply(lambda x: x*D(x.index)/S, axis = 0)
    option_ask_norm = (option_asks-option_prices).apply(lambda x: x*D(x.index)/S, axis = 0)
    
    option_prices_norm = option_prices.apply(lambda x: x*D(x.index)/S, axis=0)
    option_prices_norm.insert(loc=0, column=0.0, value=[1]*len(option_prices_norm.index))
    
    strikes_norm = pd.DataFrame(index=maturities_frac,columns=strikes,data=[strikes for i in range(len(maturities_frac))])
    strikes_norm = strikes_norm.apply(lambda x: x*D(x.index)/S, axis = 0)
    strikes_norm.insert(loc=0, column=0.0, value = [0.0]*len(option_prices_norm.index))
    
    return option_prices_norm, option_bid_norm, option_ask_norm, strikes_norm
