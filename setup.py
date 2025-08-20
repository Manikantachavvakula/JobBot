#!/usr/bin/env python3
"""
Automated Setup Script for Manikanta's Job Search Bot
This script automates the initial setup process and configuration
"""

import os
import sys
import json
import subprocess
from pathlib import Path
import getpass

def print_header():
    header = """
╔══════════════════════════════════════════════════════════════╗
║              🤖 MANIKANTA'S JOB SEARCH BOT SETUP              ║
║                                                              ║
║  This setup will configure your personalized job search bot ║
║  for QA Engineer and Automation Testing positions           ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(header)

def check_python_version():
    """Check if Python version is compatible"""
    print("\\n🐍 Checking Python version...")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        print(f"   Current version: {sys.version}")
        print("   Please upgrade Python and try again")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} is compatible")
    return True

def install_dependencies():
    """Install required Python packages"""
    print("\\n📦 Installing dependencies...")
    
    try:
        print("   Installing packages from requirements.txt...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--quiet"
        ])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        print("   Try running: pip install -r requirements.txt")
        return False
    except FileNotFoundError:
        print("❌ requirements.txt not found!")
        print("   Please ensure all bot files are in the current directory")
        return False

def create_directories():
    """Create necessary directories"""
    print("\\n📁 Creating project directories...")
    
    directories = [
        "resumes",
        "data", 
        "reports",
        "logs"
    ]
    
    created_dirs = []
    for directory in directories:
        if not os.path.exists(directory):
            Path(directory).mkdir(exist_ok=True)
            created_dirs.append(directory)
        
    if created_dirs:
        print(f"✅ Created directories: {', '.join(created_dirs)}")
    else:
        print("✅ All directories already exist")
    
    return True

def setup_manikanta_config():
    """Interactive configuration setup for Manikanta's profile"""
    print("\\n⚙️ Setting up Manikanta's job search configuration...")
    
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        print("❌ config.json not found!")
        print("   Please ensure all bot files are in the current directory")
        return False
    
    print("\\n👨‍💻 Verifying Manikanta's Profile Information:")
    print(f"   Name: {config['profile']['name']}")
    print(f"   Email: {config['profile']['email']}")
    print(f"   Phone: {config['profile']['phone']}")
    print(f"   Location: {config['profile']['location']}")
    
    update_profile = input("\\nWould you like to update any profile information? (y/n): ").lower().strip()
    
    if update_profile == 'y':
        print("\\n📝 Update Profile Information (press Enter to keep current value):")
        
        new_name = input(f"Full Name ({config['profile']['name']}): ").strip()
        if new_name:
            config['profile']['name'] = new_name
        
        new_email = input(f"Email ({config['profile']['email']}): ").strip()
        if new_email:
            config['profile']['email'] = new_email
        
        new_phone = input(f"Phone ({config['profile']['phone']}): ").strip()
        if new_phone:
            config['profile']['phone'] = new_phone
        
        new_location = input(f"Location ({config['profile']['location']}): ").strip()
        if new_location:
            config['profile']['location'] = new_location
    
    # Job preferences
    print("\\n🎯 Job Search Preferences:")
    print(f"   Target Roles: {', '.join(config['job_preferences']['roles'][:3])}")
    print(f"   Minimum Salary: ₹{config['job_preferences']['min_salary_lpa']} LPA")
    print(f"   Preferred Locations: {', '.join(config['job_preferences']['locations'][:3])}")
    
    update_preferences = input("\\nWould you like to update job preferences? (y/n): ").lower().strip()
    
    if update_preferences == 'y':
        min_salary = input(f"Minimum Salary LPA ({config['job_preferences']['min_salary_lpa']}): ").strip()
        if min_salary and min_salary.isdigit():
            config['job_preferences']['min_salary_lpa'] = int(min_salary)
        
        print("\\nAdd any additional preferred locations (comma-separated):")
        additional_locations = input("Additional locations: ").strip()
        if additional_locations:
            new_locations = [loc.strip() for loc in additional_locations.split(',')]
            config['job_preferences']['locations'].extend(new_locations)
            # Remove duplicates while preserving order
            config['job_preferences']['locations'] = list(dict.fromkeys(config['job_preferences']['locations']))
    
    # Save updated config
    try:
        with open("config.json", "w") as f:
            json.dump(config, f, indent=2)
        print("✅ Configuration saved successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to save configuration: {e}")
        return False

