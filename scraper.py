## FUNCTIONS
def create_new_dict():
    dict = {
        "provider": None,
        "records": None,
        "purge_before": None,
        "sections": [
          {
            "provider_course_id": None,
            "course_name": None,
            "url": None,
            "available_seats": None,
            "price": None,
            "sessions": [
              {
                "date": None,
                "start_time": None,
                "end_time": None
              }
            ],
            "location_type": None,
            "location": {
                "name": None,
                "street_address": None,
                "street_address2": None,
                "city": None,
                "state": None,
                "zip": None,
                "cross_streets": None
                },
            "notes": None,
            "teacher": None,
            "enrollment_close_datetime": None,
          }
        ],
        "scrape_notices": [
          {
            "notice": None,
            "url": None
          }
        ]
    }

    return dict

def post_json_data(endpoint, data):
    # create an HTML session
    session = HTMLSession()

    try:
        # POST request to endpoint
        response = session.post(endpoint, json=data)

        # check status of request
        if response.status_code == 200:
            print("POST request received")
            print("Response:", response.text)
        else:
            print("POST request failed")
            print("Status code:", response.status_code)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # close the session
        session.close()


def get_actors_connection():
    # initiate html session
    session = HTMLSession()

    # set url for this provider
    provider = 'https://www.actorsconnection.com/classes/'
    
    # determine how many pages
    response = session.get(provider)
    class_count_html = response.html.find('p.nav_text', first=True)
    class_count_text = class_count_html.text
    class_count_list = class_count_text.split()
    class_count_string = class_count_list[-1]
    class_count = int(class_count_string)
    page_count = math.ceil(class_count / 20)


    # loop through pages
    # for page in range(1, page_count + 1):
    for page in range(1, 1 + 1):
        response = session.get(provider + 'page/' + str(page) + '/')
        listings = response.html.find('div.listing.clearfix')

        # loop through classes on page
        for listing in listings:
            link = listing.find('a', first=True).attrs['href']
            url = "https:" + link
            
            # initialize empty json object
            dict = create_new_dict()

            # request class data
            data = session.get(url)
            
            # parse class data & update json
            # course_name
            tag = "h1"
            dict["sections"][0]["course_name"] = data.html.find(tag, first=True).text
    
            # url
            dict["sections"][0]["url"] = url

            # available_seats incl date
    
            # price
            tag = "div.price"
            price_text = data.html.find(tag, first=True).text

            if price_text == "Free":
                price = 0

            else:
                try:
                    price_strip = price_text[1:]
                    price = float(price_strip)
                except:
                    price = None

            dict["sections"][0]["price"] = price

            # post json object
            # json_data = json.dumps(dict)
            # post_url = "https://horseshoe.coursehorse.com/sync"
            # post_json_data(post_url, json = json_data):

def get_all_providers():
    get_actors_connection()

## MAIN
import json
import math
from requests_html import HTMLSession

get_all_providers()
