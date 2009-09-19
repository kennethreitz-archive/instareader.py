#
# class to authenticate to google and get items from
# google reader
#
#
import urllib
import urllib2
import re
import xml.dom.minidom
import sys

class GoogleReader:
    ''' class for connecting to google'''
    def __init__(self, login, password):
        self.login = login
        self.password = password
        self.auth_url = "https://www.google.com/accounts/ClientLogin"
        self.re_auth = re.compile("SID=")
        self.sid = self.authenticate(self.login,self.password)
        if self.sid == -1:
            print "Authentication unsuccessful. Exiting."
            sys.exit(-1)

        self.header = {}
        self.header = self.create_header(self.header,self.sid)
        self.items = []
        
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
            print "Authenticate error %s" % e
            return -1
    
    def create_header(self, header, sid):
        ''' Method to create the header which is used afterwards for authentication '''
        header = {'User-agent' : 'python'}
        header['Cookie'] = 'Name=SID;SID=%s;Domain=.google.com;Path=/;Expires=160000000000' % sid
        return header
        
    def get_starred_items(self,header,sid=False):
        ''' method to get starred items from google reader 
            returns a list of hashmaps of the form
            item = { 
                    'title' : "foo",
        	        'url' : "bla"
        	       }
        '''
        if sid:
            id = sid
        else:
            id = self.sid
        starred_url = "http://www.google.com/reader/atom/user/-/state/com.google/starred"
        try:
            request = urllib2.Request(starred_url, None, header)
            response = urllib2.urlopen(request).read()
            dom = xml.dom.minidom.parseString(response)
            entries = dom.getElementsByTagName("entry")
            for e in entries:
                item = { 'title' : "", 'url' : "" }
                title =  e.getElementsByTagName("title")[0].firstChild.data.encode("utf-8")
                item['title'] = title
                links = e.getElementsByTagName("link")
                item['url'] = links[0].getAttribute("href")
                self.items.append(item)
            return self.items
        except IOError, e:
            print e
            return -1

    def get_subscription_list(self, header):
        ''' Generic Method for getting data from google reader
        '''
        url = 'http://www.google.com/reader/api/0/subscription/list'
        # retrieve data here
        try:
            request = urllib2.Request(url, None, header)
            response = urllib2.urlopen(request).read()
            return response
        except IOError, e:
            print e
            return -5