def setup_email_config():
    """Configure email settings for Manikanta"""
    print("\\n📧 Email Configuration Setup")
    print("We need to set up email functionality for:")
    print("   • Daily summary reports")
    print("   • HR outreach emails")
    print("   • Application confirmations")
    
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
    except:
        print("❌ Could not load config.json")
        return False
    
    print("\\n📮 Gmail Setup Instructions:")
    print("1. Enable 2-Factor Authentication on your Gmail account")
    print("2. Generate an App Password:")
    print("   • Go to: https://support.google.com/accounts/answer/185833")
    print("   • Follow the steps to create an app password")
    print("   • Use 'Job Search Bot' as the app name")
    
    setup_email = input("\\nDo you want to configure email now? (y/n): ").lower().strip()
    
    if setup_email == 'y':
        email = input("\\nEnter your Gmail address: ").strip()
        if email:
            config['email_config']['sender_email'] = email
            config['profile']['email'] = email  # Update profile email too
        
        print("\\n🔐 Enter your Gmail App Password:")
        print("   (This will not be displayed as you type)")
        app_password = getpass.getpass("App Password: ").strip()
        
        if app_password:
            config['email_config']['sender_password'] = app_password
        
        # Save email config
        try:
            with open("config.json", "w") as f:
                json.dump(config, f, indent=2)
            print("✅ Email configuration saved")
            
            # Test email configuration
            test_email = input("\\nWould you like to test email configuration? (y/n): ").lower().strip()
            if test_email == 'y':
                success = test_email_connection(config)
                if not success:
                    print("⚠️  Email test failed - you can configure this later")
            
            return True
        except Exception as e:
            print(f"❌ Failed to save email configuration: {e}")
            return False
    else:
        print("⚠️  Email configuration skipped")
        print("   You can configure this later by updating config.json")
        return True

def test_email_connection(config):
    """Test email connection"""
    try:
        import smtplib
        from email.mime.text import MIMEText
        
        print("   Testing email connection...")
        
        smtp_server = smtplib.SMTP(config['email_config']['smtp_server'], config['email_config']['smtp_port'])
        smtp_server.starttls()
        smtp_server.login(config['email_config']['sender_email'], config['email_config']['sender_password'])
        
        # Send test email to self
        msg = MIMEText("Job Search Bot email configuration test successful!")
        msg['Subject'] = "Job Search Bot - Email Test"
        msg['From'] = config['email_config']['sender_email']
        msg['To'] = config['email_config']['sender_email']
        
        smtp_server.send_message(msg)
        smtp_server.quit()
        
        print("✅ Email test successful! Check your inbox for confirmation.")
        return True
    
    except Exception as e:
        print(f"❌ Email test failed: {e}")
        print("   Please check your credentials and try again later")
        return False

def check_resume_files():
    """Check for Manikanta's resume files"""
    print("\\n📄 Checking resume files...")
    
    expected_resumes = {
        "Mani_QA1.pdf": "Automation-focused resume (Python, Selenium, frameworks)",
        "Mani_QA2.pdf": "General QA resume (manual + automation)",
        "Mani_QA3.pdf": "Entry-level resume (concise, fresher-friendly)"
    }
    
    resume_dir = "resumes"
    missing_files = []
    found_files = []
    
    for resume_file, description in expected_resumes.items():
        resume_path = os.path.join(resume_dir, resume_file)
        if os.path.exists(resume_path):
            found_files.append(resume_file)
        else:
            missing_files.append((resume_file, description))
    
    if found_files:
        print("✅ Found resume files:")
        for file in found_files:
            print(f"   • {file}")
    
    if missing_files:
        print("\\n📝 Missing resume files:")
        for file, description in missing_files:
            print(f"   • {file} - {description}")
        
        print(f"\\n📂 Please add your resume files to the '{resume_dir}/' directory")
        print("   Based on your profile, create these versions:")
        print("   1. Mani_QA1.pdf - Highlight automation projects (QA-Monkey, NetWrecker)")
        print("   2. Mani_QA2.pdf - Balanced QA experience (Amazon + automation)")
        print("   3. Mani_QA3.pdf - Concise entry-level version")
        
        add_resumes = input("\\nHave you added the resume files? (y/n): ").lower().strip()
        if add_resumes == 'y':
            return check_resume_files()  # Recheck
        else:
            print("⚠️  Resume files missing - add them before running the bot")
            return False
    
    print("✅ All resume files found")
    return True

