#! /usr/bin/env python
# A System Information gathering script
import subprocess 

#Command 1
hostname = "hostname"
print "Gathering the System info with %s command:\n" % hostname
subprocess.call("hostname", shell=True)

#Command 2
diskspace = "df"
diskspace_arg = "-h"
print "Gathering diskspace info with %s command:\n" % diskspace
subprocess.call([diskspace,diskspace_arg])

