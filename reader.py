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
        self.auth_url = "https://www.google.com/accounts/ClientLogin"
        self.re_auth = re.compile("SID=")
        self.sid = self.authenticate(self.login,self.password)
        self.header = {}
        self.header = self.create_header(self.header,self.sid)
        
    def authenticate(self,login,password):
        ''' method to authenticate to google'''
        parameters = {  'Email' : login,
                        'Passwd' : password,
                        'accountType' : 'HOSTED_OR_GOOGLE',
                        'service' : 'reader', 
                        'source' : 'googlereader2instapaper',
                        'continue': 'http://www.google.com' }
        headerdata = urllib.urlencode(parameters)
        try:
            request = urllib2.Request(self.auth_url, headerdata)
            response = urllib2.urlopen(request).read().split("\n")
            for r in response:
                if self.re_auth.match(r):
                    return r.split("=")[1]
        except IOError, e:
            print e
            return -1
    
    def create_header(self, header, sid):
        ''' Method to create the header which is used afterwards for authentication '''
        header = {'User-agent' : 'python'}
        header['Cookie'] = 'Name=SID;SID=%s;Domain=.google.com;Path=/;Expires=160000000000' % sid
        return header
        
    def get_starred_items(self,header,sid=False):
        ''' method to get starred items from google reader '''
        if sid:
            id = sid
        else:
            id = self.sid
        starred_url = "http://www.google.com/reader/atom/user/-/state/com.google/starred"
        try:
            request = urllib2.Request(starred_url, None, header)
            response = urllib2.urlopen(request).read()
            return response
        except IOError, e:
            print e
            return -1
        