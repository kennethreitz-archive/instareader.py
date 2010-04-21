#!/usr/bin/env python
# encoding: utf-8

""" InstaReader.py -- Feeds Instapaper with Google Stars. Google makes the best Stars.
"""

from opster import command
import xml.dom.minidom
import sys, urllib, urllib2, re

class Instapaper:
	''' Base class for Instapaper connection'''
	
	def __init__(self, user, password):
		self.user = user
		self.password = password
		self.authurl = "https://www.instapaper.com/api/authenticate"
		self.addurl = "https://www.instapaper.com/api/add"
		
	def addItem(self, url, title=""):
		''' Method to add a new item to a instapaper account
			Returns 0 on success and -1 if something went wrong
		'''
		parameters = {'username' : self.user,'password' : self.password,'url' : url, 'title' : title}
		headerdata = urllib.urlencode(parameters)
		try:
			request = urllib2.Request(self.addurl, headerdata)
			response = urllib2.urlopen(request).read()
			if (int(response) == 201):
				return 0
			else:
				return -1
		except IOError, e:
			return -1
			
class GoogleReader:
	''' Simple Google Reader API wrapper'''
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
		parameters = {	'Email' : login,
						'Passwd' : password,
						'accountType' : 'HOSTED_OR_GOOGLE',
						'service' : 'reader',
						'source' : 'googlereader2instapaper',
						'continue': 'http://www.google.com'
					 }
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
		''' Create the authentication header '''
		header = {'User-agent' : 'python'}
		header['Cookie'] = 'Name=SID;SID=%s;Domain=.google.com;Path=/;Expires=160000000000' % sid
		return header

	def get_starred_items(self,count=60,header=None):
		''' method to get starred items from google reader 
			returns a list of hashmaps of the form
			item = { 
					'title' : "foo",
					'url' : "bla"
					'item' : "baz"
					'feed' : "bar"
				   }
		'''
		if header is None:
			header = self.header

		print count
		params = {
					'n' : count,
				 }

		starred_base_url = "http://www.google.com/reader/atom/user/-/state/com.google/starred"
		starred_url = starred_base_url + '?' + urllib.urlencode(params)
		try:
			request = urllib2.Request(starred_url, None, header)
			response = urllib2.urlopen(request).read()
			dom = xml.dom.minidom.parseString(response)
			try:
				entries = dom.getElementsByTagName("entry")
				for e in entries:
					item = { 'title' : "", 'url' : "" }
					title =	 e.getElementsByTagName("title")[0].firstChild.data.encode("utf-8")
					item['title'] = title
					links = e.getElementsByTagName("link")
					item['url'] = links[0].getAttribute("href")
					item_id = e.getElementsByTagName("id")
					item['item'] = item_id[0].firstChild.data.encode("utf-8")
					source = e.getElementsByTagName("source")
					item['feed'] = source[0].getAttribute("gr:stream-id")
					self.items.append(item)
				return self.items
			except ExpatError, er:
				print er
				return -2
		except IOError, e:
			print e
			return -2


	def remove_starred_item(self,item,feed,header=None):
		""" Method to remove the starred status from a reader item
		"""
		if header is None:
			header = self.header
		# Get edit token
		token = self.get_edit_token()
		post_args = {
						'client' : 'python',
						'r'		 : 'user/-/state/com.google/starred',
						'async'	 : 'true',
						's'		 : feed,
						'i'		 : item,
						'T'		 : token
					}
		# Basic edit url
		edit_base_url = "http://www.google.com/reader/api/0/edit-tag"
		edit_params = urllib.urlencode(post_args)
		#edit_url = edit_base_url + '?' + edit_params
		try:
			request = urllib2.Request(edit_base_url, edit_params, header)
			response = urllib2.urlopen(request).read()
			return response
		except IOError, e:
			print "Remove starred item error: %s" % e
			return -3

	def get_edit_token(self,header=None):
		"""method for get_edit_token"""
		token_url = "http://www.google.com/reader/api/0/token"
		if header is None:
			header = self.header

		try:
			request = urllib2.Request(token_url, None, header)
			response = urllib2.urlopen(request).read()
			return response
		except IOError, e:
			print "Get token error: %s" % e
			return -4

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

@command(usage='googlereader:auth instapaper:auth')
def main(rauth, iauth):
	'''Takes Google Reader's starred items and pushes them to instapaper. 
	'''
	
	gr = GoogleReader(*rauth.split(':'))
	instapaper = Instapaper(*iauth.split(':'))
	items = gr.get_starred_items(count='100',header=gr.header)
	# get items in the right temporal order
	items.reverse() 
	for i in items:
		instapaper.addItem(i['url'],i['title'])
		gr.remove_starred_item(item=i['item'],feed=i['feed'])

if __name__ == '__main__':
	main()
