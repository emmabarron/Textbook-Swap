# Imports
import os
import json
import jinja2
import uber
import lyft
import api
import webapp2
import urllib
from google.appengine.api import urlfetch

jinja_env = jinja2.Environment(
    loader = jinja2.FileSystemLoader(os.path.dirname(__file__)),
    autoescape = True,
)

def format_seconds(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "%d:%02d:%02d" % (h, m, s)

def format_cost(number):
    if number % 1 == 0:
        return int(number)
    return number

def get_lyft_deeplink(start_lat, start_lon, end_lat, end_lon):
    api_url = "https://lyft.com/ride?id=lyft&pickup[latitude]={}&pickup[longitude]={}&partner={}&destination[latitude]={}&destination[longitude]={}"
    api_url = api_url.format(
        start_lat, start_lon, lyft.client_id, end_lat, end_lon
    )
    return api_url

def get_uber_deeplink(start_lat, start_lon, end_lat, end_lon, from_address, to_address):
    api_url = "https://m.uber.com/ul/?client_id={}&action=setPickup&pickup[latitude]={}&pickup[longitude]={}&pickup&pickup[formatted_address]{}&dropoff[latitude]={}&dropoff[longitude]={}&dropoff[formatted_address]{}"
    api_url = api_url.format(
        uber.client_id, start_lat, start_lon, urllib.urlencode({"": from_address}),
        end_lat, end_lon, urllib.urlencode({"": to_address})
    )
    return api_url

class GreetingsPage(webapp2.RequestHandler):
    def fetch_json(self, api_url, headers):
        try:
            result = urlfetch.fetch(
                api_url,
                headers = headers
            )
            if result.status_code == 200:
                return json.loads(result.content)
            else:
                self.response.status_code = result.status_code
        except urlfetch.Error:
            logging.exception('Caught exception fetching url')

        return {}

    def get_coords(self, address):
        #formatted_address = "+".join(address.split(" "))
        formatted_address = urllib.urlencode({"address": address})
        api_url = "https://maps.googleapis.com/maps/api/geocode/json?{}&key={}"
        api_url = api_url.format(formatted_address, api.key)
        jason = self.fetch_json(api_url, {})
        location = jason["results"][0]["geometry"]["location"]
        return location["lat"], location["lng"]

    def get_uber_estimates(self, start_lat, start_lon, end_lat, end_lon):
        api_url = "https://api.uber.com/v1.2/estimates/price?start_latitude={}&start_longitude={}&end_latitude={}&end_longitude={}"
        api_url = api_url.format(start_lat, start_lon, end_lat, end_lon)
        headers = {
            "Authorization": "Token {}".format(uber.server_token),
            "Accept-Language": "en_US",
            "Content-Type": "application/json"
        }
        return self.fetch_json(api_url, headers)

    def get_uber_estimate(self, ride_type, start_lat, start_lon, end_lat, end_lon):
        # Gets a price estimate for a specific ride type (documented as localized_display_name)
        estimates = self.get_uber_estimates(start_lat, start_lon, end_lat, end_lon)
        estimate = [estimate for estimate in estimates["prices"] if estimate["localized_display_name"] == ride_type][0]
        return estimate["estimate"]

    def get_uber_etas(self, start_lat, start_lon):
        api_url = "https://api.uber.com/v1.2/estimates/time?start_latitude={}&start_longitude={}"
        api_url = api_url.format(start_lat, start_lon)
        headers = {
            "Authorization": "Token {}".format(uber.server_token),
            "Accept-Language": "en_US",
            "Content-Type": "application/json",
        }
        return self.fetch_json(api_url, headers)

    def get_uber_eta(self, ride_type, start_lat, start_lon):
        etas = self.get_uber_etas(start_lat, start_lon)
        eta = [eta for eta in etas["times"] if eta["localized_display_name"] == ride_type]
        return format_seconds(eta[0]["estimate"])

    def get_lyft_estimates(self, start_lat, start_lon, end_lat, end_lon):
        api_url = 'https://api.lyft.com/v1/cost?start_lat={}&start_lng={}&end_lat={}&end_lng={}'
        api_url = api_url.format(start_lat, start_lon, end_lat, end_lon)
        headers = {
            "Authorization": "bearer {}".format(lyft.server_token),
        }
        return self.fetch_json(api_url, headers)

    def get_lyft_estimate(self, ride_type, start_lat, start_lon, end_lat, end_lon):
        api_url = 'https://api.lyft.com/v1/cost?start_lat={}&start_lng={}&end_lat={}&end_lng={}&ride_type={}'
        api_url = api_url.format(start_lat, start_lon, end_lat, end_lon, ride_type)
        headers = {
            "Authorization": "bearer {}".format(lyft.server_token),
        }
        jason = self.fetch_json(api_url, headers)
        ride = jason["cost_estimates"][0]
        min = format_cost(ride["estimated_cost_cents_min"]/100.0)
        max = format_cost(ride["estimated_cost_cents_max"]/100.0)
        return "${}-{}".format(min, max)

    def get_lyft_etas(self, start_lat, start_lon):
        api_url = 'https://api.lyft.com/v1/eta?lat={}&lng={}'
        api_url = api_url.format(start_lat, start_lon)
        headers = {
            "Authorization": "Bearer {}".format(lyft.server_token)
        }
        return self.fetch_json(api_url, headers)

    def get_lyft_eta(self, ride_type, start_lat, start_lon):
        api_url = 'https://api.lyft.com/v1/eta?lat={}&lng={}&ride_type={}'
        api_url = api_url.format(start_lat, start_lon, ride_type)
        headers = {
            "Authorization": "Bearer {}".format(lyft.server_token)
        }
        jason = self.fetch_json(api_url, headers)
        return format_seconds(jason["eta_estimates"][0]["eta_seconds"])

    def get(self):
        home_template = jinja_env.get_template("templates/index.html")
        self.response.write(home_template.render())# Home Page

class ResultsPage(webapp2.RequestHandler):
    def get(self):
        try:
            from_address = self.request.get("fromAddress")
            to_address = self.request.get("toAddress")
            results_page = jinja_env.get_template('templates/results.html')
            page = GreetingsPage()
            from_coords = (page.get_coords(from_address))
            to_coords = (page.get_coords(to_address))
            variables = {
                "ueta": page.get_uber_eta("UberX", from_coords[0], from_coords[1]),
                "leta": page.get_lyft_eta("lyft", from_coords[0], from_coords[1]),
                "ufare": page.get_uber_estimate("UberX", from_coords[0], from_coords[1], to_coords[0], to_coords[1]),
                "lfare": page.get_lyft_estimate("lyft", from_coords[0], from_coords[1], to_coords[0], to_coords[1]),
                "ldeeplink": get_lyft_deeplink(from_coords[0], from_coords[1], to_coords[0], to_coords[1]),
                "udeeplink": get_uber_deeplink(from_coords[0], from_coords[1], from_address, to_coords[0], to_coords[1], to_address),
                "from_address" : from_address, "to_address": to_address
            }
            del page
            self.response.write(results_page.render(variables))
        except Exception as e:
            print e
            self.redirect("/")

class TestPage(webapp2.RequestHandler):
    def get(self):
        self.response.write(get_lyft_deeplink(37.7833, -122.4167, 37.791, -122.405))

app = webapp2.WSGIApplication([
    ('/', GreetingsPage),
    ("/test", TestPage),
    ('/results', ResultsPage)
], debug=True)
