from datetime import datetime as dt
from datetime import timedelta as td
from datetime import timezone as tz

def utc2est(dts):
	OFFSET = td(hours=-4) # [TODO] handle DST
	if type(dts) is not list:
		return dts + OFFSET
	return [d + OFFSET for d in dts]

def f_weekday(weekday, dts):
	return [d for d in dts if d.weekday() == weekday]

def f_weekdays(dts):
	return [d for d in dts if d.weekday() <= 4]

def f_time(from_hour, to_hour, dts):
	return [d for d in dts if from_hour <= d.hour < to_hour]

def f_mornings(dts):
	return f_time(0, 12, dts)

def get_next_noon_of(weekday, datetime=dt.now(tz.utc)):
	if datetime.weekday() == weekday and datetime.hour >= 12:
		datetime += td(days=1)
	while datetime.weekday() != weekday:
		datetime += td(days=1)
	return dt(datetime.year, datetime.month, datetime.day, 12, tzinfo=tz.utc)

def group_by_week(weekday, datetimes):
	datetimes = sorted(datetimes)
	datetime = datetimes.pop()
	week_cutoff = get_next_noon_of(weekday, datetime)
	buckets = [[datetime]]
	while len(datetimes) > 0:
		datetime = datetimes.pop()
		new_cutoff = get_next_noon_of(weekday, datetime)
		if new_cutoff != week_cutoff:
			week_cutoff = new_cutoff
			buckets.append([])
		buckets[-1].append(datetime)
	return buckets

def group_by_weekday(datetimes):
	buckets = [[], [], [], [], [], [], []]
	for datetime in datetimes:
		buckets[datetime.weekday()].append(datetime)
	return buckets

def group_by_day(datetimes, include_days=range(7)):
	datetimes = sorted(datetimes)
	datetime = datetimes.pop()
	current_date = datetime.date()
	buckets = [[datetime]]
	while len(datetimes) > 0:
		datetime = datetimes.pop()
		while current_date > datetime.date():
			current_date -= td(days=1)
			if current_date.weekday() in include_days:
				buckets.append([])
		buckets[-1].append(datetime)
	return buckets
