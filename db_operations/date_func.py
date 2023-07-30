import datetime

def todays_date() -> str:
    today = datetime.date.today()
    today_str = datetime.datetime.strftime(today, '%Y-%m-%d')
    return today_str