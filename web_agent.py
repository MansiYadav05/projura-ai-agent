""" Project Ideas AI Agent using Flask with Built-in Tools, Custom Tools, and Improved Memory
"""

from flask import Flask, render_template, request, jsonify, session, redirect
import os
from dotenv import load_dotenv
import google.generativeai as genai
import secrets
import requests
from typing import Dict, List, Any
from datetime import datetime, timedelta
import jwt
from functools import wraps
from database import db
import re
import bcrypt
from email_validator import validate_email, EmailNotValidError
from email_service import email_service

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.permanent_session_lifetime = timedelta(days=7)  # Remember me duration

# Configure Gemini API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

# JWT Configuration
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

# In-memory storage for sessions (use database in production)
SESSION_STORE = {}
USER_PREFERENCES = {}

# In-memory storage for projects
PROJECTS_STORE = {}  # {user_id: {project_id: project_data}}
PROJECT_ID_COUNTER = {}  # {user_id: counter}


# JWT Authentication Functions
def generate_jwt_token(username: str) -> str:
    """Generate JWT token for authenticated user"""
    payload = {
        'username': username,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token


def verify_jwt_token(token: str) -> Dict[str, Any]:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return {'valid': True, 'payload': payload}
    except jwt.ExpiredSignatureError:
        return {'valid': False, 'message': 'Token has expired'}
    except jwt.InvalidTokenError:
        return {'valid': False, 'message': 'Invalid token'}


def token_required(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check for token in Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'error': 'Invalid authorization header'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        # Verify token
        result = verify_jwt_token(token)
        if not result['valid']:
            return jsonify({'error': result['message']}), 401
        
        # Store username in request context
        request.username = result['payload']['username']
        return f(*args, **kwargs)
    
    return decorated


class BudgetCalculatorTool:
    """Custom tool to calculate project budget breakdown"""
    
    @staticmethod
    def calculate_budget(project_type: str, duration_months: int, team_size: int = 1) -> Dict[str, Any]:
        """Calculate estimated budget for a project"""
        
        # Base costs per month
        base_costs = {
            "web_development": 500,
            "mobile_app": 800,
            "ai_ml": 1200,
            "data_science": 1000,
            "game_development": 900,
            "iot": 700,
            "blockchain": 1500,
            "default": 600
        }
        
        base = base_costs.get(project_type.lower().replace(" ", "_"), base_costs["default"])
        
        # Calculate costs
        development_cost = base * duration_months * team_size
        infrastructure_cost = (50 + (team_size * 20)) * duration_months
        tools_licenses = 100 * duration_months
        contingency = (development_cost + infrastructure_cost + tools_licenses) * 0.2
        
        total = development_cost + infrastructure_cost + tools_licenses + contingency
        
        return {
            "total_budget": round(total, 2),
            "breakdown": {
                "development": round(development_cost, 2),
                "infrastructure": round(infrastructure_cost, 2),
                "tools_and_licenses": round(tools_licenses, 2),
                "contingency_20_percent": round(contingency, 2)
            },
            "monthly_burn_rate": round(total / duration_months, 2),
            "per_person_cost": round(total / team_size, 2) if team_size > 0 else 0
        }


class SkillAssessmentTool:
    """Custom tool to assess skill gaps and provide recommendations"""
    
    @staticmethod
    def assess_skills(current_skills: List[str], required_skills: List[str]) -> Dict[str, Any]:
        """Assess skill gaps and provide learning recommendations"""
        
        current_set = set(skill.lower().strip() for skill in current_skills)
        required_set = set(skill.lower().strip() for skill in required_skills)
        
        matched_skills = current_set.intersection(required_set)
        missing_skills = required_set - current_set
        extra_skills = current_set - required_set
        
        # Calculate proficiency score
        if required_set:
            proficiency_score = (len(matched_skills) / len(required_set)) * 100
        else:
            proficiency_score = 100
        
        # Determine difficulty level
        if proficiency_score >= 80:
            difficulty = "Easy - You have most required skills"
        elif proficiency_score >= 50:
            difficulty = "Moderate - Some learning required"
        else:
            difficulty = "Challenging - Significant skill development needed"
        
        # Learning time estimation (weeks)
        learning_time = len(missing_skills) * 3  # 3 weeks per skill (average)
        
        return {
            "proficiency_score": round(proficiency_score, 2),
            "difficulty_level": difficulty,
            "matched_skills": list(matched_skills),
            "missing_skills": list(missing_skills),
            "additional_skills": list(extra_skills),
            "estimated_learning_time_weeks": learning_time,
            "recommendation": "Ready to start!" if proficiency_score >= 70 
                           else "Complete skill development first" if proficiency_score < 40
                           else "Start with tutorials alongside development"
        }


class GitHubSearchTool:
    """Custom tool to search GitHub for similar projects"""
    
    @staticmethod
    def search_similar_projects(query: str, max_results: int = 5) -> Dict[str, Any]:
        """Search GitHub for similar projects"""
        
        try:
            # GitHub API search
            url = "https://api.github.com/search/repositories"
            params = {
                "q": query,
                "sort": "stars",
                "order": "desc",
                "per_page": max_results
            }
            
            headers = {
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "ProjectIdeasAgent"
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                projects = []
                
                for item in data.get("items", [])[:max_results]:
                    projects.append({
                        "name": item.get("name"),
                        "description": item.get("description", "No description"),
                        "stars": item.get("stargazers_count", 0),
                        "language": item.get("language", "Not specified"),
                        "url": item.get("html_url"),
                        "last_updated": item.get("updated_at", "Unknown")
                    })
                
                return {
                    "success": True,
                    "total_found": data.get("total_count", 0),
                    "projects": projects,
                    "message": f"Found {len(projects)} similar projects on GitHub"
                }
            else:
                return {
                    "success": False,
                    "projects": [],
                    "message": f"GitHub API error: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "projects": [],
                "message": f"Error searching GitHub: {str(e)}"
            }


class WebSearchTool:
    """Built-in tool wrapper for web search capabilities"""
    
    @staticmethod
    def search_tech_trends(query: str) -> str:
        """Search for latest tech trends (simulated - integrate with real API)"""
        
        # In production, integrate with actual search API
        # For now, using Gemini to provide trend insights
        model = genai.GenerativeModel(model_name="models/gemini-2.5-flash")
        
        prompt = f"""
        Provide the latest trends and insights about: {query}
        
        Focus on:
        1. Current industry trends (2024-2025)
        2. Popular technologies and frameworks
        3. Best practices
        4. Emerging patterns
        5. Market demand
        
        Keep it concise and actionable.
        """
        
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Unable to fetch trends: {str(e)}"


class SessionManager:
    """Improved session management with timestamps and history"""
    
    @staticmethod
    def get_or_create_session(session_id: str) -> Dict[str, Any]:
        """Get existing session or create new one"""
        
        if session_id not in SESSION_STORE:
            SESSION_STORE[session_id] = {
                "id": session_id,
                "created_at": datetime.now().isoformat(),
                "last_accessed": datetime.now().isoformat(),
                "conversation_history": [],
                "generated_ideas": [],
                "roadmaps": [],
                "feasibility_assessments": []
            }
        
        SESSION_STORE[session_id]["last_accessed"] = datetime.now().isoformat()
        return SESSION_STORE[session_id]
    
    @staticmethod
    def add_to_history(session_id: str, action: str, data: Dict[str, Any], result: str):
        """Add interaction to session history"""
        
        session_data = SessionManager.get_or_create_session(session_id)
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "input": data,
            "output": result[:500]  # Store first 500 chars
        }
        
        session_data["conversation_history"].append(entry)
        
        # Store in specific categories
        if action == "generate_ideas":
            session_data["generated_ideas"].append(entry)
        elif action == "create_roadmap":
            session_data["roadmaps"].append(entry)
        elif action == "assess_feasibility":
            session_data["feasibility_assessments"].append(entry)
    
    @staticmethod
    def get_conversation_summary(session_id: str) -> str:
        """Get summarized conversation history"""
        
        session_data = SessionManager.get_or_create_session(session_id)
        history = session_data["conversation_history"]
        
        if not history:
            return "No conversation history yet."
        
        summary = f"Session Summary (Total interactions: {len(history)})\n\n"
        summary += f"Ideas Generated: {len(session_data['generated_ideas'])}\n"
        summary += f"Roadmaps Created: {len(session_data['roadmaps'])}\n"
        summary += f"Feasibility Assessments: {len(session_data['feasibility_assessments'])}\n"
        
        return summary


class UserPreferenceManager:
    """Manage user preferences"""
    
    @staticmethod
    def set_preference(user_id: str, key: str, value: Any):
        """Set user preference"""
        if user_id not in USER_PREFERENCES:
            USER_PREFERENCES[user_id] = {}
        USER_PREFERENCES[user_id][key] = value
    
    @staticmethod
    def get_preference(user_id: str, key: str, default: Any = None) -> Any:
        """Get user preference"""
        return USER_PREFERENCES.get(user_id, {}).get(key, default)
    
    @staticmethod
    def get_all_preferences(user_id: str) -> Dict[str, Any]:
        """Get all user preferences"""
        return USER_PREFERENCES.get(user_id, {})


class EnhancedProjectIdeasAgent:
    """Enhanced AI Agent with tools and improved memory"""
    
    def __init__(self):
        self.model = genai.GenerativeModel(model_name="models/gemini-2.5-flash")
        self.budget_tool = BudgetCalculatorTool()
        self.skill_tool = SkillAssessmentTool()
        self.github_tool = GitHubSearchTool()
        self.search_tool = WebSearchTool()
    
    def generate_project_ideas(self, domain: str, skill_level: str, 
                              constraints: str = "", use_trends: bool = True) -> str:
        """Generate project ideas with optional trend research"""
        
        trend_info = ""
        if use_trends:
            print(f"Searching for latest trends in {domain}...")
            trend_info = self.search_tool.search_tech_trends(f"{domain} project ideas trends 2024-2025")
            trend_context = f"\n\nLatest Trends:\n{trend_info}\n"
        else:
            trend_context = ""
        
        prompt = f"""
        Generate 5 innovative project ideas for the following specifications:
        
        Domain: {domain}
        Skill Level: {skill_level}
        Additional Constraints: {constraints if constraints else "None"}
        {trend_context}
        
        For each project idea, provide:
        1. Project Name
        2. Brief Description (2-3 sentences)
        3. Key Technologies Required
        4. Estimated Timeline
        5. Learning Outcomes
        
        Consider current trends and practical implementation.
        Format the response in a clear, structured way.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating project ideas: {str(e)}"
    
    def create_roadmap(self, project_description: str, 
                      check_similar: bool = True) -> Dict[str, Any]:
        """Create roadmap with optional GitHub research"""
        
        github_results = {}
        if check_similar:
            print("Searching GitHub for similar projects...")
            # Extract key terms from description for search
            search_query = " ".join(project_description.split()[:5])
            github_results = self.github_tool.search_similar_projects(search_query)
        
        similar_projects_context = ""
        if github_results.get("success") and github_results.get("projects"):
            similar_projects_context = "\n\nSimilar Projects Found on GitHub:\n"
            for proj in github_results["projects"][:3]:
                similar_projects_context += f"- {proj['name']}: {proj['description']} (⭐ {proj['stars']})\n"
        
        prompt = f"""
        Create a comprehensive project roadmap for the following project:
        
        Project: {project_description}
        {similar_projects_context}
        
        Provide:
        1. Project Overview
        2. Prerequisites and Setup
        3. Phase-by-phase breakdown with:
           - Phase name
           - Duration estimate
           - Key tasks and deliverables
           - Technologies/tools to learn
           - Success criteria
        4. Testing and Deployment strategy
        5. Potential challenges and solutions
        6. Resources for learning
        
        {f"Consider insights from similar projects above." if similar_projects_context else ""}
        Make the roadmap practical and actionable.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return {
                "roadmap": response.text,
                "similar_projects": github_results.get("projects", [])
            }
        except Exception as e:
            return {
                "roadmap": f"Error creating roadmap: {str(e)}",
                "similar_projects": []
            }
    
    def assess_feasibility(self, project_description: str, available_time: str, 
                          current_skills: str, budget: str = "Limited",
                          project_type: str = "web_development") -> Dict[str, Any]:
        """Assess feasibility with custom tools"""
        
        # Parse skills
        current_skills_list = [s.strip() for s in current_skills.split(",")]
        
        # Extract required skills from project description (simplified)
        # In production, use NLP or let LLM extract this
        common_skills = ["python", "javascript", "react", "node.js", "sql", 
                        "html", "css", "git", "api", "docker"]
        required_skills_list = [s for s in common_skills 
                               if s in project_description.lower()]
        
        # Use skill assessment tool
        skill_assessment = self.skill_tool.assess_skills(
            current_skills_list, 
            required_skills_list if required_skills_list else ["programming"]
        )
        
        # Extract duration in months
        duration_match = re.search(r'(\d+)\s*(month|mo)', available_time.lower())
        duration_months = int(duration_match.group(1)) if duration_match else 3
        
        # Calculate budget
        budget_calc = self.budget_tool.calculate_budget(
            project_type, 
            duration_months, 
            team_size=1
        )
        
        prompt = f"""
        Assess the feasibility of the following project:
        
        Project Description: {project_description}
        Available Time: {available_time}
        Current Skills: {current_skills}
        Budget: {budget}
        
        Skill Assessment Results:
        - Proficiency Score: {skill_assessment['proficiency_score']}%
        - Difficulty Level: {skill_assessment['difficulty_level']}
        - Missing Skills: {', '.join(skill_assessment['missing_skills'])}
        - Learning Time Needed: {skill_assessment['estimated_learning_time_weeks']} weeks
        
        Budget Estimation:
        - Estimated Total Budget: ${budget_calc['total_budget']}
        - Monthly Burn Rate: ${budget_calc['monthly_burn_rate']}
        - Development Cost: ${budget_calc['breakdown']['development']}
        
        Provide a detailed feasibility analysis including on different lines:
        
        1. Feasibility Score (1-10 scale with justification)
        2. Technical Feasibility (considering skill assessment above)
        3. Time Feasibility (realistic timeline)
        4. Resource Feasibility (budget analysis)
        5. Risk Analysis
        6. Recommendations
        
        Be honest and practical in your assessment. Use proper formatting while explaining each point mentioned above.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return {
                "assessment": response.text,
                "skill_analysis": skill_assessment,
                "budget_analysis": budget_calc
            }
        except Exception as e:
            return {
                "assessment": f"Error assessing feasibility: {str(e)}",
                "skill_analysis": skill_assessment,
                "budget_analysis": budget_calc
            }


# Initialize enhanced agent
agent = EnhancedProjectIdeasAgent()

# ===== AUTHENTICATION ROUTES =====

@app.route('/')
def login_page():
    """Render the login page"""
    # Check if already logged in
    if session.get('logged_in'):
        return redirect('/dashboard')
    
    return render_template('login.html')


@app.route('/signup', methods=['GET'])
def signup_page():
    """Render the sign-up page"""
    if session.get('logged_in'):
        return redirect('/dashboard')
    
    return render_template('signup.html')


@app.route('/api/signup', methods=['POST'])
def signup():
    """Handle user sign-up with email verification"""
    data = request.get_json(force=True)
    
    email = data.get('email', '').strip().lower()
    name = data.get('name', '').strip()
    password = data.get('password', '').strip()
    confirm_password = data.get('confirm_password', '').strip()
    
    # Validate inputs
    if not all([email, name, password, confirm_password]):
        return jsonify({'success': False, 'message': 'All fields are required'}), 400
    
    # Validate email format
    try:
        validate_email(email)
    except EmailNotValidError as e:
        return jsonify({'success': False, 'message': f'Invalid email: {str(e)}'}), 400
    
    # Validate name length
    if len(name) < 2 or len(name) > 100:
        return jsonify({'success': False, 'message': 'Name must be between 2 and 100 characters'}), 400
    
    # Validate password length
    if len(password) < 6:
        return jsonify({'success': False, 'message': 'Password must be at least 6 characters'}), 400
    
    # Check password match
    if password != confirm_password:
        return jsonify({'success': False, 'message': 'Passwords do not match'}), 400
    
    # Check if email already exists
    existing_user = db.get_user_by_email(email)
    if existing_user:
        return jsonify({'success': False, 'message': 'Email already registered. Please login or use a different email'}), 409
    
    # Hash password
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Create user
    user_result = db.create_user(email, name, password_hash)
    
    if not user_result['success']:
        return jsonify({'success': False, 'message': user_result['message']}), 409
    
    # Generate and send verification code
    code = email_service.generate_verification_code()
    expires_at = email_service.get_expiration_time(minutes=10)
    
    code_stored = db.create_verification_code(email, code, expires_at)
    
    if not code_stored:
        return jsonify({'success': False, 'message': 'Failed to create verification code'}), 500
    
    # Send verification email
    email_sent = email_service.send_verification_email(email, name, code)
    
    if not email_sent:
        print(f"⚠️ Warning: Verification email not sent to {email}, but code was generated: {code}")
    
    return jsonify({
        'success': True,
        'message': 'Sign-up successful! Please check your email for the verification code.',
        'email': email,
        'user_name': name
    }), 201


@app.route('/api/verify-email', methods=['POST'])
def verify_email():
    """Verify email with the code sent to user"""
    data = request.get_json(force=True)
    
    email = data.get('email', '').strip().lower()
    code = data.get('code', '').strip()
    
    # Validate inputs
    if not email or not code:
        return jsonify({'success': False, 'message': 'Email and verification code are required'}), 400
    
    # Check if user exists
    user = db.get_user_by_email(email)
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    
    # Verify code
    code_valid = db.verify_code(email, code)
    
    if not code_valid:
        return jsonify({'success': False, 'message': 'Invalid or expired verification code'}), 400
    
    # Mark email as verified
    verified = db.verify_user_email(email)
    
    if not verified:
        return jsonify({'success': False, 'message': 'Failed to verify email'}), 500
    
    # Send welcome email
    email_service.send_welcome_email(email, user['name'])
    
    return jsonify({
        'success': True,
        'message': 'Email verified successfully! You can now login.',
        'email': email
    }), 200


@app.route('/api/resend-code', methods=['POST'])
def resend_code():
    """Resend verification code to email"""
    data = request.get_json(force=True)
    email = data.get('email', '').strip().lower()
    
    if not email:
        return jsonify({'success': False, 'message': 'Email is required'}), 400
    
    user = db.get_user_by_email(email)
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    
    if user['is_verified']:
        return jsonify({'success': False, 'message': 'Email is already verified'}), 400
    
    # Generate new verification code
    code = email_service.generate_verification_code()
    expires_at = email_service.get_expiration_time(minutes=10)
    
    db.create_verification_code(email, code, expires_at)
    email_service.send_verification_email(email, user['name'], code)
    
    return jsonify({
        'success': True,
        'message': 'Verification code resent to your email'
    }), 200


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle login request with JWT authentication"""
    # If GET request, render the login page
    if request.method == 'GET':
        if session.get('logged_in'):
            return redirect('/dashboard')
        return render_template('login.html')
    
    # Handle POST request for login
    data = request.get_json(force=True)
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    # Validate input
    if not email or not password:
        return jsonify({'success': False, 'message': 'Email and password are required'}), 400
    
    # Check if user exists
    user = db.get_user_by_email(email)
    if not user:
        print(f"⚠️ Failed login attempt - user not found: {email}")
        return jsonify({'success': False, 'message': 'Invalid email or password'}), 401
    
    # Check if email is verified
    if not user['is_verified']:
        return jsonify({
            'success': False,
            'message': 'Please verify your email first',
            'redirect': '/verify-email',
            'email': email
        }), 403
    
    # Verify password
    if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
        print(f"⚠️ Failed login attempt - wrong password for: {email}")
        return jsonify({'success': False, 'message': 'Invalid email or password'}), 401
    
    # Generate JWT token
    token = generate_jwt_token(email)
    
    # Initialize session
    if 'session_id' not in session:
        session['session_id'] = secrets.token_hex(16)
        session['user_id'] = str(user['id'])
    
    session['email'] = email
    session['name'] = user['name']
    session['logged_in'] = True
    SessionManager.get_or_create_session(session['session_id'])
    
    print(f"✅ Successful login for user: {email}")
    
    return jsonify({
        'success': True,
        'message': 'Login successful',
        'redirect': '/dashboard',
        'email': email,
        'name': user['name'],
        'token': token
    }), 200


@app.route('/verify-email', methods=['GET'])
def verify_email_page():
    """Render email verification page"""
    if session.get('logged_in'):
        return redirect('/dashboard')
    
    return render_template('verify_email.html')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    """Logout user"""
    session.clear()
    return redirect('/')

@app.route('/login_old', methods=['POST'])
def login_old():
    """Handle login request with JWT authentication (OLD HARDCODED VERSION - DEPRECATED)"""
    data = request.get_json(force=True)
    username = data.get('username', '').strip()
    password = data.get('password', '')

    
    # Validate input
    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password are required'}), 400
    
    # Simple validation - In production, use a database with hashed passwords
    # This is a demo setup with basic credentials
    valid_users = {
        'admin': 'admin@865',
        'demo': 'demo@123',
        'user': 'password123'
    }
    
    # Check if user exists and password is correct
    if username not in valid_users or valid_users[username] != password:
        print(f"⚠️ Failed login attempt for user: {username}")
        return jsonify({'success': False, 'message': 'Invalid username or password'}), 401
    
    # Generate JWT token
    token = generate_jwt_token(username)
    
    # Initialize session
    if 'session_id' not in session:
        session['session_id'] = secrets.token_hex(16)
        session['user_id'] = secrets.token_hex(8)
    
    session['username'] = username
    SessionManager.get_or_create_session(session['session_id'])
    
    print(f"✅ Successful login for user: {username}")
    
    return jsonify({
        'success': True, 
        'message': 'Login successful (OLD DEPRECATED)',
        'redirect': '/dashboard',
        'username': username,
        'token': token
    })

@app.route('/dashboard', methods=['GET'])
def index():
    """Render the main dashboard page"""
    # Check if logged in (session-based check)
    if not session.get('logged_in'):
        return redirect('/')
    
    # Initialize session if needed
    if 'session_id' not in session:
        session['session_id'] = secrets.token_hex(16)
        session['user_id'] = secrets.token_hex(8)
    
    SessionManager.get_or_create_session(session['session_id'])
    return render_template('index.html')

@app.route('/logout_old', methods=['POST'])
def logout_old():
    """Handle logout request (OLD VERSION - DEPRECATED)"""
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully', 'redirect': '/'})

@app.route('/generate_ideas', methods=['POST'])
@token_required
def generate_ideas():
    """API endpoint for generating project ideas"""
    # Check login
    if not session.get('logged_in'):
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json(force=True)
    domain = data.get('domain', '')
    skill_level = data.get('skill_level', '')
    constraints = data.get('constraints', '')
    use_trends = data.get('use_trends', True)
    
    result = agent.generate_project_ideas(domain, skill_level, constraints, use_trends)
    
    # Store in session
    SessionManager.add_to_history(
        session['session_id'],
        'generate_ideas',
        {'domain': domain, 'skill_level': skill_level},
        result
    )
    
    return jsonify({'result': result})

@app.route('/create_roadmap', methods=['POST'])
@token_required
def create_roadmap():
    """API endpoint for creating project roadmap"""
    # Check login
    if not session.get('logged_in'):
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json(force=True)
    project_description = data.get('project_description', '')
    check_similar = data.get('check_similar', True)
    
    result = agent.create_roadmap(project_description, check_similar)
    
    # Store in session
    SessionManager.add_to_history(
        session['session_id'],
        'create_roadmap',
        {'project': project_description},
        result['roadmap']
    )
    
    return jsonify(result)

@app.route('/assess_feasibility', methods=['POST'])
@token_required
def assess_feasibility():
    """API endpoint for assessing project feasibility"""
    # Check login
    if not session.get('logged_in'):
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json(force=True)
    project_description = data.get('project_description', '')
    available_time = data.get('available_time', '')
    current_skills = data.get('current_skills', '')
    budget = data.get('budget', 'Limited')
    project_type = data.get('project_type', 'web_development')
    
    result = agent.assess_feasibility(
        project_description, available_time, 
        current_skills, budget, project_type
    )
    
    # Store in session
    SessionManager.add_to_history(
        session['session_id'],
        'assess_feasibility',
        {'project': project_description, 'time': available_time},
        result['assessment']
    )
    
    return jsonify(result)

@app.route('/session_summary', methods=['GET'])
def get_session_summary():
    """Get conversation summary for current session"""
    summary = SessionManager.get_conversation_summary(session.get('session_id', ''))
    session_data = SessionManager.get_or_create_session(session.get('session_id', ''))
    
    return jsonify({
        'summary': summary,
        'total_interactions': len(session_data['conversation_history']),
        'history': session_data['conversation_history'][-10:]  # Last 10 interactions
    })

@app.route('/preferences', methods=['GET', 'POST'])
def manage_preferences():
    """Manage user preferences"""
    user_id = session.get('user_id', 'default')
    
    if request.method == 'POST':
        prefs = request.json
        for key, value in prefs.items():
            UserPreferenceManager.set_preference(user_id, key, value)
        return jsonify({'success': True, 'message': 'Preferences saved'})
    else:
        prefs = UserPreferenceManager.get_all_preferences(user_id)
        return jsonify({'preferences': prefs})

@app.route('/tools/github_search', methods=['POST'])
@token_required
def search_github():
    """Direct GitHub search tool endpoint"""
    data = request.get_json(force=True)
    query = data.get('query', '')
    max_results = data.get('max_results', 5)
    
    result = agent.github_tool.search_similar_projects(query, max_results)
    return jsonify(result)

@app.route('/tools/budget_calculator', methods=['POST'])
@token_required
def calculate_budget():
    """Direct budget calculator tool endpoint"""
    data = request.get_json(force=True)
    project_type = data.get('project_type', 'web_development')
    duration = data.get('duration_months', 3)
    team_size = data.get('team_size', 1)
    
    result = agent.budget_tool.calculate_budget(project_type, duration, team_size)
    return jsonify(result)

@app.route('/tools/skill_assessment', methods=['POST'])
@token_required
def assess_skills():
    """Direct skill assessment tool endpoint"""
    data = request.get_json(force=True)
    current_skills = data.get('current_skills', [])
    required_skills = data.get('required_skills', [])
    
    result = agent.skill_tool.assess_skills(current_skills, required_skills)
    return jsonify(result)

@app.route('/history')
def history_page():
    """Render the history page"""
    return render_template('history.html')

@app.route('/api/full_history', methods=['GET'])
@token_required
def get_full_history():
    """Get complete session history with all details"""
    session_id = session.get('session_id', '')
    session_data = SessionManager.get_or_create_session(session_id)
    
    return jsonify({
        'session_id': session_data['id'],
        'created_at': session_data['created_at'],
        'last_accessed': session_data['last_accessed'],
        'total_interactions': len(session_data['conversation_history']),
        'statistics': {
            'ideas_generated': len(session_data['generated_ideas']),
            'roadmaps_created': len(session_data['roadmaps']),
            'feasibility_assessments': len(session_data['feasibility_assessments'])
        },
        'conversation_history': session_data['conversation_history']
    })

@app.route('/api/clear_history', methods=['POST'])
@token_required
def clear_history():
    """Clear session history"""
    session_id = session.get('session_id', '')
    if session_id in SESSION_STORE:
        SESSION_STORE[session_id]['conversation_history'] = []
        SESSION_STORE[session_id]['generated_ideas'] = []
        SESSION_STORE[session_id]['roadmaps'] = []
        SESSION_STORE[session_id]['feasibility_assessments'] = []
    return jsonify({'success': True, 'message': 'History cleared'})


# ==================== PROJECT TRACKER ENDPOINTS ====================

@app.route('/api/projects', methods=['GET'])
@token_required
def get_projects():
    """Get all projects for current user"""
    user_id = session.get('user_id', 'default')
    
    if user_id not in PROJECTS_STORE:
        return jsonify({'success': True, 'projects': []})
    
    projects = list(PROJECTS_STORE[user_id].values())
    return jsonify({'success': True, 'projects': projects})


@app.route('/api/projects', methods=['POST'])
@token_required
def create_project():
    """Create a new project"""
    user_id = session.get('user_id', 'default')
    data = request.get_json(force=True)
    
    # Initialize user storage if needed
    if user_id not in PROJECTS_STORE:
        PROJECTS_STORE[user_id] = {}
        PROJECT_ID_COUNTER[user_id] = 0
    
    # Generate project ID
    PROJECT_ID_COUNTER[user_id] += 1
    project_id = PROJECT_ID_COUNTER[user_id]
    
    # Create project object
    project = {
        'id': project_id,
        'project_name': data.get('project_name', 'Untitled Project'),
        'description': data.get('description', ''),
        'domain': data.get('domain', ''),
        'skill_level': data.get('skill_level', 'Beginner'),
        'available_time': data.get('available_time', ''),
        'budget': data.get('budget', 'Limited'),
        'status': 'planning',
        'created_at': datetime.utcnow().isoformat(),
        'progress_percentage': 0,
        'current_phase': 'Planning',
        'milestones': [
            {'id': 1, 'milestone_name': 'Project Setup', 'description': 'Set up development environment', 'status': 'pending'},
            {'id': 2, 'milestone_name': 'Requirements', 'description': 'Define project requirements', 'status': 'pending'},
            {'id': 3, 'milestone_name': 'Development', 'description': 'Build core features', 'status': 'pending'},
            {'id': 4, 'milestone_name': 'Testing', 'description': 'Test and fix bugs', 'status': 'pending'},
            {'id': 5, 'milestone_name': 'Deployment', 'description': 'Deploy to production', 'status': 'pending'}
        ],
        'analyses': [{
            'id': 1,
            'feasibility_score': 7,
            'analysis_data': {
                'feasibility_score': 7,
                'difficulty': 'Medium',
                'estimated_weeks': 12
            },
            'next_step': 'Start by setting up your development environment and creating a project roadmap.',
            'created_at': datetime.utcnow().isoformat()
        }]
    }
    
    # AI Analysis - Generate feasibility assessment
    try:
        feasibility_result = agent.assess_feasibility(
            data.get('description', ''),
            data.get('available_time', ''),
            '',
            data.get('budget', 'Limited'),
            'web_development'
        )
        
        if feasibility_result and 'skill_analysis' in feasibility_result:
            skill_analysis = feasibility_result['skill_analysis']
            project['analyses'][0]['feasibility_score'] = min(10, int(skill_analysis.get('proficiency_score', 70) / 10))
            project['analyses'][0]['analysis_data'] = skill_analysis
            project['analyses'][0]['next_step'] = feasibility_result.get('assessment', 'Start working on your project.')
    except Exception as e:
        print(f"Analysis error: {str(e)}")
    
    # Store project
    PROJECTS_STORE[user_id][project_id] = project
    
    return jsonify({
        'success': True,
        'project_id': project_id,
        'message': 'Project created and analyzed successfully!'
    })


@app.route('/api/projects/<int:project_id>', methods=['GET'])
@token_required
def get_project_details(project_id):
    """Get detailed information about a specific project"""
    user_id = session.get('user_id', 'default')
    
    if user_id not in PROJECTS_STORE or project_id not in PROJECTS_STORE[user_id]:
        return jsonify({'error': 'Project not found'}), 404
    
    project = PROJECTS_STORE[user_id][project_id]
    
    # Calculate statistics
    completed_milestones = sum(1 for m in project['milestones'] if m['status'] == 'completed')
    total_milestones = len(project['milestones'])
    progress = int((completed_milestones / total_milestones * 100) if total_milestones > 0 else 0)
    
    project['progress_percentage'] = progress
    
    return jsonify({
        'success': True,
        'project': project,
        'analyses': project.get('analyses', []),
        'milestones': project.get('milestones', []),
        'progress': {
            'progress_percentage': progress,
            'completed_milestones': completed_milestones,
            'total_milestones': total_milestones,
            'current_phase': project.get('current_phase', 'Planning')
        }
    })


@app.route('/api/projects/<int:project_id>', methods=['PUT'])
@token_required
def update_project(project_id):
    """Update project status and information"""
    user_id = session.get('user_id', 'default')
    data = request.get_json(force=True)
    
    if user_id not in PROJECTS_STORE or project_id not in PROJECTS_STORE[user_id]:
        return jsonify({'error': 'Project not found'}), 404
    
    project = PROJECTS_STORE[user_id][project_id]
    
    # Update allowed fields
    if 'status' in data:
        project['status'] = data['status']
    if 'current_phase' in data:
        project['current_phase'] = data['current_phase']
    
    return jsonify({'success': True, 'message': 'Project updated'})


@app.route('/api/projects/<int:project_id>', methods=['DELETE'])
@token_required
def delete_project(project_id):
    """Delete a project"""
    user_id = session.get('user_id', 'default')
    
    if user_id not in PROJECTS_STORE or project_id not in PROJECTS_STORE[user_id]:
        return jsonify({'error': 'Project not found'}), 404
    
    del PROJECTS_STORE[user_id][project_id]
    
    return jsonify({'success': True, 'message': 'Project deleted'})


@app.route('/api/projects/<int:project_id>/milestones/<int:milestone_id>', methods=['PUT'])
@token_required
def update_milestone(project_id, milestone_id):
    """Update milestone status"""
    user_id = session.get('user_id', 'default')
    data = request.get_json(force=True)
    
    if user_id not in PROJECTS_STORE or project_id not in PROJECTS_STORE[user_id]:
        return jsonify({'error': 'Project not found'}), 404
    
    project = PROJECTS_STORE[user_id][project_id]
    
    # Find and update milestone
    for milestone in project.get('milestones', []):
        if milestone['id'] == milestone_id:
            milestone['status'] = data.get('status', 'pending')
            break
    
    # Calculate progress
    completed = sum(1 for m in project['milestones'] if m['status'] == 'completed')
    total = len(project['milestones'])
    project['progress_percentage'] = int((completed / total * 100) if total > 0 else 0)
    
    # Update phase
    if completed == total:
        project['current_phase'] = 'Completed'
        project['status'] = 'completed'
    elif completed > 0:
        project['current_phase'] = f'Phase {min(5, completed + 1)}'
        project['status'] = 'in_progress'
    
    return jsonify({'success': True, 'message': 'Milestone updated', 'progress': project['progress_percentage']})


@app.route('/api/statistics', methods=['GET'])
@token_required
def get_statistics():
    """Get project statistics for current user"""
    user_id = session.get('user_id', 'default')
    
    if user_id not in PROJECTS_STORE:
        return jsonify({
            'total_projects': 0,
            'in_progress': 0,
            'completed': 0,
            'completed_milestones': 0
        })
    
    projects = PROJECTS_STORE[user_id].values()
    
    total_projects = len(projects)
    in_progress = sum(1 for p in projects if p['status'] == 'in_progress')
    completed = sum(1 for p in projects if p['status'] == 'completed')
    completed_milestones = sum(
        sum(1 for m in p['milestones'] if m['status'] == 'completed')
        for p in projects
    )
    
    return jsonify({
        'total_projects': total_projects,
        'in_progress': in_progress,
        'completed': completed,
        'completed_milestones': completed_milestones
    })

if __name__ == '__main__':
    print("🚀 Projura Starting...")
    print(" Features Loaded:")
    print("   ✅ Google Search (Tech Trends)")
    print("   ✅ GitHub Project Search")
    print("   ✅ Budget Calculator")
    print("   ✅ Skill Assessment")
    print("   ✅ Session Management")
    print("   ✅ User Preferences")
    print("   ✅ Project Tracker")
    print("\n🌐 Server running on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)