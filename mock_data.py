#!/usr/bin/env python
import argparse
import time
import datetime
import random
import json
import urllib
import urllib2

def exit_gracefully(ret=0):
    """
    Exit the application returning :ret:
    """
    import sys
    sys.exit(ret)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
    description='This is the script for simulating the incoming data.\n\
If a file is specified then the CSV data on that file will be posted.\n\
If no file is passed, random data is generated and sent every second.',
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('url',
            help='URL to post the data.\n\
Default: http://localhost:8080/opened',
            default='http://localhost:8080/opened',
            nargs='?')
    parser.add_argument('-f','--file',
            help='CSV File to load the data from.\n\
Default: mock_data.csv')
    args = parser.parse_args()

    try:
        import signal
        for i in (signal.SIGABRT, signal.SIGALRM, signal.SIGHUP, signal.SIGILL,
                signal.SIGINT, signal.SIGTERM):
            signal.signal(i, lambda a,b: exit_gracefully())
    except:
        pass #Not UNIX/like

    res = None
    try:
        res = urllib2.urlopen(args.url)
    except urllib2.URLError as ex:
        print 'Error accessing URL: {}\n\t{}'.format(args.url, ex.message)
        exit_gracefully(1)

    res = res.read()
    print res
    conveyor_data = json.loads(res)
    current_total_weight = conveyor_data['last_data']['current_total_weight']

    values = {
            'timestamp': None,
            'current_total_weight': current_total_weight,
            'status': 'Working'
            }
    while True:
        values['timestamp'] = datetime.datetime.utcnow()\
                .strftime('%Y-%m-%d %H:%M:%S.%f')
        values['current_total_weight'] += random.random() * 100
        values['status'] = 'Working' if random.random() > .1 else 'Stopped'
        data = urllib.urlencode(values)
        try:
            req = urllib2.Request(args.url, data)
            res = urllib2.urlopen(req)
        except urllib2.URLError as ex:
            print 'Error sending to URL: {}\n\t{}'.format(args.url, ex)
            exit_gracefully(1)
        print 'Data sent:', data
        time.sleep(random.random() * 5)

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
