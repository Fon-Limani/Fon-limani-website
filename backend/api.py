import os

from database import Connection
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.responses import JSONResponse



load_dotenv()

# Will be updated
methods =\
"""
<center><h2>Methods</h2></center>
<hr>

| **Server**                               | **Funds**                                     | **Users**                                    | **User Portfolios**                                    | **News**                                    | **Messages**                                    |
|:----------------------------------------:|:---------------------------------------------:|:--------------------------------------------:|:------------------------------------------------------:|:-------------------------------------------:|:-----------------------------------------------:|
| [GET] &emsp;&emsp;&emsp; server_status   | [POST] &emsp;&emsp;&nbsp;     add_fund        | [POST] &emsp;&emsp;&nbsp;    add_user        | [POST] &emsp;&emsp;&nbsp;    add_user_portfolio        | [POST] &emsp;&emsp;&nbsp;    add_news       | [POST] &emsp;&emsp;&nbsp;    add_message        |
| ‎                                 | [GET] &emsp;&emsp;&emsp;      get_fund        | [GET] &emsp;&emsp;&emsp;     get_user        | [GET] &emsp;&emsp;&emsp;     get_user_portfolio        | [GET] &emsp;&emsp;&emsp;     get_news       | [GET] &emsp;&emsp;&emsp;     get_message        |
| ‎                                 | [GET] &emsp;&emsp;&emsp;      get_all_funds   | [GET] &emsp;&emsp;&emsp;     get_all_users   | [GET] &emsp;&emsp;&emsp;     get_all_user_portfolios   | [GET] &emsp;&emsp;&emsp;     get_all_news   | [GET] &emsp;&emsp;&emsp;     get_all_messages   |
| ‎                                 | [PUT] &emsp;&emsp;&emsp;      update_fund     | [PUT] &emsp;&emsp;&emsp;     update_user     | [PUT] &emsp;&emsp;&emsp;     update_user_portfolio     | [PUT] &emsp;&emsp;&emsp;     update_news    | [PUT] &emsp;&emsp;&emsp;     update_message     |
| ‎                                 | [DELETE] &emsp; delete_fund                   | [DELETE] &emsp;  delete_user                 | [DELETE] &emsp;  delete_user_portfolio                 | [DELETE] &emsp;  delete_news                | [DELETE] &emsp;  delete_message                 |
"""

app = FastAPI(title="Fon Limanı",
              version="0.1",
              description=f"Fon Limanı Application Programming Interface\n{methods}",
              openapi_url="/docs.json",
              docs_url= "/",
              swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"})

db = Connection(uri = os.getenv("MONGO_URI"))

API_KEY = os.getenv("API_KEY")

def verify_api_key(api_key: str = Header(..., convert_underscores=False)):
    # Check if the provided API key is valid (replace with your validation logic)
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return api_key


@app.get("/server_status", tags=["Server"])
def server_status(api_key: str = Depends(verify_api_key)):
    return {"message": "Up and Running"}


# FUNDS
@app.post("/funds/add_fund", tags=["Funds"])
async def add_fund(history, fund_code, fund_name, price, number_of_shares_in_circulation, num_investors, fund_total_value, api_key: str = Depends(verify_api_key)):
    result = db.add_fund(history, fund_code, fund_name, price, number_of_shares_in_circulation, num_investors, fund_total_value)
    if result:
        return result
    else:
        raise HTTPException(status_code=500, detail="Failed to add fund")


@app.get("/funds/get_fund", tags=["Funds"])
async def get_fund(value, by: str = "_id", api_key: str = Depends(verify_api_key)):
    if by == "_id":
        value = int(value)
    result = db.get_fund(by=by, value=value)
    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail="Fund not found")
    
@app.get("/funds/get_fund_information", tags=["Funds"])
async def get_fund_information(value, by: str = "_id", api_key: str = Depends(verify_api_key)):
    if by == "_id":
        value = int(value)
    result = db.get_fund_information(by=by, value=value)
    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail="Fund not found")
    
