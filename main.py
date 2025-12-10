import pandas as pd
from scrape_and_filter_jobs import scrape_and_filter_jobs, export_jobs_to_csv
import os
import sys
import logging

import re

def extract_linkedin_id(url: str) -> str | None:
    """Extract LinkedIn job ID from job_url."""
    match = re.search(r"linkedin\.com/jobs/view/(\d+)", url)
    return match.group(1) if match else None

def filter_seen_linkedin_jobs(df: pd.DataFrame, seen_file: str) -> pd.DataFrame:
    """Remove LinkedIn jobs we've already seen and update the seen file."""
    # Load existing seen IDs
    if os.path.exists(seen_file):
        with open(seen_file, "r") as f:
            seen_ids = set(line.strip() for line in f if line.strip())
    else:
        seen_ids = set()

    # Extract IDs for LinkedIn rows
    df["linkedin_id"] = df.apply(
        lambda row: extract_linkedin_id(row["job_url"]) if row["site"].lower() == "linkedin" else None,
        axis=1
    )

    # Split into LinkedIn + others
    linkedin_jobs = df[df["linkedin_id"].notna()]
    non_linkedin_jobs = df[df["linkedin_id"].isna()]

    # Keep only new LinkedIn jobs
    new_linkedin_jobs = linkedin_jobs[~linkedin_jobs["linkedin_id"].isin(seen_ids)]

    # Update seen IDs with newly found ones
    new_ids = set(new_linkedin_jobs["linkedin_id"].tolist())
    if new_ids:
        with open(seen_file, "a") as f:
            for job_id in new_ids:
                f.write(job_id + "\n")

    # Return combined DataFrame
    return pd.concat([new_linkedin_jobs, non_linkedin_jobs], axis=0)

def run_my_searches(search_term: str, hours_old = 24) -> pd.DataFrame:
    '''
    Defines my filters for terms/companies to exclude and runs scrape_and_filter_jobs for NYC, Boston, Westport CT, White Plains, and remote (USA)
    :return: Pandas dataframe containing job data
    '''

    EXCLUDE_TERMS_LIST = ["Senior", "Sr", "Lead", "Founding", "Founder", "Cofounder", "III", "IV", "Manager", "Staff", "Principal", "Principle", "VP", "Director", 
                          "President", "Expert", "Distinguished", "CEO"]
    # Read in exclude companies from file
    with open("exclude_companies_list.txt", "r") as f:
        lines = f.readlines
        EXCLUDE_COMPANIES_LIST = [line.strip() for line in lines]
    RESULTS_WANTED = 200
    SITES_TO_SEARCH = ["indeed", "linkedin"]


    jobs_nyc = scrape_and_filter_jobs(
        site_name=SITES_TO_SEARCH,
        search_term=search_term,
        location="New York, NY",
        distance=5,
        hours_old=hours_old,
        country_indeed="USA",
        results_wanted=RESULTS_WANTED,
        linkedin_fetch_description=True,
        filter_state="NY",
        exclude_companies=EXCLUDE_COMPANIES_LIST,
        exclude_title_terms=EXCLUDE_TERMS_LIST
    )

    jobs_ct = scrape_and_filter_jobs(
        site_name=SITES_TO_SEARCH,
        search_term=search_term,
        location="Westport, CT",
        distance=40,
        hours_old=hours_old,
        country_indeed="USA",
        results_wanted=RESULTS_WANTED,
        linkedin_fetch_description=True,
        filter_state="CT",
        exclude_companies=EXCLUDE_COMPANIES_LIST,
        exclude_title_terms=EXCLUDE_TERMS_LIST
    )

    jobs_bos = scrape_and_filter_jobs(
        site_name=SITES_TO_SEARCH,
        search_term=search_term,
        location="Boston, MA",
        distance=20,
        hours_old=hours_old,
        country_indeed="USA",
        results_wanted=RESULTS_WANTED,
        linkedin_fetch_description=True,
        filter_state="MA",
        exclude_companies=EXCLUDE_COMPANIES_LIST,
        exclude_title_terms=EXCLUDE_TERMS_LIST
    )

    jobs_westchester = scrape_and_filter_jobs(
        site_name=SITES_TO_SEARCH,
        search_term=search_term,
        location="White Plains, NY",
        distance=10,
        hours_old=hours_old,
        country_indeed="USA",
        results_wanted=RESULTS_WANTED,
        linkedin_fetch_description=True,
        filter_state="NY",
        exclude_companies=EXCLUDE_COMPANIES_LIST,
        exclude_title_terms=EXCLUDE_TERMS_LIST
    )

    jobs_remote = scrape_and_filter_jobs(
        site_name=["linkedin"],
        search_term=search_term,
        location="United States",
        is_remote=True,
        hours_old=hours_old,
        country_indeed="USA",
        results_wanted=RESULTS_WANTED,
        linkedin_fetch_description=True,
        exclude_companies=EXCLUDE_COMPANIES_LIST,
        exclude_title_terms=EXCLUDE_TERMS_LIST
    )

    jobs = pd.concat([jobs_nyc, jobs_ct, jobs_bos, jobs_westchester, jobs_remote], axis=0)
    return jobs

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Set up logging
log_file = os.path.join(script_dir, 'job_searcher.log')
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='a'
)

try:
    hours_lookback = int(sys.argv[1])
    logging.info(f"Looking for jobs in the last {hours_lookback} hours")
    jobs_se = run_my_searches("Software Engineer", hours_lookback)
    jobs_pd = run_my_searches("Python Developer", hours_lookback)
    jobs_pr = run_my_searches("Computer Programmer", hours_lookback)
    jobs_tb = run_my_searches("Tableau Analyst", hours_lookback)
    jobs = pd.concat([jobs_se, jobs_pd, jobs_pr, jobs_tb], axis=0)
    
    seen_file = os.path.join(script_dir, "seen_linkedin_ids.txt")
    logging.info(f"Total jobs found: {len(jobs)}")
    filtered_jobs = filter_seen_linkedin_jobs(jobs, seen_file)
    logging.info(f"Filtered {len(jobs) - len(filtered_jobs)} LinkedIn jobs that have appeared before.")

    # Columns we want: site, job_url, title, company, location, job_type, description, date_posted
    output_jobs = filtered_jobs[['site', 'company', 'location', 'title', 'job_url', 'date_posted', 'job_type', 'description']].copy().drop_duplicates()

    csv_file = export_jobs_to_csv(output_jobs)
    logging.info(f"Job scraping completed. Saved to {csv_file}")
    logging.info(" ")
except Exception as e:
    logging.error(f"Job scraping failed: {str(e)}")
    sys.exit(1)