import base64
import json
import numpy as np
import os
import pandas as pd
import plotly
import plotly.express as px
import plotly.graph_objects as go
import random
import requests
import secrets

import matplotlib
matplotlib.use('Agg')

from dotenv import load_dotenv
from flask import render_template, redirect, url_for, session, request, jsonify, flash
from flask_mail import Message
from numpy import radians, cos, sin
from io import BytesIO
from requests.exceptions import RequestException
from frontend import app, google, mail

from ml.trend_analysis import predictFund
from ml.portfolio_simulation import portfoy_sim, visualize_fund_units, visualize_contribution_to_total_capital, visualize_combined_chart, visualize_comparison_of_capital



load_dotenv()

API_KEY = os.getenv("API_KEY")

def verification_code_message(name, verification_code):
    return f"""
<body>
    <div style="padding: 20px;">
        <h2>Kullanıcı Kaydı Doğrulama Kodu</h2>
        <p>Merhaba {name},</p>
        <p>Hesabınızı başarıyla oluşturdunuz. Şimdi, hesabınızı etkinleştirmek için aşağıdaki 6 haneli doğrulama kodunu kullanmanız gerekiyor:</p>
        <div style="text-align: center">
            <p style="font-size: 24px; font-weight: bold;">Doğrulama Kodu: <span style="color: #1039a5;">{verification_code}</span></p>
        </div>
        <p>Lütfen bu kodu giriş yaparken kullanarak hesabınızı tamamen etkinleştirin. Eğer bu işlemi siz yapmadıysanız veya hesabınızı oluşturmadıysanız, bu e-postayı dikkate almayınız.</p>
        <p>Hesabınızı güvende tutmak için bu kodu kimseyle paylaşmayın.</p>
        <p>İyi günler dileriz</p>
    </div>
    <div style="margin-top: 20px; display: flex; flex-direction: row">
        <img src="https://lh3.googleusercontent.com/drive-viewer/AEYmBYSRaf_zK_eH69zxZKeN1jMBtAFNtAXO4717u_7wkKdhiiuLdvFISCykysjloMR4kmfxcY9UjSbw90svP3ukAoi6WC3H=w1912-h947" height="72" style="margin-right: 36px;">
        <div>
            <p>(+90) 212 227 4480</p>
            <p>Çırağan Caddesi No:36 34349 Ortaköy/İstanbul</p>
        </div>
    </div>
</body>
"""

def renew_password_message(name, password_reset_link):
    return f"""
<body>
    <div style="padding: 20px;">
        <h2>Şifre Yenileme İsteği</h2>
        <p>Merhaba {name}</p>
        <p>Şifre yenileme isteğiniz alınmıştır. Hesabınızın güvenliği için lütfen aşağıdaki bağlantıyı kullanarak yeni bir şifre belirleyin:</p>
        <div style="text-align: center;">
            <p><a href="{password_reset_link}">Şifre Yenileme Bağlantısı</a></p>
        </div>
        <p>Bağlantıyı tıklamıyorsanız, tarayıcınızın adres çubuğuna şu bağlantıyı yapıştırabilirsiniz: {password_reset_link}</p>
        <p>Bu işlemi siz yapmadıysanız veya şifre yenileme talebinde bulunmadıysanız, lütfen bu e-postayı dikkate almayınız.</p>
        <p>Şifrenizi güvende tutmak için bu bilgiyi kimseyle paylaşmayınız.</p>
        <p>İyi günler dileriz</p>
    </div>
    <div style="margin-top: 20px; display: flex; flex-direction: row">
        <img src="https://lh3.googleusercontent.com/drive-viewer/AEYmBYSRaf_zK_eH69zxZKeN1jMBtAFNtAXO4717u_7wkKdhiiuLdvFISCykysjloMR4kmfxcY9UjSbw90svP3ukAoi6WC3H=w1912-h947" height="72" style="margin-right: 36px;">
        <div>
            <p>(+90) 212 227 4480</p>
            <p>Çırağan Caddesi No:36 34349 Ortaköy/İstanbul</p>
        </div>
    </div>
</body>
"""

class APIRequestError(RequestException):
    pass

