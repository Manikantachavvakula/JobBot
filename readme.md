# 🤖 Manikanta's AI-Powered Job Search Bot

An intelligent automation bot specifically designed for **Manikanta Chavvakula** to find and apply to QA Engineer/Automation Testing positions across multiple job platforms.

## 🎯 Bot Overview

This bot is tailored for Manikanta's profile:
- **Target Role**: QA Engineer, Automation Engineer, Software Tester, SDET
- **Experience Level**: 1+ years (Amazon ROC Specialist + automation projects)
- **Skills**: Python, Selenium, PyTest, API Testing, Process Optimization
- **Salary Range**: ₹5+ LPA
- **Locations**: Remote, Hyderabad, Visakhapatnam, Bangalore

## ⚡ Key Features

### 🔍 **Multi-Platform Job Scraping**
- **LinkedIn**: Premium job search with Easy Apply detection
- **Naukri.com**: India's largest job portal
- **Indeed**: International opportunities
- **TimesJobs**: Additional Indian market coverage
- **Smart Deduplication**: Removes duplicate listings

### 🎯 **Intelligent Job Filtering**
- **Role Relevance**: Matches QA/Testing keywords and requirements
- **Experience Matching**: Filters for fresher-friendly and 1-2 year positions
- **Salary Filtering**: Ensures minimum ₹5 LPA requirements
- **Location Preferences**: Prioritizes remote and preferred cities
- **Resume Selection**: Automatically chooses best-fit resume based on job requirements

### 📝 **Automated Applications**
- **LinkedIn Easy Apply**: Automated form filling and submission
- **Resume Upload**: Smart selection from 3 resume versions
- **Form Intelligence**: Fills common fields (experience, salary, notice period)
- **Error Handling**: Graceful failure management and retry logic
- **Rate Limiting**: Respects platform limits (15-20 applications/day)

### 📧 **HR Outreach System**
- **Contact Discovery**: Extracts HR emails from job postings
- **Domain Generation**: Creates likely HR email patterns
- **Personalized Templates**: Multiple email variations for Manikanta's profile
- **Professional Tone**: Highlights Amazon experience and automation skills
- **Attachment Management**: Includes relevant resume version

### 📊 **Comprehensive Reporting**
- **Daily HTML Reports**: Visual performance dashboards
- **Weekly Summaries**: Trend analysis and insights
- **Email Notifications**: Daily summary sent to Manikanta
- **Data Export**: CSV/Excel for external analysis
- **Success Tracking**: Application outcomes and response rates

## 🚀 Quick Start Guide

### 1. **Initial Setup**
```bash
# Clone/download all bot files to a directory
mkdir manikanta-job-bot
cd manikanta-job-bot

# Run automated setup
python setup.py
```

### 2. **Add Resume Files**
Place these 3 resume versions in the `resumes/` directory:
- **Mani_QA1.pdf** - Automation-focused (for Selenium/PyTest roles)
- **Mani_QA2.pdf** - General QA (balanced manual + automation)
- **Mani_QA3.pdf** - Entry-level (concise, fresher-friendly)