@app.get("/funds/get_all_fund_informations", tags=["Funds"])
async def get_all_fund_informations(api_key: str = Depends(verify_api_key)):
    result = db.get_all_fund_informations()
    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail="Fund not found")
    
@app.get("/get_monthly_tufe", tags=["Funds"])
async def get_monthly_tufe(api_key: str = Depends(verify_api_key)):
    result = db.get_monthly_tufe()
    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail="Fund not found")
    
@app.get("/funds/get_all_funds_detailed", tags=["Funds"])
async def get_all_funds_detailed(api_key: str = Depends(verify_api_key)):
    result = db.get_all_funds_detailed()
    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail="Fund not found")
    
@app.get("/funds/get_fund_detailed", tags=["Funds"])
async def get_fund_detailed(value, by: str = "_id", api_key: str = Depends(verify_api_key)):
    if by == "_id":
        value = int(value)
    result = db.get_fund_detailed(by=by, value=value)
    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail="Fund not found")
    
@app.get("/funds/get_candlestick_data", tags=["Funds"])
async def get_candlestick_data(value, by: str = "_id", api_key: str = Depends(verify_api_key)):
    if by == "_id":
        value = int(value)
    result = db.get_candlestick_data(by=by, value=value)
    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail="Fund not found")
    
@app.get("/funds/get_today_data", tags=["Funds"])
async def get_today_data(value="", by="_id", api_key: str = Depends(verify_api_key)):
    if value != "":
        if by == "_id":
            value = int(value)
        elif by == "user_id":
            value = int(value)
    result = db.get_today_data(value=value, by=by)
    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail="Fund not found")
    
@app.get("/funds/get_day_data", tags=["Funds"])
async def get_day_data(history, value="", by="_id", api_key: str = Depends(verify_api_key)):
    if value != "":
        if by == "_id":
           value = int(value)
        elif by == "user_id":
            value = int(value)
    result = db.get_day_data(history, value=value, by=by)
    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail="Fund not found")
    
@app.get("/funds/get_one_month_ago_data", tags=["Funds"])
async def get_one_month_ago_data(value="", by="_id", api_key: str = Depends(verify_api_key)):
    if value != "":
        if by == "_id":
            value = int(value)
        elif by == "user_id":
            value = int(value)
    result = db.get_one_month_ago_data(value=value, by=by)
    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail="Fund not found")
    
@app.get("/funds/get_last_week_data", tags=["Funds"])
async def get_last_week_data(value="", by="_id", api_key: str = Depends(verify_api_key)):
    result = db.get_last_week_data(value=value, by=by)
    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail="Fund not found")
    
@app.get("/funds/get_last_month_data", tags=["Funds"])
async def get_last_month_data(value="", by="_id", api_key: str = Depends(verify_api_key)):
    result = db.get_last_month_data(value=value, by=by)
    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail="Fund not found")


@app.get("/funds/get_all_funds", tags=["Funds"])
async def get_all_funds(value="", by="_id", api_key: str = Depends(verify_api_key)):
    return db.get_all_funds(value, by)


@app.get("/funds/get_filtered_fund", tags=["Funds"])
async def get_filtered_fund(text, api_key: str = Depends(verify_api_key)):
    return db.get_filtered_fund(text)


@app.get("/funds/get_all_reports", tags=["Funds"])
async def get_all_reports(api_key: str = Depends(verify_api_key)):
    return db.get_all_reports()


@app.get("/funds/get_last_n_reports", tags=["Funds"])
async def get_last_n_reports(n, api_key: str = Depends(verify_api_key)):
    n = int(n)
    return db.get_last_n_reports(n)


@app.put("/funds/update_fund/{fund_id}", tags=["Funds"])
async def update_fund(fund_id: int, update_data: dict, api_key: str = Depends(verify_api_key)):
    result = db.update_fund(fund_id, update_data)
    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail="Fund not found")


