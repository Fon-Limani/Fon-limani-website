import pymongo
import os

from datetime import datetime, timedelta
from dotenv import load_dotenv
from encryption import PasswordEncryptor

load_dotenv()

class Connection:
    """A connection to the database."""

    def __init__(self, uri):
        self.connection_string = uri
        self.client = pymongo.MongoClient(self.connection_string)
        self.current_database = "fon_limani"
        self.database = self.client[self.current_database]

        self.key = os.getenv("DATABASE_KEY")

        self.password_encryptor = PasswordEncryptor(secret_key=self.key)

        # Tables
        self.funds = self.database["funds_daily"]
        self.funds_detailed = self.database["funds_detailed"]
        self.funds_founders = self.database["funds_founders"]
        self.funds_information = self.database["funds_information"]
        self.funds_report_links = self.database["funds_report_links"]

        self.logs = self.database["logs"]
        self.messages = self.database["messages"]
        self.news = self.database["news"]
        self.portfolios = self.database["portfolios"]
        self.user_portfolios = self.database["user_portfolios"]
        self.users = self.database["users"]
        self.tokens = self.database["tokens"]
        self.codes = self.database["codes"]
        self.counts = self.database["counts"]
        self.tufe_monthly = self.database["tufe_monthly"]

    # FUNDS

    def add_fund(self, history, fund_code, fund_name, price, number_of_shares_in_circulation, num_investors, fund_total_value):
        try:
            count = self.get_counts()["funds"]
            fund_data = {
                "_id": count,
                "timestamp": datetime.now(),
                "history": history,
                "fund_code": fund_code,
                "fund_name": fund_name,
                "price": price,
                "number_of_shares_in_circulation": number_of_shares_in_circulation,
                "num_investors": num_investors,
                "fund_total_value": fund_total_value
            }
            self.funds.insert_one(fund_data)
            self.update_counts({"funds": count + 1})
            return self.get_fund(count)
        except Exception as e:
            return self.error_log(error_message=f"Fund Error: {e}", error_code=1000)
        
    def get_fund(self, value, by="_id"):
        return self.funds.find_one({by: value})
    
    def get_fund_information(self, value, by="_id"):
        return self.funds_information.find_one({by: value})
    
    def get_all_fund_informations(self):
        return list(self.funds_information.find())
    
    def get_all_funds_detailed(self):
        return list(self.funds_detailed.find())
    
    def get_fund_detailed(self, value, by="_id"):
        return self.funds_detailed.find_one({by: value})
    
    def get_candlestick_data(self, value, by="_id"):
        data = list(self.funds.find({by: value}))
        return data
    
    def get_today_data(self, value="", by="_id"):
        if value == "":
            data = list(self.funds.find({"history": "15.12.23"}))
        else:
            data = list(self.funds.find({by: value, "history": "15.12.23"}))
        return data
    
    def get_day_data(self, history, value="", by="_id"):
        data = list(self.funds.find({by: value, "history": history}))
        print(data)
        return data
    
    def get_one_month_ago_data(self, value="", by="_id"):
        if value == "":
            data = list(self.funds.find({"history": "22.11.23"}))
        else:
            data = list(self.funds.find({by: value, "history": "22.11.23"}))
        return data
    
    def get_last_week_data(self, value="", by="_id"):
        today = datetime.now()
        one_week_before = (today - timedelta(days=10)).strftime("%d.%m.%y")
        if value == "":
            data = list(self.funds.find({"history": { "$in": self.create_date(one_week_before)}}))
        else:
            data = list(self.funds.find({by: value, "history": {"$in": self.create_date(one_week_before)}}))
        return data
    
    def get_last_month_data(self,  value="", by="_id"):
        today = datetime.now()
        one_month_before = (today - timedelta(days=30)).strftime("%d.%m.%y")
        if value == "":
            data = list(self.funds.find({"history": { "$in": self.create_date(one_month_before)}}))
        else:
            data = list(self.funds.find({by: value, "history": {"$in": self.create_date(one_month_before)}}))
        return data
    
    def get_all_funds(self, value="", by="_id"):
        if value == "":
            return list(self.funds.find())
        else:
            return list(self.funds.find({by: value}))
        
    def get_monthly_tufe(self):
        return list(self.tufe_monthly.find())
    
    def get_filtered_fund(self, text):
        funds_list = list(self.funds_detailed.find({"fund_code": {"$regex": text}}))
        if funds_list == []:
            funds_list = list(self.funds_detailed.find({"fund_name": {"$regex": text}}))
        return funds_list
    
    def get_all_reports(self):
        return list(self.funds_report_links.find())
    
    def get_last_n_reports(self, n):
        return list(self.funds_report_links.find().sort([("rapor_id", pymongo.DESCENDING)]).limit(n))
    
    def update_fund(self, fund_id, update_data):
        result = self.funds.find_one_and_update({"_id": fund_id}, {"$set": update_data}, return_document=pymongo.ReturnDocument.AFTER)
        return result

    def delete_fund(self, fund_id):
        result = self.funds.delete_one({"_id": fund_id})
        return "Deleted successfully" if result.deleted_count > 0 else "No record found for deletion"

    # USERS

    def add_user(self, username, password, email, name="", verified=False, subscription=False, subscription_end_date=None, phone=""):
        try:
            count = self.get_counts()["users"]

            # Check if the email is unique
            existing_user = self.users.find_one({"email": email})
            if existing_user:
                return self.error_log("User with the same email already exists.", error_code=2001)
            
            hashed_password = self.password_encryptor.hash_password(password=password)

            user_data = {
                "_id": count,
                "timestamp": datetime.now(),
                "name": name,
                "username": username,
                "password": hashed_password,
                "email": email,
                "verified": verified,
                "subscription": subscription,
                "subscription_end_date": subscription_end_date,
                "phone": phone,
                "birthday": "",
                "location": "",
                "organization": ""
            }
            self.users.insert_one(user_data)
            self.update_counts({"users": count + 1})
            return self.get_user(count)
        except Exception as e:
            return self.error_log(error_message=f"User Error: {e}", error_code=2000)

    def get_user(self, value, by="_id"):
        return self.users.find_one({by: value})

    def get_all_users(self):
        return list(self.users.find())
    
    def update_user(self, user_id, update_data):
        if "password" in update_data.keys():
            update_data["password"] = self.password_encryptor.hash_password(password=update_data["password"])
        result = self.users.find_one_and_update({"_id": user_id}, {"$set": update_data}, return_document=pymongo.ReturnDocument.AFTER)
        return result

    def delete_user(self, user_id):
        result = self.users.delete_one({"_id": user_id})
        return "Deleted successfully" if result.deleted_count > 0 else "No record found for deletion"
    
    def validate_user(self, username, password):
        return self.password_encryptor.verify_password(password=password, hashed_password=self.get_user(by="username", value=username)["password"])
    
    # PORTFOLIOS

    def get_portfolio(self, value, by="_id"):
        return self.portfolios.find_one({by: value, "history": "15.12.23"})

    # USER PORTFOLIOS
    
    def add_user_portfolio(self, user_id, fund, portion):
        try:
            count = self.get_counts()["user_portfolios"]
            user_portfolio_data = {
                "_id": count,
                "timestamp": datetime.now(),
                "user_id": user_id,
                "holds": [fund],
                "hold_numbers": [portion]
            }
            self.user_portfolios.insert_one(user_portfolio_data)
            self.update_counts({"user_portfolios": count + 1})
            return self.get_user_portfolio(count)
        except Exception as e:
            return self.error_log(error_message=f"User Portfolio Error: {e}", error_code=3000)

    def get_user_portfolio(self, value, by="_id"):
        return self.user_portfolios.find_one({by: value})

    def get_all_user_portfolios(self):
        return list(self.user_portfolios.find())
    
    def update_user_portfolio(self, portfolio_id, update_data):
        result = self.user_portfolios.find_one_and_update({"_id": portfolio_id}, {"$set": update_data}, return_document=pymongo.ReturnDocument.AFTER)
        return result

    def delete_user_portfolio(self, portfolio_id):
        result = self.user_portfolios.delete_one({"_id": portfolio_id})
        return "Deleted successfully" if result.deleted_count > 0 else "No record found for deletion"

    # NEWS

    def add_news(self, news_information, news_link):
        try:
            count = self.get_counts()["news"]
            news_data = {
                "_id": count,
                "timestamp": datetime.now(),
                "news_information": news_information,
                "news_link": news_link
            }
            self.news.insert_one(news_data)
            self.update_counts({"news": count + 1})
            return self.get_news(count)
        except Exception as e:
            return self.error_log(error_message=f"News Error: {e}", error_code=4000)

    def get_news(self, value, by="_id"):
        return self.news.find_one({by: value})

    def get_all_news(self):
        return list(self.news.find())
    
    def get_last_n_news(self, n):
        return list(self.news.find().sort([("_id", pymongo.DESCENDING)]).limit(n))
    
    def update_news(self, news_id, update_data):
        result = self.news.find_one_and_update({"_id": news_id}, {"$set": update_data}, return_document=pymongo.ReturnDocument.AFTER)
        return result

    def delete_news(self, news_id):
        result = self.news.delete_one({"_id": news_id})
        return "Deleted successfully" if result.deleted_count > 0 else "No record found for deletion"

    # MESSAGES

    def add_message(self, title, body, email):
        try:
            count = self.get_counts()["messages"]
            message_data = {
                "_id": count,
                "timestamp": datetime.now(),
                "title": title,
                "body": body,
                "email": email,
            }
            self.messages.insert_one(message_data)
            self.update_counts({"messages": count + 1})
            return self.get_message(count)
        except Exception as e:
            return self.error_log(error_message=f"Message Error: {e}", error_code=5000)

    def get_message(self, value, by="_id"):
        return self.messages.find_one({by: value})

    def get_all_messages(self):
        return list(self.messages.find())
    
    def update_message(self, message_id, update_data):
        result = self.messages.find_one_and_update({"_id": message_id}, {"$set": update_data}, return_document=pymongo.ReturnDocument.AFTER)
        return result

    def delete_message(self, message_id):
        result = self.messages.delete_one({"_id": message_id})
        return "Deleted successfully" if result.deleted_count > 0 else "No record found for deletion"
    
    # TOKENS

    def add_token(self, user_id, token):
        try:
            count = self.get_counts()["tokens"]
            token_data = {
                "_id": count,
                "timestamp": datetime.now(),
                "user_id": user_id,
                "token": token,
            }
            self.tokens.insert_one(token_data)
            self.update_counts({"tokens": count + 1})
            return self.get_token(count)
        except Exception as e:
            return self.error_log(error_message=f"Token Error: {e}", error_code=5000)

    def get_token(self, value, by="_id"):
        return self.tokens.find_one({by: value})
    
    # CODES

    def add_code(self, user_id, code):
        try:
            count = self.get_counts()["codes"]
            code_data = {
                "_id": count,
                "timestamp": datetime.now(),
                "user_id": user_id,
                "code": code,
            }
            self.codes.insert_one(code_data)
            self.update_counts({"codes": count + 1})
            return self.get_code(count)
        except Exception as e:
            return self.error_log(error_message=f"Code Error: {e}", error_code=6000)

    def get_code(self, value, by="_id"):
        return self.codes.find_one({by: value})
    
    # COUNTS

    def get_counts(self):
        return self.counts.find_one()
    
    def update_counts(self, update_data):
        result = self.counts.update_one({}, {"$set": update_data})
        return result
    
    def initialize_counts(self):
        counts = self.get_counts()

        if not counts:

            counts_data = {
                "_id": 0,
                "codes": 0 ,
                "funds": 0 ,
                "logs": 0 ,
                "messages": 0 ,
                "news": 0 ,
                "tokens": 0 ,
                "user_portfolios": 0 ,
                "users": 0 ,
            }

            self.counts.insert_one(counts_data)

        return self.get_counts()

    def error_log(self, error_message, error_code):
        count = self.get_counts()["logs"]
        log = {
            "_id": count,
            "timestamp": datetime.now(),
            "error_code": error_code,
            "error_message": error_message,
        }
        self.logs.insert_one(log)
        self.update_counts({"logs": count + 1})

        return error_code

    def create_date(self, start_date_str, end_date_str=datetime.now().strftime("%d.%m.%y")):
        start_date = datetime.strptime(start_date_str, "%d.%m.%y")
        end_date = datetime.strptime(end_date_str, "%d.%m.%y")

        current_date = start_date
        date_list = []

        while current_date <= end_date:
            # Exclude weekends (Saturday and Sunday)
            if current_date.weekday() < 5:
                date_list.append(current_date.strftime("%d.%m.%y"))
            
            current_date += timedelta(days=1)

        return date_list