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
    """Query xclip and return the content of the primary X11 selection."""
    return subprocess.check_output(['/usr/bin/xclip', '-o'])


def setClipboard(data, clicks=None):
    """Set the content of the primary X11 selection.

    xclip seems to be a little nitpicky here with regard to waiting for a
    number of paste operations. A single paste operation seems to happen
    always, so it is either added or used as a default.
    Leaving out the option -l at all does not seem to work: xclip will wait
    indefinitely until someone else fills the X11 selection.

    Note: You need to patch xclip-0.12 with
    http://sourceforge.net/p/xclip/code/85/
    """
    command = ['/usr/bin/xclip', '-i']
    if clicks is not None:
        command += ['-l', str(clicks+1)]
    else:
        command += ['-l', '1']

    p = subprocess.Popen(command,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    # output of command is ignored
    p.communicate(input=data)
