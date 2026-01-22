from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime
import random
import os

app = Flask(__name__)
app.secret_key = 'ai-marketing-2030'

# ----------------- DATA -----------------
users = {'admin': 'admin123'}

customers = [
    {'id': 1, 'name': 'Anita Sharma', 'email': 'anita@company.com', 'engagement_score': 0.86, 'last_purchase_value': 1250},
    {'id': 2, 'name': 'Ravi Kumar', 'email': 'ravi@company.com', 'engagement_score': 0.42, 'last_purchase_value': 89},
    {'id': 3, 'name': 'Sara Patel', 'email': 'sara@company.com', 'engagement_score': 0.93, 'last_purchase_value': 3400},
]

campaigns = []

# ----------------- HELPERS -----------------
def is_logged_in():
    return 'username' in session

def require_login():
    if not is_logged_in():
        flash('Please log in to continue.', 'error')
        return redirect(url_for('login'))
    return None

# ----------------- ALL ROUTES -----------------
@app.route('/')
def index():
    if is_logged_in():
        return redirect(url_for('dashboard'))
    return render_template('index.html', username=session.get('username'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        if username in users and users[username] == password:
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials.', 'error')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        if username in users:
            flash('Username already exists.', 'error')
        else:
            users[username] = password
            flash('Account created! Please log in.', 'success')
            return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out!', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    login_check = require_login()
    if login_check:
        return login_check
    
    total_customers = len(customers)
    total_campaigns = len(campaigns)
    avg_engagement = round(sum(c['engagement_score'] for c in customers) / total_customers, 2) if total_customers else 0
    
    return render_template('dashboard.html', 
                         username=session['username'],
                         total_customers=total_customers, 
                         total_campaigns=total_campaigns, 
                         avg_engagement=avg_engagement)

@app.route('/insights')
def insights():
    login_check = require_login()
    if login_check:
        return login_check
    high_value = len([c for c in customers if c.get('last_purchase_value', 0) > 1000])
    high_engagement = len([c for c in customers if c['engagement_score'] > 0.8])
    return render_template('insights.html', 
                         total_customers=len(customers), 
                         high_value=high_value, 
                         high_engagement=high_engagement)

@app.route('/reports')
def reports():
    login_check = require_login()
    if login_check:
        return login_check
    
    total_customers_count = len(customers)
    avg_engagement_pct = round(sum(c['engagement_score'] for c in customers)/len(customers), 2) if customers else 0
    
    high_value_customers = len([c for c in customers if c.get('last_purchase_value', 0) > 1000])
    high_engagement_customers = len([c for c in customers if c['engagement_score'] > 0.8])
    at_risk_customers = len([c for c in customers if c['engagement_score'] < 0.3])
    
    total_revenue = sum(c.get('last_purchase_value', 0) for c in customers)
    avg_customer_value = round(total_revenue / total_customers_count, 0) if total_customers_count else 0
    
    return render_template('reports.html', 
                         total_customers=total_customers_count,
                         avg_engagement=avg_engagement_pct,
                         high_value_customers=high_value_customers,
                         high_engagement_customers=high_engagement_customers,
                         at_risk_customers=at_risk_customers,
                         total_revenue=total_revenue,
                         avg_customer_value=avg_customer_value)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    login_check = require_login()
    if login_check:
        return login_check
    if request.method == 'POST':
        flash('Settings saved!', 'success')
        return redirect(url_for('settings'))
    return render_template('settings.html')

@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

@app.route('/demo', methods=['GET', 'POST'])
def demo():
    login_check = require_login()
    if login_check:
        return login_check
    message = ""
    if request.method == 'POST':
        name = request.form['name']
        message = f"Hi {name}! Your personalized AI message: 25% OFF exclusive offer just for you! 🎁"
    return render_template('demo.html', message=message)

@app.route('/integrations')
def integrations():
    login_check = require_login()
    if login_check:
        return login_check
    return render_template('integrations.html')

@app.route('/help')
def help_page():
    return render_template('help.html')

@app.route('/debug')
def debug():
    import os
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    files = os.listdir(template_dir) if os.path.exists(template_dir) else []
    return f"Template folder exists: {os.path.exists(template_dir)}<br>Files: {files}"

if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)
