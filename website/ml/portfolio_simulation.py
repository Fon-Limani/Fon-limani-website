import pandas as pd
import numpy as np
import plotly.graph_objects as go

def visualize_fund_units(fundCodes, initial_prices, last_prices, fund_units):
    fig = go.Figure()

    # Add bar for initial unit prices
    fig.add_trace(go.Bar(x=fundCodes, y=initial_prices, name='Başlangıç Birim Fiyatları', marker_color='blue'))

    # Add bar for last unit prices
    fig.add_trace(go.Bar(x=fundCodes, y=last_prices, name='Son Birim Fiyatları', marker_color='green'))

    # Create a second y-axis for fund units
    fig.update_layout(yaxis2=dict(title='Fon Birimleri', overlaying='y', side='right'))
    
    # Add line plot for fund units on the second y-axis
    fig.add_trace(go.Scatter(x=fundCodes, y=fund_units, mode='lines+markers', name='Fon Birimleri', line=dict(color='orange', width=2), yaxis='y2'))

    # Update layout
    fig.update_layout(
        title='Başlangıç ve Son Birim Fiyatları ile Fon Birimlerinin Karşılaştırılması',
        xaxis_title='Fon Kodları',
        yaxis_title='Birim Fiyatları (TL)',
        margin=dict(l=0, r=0, b=0, t=40),
        barmode='group',  # 'group' for grouped bar chart
    )

    return fig


def visualize_comparison_of_capital(initial_value, total_capital_with_investment, total_capital_without_investment):
    fig = go.Figure()

    # Add bar for initial capital
    fig.add_trace(go.Bar(x=['Initial Capital'], y=[initial_value], name='Başlangıç Sermayesi', marker_color='blue'))

    # Add bar for total capital with investment
    fig.add_trace(go.Bar(x=['Total Capital (with Investment)'], y=[total_capital_with_investment], name='Toplam Sermaye (Yatırım Dahil)', marker_color='green'))

    # Add bar for total capital without investment
    fig.add_trace(go.Bar(x=['Total Capital (without Investment)'], y=[total_capital_without_investment], name='Toplam Sermaye (Yatırımsız - Bugünkü Alım Gücü)', marker_color='orange'))

    # Update layout
    fig.update_layout(
        title='Başlangıç ve Toplam Sermayenin Karşılaştırılması',
        xaxis_title='Sermaye Türü',
        yaxis_title='Tutar (TL)',
        margin=dict(l=0, r=0, b=0, t=40),
    )

    return fig

def visualize_combined_chart(fundCodes, fund_allocations, final_fund_values):
    fig = go.Figure()

    # Add bar for fund allocations
    fig.add_trace(go.Bar(x=fundCodes, y=fund_allocations, name='Fon Tahsisleri', marker_color='blue'))

    # Add bar for final fund values
    fig.add_trace(go.Bar(x=fundCodes, y=final_fund_values, name='Nihai Fon Değerleri', marker_color='orange'))

    # Update layout
    fig.update_layout(
        barmode='group',  # 'group' for grouped bar chart
        title='Birleşik Fon Tahsisleri ve Nihai Fon Değerleri',
        xaxis_title='Fon Kodları',
        yaxis_title='Tutar (TL)',
        margin=dict(l=0, r=0, b=0, t=40),
    )

    return fig

def visualize_contribution_to_total_capital(fundCodes, final_fund_values):
    fig = go.Figure(go.Pie(labels=fundCodes, values=final_fund_values, textinfo='percent+label', hole=0.3))
    fig.update_layout(title='Fonların Toplam Sermayeye Katkısı', margin=dict(l=0, r=0, b=0, t=40))
    return fig



