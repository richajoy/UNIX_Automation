#! /usr/bin/env python

import subprocess

#Command 1
def uname_func() :
    uname = "uname"
    print " Gathering system information using %s command:" % uname
    subprocess.call("uname -a ",shell=True)

#Command 2
def mount_func() :
    mount = "df"
    print "Gathering system information using %s command:" % mount
    subprocess.call("df -h",shell=True)

#Main funtion that calls the sub funtions

def main() :
    uname_func()
    mount_func()

main()
