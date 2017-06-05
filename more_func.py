#! /usr/bin/env python 
#Very short script that reuse the func.py code

from func import mount_func
import subprocess

def tmp_space():
    tmp_usage = "ls"
    tmp_arg = "-l"
    path = "/tmp"
    print "Checking the files in  %s directory\n" % path
    subprocess.call([tmp_usage,tmp_arg,path])

def main():
    tmp_space()
    mount_func


if __name__ == "__main__":
    main()
