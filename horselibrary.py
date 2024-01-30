## LIBRARIES
from datetime import datetime, timedelta
import json
from requests_html import HTMLSession

## CONSTRUCTORS
class Provider:
    def __init__ (
        self,
        name,
        url,
        records,
        nav_tag,
        section_url_tag,
        section_id_tag,
        section_name_tag,
        section_available_tag,
        section_price_tag,
        section_teacher_tag,
        remove_if = []
        ):

        self.name = name
        self. url = url
        self.records = records
        self.nav_tag = nav_tag
        self.section_url_tag = section_url_tag
        self.section_id_tag = section_id_tag
        self.section_name_tag = section_name_tag
        self.section_available_tag = section_available_tag
        self.section_price_tag = section_price_tag
        self.section_teacher_tag = section_teacher_tag
        self.remove_if = remove_if

class Scrape:
    def __init__ (
        self,
        provider,
        records,
        purge_before,
        sections = [], 
        scrape_notices = []
        ):

        self.provider = provider
        self.records = records
        self.purge_before = purge_before
        self.sections = sections
        self.scrape_notices = scrape_notices

    def __str__(self):
        scrape_dictionary = self.get_dictionary()
        return str(scrape_dictionary)

    def __repr__(self):
        return str(self)

    def add_section(self, section):
        self.sections.append(section)

    def add_notice(self, notice):
        self.scrape_notices.append(notice)

    def get_dictionary(self):
        sections_list = []
        for section in self.sections:
            sections_list.append(section.get_dictionary())

        scrape_notices_list = []
        for scrape_notice in self.scrape_notices:
            scrape_notices_list.append(scrape_notice.get_dictionary())

        scrape_dictionary = {
            "provider": self.provider,
            "records": self.records,
            "purge_before": self.purge_before,
            "sections": sections_list,
            "scrape_notices": scrape_notices_list
        }
        return scrape_dictionary

class Section:
    def __init__ (
            self,
            provider_course_id,
            course_name,
            url,
            available_seats,
            price,
            sessions = [],
            location_type = "default",
            location = {},
            notes = "",
            teacher = "",
            enrollment_close_datetime = ""
        ):
    
        self.provider_course_id = provider_course_id
        self.course_name = course_name
        self.url = url
        self.available_seats = available_seats
        self.price = price
        self.sessions = sessions
        self.location_type = location_type
        self.location = location
        self.notes = notes
        self.teacher = teacher
        self.enrollment_close_datetime = enrollment_close_datetime

    def __str__(self):
        section_dictionary = self.get_dictionary()
        return str(section_dictionary)

    def __repr__(self):
        return str(self)

    def add_session(self, session):
        self.sessions.append(session)

    def get_dictionary(self):
        sessions_list = []
        for session in self.sessions:
            sessions_list.append(session.get_dictionary())
            
        section_dictionary = {
            "provider_course_id": self.provider_course_id,
            "course_name": self.course_name,
            "url": self.url,
            "available_seats": self.available_seats,
            "price": self.price,
            "sessions": sessions_list,
            "location_type": self.location_type,
            "location": self.location,
            "notes": self.notes, 
            "teacher": self.teacher,
            "enrollment_close_datetime": self.enrollment_close_datetime
        }
        return section_dictionary

class Session:
    def __init__ (
            self,
            date,
            start_time,
            end_time
        ):

        self.date = date
        self.start_time = start_time
        self.end_time = end_time

    def __str__(self):
        session_dictionary = self.get_dictionary()
        return str(session_dictionary)

    def __repr__(self):
        return str(self)

    def get_dictionary(self):
        session_dictionary = {
            "date": self.date,
            "start_time": self.start_time,
            "end_time": self.end_time       
        }
        return session_dictionary
        
## FUNCTIONS
def clean_urls(
    raw_urls: list,
    start: int = None,
    stop: int = None,
    step: int = 1,
    prefix: str = ""
    ):
    
    if start is None:
        start = 0
    if stop is None:
        stop = len(raw_urls)
        
    urls = list(map(lambda url: prefix + url, raw_urls[start:stop:step]))
    
    return urls
    
def create_new_dictionary(key_value_pairs):
    new_dictionary = {}
    for key, value in key_value_pairs:
        new_dictionary[key] = value
    return new_dictionary

def get_timestamp(form):
    tmp = datetime.now()
    timestamp = tmp.strftime(form)
    return timestamp

def extract_from_container(container, tag, attr):
    results = []
    # loop through items
    for item in container.find(tag):
        # extract link and add to list
        results.append(item.attrs[attr])

    # return results    
    return results

def extract_from_container_list(container_list, tag, attr):
    results = []
    # loop through items
    for container in container_list:
        # extract information and add to list
        result = container.find(tag, first=True).attrs[attr]
        results.append(result)

    # return results    
    return results    
 
def get_container_from_html(
    session,
    url: str,
    containertag: str
    ):
    
    # get html
    response = session.get(url)

    # if valid response
    if response.status_code == 200:
        # extract container
        container = response.html.find(containertag, first = True)

    # if error 
    else:
        # log error
        log_error_message("GET", url, response.status_code)

    # return container
    return container

def get_container_list_from_html(
    session,
    url: str,
    containertag: str,
    ):
    
    # get html
    response = session.get(url)

    # if valid response
    if response.status_code == 200:
        # extract container
        container_list = response.html.find(containertag)

    # if error 
    else:
        # log error
        log_error_message("GET", url, response.status_code)

    # return container
    return container_list

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
