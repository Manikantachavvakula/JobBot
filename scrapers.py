import time
import random
import json
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from typing import List, Dict, Any
import logging
import urllib.parse

class JobScraper:
    def __init__(self, config_path: str = "config.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.ua = UserAgent()
        self.setup_logging()
        self.driver = None
        self.scraped_urls = set()  # Avoid duplicates
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('job_scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_driver(self, headless: bool = True) -> webdriver.Chrome:
        """Setup Chrome driver with stealth options"""
        chrome_options = Options()
        
        if headless:
            chrome_options.add_argument('--headless')
        
        # Stealth options to avoid detection
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument(f'--user-agent={self.ua.random}')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-plugins-discovery')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Remove automation indicators
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    
    def random_delay(self, min_sec: float = 2, max_sec: float = 5):
        """Add random delay to appear human-like"""
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        return ' '.join(text.strip().split())
    
    def scrape_linkedin_jobs(self, keywords: str = "QA Engineer", location: str = "Hyderabad") -> List[Dict]:
        """Scrape LinkedIn jobs - Educational example"""
        jobs = []
        
        try:
            self.driver = self.setup_driver(headless=True)
            
            # LinkedIn job search URL for India
            search_params = {
                'keywords': keywords,
                'location': location,
                'f_E': '2',  # Entry level
                'f_C': '104738515',  # India (company location)
                'sortBy': 'DD'  # Date posted (newest first)
            }
            
            search_url = "https://www.linkedin.com/jobs/search/?" + urllib.parse.urlencode(search_params)
            
            self.logger.info(f"Scraping LinkedIn: {search_url}")
            self.driver.get(search_url)
            self.random_delay(3, 5)
            
            # Wait for job listings to load
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='job-search-card']"))
                )
            except:
                self.logger.warning("LinkedIn job cards not found, trying alternative selector")
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "job-search-card"))
                    )
                except:
                    self.logger.error("Failed to load LinkedIn job listings")
                    return jobs
            
            # Scroll to load more jobs
            for i in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                self.random_delay(2, 3)
            
            job_cards = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='job-search-card'], .job-search-card")
            self.logger.info(f"Found {len(job_cards)} LinkedIn job cards")
            
            for idx, card in enumerate(job_cards[:15]):  # Limit to 15 jobs per search
                try:
                    # Extract job details
                    title_elem = card.find_element(By.CSS_SELECTOR, "h3 a, .base-search-card__title a")
                    title = self.clean_text(title_elem.text)
                    job_url = title_elem.get_attribute('href')
                    
                    if job_url in self.scraped_urls:
                        continue
                    self.scraped_urls.add(job_url)
                    
                    company_elem = card.find_element(By.CSS_SELECTOR, ".base-search-card__subtitle a, h4 a")
                    company = self.clean_text(company_elem.text)
                    
                    location_elem = card.find_element(By.CSS_SELECTOR, ".job-search-card__location")
                    location_text = self.clean_text(location_elem.text)
                    
                    # Try to get job insights (salary, benefits)
                    insights = ""
                    try:
                        insights_elem = card.find_element(By.CSS_SELECTOR, ".job-search-card__benefits")
                        insights = self.clean_text(insights_elem.text)
                    except:
                        pass
                    
                    # Get posting date
                    posted_date = ""
                    try:
                        date_elem = card.find_element(By.CSS_SELECTOR, ".job-search-card__listdate")
                        posted_date = self.clean_text(date_elem.text)
                    except:
                        pass
                    
                    job_data = {
                        'title': title,
                        'company': company,
                        'location': location_text,
                        'description': insights,  # Will be enriched later if needed
                        'url': job_url,
                        'source': 'LinkedIn',
                        'posted_date': posted_date,
                        'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'search_keywords': keywords
                    }
                    
                    jobs.append(job_data)
                    self.logger.info(f"Scraped LinkedIn job {idx+1}: {title} at {company}")
                    
                except Exception as e:
                    self.logger.error(f"Error scraping LinkedIn job card {idx+1}: {e}")
                    continue
        
        except Exception as e:
            self.logger.error(f"Error scraping LinkedIn: {e}")
        
        finally:
            if self.driver:
                self.driver.quit()
        
        return jobs
    
    def scrape_naukri_jobs(self, keywords: str = "QA Engineer", location: str = "Hyderabad") -> List[Dict]:
        """Scrape Naukri jobs - Major Indian job portal"""
        jobs = []
        
        try:
            # Use requests for initial scraping (more reliable for Naukri)
            headers = {
                'User-Agent': self.ua.random,
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            # Format URL for Naukri search
            keywords_formatted = keywords.replace(' ', '-').lower()
            location_formatted = location.lower()
            
            search_url = f"https://www.naukri.com/{keywords_formatted}-jobs-in-{location_formatted}"
            
            self.logger.info(f"Scraping Naukri: {search_url}")
            
            response = requests.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find job containers
            job_containers = soup.find_all('article', class_=lambda x: x and 'jobTuple' in x)
            
            if not job_containers:
                # Try alternative selector
                job_containers = soup.find_all('div', class_=lambda x: x and 'srp-jobtuple-wrapper' in x)
            
            self.logger.info(f"Found {len(job_containers)} Naukri job containers")
            
            for idx, container in enumerate(job_containers[:15]):
                try:
                    # Extract title and URL
                    title_elem = container.find('a', class_=lambda x: x and 'title' in x)
                    if not title_elem:
                        title_elem = container.find('h3')
                    
                    if title_elem:
                        title = self.clean_text(title_elem.get_text())
                        job_url = title_elem.get('href', '')
                        
                        if job_url and not job_url.startswith('http'):
                            job_url = 'https://www.naukri.com' + job_url
                    else:
                        continue
                    
                    if job_url in self.scraped_urls:
                        continue
                    self.scraped_urls.add(job_url)
                    
                    # Extract company
                    company_elem = container.find('a', class_=lambda x: x and 'comp-name' in x)
                    company = self.clean_text(company_elem.get_text()) if company_elem else 'Company not specified'
                    
                    # Extract location
                    location_elem = container.find('span', class_=lambda x: x and 'loc' in x)
                    location_text = self.clean_text(location_elem.get_text()) if location_elem else location
                    
                    # Extract experience
                    exp_elem = container.find('span', class_=lambda x: x and 'exp' in x)
                    experience = self.clean_text(exp_elem.get_text()) if exp_elem else 'Not specified'
                    
                    # Extract salary
                    salary_elem = container.find('span', class_=lambda x: x and 'sal' in x)
                    salary = self.clean_text(salary_elem.get_text()) if salary_elem else 'Not disclosed'
                    
                    # Extract job description snippet
                    desc_elem = container.find('div', class_=lambda x: x and 'job-description' in x)
                    if not desc_elem:
                        desc_elem = container.find('div', class_=lambda x: x and 'summary' in x)
                    description = self.clean_text(desc_elem.get_text()) if desc_elem else ''
                    
                    # Extract posted date
                    posted_elem = container.find('span', class_=lambda x: x and 'posted' in x)
                    posted_date = self.clean_text(posted_elem.get_text()) if posted_elem else ''
                    
                    job_data = {
                        'title': title,
                        'company': company,
                        'location': location_text,
                        'experience': experience,
                        'salary': salary,
                        'description': description,
                        'url': job_url,
                        'source': 'Naukri',
                        'posted_date': posted_date,
                        'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'search_keywords': keywords
                    }
                    
                    jobs.append(job_data)
                    self.logger.info(f"Scraped Naukri job {idx+1}: {title} at {company}")
                    
                except Exception as e:
                    self.logger.error(f"Error scraping Naukri job {idx+1}: {e}")
                    continue
        
        except Exception as e:
            self.logger.error(f"Error scraping Naukri: {e}")
        
        return jobs
    
    def scrape_indeed_jobs(self, keywords: str = "QA Engineer", location: str = "Hyderabad") -> List[Dict]:
        """Scrape Indeed jobs - International job portal"""
        jobs = []
        
        try:
            headers = {
                'User-Agent': self.ua.random,
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
            }
            
            # Indeed India search URL
            search_params = {
                'q': keywords,
                'l': location,
                'fromage': '7',  # Last 7 days
                'sort': 'date'   # Sort by date
            }
            
            search_url = "https://in.indeed.com/jobs?" + urllib.parse.urlencode(search_params)
            
            self.logger.info(f"Scraping Indeed: {search_url}")
            
            response = requests.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find job containers
            job_containers = soup.find_all('div', class_=lambda x: x and 'job_seen_beacon' in x)
            
            if not job_containers:
                job_containers = soup.find_all('div', class_=lambda x: x and 'slider_container' in x)
            
            self.logger.info(f"Found {len(job_containers)} Indeed job containers")
            
            for idx, container in enumerate(job_containers[:15]):
                try:
                    # Extract title and URL
                    title_elem = container.find('h2', class_=lambda x: x and 'jobTitle' in x)
                    if title_elem:
                        title_link = title_elem.find('a')
                        if title_link:
                            title = self.clean_text(title_link.get('title', title_link.get_text()))
                            job_url = 'https://in.indeed.com' + title_link.get('href', '')
                        else:
                            title = self.clean_text(title_elem.get_text())
                            job_url = ''
                    else:
                        continue
                    
                    if job_url in self.scraped_urls:
                        continue
                    self.scraped_urls.add(job_url)
                    
                    # Extract company
                    company_elem = container.find('span', class_=lambda x: x and 'companyName' in x)
                    company = self.clean_text(company_elem.get_text()) if company_elem else 'Company not specified'
                    
                    # Extract location
                    location_elem = container.find('div', class_=lambda x: x and 'companyLocation' in x)
                    location_text = self.clean_text(location_elem.get_text()) if location_elem else location
                    
                    # Extract salary
                    salary_elem = container.find('span', class_=lambda x: x and 'salaryText' in x)
                    salary = self.clean_text(salary_elem.get_text()) if salary_elem else 'Not disclosed'
                    
                    # Extract job summary
                    summary_elem = container.find('div', class_=lambda x: x and 'summary' in x)
                    description = self.clean_text(summary_elem.get_text()) if summary_elem else ''
                    
                    # Extract posted date
                    posted_elem = container.find('span', class_=lambda x: x and 'date' in x)
                    posted_date = self.clean_text(posted_elem.get_text()) if posted_elem else ''
                    
                    job_data = {
                        'title': title,
                        'company': company,
                        'location': location_text,
                        'salary': salary,
                        'description': description,
                        'url': job_url,
                        'source': 'Indeed',
                        'posted_date': posted_date,
                        'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'search_keywords': keywords
                    }
                    
                    jobs.append(job_data)
                    self.logger.info(f"Scraped Indeed job {idx+1}: {title} at {company}")
                    
                except Exception as e:
                    self.logger.error(f"Error scraping Indeed job {idx+1}: {e}")
                    continue
        
        except Exception as e:
            self.logger.error(f"Error scraping Indeed: {e}")
        
        return jobs
    
    def scrape_timesjobs(self, keywords: str = "QA Engineer", location: str = "Hyderabad") -> List[Dict]:
        """Scrape TimesJobs - Popular Indian job portal"""
        jobs = []
        
        try:
            headers = {
                'User-Agent': self.ua.random,
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }
            
            # TimesJobs search URL
            search_params = {
                'searchType': 'personalizedSearch',
                'from': 'submit',
                'txtKeywords': keywords,
                'txtLocation': location,
                'cboWorkExp1': '0',
                'cboWorkExp2': '2'
            }
            
            search_url = "https://www.timesjobs.com/candidate/job-search.html?" + urllib.parse.urlencode(search_params)
            
            self.logger.info(f"Scraping TimesJobs: {search_url}")
            
            response = requests.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find job listings
            job_containers = soup.find_all('li', class_=lambda x: x and 'clearfix job-bx' in str(x))
            
            self.logger.info(f"Found {len(job_containers)} TimesJobs listings")
            
            for idx, container in enumerate(job_containers[:10]):
                try:
                    # Extract title and URL
                    title_elem = container.find('h2')
                    if title_elem:
                        title_link = title_elem.find('a')
                        if title_link:
                            title = self.clean_text(title_link.get_text())
                            job_url = title_link.get('href', '')
                        else:
                            continue
                    else:
                        continue
                    
                    if job_url in self.scraped_urls:
                        continue
                    self.scraped_urls.add(job_url)
                    
                    # Extract company
                    company_elem = container.find('h3', class_=lambda x: x and 'joblist-comp-name' in str(x))
                    company = self.clean_text(company_elem.get_text()) if company_elem else 'Company not specified'
                    
                    # Extract experience and location
                    exp_loc_elem = container.find('ul', class_=lambda x: x and 'top-jd-dtl' in str(x))
                    experience = 'Not specified'
                    location_text = location
                    
                    if exp_loc_elem:
                        items = exp_loc_elem.find_all('li')
                        for item in items:
                            text = item.get_text()
                            if 'year' in text.lower() or 'exp' in text.lower():
                                experience = self.clean_text(text)
                            elif any(loc in text for loc in ['hyderabad', 'bangalore', 'chennai', 'pune', 'mumbai', 'delhi']):
                                location_text = self.clean_text(text)
                    
                    # Extract job description
                    desc_elem = container.find('ul', class_=lambda x: x and 'list-job-dtl' in str(x))
                    description = self.clean_text(desc_elem.get_text()) if desc_elem else ''
                    
                    # Extract posted date
                    posted_elem = container.find('span', class_=lambda x: x and 'sim-posted' in str(x))
                    posted_date = self.clean_text(posted_elem.get_text()) if posted_elem else ''
                    
                    job_data = {
                        'title': title,
                        'company': company,
                        'location': location_text,
                        'experience': experience,
                        'description': description,
                        'url': job_url,
                        'source': 'TimesJobs',
                        'posted_date': posted_date,
                        'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'search_keywords': keywords
                    }
                    
                    jobs.append(job_data)
                    self.logger.info(f"Scraped TimesJobs job {idx+1}: {title} at {company}")
                    
                except Exception as e:
                    self.logger.error(f"Error scraping TimesJobs job {idx+1}: {e}")
                    continue
        
        except Exception as e:
            self.logger.error(f"Error scraping TimesJobs: {e}")
        
        return jobs
    
    def scrape_all_sites(self) -> List[Dict]:
        """Scrape jobs from all configured sites"""
        all_jobs = []
        
        # Get job preferences from config
        roles = self.config['job_preferences']['roles']
        locations = self.config['job_preferences']['locations']
        
        # Use primary role and multiple locations for comprehensive search
        primary_role = roles[0] if roles else "QA Engineer"
        search_locations = locations[:3] if len(locations) > 3 else locations
        
        self.logger.info(f"Starting job scraping for '{primary_role}' in locations: {search_locations}")
        
        for location in search_locations:
            self.logger.info(f"\\n=== Searching in {location} ===")
            
            # Scrape LinkedIn
            try:
                self.logger.info("Scraping LinkedIn...")
                linkedin_jobs = self.scrape_linkedin_jobs(primary_role, location)
                all_jobs.extend(linkedin_jobs)
                self.logger.info(f"LinkedIn: {len(linkedin_jobs)} jobs found")
                self.random_delay(5, 10)  # Respectful delay between sites
            except Exception as e:
                self.logger.error(f"LinkedIn scraping failed for {location}: {e}")
            
            # Scrape Naukri
            try:
                self.logger.info("Scraping Naukri...")
                naukri_jobs = self.scrape_naukri_jobs(primary_role, location)
                all_jobs.extend(naukri_jobs)
                self.logger.info(f"Naukri: {len(naukri_jobs)} jobs found")
                self.random_delay(5, 10)
            except Exception as e:
                self.logger.error(f"Naukri scraping failed for {location}: {e}")
            
            # Scrape Indeed
            try:
                self.logger.info("Scraping Indeed...")
                indeed_jobs = self.scrape_indeed_jobs(primary_role, location)
                all_jobs.extend(indeed_jobs)
                self.logger.info(f"Indeed: {len(indeed_jobs)} jobs found")
                self.random_delay(5, 10)
            except Exception as e:
                self.logger.error(f"Indeed scraping failed for {location}: {e}")
            
            # Scrape TimesJobs (for major cities)
            if location.lower() in ['hyderabad', 'bangalore', 'chennai', 'pune', 'mumbai', 'delhi']:
                try:
                    self.logger.info("Scraping TimesJobs...")
                    timesjobs_jobs = self.scrape_timesjobs(primary_role, location)
                    all_jobs.extend(timesjobs_jobs)
                    self.logger.info(f"TimesJobs: {len(timesjobs_jobs)} jobs found")
                    self.random_delay(5, 10)
                except Exception as e:
                    self.logger.error(f"TimesJobs scraping failed for {location}: {e}")
        
        # Remove duplicates based on URL
        unique_jobs = []
        seen_urls = set()
        
        for job in all_jobs:
            job_url = job.get('url', '')
            if job_url and job_url not in seen_urls:
                seen_urls.add(job_url)
                unique_jobs.append(job)
            elif not job_url:
                # If no URL, check for title + company combination
                job_key = f"{job.get('title', '')}-{job.get('company', '')}"
                if job_key not in seen_urls:
                    seen_urls.add(job_key)
                    unique_jobs.append(job)
        
        self.logger.info(f"\\n=== Scraping Summary ===")
        self.logger.info(f"Total jobs scraped: {len(all_jobs)}")
        self.logger.info(f"Unique jobs after deduplication: {len(unique_jobs)}")
        
        # Log breakdown by source
        source_breakdown = {}
        for job in unique_jobs:
            source = job.get('source', 'Unknown')
            source_breakdown[source] = source_breakdown.get(source, 0) + 1
        
        for source, count in source_breakdown.items():
            self.logger.info(f"{source}: {count} jobs")
        
        return unique_jobs
    
    def search_specific_keywords(self, keywords_list: List[str]) -> List[Dict]:
        """Search for jobs with specific keyword combinations"""
        all_jobs = []
        locations = self.config['job_preferences']['locations'][:2]  # Limit to 2 locations
        
        for keywords in keywords_list:
            for location in locations:
                self.logger.info(f"Searching for '{keywords}' in {location}")
                
                # LinkedIn search
                try:
                    jobs = self.scrape_linkedin_jobs(keywords, location)
                    all_jobs.extend(jobs)
                    self.random_delay(3, 6)
                except Exception as e:
                    self.logger.error(f"Error searching LinkedIn for '{keywords}': {e}")
                
                # Naukri search
                try:
                    jobs = self.scrape_naukri_jobs(keywords, location)
                    all_jobs.extend(jobs)
                    self.random_delay(3, 6)
                except Exception as e:
                    self.logger.error(f"Error searching Naukri for '{keywords}': {e}")
        
        return all_jobs

# Example usage and testing
if __name__ == "__main__":
    scraper = JobScraper()
    
    print("=== Testing Job Scraper ===")
    print("This will scrape a few jobs from each site...")
    
    # Test individual sites
    print("\\n1. Testing LinkedIn...")
    linkedin_jobs = scraper.scrape_linkedin_jobs("QA Automation Engineer", "Hyderabad")
    print(f"LinkedIn: {len(linkedin_jobs)} jobs")
    
    print("\\n2. Testing Naukri...")
    naukri_jobs = scraper.scrape_naukri_jobs("Software Tester", "Hyderabad")
    print(f"Naukri: {len(naukri_jobs)} jobs")
    
    print("\\n3. Testing Indeed...")
    indeed_jobs = scraper.scrape_indeed_jobs("QA Engineer", "Hyderabad")
    print(f"Indeed: {len(indeed_jobs)} jobs")
    
    # Test comprehensive search
    print("\\n4. Testing comprehensive search...")
    all_jobs = scraper.scrape_all_sites()
    print(f"Total unique jobs: {len(all_jobs)}")
    
    # Display sample results
    if all_jobs:
        print("\\n=== Sample Jobs ===")
        for i, job in enumerate(all_jobs[:3]):
            print(f"\\nJob {i+1}:")
            print(f"Title: {job['title']}")
            print(f"Company: {job['company']}")
            print(f"Location: {job['location']}")
            print(f"Source: {job['source']}")
            print(f"URL: {job['url'][:80]}...")
    
    print("\\n=== Test Complete ===")
    print("Check job_scraper.log for detailed logs")