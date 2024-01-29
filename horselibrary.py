## LIBRARIES
import json
from requests_html import HTMLSession
        
## FUNCTIONS
def create_new_dictionary(key_value_pairs):
    new_dictionary = {}
    for key, value in key_value_pairs:
        new_dictionary[key] = value
    return new_dictionary

def get_page_urls(session, url, navtag):
    response = session.get(url)
    status = response.status_code
    page_urls = []
    if status == 200:
        unordered_list = response.html.find(navtag, first=True)
        list_items = unordered_list.find('a')
        for item in list_items:
            page_urls.append(item.attrs['href'])
    else:
        log_error_message("GET", url, status)

    return page_urls

def get_course_urls(session, url, coursetag):
    response = session.get(url)
    status = response.status_code
    course_urls = []
    if status == 200:
        listings = response.html.find(coursetag)
        for listing in listings:
            some_urls = listing.find('a', first=True).attrs['href']
            course_urls.append(some_urls)
    else:
        log_error_message("GET", url, status)

    return course_urls

def log_error_message(action, url, status):
    print(f'{action} request from {url} returns status {status}')

def post_json_data(endpoint, data):
    # create an HTML session
    session = HTMLSession()

    # POST request to endpoint
    response = session.post(endpoint, json=data)

    # check status of request
    if response.status_code == 200:
        print("POST request received")
        print("Response:", response.text)
    else:
        print("POST request failed")
        print("Status code:", response.status_code)

    # close session
    session.close()

