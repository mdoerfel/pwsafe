#!/usr/bin/python
import argparse
import ConfigParser
import getpass
import os
import re
import sqlite3
import subprocess
import sys

# local modules
import db
import gpg

config = ConfigParser.SafeConfigParser()
config.read(['pwsafe.cfg', os.path.expanduser('~/.pwsafe/pwsafe.cfg')])
# Usage: value = config.get( 'Section', 'option', false, {'option' : 'override'} )


parser = argparse.ArgumentParser()
#
# Basic arguments
#
parser.add_argument("-v", "--verbosity", action="count", 
                    default=config.getint('DEFAULT', 'verbosity'),
                    help="increase output verbosity")
parser.add_argument("key", nargs='?', 
                    help="lookup key, if not provided the "
                         "current selection is used")
parser.add_argument("-c", "--category", 
                    choices=['all', 'admin', 'company', 'private'],
                    default=config.get('DEFAULT', 'category'),
                    help='specify the category for the key')

#
# optional commands: --add
#
group = parser.add_mutually_exclusive_group()
group.add_argument("-a", "--add", action="store_true",
                    help="add an entry")
parser.add_argument("-C", "--comment",
                    help="specify comment")
parser.add_argument("-U", "--url",
                    help="specify URL")
parser.add_argument("-u", "--user",
                    help="specify user id")
parser.add_argument("-p", "--password",
                    help="specify password on commandline (not recommended)")
parser.add_argument("-P", "--ask-password", action="store_true",
                    help="interactively ask for password")


#
# optional commands: --list
#
group.add_argument("-l", "--list", action="store_true",
                    help="list all entries")
parser.add_argument("-d", "--decrypt", action="store_true",
                    help="show decrypted passwords in listing")


args = parser.parse_args()



if args.add:
    if args.category == 'all':
        print "'all' is no valid category for add."
        exit(1)

    dbCon = db.initializeDataBase(config, args.category)
    cur = dbCon.cursor()

    if args.key == None:
        args.key = subprocess.check_output(['/usr/bin/xclip', '-o'])

    length = config.getint(args.category, 'length')
    if args.user == None:
        args.user = subprocess.check_output(['/usr/bin/pwgen', 
                                             '-AB', str(length+2), '1'])
        print 'user:', args.user

    password = args.password
    if args.ask_password:
        password = getpass.getpass("Enter password:")
        if password != getpass.getpass("Re-enter password:"):
            print 'Password mismatch!'
            exit(2)
    if password == None:
        password = subprocess.check_output(['/usr/bin/pwgen', 
                                            '-s', str(length), '1'])

    if url.args == None:
        url.args = args.key

    crypto = gpg.crypt(config, args.category, password, args.user, args.url)

    cur.execute("INSERT INTO Accounts(Name, Comment, Url, User, Length, Password) VALUES (?, ?, ?, ?, ?, ?)", 
                (args.key, args.comment, args.url, args.user, length, crypto) )
    dbCon.commit()


elif args.list:
    categories = []
    if ( args.category == 'all' ):
        categories.append('admin')
        categories.append('company')
        categories.append('private')
    else:
        categories.append(args.category)

    for category in categories:
        print '-----', category, '-----'
        dbCon = db.initializeDataBase(config, category)
        cur = dbCon.cursor()
        cur.execute('SELECT * FROM Accounts')
        for answer in cur.fetchall():
            emptyResult = False
            print '[', answer[1], ']'
            print 'Comment  =', answer[2]
            print 'URL      =', answer[3].replace('\n', '') if answer[3] != None else ''
            print 'User     =', answer[4].replace('\n', '') if answer[4] != None else ''
            if args.decrypt:
                data = gpg.decrypt( answer[5], answer[6] )
                print 'Password =', data[0].replace('\n', '') if data[0] != None else ''
            print
        dbCon.close()


else:
    dbCon = db.initializeDataBase(config, args.category)
    cur = dbCon.cursor()

    if args.key == None:
        args.key = subprocess.check_output(['/usr/bin/xclip', '-o'])

    args.key = '%' + args.key + '%';
    theKey = (args.key, args.key, args.key)
    cur.execute('SELECT * FROM Accounts WHERE Name LIKE ? OR Comment LIKE ? OR Url LIKE ?', (theKey))
    emptyResult = True
    for answer in cur.fetchall():
        emptyResult = False
        print answer
        data = gpg.decrypt( answer[5], answer[6] )
        print 'User:', data[2], 'Password:', data[0]
#        p = subprocess.Popen(['/usr/bin/xclip', '-i', '-l', '1'], 
        p = subprocess.Popen(['/usr/bin/xsel', '-i'], 
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        result = p.communicate(input=data[0])[0]

    if emptyResult:
        print 'Sorry, no matching entry'

if dbCon:
    dbCon.close()
