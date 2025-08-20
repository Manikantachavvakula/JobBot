import re
import json
from typing import Dict, List, Any
import logging

class JobFilter:
    def __init__(self, config_path: str = "config.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.target_roles = self.config['job_preferences']['roles']
        self.min_salary = self.config['job_preferences']['min_salary_lpa']
        self.max_salary = self.config['job_preferences'].get('max_salary_lpa', 15)
        self.target_locations = self.config['job_preferences']['locations']
        self.skills = self.config['skills']
        self.keywords = self.config['keywords']
        
        self.setup_logging()
        
    def setup_logging(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def is_relevant_role(self, job_title: str, job_description: str = "") -> Dict[str, Any]:
        """Check if job title/description matches target roles"""
        text = f"{job_title} {job_description}".lower()
        
        # Check for positive QA/Testing keywords
        positive_matches = 0
        matched_keywords = []
        
        for keyword in self.keywords['positive']:
            if keyword in text:
                positive_matches += 1
                matched_keywords.append(keyword)
        
        # Must have at least 2 positive matches
        if positive_matches < 2:
            return {
                'is_relevant': False,
                'reason': 'Insufficient QA/Testing keywords',
                'matched_keywords': matched_keywords,
                'score': 0
            }
        
        # Check for negative keywords (high experience requirements)
        negative_matches = 0
        negative_keywords = []
        
        for keyword in self.keywords['negative']:
            if keyword in text:
                negative_matches += 1
                negative_keywords.append(keyword)
        
        # Check for fresher-friendly indicators
        fresher_matches = 0
        fresher_keywords = []
        
        for keyword in self.keywords['fresher_friendly']:
            if keyword in text:
                fresher_matches += 1
                fresher_keywords.append(keyword)
        
        # Decision logic
        if negative_matches > 0:
            if fresher_matches == 0:
                return {
                    'is_relevant': False,
                    'reason': f'High experience requirement: {negative_keywords}',
                    'matched_keywords': matched_keywords,
                    'score': 0
                }
        
        # Calculate relevance score
        relevance_score = min(100, (positive_matches * 10) + (fresher_matches * 5))
        
        return {
            'is_relevant': True,
            'reason': f'Good match with {positive_matches} QA keywords',
            'matched_keywords': matched_keywords,
            'fresher_friendly': fresher_matches > 0,
            'score': relevance_score
        }
    
    def extract_salary(self, job_text: str) -> Dict[str, Any]:
        """Extract salary from job description"""
        text = job_text.lower()
        
        # Enhanced salary patterns for Indian job market
        patterns = [
            r'(\d+(?:\.\d+)?)\s*-?\s*(\d+(?:\.\d+)?)?\s*lpa',
            r'₹\s*(\d+(?:\.\d+)?)\s*-?\s*(\d+(?:\.\d+)?)?\s*lakh',
            r'(\d+(?:\.\d+)?)\s*-?\s*(\d+(?:\.\d+)?)?\s*lakhs?\s*per\s*annum',
            r'salary:?\s*(\d+(?:\.\d+)?)\s*-?\s*(\d+(?:\.\d+)?)?\s*lpa',
            r'ctc:?\s*(\d+(?:\.\d+)?)\s*-?\s*(\d+(?:\.\d+)?)?\s*lpa',
            r'package:?\s*(\d+(?:\.\d+)?)\s*-?\s*(\d+(?:\.\d+)?)?\s*lpa',
            r'(\d+(?:\.\d+)?)\s*to\s*(\d+(?:\.\d+)?)\s*lpa',
            r'upto?\s*(\d+(?:\.\d+)?)\s*lpa'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            if matches:
                if isinstance(matches[0], tuple):
                    # Range format
                    salaries = [float(x) for x in matches[0] if x and x.replace('.', '').isdigit()]
                    if len(salaries) == 2:
                        return {
                            'min_salary': min(salaries),
                            'max_salary': max(salaries),
                            'average_salary': sum(salaries) / 2,
                            'found': True
                        }
                    elif len(salaries) == 1:
                        return {
                            'min_salary': salaries[0],
                            'max_salary': salaries[0],
                            'average_salary': salaries[0],
                            'found': True
                        }
                else:
                    # Single value
                    salary = float(matches[0])
                    return {
                        'min_salary': salary,
                        'max_salary': salary,
                        'average_salary': salary,
                        'found': True
                    }
        
        return {
            'min_salary': 0,
            'max_salary': 0,
            'average_salary': 0,
            'found': False
        }
    
    def is_location_match(self, location: str) -> Dict[str, Any]:
        """Check if job location matches preferences"""
        if not location:
            return {'is_match': True, 'reason': 'No location specified (assuming remote)'}
            
        location_lower = location.lower()
        
        # Direct location matches
        for target_loc in self.target_locations:
            if target_loc.lower() in location_lower:
                return {'is_match': True, 'reason': f'Matches preferred location: {target_loc}'}
        
        # Remote work indicators
        remote_indicators = [
            'remote', 'work from home', 'wfh', 'anywhere', 'virtual',
            'distributed', 'home based', 'telecommute'
        ]
        
        for indicator in remote_indicators:
            if indicator in location_lower:
                return {'is_match': True, 'reason': f'Remote work: {indicator}'}
        
        # Partial matches (for flexibility)
        for target_loc in self.target_locations:
            if any(word in location_lower for word in target_loc.lower().split()):
                return {'is_match': True, 'reason': f'Partial location match: {target_loc}'}
        
        return {'is_match': False, 'reason': f'Location {location} not in preferred list'}
    
    def select_resume(self, job_title: str, job_description: str) -> str:
        """Select appropriate resume based on job requirements"""
        text = f"{job_title} {job_description}".lower()
        
        # Advanced automation keywords (for Mani_QA1.pdf)
        automation_keywords = [
            'selenium', 'pytest', 'automation framework', 'ci/cd', 'jenkins',
            'api testing', 'python automation', 'test framework', 'automation engineer',
            'sdet', 'technical testing', 'test automation', 'framework development',
            'scripting', 'api automation', 'regression automation'
        ]
        
        # Entry level keywords (for Mani_QA3.pdf)
        entry_keywords = [
            'fresher', 'entry level', 'trainee', 'graduate', '0-1 year',
            '0-2 year', 'manual testing', 'basic', 'beginner', 'new grad',
            'associate', 'junior', 'starting career'
        ]
        
        # Advanced project keywords (QA-Monkey, NetWrecker mentions)
        advanced_project_keywords = [
            'framework', 'tool development', 'python', 'automation tool',
            'testing utility', 'performance testing', 'load testing'
        ]
        
        # Count matches
        automation_score = sum(1 for keyword in automation_keywords if keyword in text)
        entry_score = sum(1 for keyword in entry_keywords if keyword in text)
        advanced_score = sum(1 for keyword in advanced_project_keywords if keyword in text)
        
        # Decision logic
        if automation_score >= 3 or advanced_score >= 2:
            return self.config['resume_files']['qa_automation']  # Mani_QA1.pdf
        elif entry_score >= 2:
            return self.config['resume_files']['qa_entry']       # Mani_QA3.pdf  
        else:
            return self.config['resume_files']['qa_general']     # Mani_QA2.pdf
    
    def calculate_experience_match(self, job_description: str) -> Dict[str, Any]:
        """Check if experience requirements match Manikanta's profile"""
        text = job_description.lower()
        
        # Manikanta's experience: 1+ years at Amazon + internships + projects
        actual_experience = 1.5  # Conservative estimate
        
        # Extract experience requirements
        exp_patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'(\d+)\s*to\s*(\d+)\s*years?',
            r'minimum\s*(\d+)\s*years?',
            r'at\s*least\s*(\d+)\s*years?',
            r'(\d+)\s*-\s*(\d+)\s*years?'
        ]
        
        for pattern in exp_patterns:
            matches = re.findall(pattern, text)
            if matches:
                if isinstance(matches[0], tuple):
                    exp_nums = [int(x) for x in matches[0] if x.isdigit()]
                    required_exp = min(exp_nums) if exp_nums else 0
                else:
                    required_exp = int(matches[0])
                
                if required_exp <= actual_experience + 1:  # Allow 1 year flexibility
                    return {
                        'is_match': True,
                        'required_exp': required_exp,
                        'reason': f'Experience requirement ({required_exp} years) matches profile'
                    }
                else:
                    return {
                        'is_match': False,
                        'required_exp': required_exp,
                        'reason': f'Requires {required_exp} years, profile has {actual_experience}'
                    }
        
        # No specific experience mentioned - assume suitable for freshers
        return {
            'is_match': True,
            'required_exp': 0,
            'reason': 'No specific experience requirement mentioned'
        }
    
    def filter_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main filtering function for a job"""
        try:
            title = job_data.get('title', '')
            description = job_data.get('description', '')
            location = job_data.get('location', '')
            company = job_data.get('company', '')
            
            filter_result = {
                'is_relevant': False,
                'reason': '',
                'details': {},
                'resume_to_use': '',
                'relevance_score': 0
            }
            
            # Step 1: Check role relevance
            role_check = self.is_relevant_role(title, description)
            filter_result['details']['role_check'] = role_check
            
            if not role_check['is_relevant']:
                filter_result['reason'] = role_check['reason']
                return filter_result
            
            # Step 2: Check location
            location_check = self.is_location_match(location)
            filter_result['details']['location_check'] = location_check
            
            if not location_check['is_match']:
                filter_result['reason'] = location_check['reason']
                return filter_result
            
            # Step 3: Check experience requirements
            exp_check = self.calculate_experience_match(description)
            filter_result['details']['experience_check'] = exp_check
            
            if not exp_check['is_match']:
                filter_result['reason'] = exp_check['reason']
                return filter_result
            
            # Step 4: Check salary (if available)
            salary_info = self.extract_salary(f"{title} {description}")
            filter_result['details']['salary_info'] = salary_info
            
            if salary_info['found']:
                if salary_info['max_salary'] < self.min_salary:
                    filter_result['reason'] = f"Salary {salary_info['max_salary']} LPA below minimum {self.min_salary} LPA"
                    return filter_result
                
                if salary_info['min_salary'] > self.max_salary:
                    filter_result['reason'] = f"Salary {salary_info['min_salary']} LPA above realistic range"
                    return filter_result
            
            # Step 5: Select appropriate resume
            resume_file = self.select_resume(title, description)
            
            # All checks passed!
            filter_result.update({
                'is_relevant': True,
                'reason': 'Job matches all criteria',
                'resume_to_use': resume_file,
                'relevance_score': role_check['score'],
                'salary_lpa': salary_info['average_salary'] if salary_info['found'] else 'Not specified',
                'is_fresher_friendly': role_check.get('fresher_friendly', False),
                'matched_keywords': role_check['matched_keywords']
            })
            
            return filter_result
            
        except Exception as e:
            self.logger.error(f"Error filtering job: {e}")
            return {
                'is_relevant': False,
                'reason': f'Error filtering job: {str(e)}',
                'details': {},
                'resume_to_use': '',
                'relevance_score': 0
            }
    
    def get_filter_summary(self, jobs: List[Dict]) -> Dict[str, Any]:
        """Generate filtering summary statistics"""
        total_jobs = len(jobs)
        relevant_jobs = []
        rejection_reasons = {}
        
        for job in jobs:
            result = self.filter_job(job)
            if result['is_relevant']:
                relevant_jobs.append(job)
            else:
                reason = result['reason']
                rejection_reasons[reason] = rejection_reasons.get(reason, 0) + 1
        
        return {
            'total_jobs': total_jobs,
            'relevant_jobs': len(relevant_jobs),
            'relevance_rate': round((len(relevant_jobs) / max(total_jobs, 1)) * 100, 2),
            'rejection_reasons': rejection_reasons,
            'relevant_job_list': relevant_jobs
        }

# Example usage and testing
if __name__ == "__main__":
    filter_obj = JobFilter()
    
    # Test jobs based on Manikanta's profile
    test_jobs = [
        {
            'title': 'QA Automation Engineer - Fresher',
            'description': 'Looking for fresher QA engineer with Python and Selenium knowledge. 0-1 years experience. Salary: 5-8 LPA',
            'location': 'Hyderabad',
            'company': 'Tech Startup',
            'source': 'LinkedIn'
        },
        {
            'title': 'Senior Test Lead',
            'description': 'Seeking experienced test lead with 5+ years experience in automation testing',
            'location': 'Bangalore',
            'company': 'Big Corp',
            'source': 'Naukri'
        },
        {
            'title': 'SDET - Entry Level',
            'description': 'Entry level SDET position. Python, Selenium, API testing. Remote work available. Fresh graduates welcome.',
            'location': 'Remote',
            'company': 'Product Company',
            'source': 'Indeed'
        }
    ]
    
    print("=== Job Filtering Test Results ===")
    for i, job in enumerate(test_jobs, 1):
        result = filter_obj.filter_job(job)
        print(f"\\nJob {i}: {job['title']}")
        print(f"Relevant: {result['is_relevant']}")
        print(f"Reason: {result['reason']}")
        print(f"Resume: {result['resume_to_use']}")
        print(f"Score: {result['relevance_score']}")
        if result['is_relevant']:
            print(f"Salary: {result['salary_lpa']}")
            print(f"Keywords: {result['matched_keywords']}")
    
    # Test summary
    summary = filter_obj.get_filter_summary(test_jobs)
    print(f"\\n=== Summary ===")
    print(f"Total Jobs: {summary['total_jobs']}")
    print(f"Relevant Jobs: {summary['relevant_jobs']}")
    print(f"Relevance Rate: {summary['relevance_rate']}%")
    print(f"Rejection Reasons: {summary['rejection_reasons']}")