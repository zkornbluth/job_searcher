import jobspy
import pandas as pd
import strip_markdown.strip_markdown as strip_markdown # for job descriptions
from datetime import datetime
import csv

def scrape_and_filter_jobs(
    site_name: str | list[str] | jobspy.Site | list[jobspy.Site] | None = None,
    search_term: str | None = None,
    google_search_term: str | None = None,
    location: str | None = None,
    distance: int | None = 50,
    is_remote: bool = False,
    job_type: str | None = None,
    easy_apply: bool | None = None,
    results_wanted: int = 15,
    country_indeed: str = "usa",
    proxies: list[str] | str | None = None,
    ca_cert: str | None = None,
    description_format: str = "markdown",
    linkedin_fetch_description: bool | None = False,
    linkedin_company_ids: list[int] | None = None,
    offset: int | None = 0,
    hours_old: int = None,
    enforce_annual_salary: bool = False,
    verbose: int = 0,
    filter_state: str | None = None,
    exclude_companies: list[str] | None = None,
    exclude_title_terms: list[str] | None = None,
) -> pd.DataFrame:
    '''
    Calls jobspy.scrape_jobs, then filters out results based on title terms, location, and company
    :return: Pandas dataframe containing job data
    '''
    jobs = jobspy.scrape_jobs(
        site_name, search_term, google_search_term, location, distance, is_remote,
        job_type, easy_apply, results_wanted, country_indeed, proxies, ca_cert, 
        description_format, linkedin_fetch_description, linkedin_company_ids, offset,
        hours_old, enforce_annual_salary, verbose
    )

    filtered_jobs = pd.DataFrame(columns=jobs.columns)
    removed_for_state = 0
    removed_for_company = 0
    removed_for_title = 0

    for i in range(len(jobs)):
        found_filter_reason = False
        job = jobs.iloc[i]
        # Check if we have a filter_state and if job's state matches
        if filter_state is not None:
            job_location = job.location
            if job_location.endswith(", US"):
                # Remove , US - standardize location as city, state
                job_location = job_location[:-4]
            job_state = job_location[-2:]
            if job_state != filter_state:
                found_filter_reason = True
                removed_for_state += 1

        # If no reason to filter this out yet, check if job.company is in our exclude_companies list
        if found_filter_reason == False and exclude_companies is not None and job.company in exclude_companies:
            found_filter_reason = True
            removed_for_company += 1

        # If no reason to filter this out yet, check if job.title contains any words in exclude_title_terms
        if found_filter_reason == False:
            for term in exclude_title_terms:
                if term in job.title:
                    found_filter_reason = True
                    removed_for_title += 1
                    break

        # If after all checks, found_filter_reason is still False, add job to filtered_jobs
        if found_filter_reason == False:
            filtered_jobs.loc[len(filtered_jobs)] = job

    filtered_jobs['description'] = filtered_jobs['description'].map(strip_markdown)

    print(f"Jobs found in {location}: {len(jobs)}")
    print(f"Removed {removed_for_state} jobs due to state")
    print(f"Removed {removed_for_company} jobs due to company")
    print(f"Removed {removed_for_title} jobs due to title keywords")
    print(f"Remaining jobs: {len(filtered_jobs)}")
    print("")
    return filtered_jobs

def export_jobs_to_csv(job_data: pd.DataFrame) -> None:
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
    job_data.to_csv(f"jobs_{timestamp}.csv", quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False)
