import json
from datetime import datetime as dt
from datetime import timedelta as td
from datetime import timezone as tz
from pprint import pprint as pp

import twitter
api = twitter.Api(consumer_key='s7rxM3EtQxWRicsFyq16yMOQo',
	consumer_secret='uToP7FxzAwl0PtapIWbMgXI0lWcLx1nXeUiwKoiCTsfnoYLgum',
	access_token_key='1043992880-6yvvOgaUU389q2sK9LgWRRggFimvZVy8por8bBL',
	access_token_secret='3A05LRtPO6BBax6L0JWg2E2bBx34lXbKYTVaeXcDPjwDg')

DT_FMT = '%a %b %d %H:%M:%S %z %Y'
NOON_FRI = dt(2017, 9, 29, 16, tzinfo=tz.utc) # [TODO] handle EST/EDT instead of 16 placeholder

def fetch_all_timestamps(screen_name='vp', max_id=None, count=None):
	data = []
	while count is None or len(data) < count:
		page = api.GetUserTimeline(screen_name=screen_name, count=200, max_id=max_id)
		if len(page) == 0: break
		data.extend(page)
		max_id = data[-1].AsDict()['id'] - 1

	statuses = [status.AsDict() for status in data]
	timestamps = [s['created_at'] for s in statuses]
	return timestamps

def get_next_noon_of(weekday, datetime=dt.now(tz.utc)):
	if datetime.weekday() == weekday and datetime.hour >= 16:
		datetime += td(days=1)
	while datetime.weekday() != weekday:
		datetime += td(days=1)
	return dt(datetime.year, datetime.month, datetime.day, 16, tzinfo=tz.utc)

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

dts_vp = [dt.strptime(t, DT_FMT) for t in fetch_all_timestamps('vp')]
dts_potus = [dt.strptime(t, DT_FMT) for t in fetch_all_timestamps('potus')]

print(len([d for d in dts_vp if d > NOON_FRI]))

b1 = [len(x) for x in group_by_week(1, dts_vp)]
b2 = [len(x) for x in group_by_week(4, dts_vp)]
b3 = [len(x) for x in group_by_week(1, dts_potus)]

print('vp Tuesday')
print(b1)

print('vp Friday')
print(b2)

print('potus Tuesday')
print(b3)
