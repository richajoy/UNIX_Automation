#!/opt/opsware/bin/python2

# $Id: sudoersCHK.py 288 2015-01-26 21:39:11Z dblackbu $
# $Header: https://uslv-papp-adm01/svn/unix/dblackbu/DevOps/OpswareJobs/sudoersCHK.py 288 2015-01-26 21:39:11Z dblackbu $

import xmlrpclib
import glob
import sys
import os
import re
import sets
import smtplib
import traceback

sys.path.append("/opt/opsware/pylibs2")
from pytwist import *
from pytwist.com.opsware.search import Filter
from pytwist.com.opsware.server import ServerRef
from pytwist.com.opsware.locality import CustomerRef

def sendmail(BODY,ALARM):
    #
    # Emails output if a problem occurs.
    #
    import string
    HOST = "mailhost-i.amgen.com"
    FROM = "unix@amgen.com"
    TO = "rjoy@amgen.com"

    SUBJECT = "** %s Servers Sudoers files are out of sync **" % ALARM
    MIME = "MIME-Version: 1.0\nContent-type: text/html"
    HTML1 = "<html><head></head><body>"
    HTML2 = "</body></html>"
    body = string.join((
        "From: %s" % FROM,
        "To: %s" % TO,
        MIME,
        "Subject: %s" % SUBJECT,
        "",
        HTML1,
        BODY,
        HTML2), "\r\n")

    server = smtplib.SMTP(HOST)
    server.sendmail(FROM, [TO], body)
    server.quit()

def getMids():
#
# Return a list of mid's using the filter below.
#
    ts=twistserver.TwistServer()

    f=Filter()
    f.expression='(device_agent_status *=* "OK") &\
                    ((device_OS_Version *=* "Linux 5") | (device_OS_Version *=* "Linux 6")) &\
                    (device_Customer_Name = "UNIX") &\
                    (device_Platform_Name *=* "Red Hat ") &\
                    (device_hostname *<>* "uslv-papp-sat") &\
                    (device_hostname *<>* "uslv-papp-sam") &\
                    (device_hostname *<>* "usri-papp-spx01") &\
                    ((device_hostname *=* "uslv-") | (device_hostname *=* "usto-") | (device_hostname *=* "usri-"))'
    serverservice=ts.server.ServerService.findServerRefs(f)

    if len(serverservice) < 1 :
            print "Cannot find any servers"
            sys.exit(999)
    else:
            mids=[]
            for server in serverservice:
                    mids.append(ts.server.ServerService.getServerVO(server).mid)
    return mids

def getSystemId(mid):
#
# Return Satellite server ID if the server is connected to satellite.
#
    file="/opsw/.Server.ID/" + str(mid) + "/files/root/etc/sysconfig/rhn/systemid"
    print file
    try:
        f=open(file,"r")
        systemID=0
        for line in f:
            if re.match (".*ID-.*",line):
                x = re.match ("%sID-(\d+)%s" % ("<value><string>","</string></value>"),line)
                systemID=x.group(1)
        if systemID:
            print "systemid=>" + systemID
            return systemID
        else:
            return None
    except:
        return None

class satCon:
    """ This should be moved out to a shared library """
    def __init__(self):
        SATELLITE_URL = "https://uslv-papp-sat01.amgen.com/rpc/api"
        SATELLITE_LOGIN = "eistsadmin"
        SATELLITE_PASSWORD = "admin"
        self.client = xmlrpclib.Server(SATELLITE_URL, verbose=0)
        self.key = self.client.auth.login(SATELLITE_LOGIN, SATELLITE_PASSWORD)

    def listGlobals(self):
        return self.client.configchannel.listGlobals(self.key)

    def listChannels(self,systemid):
        return self.client.system.config.listChannels(self.key,systemid)

    def listFiles(self,systemid):
        return self.client.system.config.listFiles(self.key,systemid,1)

    def lookupFileInfo(self,systemid,path):
        return self.client.system.config.lookupFileInfo(self.key,systemid,path,1)

