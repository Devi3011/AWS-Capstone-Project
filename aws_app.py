from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import boto3
import uuid
from werkzeug.utils import secure_filename
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'ai_marketing_platform_secret_key_2026'

# AWS Configuration 
REGION = 'us-east-1' 

dynamodb = boto3.resource('dynamodb', region_name=REGION)
sns = boto3.client('sns', region_name=REGION)

# DynamoDB Tables for AI Driven Personalized Marketing Platform
users_table = dynamodb.Table('MarketingUsers')
admin_users_table = dynamodb.Table('MarketingAdmins')
campaigns_table = dynamodb.Table('MarketingCampaigns')
customer_segments_table = dynamodb.Table('CustomerSegments')
analytics_table = dynamodb.Table('MarketingAnalytics')

# SNS Topic ARN for Marketing Notifications
SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:604665149129:ai_marketing_platform_topic'

# Configuration for File Uploads (Customer Data, Campaign Assets)
UPLOAD_FOLDER = 'static/marketing_uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'csv', 'xlsx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def send_marketing_notification(subject, message):
    """Send SNS notifications for marketing platform events"""
    try:
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=f"AI Marketing Platform: {subject}",
            Message=message
        )
    except ClientError as e:
        print(f"Notification error: {e}")

@app.route('/')
def index():
    """AI Driven Personalized Marketing Platform Homepage"""
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('marketing_index.html')

