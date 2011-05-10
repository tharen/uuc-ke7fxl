'''
Created on Nov 4, 2010

@author: Tod
'''

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.runtime import DeadlineExceededError
from google.appengine.ext import db

class DistanceMatrix:
    def __init__(self,locations):
        self.matrix = []
        for i in xrange(len(locations)):
            li = locations[i]
            self.matrix.append([0.0] * len(locations))
            for j in xrange(len(locations)):
                lj = locations[j]
                self.matrix[i][j] = self._calcdistance(li,lj)
    
    def _calcdistance(self,li,lj):
        xi,yi = li
        xj,yj = lj
        xd = (xi - xj) ** 2
        yd = (yi - yj) ** 2
        return (xd + yd) ** 0.5
    
class MainPage(webapp.RequestHandler):
    def get(self):
        try:
            keys = self.request.__dict__.keys()
            
            out = """
              <html>
                <body>
                  <br>"""
            
            out += '<br>'.join(['%s: %s' % (k,getattr(self.request,k)) for k in keys])
            
            out += """
                </body>
              </html>
              """
            
            self.response.out.write(out)
        
        except DeadlineExceededError:
            self.response.clear()
            self.response.set_status(500)
            self.response.out.write("Simanneal failed to complete in time")

    def post(self):
        try:
            
            self.response.write()
        
        except DeadlineExceededError:
            self.response.clear()
            self.response.set_status(500)
            self.response.out.write("Simanneal failed to complete in time")
            
application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/simanneal', MainPage),
                                      ],
                                     debug=True)

def main():
    run_wsgi_app(application)

def testDist():
    cases = 10
    import random
    locs = [()] * cases
    for i in range(cases):
        x = random.random() * 100
        y = random.random() * 100
        locs[i] = (x,y)
        
if __name__=='__main__':
    #main()
    
    testDist()