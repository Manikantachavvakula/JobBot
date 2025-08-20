import json
import csv
import os
import time
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging
from pathlib import Path

class JobReporter:
    def __init__(self, config_path: str = "config.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.setup_logging()
        self.reports_dir = "reports"
        self.data_dir = "data"
        self.ensure_directories()
        
        # Manikanta's profile for report personalization
        self.profile = self.config['profile']
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('job_reporter.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def ensure_directories(self):
        """Create necessary directories"""
        for directory in [self.reports_dir, self.data_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
                self.logger.info(f"Created directory: {directory}")
    
    def save_scraped_jobs(self, jobs: List[Dict], filename: str = None) -> str:
        """Save scraped jobs to JSON and CSV"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if not filename:
                filename = f"scraped_jobs_{timestamp}"
            
            # Save as JSON (detailed data)
            json_path = os.path.join(self.data_dir, f"{filename}.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(jobs, f, indent=2, ensure_ascii=False)
            
            # Save as CSV (for easy analysis)
            csv_path = os.path.join(self.data_dir, f"{filename}.csv")
            if jobs:
                # Flatten job data for CSV
                csv_data = []
                for job in jobs:
                    csv_row = {
                        'title': job.get('title', ''),
                        'company': job.get('company', ''),
                        'location': job.get('location', ''),
                        'salary': job.get('salary', ''),
                        'experience': job.get('experience', ''),
                        'description_snippet': job.get('description', '')[:200] + '...' if job.get('description', '') else '',
                        'url': job.get('url', ''),
                        'source': job.get('source', ''),
                        'posted_date': job.get('posted_date', ''),
                        'scraped_at': job.get('scraped_at', ''),
                        'search_keywords': job.get('search_keywords', '')
                    }
                    csv_data.append(csv_row)
                
                df = pd.DataFrame(csv_data)
                df.to_csv(csv_path, index=False, encoding='utf-8')
            
            self.logger.info(f"Saved {len(jobs)} jobs to {json_path} and {csv_path}")
            return json_path
        
        except Exception as e:
            self.logger.error(f"Error saving scraped jobs: {e}")
            return None
    
    def save_application_results(self, results: List[Dict], filename: str = None) -> str:
        """Save job application results"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if not filename:
                filename = f"application_results_{timestamp}"
            
            # Save as JSON
            json_path = os.path.join(self.data_dir, f"{filename}.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            # Save as CSV
            csv_path = os.path.join(self.data_dir, f"{filename}.csv")
            if results:
                # Flatten the data for CSV
                flattened_results = []
                for result in results:
                    filter_result = result.get('filter_result', {})
                    flat_result = {
                        'job_id': result.get('job_id', ''),
                        'title': result.get('title', ''),
                        'company': result.get('company', ''),
                        'status': result.get('status', ''),
                        'reason': result.get('reason', ''),
                        'applied_at': result.get('applied_at', ''),
                        'steps_completed': result.get('steps_completed', 0),
                        'resume_used': filter_result.get('resume_to_use', ''),
                        'relevance_score': filter_result.get('relevance_score', 0),
                        'salary_lpa': filter_result.get('salary_lpa', ''),
                        'is_fresher_friendly': filter_result.get('is_fresher_friendly', False),
                        'matched_keywords': ', '.join(filter_result.get('matched_keywords', [])),
                        'search_keywords': result.get('search_keywords', '')
                    }
                    flattened_results.append(flat_result)
                
                df = pd.DataFrame(flattened_results)
                df.to_csv(csv_path, index=False, encoding='utf-8')
            
            self.logger.info(f"Saved {len(results)} application results to {json_path} and {csv_path}")
            return json_path
        
        except Exception as e:
            self.logger.error(f"Error saving application results: {e}")
            return None
    
    def save_email_results(self, results: List[Dict], filename: str = None) -> str:
        """Save email outreach results"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if not filename:
                filename = f"email_results_{timestamp}"
            
            # Save as JSON
            json_path = os.path.join(self.data_dir, f"{filename}.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            # Save as CSV
            csv_path = os.path.join(self.data_dir, f"{filename}.csv")
            if results:
                df = pd.DataFrame(results)
                df.to_csv(csv_path, index=False, encoding='utf-8')
            
            self.logger.info(f"Saved {len(results)} email results to {json_path} and {csv_path}")
            return json_path
        
        except Exception as e:
            self.logger.error(f"Error saving email results: {e}")
            return None
    
    def generate_daily_report(self, application_summary: Dict, email_results: List[Dict], 
                             scraped_jobs: List[Dict]) -> str:
        """Generate comprehensive daily HTML report"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d')
            report_filename = f"daily_report_{timestamp}.html"
            report_path = os.path.join(self.reports_dir, report_filename)
            
            # Generate HTML report
            html_content = self._generate_html_report(application_summary, email_results, scraped_jobs)
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.logger.info(f"Generated daily report: {report_path}")
            return report_path
        
        except Exception as e:
            self.logger.error(f"Error generating daily report: {e}")
            return None
    
    def _generate_html_report(self, application_summary: Dict, email_results: List[Dict], 
                             scraped_jobs: List[Dict]) -> str:
        """Generate comprehensive HTML report content"""
        date_str = datetime.now().strftime('%B %d, %Y')
        day_name = datetime.now().strftime('%A')
        
        # Calculate statistics
        total_scraped = len(scraped_jobs)
        total_applications = application_summary.get('total_attempted', 0)
        successful_applications = application_summary.get('successful', 0)
        successful_emails = len([e for e in email_results if e.get('success', False)])
        total_emails = len(email_results)
        
        success_rate = (successful_applications / max(total_applications, 1)) * 100
        email_rate = (successful_emails / max(total_emails, 1)) * 100
        
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Job Search Bot Report - {date_str}</title>
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                    margin: 20px; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                }}
                .container {{ 
                    max-width: 1200px; 
                    margin: 0 auto; 
                    background: white; 
                    padding: 30px; 
                    border-radius: 15px; 
                    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                }}
                .header {{ 
                    text-align: center; 
                    color: #2c3e50; 
                    border-bottom: 3px solid #3498db; 
                    padding-bottom: 20px; 
                    margin-bottom: 30px;
                }}
                .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
                .header h2 {{ color: #7f8c8d; font-weight: 300; }}
                .profile-info {{ 
                    background: #ecf0f1; 
                    padding: 15px; 
                    border-radius: 10px; 
                    margin-bottom: 30px; 
                    text-align: center;
                }}
                .summary-cards {{ 
                    display: grid; 
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                    gap: 20px; 
                    margin: 30px 0; 
                }}
                .card {{ 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; 
                    padding: 25px; 
                    border-radius: 15px; 
                    text-align: center; 
                    box-shadow: 0 10px 20px rgba(0,0,0,0.1);
                    transition: transform 0.3s ease;
                }}
                .card:hover {{ transform: translateY(-5px); }}
                .card h3 {{ margin-bottom: 10px; font-size: 1.1em; opacity: 0.9; }}
                .card .number {{ font-size: 2.5em; font-weight: bold; margin-bottom: 5px; }}
                .card .subtitle {{ font-size: 0.9em; opacity: 0.8; }}
                .success {{ background: linear-gradient(135deg, #56ab2f 0%, #a8e6cf 100%) !important; }}
                .warning {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%) !important; }}
                .info {{ background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%) !important; }}
                .secondary {{ background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%) !important; }}
                
                .section {{ margin: 40px 0; }}
                .section h2 {{ 
                    color: #2c3e50; 
                    border-left: 4px solid #3498db; 
                    padding-left: 15px; 
                    margin-bottom: 20px;
                    font-size: 1.5em;
                }}
                
                table {{ 
                    width: 100%; 
                    border-collapse: collapse; 
                    margin: 20px 0; 
                    background: white;
                    border-radius: 10px;
                    overflow: hidden;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.08);
                }}
                th, td {{ 
                    padding: 15px; 
                    text-align: left; 
                    border-bottom: 1px solid #ecf0f1;
                }}
                th {{ 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; 
                    font-weight: 600;
                    text-transform: uppercase;
                    font-size: 0.9em;
                    letter-spacing: 0.5px;
                }}
                tr:hover {{ background-color: #f8f9fa; }}
                
                .status-success {{ background-color: #d5edda; color: #155724; padding: 8px 12px; border-radius: 20px; font-weight: 600; }}
                .status-failed {{ background-color: #f8d7da; color: #721c24; padding: 8px 12px; border-radius: 20px; font-weight: 600; }}
                .status-external {{ background-color: #fff3cd; color: #856404; padding: 8px 12px; border-radius: 20px; font-weight: 600; }}
                .status-login_required {{ background-color: #cce7ff; color: #004085; padding: 8px 12px; border-radius: 20px; font-weight: 600; }}
                
                .insights {{ 
                    display: grid; 
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
                    gap: 25px; 
                    margin: 30px 0; 
                }}
                .insight-box {{ 
                    background: #f8f9fa; 
                    padding: 25px; 
                    border-radius: 15px; 
                    border-left: 5px solid #3498db;
                }}
                .insight-box h3 {{ color: #2c3e50; margin-bottom: 15px; }}
                .insight-box ul {{ list-style: none; }}
                .insight-box li {{ 
                    padding: 8px 0; 
                    border-bottom: 1px solid #ecf0f1; 
                    display: flex; 
                    justify-content: space-between;
                }}
                .insight-box li:last-child {{ border-bottom: none; }}
                
                .progress-bar {{ 
                    background: #ecf0f1; 
                    border-radius: 10px; 
                    height: 20px; 
                    margin: 10px 0;
                    overflow: hidden;
                }}
                .progress-fill {{ 
                    background: linear-gradient(90deg, #56ab2f 0%, #a8e6cf 100%); 
                    height: 100%; 
                    border-radius: 10px;
                    transition: width 0.3s ease;
                }}
                
                .footer {{ 
                    text-align: center; 
                    margin-top: 50px; 
                    padding: 30px; 
                    background: #2c3e50; 
                    color: white; 
                    border-radius: 15px;
                }}
                .footer h3 {{ margin-bottom: 15px; }}
                .footer p {{ margin: 5px 0; opacity: 0.8; }}
                
                .emoji {{ font-size: 1.2em; margin-right: 8px; }}
                .highlight {{ background: #fff3cd; padding: 2px 6px; border-radius: 4px; }}
                
                @media (max-width: 768px) {{
                    .container {{ margin: 10px; padding: 20px; }}
                    .summary-cards {{ grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); }}
                    .card .number {{ font-size: 2em; }}
                    table {{ font-size: 0.9em; }}
                    th, td {{ padding: 10px; }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🤖 AI Job Search Bot Report</h1>
                    <h2>{day_name}, {date_str}</h2>
                </div>
                
                <div class="profile-info">
                    <h3>👨‍💻 {self.profile['name']} - QA Automation Engineer</h3>
                    <p>📧 {self.profile['email']} | 📱 {self.profile['phone']} | 📍 {self.profile['location']}</p>
                    <p>🎯 Target: QA/Automation Testing Roles | 💰 Salary: ₹{self.config['job_preferences']['min_salary_lpa']}+ LPA</p>
                </div>
                
                <div class="summary-cards">
                    <div class="card info">
                        <h3>Jobs Scraped</h3>
                        <div class="number">{total_scraped}</div>
                        <div class="subtitle">From multiple sources</div>
                    </div>
                    <div class="card success">
                        <h3>Applications</h3>
                        <div class="number">{successful_applications}</div>
                        <div class="subtitle">Successfully Applied</div>
                    </div>
                    <div class="card warning">
                        <h3>HR Emails</h3>
                        <div class="number">{successful_emails}</div>
                        <div class="subtitle">Outreach Sent</div>
                    </div>
                    <div class="card secondary">
                        <h3>Success Rate</h3>
                        <div class="number">{success_rate:.1f}%</div>
                        <div class="subtitle">Application Success</div>
                    </div>
                </div>
                
                <div class="insights">
                    <div class="insight-box">
                        <h3>📊 Today's Performance</h3>
                        <ul>
                            <li><span>Total Applications</span><span class="highlight">{total_applications}</span></li>
                            <li><span>Success Rate</span><span class="highlight">{success_rate:.1f}%</span></li>
                            <li><span>Email Delivery</span><span class="highlight">{email_rate:.1f}%</span></li>
                            <li><span>Sources Used</span><span class="highlight">{len(set(job.get('source', '') for job in scraped_jobs))}</span></li>
                        </ul>
                    </div>
                    
                    <div class="insight-box">
                        <h3>🎯 Job Sources Breakdown</h3>
                        <ul>
        """
        
        # Add source breakdown
        source_counts = {}
        for job in scraped_jobs:
            source = job.get('source', 'Unknown')
            source_counts[source] = source_counts.get(source, 0) + 1
        
        for source, count in source_counts.items():
            percentage = (count / max(total_scraped, 1)) * 100
            html += f'<li><span>{source}</span><span class="highlight">{count} ({percentage:.1f}%)</span></li>'
        
        html += """
                        </ul>
                    </div>
                </div>
        """
        
        # Application Details Table
        if application_summary.get('details'):
            html += """
                <div class="section">
                    <h2>📝 Application Details</h2>
                    <table>
                        <tr>
                            <th>Job Title</th>
                            <th>Company</th>
                            <th>Status</th>
                            <th>Resume Used</th>
                            <th>Score</th>
                            <th>Applied At</th>
                        </tr>
            """
            
            for app in application_summary['details']:
                status_class = f"status-{app.get('status', 'unknown')}"
                filter_result = app.get('filter_result', {})
                resume_used = filter_result.get('resume_to_use', 'N/A').replace('.pdf', '')
                score = filter_result.get('relevance_score', 0)
                
                html += f"""
                        <tr>
                            <td><strong>{app.get('title', 'N/A')}</strong></td>
                            <td>{app.get('company', 'N/A')}</td>
                            <td><span class="{status_class}">{app.get('status', 'N/A').replace('_', ' ').title()}</span></td>
                            <td>{resume_used}</td>
                            <td>{score}%</td>
                            <td>{app.get('applied_at', 'N/A')}</td>
                        </tr>
                """
            
            html += "</table></div>"
        
        # Email Outreach Table
        if email_results:
            html += """
                <div class="section">
                    <h2>📧 HR Outreach Results</h2>
                    <table>
                        <tr>
                            <th>Company</th>
                            <th>Contact Email</th>
                            <th>Email Type</th>
                            <th>Source</th>
                            <th>Status</th>
                            <th>Sent At</th>
                        </tr>
            """
            
            for email in email_results:
                status = "✅ Sent" if email.get('success', False) else "❌ Failed"
                email_type = email.get('email_type', 'N/A').replace('_', ' ').title()
                
                html += f"""
                        <tr>
                            <td><strong>{email.get('company', 'N/A')}</strong></td>
                            <td>{email.get('recipient_email', 'N/A')}</td>
                            <td>{email_type}</td>
                            <td>{email.get('contact_source', 'N/A')}</td>
                            <td>{status}</td>
                            <td>{email.get('sent_at', 'N/A')}</td>
                        </tr>
                """
            
            html += "</table></div>"
        
        # Progress towards goals
        daily_app_goal = self.config['daily_limits']['max_applications']
        daily_email_goal = self.config['daily_limits']['max_hr_emails']
        
        app_progress = min((total_applications / daily_app_goal) * 100, 100)
        email_progress = min((total_emails / daily_email_goal) * 100, 100)
        
        html += f"""
                <div class="section">
                    <h2>🎯 Daily Goals Progress</h2>
                    <div class="insights">
                        <div class="insight-box">
                            <h3>📝 Applications Goal</h3>
                            <p>{total_applications} / {daily_app_goal} applications</p>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: {app_progress}%"></div>
                            </div>
                            <p><strong>{app_progress:.1f}% Complete</strong></p>
                        </div>
                        
                        <div class="insight-box">
                            <h3>📧 Email Outreach Goal</h3>
                            <p>{total_emails} / {daily_email_goal} emails sent</p>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: {email_progress}%"></div>
                            </div>
                            <p><strong>{email_progress:.1f}% Complete</strong></p>
                        </div>
                    </div>
                </div>
                
                <div class="section">
                    <h2>💡 Insights & Recommendations</h2>
                    <div class="insights">
                        <div class="insight-box">
                            <h3>🔍 Job Market Analysis</h3>
                            <ul>
        """
        
        # Add intelligent insights
        if total_scraped > 0:
            relevant_rate = (len([app for app in application_summary.get('details', []) if app.get('filter_result', {}).get('is_relevant', False)]) / total_scraped) * 100
            html += f"<li>Job Relevance Rate: <strong>{relevant_rate:.1f}%</strong></li>"
        
        if successful_applications > 0:
            avg_score = sum([app.get('filter_result', {}).get('relevance_score', 0) for app in application_summary.get('details', []) if app.get('status') == 'success']) / successful_applications
            html += f"<li>Avg. Success Score: <strong>{avg_score:.1f}%</strong></li>"
        
        html += f"""
                                <li>Most Active Source: <strong>{max(source_counts.items(), key=lambda x: x[1])[0] if source_counts else 'N/A'}</strong></li>
                                <li>Peak Application Time: <strong>{datetime.now().strftime('%I:%M %p')}</strong></li>
                            </ul>
                        </div>
                        
                        <div class="insight-box">
                            <h3>📈 Next Steps</h3>
                            <ul>
                                <li>✅ Check email responses in 24-48 hours</li>
                                <li>📞 Follow up on high-interest applications</li>
                                <li>📝 Update resume based on feedback</li>
                                <li>🔍 Expand search to new companies</li>
                                <li>💼 Prepare for potential interviews</li>
                            </ul>
                        </div>
                    </div>
                </div>
                
                <div class="footer">
                    <h3>🚀 Keep Going, {self.profile['name']}!</h3>
                    <p>🤖 Generated by AI Job Search Bot | ⏰ Next run: Tomorrow 9:00 AM</p>
                    <p>📊 Total Career Progress: Building towards QA Automation Excellence</p>
                    <p>💪 Remember: Every application is a step closer to your dream job!</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def get_weekly_summary(self) -> Dict:
        """Generate weekly performance summary"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            
            weekly_data = {
                'week_start': start_date.strftime('%Y-%m-%d'),
                'week_end': end_date.strftime('%Y-%m-%d'),
                'total_jobs_scraped': 0,
                'total_applications': 0,
                'successful_applications': 0,
                'total_emails_sent': 0,
                'daily_breakdown': [],
                'top_companies': {},
                'top_sources': {},
                'success_trends': []
            }
            
            # Check each day's files
            for i in range(7):
                check_date = start_date + timedelta(days=i)
                date_str = check_date.strftime('%Y%m%d')
                
                day_data = {
                    'date': check_date.strftime('%Y-%m-%d'),
                    'day_name': check_date.strftime('%A'),
                    'applications': 0,
                    'successful': 0,
                    'emails_sent': 0,
                    'jobs_scraped': 0
                }
                
                # Check data directory for matching files
                for filename in os.listdir(self.data_dir):
                    if date_str in filename and filename.endswith('.json'):
                        try:
                            with open(os.path.join(self.data_dir, filename), 'r') as f:
                                data = json.load(f)
                            
                            if 'application_results' in filename:
                                day_data['applications'] = len(data)
                                day_data['successful'] = len([a for a in data if a.get('status') == 'success'])
                                
                                # Track companies
                                for app in data:
                                    company = app.get('company', 'Unknown')
                                    weekly_data['top_companies'][company] = weekly_data['top_companies'].get(company, 0) + 1
                            
                            elif 'email_results' in filename:
                                day_data['emails_sent'] = len([e for e in data if e.get('success', False)])
                            
                            elif 'scraped_jobs' in filename:
                                day_data['jobs_scraped'] = len(data)
                                
                                # Track sources
                                for job in data:
                                    source = job.get('source', 'Unknown')
                                    weekly_data['top_sources'][source] = weekly_data['top_sources'].get(source, 0) + 1
                        
                        except Exception as e:
                            self.logger.error(f"Error reading {filename}: {e}")
                
                weekly_data['total_applications'] += day_data['applications']
                weekly_data['successful_applications'] += day_data['successful']
                weekly_data['total_emails_sent'] += day_data['emails_sent']
                weekly_data['total_jobs_scraped'] += day_data['jobs_scraped']
                weekly_data['daily_breakdown'].append(day_data)
            
            # Calculate success rate trend
            for day in weekly_data['daily_breakdown']:
                success_rate = (day['successful'] / max(day['applications'], 1)) * 100
                weekly_data['success_trends'].append({
                    'date': day['date'],
                    'success_rate': round(success_rate, 2)
                })
            
            return weekly_data
        
        except Exception as e:
            self.logger.error(f"Error generating weekly summary: {e}")
            return {}
    
    def generate_weekly_report(self) -> str:
        """Generate weekly HTML report"""
        try:
            weekly_data = self.get_weekly_summary()
            if not weekly_data:
                return None
            
            timestamp = datetime.now().strftime('%Y%m%d')
            report_filename = f"weekly_report_{timestamp}.html"
            report_path = os.path.join(self.reports_dir, report_filename)
            
            # Create weekly HTML report (simplified version)
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Weekly Job Search Report - {self.profile['name']}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .header {{ text-align: center; color: #2c3e50; }}
                    .summary {{ display: flex; justify-content: space-around; margin: 20px 0; }}
                    .stat {{ text-align: center; padding: 15px; background: #ecf0f1; border-radius: 5px; }}
                    .chart {{ margin: 20px 0; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>📊 Weekly Job Search Report</h1>
                    <h2>{weekly_data['week_start']} to {weekly_data['week_end']}</h2>
                    <h3>{self.profile['name']} - QA Automation Engineer</h3>
                </div>
                
                <div class="summary">
                    <div class="stat">
                        <h3>Total Applications</h3>
                        <div style="font-size: 2em; color: #e74c3c;">{weekly_data['total_applications']}</div>
                    </div>
                    <div class="stat">
                        <h3>Successful</h3>
                        <div style="font-size: 2em; color: #27ae60;">{weekly_data['successful_applications']}</div>
                    </div>
                    <div class="stat">
                        <h3>HR Emails</h3>
                        <div style="font-size: 2em; color: #3498db;">{weekly_data['total_emails_sent']}</div>
                    </div>
                    <div class="stat">
                        <h3>Jobs Scraped</h3>
                        <div style="font-size: 2em; color: #9b59b6;">{weekly_data['total_jobs_scraped']}</div>
                    </div>
                </div>
                
                <h2>📅 Daily Breakdown</h2>
                <table border="1" style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <th>Date</th>
                        <th>Day</th>
                        <th>Applications</th>
                        <th>Successful</th>
                        <th>Emails</th>
                        <th>Success Rate</th>
                    </tr>
            """
            
            for day in weekly_data['daily_breakdown']:
                success_rate = (day['successful'] / max(day['applications'], 1)) * 100
                html_content += f"""
                    <tr>
                        <td>{day['date']}</td>
                        <td>{day['day_name']}</td>
                        <td>{day['applications']}</td>
                        <td>{day['successful']}</td>
                        <td>{day['emails_sent']}</td>
                        <td>{success_rate:.1f}%</td>
                    </tr>
                """
            
            html_content += """
                </table>
                
                <h2>🏢 Top Companies Applied</h2>
                <ul>
            """
            
            # Show top 10 companies
            top_companies = sorted(weekly_data['top_companies'].items(), key=lambda x: x[1], reverse=True)[:10]
            for company, count in top_companies:
                html_content += f"<li>{company}: {count} applications</li>"
            
            html_content += """
                </ul>
                
                <div style="text-align: center; margin-top: 30px; color: #7f8c8d;">
                    <p>Generated by Job Search Bot | Keep up the great work!</p>
                </div>
            </body>
            </html>
            """
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.logger.info(f"Generated weekly report: {report_path}")
            return report_path
        
        except Exception as e:
            self.logger.error(f"Error generating weekly report: {e}")
            return None
    
    def cleanup_old_files(self, days_to_keep: int = 30):
        """Clean up old report and data files"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            deleted_count = 0
            
            for directory in [self.reports_dir, self.data_dir]:
                if not os.path.exists(directory):
                    continue
                    
                for filename in os.listdir(directory):
                    filepath = os.path.join(directory, filename)
                    
                    try:
                        # Check file modification time
                        file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                        
                        if file_time < cutoff_date:
                            os.remove(filepath)
                            deleted_count += 1
                            self.logger.info(f"Deleted old file: {filename}")
                    except Exception as e:
                        self.logger.error(f"Error checking file {filename}: {e}")
            
            self.logger.info(f"Cleanup completed. Deleted {deleted_count} old files.")
        
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    def export_data_summary(self, format: str = 'excel') -> str:
        """Export comprehensive data summary"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if format.lower() == 'excel':
                filename = f"job_search_summary_{timestamp}.xlsx"
                filepath = os.path.join(self.reports_dir, filename)
                
                # Create Excel workbook with multiple sheets
                with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                    # Get all data files
                    all_applications = []
                    all_emails = []
                    all_jobs = []
                    
                    # Collect data from last 7 days
                    for i in range(7):
                        date = datetime.now() - timedelta(days=i)
                        date_str = date.strftime('%Y%m%d')
                        
                        for filename in os.listdir(self.data_dir):
                            if date_str in filename and filename.endswith('.json'):
                                try:
                                    with open(os.path.join(self.data_dir, filename), 'r') as f:
                                        data = json.load(f)
                                    
                                    if 'application_results' in filename:
                                        all_applications.extend(data)
                                    elif 'email_results' in filename:
                                        all_emails.extend(data)
                                    elif 'scraped_jobs' in filename:
                                        all_jobs.extend(data)
                                except:
                                    continue
                    
                    # Create DataFrames and save to Excel
                    if all_applications:
                        df_apps = pd.json_normalize(all_applications)
                        df_apps.to_excel(writer, sheet_name='Applications', index=False)
                    
                    if all_emails:
                        df_emails = pd.DataFrame(all_emails)
                        df_emails.to_excel(writer, sheet_name='Email_Outreach', index=False)
                    
                    if all_jobs:
                        df_jobs = pd.json_normalize(all_jobs)
                        df_jobs.to_excel(writer, sheet_name='Scraped_Jobs', index=False)
                
                self.logger.info(f"Data summary exported to: {filepath}")
                return filepath
        
        except Exception as e:
            self.logger.error(f"Error exporting data summary: {e}")
            return None

# Example usage and testing
if __name__ == "__main__":
    reporter = JobReporter()
    
    print("=== Testing Job Reporter ===")
    
    # Test data
    test_apps = [
        {
            'job_id': 'test-1',
            'title': 'QA Automation Engineer',
            'company': 'TechCorp Solutions',
            'status': 'success',
            'reason': 'Applied successfully via Easy Apply',
            'applied_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'steps_completed': 3,
            'filter_result': {
                'resume_to_use': 'Mani_QA1.pdf',
                'relevance_score': 85,
                'salary_lpa': 7,
                'is_fresher_friendly': True,
                'matched_keywords': ['qa', 'automation', 'python', 'selenium']
            },
            'search_keywords': 'QA Automation Engineer'
        },
        {
            'job_id': 'test-2',
            'title': 'Software Tester',
            'company': 'Innovation Systems',
            'status': 'external',
            'reason': 'Redirected to company website',
            'applied_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'steps_completed': 1,
            'filter_result': {
                'resume_to_use': 'Mani_QA2.pdf',
                'relevance_score': 72,
                'salary_lpa': 6,
                'is_fresher_friendly': True,
                'matched_keywords': ['testing', 'manual', 'api']
            },
            'search_keywords': 'Software Tester'
        }
    ]
    
    test_emails = [
        {
            'job_title': 'QA Automation Engineer',
            'company': 'TechCorp Solutions',
            'recipient_email': 'hr@techcorp.com',
            'recipient_name': 'HR Team',
            'email_type': 'formal_application',
            'contact_source': 'domain_pattern',
            'confidence': 'medium',
            'success': True,
            'sent_at': time.strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'job_title': 'Software Tester',
            'company': 'Innovation Systems',
            'recipient_email': 'careers@innovation.com',
            'recipient_name': 'Careers Team',
            'email_type': 'networking',
            'contact_source': 'job_description',
            'confidence': 'high',
            'success': True,
            'sent_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }
    ]
    
    test_jobs = [
        {
            'title': 'QA Automation Engineer',
            'company': 'TechCorp Solutions',
            'location': 'Hyderabad',
            'source': 'LinkedIn',
            'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'title': 'Software Tester',
            'company': 'Innovation Systems',
            'location': 'Bangalore',
            'source': 'Naukri',
            'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }
    ]
    
    print("\\n1. Testing data saving...")
    
    # Save test data
    app_path = reporter.save_application_results(test_apps, "test_applications")
    email_path = reporter.save_email_results(test_emails, "test_emails") 
    jobs_path = reporter.save_scraped_jobs(test_jobs, "test_jobs")
    
    print(f"✅ Applications saved: {app_path}")
    print(f"✅ Emails saved: {email_path}")
    print(f"✅ Jobs saved: {jobs_path}")
    
    print("\\n2. Testing report generation...")
    
    # Generate test reports
    summary = {
        'total_attempted': 2,
        'successful': 1,
        'failed': 0,
        'external': 1,
        'login_required': 0,
        'details': test_apps
    }
    
    daily_report = reporter.generate_daily_report(summary, test_emails, test_jobs)
    print(f"✅ Daily report generated: {daily_report}")
    
    weekly_report = reporter.generate_weekly_report()
    print(f"✅ Weekly report generated: {weekly_report}")
    
    print("\\n3. Testing data export...")
    export_path = reporter.export_data_summary('excel')
    print(f"✅ Data exported: {export_path}")
    
    print("\\n4. Testing weekly summary...")
    weekly_summary = reporter.get_weekly_summary()
    print(f"✅ Weekly summary generated with {len(weekly_summary.get('daily_breakdown', []))} days")
    
    print("\\n=== Reporter Test Complete ===")
    print("Check the 'reports/' and 'data/' directories for generated files")
    print("Open the HTML reports in a web browser to see the full visual report")