from handle_api import price_hist, tickers_list
import numpy as np
# import pandas as pd
# import seaborn as sns
# import matplotlib.pyplot as plt
from scipy.stats import norm


def portfolio_model(k, r=0.00075, Ke=0.5, currency='BRL', monthly_g=1.1):
    # Variables descriptions:
        # Vp[k] = portfolio value vector for each asset / [vp1(k), vp2(k), ..., vpq(k)](transposed)
        # r = intermediary charges
        # p = price of unique asset
        # n = amount of unique assets bought
        # cost = cost of buying a unique asset
        # value = value of selling a unique asset
        # M[k] = vector of total amount to be invested at time step k in each asset / [m1(k) m2(k) ... mq(k)](transposed)
        # Na[k] = total amount of assets vector at time step k (beginning of period) / [na1(k), na2(k), ..., naq(k)](transposed)
        # Nam[k] = total amount of assets vector bought or sold at time step k / [nam1(k), nam2(k), ..., namq(k)](transposed)
        # U[k] = control signal vector / [u1(k), u2(k), ..., uq(k)]
        # P[k] = diagonal matrix of prices of each asset at time step k / diag[p1(k), p2(k), ..., pq(k)]
        # k = time step variable
        # a = indication of selling (-1) or buying (1) operation
        # q = total number of assets available
        # ep[k] = error at time step k
        # Vpref = constant desired portfolio value
        # dP[k] = price increment o asset at time step k

    Na = balances()
    M = balances()[currency]
    if a == -1:
        P = prices()[1]
    else:
        P = prices()[0]

    U[k] = a*Nam[k]

    Na[k+1] = Na[k] + U[k]
    M[k+1] = M[k] - P[k]*U[k] - r*P[k]*math.fabs(U[k])
    Vp[k] = P[k]*Na[k] + M[k]

    Vref = Vp*monthly_g*(k/30*24*60)

    Vp[k+1] = Vp[k] + dP[k]*Na[k] + dP[k]*U[k] - r*P[k]*U[k]

    ep[k] = Vref - Vp[k]

    ep[k+1] = Ke*ep[k] + r*P[k]*math.fabs(U[k])

    U[k] = (ep[k] - dp[k]*Na[k] - Ke*ep[k])/dp[k]


def PID(Kp=0.5, Ki=0, Kd=0, MV_bar=0):
    # initialize stored data
    # e_prev = 0
    # t_prev = 0
    # I = 0
    
    # initial control
    MV = MV_bar
    
    while True:
        # yield MV, wait for new t, PV, SP
        # t, PV, SP = yield MV
        PV, SP = yield MV
        
        # PID calculations
        e = SP - PV
        
        P = Kp*e
        # I = I + Ki*e*(t - t_prev)
        # D = Kd*(e - e_prev)/(t - t_prev)
        
        MV = MV_bar + P # + I + D
        
        # update stored data for next iteration
        # e_prev = e
        # t_prev = t


def delta_price(t, k=101, trials=10000):
    # Monte Carlo
    # gathering data
    tickers = t
    data = price_hist(tickers) # dict of dataframes

    # simulation
    price_paths = {}
    delta = {}

    for i in data.keys():
        log_return = np.log(1 + data[i].pct_change())
        
        u = log_return.mean()
        var = log_return.var()
        drift = u - (0.5*var)
        
        stdev = log_return.std()
        Z = norm.ppf(np.random.rand(k, trials)) # k, trials
        daily_returns = np.exp(drift.values + stdev.values * Z)
        
        price_paths[i] = np.zeros_like(daily_returns)
        price_paths[i][0] = data[i].iloc[-1]
        for t in range(1, k):
            price_paths[i][t] = price_paths[i][t-1]*daily_returns[t]
    
    # pricing assets
    for i in price_paths.keys():
        delta[i] = (sum(price_paths[i][100])/len(price_paths[i][100])) - price_paths[i][0][1]

    return delta