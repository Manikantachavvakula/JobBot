import smtplib
import json
import time
import random
import re
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.mime.application import MIMEApplication
from typing import List, Dict, Any
import logging
from bs4 import BeautifulSoup
import os
from datetime import datetime

class EmailManager:
    def __init__(self, config_path: str = "config.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.setup_logging()
        self.email_count = 0
        self.daily_limit = self.config['daily_limits']['max_hr_emails']
        
        # Manikanta's profile for personalization
        self.profile = self.config['profile']
        self.skills_summary = self.create_skills_summary()
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('email_manager.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def create_skills_summary(self) -> str:
        """Create a concise skills summary for emails"""
        skills = self.config['skills']
        summary_parts = []
        
        if skills.get('languages'):
            summary_parts.append(f"Programming: {', '.join(skills['languages'])}")
        
        if skills.get('testing_tools'):
            summary_parts.append(f"Testing Tools: {', '.join(skills['testing_tools'][:3])}")  # Top 3
        
        if skills.get('concepts'):
            summary_parts.append(f"Specializations: {', '.join(skills['concepts'][:2])}")  # Top 2
        
        return " | ".join(summary_parts)
    
    def setup_smtp_connection(self):
        """Setup SMTP connection for sending emails"""
        try:
            smtp_server = smtplib.SMTP(
                self.config['email_config']['smtp_server'],
                self.config['email_config']['smtp_port']
            )
            smtp_server.starttls()
            smtp_server.login(
                self.config['email_config']['sender_email'],
                self.config['email_config']['sender_password']
            )
            return smtp_server
        except Exception as e:
            self.logger.error(f"Failed to setup SMTP connection: {e}")
            return None
    
    def create_job_application_email(self, job_data: Dict, resume_path: str = None) -> MIMEMultipart:
        """Create formal job application email for Manikanta"""
        msg = MIMEMultipart()
        
        company = job_data.get('company', 'your esteemed organization')
        title = job_data.get('title', 'QA Engineer')
        
        # Email headers
        msg['From'] = self.config['email_config']['sender_email']
        msg['To'] = job_data.get('hr_email', '')
        msg['Subject'] = f"Application for {title} Role - {self.profile['name']}"
        
        # Enhanced email body templates
        body_templates = [
            f"""Dear Hiring Manager,

I hope this email finds you well. I am writing to express my strong interest in the {title} position at {company}.

With over a year of experience as a ROC Specialist at Amazon Development Centre and a solid foundation in automation testing, I bring a unique blend of operational excellence and technical expertise to quality assurance.

**My Key Qualifications:**
• **Automation Testing**: Proficient in Selenium WebDriver, PyTest, and API testing using Postman
• **Programming**: Strong Python and SQL skills with hands-on project experience
• **Process Excellence**: Proven track record at Amazon resolving 100+ escalations monthly within strict SLAs
• **Framework Development**: Created QA-Monkey automation framework achieving 92% regression testing success
• **Stakeholder Management**: Experience mentoring teams and streamlining workflows

**Educational Background:**
B.Tech in Computer Science and Engineering from Chaitanya Engineering College (JNTUK)

**Notable Projects:**
- QA-Monkey: Python-Selenium testing framework with POM design and multi-format reporting
- NetWrecker v2.0: Performance testing utility for DoS simulation and server analysis
- RecruitIntel: AI-powered Chrome extension for preventing job scams

**Certifications:** CS50 SQL (Harvard), Software Testing (Udemy), Python by Google (Coursera)

I am particularly excited about {company} and would welcome the opportunity to contribute to your quality assurance initiatives. My combination of technical skills and operational experience from Amazon would enable me to make meaningful contributions from day one.

Please find my resume attached for your review. I would be grateful for the opportunity to discuss how my background aligns with your requirements.

Thank you for your time and consideration.

Best regards,
{self.profile['name']}
📧 {self.profile['email']}
📱 {self.profile['phone']}
🔗 LinkedIn: {self.profile.get('linkedin', '')}
💼 Portfolio: {self.profile.get('portfolio', '')}""",

            f"""Hello,

I am reaching out regarding the {title} opportunity at {company}. As a QA professional with automation expertise and Amazon experience, I am excited about the possibility of contributing to your team.

**My Background:**
Currently transitioning from operations to full-time testing, I bring:
• Amazon ROC Specialist experience with process optimization
• Hands-on automation testing with Python, Selenium, and PyTest
• Strong foundation in API testing and test case design
• Published work on testing frameworks (QA-Monkey article on Medium)

**Technical Skills:** {self.skills_summary}

**Why I'm Interested:**
{company} stands out for its commitment to quality and innovation. I believe my blend of operational excellence and technical testing skills would be valuable for your QA initiatives.

**Recent Achievements:**
- Best Performer recognition (3x) at Amazon for consistent accuracy
- Runner-up at Smart India Hackathon
- Published testing framework achieving 92% regression success rate

I would love to discuss how my background can contribute to {company}'s success. My resume is attached for your review.

Looking forward to hearing from you.

Warm regards,
{self.profile['name']}
{self.profile['phone']} | {self.profile['email']}""",

            f"""Dear {company} Hiring Team,

I hope you're doing well. I'm writing to apply for the {title} position and share why I believe I'd be a great fit for your team.

**About Me:**
I'm {self.profile['name']}, a dedicated QA professional with a unique journey from Amazon operations to automation testing. My experience includes:

✅ **Operations Excellence**: 1+ years at Amazon resolving complex escalations and optimizing processes
✅ **Automation Testing**: Proficient in Selenium, PyTest, Python, and API testing
✅ **Innovation**: Developed QA-Monkey framework and contributed to AI-powered testing solutions
✅ **Continuous Learning**: Active in tech community with published articles and certifications

**What I Bring:**
• Strong analytical mindset honed through Amazon's high-pressure environment
• Hands-on automation experience with modern testing tools
• Proven ability to work with diverse stakeholders and cross-functional teams
• Passion for quality and delivering reliable software solutions

**Education & Credentials:**
B.Tech Computer Science | Harvard CS50 SQL | Google Python Certification

I'm genuinely excited about {company} and the opportunity to contribute to your quality assurance efforts. I'd welcome the chance to discuss how my background and enthusiasm align with your needs.

Resume attached for your consideration.

Best,
{self.profile['name']}
📞 {self.profile['phone']}
💼 Available for immediate joining with 1-month notice period"""
        ]
        
        body = random.choice(body_templates)
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach resume if provided
        if resume_path and os.path.exists(resume_path):
            try:
                with open(resume_path, 'rb') as attachment:
                    part = MIMEApplication(attachment.read(), _subtype='pdf')
                    part.add_header('Content-Disposition', f'attachment; filename={self.profile["name"]}_Resume.pdf')
                    msg.attach(part)
                self.logger.info(f"Resume attached: {resume_path}")
            except Exception as e:
                self.logger.error(f"Failed to attach resume: {e}")
        
        return msg
    
    def create_networking_email(self, contact_data: Dict) -> MIMEMultipart:
        """Create networking/HR outreach email"""
        msg = MIMEMultipart()
        
        contact_name = contact_data.get('name', 'there')
        company = contact_data.get('company', 'your organization')
        
        msg['From'] = self.config['email_config']['sender_email']
        msg['To'] = contact_data.get('email', '')
        msg['Subject'] = f"QA/Automation Testing Opportunity Inquiry - {self.profile['name']}"
        
        # Networking email templates
        templates = [
            f"""Hi {contact_name},

I hope this message finds you well. I came across your profile and noticed that {company} has opportunities in QA/Testing.

I'm {self.profile['name']}, currently seeking QA Automation roles after gaining valuable experience at Amazon. I'd love to explore potential opportunities with your team.

**My Background:**
• Amazon ROC Specialist with 1+ years of operational excellence
• Automation testing expertise: Python, Selenium WebDriver, PyTest
• API testing proficiency with Postman and REST services
• Framework development experience (QA-Monkey testing framework)
• Strong foundation in both manual and automated testing approaches

**Recent Highlights:**
- 3x Best Performer at Amazon for process optimization
- Published article on automation testing frameworks
- B.Tech Computer Science with relevant certifications

I've attached my resume for your reference. Would appreciate any guidance on current QA openings or the application process at {company}.

Thank you for your time!

Best regards,
{self.profile['name']}
{self.profile['phone']} | {self.profile['email']}
LinkedIn: {self.profile.get('linkedin', '')}""",

            f"""Hello {contact_name},

I hope you're having a great day! I'm reaching out because I'm very interested in QA/Testing opportunities at {company}.

**Quick Introduction:**
I'm {self.profile['name']}, a QA Engineer with Amazon experience, specializing in automation testing. My journey includes:

🔧 **Technical Skills**: Python, Selenium, PyTest, API Testing, SQL
🏢 **Experience**: Amazon operations + automation testing projects  
🎯 **Focus**: Quality assurance, test automation, and process improvement
📚 **Learning**: Harvard CS50, Google certifications, continuous skill development

**Why {company}?**
Your company's reputation for innovation and quality aligns perfectly with my career goals in QA automation.

**What I'm Looking For:**
Entry to mid-level QA/SDET positions where I can contribute my Amazon operational experience and growing automation expertise.

I'd be grateful if you could share my profile with the relevant hiring team or provide guidance on how to apply for suitable positions.

My resume is attached for your review.

Thanks in advance for your help!

Regards,
{self.profile['name']}
📧 {self.profile['email']}""",

            f"""Dear {contact_name},

I hope this email finds you well. I'm writing to inquire about QA Engineer opportunities at {company}.

**A bit about me:**
I bring a unique combination of Amazon operational excellence and hands-on testing expertise. My background includes:

• **Operations Excellence**: Proven track record at Amazon Development Centre
• **Automation Testing**: Practical experience with Selenium, Python, and testing frameworks
• **Problem Solving**: Strong analytical skills developed through complex escalation resolution
• **Innovation**: Developed testing utilities and contributed to AI-powered solutions

**Technical Expertise:**
{self.skills_summary}

**Career Objective:**
I'm passionate about ensuring software quality and am actively seeking opportunities to apply my skills in a dedicated QA role.

**Availability:** Immediate joining with standard notice period

Would love to connect and discuss how I can contribute to {company}'s quality assurance initiatives.

Resume attached for your kind consideration.

Looking forward to hearing from you.

Best regards,
{self.profile['name']}
Email: {self.profile['email']}
Phone: {self.profile['phone']}
Location: {self.profile['location']}"""
        ]
        
        body = random.choice(templates)
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach general resume for networking
        resume_path = f"./resumes/{self.config['resume_files']['qa_general']}"
        if os.path.exists(resume_path):
            try:
                with open(resume_path, 'rb') as attachment:
                    part = MIMEApplication(attachment.read(), _subtype='pdf')
                    part.add_header('Content-Disposition', f'attachment; filename={self.profile["name"]}_QA_Resume.pdf')
                    msg.attach(part)
            except Exception as e:
                self.logger.error(f"Failed to attach resume for networking: {e}")
        
        return msg
    
    def extract_hr_contacts(self, job_data: Dict) -> List[Dict]:
        """Extract HR contacts from job postings or generate likely contacts"""
        contacts = []
        
        try:
            company = job_data.get('company', '')
            if not company:
                return contacts
            
            # Clean company name for domain generation
            clean_company = self.clean_company_name(company)
            
            # Generate possible company domains
            possible_domains = self.generate_company_domains(clean_company)
            
            # Create HR email patterns
            for domain in possible_domains:
                hr_patterns = [
                    f"hr@{domain}",
                    f"careers@{domain}",
                    f"jobs@{domain}",
                    f"recruitment@{domain}",
                    f"hiring@{domain}",
                    f"talent@{domain}"
                ]
                
                for email in hr_patterns:
                    contacts.append({
                        'email': email,
                        'name': 'HR Team',
                        'company': company,
                        'source': 'domain_pattern',
                        'job_title': job_data.get('title', ''),
                        'confidence': 'medium'
                    })
            
            # Extract emails from job description
            description = job_data.get('description', '')
            extracted_emails = self.extract_emails_from_text(description)
            
            for email in extracted_emails:
                contacts.append({
                    'email': email,
                    'name': 'Contact Person',
                    'company': company,
                    'source': 'job_description',
                    'job_title': job_data.get('title', ''),
                    'confidence': 'high'
                })
            
            # Add location-based HR contacts for major companies
            if any(keyword in company.lower() for keyword in ['tech', 'solutions', 'systems', 'software']):
                location = job_data.get('location', '').lower()
                if 'hyderabad' in location or 'bangalore' in location:
                    contacts.append({
                        'email': f"hr.{location.split()[0]}@{possible_domains[0] if possible_domains else 'company.com'}",
                        'name': f'HR Team - {location.title()}',
                        'company': company,
                        'source': 'location_pattern',
                        'job_title': job_data.get('title', ''),
                        'confidence': 'low'
                    })
        
        except Exception as e:
            self.logger.error(f"Error extracting HR contacts: {e}")
        
        # Remove duplicates and limit to top 3 contacts
        unique_contacts = []
        seen_emails = set()
        
        for contact in contacts:
            email = contact['email']
            if email not in seen_emails and self.is_valid_email(email):
                seen_emails.add(email)
                unique_contacts.append(contact)
                if len(unique_contacts) >= 3:
                    break
        
        return unique_contacts
    
    def clean_company_name(self, company_name: str) -> str:
        """Clean company name for domain generation"""
        # Remove common company suffixes and clean
        suffixes = [
            'pvt ltd', 'private limited', 'ltd', 'limited', 'inc', 'corporation',
            'corp', 'company', 'technologies', 'technology', 'tech', 'solutions',
            'solution', 'systems', 'system', 'services', 'service', 'enterprises',
            'enterprise', 'group', 'pvt', 'llp', 'llc'
        ]
        
        clean_name = company_name.lower()
        
        # Remove suffixes
        for suffix in suffixes:
            clean_name = re.sub(rf'\\b{suffix}\\b', '', clean_name)
        
        # Clean special characters and spaces
        clean_name = re.sub(r'[^a-zA-Z0-9\\s]', '', clean_name)
        clean_name = re.sub(r'\\s+', '', clean_name).strip()
        
        return clean_name
    
    def generate_company_domains(self, clean_company: str) -> List[str]:
        """Generate possible company domains"""
        if not clean_company:
            return []
        
        domains = []
        
        # Basic domain patterns
        domains.extend([
            f"{clean_company}.com",
            f"{clean_company}.in",
            f"{clean_company}.co.in",
            f"{clean_company}.org"
        ])
        
        # Alternative patterns
        if len(clean_company) > 8:
            # Use first part for long names
            short_name = clean_company[:8]
            domains.extend([
                f"{short_name}.com",
                f"{short_name}.in"
            ])
        
        # Add common variations
        variations = [
            clean_company.replace('technologies', 'tech'),
            clean_company.replace('solutions', 'sol'),
            clean_company.replace('systems', 'sys')
        ]
        
        for variation in variations:
            if variation != clean_company:
                domains.extend([
                    f"{variation}.com",
                    f"{variation}.in"
                ])
        
        return domains[:5]  # Limit to top 5
    
    def extract_emails_from_text(self, text: str) -> List[str]:
        """Extract email addresses from text"""
        email_pattern = r'\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b'
        found_emails = re.findall(email_pattern, text)
        
        # Filter out generic/noreply emails
        filtered_emails = []
        avoid_patterns = ['noreply', 'no-reply', 'donotreply', 'admin', 'support']
        
        for email in found_emails:
            email_lower = email.lower()
            if not any(pattern in email_lower for pattern in avoid_patterns):
                filtered_emails.append(email)
        
        return filtered_emails
    
    def is_valid_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}$'
        return bool(re.match(pattern, email))
    
    def send_email(self, msg: MIMEMultipart, recipient_email: str) -> bool:
        """Send email safely with error handling"""
        try:
            smtp_server = self.setup_smtp_connection()
            if not smtp_server:
                return False
            
            smtp_server.send_message(msg)
            smtp_server.quit()
            
            self.logger.info(f"Email sent successfully to {recipient_email}")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to send email to {recipient_email}: {e}")
            return False
    
    def send_job_application_emails(self, jobs_with_contacts: List[Dict]) -> List[Dict]:
        """Send job application emails to HR contacts"""
        email_results = []
        
        for job in jobs_with_contacts:
            if self.email_count >= self.daily_limit:
                self.logger.info(f"Daily email limit ({self.daily_limit}) reached")
                break
            
            contacts = self.extract_hr_contacts(job)
            
            if not contacts:
                self.logger.info(f"No HR contacts found for {job.get('company', 'Unknown')} - {job.get('title', 'Unknown')}")
                continue
            
            # Send to top 2 contacts per job
            for contact in contacts[:2]:
                if self.email_count >= self.daily_limit:
                    break
                
                try:
                    # Create appropriate email based on contact source
                    if contact['source'] == 'job_description':
                        # High confidence contact - formal application
                        msg = self.create_job_application_email(job)
                        msg['To'] = contact['email']
                        email_type = 'formal_application'
                    else:
                        # Generated contact - networking approach
                        msg = self.create_networking_email(contact)
                        email_type = 'networking'
                    
                    # For safety in testing, simulate sending
                    success = True  # Set to False to actually send: self.send_email(msg, contact['email'])
                    
                    if success:
                        self.logger.info(f"✅ Email sent (simulated) to {contact['email']} for {job['title']} at {job['company']}")
                    else:
                        self.logger.warning(f"❌ Failed to send email to {contact['email']}")
                    
                    result = {
                        'job_title': job.get('title', ''),
                        'company': job.get('company', ''),
                        'recipient_email': contact['email'],
                        'recipient_name': contact.get('name', ''),
                        'email_type': email_type,
                        'contact_source': contact['source'],
                        'confidence': contact['confidence'],
                        'success': success,
                        'sent_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    email_results.append(result)
                    
                    if success:
                        self.email_count += 1
                    
                    # Delay between emails (30-120 seconds)
                    delay = random.uniform(
                        self.config['daily_limits']['email_delay_min'],
                        self.config['daily_limits']['email_delay_max']
                    )
                    
                    self.logger.info(f"Waiting {delay:.1f} seconds before next email...")
                    time.sleep(delay)
                
                except Exception as e:
                    self.logger.error(f"Error sending email for {job['title']}: {e}")
        
        return email_results
    
    def send_daily_summary_email(self, application_summary: Dict, email_summary: List[Dict]) -> bool:
        """Send daily summary email to Manikanta"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config['email_config']['sender_email']
            msg['To'] = self.profile['email']
            msg['Subject'] = f"🤖 Daily Job Bot Summary - {datetime.now().strftime('%B %d, %Y')}"
            
            # Create comprehensive summary body
            successful_emails = len([e for e in email_summary if e.get('success', False)])
            failed_emails = len([e for e in email_summary if not e.get('success', False)])
            
            body = f"""🤖 **Job Search Bot Daily Summary**

Date: {datetime.now().strftime('%A, %B %d, %Y')}
Generated at: {datetime.now().strftime('%I:%M %p')}

📊 **PERFORMANCE OVERVIEW**
════════════════════════════════

📝 **Job Applications:**
   ✅ Successful Applications: {application_summary.get('successful', 0)}
   ❌ Failed Applications: {application_summary.get('failed', 0)}
   🔗 External Applications: {application_summary.get('external', 0)}
   🔐 Login Required: {application_summary.get('login_required', 0)}
   📊 Total Attempted: {application_summary.get('total_attempted', 0)}

📧 **HR Outreach:**
   ✅ Emails Sent: {successful_emails}
   ❌ Failed Emails: {failed_emails}
   📊 Total Attempted: {len(email_summary)}

💼 **SUCCESSFUL APPLICATIONS TODAY**
════════════════════════════════════
"""
            
            # Add successful applications
            successful_apps = [app for app in application_summary.get('details', []) if app['status'] == 'success']
            
            if successful_apps:
                for i, app in enumerate(successful_apps, 1):
                    body += f"""
{i}. **{app['title']}** at **{app['company']}**
   📄 Resume Used: {app.get('filter_result', {}).get('resume_to_use', 'N/A')}
   ⭐ Relevance Score: {app.get('filter_result', {}).get('relevance_score', 0)}%
   🕒 Applied At: {app.get('applied_at', 'N/A')}
"""
            else:
                body += "\\n   No successful applications today. Keep trying! 💪"
            
            body += f"""

📧 **HR OUTREACH SUMMARY**
═══════════════════════════
"""
            
            # Add email outreach summary
            if email_summary:
                companies_contacted = set()
                for email in email_summary:
                    if email.get('success', False):
                        companies_contacted.add(email.get('company', 'Unknown'))
                
                body += f"\\n   Companies Contacted: {len(companies_contacted)}"
                body += f"\\n   **Companies:** {', '.join(list(companies_contacted)[:5])}"
                
                if len(companies_contacted) > 5:
                    body += f" and {len(companies_contacted) - 5} more..."
            else:
                body += "\\n   No HR outreach emails sent today."
            
            body += f"""

📈 **NEXT STEPS & RECOMMENDATIONS**
════════════════════════════════════

🎯 **Immediate Actions:**
   • Check email for responses to applications
   • Follow up on external applications that require manual completion
   • Update LinkedIn profile if needed
   • Review and customize resume based on today's applications

📊 **Performance Insights:**
   • Success Rate: {(application_summary.get('successful', 0) / max(application_summary.get('total_attempted', 1), 1) * 100):.1f}%
   • Email Delivery Rate: {(successful_emails / max(len(email_summary), 1) * 100):.1f}%

🚀 **Tomorrow's Plan:**
   • Continue morning and evening job search routine
   • Target {self.daily_limit - application_summary.get('total_attempted', 0)} more applications
   • Focus on companies that haven't been contacted yet

💡 **Tips:**
   • Best response rates typically come 2-3 days after application
   • Consider following up on high-interest positions after 1 week
   • Keep tracking responses to optimize future applications

════════════════════════════════════

🤖 **Bot Status:** Running smoothly ✅
⏰ **Next Scheduled Run:** Tomorrow 9:00 AM

**Contact:** {self.profile['phone']} | {self.profile['email']}
**Generated by:** AI Job Search Bot v1.0

Good luck with your job search, {self.profile['name']}! 🍀
"""
            
            msg.attach(MIMEText(body, 'plain'))
            
            # For safety, simulate sending
            success = True  # Set to: self.send_email(msg, self.profile['email'])
            
            if success:
                self.logger.info("✅ Daily summary email prepared successfully (simulated)")
            else:
                self.logger.error("❌ Failed to send daily summary email")
            
            return success
        
        except Exception as e:
            self.logger.error(f"Error creating daily summary email: {e}")
            return False

# Example usage and testing
if __name__ == "__main__":
    emailer = EmailManager()
    
    print("=== Testing Email Manager ===")
    
    # Test job data
    test_jobs = [
        {
            'title': 'QA Automation Engineer',
            'company': 'TechSolutions Pvt Ltd',
            'location': 'Hyderabad',
            'description': 'Looking for QA engineer with automation skills. Contact: careers@techsolutions.com for more details.',
            'url': 'https://example.com/job1',
            'source': 'LinkedIn'
        },
        {
            'title': 'Software Tester',
            'company': 'Innovation Systems',
            'location': 'Bangalore',
            'description': 'Manual and automation testing role. Python and Selenium knowledge preferred.',
            'url': 'https://example.com/job2',
            'source': 'Naukri'
        }
    ]
    
    print("\\n1. Testing HR Contact Extraction...")
    for job in test_jobs:
        contacts = emailer.extract_hr_contacts(job)
        print(f"\\nJob: {job['title']} at {job['company']}")
        print(f"Extracted {len(contacts)} contacts:")
        for contact in contacts:
            print(f"  - {contact['email']} ({contact['source']}, {contact['confidence']} confidence)")
    
    print("\\n2. Testing Email Generation...")
    test_contact = {
        'email': 'hr@techsolutions.com',
        'name': 'HR Team',
        'company': 'TechSolutions',
        'source': 'domain_pattern'
    }
    
    # Test application email
    app_email = emailer.create_job_application_email(test_jobs[0])
    print(f"Application email subject: {app_email['Subject']}")
    
    # Test networking email  
    net_email = emailer.create_networking_email(test_contact)
    print(f"Networking email subject: {net_email['Subject']}")
    
    print("\\n3. Testing Email Sending (Simulated)...")
    email_results = emailer.send_job_application_emails(test_jobs)
    print(f"Email results: {len(email_results)} emails processed")
    
    for result in email_results:
        print(f"  - {result['recipient_email']}: {result['success']} ({result['email_type']})")
    
    print("\\n4. Testing Daily Summary...")
    test_app_summary = {
        'total_attempted': 5,
        'successful': 3,
        'failed': 1,
        'external': 1,
        'details': [
            {'title': 'QA Engineer', 'company': 'Test Corp', 'status': 'success', 'applied_at': '2024-01-01 10:00:00'}
        ]
    }
    
    summary_sent = emailer.send_daily_summary_email(test_app_summary, email_results)
    print(f"Daily summary status: {'✅ Success' if summary_sent else '❌ Failed'}")
    
    print("\\n=== Email Manager Test Complete ===")
    print("Check email_manager.log for detailed logs")
    print("\\n📧 To enable actual email sending:")
    print("1. Set up Gmail app password in config.json")
    print("2. Change 'success = True' to 'success = self.send_email(...)' in the code")
    print("3. Test with a small number of emails first")