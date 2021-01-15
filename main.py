import requests
import datetime
from twilio.rest import Client
import cfg

STOCK = "TSLA"
COMPANY_NAME = "Teslasvagzsebgf"
STOCKS_URL = "https://www.alphavantage.co/query"
NEWS_URL = "http://newsapi.org/v2/everything"
PERCENT_AMT = 1
NUM_ARTICLES = 3
NEWS_AGE = 5

today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)
day_before = today - datetime.timedelta(days=2)
news_date = today - datetime.timedelta(days=NEWS_AGE)


def check_stocks():
    """Fetch stock data about watched company from API and returns the difference between yesterday and
    the day before's closing price as a percentage."""
    stock_params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": STOCK,
        "apikey": cfg.STOCKS_API_KEY
    }
    response = requests.get(STOCKS_URL, params=stock_params)
    response.raise_for_status()
    stock_data = response.json()
    yesterday_close = float(stock_data["Time Series (Daily)"][str(yesterday)]["4. close"])
    day_before_close = float(stock_data["Time Series (Daily)"][str(day_before)]["4. close"])
    difference = yesterday_close - day_before_close
    return round(difference / day_before_close * 100)


def get_news():
    """Fetch and return specified amount of news articles for the past specified days related to watched company."""
    news_params = {
        "qInTitle": COMPANY_NAME,
        "from": news_date,
        "to": today,
        "sortBy": "popularity",
        "apiKey": cfg.NEWS_API_KEY
    }
    response = requests.get(NEWS_URL, params=news_params)
    response.raise_for_status()
    news_data = response.json()
    return news_data["articles"][:NUM_ARTICLES]


def send_message():
    """Send news article as a text message via Twilio service."""
    client = Client(cfg.TWILIO_ACC_SID, cfg.TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        body=formatted_message,
        from_=cfg.TWILIO_PHONE_NUM,
        to=cfg.MY_PHONE_NUM
    )
    print(message.status)


percent_change = check_stocks()

if percent_change < 0:
    direction = "🔻"
    percent_change *= -1
else:
    direction = "🔺"

if percent_change >= PERCENT_AMT:
    news_articles = get_news()
    stock_change = f"\nTSLA: {direction}{percent_change}%\n"

    # If articles were fetched successfully:
    if len(news_articles) > 0:
        for article in news_articles:
            headline = article["title"].replace(" - Reuters", "")
            brief = article["description"]
            formatted_message = f"{stock_change}Headline: {headline}\nBrief: {brief}"
            # print(formatted_message)
            send_message()
    # If no articles were found:
    else:
        formatted_message = f"{stock_change}No relevant news articles found.\n"
        # print(formatted_message)
        send_message()
