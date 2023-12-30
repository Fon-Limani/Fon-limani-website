from prophet import Prophet
from prophet.plot import add_changepoints_to_plot, plot_cross_validation_metric
from prophet.diagnostics import cross_validation, performance_metrics

import plotly.express as px
import plotly.graph_objs as go

import pandas as pd

"""
Preprocess daily fund prices data according to the selected fund

Parameters:
df = dataset from Mongo or csv -- NEEDS to be configured
fundCode = fund code ex. "AFT"

Return:
dfFundProphet = pd.DataFrame()
"""
def preprocessDataset(df, fundCode):
    if df.isnull().sum().sum() == 0:
        # written only for funds_daily data.
        # Portfolio data needs more preprocessing!
        dfFund = df.convert_dtypes()
        
        # filter df according to fundCode 
        dfFund = dfFund[dfFund.fund_code == fundCode].drop(columns=["fund_name", "fund_code", "_id","timestamp"])
        
        # create a new df for prophet and rename columns (obligatory for prophet)
        dfFundProphet = dfFund[["history","price"]].copy().rename(columns={"history": 'ds', "price": 'y'})
        
        # use datetime[ns] type for ds column
        dfFundProphet.ds = dfFundProphet.ds.astype("datetime64[ns]")

        # use float64 type for y column
        dfFundProphet.y = dfFundProphet.y.astype("float64")
        
        return dfFundProphet
    else:
        print("There are missing values!")
        return 1
    
"""
Analyse fund's trend

Parameters:
dfFunds = preprocessed version of fon_limani.funds_daily
fundCode = fund code ex. "AFT"
"""
def predictFund(dfFunds, days):
    
    # split prophet df into train and test
    dfTrain = dfFunds[dfFunds['ds'] <= '2023-12-15']
    
    # Train
    m = Prophet(interval_width=0.95)
    m.fit(dfTrain)

    # Create a future dataframe for prediction
    future = m.make_future_dataframe(periods=days, freq='D') # same day lenght as dfTest

    # Forecast the future dataframe values 
    forecast = m.predict(future)

    return forecast, m

"""
# Example usage
dfFunds = pd.read_csv("funds_daily.csv")
df = preprocessDataset(dfFunds, "AFT")

## INPUT ALINACAK
# user input = 2024-12-17
user = '2024-12-17'
start = pd.to_datetime('2023-12-18')# 15 aralik cuma. ilik is gunu 18 aralik 2023 pzt!
end = pd.to_datetime(user)
daysToPredict = len(pd.bdate_range(start,end))


dfFundTest = pd.DataFrame()
dfFundTest["ds"] = pd.bdate_range(start,end)
dfFundTest["y"] = 0

dfFundPro = pd.concat([df, dfFundTest]).reset_index()

dfForecast, prophet = predictFund(dfFundPro, daysToPredict)


# RESIM 1
fig = prophet.plot(dfForecast)
ax = fig.gca()

# RESIM 2
prophet.plot_components(dfForecast, weekly_start=1)
"""