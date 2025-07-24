import pandas as pd
from scrape_and_filter_jobs import scrape_and_filter_jobs, export_jobs_to_csv

def run_my_searches() -> pd.DataFrame:
    '''
    Defines my filters for terms/companies to exclude and runs scrape_and_filter_jobs for NYC, Boston, and Westport CT
    :return: Pandas dataframe containing job data
    '''

    EXCLUDE_TERMS_LIST = ["Senior", "Sr", "Lead", "Founding", "III", "IV", "Manager", "Staff", "Principal"]
    EXCLUDE_COMPANIES_LIST = ["Jobright.ai", "Jobs via Dice", "Lensa", "Epic", "DataAnnotation"]
    HOURS_OLD = 24
    RESULTS_WANTED = 100
    SITES_TO_SEARCH = ["indeed", "linkedin"]


    jobs_nyc = scrape_and_filter_jobs(
        site_name=SITES_TO_SEARCH,
        search_term="software engineer",
        location="New York, NY",
        distance=5,
        hours_old=HOURS_OLD,
        country_indeed="USA",
        results_wanted=RESULTS_WANTED,
        linkedin_fetch_description=True,
        filter_state="NY",
        exclude_companies=EXCLUDE_COMPANIES_LIST,
        exclude_title_terms=EXCLUDE_TERMS_LIST
    )

    jobs_ct = scrape_and_filter_jobs(
        site_name=SITES_TO_SEARCH,
        search_term="software engineer",
        location="Westport, CT",
        distance=40,
        hours_old=HOURS_OLD,
        country_indeed="USA",
        results_wanted=RESULTS_WANTED,
        linkedin_fetch_description=True,
        filter_state="CT",
        exclude_companies=EXCLUDE_COMPANIES_LIST,
        exclude_title_terms=EXCLUDE_TERMS_LIST
    )

    jobs_bos = scrape_and_filter_jobs(
        site_name=SITES_TO_SEARCH,
        search_term="software engineer",
        location="Boston, MA",
        distance=20,
        hours_old=HOURS_OLD,
        country_indeed="USA",
        results_wanted=RESULTS_WANTED,
        linkedin_fetch_description=True,
        filter_state="MA",
        exclude_companies=EXCLUDE_COMPANIES_LIST,
        exclude_title_terms=EXCLUDE_TERMS_LIST
    )

    jobs = pd.concat([jobs_nyc, jobs_ct, jobs_bos], axis=0)
    return jobs

jobs = run_my_searches()

# Columns we want: site, job_url, title, company, location, job_type, description, date_posted
output_jobs = jobs[['site', 'company', 'location', 'title', 'job_url', 'date_posted', 'job_type', 'description']].copy()

export_jobs_to_csv(output_jobs)