def portfoy_sim(capital, fundList, start_date, df_funds, df_tufe_monthly):
    fundCodes = fundList[0]
    fundPct = fundList[1]

    if sum(fundPct) != 100:
        raise Exception("Yüzdeler 100'e eşit olmalıdır")
    else:
        df_funds.history = pd.to_datetime(df_funds.history)
        df_fund = df_funds[(df_funds.fund_code.isin(fundCodes)) & (df_funds.history >= pd.to_datetime(start_date))]
        
        df_tufe_monthly.month_year = pd.to_datetime(df_tufe_monthly.month_year)
        inflation_data = df_tufe_monthly[df_tufe_monthly['month_year'] >= pd.to_datetime("01." + start_date.split(".", maxsplit=1)[1])]
        
        cumulative_inflation = 100
        for tufe in df_tufe_monthly.tufe:
            cumulative_inflation += (tufe*cumulative_inflation/100)

        # Part1: Calculate how much money's value changes if the capital was never
        # used from the start_date until now. Return the real value of the capital and
        # the percentage of the change (indicate with - or + for loss or win)
        initial_value = capital
        final_value = initial_value * cumulative_inflation/100

        final = (initial_value * initial_value) / final_value
        change_percentage = ((final - initial_value) / initial_value) * 100

        print("\nKümülatif enflasyon:", cumulative_inflation)
        print(f"Başlangıç Sermayesi: {initial_value:.2f} TL")
        print(f"Nihai Sermaye (Kümülatif Enflasyonla Birlikte): {final:.2f} TL")
        print(f"Yüzdelik Değişimi: {'+' if change_percentage >= 0 else '-'}{abs(change_percentage):.2f}%\n")

        # Part2: Calculate the real value of the capital considering the fund investments

        total_capital = 0
        fund_allocations= []
        latest_fund_prices = []
        final_fund_values = []
        fund_units = []
        initial_fund_prices = []
        for code, pct in zip(fundCodes, fundPct):
            print(f"Fon Kodu: {code}")
            # Example: Get the relevant rows from df_fund for the specific fund code
            df_fund_single = df_fund[df_fund['fund_code'] == code]

            # Calculate the initial fund amount based on the given percentage
            fund_allocation = initial_value * (pct / 100)
            fund_allocations.append(fund_allocation)

            # Find the number of fund units (integer value) based on the starting day's fund price
            
            initial_fund_price = df_fund_single[df_fund_single['history'] == pd.to_datetime(start_date)]['price'].values[0]
            initial_fund_prices.append(initial_fund_price)
            print(f"Başlangıç Fon Fiyatı: {initial_fund_price}")
            
            fund_unit = fund_allocation // initial_fund_price
            fund_units.append(fund_unit)
            
            # Get the latest fund price for the specific fund
            latest_fund_price = df_fund_single.iloc[-1]['price']
            latest_fund_prices.append(latest_fund_price)

            # Calculate the final value of the fund investment
            final_fund_value = fund_unit * latest_fund_price
            final_fund_values.append(final_fund_value)
            
            print(f"Başlangıç Sermayesi Paylaşımı: {fund_allocation:.2f} TL")
            print(f"Başlangıç Fon Birimleri: {fund_unit}")
            print(f"Son Fon Fiyatı: {latest_fund_price:.6f} TL")
            print(f"Nihai Fon Değeri: {final_fund_value:.2f} TL")

            total_capital += final_fund_value
        
        print(f"Nihai Sermaye (Fon Tatırımı İle): {total_capital} TL")

        change_percentage2 = ((total_capital - initial_value) / initial_value) * 100
        print(f"Yüzdelik Değişimi: {'+' if change_percentage2>= 0 else '-'}{abs(change_percentage2):.2f}%\n")
        # Call the visualization function with your data
        return initial_value, final, fundCodes, fund_allocations, initial_fund_prices, fund_units, latest_fund_prices, final_fund_values, total_capital


"""
# Example usage
dfFunds = pd.read_csv("../model/funds_daily.csv")
dfTufe = pd.read_csv("tufe-aylik.csv")
dfInfo = pd.read_excel("../model/funds_information2.xlsx")

capital = 100000  # TL
fundList = [['AFT', 15], ['DVT', 12], ['YAY', 73]]  # Total percentage should be 100
start_date = '19.10.2022'

# Run your portfoy_sim function
initial_value, final, fundCodes, fund_allocations, initial_fund_prices, fund_units, latest_fund_prices, final_fund_values, total_capital = portfoy_sim(capital, fundList, start_date, dfInfo, dfFunds, dfTufe)
visualize_contribution_to_total_capital(fundCodes, final_fund_values)
visualize_combined_chart(fundCodes, fund_allocations, final_fund_values)
visualize_fund_units(fundCodes, initial_fund_prices, latest_fund_prices, fund_units)
visualize_comparison_of_capital(initial_value, final, total_capital)

"""