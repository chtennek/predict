"""PredictIt analysis.

Usage:
  predict [--vp1 --vp2 --rdt --potus] [--all --calendar --week --day --weekday] [(-w WEEKDAY)] [(-t FROM TO)] [(-f <filters>)...] [-c | --cached] [-v]
  predict ship <name> move <x> <y> [--speed=<kn>]
  predict -h

Options:
  -h --help     Show this screen.
  --verbose     Show debugging output.
  --version     Show version.
  --speed=<kn>  Speed in knots [default: 10].
  --moored      Moored (anchored) mine.
  --drifting    Drifting mine.

"""
from docopt import docopt

import json
from datetime import datetime as dt
from datetime import timedelta as td
from datetime import timezone as tz
from pprint import pprint as pp
import pickle

import twitter
api = twitter.Api(consumer_key='s7rxM3EtQxWRicsFyq16yMOQo',
	consumer_secret='uToP7FxzAwl0PtapIWbMgXI0lWcLx1nXeUiwKoiCTsfnoYLgum',
	access_token_key='1043992880-6yvvOgaUU389q2sK9LgWRRggFimvZVy8por8bBL',
	access_token_secret='3A05LRtPO6BBax6L0JWg2E2bBx34lXbKYTVaeXcDPjwDg')

import analysis

DT_FMT = '%a %b %d %H:%M:%S %z %Y'

def fetch_all_timestamps(screen_name='vp', max_id=None, count=3000):
	data = []
	while count is None or len(data) < count:
		page = api.GetUserTimeline(screen_name=screen_name, count=200, max_id=max_id)
		if len(page) == 0: break
		data.extend(page)
		max_id = data[-1].AsDict()['id'] - 1

	statuses = [status.AsDict() for status in data]
	timestamps = [s['created_at'] for s in statuses]
	return timestamps

def calendar_format(latest_dt, data):
	# data = [ (datetime, output) ]
	weeks = [[]] # [ week = [outputs] ]
	weekday = latest_dt.weekday()
	for value in data:
		weeks[-1].insert(0, str(value)) # str() for outputting
		if weekday == 0:
			weeks.append([])
		weekday = (weekday - 1) % 7
	return '\n'.join(['\t'.join(week) for week in reversed(weeks)])

def counts(buckets):
	return [len(b) for b in buckets]

if __name__ == '__main__':
	args = docopt(__doc__)
	if args['-v']:
		print(args)

	if args['--all']:
		args['--recent'] = True
		args['--week'] = True
		args['--day'] = True
		args['--weekday'] = True

	# Parse usernames to search
	usernames = []
	if args['--vp1'] or args['--vp2']:
		usernames += ['vp']
	if args['--rdt']:
		usernames += ['realDonaldTrump']
	if args['--potus']:
		usernames += ['potus']
	if not any([args[u] for u in ['--vp1', '--vp2', '--rdt', '--potus']]):
		usernames = ['vp', 'realDonaldTrump', 'potus']

	# Load/fetch tweet data
	dts = {}
	if args['-c']:
		for username in usernames:
			with open(username + '.pkl', 'rb') as f:
				dts[username] = pickle.load(f)
	else:
		for username in usernames:
			dts[username] = [dt.strptime(t, DT_FMT) for t in fetch_all_timestamps(username)]
			with open(username + '.pkl', 'wb') as f:
				pickle.dump(dts[username], f)
	# [TODO] handle EST conversion better
	for username in usernames:
		dts[username] = [analysis.utc2est(d) for d in dts[username]]

	# Apply filters
	for username in usernames:
		print('Filtering {} from {}...'.format(username, len(dts[username])))
		if 'weekdays' in args['<filters>']:
			dts[username] = analysis.f_weekdays(dts[username])
		if 'mornings' in args['<filters>']:
			dts[username] = analysis.f_mornings(dts[username])
		if str(args['WEEKDAY']).isdigit():
			args['WEEKDAY'] = int(args['WEEKDAY'])
			dts[username] = analysis.f_weekday(args['WEEKDAY'], dts[username])
		if str(args['FROM']).isdigit() and str(args['TO']).isdigit():
			args['FROM'] = int(args['FROM'])
			args['TO'] = int(args['TO'])
			dts[username] = analysis.f_time(args['FROM'], args['TO'], dts[username])
		print('to {}!'.format(len(dts[username])))

	# Analyses [TODO] merge these with dispatch
	if args['--recent']:
		if args['--vp1'] or args['--vp2']: pp(dts['vp'][:15])
		if args['--rdt']: pp(dts['rdt'][:15])
		if args['--potus']: pp(dts['potus'][:15])

	by_week = {}
	if args['--week']:
		if args['--vp1']: by_week['vp T'] = analysis.group_by_week(1, dts['vp'])
		if args['--vp2']: by_week['vp F'] = analysis.group_by_week(4, dts['vp'])
		if args['--rdt']: by_week['rdt W'] = analysis.group_by_week(2, dts['realDonaldTrump'])
		if args['--potus']: by_week['potus T'] = analysis.group_by_week(1, dts['potus'])

	by_weekday = {}
	if args['--weekday']:
		if args['--vp1'] or args['--vp2']: by_weekday['vp'] = analysis.group_by_weekday(dts['vp'])
		if args['--rdt']: by_weekday['rdt'] = analysis.group_by_weekday(dts['realDonaldTrump'])
		if args['--potus']: by_weekday['potus'] = analysis.group_by_weekday(dts['potus'])

	by_day = {}
	if args['--day']:
		if args['--vp1'] or args['--vp2']: by_day['vp'] = analysis.group_by_day(dts['vp'])
		if args['--rdt']: by_day['rdt'] = analysis.group_by_day(dts['realDonaldTrump'])
		if args['--potus']: by_day['potus'] = analysis.group_by_day(dts['potus'])

	for label, datetimes in dts.items():
		print(label)
		print(len(datetimes))

	for label, data in by_week.items():
		print(label)
		print(counts(data))

	for label, data in by_weekday.items():
		print(label)
		print(counts(data))

	for label, data in by_day.items():
		print(label)
		print(counts(data))
		if args['--calendar']:
			print(calendar_format(data[0][0], counts(data)))
