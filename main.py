# Imports
import os
import json
import jinja2
import webapp2
import urllib
from google.appengine.api import urlfetch

jinja_env = jinja2.Environment(
    loader = jinja2.FileSystemLoader(os.path.dirname(__file__)),
    autoescape = True,
)

class GreetingsPage(webapp2.RequestHandler):
    def get(self):
        home_template = jinja_env.get_template("templates/index.html")
        self.response.write(home_template.render())# Home Page

class ResultsPage(webapp2.RequestHandler):
    def get(self):
        try:
            self.response.write(results_page.render())
        except Exception as e:
            print e
            self.redirect("/")

app = webapp2.WSGIApplication([
    ('/', GreetingsPage),
    ('/results', ResultsPage)
], debug=True)