def api_call(endpoint, params=None, json=None, type="get"):
    # Specify the API endpoint URL
    api_url = f"http://backend:1111/{endpoint}"

    # Make a GET request to the API
    if type == "get":
        response = requests.get(api_url, headers={"api_key": API_KEY}, params=params, json=json)
    if type == "post":
        response = requests.post(api_url, headers={"api_key": API_KEY}, params=params, json=json)
    if type == "put":
        response = requests.put(api_url, headers={"api_key": API_KEY}, params=params, json=json)
    if type == "delete":
        response = requests.delete(api_url, headers={"api_key": API_KEY}, params=params, json=json)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse and use the response data (assuming it's in JSON format)
        data = response.json()
        return data
    else:
        # Print an error message if the request was not successful
        raise APIRequestError(f"Error: {response.status_code} - {response.text}")

api_call(endpoint="initialize_counts", type="post")

def generate_plot(chart_type, df="", x="x", y="y", width=None, height=None, title="", theme="light", text="text", *args, **kwargs):

    colors = ["#0F3375", "#1039a5", "#1557C0", "#196BDE", "#2382F7", "#4B9CF9", "#77B6FB", "#A4CEFC", "#CCE4FD", "#E8F3FE"]

    if chart_type == 'scatter':
        fig = px.scatter(df, x=x, y=y)
    elif chart_type == 'bar':
        fig = px.bar(df, x=x, y=y, title=title)
    elif chart_type == 'line':
        fig = px.line(df, x=x, y=y, title=title, width=width, height=height, *args, **kwargs)
    elif chart_type == 'pie':
        fig = go.Figure(data=[go.Pie(labels=df[x].values, values=df[y].values, hole=.7, marker_colors=colors[:len(df[x].values)])])
    elif chart_type == 'candlestick':
        fig = go.Figure(data=[go.Candlestick(x=df["history"], open=df["open"], high=df["high"], low=df["low"], close=df["close"])])

        fig['layout']['yaxis'].update(autorange = True)
        fig['layout']['xaxis'].update(autorange = True)

        earliest_date = df['history'].min()
        latest_date = df['history'].max()

        fig.update_xaxes(type="date", range=[earliest_date, latest_date], showgrid=True, gridwidth=.25, gridcolor="#889cd2", showline=True, linewidth=.25, linecolor="#889cd2", mirror=True)
        fig.update_yaxes(showgrid=True, gridwidth=.25, gridcolor="#889cd2", showline=True, linewidth=.25, linecolor="#889cd2", mirror=True)
    elif chart_type == "gauge":
        fig = go.Figure(go.Indicator(
            domain = {'x': [0, 1], 'y': [0, 1]},
            value = int(x),
            mode = "gauge",
            title = {'text': f"Risk Değeri: {x}"},
            gauge = {'axis': {'range': [.5, 7.5], 'tickwidth': 1, 'tickmode':"array", 'tickvals':[1,2,3,4,5,6,7]},
                    'bar': { 'thickness': 0 },
                    'steps' : [
                        {'range': [0.5, 1.5], 'color': "#2d7d00"},
                        {'range': [1.5, 2.5], 'color': "#5f9600"},
                        {'range': [2.5, 3.5], 'color': "#afc611"},
                        {'range': [3.5, 4.5], 'color': "#f7dc00"},
                        {'range': [4.5, 5.5], 'color': "#f4af0a"},
                        {'range': [5.5, 6.5], 'color': "#e74404"},
                        {'range': [6.5, 7.5], 'color': "#b20811"}],
                    }
            )
        )

        fig.update_layout(
        font={'color': "black", 'family': "Arial"},
        xaxis={'showgrid': False, 'showticklabels':False, 'range':[-1,1]},
        yaxis={'showgrid': False, 'showticklabels':False, 'range':[0,1]},
        plot_bgcolor='rgba(0,0,0,0)'
        )
        theta = 22.5 * ( 8 - int(x))
        r= 0.75
        x_head = r * cos(radians(theta))
        y_head = r * sin(radians(theta))

        fig.add_annotation(
            ax=0,
            ay=0.2,
            axref='x',
            ayref='y',
            x=x_head,
            y=y_head,
            xref='x',
            yref='y',
            showarrow=True,
            arrowhead=3,
            arrowsize=1,
            arrowwidth=4,
            arrowcolor = "black"
            )
    else:
        raise ValueError(f"Unsupported chart type: {chart_type}")

    if theme=="dark":
        if chart_type == 'line':
            fig.update_traces(line_color='#ffffff')
        elif chart_type == 'bar':    
            fig.update_traces(marker_color='#1039A5')
        elif chart_type == "pie":
            None

        fig.update_layout(plot_bgcolor='rgba(0, 0, 0, 0)', paper_bgcolor='rgba(0, 0, 0, 0)')

    if text=="notext":
        fig.update_layout(
        margin=dict(l=10, r=10, b=10, t=10),
        showlegend=False,  # Hide legend
        title_text='',  # Remove title
        xaxis_title='',  # Remove x-axis title
        yaxis_title='',  # Remove y-axis title
        xaxis_showgrid=False,  # Hide x-axis grid lines
        yaxis_showgrid=False,  # Hide y-axis grid lines
        xaxis_showticklabels=False,  # Hide x-axis tick labels
        yaxis_showticklabels=False,  # Hide y-axis tick labels
        )

    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

@app.route('/login', methods=["GET", "POST"])
def login():

    if "logged_in" in session:
        if session["logged_in"]:
            return redirect(url_for("main_panel"))

    if request.method == "POST":

        username = request.form['username']
        password = request.form['password']
        remember_me = request.form.get("remember_me", False)

        any_problem = False

        if username == "":
            any_problem = True
        if password == "":
            any_problem = True

        if any_problem:
            flash("Lütfen kullanıcı adı ve şifreyi boş bırakmayınız.")
            return redirect(url_for("login"))

        user = api_call("users/get_user", params={"by": "username", "value": username}, type="get")

        if "username" not in user.keys():
            any_problem = True
            flash("Kullanıcı adı geçersiz.")
            return redirect(url_for("login"))

        login = api_call(endpoint="users/login", params={"username": username, "password": password}, type="get")

        if login:
            user = api_call("users/get_user", params={"by": "username", "value": username})
            session["user_id"] = user["_id"]
            session["logged_in"] = True
            session["login_type"] = "email"
            session["remember_me"] = remember_me
            return redirect(url_for("main_panel"))
        else:
            flash("Kullanıcı adı ya da şifre yanlış!")
            return redirect(url_for("login"))

    return render_template('login.html')

@app.route('/register', methods=["GET", "POST"])
def register():

    if request.method == "POST":
        username = request.form['username']
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone']

        any_problem = False

        if username == "":
            any_problem = True
        if name == "":
            any_problem = True
        if email == "":
            any_problem = True
        if password == "":
            any_problem = True

        if any_problem:
            flash("Opsiyonel olmayan alanlar doldurulmak zorundadır.")

        username_data = api_call("users/get_user", params={"by": "username", "value": username}, type="get")

        email_data = api_call("users/get_user", params={"by": "email", "value": email}, type="get")

        if "username" in username_data.keys():
            if username_data["username"] == username:
                any_problem = True
                flash("Kullanıcı adı alınmış. Lütfen başka bir kullanıcı adı kullanın.")

        if "email" in email_data.keys():
            if email_data["email"] == email:
                any_problem = True
                flash("Bu e-posta adresi ile bir hesap mevcut. Lütfen başka bir e-posta adresi kullanın.")

        if not any_problem:

            user = api_call("users/add_user", params={"username": username, "name": name, "password": password, "email": email, "phone": phone, "verified": False}, type="post")

            session["user_id"] = user["_id"]
            session["logged_in"] = True
            session["login_type"] = "email"
            session["remember_me"] = False

            verification_code = random.randint(100000, 999999)

            message = Message(subject="Fon Limanı Doğrulama Kodu", sender="fonlimani@gmail.com", recipients=[email], html=verification_code_message(name=name, verification_code=verification_code))

            mail.send(message)

            api_call("codes/add_code", params={"user_id": user["_id"], "code": verification_code}, type="post")

            return redirect(url_for("sign_up"))

    return render_template('register.html')

@app.route('/sign_up', methods=["GET", "POST"])
def sign_up():
    try:
        if session["login_type"] == "gmail":
            if request.method == "POST":

                username = request.form.get('username')
                name = request.form.get('name')
                password = request.form.get('password')
                phone = request.form.get('phone')

                user = api_call("users/get_user", params={"by": "_id", "value": session["user_id"]})

                api_call(f"users/update_user/{user['_id']}", json={"username": username, "name": name, "password": password, "phone": phone}, type="put")

                return redirect(url_for("main_panel"))

            return render_template("sign_up_from_google.html")
        else:
            if request.method == "POST":

                six_digit_code = request.form.get('six_digit_code')

                user_code = api_call("codes/get_code", params={"by": "user_id", "value": session["user_id"]})

                user = api_call("users/get_user", params={"by": "_id", "value": session["user_id"]})

                if six_digit_code == user_code["code"]:
                    api_call(f"users/update_user/{user['_id']}", json={"verified": six_digit_code == user_code["code"]}, type="put")
                    return redirect(url_for("main_panel"))
                else:
                    flash("Girdiğiniz kod yanlış! Lütfen tekrar deneyiniz.")
                    return redirect(url_for('sign_up'))

            return render_template("sign_up.html")
    except:
        if "google_token" in session.keys():
            if request.method == "POST":
                username = request.form.get('username')
                name = request.form.get('name')
                password = request.form.get('password')
                phone = request.form.get('phone')

                user = api_call("users/get_user", params={"by": "_id", "value": session["user_id"]})

                api_call(f"users/update_user/{user['_id']}", json={"username": username, "name": name, "password": password, "phone": phone}, type="put")

            return redirect(url_for("main_panel"))
    return redirect(url_for("main_panel"))
    
@app.route('/login_action')
def login_action():
    return google.authorize(callback=url_for('authorized', _external=True))

@app.route('/register_action')
def register_action():
    return google.authorize(callback=url_for('r_authorized', _external=True))

@app.route('/login/authorized')
def authorized():
    response = google.authorized_response()
    if response is None or response.get('access_token') is None:
        return 'Login failed.'

    session['google_token'] = (response['access_token'], '')
    user = google.get('userinfo').data
    
    user_mail = user["email"]
    is_user_verified = bool(user["verified_email"])

    user = api_call("users/get_user", params={"by": "email", "value": user_mail})

    if "status_code" not in user.keys():
        session["user_id"] = user["_id"]
        session["logged_in"] = True
        session["login_type"] = "gmail"
        session["remember_me"] = False

        return redirect(url_for('main_panel'))
    else:
        user = api_call("users/add_user", params={"username":"", "password":"", "email": user_mail, "verified":is_user_verified}, type="post")
        session["user_id"] = user["_id"]
        session["logged_in"] = True
        session["login_type"] = "gmail"
        session["remember_me"] = False
        return redirect(url_for("sign_up"))

@app.route('/register/authorized')
def r_authorized():
    response = google.authorized_response()
    if response is None or response.get('access_token') is None:
        return 'Login failed.'

    session['google_token'] = (response['access_token'], '')
    user = google.get('userinfo').data
    
    user_mail = user["email"]
    is_user_verified = user["verified_email"]

    user = api_call("users/add_user", params={"username":"", "password":"", "email": user_mail, "verified":is_user_verified}, type="post")
    session["user_id"] = user["_id"]
    session["logged_in"] = True
    session["login_type"] = "gmail"
    session["remember_me"] = False

    return redirect(url_for("sign_up"))

@app.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    if request.method == 'POST':
        email = request.form.get('email')

        user = api_call("users/get_user", params={"by": "email", "value": email}, type="get")

        if "status_code" in user:
            flash("Böyle bir e-posta adresi mevcut değil!")

            return redirect(url_for("reset_password"))
        else:
            token = secrets.token_urlsafe(32)

            api_call(endpoint="token/add_token", params={"token": token, "user_id": int(user["_id"])}, type="post")

            reset_link = url_for('renew_password', token=token, _external=True)

            message = Message(subject="Şifre Yenileme", recipients=[email], sender="fonlimani@gmail.com", html=renew_password_message(user["name"], reset_link))

            mail.send(message)

            flash(f'Şifreniz sıfırlandı! E-posta adresinizi kontrol edin!')

            return redirect(url_for("reset_password"))
    
    return render_template('reset_password.html')

@app.route('/renew_password/<token>', methods=["GET", "POST"])
def renew_password(token):
    if request.method == 'POST':

        token = api_call("token/get_token", params={"by": "token", "value": token}, type="get")

        password = request.form.get('password')

        api_call(f"users/update_user/{token['user_id']}", type="put", json={"password": str(password)})

        flash(f'Şifreniz sıfırlandı! Yeniden giriş yapınız!')

        return redirect(url_for("login"))

    return render_template('renew_password.html', token=token)
       
@app.route('/logout')
def logout():
    if not session["remember_me"]:
        session.clear()
    else:
        session.pop("google_token", None)
    return redirect(url_for('index'))

@app.route('/profil')
def profil():
    try:
        if session["logged_in"]:
            user = api_call(f"users/get_user", params={"value": session['user_id']})
            username = user["username"]
            name = user["name"]
            organization = user["organization"]
            location = user["location"]
            email = user["email"]
            phone = user["phone"]
            birthday = user["birthday"]
            return render_template("profile.html", username=username, name=name, organization=organization, location=location, email=email, phone=phone, birthday=birthday)
        else:
            return redirect(url_for("login"))
    except:
        return redirect(url_for("login"))
    
@app.route('/ana_panel')
def main_panel():
    try:
        if session["logged_in"]:
            ######### EN ÇOK KAZANDIRANLAR #########

            today_df = pd.DataFrame(api_call(f"funds/get_today_data"))
            one_month_ago_df = pd.DataFrame(api_call(f"funds/get_one_month_ago_data"))

            today_df['history'] = pd.to_datetime(today_df['history'], format='%d.%m.%y')
            one_month_ago_df['history'] = pd.to_datetime(one_month_ago_df['history'], format='%d.%m.%y')

            today_df = today_df.sort_values(by='history', ascending=False)
            one_month_ago_df = one_month_ago_df.sort_values(by='history', ascending=False)

            today_df = today_df[['price', 'fund_code']]
            one_month_ago_df = one_month_ago_df[['price', 'fund_code']]

            kazandiran_df = pd.merge(today_df, one_month_ago_df, on='fund_code', suffixes=('_df1', '_df2'))

            kazandiran_df['percentage'] = (kazandiran_df['price_df1'] - kazandiran_df['price_df2']) / kazandiran_df['price_df2'] * 100

            kazandiran_df = kazandiran_df[['fund_code', 'percentage']]

            kazandiran_df = kazandiran_df.replace([np.inf, -np.inf], np.nan)
            kazandiran_df.dropna(subset=['percentage'], inplace=True)

            df_sorted_desc = kazandiran_df.sort_values(by="percentage", ascending=False)

            df_top_nine = df_sorted_desc[["fund_code", "percentage"]].head(9)

            column_mapping = {'percentage': 'Değişim', 'fund_code': 'Fon Kodu'}

            # Use the rename method to change the column names
            df_top_nine.rename(columns=column_mapping, inplace=True)

            top_nine_figure = generate_plot(chart_type="bar", df=df_top_nine, x="Fon Kodu", y="Değişim", theme="dark")

            fund_codes= list(df_top_nine['Fon Kodu'].values)

            ######### EN İYİ 9 GRAFİK #########

            top_nine = []
            top_nine_code_data = []
            top_nine_price_data = []

            for fund_code in fund_codes:
                fund = pd.DataFrame(api_call(endpoint=("funds/get_last_month_data"), params={"by": "fund_code", "value": fund_code}))
                fund = fund[fund['history'].str.strip() != '']
                fund['history'] = pd.to_datetime(fund['history'], format='%d.%m.%y')
                fund = fund.sort_values(by='history', ascending=False)
                column_mapping = {'history': 'Tarih', 'price': 'Fiyat'}
                fund.rename(columns=column_mapping, inplace=True)
                figure = generate_plot(chart_type="line", df=fund, x="Tarih", y="Fiyat", width=128, height=96, theme="dark", text="notext")
                top_nine.append(figure)
                top_nine_code_data.append(fund["fund_code"].iloc[-1])
                top_nine_price_data.append(fund["Fiyat"].iloc[-1])


            ######### PORTFÖYÜM #########

            try:
                pie_df = pd.DataFrame(api_call(f"user_portfolios/get_user_portfolios", params={"by": "user_id", "value": int(session["user_id"])} ))
                pie_df = pie_df[["holds", "hold_numbers"]]

                pie_df["fund_prices"] = [api_call(endpoint="funds/get_today_data", params={"by": "fund_code", "value": x})[0]["price"] for x in pie_df["holds"].values]

                pie_df['value'] = pie_df["fund_prices"] * pie_df['hold_numbers']

                value_sum = pie_df["value"].sum()

                pie_df["Yüzde"] = pie_df["value"] / value_sum * 100

                pie_df.sort_values(by="Yüzde", ascending=False)

                column_mapping = {'holds': 'Fon Kodu'}
                pie_df.rename(columns=column_mapping, inplace=True)

                pie_figure = generate_plot(chart_type="pie", df=pie_df, x="Fon Kodu", y="Yüzde", theme="dark")

                pie_data = pie_df.to_dict(orient="list")

                pie_data["sum"] = value_sum
            except:
                pie_figure = "404"
                pie_data = "404"

            ######### RAPORLAR #########

            reports = api_call("funds/get_last_n_reports", params={"n": 6})

            ######### HABERLER #########

            news = api_call("news/get_last_n_news", params={"n": 5})

            if 'google_token' in session:
                me = google.get('userinfo')
                return render_template('main_panel.html', reports=reports, news=news, top_nine_figure=top_nine_figure, pie_figure = pie_figure, pie_data=pie_data, top_nine=top_nine, top_nine_code_data=top_nine_code_data, top_nine_price_data=top_nine_price_data)
            elif 'user_id' in session:
                user = api_call("users/get_user", params={"by": "_id", "value": session["user_id"]})
                return render_template('main_panel.html', reports=reports, news=news, top_nine_figure=top_nine_figure, pie_figure = pie_figure, pie_data=pie_data, top_nine=top_nine, top_nine_code_data=top_nine_code_data, top_nine_price_data=top_nine_price_data)
        else:
            return redirect(url_for("login"))
    except:
        return redirect(url_for("login"))

@app.route("/fon/<kod>")
def fon_detay(kod):
    try:
        if session["logged_in"]:
            """
            default -> 1 months

            options

            3 months
            1 year
            3 years
            5 years
            """

            date = request.args.get('date', default="1")

            match date:
                case "1":
                    start_time ='2023-11-17'
                    end_time='2023-12-17'
                case "2":
                    start_time ='2023-9-17'
                    end_time='2023-12-17'
                case "3":
                    start_time ='2022-12-17'
                    end_time='2023-12-17'
                case "4":
                    start_time ='2020-12-17'
                    end_time='2023-12-17'
                case "5":
                    start_time ='2018-11-17'
                    end_time='2023-12-17'


            df = pd.DataFrame(api_call(f"funds/get_candlestick_data", params={"by": "fund_code", "value": kod}))

            df['history'] = pd.to_datetime(df['history'], format='%d.%m.%y')

            df = df.sort_values(by='history')

            df = df[(df['history'] > start_time) & (df['history'] < end_time)]

            df['close'] = df['price'].shift(-1)

            def subtract_random(row):
                mean = row["price"]
                close = row["close"]
                std_dev = mean/216
                random_value = np.random.normal(mean, std_dev)
                i = 0
                while (random_value > mean) or (random_value > close) and (i < 10):
                    random_value = np.random.normal(mean, std_dev)
                    i += 1

                if random_value > mean or random_value > close:
                    random_value = mean if mean < close else close
                
                return random_value
            
            def sum_random(row):
                mean = row["price"]
                close = row["close"]
                std_dev = mean/216
                random_value = np.random.normal(mean, std_dev)
                i = 0
                while (random_value < mean) or (random_value < close) and (i < 10):
                    random_value = np.random.normal(mean, std_dev)
                    i += 1

                if random_value < mean or random_value < close:
                    random_value = mean if mean > close else close
                return random_value
            
            df['low'] = df.apply(subtract_random, axis=1)
            df['high'] = df.apply(sum_random, axis=1)

            df = df.rename(columns={'price': 'open'})

            last_item = df.iloc[-1].to_dict()

            figure = generate_plot("candlestick", df = df, theme="dark")

            fund_information = api_call(f"funds/get_fund_information", params={"by": "fund_code", "value": kod})

            try:
                risk_graph = generate_plot("gauge", x=fund_information["risk_value"])
            except:
                risk_graph = None

            fund_portfolio = api_call(f"portfolios/get_portfolio", params={"by": "fund_code", "value": kod})["percentages"]

            portfolio_df = pd.DataFrame(list(fund_portfolio.items()), columns=['Pay', 'Yüzde'])

            portfolio_pie = generate_plot(chart_type="pie", df=portfolio_df, x="Pay", y="Yüzde")

            return render_template("fon_detay.html", figure=figure, fund_information=fund_information, daily_fund_information=last_item, risk_graph=risk_graph, portfolio_pie=portfolio_pie, fund_portfolio=fund_portfolio)
        else:
            return redirect(url_for("login"))
    except:
        return redirect(url_for("login"))

@app.route("/fon_ara")
def fon_ara():
    try:
        if session["logged_in"]:
            funds_data = api_call(f"funds/get_all_fund_informations")

            # Pagination parameters
            page = request.args.get('page', 1, type=int)
            per_page = 50
            total_pages = 29  # Set the total number of pages

            start_index = (page - 1) * per_page
            end_index = start_index + per_page
            paginated_funds = funds_data[start_index:end_index]
            
            for fund in paginated_funds:
                fund["fund_name"] = api_call(f"funds/get_fund_detailed", params={"by": "fund_code", "value": fund["fund_code"]})["fund_name"]

            return render_template("fon_ara.html", funds_data=paginated_funds, current_page=page, total_pages=total_pages)
        else:
            return redirect(url_for("login"))
    except:
        return redirect(url_for("login"))

@app.route('/search_funds', methods=['GET'])
def search_funds():
    try:
        if session["logged_in"]:
            text = request.args.get('text')

            try:
                data = api_call(endpoint="funds/get_filtered_fund", params={'text': text})
                return jsonify({'results': data})
            except APIRequestError as e:
                return jsonify({'error': str(e)})
        else:
            return redirect(url_for("login"))
    except:
        return redirect(url_for("login"))
    
@app.route('/trend_analizi', methods=['GET', 'POST'])
def trend_analizi():
    try:
        if session["logged_in"]:
            if request.method == 'POST':
                try:
                    fund_code = request.form.get("fund_code")
                    end_time = request.form.get("datetimePicker")
                    funds_data = pd.DataFrame(api_call(f"funds/get_all_funds", params={"by": "fund_code", "value": fund_code[:3]}))

                    df = funds_data[["history","price"]].copy().rename(columns={"history": 'ds', "price": 'y'})

                    df.ds = df.ds.astype("datetime64[ns]")

                    # use float64 type for y column
                    df.y = df.y.astype("float64")

                    start = pd.to_datetime('2023-12-18')# 15 aralik cuma. ilik is gunu 18 aralik 2023 pzt!
                    end = pd.to_datetime(end_time)
                    daysToPredict = len(pd.bdate_range(start,end))

                    dfFundTest = pd.DataFrame()
                    dfFundTest["ds"] = pd.bdate_range(start,end)
                    dfFundTest["y"] = 0

                    dfFundPro = pd.concat([df, dfFundTest]).reset_index()

                    dfForecast, prophet = predictFund(dfFundPro, daysToPredict)

                    # RESIM 1
                    figure_1 = prophet.plot(dfForecast)
                    ax = figure_1.gca()

                    # RESIM 2
                    figure_2 = prophet.plot_components(dfForecast, weekly_start=1)

                    forecasted_df = dfForecast.copy()

                    forecasted_df = forecasted_df[["ds", "trend"]]

                    forecasted_df['ds'] = pd.to_datetime(forecasted_df['ds'], format='%Y-%m-%d')

                    forecasted_df = forecasted_df.sort_values(by='ds', ascending=True)

                    forecasted_df = forecasted_df.tail(27)

                    forecasted_df.rename(columns={"ds": "Tarih", "trend": "Trend Fiyatı"}, inplace=True)

                    figure_base64s = []
                    for fig in [figure_1, figure_2]:
                        img_buffer = BytesIO()
                        fig.savefig(img_buffer, format='png')
                        img_buffer.seek(0)
                        img_base64 = base64.b64encode(img_buffer.read()).decode('utf-8')
                        figure_base64s.append(img_base64)

                    return render_template("trend_analizi.html", figures = figure_base64s, fund_code = fund_code, table=forecasted_df.to_html(classes='table table-bordered table-striped', index=False))
                except:
                    flash("Bir sorun oluştu! Lütfen daha sonra tekrar deneyin.")
                    return render_template("trend_analizi.html")
            
            return render_template("trend_analizi.html")
        else:
            return redirect(url_for("login"))
    except:
        return redirect(url_for("login"))

@app.route('/portfoyum', methods=['GET', 'POST'])
def portfoyum():
    try:
        if session["logged_in"]:
            try:
                data = api_call(f"user_portfolios/get_user_portfolios", params={"by": "user_id", "value": int(session["user_id"])} )
                portfolio_id = data["_id"]
            except:
                data = "404"
                portfolio_id = "404"

            if request.method == 'POST':
                fund_code = request.form.get("fund_code")
                share_number = request.form.get("fund_number")

                if not data == "404":

                    update_data = data.copy()

                    update_data["holds"].append(fund_code[:3])
                    update_data["hold_numbers"].append(share_number)

                    api_call(f"user_portfolios/update_user_portfolio/{portfolio_id}", json={"holds":update_data["holds"], "hold_numbers":update_data["hold_numbers"]}, type="put")

                else:
                    api_call(f"user_portfolios/add_user_portfolio/{session['user_id']}", params={"fund": fund_code[:3], "portion": share_number}, type="post")

                return redirect(url_for("portfoyum"))

            try:
                pie_df = pd.DataFrame(data)
                
                pie_df = pie_df[["holds", "hold_numbers"]]

                pie_df["fund_prices"] = [api_call(endpoint="funds/get_today_data", params={"by": "fund_code", "value": x})[0]["price"] for x in pie_df["holds"].values]

                pie_df['value'] = pie_df["fund_prices"] * pie_df['hold_numbers']

                value_sum = pie_df["value"].sum()

                pie_df["Yüzde"] = pie_df["value"] / value_sum * 100

                pie_df.sort_values(by="Yüzde", ascending=False)

                column_mapping = {'holds': 'Fon Kodu'}
                pie_df.rename(columns=column_mapping, inplace=True)

                pie_figure = generate_plot(chart_type="pie", df=pie_df, x="Fon Kodu", y="Yüzde", theme="dark")

                pie_data = pie_df.to_dict(orient="list")

                pie_data["sum"] = value_sum
            except Exception as e:
                pie_figure = "404"
                pie_data = "404"

            return render_template("portfoyum.html", pie_figure=pie_figure, pie_data=pie_data, portfolio_id=portfolio_id)
        else:
            return redirect(url_for("login"))
    except:
        return redirect(url_for("login"))

@app.route('/haberler', methods=['GET', 'POST'])
def haberler():
    try:
        if session["logged_in"]:
            news = api_call("news/get_all_news")
            return render_template("haberler.html", news=news)
        else:
            return redirect(url_for("login"))
    except:
        return redirect(url_for("login"))

@app.route('/portfoy_simulasyonu', methods=['GET', 'POST'])
def portfoy_simulasyonu():
    try:
        if session["logged_in"]:
            if request.method == 'POST':
                fund_code_1 = request.form.get("fund_code_1")
                fund_code_2 = request.form.get("fund_code_2")
                fund_code_3 = request.form.get("fund_code_3")

                fund_percantage_1 = request.form.get("fund_percantage_1")
                fund_percantage_2 = request.form.get("fund_percantage_2")
                fund_percantage_3 = request.form.get("fund_percantage_3")

                money = request.form.get("start_money")
                start_date = request.form.get("datetimePicker")

                fund_codes = [fund_code_1[:3], fund_code_2[:3], fund_code_3[:3]]

                fund_percantages = [int(fund_percantage_1), int(fund_percantage_2), int(fund_percantage_3)]

                fundList = [fund_codes, fund_percantages]
                
                datas = []

                edited_history = start_date[:-4] + start_date[-2:]

                for fund_code in fund_codes:
                    aax = api_call("funds/get_day_data", params={"history": edited_history, "value": fund_code, "by":"fund_code"})
                    aay = api_call("funds/get_today_data", params={"value": fund_code[:3], "by": "fund_code"})
                    datas.append(aax[0])
                    datas.append(aay[0])

                dfFunds = pd.DataFrame(datas)

                dfTufe = pd.DataFrame(api_call("get_monthly_tufe"))

                initial_value, final, fundCodes, fund_allocations, initial_fund_prices, fund_units, latest_fund_prices, final_fund_values, total_capital = portfoy_sim(int(money), fundList, start_date, dfFunds, dfTufe)

                try:
                    fig1 = visualize_contribution_to_total_capital(fundCodes, final_fund_values)
                    fig2 = visualize_combined_chart(fundCodes, fund_allocations, final_fund_values)
                    fig3 = visualize_fund_units(fundCodes, initial_fund_prices, latest_fund_prices, fund_units)
                    fig4 = visualize_comparison_of_capital(initial_value, total_capital, final)
                except Exception as e:
                    print(e)

                figures = [json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder), json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder), json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder), json.dumps(fig4, cls=plotly.utils.PlotlyJSONEncoder)]

                user_portfolio_df = pd.DataFrame(api_call(f"user_portfolios/get_user_portfolios", params={"by": "user_id", "value": int(session["user_id"])} ))
                user_portfolio_df = user_portfolio_df[["holds", "hold_numbers"]]

                dfs = []

                for fund_code in fund_codes:
                    fund = pd.DataFrame(api_call(endpoint=("funds/get_all_funds"), params={"by": "fund_code", "value": fund_code}))
                    fund = fund[fund['history'].str.strip() != '']
                    fund['history'] = pd.to_datetime(fund['history'], format='%d.%m.%y')
                    fund = fund.sort_values(by='history', ascending=False)
                    fund["Kod"] = fund_code
                    column_mapping = {'history': 'Tarih', 'price': f'Fiyat'}
                    fund.rename(columns=column_mapping, inplace=True)

                    fund = fund[["Kod", "Tarih", "Fiyat"]]

                    dfs.append(fund)

                merged_df = pd.concat(dfs)
                
                figure = generate_plot(chart_type="line", df=merged_df, x='Tarih', y='Fiyat', color='Kod', template='plotly_white', labels={'Fiyat': 'Fiyat', 'Tarih': 'Tarih'})

                return render_template("portfoy_simulasyonu.html", figure=figure, figures=figures)
            
            return render_template("portfoy_simulasyonu.html", figures = None, figure = None)
        else:
            return redirect(url_for("login"))
    except:
        return redirect(url_for("login"))

@app.route('/', methods=['GET', 'POST'])
def index():
    news = api_call("news/get_all_news")

    if request.method == 'POST':
        senderEmail = request.form.get("senderEmail")
        messageTitle = request.form.get("messageTitle")
        messageBody = request.form.get("messageBody")

        api_call("messages/add_message", params={"email":senderEmail, "title":messageTitle, "body":messageBody}, type="post")

        flash("Mesajınız başarıyla gönderildi!")
        return redirect(url_for('index', news=news))

    return render_template('index.html', news=news)

@app.route('/cerez_politikasi')
def cerez():
    return render_template('cookies.html')

@app.route('/gizlilik_ve_kvkk')
def secandkvvk():
    return render_template('sec_kvkk.html')

@app.errorhandler(400)
def bad_request(e):
    return render_template("400.html"), 400

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500

@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')