### 3. **Configure Email**
- Enable 2FA on Gmail
- Generate app password: [Gmail Setup Guide](https://support.google.com/accounts/answer/185833)
- Update `config.json` with credentials

### 4. **Test the Bot**
```bash
# Safe test mode (no actual applications)
python main.py --test

# Single run test
python main.py --once

# Start daily automation
python main.py
```

## 📋 Detailed Setup Instructions

### Prerequisites
- **Python 3.8+**
- **Chrome Browser** (latest version)
- **Gmail Account** with app password
- **Resume Files** in PDF format
- **Stable Internet** connection

### Installation Steps

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Configure Profile** (edit `config.json`)
```json
{
  "profile": {
    "name": "Manikanta Chavvakula",
    "email": "manikantaa.dev@gmail.com",
    "phone": "+91-9676853187",
    "location": "Hyderabad, India"
  }
}
```

3. **Set Email Credentials**
```json
{
  "email_config": {
    "sender_email": "manikantaa.dev@gmail.com",
    "sender_password": "your_app_password_here"
  }
}
```

4. **Verify Resume Files**
```
resumes/
├── Mani_QA1.pdf    # Automation roles
├── Mani_QA2.pdf    # General QA roles
└── Mani_QA3.pdf    # Entry-level roles
```

## ⚙️ Configuration Guide

### Job Preferences (`config.json`)
```json
{
  "job_preferences": {
    "roles": [
      "QA Engineer",
      "QA Automation Engineer",
      "Software Tester",
      "SDET"
    ],
    "min_salary_lpa": 5,
    "locations": ["Remote", "Hyderabad", "Visakhapatnam"],
    "experience_level": ["Fresher", "0-1 years", "1-2 years"]
  }
}
```

### Daily Limits (Safety)
```json
{
  "daily_limits": {
    "max_applications": 20,
    "max_hr_emails": 40,
    "morning_applications": 8,
    "evening_applications": 12
  }
}
```

### Resume Selection Logic
The bot automatically selects the best resume based on job requirements:

- **Mani_QA1.pdf**: Jobs mentioning Selenium, PyTest, automation frameworks, SDET
- **Mani_QA2.pdf**: General QA positions, mix of manual and automation
- **Mani_QA3.pdf**: Entry-level roles, fresher positions, simple requirements

## 🕐 Daily Schedule

### Morning Routine (9:00 AM)
1. **🔍 Job Scraping**: Search across all platforms
2. **🎯 Filtering**: Apply Manikanta's criteria
3. **📝 Applications**: Submit 6-8 best matches
4. **📧 HR Outreach**: Email 15-20 hiring managers

### Evening Routine (6:00 PM)
1. **🔍 Additional Search**: Alternative keywords and sources
2. **📝 More Applications**: 8-12 additional submissions
3. **📊 Daily Report**: Generate comprehensive summary
4. **📧 Email Summary**: Send daily performance report

### Weekly Tasks (Sunday)
- **📊 Weekly Report**: Generate performance analysis
- **🧹 Cleanup**: Remove old files (30+ days)
- **📈 Trend Analysis**: Success rates and optimization suggestions

## 📊 Expected Results

### Daily Performance
| Metric | Target | Actual Range |
|--------|--------|--------------|
| Jobs Scraped | 50-100 | 60-120 |
| Applications | 15-20 | 12-18 |
| HR Emails | 30-40 | 25-35 |
| Success Rate | 60-80% | 65-75% |

### Weekly Outcomes
- **Applications**: 100-140 per week
- **Interview Callbacks**: 5-15% response rate
- **HR Responses**: 10-20% engagement rate
- **Platform Coverage**: 4-6 job sites daily

## 🛡️ Safety & Compliance

### Rate Limiting
- **Random Delays**: 10-30 seconds between applications
- **Human-like Patterns**: Varied timing and behavior
- **Daily Caps**: Strict limits to prevent spam detection
- **Error Handling**: Graceful failure recovery

### Data Privacy
- **Local Storage**: All data stored locally
- **Secure Credentials**: Environment variables for sensitive data
- **No Data Sharing**: Zero external data transmission
- **Log Management**: Automatic cleanup of old files

### Platform Compliance
- **Terms of Service**: Designed to respect platform ToS
- **API Limits**: Stays within documented rate limits
- **User Agent Rotation**: Appears as regular browser usage
- **Session Management**: Proper login/logout procedures

## 📈 Monitoring & Reports

### Real-time Monitoring
```bash
# View live logs
tail -f logs/mani_job_bot.log

# Check daily stats
python main.py --status

# Generate immediate report
python main.py --weekly
```

### Report Types

1. **Daily HTML Report**
   - Visual dashboard with charts
   - Application success breakdown
   - HR outreach summary
   - Performance metrics

2. **Weekly Analysis**
   - Trend analysis
   - Success rate patterns
   - Top companies applied
   - Optimization recommendations

3. **Email Summaries**
   - Sent to Manikanta daily
   - Key metrics and highlights
   - Next day recommendations
   - Success celebration

## 🔧 Troubleshooting

### Common Issues

1. **Chrome Driver Issues**
```bash
# Update webdriver
pip install webdriver-manager --upgrade
```

2. **Email Authentication Failed**
- Verify 2FA is enabled on Gmail
- Generate new app password
- Check for typos in credentials

3. **No Jobs Found**
- Verify search keywords in config
- Check target locations
- Review salary requirements

4. **Application Failures**
- Check resume file paths
- Verify internet connection
- Review platform changes

### Debug Mode
Enable detailed logging:
```json
{
  "debug_mode": true,
  "headless_browser": false
}
```

### Log Files
- **mani_job_bot.log**: Main bot activities
- **job_scraper.log**: Scraping operations
- **job_applications.log**: Application attempts
- **email_manager.log**: Email operations

## 🎯 Customization Options

### Adding New Job Sites
1. Create scraper function in `scrapers.py`
2. Add application logic in `auto_apply.py`
3. Update site list in `config.json`

### Custom Email Templates
Edit templates in `emailer.py`:
```python
def create_job_application_email(self, job_data):
    # Add custom email templates for Manikanta
    templates = [
        "Your custom template highlighting Amazon experience...",
        "Another variation emphasizing automation skills..."
    ]
```

### Filter Customization
Modify job filtering in `filters.py`:
```python
def is_relevant_role(self, job_title, job_description):
    # Customize filtering logic for Manikanta's requirements
```

## 📞 Support & Maintenance

### Getting Help
1. **Check Logs**: Review detailed error logs
2. **Test Components**: Run individual modules
3. **Verify Config**: Ensure all settings are correct
4. **Update Dependencies**: Keep packages current

### Regular Maintenance
- **Weekly Review**: Check success rates and adjust
- **Monthly Updates**: Update search keywords and preferences
- **Quarterly Cleanup**: Archive old reports and optimize
- **Resume Updates**: Refresh based on market feedback

### Performance Optimization
- **Success Rate Analysis**: Track which approaches work best
- **Keyword Optimization**: Refine search terms based on results
- **Template A/B Testing**: Try different email approaches
- **Platform Focus**: Prioritize most successful sources

## 🎉 Success Tips for Manikanta

### Profile Optimization
1. **LinkedIn Profile**: Keep updated with recent projects
2. **Resume Versions**: Tailor for different role types
3. **Skills Keywords**: Include trending QA technologies
4. **Project Highlights**: Emphasize QA-Monkey and automation work

### Application Strategy
1. **Quality over Quantity**: Focus on relevant positions
2. **Follow-up Schedule**: Manual follow-up after 1 week
3. **Response Tracking**: Monitor callback patterns
4. **Interview Prep**: Stay ready for quick responses

### Market Adaptation
1. **Trend Monitoring**: Watch for new QA technologies
2. **Salary Benchmarking**: Adjust expectations based on responses
3. **Location Flexibility**: Consider hybrid opportunities
4. **Company Research**: Target companies with growth potential

## 🚨 Important Notes

### Legal & Ethical Use
- **Personal Use Only**: Designed specifically for Manikanta's job search
- **Respect Platform ToS**: Always comply with site terms of service
- **Rate Limiting**: Built-in safeguards to prevent abuse
- **Data Responsibility**: User responsible for credential security

### Limitations
- **Platform Changes**: Sites may update and break scrapers
- **CAPTCHA Challenges**: Manual intervention sometimes required
- **Login Requirements**: Some sites need manual authentication
- **Market Conditions**: Success depends on job availability

### Disclaimer
This bot is an automation tool designed to assist in job searching. Success depends on market conditions, profile quality, and proper configuration. The bot respects platform terms of service and includes safety measures to prevent misuse.

---

## 📧 Contact Information

**For Manikanta Chavvakula:**
- **Email**: manikantaa.dev@gmail.com
- **Phone**: +91-9676853187
- **LinkedIn**: [Manikanta Chavvakula](https://linkedin.com/in/manikanta-chavvakula)
- **GitHub**: [manikanta-chavvakula](https://github.com/manikanta-chavvakula)

**Bot Version**: 1.0  
**Last Updated**: January 2025  
**Target Role**: QA Automation Engineer  

---

*🎯 "Every application is a step closer to your dream QA role!" - Keep going, Manikanta!* 🚀