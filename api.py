from google.appengine.api import urlfetch
import json

openlibrary = "https://openlibrary.org/api/books?bibkeys=ISBN:{}&format=json"
googlebooks = "https://www.googleapis.com/books/v1/volumes?q=isbn:{}&key=AIzaSyAyZMulstKQKPSV4Pm9zKoJB8OIQJRrXT4"

# page is the self object inside of a requesthandler
def fetch_json(page, api_url, headers={}):
    try:
        result = urlfetch.fetch(
            api_url,
            headers = headers
        )
        if result.status_code == 200:
            return json.loads(result.content)
        else:
            page.response.status_code = result.status_code
    except urlfetch.Error as e:
        print e
        # logging.exception('Caught exception fetching url')
        pass

    return {}

def get_book(page, isbn):
    api_url = googlebooks.format(isbn) # openlibrary.format(isbn)
    return fetch_json(page, api_url)