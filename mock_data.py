#!/usr/bin/env python
import argparse
import time
import datetime
import random
import json
import logging
import urllib
import urllib2
import sys

def exit_gracefully(ret=0):
    """
    Exit the application returning :ret:
    """
    import sys
    sys.exit(ret)

if __name__ == '__main__':
    # You can change logging level to INFO to get some information on the data
    # received and sent
    logging.basicConfig(stream=sys.stdout, level=logging.WARNING,
            format='%(message)s')

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
    args = parser.parse_args()

    try:
        import signal
        for i in (signal.SIGABRT, signal.SIGALRM, signal.SIGHUP, signal.SIGILL,
                signal.SIGINT, signal.SIGTERM):
            signal.signal(i, lambda a,b: exit_gracefully())
    except:
        pass #Not UNIX/like system

    res = None
    try:
        res = urllib2.urlopen(args.url)
    except urllib2.URLError as ex:
        logging.error('Error accessing URL: {}\n\t{}'.format(args.url, ex.message))
        exit_gracefully(1)

    res = res.read()
    logging.info('Data got from the server: {}'.format(res))
    conveyor_data = json.loads(res)
    current_total_weight = 0
    if conveyor_data['last_data']:
        current_total_weight = conveyor_data['last_data']['current_total_weight']

    values = {
            'timestamp': None,
            'current_total_weight': current_total_weight,
            'status': None
            }
    while True:
        values['timestamp'] = datetime.datetime.utcnow()\
                .strftime('%Y-%m-%d %H:%M:%S.%f')
        values['current_total_weight'] += random.random() * 100 + 50
        values['status'] = 'Working' if random.random() > .1 else 'Stopped'
        data = urllib.urlencode(values)
        try:
            req = urllib2.Request(args.url, data)
            res = urllib2.urlopen(req)
        except urllib2.URLError as ex:
            loggin.error('Error sending to URL: {}\n\t{}'.format(args.url, ex))
            exit_gracefully(1)
        logging.info('Data sent: {}'.format(data))
        time.sleep(random.random() * 5)

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
