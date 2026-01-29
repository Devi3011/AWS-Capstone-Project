AWS AI-Driven Personalized Marketing Platform

1.🏠 home.html
Purpose: Welcome page
What user sees:
App name at top
Big heading: AI Marketing Platform
Short description
Button: Get Started / Login
👉 This is the main entry page

2.🔐 login.html
Purpose: User login
What user sees:
Email field
Password field
Login button
Link: “Don’t have an account? Sign up”
👉 Used to access dashboard

3.📝 signup.html
Purpose: New user registration
What user sees:
Name
Email
Password
Signup button
👉 Creates a new account

4.ℹ️ about.html
Purpose: About the application
What user sees:
What the platform does
Why AI marketing is useful
Simple explanation text
👉 Explains project idea

5.🧱 base.html
Purpose: Common layout
What it contains visually:
Top navigation bar
Same header & footer on all pages
👉 All pages look consistent

6.📊 dashboard.html
Purpose: Main working page
What user sees:
Big number boxes:
Customers
Campaigns
Engagement
Performance table below
👉 Shows marketing data

7.🤖 demo.html
Purpose: AI feature demo
What user sees:
One input box
One button
Generated AI message appears
👉 Demonstrates AI personalization

8.❓ help.html
Purpose: User guidance
What user sees:
FAQ questions
Simple answers
👉 Helps users understand the app

9.🏁 index.html
Purpose: Default landing page
What user sees:
Same as home OR redirect to home
Clean introduction
👉 First page when app loads

10.📈 insight.html
Purpose: Analytics & insights
What user sees:
Charts (conceptually)
Insights like:
High-performing campaigns
User behavior summary
👉 Shows AI analysis

11.🔌 integration.html
Purpose: External connections
What user sees:
List of tools:
Email
CRM
Social media
Connect buttons
👉 Shows scalability

12.💰 pricing.html
Purpose: Subscription plans
What user sees:
Free plan
Pro plan
Enterprise plan
Buy buttons
👉 Monetization page

13.📑 reports.html
Purpose: Reports
What user sees:
Download buttons
Report list
Summary tables
👉 For business reporting

14.⚙️ setting.html
Purpose: User settings
What user sees:
Profile info
Change password
Preferences
👉 User control panel

app.py

Visual Flow
👤 User
   ↓
🧠 app.py
   ↓
📄 Pages (Home, Login, Dashboard, etc.)
What app.py does
Starts the application
Opens Home / Index page
Connects all pages
Handles login and user actions
Runs only on local system
Pages Connected by app.py
Home → Login → Dashboard → Insights → Reports → Demo → Settings → Help
Use of app.py
Development
Testing

Project building

 aws_app.py

Visual Flow
🌍 Internet User
        ↓
☁️ AWS Server
        ↓
🧠 aws_app.py
        ↓
📄 Pages (Dashboard, Reports, Demo, etc.)
What aws_app.py does
Runs the app on AWS
Gives a public URL
Allows many users
used for final deployment
Use of aws_app.py
Hosting
Online access
Final demo / submission







