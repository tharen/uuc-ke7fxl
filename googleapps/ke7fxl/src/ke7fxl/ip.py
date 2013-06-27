'''
Created on Dec 29, 2010

@author: Tod
'''

import os
import sys
import smtplib

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import mail

class IP(db.Model):
    """
    Represent a remote machine ip address as a google db object
    """
    name = db.StringProperty(multiline=False)
    address = db.StringProperty(multiline=False)
    date = db.DateTimeProperty(auto_now_add=True)
    
    def __str__(self):
        return '%s' % self.address
    
    def __repr__(self):
        #respond with a JSON serialization of IP
        out = '{\n'
        out += '  "name": "%s"\n' % self.name
        out += '  ,"address": "%s"\n' % self.address
        out += '  ,"date": "%s"\n' % self.date
        out += '}\n'
        
        return out
    
class IPApp(webapp.RequestHandler):
    def get(self):
        """
        Process an HTML get request by updating an ip address for <name> or 
        responding with the current machine <name> ip
        """
        self.response.headers['Content-Type'] = 'text/plain'
        
        #set the address based on the request
        addr = self.request.get('address')
        name = self.request.get('name').lower()
        use_remote = self.request.get('use_remote')
        notify_on_new = self.request.get('notify_on_new')
        
        ##TODO: Will appengine do boolean conversion?
        ##TODO: Check for IP different than most recent
        if use_remote:
            use_remote = bool(int(use_remote))
        
        if notify_on_new:
            notify_on_new = bool(int(notify_on_new))
        
        if name and addr:
            ip = IP()
            ip.name = name
            ip.address = addr
            ip.put()
            
        if name and use_remote:
            remote = os.environ['REMOTE_ADDR']
            ip = IP() 
            ip.name = name
            ip.address = remote
            ip.put()
        
        #if notify_on_new and self._lastIsNew(name):
        if self._lastIsNew(name):
            self._notify(name)
            
        self.echo(name)
    
    def _lastIsNew(self,name):
        """
        Compare the last two posted addresses
        """
        ips = db.GqlQuery("SELECT * FROM IP where name='%s' ORDER BY date DESC LIMIT 2" % (name,))
        
        if ips[0].address != ips[1].address:
            return True
        else:
            return False
    
    def _notify(self,name):
        host='smtp.gmail.com'
        port=587
        user='ke7fxl@gmail.com'
        pswd='2a2372'
        fromAddr='ke7fxl@gmail.com'
        toAddr='5034809307@txt.att.net'
        
        ip = db.GqlQuery("SELECT * FROM IP where name='%s' ORDER BY date DESC LIMIT 1" % (name,))[0]
                
        message = mail.EmailMessage()
        
        message.sender = fromAddr
        message.to = toAddr
        message.subject="IP Address"
        message.body = repr(ip)
        
        message.send()

    def echo(self,name):
        try:
            ip = db.GqlQuery("SELECT * FROM IP where name='%s' ORDER BY date DESC LIMIT 1" % (name,))[0]
            
        except:
            ip = IP()
            ip.name = name
            ip.address = '0.0.0.0'
        
        #echo the latest IP
        self.response.out.write(repr(ip))
    
    def post(self):
        return self.get()
        
application = webapp.WSGIApplication([
        ('/ip', IPApp)
        #, ('/sign', Guestbook)
        ],
        debug=True)

def main():
    run_wsgi_app(application)
    
if __name__=='__main__':
    main()