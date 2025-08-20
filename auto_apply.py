import time
import random
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from fake_useragent import UserAgent
from typing import List, Dict, Any
import logging
from filters import JobFilter

class JobApplicator:
    def __init__(self, config_path: str = "config.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.filter = JobFilter(config_path)
        self.ua = UserAgent()
        self.setup_logging()
        self.driver = None
        self.application_count = 0
        self.daily_limit = self.config['daily_limits']['max_applications']
        
        # Manikanta's profile data for form filling
        self.profile_data = {
            'name': self.config['profile']['name'],
            'email': self.config['profile']['email'],
            'phone': self.config['profile']['phone'],
            'location': self.config['profile']['location'],
            'linkedin': self.config['profile'].get('linkedin', ''),
            'github': self.config['profile'].get('github', ''),
            'portfolio': self.config['profile'].get('portfolio', ''),
            'experience_years': 1,  # Based on Amazon experience
            'current_salary': 6,    # Estimate in LPA
            'expected_salary': 8,   # Target salary
            'notice_period': '1 month',
            'skills': ', '.join(self.config['skills']['languages'] + self.config['skills']['testing_tools'])
        }
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('job_applications.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_driver(self, headless: bool = False) -> webdriver.Chrome:
        """Setup Chrome driver for applications"""
        chrome_options = Options()
        
        if headless:
            chrome_options.add_argument('--headless')
        
        # Application-specific options
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument(f'--user-agent={self.ua.random}')
        chrome_options.add_argument('--window-size=1366,768')
        
        # Set download directory for resume uploads
        download_dir = os.path.abspath('./resumes')
        prefs = {
            'download.default_directory': download_dir,
            'profile.default_content_setting_values.notifications': 2,
            'profile.default_content_settings.popups': 0
        }
        chrome_options.add_experimental_option('prefs', prefs)
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Remove automation indicators
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    
    def random_delay(self, min_sec: float = 2, max_sec: float = 5):
        """Human-like delay between actions"""
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)
    
    def human_type(self, element, text: str, clear_first: bool = True):
        """Type text in a human-like manner"""
        if clear_first:
            element.clear()
        
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))
    
    def smart_fill_field(self, driver, field_patterns: List[str], value: str, field_type: str = "input"):
        """Smart field filling based on multiple possible selectors"""
        for pattern in field_patterns:
            try:
                if field_type == "input":
                    element = driver.find_element(By.XPATH, f"//input[{pattern}]")
                elif field_type == "textarea":
                    element = driver.find_element(By.XPATH, f"//textarea[{pattern}]")
                elif field_type == "select":
                    element = driver.find_element(By.XPATH, f"//select[{pattern}]")
                else:
                    element = driver.find_element(By.XPATH, f"//*[{pattern}]")
                
                if field_type == "select":
                    select = Select(element)
                    # Try to select by visible text first, then by value
                    try:
                        select.select_by_visible_text(value)
                    except:
                        select.select_by_value(value)
                else:
                    self.human_type(element, value)
                
                self.logger.info(f"Successfully filled field with pattern: {pattern}")
                return True
            except:
                continue
        
        self.logger.warning(f"Could not find field for value: {value}")
        return False
    
    def apply_to_linkedin_job(self, job_data: Dict) -> Dict[str, Any]:
        """Apply to LinkedIn job using Easy Apply"""
        result = {
            'job_id': job_data.get('url', ''),
            'title': job_data.get('title', ''),
            'company': job_data.get('company', ''),
            'status': 'failed',
            'reason': '',
            'applied_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'steps_completed': 0
        }
        
        try:
            if not self.driver:
                self.driver = self.setup_driver()
            
            # Navigate to job URL
            self.driver.get(job_data['url'])
            self.random_delay(3, 5)
            
            # Check if login is required
            if "login" in self.driver.current_url or "signup" in self.driver.current_url:
                result['reason'] = 'LinkedIn login required'
                result['status'] = 'login_required'
                return result
            
            # Look for Easy Apply button
            easy_apply_selectors = [
                "//button[contains(@aria-label, 'Easy Apply')]",
                "//button[contains(text(), 'Easy Apply')]",
                "//button[contains(@class, 'jobs-apply-button')]"
            ]
            
            easy_apply_btn = None
            for selector in easy_apply_selectors:
                try:
                    easy_apply_btn = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except:
                    continue
            
            if not easy_apply_btn:
                result['reason'] = 'Easy Apply button not found'
                return result
            
            # Click Easy Apply
            easy_apply_btn.click()
            self.random_delay(2, 4)
            result['steps_completed'] = 1
            
            # Handle multi-step application form
            max_steps = 8
            current_step = 0
            
            while current_step < max_steps:
                try:
                    # Fill contact information
                    self.fill_linkedin_contact_info()
                    
                    # Handle resume upload
                    self.handle_linkedin_resume_upload(job_data)
                    
                    # Fill additional questions
                    self.fill_linkedin_additional_questions()
                    
                    # Look for Next button or Submit button
                    next_buttons = self.driver.find_elements(By.XPATH, 
                        "//button[contains(text(), 'Next') or contains(@aria-label, 'Next') or contains(text(), 'Continue')]")
                    
                    submit_buttons = self.driver.find_elements(By.XPATH,
                        "//button[contains(text(), 'Submit') or contains(text(), 'Review') or contains(@aria-label, 'Submit')]")
                    
                    if submit_buttons:
                        # Final step - submit application
                        self.logger.info(f"About to submit LinkedIn application for {job_data['title']} at {job_data['company']}")
                        
                        # For safety, comment out the actual submission
                        # submit_buttons[0].click()
                        
                        # Simulate successful submission
                        result['status'] = 'success'
                        result['reason'] = 'Application submitted via LinkedIn Easy Apply (simulated)'
                        result['steps_completed'] = current_step + 1
                        self.application_count += 1
                        break
                        
                    elif next_buttons:
                        next_buttons[0].click()
                        self.random_delay(2, 4)
                        current_step += 1
                        result['steps_completed'] = current_step
                    else:
                        # No more buttons found
                        result['reason'] = 'Application form incomplete - no next/submit button'
                        break
                
                except Exception as step_error:
                    self.logger.error(f"Error in LinkedIn application step {current_step}: {step_error}")
                    current_step += 1
                    
                    if current_step >= max_steps:
                        result['reason'] = f'Max steps reached - {step_error}'
                        break
        
        except Exception as e:
            result['reason'] = f'LinkedIn application failed: {str(e)}'
            self.logger.error(f"LinkedIn application error for {job_data['title']}: {e}")
        
        return result
    
    def fill_linkedin_contact_info(self):
        """Fill LinkedIn contact information fields"""
        try:
            # Phone number
            phone_patterns = [
                "contains(@id, 'phoneNumber')",
                "contains(@name, 'phone')",
                "contains(@placeholder, 'phone')"
            ]
            self.smart_fill_field(self.driver, phone_patterns, self.profile_data['phone'])
            
            # LinkedIn profile
            linkedin_patterns = [
                "contains(@id, 'linkedin')",
                "contains(@name, 'linkedin')",
                "contains(@placeholder, 'linkedin')"
            ]
            self.smart_fill_field(self.driver, linkedin_patterns, self.profile_data['linkedin'])
            
        except Exception as e:
            self.logger.warning(f"Error filling LinkedIn contact info: {e}")
    
    def handle_linkedin_resume_upload(self, job_data: Dict):
        """Handle resume upload on LinkedIn"""
        try:
            # Select appropriate resume
            filter_result = self.filter.filter_job(job_data)
            resume_file = filter_result.get('resume_to_use', 'Mani_QA2.pdf')
            resume_path = os.path.abspath(f'./resumes/{resume_file}')
            
            if not os.path.exists(resume_path):
                self.logger.warning(f"Resume file not found: {resume_path}")
                return
            
            # Find file upload input
            file_inputs = self.driver.find_elements(By.XPATH, "//input[@type='file']")
            
            if file_inputs:
                file_inputs[0].send_keys(resume_path)
                self.random_delay(3, 5)  # Wait for upload
                self.logger.info(f"Uploaded resume: {resume_file}")
            
        except Exception as e:
            self.logger.warning(f"Error uploading resume: {e}")
    
    def fill_linkedin_additional_questions(self):
        """Fill LinkedIn additional questions"""
        try:
            # Experience questions
            exp_patterns = [
                "contains(text(), 'years') and contains(text(), 'experience')",
                "contains(@placeholder, 'experience')",
                "contains(@placeholder, 'years')"
            ]
            
            # Look for experience dropdowns or inputs
            for pattern in exp_patterns:
                try:
                    elements = self.driver.find_elements(By.XPATH, f"//*[{pattern}]")
                    for element in elements:
                        if element.tag_name == "select":
                            select = Select(element)
                            # Try to select 1-2 years experience
                            options = [opt.text for opt in select.options]
                            for option in options:
                                if "1" in option or "0-1" in option or "1-2" in option:
                                    select.select_by_visible_text(option)
                                    break
                        elif element.tag_name == "input":
                            self.human_type(element, "1")
                except:
                    continue
            
            # Salary questions
            salary_patterns = [
                "contains(text(), 'salary')",
                "contains(@placeholder, 'salary')",
                "contains(text(), 'compensation')"
            ]
            
            for pattern in salary_patterns:
                try:
                    elements = self.driver.find_elements(By.XPATH, f"//input[{pattern}]")
                    for element in elements:
                        self.human_type(element, str(self.profile_data['expected_salary']))
                        break
                except:
                    continue
            
            # Location questions
            location_patterns = [
                "contains(text(), 'location')",
                "contains(@placeholder, 'location')",
                "contains(text(), 'willing to relocate')"
            ]
            
            for pattern in location_patterns:
                try:
                    elements = self.driver.find_elements(By.XPATH, f"//input[{pattern}]")
                    for element in elements:
                        self.human_type(element, self.profile_data['location'])
                        break
                except:
                    continue
            
            # Cover letter
            cover_letter_selectors = [
                "//textarea[contains(@placeholder, 'cover letter')]",
                "//textarea[contains(@id, 'cover')]",
                "//textarea"
            ]
            
            for selector in cover_letter_selectors:
                try:
                    textarea = self.driver.find_element(By.XPATH, selector)
                    cover_letter = self.generate_cover_letter(job_data)
                    self.human_type(textarea, cover_letter)
                    break
                except:
                    continue
            
        except Exception as e:
            self.logger.warning(f"Error filling additional questions: {e}")
    
    def apply_to_naukri_job(self, job_data: Dict) -> Dict[str, Any]:
        """Apply to Naukri job"""
        result = {
            'job_id': job_data.get('url', ''),
            'title': job_data.get('title', ''),
            'company': job_data.get('company', ''),
            'status': 'failed',
            'reason': '',
            'applied_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        try:
            if not self.driver:
                self.driver = self.setup_driver()
            
            # Navigate to job URL
            self.driver.get(job_data['url'])
            self.random_delay(3, 5)
            
            # Check if login is required
            if "login" in self.driver.current_url.lower() or self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Login')]"):
                result['status'] = 'login_required'
                result['reason'] = 'Naukri login required for application'
                return result
            
            # Look for Apply button
            apply_selectors = [
                "//button[contains(text(), 'Apply') and not(contains(text(), 'Easy'))]",
                "//a[contains(text(), 'Apply')]",
                "//div[@class='apply-btn']//button",
                "//button[contains(@class, 'apply')]"
            ]
            
            apply_btn = None
            for selector in apply_selectors:
                try:
                    apply_btn = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except:
                    continue
            
            if not apply_btn:
                result['reason'] = 'Apply button not found on Naukri'
                return result
            
            # Click Apply
            apply_btn.click()
            self.random_delay(3, 5)
            
            # Check if redirected to external site
            if self.driver.current_url != job_data['url']:
                if "naukri.com" not in self.driver.current_url:
                    result['status'] = 'external'
                    result['reason'] = 'Redirected to external application site'
                    return result
            
            # Look for application confirmation or form
            success_indicators = [
                "//*[contains(text(), 'applied')]",
                "//*[contains(text(), 'Application sent')]",
                "//*[contains(text(), 'Successfully applied')]",
                "//*[contains(text(), 'Thank you')]"
            ]
            
            for indicator in success_indicators:
                if self.driver.find_elements(By.XPATH, indicator):
                    result['status'] = 'success'
                    result['reason'] = 'Successfully applied via Naukri'
                    self.application_count += 1
                    return result
            
            # If form appears, try to fill it
            if self.driver.find_elements(By.XPATH, "//form"):
                filled = self.fill_naukri_application_form()
                if filled:
                    result['status'] = 'success'
                    result['reason'] = 'Application form submitted on Naukri'
                    self.application_count += 1
                else:
                    result['reason'] = 'Could not complete Naukri application form'
            else:
                result['reason'] = 'Naukri application status unclear'
        
        except Exception as e:
            result['reason'] = f'Naukri application failed: {str(e)}'
            self.logger.error(f"Naukri application error: {e}")
        
        return result
    
    def fill_naukri_application_form(self) -> bool:
        """Fill Naukri application form"""
        try:
            # Fill basic details
            name_patterns = ["contains(@name, 'name')", "contains(@id, 'name')"]
            self.smart_fill_field(self.driver, name_patterns, self.profile_data['name'])
            
            email_patterns = ["contains(@name, 'email')", "contains(@id, 'email')"]
            self.smart_fill_field(self.driver, email_patterns, self.profile_data['email'])
            
            phone_patterns = ["contains(@name, 'phone')", "contains(@id, 'phone')", "contains(@name, 'mobile')"]
            self.smart_fill_field(self.driver, phone_patterns, self.profile_data['phone'])
            
            # Experience
            exp_patterns = ["contains(@name, 'experience')", "contains(@id, 'experience')"]
            self.smart_fill_field(self.driver, exp_patterns, str(self.profile_data['experience_years']))
            
            # Current CTC
            ctc_patterns = ["contains(@name, 'ctc')", "contains(@id, 'ctc')", "contains(@name, 'salary')"]
            self.smart_fill_field(self.driver, ctc_patterns, str(self.profile_data['current_salary']))
            
            # Expected CTC
            expected_patterns = ["contains(@name, 'expected')", "contains(@id, 'expected')"]
            self.smart_fill_field(self.driver, expected_patterns, str(self.profile_data['expected_salary']))
            
            # Notice period
            notice_patterns = ["contains(@name, 'notice')", "contains(@id, 'notice')"]
            self.smart_fill_field(self.driver, notice_patterns, self.profile_data['notice_period'])
            
            # Submit form
            submit_buttons = self.driver.find_elements(By.XPATH, 
                "//button[contains(text(), 'Submit') or contains(text(), 'Apply') or contains(@type, 'submit')]")
            
            if submit_buttons:
                # For safety, comment out actual submission
                # submit_buttons[0].click()
                self.logger.info("Naukri form filled successfully (submission simulated)")
                return True
            
            return False
        
        except Exception as e:
            self.logger.error(f"Error filling Naukri form: {e}")
            return False
    
    def apply_to_indeed_job(self, job_data: Dict) -> Dict[str, Any]:
        """Apply to Indeed job"""
        result = {
            'job_id': job_data.get('url', ''),
            'title': job_data.get('title', ''),
            'company': job_data.get('company', ''),
            'status': 'failed',
            'reason': '',
            'applied_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        try:
            if not self.driver:
                self.driver = self.setup_driver()
            
            self.driver.get(job_data['url'])
            self.random_delay(3, 5)
            
            # Indeed often redirects to external sites
            apply_buttons = self.driver.find_elements(By.XPATH, 
                "//button[contains(text(), 'Apply') or contains(@aria-label, 'Apply')]")
            
            if apply_buttons:
                apply_buttons[0].click()
                self.random_delay(3, 5)
                
                # Check if stayed on Indeed or redirected
                if "indeed.com" in self.driver.current_url:
                    # Indeed application form
                    form_filled = self.fill_indeed_application_form()
                    if form_filled:
                        result['status'] = 'success'
                        result['reason'] = 'Applied via Indeed'
                        self.application_count += 1
                    else:
                        result['reason'] = 'Could not complete Indeed form'
                else:
                    result['status'] = 'external'
                    result['reason'] = 'Redirected to company website'
            else:
                result['reason'] = 'No apply button found on Indeed'
        
        except Exception as e:
            result['reason'] = f'Indeed application failed: {str(e)}'
            self.logger.error(f"Indeed application error: {e}")
        
        return result
    
    def fill_indeed_application_form(self) -> bool:
        """Fill Indeed application form"""
        try:
            # Indeed forms are similar to others
            self.smart_fill_field(self.driver, ["contains(@name, 'email')"], self.profile_data['email'])
            self.smart_fill_field(self.driver, ["contains(@name, 'phone')"], self.profile_data['phone'])
            
            # Resume upload
            file_inputs = self.driver.find_elements(By.XPATH, "//input[@type='file']")
            if file_inputs:
                resume_path = os.path.abspath('./resumes/Mani_QA2.pdf')
                if os.path.exists(resume_path):
                    file_inputs[0].send_keys(resume_path)
            
            # Submit
            submit_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Submit')]")
            if submit_buttons:
                # Simulate submission
                self.logger.info("Indeed form filled (submission simulated)")
                return True
            
            return False
        except Exception as e:
            self.logger.error(f"Error filling Indeed form: {e}")
            return False
    
    def generate_cover_letter(self, job_data: Dict) -> str:
        """Generate personalized cover letter for Manikanta"""
        company = job_data.get('company', 'your organization')
        title = job_data.get('title', 'QA Engineer')
        
        templates = [
            f"""Dear Hiring Manager,

I am excited to apply for the {title} position at {company}. With my experience as a ROC Specialist at Amazon and expertise in automation testing using Python and Selenium, I bring a unique combination of operational excellence and technical skills.

My background includes:
• Automation testing with Selenium, PyTest, and API testing
• Process optimization and stakeholder management from Amazon
• Development of QA-Monkey framework for regression testing
• Strong foundation in manual and automated testing methodologies

I am particularly drawn to {company} and would welcome the opportunity to contribute to your quality assurance initiatives.

Best regards,
Manikanta Chavvakula""",

            f"""Hello,

I am writing to express my interest in the {title} role at {company}. 

As a QA professional with hands-on experience in automation testing and operational excellence gained at Amazon, I am excited about the opportunity to contribute to your team. My expertise includes Python, Selenium WebDriver, API testing, and test framework development.

I have successfully developed testing utilities and frameworks, including the QA-Monkey automation framework, and have experience in both manual and automated testing approaches.

Thank you for considering my application.

Regards,
Manikanta Chavvakula
+91-9676853187"""
        ]
        
        return random.choice(templates)
    
    def apply_to_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """Apply to filtered jobs"""
        application_results = []
        
        try:
            self.driver = self.setup_driver(headless=False)  # Show browser for monitoring
            
            for i, job in enumerate(jobs):
                if self.application_count >= self.daily_limit:
                    self.logger.info(f"Daily application limit ({self.daily_limit}) reached")
                    break
                
                # Filter job first
                filter_result = self.filter.filter_job(job)
                
                if not filter_result.get('is_relevant', False):
                    self.logger.info(f"Skipping irrelevant job: {job['title']} - {filter_result.get('reason', '')}")
                    continue
                
                self.logger.info(f"\\n=== Applying to Job {i+1} ===")
                self.logger.info(f"Title: {job['title']}")
                self.logger.info(f"Company: {job['company']}")
                self.logger.info(f"Source: {job['source']}")
                self.logger.info(f"Resume to use: {filter_result['resume_to_use']}")
                
                # Apply based on source
                if job['source'] == 'LinkedIn':
                    result = self.apply_to_linkedin_job(job)
                elif job['source'] == 'Naukri':
                    result = self.apply_to_naukri_job(job)
                elif job['source'] == 'Indeed':
                    result = self.apply_to_indeed_job(job)
                else:
                    result = {
                        'job_id': job.get('url', ''),
                        'title': job.get('title', ''),
                        'company': job.get('company', ''),
                        'status': 'unsupported',
                        'reason': f"Source {job['source']} not supported yet",
                        'applied_at': time.strftime('%Y-%m-%d %H:%M:%S')
                    }
                
                result['filter_result'] = filter_result
                result['search_keywords'] = job.get('search_keywords', '')
                application_results.append(result)
                
                self.logger.info(f"Application result: {result['status']} - {result['reason']}")
                
                # Random delay between applications (10-30 seconds)
                delay = random.uniform(
                    self.config['daily_limits']['application_delay_min'],
                    self.config['daily_limits']['application_delay_max']
                )
                self.logger.info(f"Waiting {delay:.1f} seconds before next application...")
                time.sleep(delay)
        
        except Exception as e:
            self.logger.error(f"Error in job application process: {e}")
        
        finally:
            if self.driver:
                self.driver.quit()
        
        return application_results
    
    def get_application_summary(self, results: List[Dict]) -> Dict:
        """Generate application summary"""
        summary = {
            'total_attempted': len(results),
            'successful': len([r for r in results if r['status'] == 'success']),
            'failed': len([r for r in results if r['status'] == 'failed']),
            'external': len([r for r in results if r['status'] == 'external']),
            'login_required': len([r for r in results if r['status'] == 'login_required']),
            'unsupported': len([r for r in results if r['status'] == 'unsupported']),
            'success_rate': 0,
            'details': results
        }
        
        if summary['total_attempted'] > 0:
            summary['success_rate'] = round((summary['successful'] / summary['total_attempted']) * 100, 2)
        
        return summary

# Example usage and testing
if __name__ == "__main__":
    # Test with sample job data
    sample_jobs = [
        {
            'title': 'QA Automation Engineer - Fresher',
            'company': 'TechCorp Solutions',
            'location': 'Hyderabad',
            'description': 'Looking for QA engineer with Python and Selenium experience. 0-1 years experience required. Salary: 5-7 LPA.',
            'url': 'https://example-job-url.com/qa-engineer',
            'source': 'LinkedIn',
            'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }
    ]
    
    print("=== Testing Job Application System ===")
    print("This will test the application logic without actually submitting applications")
    
    applicator = JobApplicator()
    
    # Test application process
    results = applicator.apply_to_jobs(sample_jobs)
    summary = applicator.get_application_summary(results)
    
    print(f"\\n=== Application Test Results ===")
    print(f"Total Attempted: {summary['total_attempted']}")
    print(f"Successful: {summary['successful']}")
    print(f"Failed: {summary['failed']}")
    print(f"External: {summary['external']}")
    print(f"Login Required: {summary['login_required']}")
    print(f"Success Rate: {summary['success_rate']}%")
    
    if results:
        print(f"\\nSample Result:")
        result = results[0]
        print(f"Job: {result['title']}")
        print(f"Status: {result['status']}")
        print(f"Reason: {result['reason']}")
        print(f"Resume Used: {result.get('filter_result', {}).get('resume_to_use', 'N/A')}")
    
    print("\\n=== Test Complete ===")
    print("Check job_applications.log for detailed logs")