@app.delete("/funds/delete_fund/{fund_id}", tags=["Funds"])
async def delete_fund(fund_id: int, api_key: str = Depends(verify_api_key)):
    result = db.delete_fund(fund_id)
    return JSONResponse(content={"message": result})


# USERS


@app.post("/users/add_user", tags=["Users"])
async def add_user(username, password, email, name="", api_key:str = Depends(verify_api_key), verified=False, subscription=False, subscription_end_date=None, phone=""):

    result = db.add_user(name=name, username=username, password=password, email=email, verified=verified, subscription=subscription, subscription_end_date=subscription_end_date, phone=phone)
    if result:
        return result
    else:
        return HTTPException(status_code=500, detail="Failed to add user")


@app.get("/users/get_user", tags=["Users"])
async def get_user(value, by: str = "_id", api_key: str = Depends(verify_api_key)):
    if by == "_id":
        value = int(value)
    result = db.get_user(by=by, value=value)
    if result:
        return result
    else:
        return HTTPException(status_code=404, detail="User not found")

@app.get("/users/get_all_users", tags=["Users"])
async def get_all_users(api_key: str = Depends(verify_api_key)):
    return db.get_all_users()


@app.put("/users/update_user/{user_id}", tags=["Users"])
async def update_user(user_id: int, data: dict, api_key: str = Depends(verify_api_key)):
    result = db.update_user(user_id, data)
    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail="User not found")


@app.delete("/users/delete_user/{user_id}", tags=["Users"])
async def delete_user(user_id: int, api_key: str = Depends(verify_api_key)):
    result = db.delete_user(user_id)
    return JSONResponse(content={"message": result})


# AUTHENTICATION

@app.get("/users/login", tags=["Authentication"])
async def login(username: str, password: str, api_key: str = Depends(verify_api_key)):
    return db.validate_user(username, password)

# PORTFOLIOS

@app.get("/portfolios/get_portfolio", tags=["Portfolios"])
async def get_user_portfolio(value, by="_id", api_key: str = Depends(verify_api_key)):
    if by == "_id":
        value = int(value)

    result = db.get_portfolio(value=value, by=by)
    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail="Portfolio not found")

# USER PORTFOLIOS

@app.post("/user_portfolios/add_user_portfolio/{user_id}", tags=["User Portfolios"])
async def add_user_portfolio(fund, user_id, portion, api_key: str = Depends(verify_api_key)):
    result = db.add_user_portfolio(int(user_id), fund, int(portion))
    if result:
        return result
    else:
        raise HTTPException(status_code=500, detail="Failed to add user portfolio")


@app.get("/user_portfolios/get_user_portfolios", tags=["User Portfolios"])
async def get_user_portfolio(value, by="_id", api_key: str = Depends(verify_api_key)):
    if by == "_id":
        value = int(value)
    elif by == "user_id":
        value = int(value)

    result = db.get_user_portfolio(value=value, by=by)
    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail="User portfolio not found")


@app.get("/user_portfolios/get_all_user_portfolios", tags=["User Portfolios"])
async def get_all_user_portfolios(api_key: str = Depends(verify_api_key)):
    return db.get_all_user_portfolios()


@app.put("/user_portfolios/update_user_portfolio/{portfolio_id}", tags=["User Portfolios"])
async def update_user_portfolio(portfolio_id: int, update_data: dict, api_key: str = Depends(verify_api_key)):
    if "hold_numbers" in update_data:
        update_data["hold_numbers"][-1] = int(update_data["hold_numbers"][-1])
    result = db.update_user_portfolio(portfolio_id, update_data)
    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail="User portfolio not found")


@app.delete("/user_portfolios/delete_user_portfolio/{portfolio_id}", tags=["User Portfolios"])
async def delete_user_portfolio(portfolio_id: int, api_key: str = Depends(verify_api_key)):
    result = db.delete_user_portfolio(portfolio_id)
    return JSONResponse(content={"message": result})


# NEWS


