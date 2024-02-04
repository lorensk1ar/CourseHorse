'''
## NOTES
removes free classes
removes full classes
removes seminars

assumes 6 seats are available if no other information
assumes length of session is 2 hours

sends separate scrape json for each page with purge before for each page!

## TO DO
parse teacher(s) as string or as list?
parse enrollment close
parse notes
include scrape notes?
parse short course name up to comma?

'''

### LIBRARIES
from datetime import datetime, timedelta
import json
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
            section_id = response.html.find('meta[property="og:title"]', first = True).attrs["content"]

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
                    print(teacher_text)
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

        # close html session
        html_session.close()

        # parse records
        records = "Page " + str(page_number)
    
        # construct new scrape
        scrape = {
            "provider": "Actors Connection",
            "records": records,
            "purge_before": purge_before,
            "sections": sections,
            "scrape_notes": [] 
        }

        scrape_json = json.dumps(scrape)
        provider_no_spaces = scrape["provider"].replace(" ", "")
        file_path = provider_no_spaces + str(page_number) + ".json"
        
        with open(file_path, 'w') as json_file:
            json.dump(scrape_json, json_file)

        # indented_json = json.dumps(scrape, indent=2)
        # print(indented_json)
        
        print(f"{len(scrape['sections'])} sections found", "\n")

def scrape_all_providers():
    scrape_actors_connection()

## MAIN
scrape_all_providers()
