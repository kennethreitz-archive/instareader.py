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
        self.sid = ""
        self.re_username = re.compile("Auth=")
        
    def authenticate(self,login,password):
        ''' method to authenticate to google'''
        parameters = {'Email' : login,'Passwd' : password,'accountType' : 'HOSTED_OR_GOOGLE',
                        'service' : 'reader', 'source' : 'googlereader2instapaper' }
        headerdata = urllib.urlencode(parameters)
        try:
            request = urllib2.Request(self.authurl, headerdata)
            response = urllib2.urlopen(request).read()
            return response
        except IOError, e:
            return -1