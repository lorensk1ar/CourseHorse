## LIBRARIES
from datetime import datetime
from horselibrary import *

## FUNCTIONS
def get_actors_connection(session):
    # set url and tags for this provider
    provider_url = 'https://www.actorsconnection.com/classes/'
    provider_navigation_tag = 'ul.pagination'
    provider_course_tag = 'div.listing.clearfix'
    section_id_tag = 'h1'
    section_name_tag = 'h1'
    section_available_seats_tag = 'p.full-class'
    section_price_tag = "div.price"

    # create new provider dictionary
    provider = "actorsconnection.com"
    records = "all except seminars"

    # get time stamp
    tmp = datetime.now()
    timestamp = tmp.strftime("%Y-%m-%d %H:%M:%S")
    purge_before = timestamp

    scrape_key_value_pairs = [
        ("provider", provider),
        ("records", records),
        ("purge_before", purge_before),
        ("sections", []),  
        ("scrape_notices", [])
    ]
    
    new_scrape = create_new_dictionary(scrape_key_value_pairs)

    # get page links
    page_urls = get_page_urls(session, provider_url, provider_navigation_tag)

    # remove first & last
    page_urls = page_urls[1:-1]

    # add https to url
    page_urls = list(map(lambda url: "https:" + url, page_urls))
    
    # loop through pages
    section_urls = []
    for page_url in page_urls:
        # get section links
        some_urls = get_section_urls(session, page_url, provider_course_tag)

        # add to list
        section_urls += some_urls

    # add https to url
    section_urls = list(map(lambda url: "https:" + url, section_urls))
    
    # loop through section links
    for section_url in section_urls:
        # get section data
        section_data = session.get(section_url)
        
        # update session
        session_date = ""
        session_start_time = ""
        session_end_time = ""
        
        session_key_value_pairs = [
            ("date", session_date),
            ("start_time", session_start_time),
            ("end_time", session_end_time)
        ]
        
        new_session = create_new_dictionary(session_key_value_pairs)

        # update location
        location_name = ""
        location_street = ""
        location_street2 = ""
        location_city = ""
        location_state = ""
        location_zip = ""
        location_cross = ""
        
        location_key_value_pairs = [
            ("name", location_name),
            ("street_address", location_street),
            ("street_address2", location_street2),
            ("city", location_city),
            ("state", location_state),
            ("zip", location_zip),
            ("cross_streets", location_cross)
        ]
       
        new_location = create_new_dictionary(location_key_value_pairs)

        # update section
        # section id
        section_id = section_data.html.find(section_id_tag, first=True).text
        
        # section name
        section_name = section_data.html.find(section_name_tag, first=True).text

        # available seats
        section_full = section_data.html.find(section_available_seats_tag, first=True)

        if section_full:
            available_seats = 0
        else:
            available_seats = 5
        
        # section price
        price_text = section_data.html.find(section_price_tag, first=True).text

        if price_text == "Price: Free":
            section_price = float(0)

        else:
            try:
                prefix = "Price: $"
                price_strip = price_text[len(prefix):]
                section_price = float(price_strip)
            except:
                section_price = "N/A"

        section_key_value_pairs = [
            ("provider_course_id", section_id),
            ("course_name", section_name),
            ("url", section_url),
            ("available_seats", available_seats),
            ("price", section_price),
            ("sessions", [new_session]),
            ("location_type", "default"),
            ("location", new_location),
            ("notes", ""),
            ("teacher", ""),
            ("enrollment_close_datetime", "")
        ]
        
        new_section = create_new_dictionary(section_key_value_pairs)

        # update scrape notice
        scrape_notice_text = ""
        scrape_notice_url = section_url

        scrape_notice_key_value_pairs = [
            ("notice", scrape_notice_text),
            ("url", scrape_notice_url)
        ]

        new_scrape_notice = create_new_dictionary(scrape_notice_key_value_pairs)

        # add section and scrape notice if not seminar
        section_name_lowercase = section_name.lower()
        index = section_name_lowercase.find("seminar")
        if index == -1:
            if new_scrape['sections'] == []:
                new_scrape['sections'] = [new_section]
            else:
                new_scrape['sections'].append(new_section)

            if len(scrape_notice_text) == 0:
                   pass
            elif new_scrape['scrape_notices'] == []:
                new_scrape['scrape_notices'] = [new_scrape_notice]
            else:
                new_scrape['scrape_notices'].append(new_scrape_notice)

    # convert provider object to json object
    scrape_json = json.dumps(new_scrape)

    # endpoint = "https://horseshoe.coursehorse.com/sync"
    # post_json_data(endpoint, scrape_json)
    print(scrape_json)
    print("\n")

def get_all_providers():
    # initiate session session
    session = HTMLSession()

    # gather data
    get_actors_connection(session)

## MAIN
get_all_providers()
