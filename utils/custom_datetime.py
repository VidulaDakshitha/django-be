
import datetime
from datetime import timedelta, time, date
import calendar


def naive_datetime(datetime_str):
    # List of datetime formats we want to support
    formats = [
        "%Y-%m-%d",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%dT%H:%M"
    ]
    # Try each format until one successfully parses the datetime_str
    for fmt in formats:
        try:
            return datetime.datetime.strptime(str(datetime_str), fmt)
        except ValueError:
            continue

    # If no format works, raise an exception or handle it appropriately
    raise ValueError(f"datetime_str does not match any supported format: {datetime_str}")


def get_unique_ascii():
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
    hexadecimals = hex(int(timestamp))
    unique_id = hexadecimals[2:]
    return str(unique_id)


def get_formatted_current_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_timestamp():
    ts = datetime.datetime.now().timestamp()
    return str(ts)


def get_today():
    today = datetime.datetime.now().date()
    today_start = datetime.datetime.combine(today, time())
    today_end = datetime.datetime.combine(today + timedelta(1), time())

    return today_start, today_end


def get_week():
    week_start = date.today() - timedelta(days=date.today().isoweekday() - 1)
    week_end = week_start + timedelta(days=7)
    week_start = datetime.datetime.combine(week_start, time())
    week_end = datetime.datetime.combine(week_end, time())

    return week_start, week_end


def get_month():
    month_start = date.today().replace(day=1)
    _, end_day = calendar.monthrange(month_start.year, month_start.month)
    month_end = month_start.replace(day=end_day)

    month_start = datetime.datetime.combine(month_start, time())
    month_end = datetime.datetime.combine(month_end + timedelta(1), time())

    return month_start, month_end


def get_quarter():
    current_month = date.today().month

    quarter_start_month = (current_month - 1) // 3 * 3 + 1
    quarter_start = date(date.today().year, quarter_start_month, 1)

    quarter_end_month = (current_month - 1) // 3 * 3 + 4
    if quarter_end_month > 12:
        quarter_end = date(date.today().year + 1, 1, 1) - timedelta(days=1)
    else:
        quarter_end = date(date.today().year, quarter_end_month, 1) - timedelta(days=1)

    quarter_start = datetime.datetime.combine(quarter_start, time())
    quarter_end = datetime.datetime.combine(quarter_end + timedelta(1), time())

    return quarter_start, quarter_end


def get_last_n_days(iteration):
    iteration = iteration + 1
    today = datetime.datetime.today() + timedelta(1)
    days = [datetime.datetime.combine((today - timedelta(days=i)), time()) for i in range(iteration)]
    days = days[::-1]

    formatted_days = []
    for idx in range(len(days)):
        if idx < len(days) - 1:
            date_name = days[idx].strftime('%Y-%m-%d')
            formatted_days.append((days[idx], days[idx + 1], date_name))

    return formatted_days


def get_last_n_weeks(iteration):
    today = date.today()
    seven_weeks_ago = today

    weeks = []
    for i in range(iteration):
        start_date = datetime.datetime.combine(
            (seven_weeks_ago - timedelta(days=seven_weeks_ago.weekday())) - timedelta(weeks=i), time())
        end_date = datetime.datetime.combine((start_date + timedelta(days=7)), time())
        week_number = start_date.isocalendar()[1]
        week_number = "W" + str(week_number)
        weeks.append((start_date, end_date, week_number))

    weeks = weeks[::-1]

    return weeks


def get_quarter_dates(year, quarter):
    if quarter == 1:
        quarter_name = str(year) + "/Q1"
        return datetime.datetime.combine(date(year, 1, 1), time()), datetime.datetime.combine(date(year, 4, 1),
                                                                                              time()), quarter_name
    elif quarter == 2:
        quarter_name = str(year) + "/Q2"
        return datetime.datetime.combine(date(year, 4, 1), time()), datetime.datetime.combine(date(year, 7, 1),
                                                                                              time()), quarter_name
    elif quarter == 3:
        quarter_name = str(year) + "/Q3"
        return datetime.datetime.combine(date(year, 7, 1), time()), datetime.datetime.combine(date(year, 10, 1),
                                                                                              time()), quarter_name
    elif quarter == 4:
        quarter_name = str(year) + "/Q4"
        return datetime.datetime.combine(date(year, 10, 1), time()), datetime.datetime.combine(date(year + 1, 1, 1),
                                                                                               time()), quarter_name


def get_last_n_quarters(iteration):
    now = date.today()
    year = now.year
    quarter = (now.month - 1) // 3 + 1

    quarter_dates = []
    for i in range(iteration):
        start, end, quarter_name = get_quarter_dates(year, quarter)
        quarter_dates.append((start, end, quarter_name))

        if quarter == 1:
            year -= 1
            quarter = 4
        else:
            quarter -= 1

    quarter_dates = quarter_dates[::-1]
    return quarter_dates


def get_month_start_end(year, month):
    month_start = datetime.datetime(year, month, 1)

    _, end_day = calendar.monthrange(year, month)
    month_end = month_start.replace(day=end_day)

    month_start = datetime.datetime.combine(month_start, time())
    month_end = datetime.datetime.combine(month_end + timedelta(1), time())

    month_name = month_start.strftime("%b")
    return month_start, month_end, month_name


def get_last_n_months(iteration):
    now = date.today()
    year = now.year
    month = now.month

    month_dates = []

    for i in range(iteration):
        start, end, month_name = get_month_start_end(year, month)

        month_dates.append((start, end, month_name))

        if month == 1:
            year -= 1
            month = 12
        else:
            month -= 1

    month_dates = month_dates[::-1]
    return month_dates


def get_next_n_date(n):
    today = datetime.datetime.now().date()
    n_date = today + timedelta(n)

    return n_date


def get_last_n_date(n):
    today = datetime.datetime.now().date()
    n_date = today - timedelta(n)

    return n_date
