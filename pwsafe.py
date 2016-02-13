#!/usr/bin/python
import argparse
import ConfigParser
import csv
import getpass
import os
import sqlite3
import subprocess
import sys

# local modules
import clipboard
import db
import gpg


config = ConfigParser.SafeConfigParser()
config.read(['pwsafe.cfg', os.path.expanduser('~/.pwsafe/pwsafe.cfg')])


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

#
# optional commands: --import
#
group.add_argument("-i", "--import", dest='importer', action="store_true",
                   help="import a batch of entries from a CSV")
parser.add_argument("-f", "--file",
                    help="file with CSV entries")
parser.add_argument("-n", "--no-action", action="store_true",
                    help="read CSV entries but do not modify DB")


args = parser.parse_args()


if args.add:
    if args.category == 'all':
        print "'all' is no valid category for add."
        exit(1)

    dbCon = db.initializeDataBase(config, args.category)
    cur = dbCon.cursor()

    if args.key is None:
        args.key = clipboard.getClipboard()

    length = config.getint(args.category, 'length')
    if args.user is None:
        args.user = subprocess.check_output(['/usr/bin/pwgen',
                                             '-AB', str(length+2), '1'])
        args.user = args.user.replace('\n', '')
        print 'user:', args.user
        clipboard.setClipboard(args.user, 1)

    password = args.password
    if args.ask_password:
        password = getpass.getpass("Enter password:")
        if password != getpass.getpass("Re-enter password:"):
            print 'Password mismatch!'
            exit(2)
    if password is None:
        password = subprocess.check_output(['/usr/bin/pwgen',
                                            '-s', str(length), '1'])
        password = password.replace('\n', '')
        print 'created password:', password
        clipboard.setClipboard(password, 2)
        clipboard.setClipboard("     ")

    if args.url is None:
        args.url = args.key

    crypto = gpg.crypt(config, args.category, password, args.user, args.url)

    cur.execute("INSERT INTO Accounts(Name, Comment, Url, User, Length, "
                "Password) VALUES (?, ?, ?, ?, ?, ?)",
                (args.key, args.comment, args.url, args.user, length, crypto))
    dbCon.commit()


elif args.list:
    categories = []
    if (args.category == 'all'):
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
            print 'URL      =', \
                answer[3].replace('\n', '') if answer[3] != None else ''
            print 'User     =', \
                answer[4].replace('\n', '') if answer[4] != None else ''
            if args.decrypt:
                data = gpg.decrypt(answer[5], answer[6])
                print 'Password =', \
                    data[0].replace('\n', '') if data[0] != None else ''
            print
        dbCon.close()


elif args.importer:
    # args.file
    # args.no_action
    dbCon = db.initializeDataBase(config, args.category)
    cur = dbCon.cursor()
    length = config.getint(args.category, 'length')

    csvfile = open(args.file, 'rb')
    reader = csv.reader(csvfile)
    for row in reader:
        if row is None or len(row) < 5:
            continue
        if row[0][0] == '#':
            continue
        crypto = gpg.crypt(config, args.category, row[4], row[3], row[2])
        length = len(row[4])
        if args.no_action:
            print "would insert:", row[0], row[1], row[2], row[3], length, crypto[0:8]
        else:
            cur.execute("INSERT INTO Accounts(Name, Comment, Url, User, "
                        "Length, Password) VALUES (?, ?, ?, ?, ?, ?)",
                        (row[0], row[1], row[2], row[3], length, crypto))
            dbCon.commit()

    dbCon.close()


else:
    dbCon = db.initializeDataBase(config, args.category)
    cur = dbCon.cursor()

    if args.key is None:
        args.key = clipboard.getClipboard()

    args.key = '%' + args.key + '%'
    theKey = (args.key, args.key, args.key)
    cur.execute("SELECT * FROM Accounts WHERE Name LIKE ? OR Comment LIKE ? "
                "OR Url LIKE ?", (theKey))
    emptyResult = True
    for answer in cur.fetchall():
        emptyResult = False
        data = gpg.decrypt(answer[5], answer[6])
        print 'User:', answer[4], 'Password:', data[0]
        clipboard.setClipboard(data[0], 1)
        clipboard.setClipboard("     ")

    if emptyResult:
        print 'Sorry, no matching entry'

    if dbCon:
        dbCon.close()
