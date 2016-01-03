#
# module clipboard
# contains clipboard helper functions for pwsafe.py
#
# config is a ConfigParser object
# args is the result of argparse
# category means the selected category, expected to be !all
#
import subprocess


def getClipboard():
    return subprocess.check_output(['/usr/bin/xclip', '-o'])


def setClipboard(data):
    p = subprocess.Popen(['/usr/bin/xsel', '-i'],
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    # output of program is ignored
    p.communicate(input=data)
