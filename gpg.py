#
# module gpg
# contains gnupg helper functions for pwsafe.py
#
# config is a ConfigParser object
# args is the result of argparse
# category means the selected category, expected to be !all
#
import re
import subprocess


def getReceivers(config, category):
    receivers = config.get(category, 'encrypt-to')
    receivers = receivers.split('\n')
    result = []
    for r in receivers:
        result.append('-r')
        result.append(re.sub(' ;.*$', '', r))
    return result


def crypt(config, category, password, user, url):
    receivers = getReceivers(config, category)

    raw = password + ':' + user + ':' + url
    raw = raw.replace('\n', '').replace('\r', '')
    p = subprocess.Popen(['/usr/bin/gpg', '-q', '--batch',
                          '-ea'] + receivers,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    cr = p.communicate(input=raw)[0]
    return cr


def decrypt(length, cr):

    p = subprocess.Popen(['/usr/bin/gpg', '-d', '-q', '--batch'],
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    raw = p.communicate(input=cr)[0]
    return [raw[0:length]] + raw.split(':')
