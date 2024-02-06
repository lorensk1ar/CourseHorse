'''
## NOTES
adds course ids
sends separate scrape json for each page with purge before for each page!

## TO DO
use session length to intuit session end times
classes with email address as location?
need to fix classes that start at 16:00? end at 01:00?

'''

### LIBRARIES
from datetime import datetime, timedelta
import json
import math
from requests_html import HTMLSession

### FUNCTIONS
def scrape_actors_connection():
    ## set constants
    provider_url = "https://www.actorsconnection.com/classes/"
    url_prefix = "https:"
    default_seats = 6
    default_session_hours = 2

    ## get time stamp
    tmp = datetime.now()
    purge_before = tmp.strftime("%Y-%m-%d %H:%M:%S")

    ## open html session
    html_session = HTMLSession()

    ## get section links
    # create list for page urls
    raw_page_urls = []

    # fetch page links
    response = html_session.get(provider_url)

    # if valid response
    if response.status_code == 200:
        # extract page containers
        page_container = response.html.find("ul.pagination", first = True)

        # loop through items in page container
        for item in page_container.find('a'):
            # extract page url and add to list
            raw_page_urls.append(item.attrs['href'])

    # if error 
    else:
        # log error
        log_error_message("GET", provider_url, response.status_code)

    # clean page urls
    page_urls = list(map(lambda url: url_prefix + url, raw_page_urls[1:-1]))
    
    # loop through page links    
    for page_index, page_url in enumerate(page_urls):
        # set page number
        page_number = page_index + 1
        
        # create list for section data
        sections_data = []
    
        # fetch section links
        response = html_session.get(page_url)

        # if valid response
        if response.status_code == 200:
            # extract section containers       
            section_containers = response.html.find('div.listing')

            # loop through section containers
            for section_container in section_containers:
                # extract section url from container
                item = section_container.find('a', first=True)
                if item:
                    raw_section_url = item.attrs['href']
                else:
                    raw_section_url = ""

                # clean section url
                section_url = url_prefix + raw_section_url
                
                # extract section price from container
                item = section_container.find('span.price', first=True)
                if item:
                    section_price = item.text
                else:
                    section_price = ""
                    
                # extract warning label from container
                item = section_container.find('span.label', first=True)
                if item:
                    section_warning = item.text
                else:
                    section_warning = ""
            
                # add section to list
                section_data = (section_url, section_price, section_warning)
                sections_data.append(section_data)
                
        # if error 
        else:
            # log error
            log_error_message("GET", page_url, response.status_code)

    
        # create list for sections
        sections = []

        ## get section information
        # loop through sections
        for section_data in sections_data:
            section_url, price_text, section_warning = section_data
            
            # fetch section data
            response = html_session.get(section_url)

            # parse course id
            section_id = ""
            pid_container = response.html.find('input[name="pid"]', first=True)
            if pid_container:
                section_id = pid_container.attrs['value']

            # parse course name
            section_name = response.html.find('meta[property="og:title"]', first = True).attrs["content"]

            # parse available seats
            if section_warning == "Sold Out!":
                available_seats = 0

            elif section_warning == "1 spot left":
                available_seats = 1

                
            elif section_warning == "2 spots left":
                available_seats = 2

            elif section_warning == "3 spots left":
                available_seats = 3

            elif section_warning == "Only a few spaces left":
                available_seats = 4

            else:
                available_seats = default_seats

            # parce price
            if price_text[0] == "$":
                section_price = float(price_text[1:])
            else:
                section_price = 0

            # parce location type
            location_type= "default"

            # parce location
            section_location = {}

            # parce sessions
            sessions = []

            session_container = response.html.find('td')
            sessions_items = [item.text for item in session_container]
            item_count = len(sessions_items)
            for i in range(0, item_count, 2):
                # determine data
                date_text = sessions_items[i]
                date_value = datetime.strptime(date_text, "%A, %B %d, %Y").date()
                session_date = date_value.strftime("%Y-%m-%d")
                
                # determine start time
                start_time_text = sessions_items[i+1]
                start_time_value = datetime.strptime(start_time_text, "%I:%M %p").time()
                session_start_time = start_time_value.strftime("%H:%M:%S")

                # determine end time
                # use default length if necessary
                end_time_value = (datetime.combine(datetime.min, start_time_value) + timedelta(hours = default_session_hours)).time()
                session_end_time = end_time_value.strftime("%H:%M:%S")

                # construct new session
                session = {
                    "date": session_date,
                    "start_time": session_start_time,
                    "end_time": session_end_time
                }

                # add to session list
                sessions.append(session)

            # parse notes:
            section_notes = ""

            # parse teacher(s):
            teachers = response.html.find('h2')

            section_teacher = ""
            for teacher in teachers:
                # extract text
                teacher_text = teacher.text
                
                # if no text
                if teacher_text == "":
                    pass

                # if instruction
                elif teacher_text[-1] == ":" :
                    pass

                # if Q&A
                elif teacher_text[0:3] == "Q&A" :
                    pass

                # if Hi!
                elif teacher_text[0:3] == "Hi!" :
                    pass
                    
                # if teacher
                else:
                    # if not first teacher, add comma
                    if section_teacher:
                        section_teacher += ", "
                        
                    # add teacher
                    section_teacher += teacher_text

            # parse enrollment close
            enrollment_close = ""

            # construct new section
            section = {
                "provider_course_id": section_id,
                "course_name": section_name,
                "url": section_url,
                "available_seats": available_seats,
                "price": section_price,
                "sessions": sessions,
                "location_type": location_type,
                "location": section_location,
                "notes": section_notes,
                "teacher": section_teacher,
                "enrollment_close_datetime": enrollment_close,
                }

            # check if section is valid & if valid add to sections list
            valid = True

            if available_seats == 0:
                valid = False

            if section_price == 0:
                valid = False

            section_name_lowercase = section_name.lower()
            index = section_name_lowercase.find("seminar")
            if index >= 0:
                valid = False
                
            if valid:
                sections.append(section)

        ## parse records
        records = "Page " + str(page_number)
    
        ## construct new scrape
        scrape = {
            "provider": "Actors Connection",
            "records": records,
            "purge_before": purge_before,
            "sections": sections,
            "scrape_notes": [] 
        }

        ## write to file
        scrape_json = json.dumps(scrape)
        provider_no_spaces = scrape["provider"].replace(" ", "")
        file_path = provider_no_spaces + str(page_number) + ".json"
        
        with open(file_path, 'w') as json_file:
            json.dump(scrape_json, json_file)
    
        ## print
        # indented_json = json.dumps(scrape, indent=2)
        # print(indented_json)
        
        print(f"{len(scrape['sections'])} sections found", "\n")

