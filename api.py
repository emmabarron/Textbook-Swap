from google.appengine.api import urlfetch
import json

openlibrary = "https://openlibrary.org/api/books?bibkeys=ISBN:{}&format=json"

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
    except urlfetch.Error:
        # logging.exception('Caught exception fetching url')
        pass

    return {}

def get_book(page, isbn):
    api_url = openlibrary.format(isbn)
    return fetch_json(page, api_url)