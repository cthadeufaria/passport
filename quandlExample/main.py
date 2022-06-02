"""
Hello, Christopher.
Please find below information regarding the chart ideas sent by you.
To make sure the first versions will be as correct as possible, would you review the data sources listed for each chart?
Note that all data comes from free sources. If you have access to paid data sources that you could share, it'd be good for the project productivity and final price.
Also, on some cases, the "Q" mark indicates a specific question about the chart or data needed. It'd be great if you could help clarifying them.
Regarding the delivery of the charts: after the data sources have been approved by you, I can start working on them effectively and deliver as many as possible until the weekend. I believe all of them are feasible by the next week if the data sources are right by the weekend.


1. Global dollar supply growth (US M0 + Foreign ownership of US treasuries YoY growth) overlay with TWDI (adv. and EM economies)
    1. US M0: https://fred.stlouisfed.org/series/BOGMBASE
    2. Foreign ownership of US treasuries: https://fred.stlouisfed.org/series/FDHBFIN / Q: Data on quarterly basis. Is it enough for this purpose?
    3. TWDI (adv. and EM economies): Q: What does it mean? Would you specify and/or give an example?

2. 1y, 5y, 10y US inflation swaps
    1. 1Y: https://fred.stlouisfed.org/series/ICERATES1100USD1Y
    2. 5Y: https://fred.stlouisfed.org/series/ICERATES1100USD5Y
    3. 10Y: https://fred.stlouisfed.org/series/ICERATES1100USD10Y

3. 1y, 5y, 10y inflation breakevens overlaid with 1y, 5y, 10y real yields
    1. Inflation Breakeven:
        1.1. 1Y: Q: 1Y data not available. Available only 5Y, 7Y, 10Y, 20Y, 30Y. Is any of the available data enough for this puspose? Is there a known data source? Is there a proxy?
        1.2. 5Y: https://fred.stlouisfed.org/series/T5YIE
        1.3. 10Y: https://fred.stlouisfed.org/series/T10YIE
    2. Real Yields:
        2.1. 1Y: https://fred.stlouisfed.org/series/REAINTRATREARAT1YE
        2.2. 5Y: Q: 5Y data not available. Available only 1Y, 10Y. Is the available data enough for this purpose? Is there a known data source? Is there a proxy? 
        2.3. 10Y: https://fred.stlouisfed.org/series/REAINTRATREARAT10Y

4. US linkers (TIPS) overlay inflation breakevens and 5y forward breakevens (attached a example chart)
    1. 5Y TIPS: https://fred.stlouisfed.org/series/DFII5
    2. 5Y Forward Breakeven: https://fred.stlouisfed.org/series/T5YIFR

5. Correlation dot plot of US linkers (TIPS) performance and US headline CPI YoY (i.e. is it beneficial to hold TIPS through maturity or are they a short term hedge)
    1. 5Y TIPS: https://fred.stlouisfed.org/series/DFII5
    2. US Headline CPI: https://fred.stlouisfed.org/series/CPIAUCSL

6. German 2y inflation swap overlay with German 2y bund yield
    1. 2Y inflation SWAP: Q: Data not found. Is there a known data source?
    2. 2Y bund yield: Q: Data not found. Is there a known data source?

7. Brazil CPI IPCA YoY overlay BRLUSD exchange rate (sample chart attached)
    1. Brazil CPI: https://fred.stlouisfed.org/series/BRACPIALLMINMEI
    2. BRLUSD: https://fred.stlouisfed.org/series/DEXBZUS

8. US Dollar liquidity guage - I'm not sure exactly how to go about this, so maybe you can help. I want to use chart #1 but include US reverse repo (RRP), since increasing RRP takes dollars out of the financial system liquidity is less available. In chart one, increasing M0 + Foreign US tsy holdings indicate favorable liquidity.
    1. Chart #1 info
    2. US Reverse Repurchase (RRP): https://fred.stlouisfed.org/series/RRPONTSYD

9. Historical performance of silver during rising and declining US real yield regimes
    1. Price of Silver: https://fred.stlouisfed.org/series/SLVPRUSD
    2. US real yield regimes data: https://fred.stlouisfed.org/series/REAINTRATREARAT1MO

10. Quad chart with growth/inflation regimes YoY and bitcoin's performance. 
- Growth accelerating/Inflation declerating
- Growth/Inflation accelerating
- Growth decleraring/inflation accelerating
- Growth/inflation decelerating.
    1. BTC/USD: https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_DAILY&symbol=BTC&market=USD&apikey=32DY46KZ3UOT9EU3
    2. Growth measure: https://fred.stlouisfed.org/series/GDPC1
    3. Inflation measure: https://fred.stlouisfed.org/series/FPCPITOTLZGUSA
"""

from tools import reporting as rpt
from tools import dataHandler as hdl

if __name__ == "__main__":
    mainReport = rpt.Report(0, 0, 0)
    mainReport.prettyTable()