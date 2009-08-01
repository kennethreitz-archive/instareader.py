#
# class to authenticate to google and get items from
# google reader
#
#
import urllib
import urllib2
import re

class GoogleReader:
    ''' class for connecting to google'''
    def __init__(self, login, password):
        self.login = login
        self.password = password
        self.authurl = "https://www.google.com/accounts/ClientLogin"
        self.re_auth = re.compile("Auth=")
        self.sid = self.authenticate(self.login,self.password)
        
    def authenticate(self,login,password):
        ''' method to authenticate to google'''
        parameters = {'Email' : login,'Passwd' : password,'accountType' : 'HOSTED_OR_GOOGLE',
                        'service' : 'reader', 'source' : 'googlereader2instapaper' }
        headerdata = urllib.urlencode(parameters)
        try:
            request = urllib2.Request(self.authurl, headerdata)
            response = urllib2.urlopen(request).read().split("\n")
            for r in response:
                if self.re_auth.match(r):
                    return r.split("=")[1]
        except IOError, e:
            print e
            return -1