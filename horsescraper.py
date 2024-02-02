'''
## NOTES
removes seminars
removes free classes
sets price at $9999.99 if unable to parse price
then removes

assumes 5 seats are available if class is not full
assumes length of session is 2 hours


## TO DO
parse price better including list of text responses?
parse teacher better including multiple teachers?
construct separate json objects if more than 100 sections
docstrings for library esp IN & OUT datatypes?
construct dictionary using for key, value in vars(self).items():
parse enrollment close
parse notes
include scrape notes?
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

    # get section urls
    section_urls = get_section_urls(html_session, provider)

    # loop through sections
    sections_list = []
    for section_url in section_urls:
 
        # get section data
        section_response = fetch_all(
            html_session,
            section_url
            )

        # parse section data
        new_section = parse_section_data(
            section_url,
            section_response,
            provider
            )

        # check if section is valid & if valid add to sections list
        valid = is_valid_section(new_section, provider)

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

    file_path = "test.json"
    with open(file_path, 'w') as json_file:
        json.dump(scrape_json, json_file)

    print(f'{len(new_scrape.sections)} sections found')

## PROVIDERS
actorsconnection = Provider(
    name = "Actors Connection",
    url = 'https://www.actorsconnection.com/classes/',
    records = "all except seminars",
    page_url_tag = 'ul.pagination',
    section_url_tag = 'div.listing.clearfix',
    section_id_tag = 'meta[property="og:title"]',
    section_name_tag = 'meta[property="og:title"]',
    section_available_tag = 'p.full-class',
    section_price_tag = 'div.price',
    section_teacher_tag = 'h2',
    page_url_start = 1,
    page_url_stop = -1,
    url_prefix = "https:",
    default_session_length = 2,
    remove_if = ["seminar"]
)

## MAIN
provider_list = [actorsconnection]
for provider in provider_list:
    scrape_provider(provider)
        

