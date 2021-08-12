from handle_api import candlestick, price_hist, tickers_list

# Get price_hist
t = tickers_list()
# candlestick(t)

# Remove less liquid assets (smallest average trading volume)
# Remove highest betas assets
# Remove low momentum
    # Calculate intraday momentum (check for evidence)
    # Check for most relevant period to calculate momentum to predict return in 4 next hours (use correlation between imi and predicted return to look for best period?)
        # IMI
        # 
        
# Choose assets based on momentum quality (smoothest price path / frog in the pan)
# Use Markovitz to define proportions of assets in portfolio
    # how to estimate volatility?
    # how to estimate return?
