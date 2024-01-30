'''
## NOTES
assumes 5 seats are available if class is not full
assumes length of session is 2 hours


## TO DO
construct separate json objects if more than 100 sections
construct dictionary using for key, value in vars(self).items():
short course name up to first comma?
parse notes
parse teacher better including multiple teachers?
parse enrollment close
some sites expose a reliable SKU, UUID, or other identifier?

'''

## LIBRARIES
from horselibrary import *

## FUNCTIONS
def scrape_provider(provider: dict):
    # open html session
    html_session = HTMLSession()

    # get time stamp
    purge_before = get_timestamp("%Y-%m-%d %H:%M:%S")

    # get page links
    page_list_container = get_container_from_html(
        html_session, provider.url,
        provider.nav_tag,
        )

    raw_urls = extract_from_container(
        page_list_container,
        tag = 'a',
        attr = 'href')

    page_urls = clean_urls(raw_urls, 1, -1, prefix  = "https:")

    # loop through pages
    raw_urls = []
    for page_url in page_urls:
        # get section links
        section_container_list = get_container_list_from_html(
            html_session,
            page_url,
            provider.section_url_tag,
        )

        some_urls = extract_from_container_list(
            section_container_list,
            tag = 'a',
            attr = 'href')
        raw_urls += some_urls

    section_urls = clean_urls(raw_urls, prefix  = "https:")

    # loop through sections
    sections_list = []
    for section_url in section_urls:
        print(section_url)
        
        # get section data
        response = html_session.get(section_url)

        # parse course id
        section_id = response.html.find(provider.section_id_tag, first = True).attrs["content"]

        # parse course name
        section_name = response.html.find(provider.section_name_tag, first = True).attrs["content"]

        # parse available seats
        section_full = response.html.find(provider.section_available_tag, first = True)

        if section_full:
            available_seats = 0
        else:
            available_seats = 5
        
        # parse price
        price_text = response.html.find(provider.section_price_tag, first = True).text

        if price_text == "Price: Free":
            section_price = float(0)

        else:
            try:
                prefix = "Price: $"
                price_strip = price_text[len(prefix):]
                section_price = float(price_strip)
            except:
                section_price = "N/A"

        # parse sessions
        sessions_list = []
        sessions_html = response.html.find('td')
        sessions_text = [item.text for item in sessions_html]
        item_count = len(sessions_text)
        for i in range(0, item_count, 2):
            date_text = sessions_text[i]
            date_value = datetime.strptime(date_text, "%A, %B %d, %Y").date()
            session_date = date_value.strftime("%Y-%m-%d")
            
            start_time_text = sessions_text[i+1]
            start_time_value = datetime.strptime(start_time_text, "%I:%M %p").time()
            session_start_time = start_time_value.strftime("%H:%M:%S")

            end_time_value = (datetime.combine(datetime.min, start_time_value) + timedelta(hours=2)).time()
            session_end_time = end_time_value.strftime("%H:%M:%S")
            
            # construct session object
            new_session = Session(session_date, session_start_time, session_end_time)

            # add to sessions list
            sessions_list.append(new_session)

        # parse location

        # parse notes

        # parse teacher
        tmp = response.html.find(provider.section_teacher_tag)
        session_teacher = tmp[-1].text

        # parse enrollment close

        # construct section object
        new_section = Section(
            section_id,
            section_name,
            section_url,
            available_seats,
            section_price,
            sessions = sessions_list,
            teacher = session_teacher
        )

        # check if section is valid & if valid add to sections list
        valid = True
        section_name_lowercase = section_name.lower()
        if provider.remove_if:
            for item in provider.remove_if:
                item_lowercase = item.lower()
                index = section_name_lowercase.find(item_lowercase)
                if index >= 0:
                    valid = False
                    break

            if valid:
                sections_list.append(new_section)

    # close html session
    html_session.close()

    # construct scrape object
    new_scrape = Scrape(
        provider.name,
        provider.records,
        purge_before,
        sections_list, 
    )

    # convert scrape object to json object
    new_scrape_dictionary = new_scrape.get_dictionary()
    scrape_json = json.dumps(new_scrape_dictionary)

    # endpoint = "https://horseshoe.coursehorse.com/sync"
    # post_json_data(endpoint, scrape_json)
    # indented_json = json.dumps(new_scrape_dictionary, indent=2)
    # print(indented_json)

    print(f'{len(new_scrape.sections)} sections found')

    file_path = "test.json"
    with open(file_path, 'w') as json_file:
        json.dump(scrape_json, json_file)

## PROVIDERS
actorsconnection = Provider(
    name = "Actors Connection",
    url = 'https://www.actorsconnection.com/classes/',
    records = "all except seminars",
    nav_tag = 'ul.pagination',
    section_url_tag = 'div.listing.clearfix',
    section_id_tag = 'meta[property="og:title"]',
    section_name_tag = 'meta[property="og:title"]',
    section_available_tag = 'p.full-class',
    section_price_tag = 'div.price',
    section_teacher_tag = 'h2',
    remove_if = ["seminar"]
)

## MAIN
provider_list = [actorsconnection]
for provider in provider_list:
    scrape_provider(provider)
