
def utcdate_to_string(d):
    datestring = d.strftime('%Y-%m-%d %H:%M:%S.%f')
    return datestring + ' +0000'
