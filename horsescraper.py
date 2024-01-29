## LIBRARIES
from horselibrary import *

## FUNCTIONS
def get_actors_connection(session):
    # set url and tags for this provider
    provider_url = 'https://www.actorsconnection.com/classes/'
    provider_navigation_tag = 'ul.pagination'
    provider_course_tag = 'div.listing.clearfix'
    course_id_tag = 'h1'
    course_name_tag = 'h1'
    course_available_tag = 'p.full-class'
    course_price_tag = "div.price"

    # get page links
    page_urls = get_page_urls(session, provider_url, provider_navigation_tag)

    # remove first & last
    page_urls = page_urls[1:-1]

    # add https to url
    page_urls = list(map(lambda url: "https:" + url, page_urls))
    
    # loop through pages
    course_urls = []
    for page_url in page_urls:
        # get course links
        some_urls = get_course_urls(session, page_url, provider_course_tag)

        # add to list
        course_urls += some_urls

    # add https to url
    course_urls = list(map(lambda url: "https:" + url, course_urls))
    
    # loop through class links
    for course_url in course_urls:
        # create new course dictionary
        course_key_value_pairs = [
            ("provider", "actorsconnection.com"),
            ("records", ""),
            ("purge_before", ""),
            ("sections", []),  
            ("scrape_notices", [])
        ]
        
        new_course = create_new_dictionary(course_key_value_pairs)
        
        # get course data
        course_data = session.get(course_url)

        # parse course data
        # course id
        course_id = course_data.html.find(course_id_tag, first=True).text
        
        # course name
        course_name = course_data.html.find(course_name_tag, first=True).text

        # available seats
        course_full = course_data.html.find(course_available_tag, first=True)

        if course_full:
            available_seats = 0
        else:
            available_seats = 5
        
        # course price
        price_text = course_data.html.find(course_price_tag, first=True).text

        if price_text == "Price: Free":
            course_price = float(0)

        else:
            try:
                prefix = "Price: $"
                price_strip = price_text[len(prefix):]
                course_price = float(price_strip)
            except:
                course_price = "N/A"
        
        # update section
        section_key_value_pairs = [
            ("provider_course_id", course_id),
            ("course_name", course_name),
            ("url", course_url),
            ("available_seats", available_seats),
            ("price", course_price),
            ("sessions", []),
            ("location_type", "default"),
            ("location", {}),
            ("notes", ""),
            ("teacher", ""),
            ("enrollment_close_datetime", "")
        ]
        
        new_section = create_new_dictionary(section_key_value_pairs)
        new_course['sections'] = [new_section]

        # update session

        # update location

        # update scrape notice

        # convert course object to json object
        course_json = json.dumps(new_course)

        # post json object if not seminar
        course_name_lowercase = course_name.lower()
        index = course_name_lowercase.find("seminar")

        valid = True
        if index >= 0:
            valid = False
        
        if valid:
            # endpoint = "https://horseshoe.coursehorse.com/sync"
            # post_json_data(endpoint, course_json)
            print(course_json)
            print("\n")

def get_all_providers():
    # initiate session session
    session = HTMLSession()

    # gather data
    get_actors_connection(session)

## MAIN
get_all_providers()

