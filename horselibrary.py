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
        page_url_tag,
        section_url_tag,
        section_id_tag,
        section_name_tag,
        section_available_tag,
        section_price_tag,
        section_teacher_tag,
        page_url_start = None,
        page_url_stop = None,
        url_prefix = "",
        default_session_length = 2,
        remove_if = []
        ):

        self.name = name
        self. url = url
        self.records = records
        self.page_url_tag = page_url_tag
        self.section_url_tag = section_url_tag
        self.section_id_tag = section_id_tag
        self.section_name_tag = section_name_tag
        self.section_available_tag = section_available_tag
        self.section_price_tag = section_price_tag
        self.section_teacher_tag = section_teacher_tag
        self.page_url_start = page_url_start
        self.page_url_stop = page_url_stop
        self.url_prefix = url_prefix
        self.default_session_length = default_session_length
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
    
    '''
    if start is None:
        start = 0
    if stop is None:
        stop = len(raw_urls)
    '''
        
    urls = list(map(lambda url: prefix + url, raw_urls[start:stop:step]))
    
    return urls
    
def create_new_dictionary(key_value_pairs):
    new_dictionary = {}
    for key, value in key_value_pairs:
        new_dictionary[key] = value
    return new_dictionary

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
 
def fetch_all(session, url):
    response = session.get(url)
    return response

def fetch_container(
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

def fetch_container_list(
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

def fetch_page_url_list(
    session,
    provider_url,
    page_url_tag):
    
    page_list_container = fetch_container(
        session,
        provider_url,
        page_url_tag,
        )

    page_urls = extract_from_container(
        page_list_container,
        tag = 'a',
        attr = 'href')

    return page_urls

def fetch_section_url_list(
    session,
    page_urls,
    section_url_tag
    ):

    # loop through pages
    section_urls = []
    for page_url in page_urls:
        section_container_list = fetch_container_list(
            session,
            page_url,
            section_url_tag,
        )

        some_urls = extract_from_container_list(
            section_container_list,
            tag = 'a',
            attr = 'href')
        
        section_urls += some_urls

    return section_urls

def get_section_urls(session, provider):
    raw_page_urls = fetch_page_url_list(
        session,
        provider.url,
        provider.page_url_tag
        )

    page_urls = clean_urls(
        raw_urls = raw_page_urls,
        start = provider.page_url_start,
        stop = provider.page_url_stop,
        prefix = provider.url_prefix
        )

    raw_section_urls = fetch_section_url_list(
        session,
        page_urls,
        provider.section_url_tag
        )

    section_urls = clean_urls(
        raw_section_urls,
        prefix = provider.url_prefix
        )

    return section_urls

def get_timestamp(form):
    tmp = datetime.now()
    timestamp = tmp.strftime(form)
    return timestamp

def is_valid_section(section, provider):
    if section.price == 0:
        return False

    if section.price == 9999.99:
        return False

    section_name_lowercase = section.course_name.lower()
    for item in provider.remove_if:
        item_lowercase = item.lower()
        index = section_name_lowercase.find(item_lowercase)
        if index >= 0:
            return False
        
    return True

def log_error_message(action, url, status):
    print(f'{action} request from {url} returns status {status}')

def parse_sessions_data(response, provider):
    sessions_list = []

    sessions_html = response.html.find('td')
    sessions_text = [item.text for item in sessions_html]
    item_count = len(sessions_text)
    for i in range(0, item_count, 2):
        # determine data
        date_text = sessions_text[i]
        date_value = datetime.strptime(date_text, "%A, %B %d, %Y").date()
        session_date = date_value.strftime("%Y-%m-%d")
        
        # determine start time
        start_time_text = sessions_text[i+1]
        start_time_value = datetime.strptime(start_time_text, "%I:%M %p").time()
        session_start_time = start_time_value.strftime("%H:%M:%S")

        # determine end time
        # use default length if necessary
        end_time_value = (datetime.combine(datetime.min, start_time_value) + timedelta(hours = provider.default_session_length)).time()
        session_end_time = end_time_value.strftime("%H:%M:%S")
        
        # construct session object
        new_session = Session(session_date, session_start_time, session_end_time)

        # add to sessions list
        sessions_list.append(new_session)

    return sessions_list

def parse_section_data(url, response, provider):
    # parse course id
    section_id = response.html.find(provider.section_id_tag, first = True).attrs["content"]

    # parse course name
    section_name = response.html.find(provider.section_name_tag, first = True).attrs["content"]

    # parse course url
    section_url = url

    # parse available seats
    section_full = response.html.find(provider.section_available_tag, first = True)

    if section_full:
        available_seats = 0
    else:
        available_seats = 5
    
    # parse price
    price_text = response.html.find(provider.section_price_tag, first = True).text
    original_text = price_text[0:]

    print(section_url)
    print(price_text)
    
    section_notes = ""

    # remove initial word
    prefix = "Price: "
    prefix_index = price_text.find(prefix)
    if prefix_index == 0:
        price_text = price_text[len(prefix):]

    # remove any trailing words
    newline_index = price_text.find("\n")
    if newline_index > 0:
        section_notes = price_text[newline_index:]
        section_notes = section_notes.strip()
        price_text = price_text[:newline_index]
            
    # convert "Free" to "0"
    if price_text == "Free":
        price_text = "0"

    try:
        price_text = price_text.strip("$")
        section_price = float(price_text)

    except:
        section_price = 9999.99
        section_notes = original_text
        
    print(price_text)
    print(section_price)
    print(section_notes)
    print("\n")


    # parse sessions
    sessions_list = parse_sessions_data(response, provider)

    '''
    # parse location

    # parse notes

    # parse teacher
    tmp = response.html.find(provider.section_teacher_tag)
    session_teacher = tmp[-1].text

    # parse enrollment close
    '''

    new_section = Section(
        provider_course_id = section_id,
        course_name = section_name,
        url = section_url,
        available_seats = available_seats,
        price = section_price,
        sessions = sessions_list,
        notes = section_notes)

    return new_section

def post_json_data(endpoint, data):
    # create an HTML session
    session = HTMLSession()

    # POST request to endpoint
    response = session.post(endpoint, json=data)

    # check status of request
    if response.status_code == 200:
        ("POST request received")
        print("Response:", response.text)
    else:
        print("POST request failed")
        print("Status code:", response.status_code)

    # close session
    session.close()