@app.route('/about')
def about():
    """About the AI Marketing Platform"""
    return render_template('marketing_about.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Marketing User Registration"""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        company = request.form['company']
        password = request.form['password']
        
        # Check if user exists
        response = users_table.get_item(Key={'username': username})
        if 'Item' in response:
            flash('Username already exists!')
            return render_template('marketing_signup.html')
        
        # Create marketing user
        users_table.put_item(Item={
            'username': username,
            'email': email,
            'company': company,
            'password': password,
            'signup_date': datetime.now().isoformat(),
            'campaigns_created': 0
        })
        
        send_marketing_notification("New Marketer Onboarded", 
            f"Marketer {username} from {company} joined the platform.")
        
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    
    return render_template('marketing_signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User Login for Marketing Platform"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        response = users_table.get_item(Key={'username': username})
        
        if ('Item' in response and 
            response['Item']['password'] == password):
            session['username'] = username
            session['company'] = response['Item'].get('company', '')
            send_marketing_notification("User Login", f"Marketer {username} logged in.")
            return redirect(url_for('dashboard'))
        
        flash('Invalid credentials!')
        return render_template('marketing_login.html')
    
    return render_template('marketing_login.html')

@app.route('/dashboard')
def dashboard():
    """Main Marketing Dashboard"""
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    
    # Get user's campaigns
    response = campaigns_table.scan(
        FilterExpression=Key('owner').eq(username)
    )
    user_campaigns = response.get('Items', [])
    
    # Get analytics summary
    analytics_response = analytics_table.scan(
        FilterExpression=Key('owner').eq(username)
    )
    total_clicks = sum(item.get('clicks', 0) for item in analytics_response.get('Items', []))
    
    return render_template('marketing_dashboard.html', 
                         username=username, 
                         campaigns=user_campaigns,
                         total_clicks=total_clicks)

@app.route('/campaigns')
def campaigns_list():
    """List all available campaigns and templates"""
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Scan all campaigns (public ones)
    response = campaigns_table.scan(
        FilterExpression=Key('visibility').eq('public')
    )
    public_campaigns = response.get('Items', [])
    
    return render_template('marketing_campaigns.html', 
                         campaigns=public_campaigns)

@app.route('/create-campaign', methods=['GET', 'POST'])
def create_campaign():
    """Create AI-Driven Marketing Campaign"""
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form['title']
        target_audience = request.form['target_audience']
        campaign_type = request.form['campaign_type']
        budget = request.form['budget']
        
        # Handle file uploads (customer data CSV, campaign creative)
        customer_data_file = request.files.get('customer_data')
        creative_asset = request.files.get('creative_asset')
        
        customer_filename = None
        creative_filename = None
        
        if customer_data_file and allowed_file(customer_data_file.filename):
            customer_filename = secure_filename(customer_data_file.filename)
            customer_data_file.save(os.path.join(app.config['UPLOAD_FOLDER'], customer_filename))
        
        if creative_asset and allowed_file(creative_asset.filename):
            creative_filename = secure_filename(creative_asset.filename)
            creative_asset.save(os.path.join(app.config['UPLOAD_FOLDER'], creative_filename))
        
        # Generate campaign ID
        campaign_id = str(uuid.uuid4())
        
        campaign_data = {
            'id': campaign_id,
            'title': title,
            'owner': session['username'],
            'target_audience': target_audience,
            'campaign_type': campaign_type,
            'budget': float(budget),
            'status': 'draft',
            'customer_data': customer_filename,
            'creative_asset': creative_filename,
            'created_date': datetime.now().isoformat(),
            'visibility': 'private',
            'ai_recommendations': 'Pending AI analysis'
        }
        
        campaigns_table.put_item(Item=campaign_data)
        
        send_marketing_notification("New Campaign Created", 
            f"{session['username']} created campaign '{title}' targeting {target_audience}")
        
        flash('Campaign created successfully!')
        return redirect(url_for('dashboard'))
    
    return render_template('marketing_create_campaign.html')

@app.route('/customer-segments', methods=['GET', 'POST'])
def customer_segments():
    """AI-Driven Customer Segmentation"""
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        segment_name = request.form['segment_name']
        criteria = request.form['criteria']
        customer_file = request.files['customer_file']
        
        if customer_file and allowed_file(customer_file.filename):
            filename = secure_filename(customer_file.filename)
            customer_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            segment_id = str(uuid.uuid4())
            customer_segments_table.put_item(Item={
                'id': segment_id,
                'owner': session['username'],
                'segment_name': segment_name,
                'criteria': criteria,
                'customer_file': filename,
                'size': 0,  # Will be populated by AI analysis
                'created_date': datetime.now().isoformat()
            })
            
            flash('Customer segment created! AI analysis will begin shortly.')
            return redirect(url_for('customer_segments'))
    
    # Get user's segments
    response = customer_segments_table.scan(
        FilterExpression=Key('owner').eq(session['username'])
    )
    segments = response.get('Items', [])
    
    return render_template('marketing_segments.html', segments=segments)

@app.route('/analytics/<campaign_id>')
def campaign_analytics(campaign_id):
    """Campaign Performance Analytics"""
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Get campaign details
    campaign_response = campaigns_table.get_item(Key={'id': campaign_id})
    campaign = campaign_response.get('Item')
    
    if not campaign or campaign['owner'] != session['username']:
        flash('Campaign not found or access denied!')
        return redirect(url_for('dashboard'))
    
    # Get analytics for this campaign
    analytics_response = analytics_table.scan(
        FilterExpression=Key('campaign_id').eq(campaign_id)
    )
    analytics_data = analytics_response.get('Items', [])
    
    return render_template('marketing_analytics.html', 
                         campaign=campaign, 
                         analytics=analytics_data)

@app.route('/logout')
def logout():
    """User Logout"""
    username = session.pop('username', None)
    session.pop('company', None)
    if username:
        send_marketing_notification("User Logout", f"Marketer {username} logged out.")
    return redirect(url_for('index'))

# Admin Routes for Marketing Platform Management
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        response = admin_users_table.get_item(Key={'username': username})
        if ('Item' in response and 
            response['Item']['password'] == password):
            session['admin'] = username
            return redirect(url_for('admin_dashboard'))
        
        flash('Invalid admin credentials!')
    
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    
    # Platform-wide statistics
    users = users_table.scan().get('Items', [])
    campaigns = campaigns_table.scan().get('Items', [])
    segments = customer_segments_table.scan().get('Items', [])
    
    active_campaigns = len([c for c in campaigns if c.get('status') == 'active'])
    total_marketers = len(users)
    
    return render_template('admin_marketing_dashboard.html',
                         username=session['admin'],
                         total_marketers=total_marketers,
                         active_campaigns=active_campaigns,
                         total_campaigns=len(campaigns),
                         total_segments=len(segments))

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
