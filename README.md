# Job Posting Filtering Tool

Save time by using this to retrieve postings from job boards and filter out those you don't want to see. Built on top of [JobSpy](https://github.com/speedyapply/JobSpy).

## Features
The `scrape_and_filter_jobs` function allows for all the same arguments as `jobspy.scrape_jobs`, with three additional optional arguments:
* `filter_state` - takes a state abbreviation and filters out any postings from other states
  * For example, if you're looking for jobs in and around NYC but only want to see jobs in New York State (ignoring NJ, CT) you would set `filter_state="NY"`
* `exclude_companies` - takes a list of strings for company names you want to ignore
* `exclude_title_terms` - takes a list of strings for terms in job titles you want to ignore (senior, principal, new grad, etc.)

The console will display how many jobs the scraper found and how many were removed by each filter.

I've also created `export_jobs_to_csv` which takes a pandas DataFrame and outputs a timestamped CSV file for easier viewing of the job postings.

## Getting Started
### 1. Install jobspy
```bash
pip install -U python-jobspy
```

See [JobSpy](https://github.com/speedyapply/JobSpy) for more details.

### 2. Clone the repository
```bash
git clone https://github.com/zkornbluth/job-searcher.git
```

### 3. Use the function in your own .py script
Example usage:
```python
from scrape_and_filter_jobs import scrape_and_filter_jobs, export_jobs_to_csv

jobs = scrape_and_filter_jobs(
        site_name=["indeed", "linkedin"]
        search_term="software engineer",
        location="New York, NY",
        distance=25,
        hours_old=24,
        country_indeed="USA",
        results_wanted=50,
        linkedin_fetch_description=True,
        exclude_title_terms=["Senior", "Sr", "Lead", "Principal"],
        filter_state="NY",
        exclude_companies=["Jobright.ai", "Lensa"]
    )

export_jobs_to_csv(jobs)
```

Be sure to put your script in the same folder as scrape_and_filter_jobs.py.

See [main.py](https://github.com/zkornbluth/job_searcher/blob/main/main.py) for how I scrape and filter jobs in multiple locations and combine the results into one CSV file.

Sample output from main.py:

<img width="308" height="245" alt="Screenshot 2025-07-24 at 3 21 55 PM" src="https://github.com/user-attachments/assets/3478020e-2123-4028-a79a-aec33485f3c7" />

Disclaimer - I have only successfully tested this scraping from Indeed and LinkedIn in the US.
