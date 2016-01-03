# pwsafe
A command-line password manager written in python.

This password manager was inspired by https://github.com/sol/pwsafe and
improves/replaces my personal long-time grep'ing in gpg encrypted files.

It uses external programs for most of its tasks:
* `gpg` for encryption of your password database
* `xclip` and `xsel` for interaction with your X selection
* `pwgen` for generation of user names and passwords

Development and testing was made on Linux (openSuSE 13.2), all used python
modules and tools are part of the standard distro. Basically pwsafe should run
on any decent Unix-like system.

## Features
This is not only yet another implementation of a command-line password manager,
it also adds some features I rely on:

* It supports three different categories of password databases: company,
  admin, and private. 
* Every category can have a different default password length.
* Every category can be encrypted to a different set of gpg keys: If you go
  out of business for any reason a trusted colleague can continue to
  administrate your servers.

## Installation

1. Clone the git repository
2. Create a directory ~/.pwsafe
3. Copy pwsafe.cfg-example to ~/.pwsafe/pwsafe.cfg
4. Create a gpg key (if you do not have one already)
5. Edit ~/.pwsafe/pwsafe.cfg and insert your key id in the encrypt-to-default line
6. Add directory with pwsafe.py to your path. Or create a link to it and add this link to your path

## Workflow

### Adding an entry
Assume you need a new password for some site and want to select your username
by your own. Then issue this command:

    $ pwsafe -a -C "For demonstration" -U "https://demo.local/login" -u myusername demo
    created password: u6XeQpJ8
    $

The new password has been added to the X11 selection and can be pasted into
any form field by pressing the middle mouse button.

If you want to have an auto-generated username just omit the option `-u
myusername`.

Sometimes it is useful to enter values for the username which are not exactly
used as usernames, e.g. the SSID of a WLAN for which the password is stored.

### Looking up an entry
The command to look up an entry is:

    $ pwsafe demo
    User: myusername Password: u6XeQpJ8
    $

If you omit the key `demo` the current X11 selection is used as key. 

The lookup for a key searches an explicit key field, the comment field, and
the URL field but currently not the username.

## Command line options

    usage: pwsafe [-h] [-v] [-c {all,admin,company,private}] [-a] [-C COMMENT]
                  [-U URL] [-u USER] [-p PASSWORD] [-P] [-l] [-d] [-i] [-f FILE]
                  [-n]
                  [key]
                  
    positional arguments:
    key                   lookup key, if not provided the current selection is
                          used
                          
    optional arguments:
      -h, --help            show this help message and exit
      -v, --verbosity       increase output verbosity
      -c {all,admin,company,private}, --category {all,admin,company,private}
                            specify the category for the key
      -a, --add             add an entry
      -C COMMENT, --comment COMMENT
                            specify comment
      -U URL, --url URL     specify URL
      -u USER, --user USER  specify user id
      -p PASSWORD, --password PASSWORD
                            specify password on commandline (not recommended)
      -P, --ask-password    interactively ask for password
      -l, --list            list all entries
      -d, --decrypt         show decrypted passwords in listing
      -i, --import          import a batch of entries from a CSV
      -f FILE, --file FILE  file with CSV entries
      -n, --no-action       read CSV entries but do not modify DB

## Configuration options
The configuration is done in ~/.pwsafe/pwsafe.cfg. This is the content of
pwsafe.cfg-example:

    [DEFAULT]
    verbosity=0
    dbbasedir=~/.pwsafe
    encrypt-to-default= <insert your key id here>
    encrypt-to=%(encrypt-to-default)s
    category=company
    length=8
      
    [company]
    db=company.sql
    encrypt-to=%(encrypt-to-default)s
      
    [admin]
    db=admin.sql
    encrypt-to=%(encrypt-to-default)s
        <insert additional key id here: 12345678 ; A Friend <friend@invalid.local> >
        
    [private]
    db=private.sql

The format follows [python's
ConfigParser](https://docs.python.org/2/library/configparser.html). 

The `[DEFAULT]` section provide default values for the sections specific to
each category. Only `verbosity`, `category`, and `dbbasedir` are explicitly
used from this section. All other values can be overwritten or substituted in
the following sections.

The sections ``, ``, and `` provite special options for the selected
category. Required is at least the entry ``db`` which specifies the name of
the database file (relative to the `dbbasedir`).

The values have the following interpretation:

* category: The default category. Overridden by command line option -c
* db: The database file relative to dbbasedir
* dbbasedir: The base directory common for all categories
* encrypt-to: The list of key to which the password of this category is encrypted 
* encrypt-to-default: The default key, only used by ConfigParser for substitutions
* length: The length of a auto-generated password.
* verbosity: The default verbosity level.

## Known Issues
Currently (January 2016) the behavior of xclip seems to be broken. Officially
xclip has an option `--loop n` where it waits for a number of paste operations
before it continues. https://github.com/sol/pwsafe uses this option to provide
first the username, then the password for two consecutive paste
operations. But there seems to be an issue where this --loop option fails. See
[Stack Overflow](http://stackoverflow.com/a/24332080) for an explanation.
