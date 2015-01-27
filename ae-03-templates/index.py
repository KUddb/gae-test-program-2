import os
import logging
import wsgiref.handlers
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from util.sessions import Session

# A Model for a User
class User(db.Model):
    acct = db.StringProperty()
    pw = db.StringProperty()
    name = db.StringProperty()


class MainHandler(webapp.RequestHandler):

  def get(self):
    path = self.request.path
    try:
        temp = os.path.join(os.path.dirname(__file__), 'templates' + path)
        outstr = template.render(temp, {'path':path})
        self.response.out.write(outstr)
    except:
        temp = os.path.join(os.path.dirname(__file__), 'templates/index.html')
        outstr = template.render(temp, {'path':path})
        self.response.out.write(outstr)

def doRender(handler, tname='index.html', values={}):
    temp = os.path.join(os.path.dirname(__file__),'templates/' + tname)
    if not os.path.isfile(temp):
        return False
    # Make a copy and add the path
    newval = dict(values)
    newval['path'] = handler.request.path
    outstr = template.render(temp, newval)
    handler.response.out.write(outstr)
    return True



class LoginHandler(webapp.RequestHandler):
    def get(self):
        doRender(self, 'loginscreen.html')

    def post(self):
      acct = self.request.get('account')
      pw = self.request.get('password')
      logging.info('Checking account='+acct+' pw='+pw)
      if pw == '' or acct == '':
          doRender(self,'loginscreen.html',{'error' : 'Please specify Acount and Password'} )
      elif pw == 'secret':
          doRender(self,'loggedin.html',{ } )
      else:
          doRender(self,'loginscreen.html',{'error' : 'Incorrect password'} )

class ApplyHandler(webapp.RequestHandler):
    def get(self):
      doRender(self, 'apply.html')

    def post(self):
      self.session = Session()
      xname = self.request.get('name')
      xacct = self.request.get('account')
      xpw = self.request.get('password')

      # Check for a user already existing
      que = db.Query(User).filter("acct =",xacct)
      results = que.fetch(limit=1)

      if len(results) > 0 :
          doRender(self,"apply.html",{'error' : 'Account Already Exists'} )
          return

      newuser = User(name=xname, acct=xacct, pw=xpw);
      newuser.put();
      self.session['username'] = xacct
      doRender(self,"index.html",{ })

class MembersHandler(webapp.RequestHandler):
    def get(self):
      doRender(self, 'members.html')

    def get(self):
      que = db.Query(User)
      user_list = que.fetch(limit=100)
      doRender(self, "members.html", {'user_list': user_list})




application = webapp.WSGIApplication([
        ('/login', LoginHandler),
        ('/apply', ApplyHandler),
        ('/members', MembersHandler),
        ('/.*', MainHandler)
    ])

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

