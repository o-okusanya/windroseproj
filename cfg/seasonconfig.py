from datetime import datetime, timedelta, timezone

def lastseason():

    now = datetime.now(timezone.utc)
    month = now.month

    if month in [3, 4, 5]:
        season, year = "winter", now.year
        sd = datetime(now.year - 1, 12, 1)
        ed = datetime(now.year, 2, 28)
    elif month in [6, 7, 8]:
        season, year = "spring", now.year
        sd = datetime(now.year, 3, 1)
        ed = datetime(now.year, 5, 31)
    elif month == [9, 10, 11]:
        season, year = "summer", now.year
        sd = datetime(now.year, 6, 1)
        ed = datetime(now.year, 8, 31)
    elif month == [12, 1, 2]:
        season, year = "fall", now.year
        sd = datetime(now.year, 9, 1)
        ed = datetime(now.year, 11, 30)

    sd = sd.strftime("%Y-%m-%dT00:00:00Z")
    ed = ed.strftime("%Y-%m-%dT23:59:59Z")

    return season, year, sd, ed