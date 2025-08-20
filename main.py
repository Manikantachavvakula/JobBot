#!/usr/bin/env python3
"""
AI-Powered Job Search Bot for Manikanta Chavvakula
Author: Manikanta Chavvakula
Version: 1.0

This bot automates job searching, applications, and HR outreach for QA/Automation roles.
Designed specifically for Manikanta's profile and requirements.

Usage:
    python main.py           # Run with daily scheduling
    python main.py --once    # Run once for testing
    python main.py --test    # Run in test mode (no actual applications/emails)
    python main.py --weekly  # Generate weekly report only
"""

import time
import json
import schedule
import logging
import sys
import os
import argparse
from datetime import datetime, timedelta
from typing import Dict, List

# Import our custom modules
from scrapers import JobScraper
from filters import JobFilter
from auto_apply import JobApplicator
from emailer import EmailManager
from reporter import JobReporter

class ManiJobSearchBot:
    def __init__(self, config_path: str = "config.json", test_mode: bool = False):
        """Initialize Manikanta's job search bot"""
        self.config_path = config_path
        self.test_mode = test_mode
        self.load_config()
        self.setup_logging()
        
        # Initialize components
        self.scraper = JobScraper(config_path)
        self.filter = JobFilter(config_path)
        self.applicator = JobApplicator(config_path)
        self.emailer = EmailManager(config_path)
        self.reporter = JobReporter(config_path)
        
        # Runtime statistics
        self.daily_stats = {
            'jobs_scraped': 0,
            'jobs_filtered': 0,
            'applications_attempted': 0,
            'applications_successful': 0,
            'emails_sent': 0,
            'start_time': datetime.now(),
            'last_run': None,
            'errors': []
        }
        
        # Manikanta's profile
        self.profile = self.config['profile']
        
        self.logger.info(f"🤖 Manikanta's Job Search Bot initialized successfully")
        self.logger.info(f"Target: {', '.join(self.config['job_preferences']['roles'][:3])}")
        self.logger.info(f"Locations: {', '.join(self.config['job_preferences']['locations'][:3])}")
        self.logger.info(f"Test Mode: {'ON' if test_mode else 'OFF'}")
        
    def load_config(self):
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
            print("✅ Configuration loaded successfully")
        except FileNotFoundError:
            print(f"❌ Config file {self.config_path} not found!")
            print("Please create config.json with your profile and preferences.")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in config file: {e}")
            sys.exit(1)
    
    def setup_logging(self):
        """Setup comprehensive logging configuration"""
        # Create logs directory
        os.makedirs('logs', exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/mani_job_bot.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger('ManiJobSearchBot')
    
    def print_banner(self):
        """Print startup banner"""
        banner = f"""
╔══════════════════════════════════════════════════════════════╗
║                  🤖 MANIKANTA'S JOB SEARCH BOT                ║
║                                                              ║
║  👨‍💻 Profile: {self.profile['name']:<45} ║
║  📧 Email: {self.profile['email']:<47} ║
║  📱 Phone: {self.profile['phone']:<47} ║
║  📍 Location: {self.profile['location']:<44} ║
║                                                              ║
║  🎯 Target Roles: QA Engineer | Automation Engineer         ║
║  💰 Salary Range: ₹{self.config['job_preferences']['min_salary_lpa']}+ LPA                                    ║
║  🌍 Preferred: {', '.join(self.config['job_preferences']['locations'][:2]):<39} ║
║                                                              ║
║  📊 Daily Limits:                                            ║
║     • Applications: {self.config['daily_limits']['max_applications']:<3} per day                            ║
║     • HR Emails: {self.config['daily_limits']['max_hr_emails']:<3} per day                               ║
║                                                              ║
║  🚀 Status: {'TEST MODE' if self.test_mode else 'LIVE MODE':<45} ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met for Manikanta's profile"""
        self.logger.info("🔍 Checking prerequisites...")
        
        issues = []
        
        # Check resume files
        resume_dir = "./resumes"
        if not os.path.exists(resume_dir):
            os.makedirs(resume_dir)
            issues.append("Created resume directory - please add resume files")
        
        resume_files = self.config.get('resume_files', {})
        missing_resumes = []
        
        for resume_type, filename in resume_files.items():
            resume_path = os.path.join(resume_dir, filename)
            if not os.path.exists(resume_path):
                missing_resumes.append(f"{filename} ({resume_type})")
        
        if missing_resumes:
            issues.append(f"Missing resume files: {', '.join(missing_resumes)}")
        
        # Check email configuration
        email_config = self.config.get('email_config', {})
        if not email_config.get('sender_email'):
            issues.append("Email configuration missing - update config.json")
        
        if email_config.get('sender_password') == 'your_gmail_app_password_here':
            issues.append("Gmail app password not configured")
        
        # Check profile completeness
        required_profile_fields = ['name', 'email', 'phone', 'location']
        for field in required_profile_fields:
            if not self.config['profile'].get(field):
                issues.append(f"Profile field '{field}' is missing")
        
        if issues:
            self.logger.error("❌ Prerequisites check failed:")
            for issue in issues:
                self.logger.error(f"   • {issue}")
            
            print("\\n🛠️ How to fix these issues:")
            print("1. Add your resume files to the resumes/ directory")
            print("2. Set up Gmail app password: https://support.google.com/accounts/answer/185833")
            print("3. Update config.json with your complete profile information")
            print("4. Run the setup script: python setup.py")
            
            return False
        
        self.logger.info("✅ All prerequisites met - ready to search for jobs!")
        return True
    
    def morning_routine(self):
        """Morning job search routine (9:00 AM)"""
        self.logger.info("🌅 Starting morning routine for Manikanta...")
        routine_start = datetime.now()
        
        try:
            # Reset daily counters for new day
            if self.daily_stats['last_run'] != 'morning' or \
               (datetime.now() - self.daily_stats['start_time']).days >= 1:
                self.reset_daily_stats()
            
            # Step 1: Scrape fresh jobs
            self.logger.info("🔍 Step 1: Scraping new QA/Automation jobs...")
            jobs = self.scraper.scrape_all_sites()
            self.daily_stats['jobs_scraped'] += len(jobs)
            
            if not jobs:
                self.logger.warning("⚠️ No jobs scraped. This might indicate site changes or network issues.")
                return
            
            # Save scraped jobs
            timestamp = datetime.now().strftime('%Y%m%d_morning')
            self.reporter.save_scraped_jobs(jobs, f"scraped_jobs_{timestamp}")
            
            # Step 2: Filter relevant jobs using Manikanta's criteria
            self.logger.info("🎯 Step 2: Filtering jobs relevant to Manikanta's profile...")
            relevant_jobs = []
            
            for job in jobs:
                filter_result = self.filter.filter_job(job)
                if filter_result.get('is_relevant', False):
                    job['filter_result'] = filter_result
                    relevant_jobs.append(job)
            
            self.daily_stats['jobs_filtered'] = len(relevant_jobs)
            self.logger.info(f"✅ Found {len(relevant_jobs)} relevant jobs out of {len(jobs)} total")
            
            if not relevant_jobs:
                self.logger.info("ℹ️ No relevant jobs found this morning. Will try again in the evening.")
                return
            
            # Log top matches
            sorted_jobs = sorted(relevant_jobs, key=lambda x: x['filter_result'].get('relevance_score', 0), reverse=True)
            self.logger.info("🏆 Top job matches:")
            for i, job in enumerate(sorted_jobs[:3]):
                score = job['filter_result'].get('relevance_score', 0)
                self.logger.info(f"   {i+1}. {job['title']} at {job['company']} (Score: {score}%)")
            
            # Step 3: Apply to morning batch
            morning_limit = self.config['daily_limits']['morning_applications']
            morning_jobs = sorted_jobs[:morning_limit]  # Take best matches first
            
            self.logger.info(f"📝 Step 3: Applying to {len(morning_jobs)} jobs...")
            
            if self.test_mode:
                self.logger.info("🧪 TEST MODE: Simulating applications...")
                application_results = self.simulate_applications(morning_jobs)
            else:
                application_results = self.applicator.apply_to_jobs(morning_jobs)
            
            # Update stats
            self.daily_stats['applications_attempted'] += len(application_results)
            self.daily_stats['applications_successful'] += len([r for r in application_results if r['status'] == 'success'])
            
            # Save application results
            self.reporter.save_application_results(application_results, f"application_results_{timestamp}")
            
            # Step 4: HR outreach for remaining good jobs
            self.logger.info("📧 Step 4: Starting HR outreach...")
            remaining_jobs = sorted_jobs[morning_limit:morning_limit+15]  # Next 15 best jobs
            
            if remaining_jobs:
                if self.test_mode:
                    self.logger.info("🧪 TEST MODE: Simulating HR emails...")
                    email_results = self.simulate_emails(remaining_jobs)
                else:
                    email_results = self.emailer.send_job_application_emails(remaining_jobs)
                
                self.daily_stats['emails_sent'] += len([e for e in email_results if e.get('success', False)])
                
                # Save email results
                self.reporter.save_email_results(email_results, f"email_results_{timestamp}")
            
            self.daily_stats['last_run'] = 'morning'
            
            runtime = datetime.now() - routine_start
            self.logger.info(f"✅ Morning routine completed in {runtime.total_seconds():.1f} seconds")
            self.print_session_summary()
            
        except Exception as e:
            self.logger.error(f"❌ Error in morning routine: {e}")
            self.daily_stats['errors'].append(f"Morning routine: {e}")
    
    def evening_routine(self):
        """Evening job search routine (6:00 PM)"""
        self.logger.info("🌆 Starting evening routine for Manikanta...")
        routine_start = datetime.now()
        
        try:
            # Step 1: Scrape for additional jobs (different keywords/sources)
            self.logger.info("🔍 Step 1: Evening job search sweep...")
            
            # Use alternative search terms for broader coverage
            alternative_searches = [
                "Software Tester Hyderabad",
                "SDET Bangalore", 
                "Test Engineer Remote",
                "Quality Assurance Chennai"
            ]
            
            evening_jobs = []
            for search_term in alternative_searches:
                try:
                    jobs = self.scraper.search_specific_keywords([search_term])
                    evening_jobs.extend(jobs)
                except Exception as e:
                    self.logger.warning(f"Search failed for '{search_term}': {e}")
            
            if evening_jobs:
                # Save evening jobs
                timestamp = datetime.now().strftime('%Y%m%d_evening')
                self.reporter.save_scraped_jobs(evening_jobs, f"scraped_jobs_{timestamp}")
                
                # Filter evening jobs
                relevant_evening_jobs = []
                for job in evening_jobs:
                    filter_result = self.filter.filter_job(job)
                    if filter_result.get('is_relevant', False):
                        job['filter_result'] = filter_result
                        relevant_evening_jobs.append(job)
                
                self.logger.info(f"🎯 Found {len(relevant_evening_jobs)} relevant evening jobs")
                
                # Apply to evening batch (if under daily limit)
                evening_limit = self.config['daily_limits']['evening_applications']
                remaining_quota = self.config['daily_limits']['max_applications'] - self.daily_stats['applications_attempted']
                
                if relevant_evening_jobs and remaining_quota > 0:
                    evening_applications = min(evening_limit, remaining_quota)
                    best_evening_jobs = sorted(relevant_evening_jobs, 
                                             key=lambda x: x['filter_result'].get('relevance_score', 0), 
                                             reverse=True)[:evening_applications]
                    
                    self.logger.info(f"📝 Step 2: Applying to {len(best_evening_jobs)} evening jobs...")
                    
                    if self.test_mode:
                        application_results = self.simulate_applications(best_evening_jobs)
                    else:
                        application_results = self.applicator.apply_to_jobs(best_evening_jobs)
                    
                    # Update stats
                    self.daily_stats['applications_attempted'] += len(application_results)
                    self.daily_stats['applications_successful'] += len([r for r in application_results if r['status'] == 'success'])
                    
                    # Save results
                    self.reporter.save_application_results(application_results, f"application_results_{timestamp}")
            
            # Step 3: Generate and send daily summary
            self.logger.info("📊 Step 3: Generating daily summary...")
            self.generate_and_send_daily_summary()
            
            self.daily_stats['last_run'] = 'evening'
            
            runtime = datetime.now() - routine_start
            self.logger.info(f"✅ Evening routine completed in {runtime.total_seconds():.1f} seconds")
            
        except Exception as e:
            self.logger.error(f"❌ Error in evening routine: {e}")
            self.daily_stats['errors'].append(f"Evening routine: {e}")
    
    def simulate_applications(self, jobs: List[Dict]) -> List[Dict]:
        """Simulate job applications for testing"""
        results = []
        for job in jobs:
            # Simulate realistic success/failure rates
            import random
            success_chance = 0.7  # 70% success rate in simulation
            
            if random.random() < success_chance:
                status = 'success'
                reason = 'Application submitted successfully (simulated)'
            else:
                status = random.choice(['failed', 'external', 'login_required'])
                reason = f'Simulated {status} status'
            
            result = {
                'job_id': job.get('url', ''),
                'title': job.get('title', ''),
                'company': job.get('company', ''),
                'status': status,
                'reason': reason,
                'applied_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'filter_result': job.get('filter_result', {}),
                'search_keywords': job.get('search_keywords', '')
            }
            results.append(result)
        
        return results
    
    def simulate_emails(self, jobs: List[Dict]) -> List[Dict]:
        """Simulate email sending for testing"""
        results = []
        for job in jobs[:10]:  # Limit to 10 for testing
            import random
            
            result = {
                'job_title': job.get('title', ''),
                'company': job.get('company', ''),
                'recipient_email': f"hr@{job.get('company', 'company').lower().replace(' ', '')}.com",
                'recipient_name': 'HR Team',
                'email_type': random.choice(['formal_application', 'networking']),
                'contact_source': 'domain_pattern',
                'confidence': 'medium',
                'success': random.random() < 0.8,  # 80% success rate
                'sent_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            results.append(result)
        
        return results
    
    def generate_and_send_daily_summary(self):
        """Generate comprehensive daily summary for Manikanta"""
        try:
            # Collect all today's data
            today = datetime.now().strftime('%Y%m%d')
            
            # Get application summary
            application_summary = {
                'total_attempted': self.daily_stats['applications_attempted'],
                'successful': self.daily_stats['applications_successful'],
                'failed': self.daily_stats['applications_attempted'] - self.daily_stats['applications_successful'],
                'external': 0,
                'login_required': 0,
                'details': []
            }
            
            # Get email results and detailed data
            email_results = []
            all_jobs_scraped = []
            
            # Load today's detailed data
            data_dir = "data"
            if os.path.exists(data_dir):
                for filename in os.listdir(data_dir):
                    if today in filename and filename.endswith('.json'):
                        try:
                            with open(os.path.join(data_dir, filename), 'r') as f:
                                data = json.load(f)
                            
                            if 'application_results' in filename:
                                application_summary['details'].extend(data)
                                # Recalculate status counts
                                application_summary['failed'] = len([a for a in data if a['status'] == 'failed'])
                                application_summary['external'] = len([a for a in data if a['status'] == 'external'])
                                application_summary['login_required'] = len([a for a in data if a['status'] == 'login_required'])
                            
                            elif 'email_results' in filename:
                                email_results.extend(data)
                            
                            elif 'scraped_jobs' in filename:
                                all_jobs_scraped.extend(data)
                        
                        except Exception as e:
                            self.logger.error(f"Error loading {filename}: {e}")
            
            # Generate HTML report
            report_path = self.reporter.generate_daily_report(application_summary, email_results, all_jobs_scraped)
            
            # Send summary email to Manikanta
            if not self.test_mode and self.config.get('email_config', {}).get('sender_email'):
                success = self.emailer.send_daily_summary_email(application_summary, email_results)
                if success:
                    self.logger.info("📧 Daily summary email sent to Manikanta")
                else:
                    self.logger.error("❌ Failed to send daily summary email")
            
            # Print summary to console
            self.print_daily_summary(application_summary, email_results)
            
            if report_path:
                self.logger.info(f"📋 Daily report generated: {report_path}")
        
        except Exception as e:
            self.logger.error(f"Error generating daily summary: {e}")
    
    def print_daily_summary(self, app_summary: Dict, email_results: List[Dict]):
        """Print comprehensive daily summary"""
        runtime = datetime.now() - self.daily_stats['start_time']
        successful_emails = len([e for e in email_results if e.get('success', False)])
        
        print("\\n" + "="*80)
        print(f"📊 DAILY JOB SEARCH SUMMARY FOR {self.profile['name'].upper()}")
        print(f"📅 {datetime.now().strftime('%A, %B %d, %Y')}")
        print("="*80)
        
        print(f"🕐 Session Runtime: {runtime}")
        print(f"🤖 Mode: {'TEST MODE' if self.test_mode else 'LIVE MODE'}")
        print()
        
        print("📈 PERFORMANCE METRICS:")
        print(f"   🔍 Jobs Scraped: {self.daily_stats['jobs_scraped']}")
        print(f"   🎯 Jobs Filtered: {self.daily_stats['jobs_filtered']}")
        print(f"   📝 Applications Attempted: {self.daily_stats['applications_attempted']}")
        print(f"   ✅ Applications Successful: {self.daily_stats['applications_successful']}")
        print(f"   📧 HR Emails Sent: {successful_emails}")
        
        if self.daily_stats['applications_attempted'] > 0:
            success_rate = (self.daily_stats['applications_successful'] / self.daily_stats['applications_attempted']) * 100
            print(f"   📊 Success Rate: {success_rate:.1f}%")
        
        print()
        
        # Daily limits progress
        app_progress = (self.daily_stats['applications_attempted'] / self.config['daily_limits']['max_applications']) * 100
        email_progress = (len(email_results) / self.config['daily_limits']['max_hr_emails']) * 100
        
        print("🎯 DAILY GOALS PROGRESS:")
        print(f"   📝 Applications: {self.daily_stats['applications_attempted']}/{self.config['daily_limits']['max_applications']} ({app_progress:.1f}%)")
        print(f"   📧 HR Emails: {len(email_results)}/{self.config['daily_limits']['max_hr_emails']} ({email_progress:.1f}%)")
        
        # Success breakdown
        if app_summary['details']:
            print("\\n✅ SUCCESSFUL APPLICATIONS TODAY:")
            successful_apps = [app for app in app_summary['details'] if app['status'] == 'success']
            
            if successful_apps:
                for i, app in enumerate(successful_apps, 1):
                    resume = app.get('filter_result', {}).get('resume_to_use', 'N/A').replace('.pdf', '')
                    score = app.get('filter_result', {}).get('relevance_score', 0)
                    print(f"   {i}. {app['title']} at {app['company']} (Resume: {resume}, Score: {score}%)")
            else:
                print("   No successful applications yet today. Keep trying! 💪")
        
        if self.daily_stats['errors']:
            print("\\n⚠️ ERRORS ENCOUNTERED:")
            for error in self.daily_stats['errors']:
                print(f"   • {error}")
        
        print()
        print("🚀 NEXT STEPS FOR MANIKANTA:")
        print("   • Check email for application responses")
        print("   • Follow up on external applications manually")
        print("   • Update LinkedIn profile with recent projects")
        print("   • Prepare for potential interview calls")
        print("   • Review and optimize resume based on feedback")
        
        print("="*80)
        print(f"🌟 Keep going, {self.profile['name']}! Every application brings you closer to your ideal QA role!")
        print("="*80 + "\\n")
    
    def print_session_summary(self):
        """Print quick session summary"""
        print(f"\\n📊 Quick Update: {self.daily_stats['applications_attempted']} applications, {self.daily_stats['emails_sent']} emails sent")
    
    def reset_daily_stats(self):
        """Reset daily statistics for new day"""
        self.daily_stats.update({
            'jobs_scraped': 0,
            'jobs_filtered': 0,
            'applications_attempted': 0,
            'applications_successful': 0,
            'emails_sent': 0,
            'start_time': datetime.now(),
            'errors': []
        })
    
    def run_once(self):
        """Run the bot once (for testing)"""
        self.print_banner()
        self.logger.info("🚀 Running Manikanta's job search bot once...")
        
        if not self.check_prerequisites():
            return False
        
        try:
            # Run both routines with a break
            self.morning_routine()
            
            self.logger.info("⏸️ 5-minute break between routines...")
            time.sleep(300)  # 5 minute break
            
            self.evening_routine()
            
            return True
        except KeyboardInterrupt:
            self.logger.info("⏹️ Bot stopped by user")
            return False
        except Exception as e:
            self.logger.error(f"❌ Critical error in run_once: {e}")
            return False
    
    def schedule_daily_runs(self):
        """Schedule daily morning and evening runs"""
        self.logger.info("📅 Scheduling Manikanta's daily job search runs...")
        
        # Schedule morning routine (9:00 AM) - Fresh job search
        schedule.every().day.at("09:00").do(self.morning_routine)
        
        # Schedule evening routine (6:00 PM) - Additional search + summary
        schedule.every().day.at("18:00").do(self.evening_routine)
        
        # Schedule weekly report (Sunday 10:00 AM)
        schedule.every().sunday.at("10:00").do(self.generate_weekly_report)
        
        # Schedule cleanup (Sunday 2:00 AM)
        schedule.every().sunday.at("02:00").do(self.reporter.cleanup_old_files)
        
        self.logger.info("✅ Scheduled daily runs:")
        self.logger.info("   🌅 Morning: 9:00 AM (job search + applications)")
        self.logger.info("   🌆 Evening: 6:00 PM (additional search + summary)")
        self.logger.info("   📊 Weekly report: Sunday 10:00 AM")
        self.logger.info("   🧹 Cleanup: Sunday 2:00 AM")
    
    def generate_weekly_report(self):
        """Generate weekly performance report"""
        try:
            self.logger.info("📊 Generating weekly report for Manikanta...")
            weekly_report = self.reporter.generate_weekly_report()
            
            if weekly_report:
                self.logger.info(f"✅ Weekly report generated: {weekly_report}")
                
                # Get weekly summary for email
                weekly_summary = self.reporter.get_weekly_summary()
                total_apps = weekly_summary.get('total_applications', 0)
                success_apps = weekly_summary.get('successful_applications', 0)
                
                self.logger.info(f"📈 Week Summary: {total_apps} applications, {success_apps} successful")
            else:
                self.logger.error("❌ Failed to generate weekly report")
        
        except Exception as e:
            self.logger.error(f"Error generating weekly report: {e}")
    
    def run_scheduled(self):
        """Run the bot with daily scheduling"""
        self.print_banner()
        self.logger.info("🤖 Starting Manikanta's scheduled job search bot...")
        
        if not self.check_prerequisites():
            return
        
        self.schedule_daily_runs()
        
        print("\\n🤖 Manikanta's Job Search Bot is now running!")
        print("📅 Scheduled runs:")
        print("   🌅 Morning: 9:00 AM (job search + applications)")
        print("   🌆 Evening: 6:00 PM (additional search + summary)")
        print("⏹️  Press Ctrl+C to stop")
        print("="*60)
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            self.logger.info("👋 Job Search Bot stopped by user")
            print(f"\\n👋 Good luck with your job search, {self.profile['name']}!")
            print("📧 Check your email for today's summary report")
    
    def run_test_mode(self):
        """Run bot in test mode (no actual applications/emails)"""
        self.test_mode = True
        self.print_banner()
        print("\\n🧪 RUNNING IN TEST MODE - No actual applications or emails will be sent")
        print("="*60)
        
        return self.run_once()

def main():
    """Main entry point with command line arguments"""
    parser = argparse.ArgumentParser(description="Manikanta's AI-Powered Job Search Bot")
    parser.add_argument('--once', action='store_true', help='Run once for testing')
    parser.add_argument('--test', action='store_true', help='Run in test mode (no actual applications)')
    parser.add_argument('--weekly', action='store_true', help='Generate weekly report only')
    parser.add_argument('--config', default='config.json', help='Config file path')
    
    args = parser.parse_args()
    
    print("🤖 Manikanta's AI-Powered Job Search Bot")
    print("Targeting QA Engineer & Automation Testing Roles")
    print("="*50)
    
    try:
        if args.weekly:
            # Generate weekly report only
            bot = ManiJobSearchBot(args.config)
            bot.generate_weekly_report()
            return
        
        if args.test:
            # Test mode
            bot = ManiJobSearchBot(args.config, test_mode=True)
            success = bot.run_test_mode()
            print(f"\\n{'✅ Test completed successfully' if success else '❌ Test encountered errors'}")
        
        elif args.once:
            # Run once for testing
            bot = ManiJobSearchBot(args.config)
            success = bot.run_once()
            print(f"\\n{'✅ Bot completed successfully' if success else '❌ Bot encountered errors'}")
            print("\\n📋 Check the reports/ directory for detailed HTML reports")
            print("📊 Check the data/ directory for raw data files")
        
        else:
            # Run with scheduling
            bot = ManiJobSearchBot(args.config)
            bot.run_scheduled()
    
    except KeyboardInterrupt:
        print("\\n👋 Bot stopped by user. Have a great day!")
    except Exception as e:
        print(f"\\n❌ Critical error: {e}")
        print("Check the logs/ directory for detailed error information")

if __name__ == "__main__":
    main()