def getInfo(mid):
#
# Build a hash of server infomation with the mid being the key, now we have everything to start checking the satellite configs
#
    midinfo={}
    d={}
    for line in open ("/opsw/.Server.ID/" + str(mid) + "/info",'r'):
        k,v=line.strip().split(':',1)
        d[k.strip()] = v.strip()

    midinfo[mid] = d
    return midinfo

def chkSatFiles(mid,systemid):
    #
    # Return a list of sudoers files managed by satellite.
    #
    try:
        conn=satCon()
        fileList=[]
    except:
        print "Problem Connecting to the Satellite Server via the API"
        print "systemid=>" + systemid + ",mid=>" + mid
        print traceback.format_exc()
        sys.exit(999)

    try:
        satFiles=conn.listFiles(int(systemid))
        for file in satFiles:
            if re.match("^/etc/sudoers.d/|/etc/sudoers$", file['path']):
                fileList.append(file['path'])
    except:
        print traceback.format_exc()
        fileList.insert(0,"")
    return fileList

def chkLocalFiles(mid):
    #
    # Return a list of sudoers files on the server.
    #
    ogfs="/opsw/.Server.ID/" + str(mid) + "/files/root"
    ogfsfiles = glob.glob(ogfs + "/etc/sudoers.d/*")
    files=['/etc/sudoers']
    for file in ogfsfiles:
        files.append(file.replace(ogfs,""))
    return files

#
# Main
#
output = {'NOSAT' : [], 'NOFILES' : [], 'CONFLICT' : [], 'OK' : [], 'NOGFS' : []}
for mid in getMids():
    #
    # Gather Opsware and Satellite information the server.
    #
    info = getInfo(mid)

    print "Checking mid=>" + mid + " name=>" + info[mid]['name']

    if not os.path.isdir("/opsw/.Server.ID/" + str(mid) + "/files/root/tmp/"):
        output['NOGFS'].append(info[mid]['name'])
        print "NO OGFS"
        continue

    systemid = getSystemId(mid)
    #
    # Check system is connected to the Satellite server.
    #
    if systemid is None:
        print "No SystemID"
        output['NOSAT'].append(info[mid]['name'])
        continue
    #
    # Check system to see if the sudoers files are under Satellite control.
    #
    if not chkSatFiles(mid,systemid):
        print "Not under satellite control"
        output['NOFILES'].append(info[mid]['name'])
    else:
        #
        # Check to see if all files are managed by Satellite.
        #
        satelliteFiles=chkSatFiles(mid,systemid)
        localFiles=chkLocalFiles(mid)
        #
        # Check differences and report any extra files on the server.
        #
        x = list (sets.Set(localFiles)-sets.Set(satelliteFiles))
        if x:
            d={info[mid]['name'] : x}
            print str(d) + " Are not managed by satellite"
            output['CONFLICT'].append(d)
        else:
            print "All sudo files are managed by satellite"
            output['OK'].append(info[mid]['name'])
#
# Send the email if there are sudoer file conflicts.
#
if len(output['CONFLICT']) > 0:
    email=[]
    email.append('<H1>%s server(s) with sudo file conflicts.</H1>' % len(output['CONFLICT']))
    email.append('<P>All sudo files should be managed by the Satellite server! the following files do not appear to be under satellite control please investigate.</P>')
    for i in output['CONFLICT']:
        for k,v in i.iteritems():
            email.append('<B>' + str(k) + ' Please check the following files' + str(v) + '</B><BR>' )
    email.append('<HR><H2>Information only ...</H2></HR>')
    for i in output['NOGFS']:
        email.append(i + " NO OGFS<BR>")
    for i in output['OK']:
        email.append(i + " OK<BR>")
    for i in output['NOFILES']:
        email.append(i + ' Sudoers not under Satellite control<BR>')
    for i in output['NOSAT']:
        email.append(i + ' Not connected to the Satellite Server<BR>')
    sendmail('\n'.join(email),len(output['CONFLICT']))
    print ('\n'.join(email))
    print (email)