@app.post("/news/add_news", tags=["News"])
async def add_news(news_information, news_link, api_key: str = Depends(verify_api_key)):
    result = db.add_news(news_information, news_link)
    if result:
        return result
    else:
        raise HTTPException(status_code=500, detail="Failed to add news")


@app.get("/news/get_news/{news_id}", tags=["News"])
async def get_news(news_id: int, api_key: str = Depends(verify_api_key)):
    result = db.get_news(news_id)
    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail="News not found")


@app.get("/news/get_all_news", tags=["News"])
async def get_all_news(api_key: str = Depends(verify_api_key)):
    return db.get_all_news()

@app.get("/news/get_last_n_news", tags=["News"])
async def get_last_n_news(n, api_key: str = Depends(verify_api_key)):
    n = int(n)
    return db.get_last_n_news(n)

@app.put("/news/update_news/{news_id}", tags=["News"])
async def update_news(news_id: int, update_data: dict, api_key: str = Depends(verify_api_key)):
    result = db.update_news(news_id, update_data)
    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail="News not found")


@app.delete("/news/delete_news/{news_id}", tags=["News"])
async def delete_news(news_id: int, api_key: str = Depends(verify_api_key)):
    result = db.delete_news(news_id)
    return JSONResponse(content={"message": result})


# MESSAGES

@app.post("/messages/add_message", tags=["Messages"])
async def add_message(title, body, email, api_key: str = Depends(verify_api_key)):
    result = db.add_message(title, body, email)
    if result:
        return result
    else:
        raise HTTPException(status_code=500, detail="Failed to add message")


@app.get("/messages/get_message/{message_id}", tags=["Messages"])
async def get_message(message_id: int, api_key: str = Depends(verify_api_key)):
    result = db.get_message(message_id)
    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail="Message not found")


@app.get("/messages/get_all_messages", tags=["Messages"])
async def get_all_messages(api_key: str = Depends(verify_api_key)):
    return db.get_all_messages()


@app.put("/messages/update_message/{message_id}", tags=["Messages"])
async def update_message(message_id: int, update_data: dict, api_key: str = Depends(verify_api_key)):
    result = db.update_message(message_id, update_data)
    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail="Message not found")


@app.delete("/messages/delete_message/{message_id}", tags=["Messages"])
async def delete_message(message_id: int, api_key: str = Depends(verify_api_key)):
    result = db.delete_message(message_id)
    return JSONResponse(content={"message": result})

# TOKENS

@app.post("/token/add_token", tags=["Tokens"])
async def add_message(user_id, token, api_key: str = Depends(verify_api_key)):
    result = db.add_token(int(user_id), token)
    if result:
        return result
    else:
        raise HTTPException(status_code=500, detail="Failed to add token")
    
@app.get("/token/get_token", tags=["Tokens"])
async def get_token(value: str, by: str = "_id", api_key: str = Depends(verify_api_key)):
    result = db.get_token(by=by, value=value)
    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail="Token not found")
    
# CODES

@app.post("/codes/add_code", tags=["Codes"])
async def add_message(user_id, code, api_key: str = Depends(verify_api_key)):
    result = db.add_code(user_id, code)
    if result:
        return result
    else:
        raise HTTPException(status_code=500, detail="Failed to add code")
    
@app.get("/codes/get_code", tags=["Codes"])
async def get_code(value: str, by: str = "_id", api_key: str = Depends(verify_api_key)):
    result = db.get_code(by=by, value=value)
    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail="Code not found")
    
@app.get("/get_counts", tags=["Counts"])
async def get_counts(api_key: str = Depends(verify_api_key)):
    result = db.get_counts()
    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail="Counts not found")
    
@app.put("/update_counts", tags=["Counts"])
async def update_counts(update_data: dict, api_key: str = Depends(verify_api_key)):
    result = db.update_counts(update_data=update_data)
    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail="Counts not found")

@app.post("/initialize_counts", tags=["Counts"])
async def initialize_counts(api_key: str = Depends(verify_api_key)):
    result = db.initialize_counts()
    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail="Count error")