def create_env_file():
    """Create .env file for sensitive data"""
    print("\\n🔐 Creating environment file...")
    
    env_content = f"""# Manikanta's Job Search Bot - Environment Variables
# Generated on {os.uname().nodename if hasattr(os, 'uname') else 'Windows'} at {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# Email Configuration (Auto-configured during setup)
SENDER_EMAIL=manikantaa.dev@gmail.com
SENDER_PASSWORD=your_gmail_app_password_here

# Bot Configuration
BOT_MODE=live
DEBUG_MODE=False
HEADLESS_BROWSER=True

# Safety Limits
MAX_DAILY_APPLICATIONS=20
MAX_DAILY_EMAILS=40

# Timing Configuration (seconds)
APPLICATION_DELAY_MIN=10
APPLICATION_DELAY_MAX=30
EMAIL_DELAY_MIN=30
EMAIL_DELAY_MAX=120

# Site-specific settings (optional login credentials)
LINKEDIN_EMAIL=
LINKEDIN_PASSWORD=
NAUKRI_EMAIL=
NAUKRI_PASSWORD=
INDEED_EMAIL=
INDEED_PASSWORD=

# Profile Information
PROFILE_NAME=Manikanta Chavvakula
PROFILE_LOCATION=Hyderabad, India
PROFILE_PHONE=+91-9676853187

# Job Search Settings
TARGET_ROLES=QA Engineer,Automation Engineer,Software Tester,SDET
MIN_SALARY_LPA=5
PREFERRED_LOCATIONS=Remote,Hyderabad,Visakhapatnam,Bangalore
"""
    
    env_path = ".env"
    
    if os.path.exists(env_path):
        print("✅ .env file already exists")
        return True
    
    try:
        with open(env_path, "w") as f:
            f.write(env_content)
        print("✅ Created .env file with default values")
        print("   You can customize these settings as needed")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def run_initial_test():
    """Run initial test to verify setup"""
    print("\\n🧪 Running initial system test...")
    
    try:
        print("   Testing module imports...")
        
        # Test core imports
        from scrapers import JobScraper
        from filters import JobFilter
        from auto_apply import JobApplicator
        from emailer import EmailManager
        from reporter import JobReporter
        
        print("   ✅ All core modules imported successfully")
        
        # Test configuration loading
        filter_test = JobFilter()
        print("   ✅ Configuration loading works")
        
        # Test directory structure
        required_dirs = ['resumes', 'data', 'reports', 'logs']
        for directory in required_dirs:
            if not os.path.exists(directory):
                print(f"   ❌ Missing directory: {directory}")
                return False
        
        print("   ✅ Directory structure verified")
        print("✅ All system tests passed!")
        return True
        
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        print("   Try reinstalling dependencies: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False

def print_completion_message():
    """Print setup completion message and next steps"""
    print("\\n" + "="*80)
    print("🎉 SETUP COMPLETE! Manikanta's Job Search Bot is Ready!")
    print("="*80)
    
    print("\\n🚀 NEXT STEPS:")
    print()
    print("1. 📄 RESUME FILES:")
    print("   • Ensure all 3 resume versions are in the resumes/ directory")
    print("   • Mani_QA1.pdf (Automation-focused)")
    print("   • Mani_QA2.pdf (General QA)")  
    print("   • Mani_QA3.pdf (Entry-level)")
    print()
    
    print("2. 🧪 TEST THE BOT:")
    print("   python main.py --test          # Safe test mode")
    print("   python main.py --once          # Single run test")
    print()
    
    print("3. 🚀 START JOB HUNTING:")
    print("   python main.py                 # Start daily automation")
    print()
    
    print("📊 MONITORING & REPORTS:")
    print("   • HTML reports: reports/ directory")
    print("   • Raw data: data/ directory")
    print("   • Logs: logs/ directory")
    print("   • Daily email summaries to your inbox")
    print()
    
    print("⚙️ CONFIGURATION:")
    print("   • Main settings: config.json")
    print("   • Environment variables: .env")
    print("   • Update preferences anytime by editing these files")
    print()
    
    print("🎯 WHAT THE BOT WILL DO:")
    print("   🌅 Morning (9:00 AM): Search & apply to QA/Automation jobs")
    print("   🌆 Evening (6:00 PM): Additional search & daily summary")
    print("   📧 HR Outreach: Personalized emails to hiring managers")
    print("   📊 Weekly Reports: Performance analysis every Sunday")
    print()
    
    print("🔗 USEFUL LINKS:")
    print("   • Gmail App Passwords: https://support.google.com/accounts/answer/185833")
    print("   • Manikanta's LinkedIn: https://linkedin.com/in/manikanta-chavvakula")
    print("   • Portfolio: https://manikanta-portfolio.com")
    print()
    
    print("💡 TIPS FOR SUCCESS:")
    print("   • Start with test mode to verify everything works")
    print("   • Monitor logs for any issues")
    print("   • Check email daily for application responses")
    print("   • Update resume based on market feedback")
    print("   • Be patient - quality applications take time!")
    print()
    
    print("🎯 TARGET: Land your dream QA Automation Engineer role!")
    print("💪 Remember: Every application is a step closer to success!")
    print()
    print("="*80)

def main():
    """Main setup process"""
    print_header()
    
    setup_steps = [
        ("Checking Python version", check_python_version),
        ("Installing dependencies", install_dependencies),
        ("Creating directories", create_directories),
        ("Setting up configuration", setup_manikanta_config),
        ("Configuring email", setup_email_config),
        ("Creating environment file", create_env_file),
        ("Checking resume files", check_resume_files),
        ("Running system test", run_initial_test)
    ]
    
    completed_steps = 0
    total_steps = len(setup_steps)
    
    for step_name, step_function in setup_steps:
        print(f"\\n[{completed_steps + 1}/{total_steps}] {step_name}...")
        
        try:
            if step_function():
                completed_steps += 1
                print(f"✅ {step_name} completed")
            else:
                print(f"❌ {step_name} failed")
                
                # Ask if user wants to continue
                if completed_steps < total_steps - 2:  # Don't ask for last 2 steps
                    continue_setup = input(f"\\nContinue setup despite this issue? (y/n): ").lower().strip()
                    if continue_setup != 'y':
                        print("\\n⏹️ Setup interrupted by user")
                        break
        except KeyboardInterrupt:
            print("\\n⏹️ Setup interrupted by user")
            break
        except Exception as e:
            print(f"❌ {step_name} failed with error: {e}")
    
    # Summary
    print(f"\\n📊 Setup Summary: {completed_steps}/{total_steps} steps completed")
    
    if completed_steps == total_steps:
        print_completion_message()
    elif completed_steps >= 6:  # Most critical steps done
        print("\\n⚠️ Setup completed with some issues, but bot should be functional")
        print("Review the errors above and fix them for optimal performance")
        print("\\nYou can run: python main.py --test")
    else:
        print("\\n❌ Setup incomplete - too many issues encountered")
        print("Please resolve the errors above and run setup again")
        print("\\nFor help, check:")
        print("• README.md for detailed instructions")
        print("• Log files in the logs/ directory")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\\n\\n👋 Setup cancelled by user. You can run this again anytime!")
    except Exception as e:
        print(f"\\n❌ Setup failed with critical error: {e}")
        print("Please check your Python installation and try again")