def scrape_big_apple_safety():
    # set constants
    provider_url = "https://baos.com/training-safety-course/"
    url_prefix = ""
    default_seats = 25
    default_session_hours = 9

    # get time stamp
    tmp = datetime.now()
    purge_before = tmp.strftime("%Y-%m-%d %H:%M:%S")

    # open html session
    html_session = HTMLSession()

    # fetch first page
    next_url = provider_url
    navigation_response = html_session.get(next_url)
    page_number = 1
    
    # while next link exist
    while next_url:
        # if valid response
        if navigation_response.status_code == 200:
            # create list for sections
            sections = []
            
            # loop through sections
            articles = navigation_response.html.find('article')
            for article in articles:                
                # extract section url
                section_container = article.find('h2.entry-title', first=True)
                section_url = section_container.find('a', first=True).attrs['href']

                # fetch section 
                section_response = html_session.get(section_url)

                # extract section id
                section_id = ""
                id_container = section_response.html.find('input[name="inpCourseId"]', first=True)
                if id_container:
                    section_id = id_container.attrs['value']
                
                # extract section name
                section_name = ""
                name_container = section_response.html.find('input[name="inpCourseName"]', first=True)
                if name_container:
                    section_name = name_container.attrs['value']
                    
                # parse available seats
                available_seats = default_seats

                # parse price
                cost_container = section_response.html.find('input#costInput', first=True)
                if cost_container:
                    cost_value = cost_container.attrs['value']
                    section_price = float(cost_value[1:])

                # parse location type
                location_type = "default"

                # parse location
                section_location = {}

                # parse sessions
                # create list for sessions
                sessions = []

                # extract length of session
                session_length_days = 1
                session_length_hours = default_session_hours
                
                length_element = section_response.html.find('input[name="inpCourseLength"]', first=True)
                if length_element:
                    session_length_text = length_element.attrs['value']
                    quantity, unit = session_length_text.split()
                    quantity = float(quantity)
                    unit = unit.lower()

                    if unit in ["hour", "hours"]:
                        if quantity <= 6:
                            session_length_days = 1
                            session_length_hours = quantity

                        elif quantity == 10:
                            session_length_days = 1
                            session_length_hours = 11
                            
                        else:
                            session_length_days = math.ceil(quantity / 8)
                            session_length_hours = 9

                    if unit in ["day", "days"]:
                        session_length_days = math.ceil(quantity)
                        session_length_hours = 9

                # extract session drop down
                session_online = False
                session_date = ""
                session_start_time = "08:00:00"
                session_end_time = "17:00:00"
                                        
                select_element = section_response.html.find('select[name="inpCourseShedule"]', first=True)
                if select_element:
                    option_elements = select_element.find('option')

                    # loop through session options
                    for option in option_elements:

                        if option.text in ["ONLINE ANYTIME"]:
                            session_online = True
                    
                        if session_online:
                            session_date = "online anytime"
                            session_start_time = "00:00:00"
                            session_end_time = "00:00:00"

                        else:
                            option_value = option.attrs['value']
                            date_text, start_time_text, _ = option_value.split('|')

                            date_value = datetime.strptime(date_text, "%Y-%m-%d").date()
                            session_date = date_value.strftime("%Y-%m-%d")
                    
                            start_time_value = datetime.strptime(start_time_text, "%I:%M %p").time()
                            session_start_time = start_time_value.strftime("%H:%M:%S")

                            end_time_value = (datetime.combine(date_value, start_time_value) +
                                              timedelta(days = session_length_days - 1) +
                                              timedelta(hours = session_length_hours)).time()
                            session_end_time = end_time_value.strftime("%H:%M:%S")

                        session = {
                            "date": session_date,
                            "start_time": session_start_time,
                            "end_time": session_end_time
                        }

                        '''
                        ### REMOVE ###
                        if session_start_time != "16:00:00":
                            print(section_url)
                            print(session_online)
                            print(option_value)
                            print(session_length_text)
                            print(session_date, session_start_time, session_end_time)
                            print()
                        ### REMOVE ###
                        '''

                        # add to session list
                        sessions.append(session)

                # parse notes
                section_notes = ""

                # parse teachers
                section_teacher = ""

                # parse enrollment close
                enrollment_close = ""

                # construct new section
                section = {
                    "provider_course_id": section_id,
                    "course_name": section_name,
                    "url": section_url,
                    "available_seats": available_seats,
                    "price": section_price,
                    "sessions": sessions,
                    "location_type": location_type,
                    "location": section_location,
                    "notes": section_notes,
                    "teacher": section_teacher,
                    "enrollment_close_datetime": enrollment_close,
                }

                # add to sections list
                sections.append(section)

            # parse records
            records = "Page " + str(page_number)

            # construct new scrape
            scrape = {
                "provider": "Big Apple Occupational Safety",
                "records": records,
                "purge_before": purge_before,
                "sections": sections,
                "scrape_notes": [] 
            }

            ## write to file
            scrape_json = json.dumps(scrape)
            provider_no_spaces = scrape["provider"].replace(" ", "")
            file_path = provider_no_spaces + str(page_number) + ".json"
            
            with open(file_path, 'w') as json_file:
                json.dump(scrape_json, json_file)

            ## print

            ### REMOVE ###
            from random import randint
            count = len(scrape["sections"])
            index = randint(0, count - 1)
            tmp = scrape["sections"][index]
            indented_json = json.dumps(tmp, indent=2)
            print(indented_json)
            ### REMOVE ###

            # indented_json = json.dumps(scrape, indent=2)
            # print(indented_json)
            
            print(f"{len(scrape['sections'])} sections found", "\n")
            
            # extract link for next page
            next_url_container = navigation_response.html.find('link[rel="next"]', first = True)
                
            # if next page exists
            if next_url_container:
                # extract url for next page
                next_url = next_url_container.attrs['href']

                # fetch next page
                navigation_response = html_session.get(next_url)

                # increment page number
                page_number += 1

            else:
                break

        # if error 
        else:
            # log error
            log_error_message("GET", provider_url, navigation_response.status_code)
            break

def scrape_all_providers():
    # scrape_actors_connection()
    scrape_big_apple_safety()

## MAIN
scrape_all_providers()
        
