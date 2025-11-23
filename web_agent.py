"""
Enhanced Web UI for Project Ideas AI Agent using Flask
With Built-in Tools, Custom Tools, and Improved Memory
"""

from flask import Flask, render_template, request, jsonify, session
import os
from dotenv import load_dotenv
import google.generativeai as genai
import secrets
import requests
from datetime import datetime
import json
from typing import Dict, List, Any
import re

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Configure Gemini API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

# In-memory storage for sessions (use database in production)
SESSION_STORE = {}
USER_PREFERENCES = {}


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
        model = genai.GenerativeModel(
    model_name="models/gemini-2.5-flash"
)
        
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
            print(f"🔍 Searching for latest trends in {domain}...")
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
            print("🔍 Searching GitHub for similar projects...")
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
        
        Provide a detailed feasibility analysis including:
        
        1. Feasibility Score (1-10 scale with justification)
        2. Technical Feasibility (considering skill assessment above)
        3. Time Feasibility (realistic timeline)
        4. Resource Feasibility (budget analysis)
        5. Risk Analysis
        6. Recommendations
        
        Be honest and practical in your assessment.
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

@app.route('/')
def index():
    """Render the main page"""
    # Initialize session
    if 'session_id' not in session:
        session['session_id'] = secrets.token_hex(16)
        session['user_id'] = secrets.token_hex(8)
    
    SessionManager.get_or_create_session(session['session_id'])
    return render_template('index.html')

@app.route('/generate_ideas', methods=['POST'])
def generate_ideas():
    """API endpoint for generating project ideas"""
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
def create_roadmap():
    """API endpoint for creating project roadmap"""
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
def assess_feasibility():
    """API endpoint for assessing project feasibility"""
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
        prefs = request.get_json(force=True)
        for key, value in prefs.items():
            UserPreferenceManager.set_preference(user_id, key, value)
        return jsonify({'success': True, 'message': 'Preferences saved'})
    else:
        prefs = UserPreferenceManager.get_all_preferences(user_id)
        return jsonify({'preferences': prefs})

@app.route('/tools/github_search', methods=['POST'])
def search_github():
    """Direct GitHub search tool endpoint"""
    data = request.get_json(force=True)
    query = data.get('query', '')
    max_results = data.get('max_results', 5)
    
    result = agent.github_tool.search_similar_projects(query, max_results)
    return jsonify(result)

@app.route('/tools/budget_calculator', methods=['POST'])
def calculate_budget():
    """Direct budget calculator tool endpoint"""
    data = request.get_json(force=True)
    project_type = data.get('project_type', 'web_development')
    duration = data.get('duration_months', 3)
    team_size = data.get('team_size', 1)
    
    result = agent.budget_tool.calculate_budget(project_type, duration, team_size)
    return jsonify(result)

@app.route('/tools/skill_assessment', methods=['POST'])
def assess_skills():
    """Direct skill assessment tool endpoint"""
    data = request.get_json(force=True)
    current_skills = data.get('current_skills', [])
    required_skills = data.get('required_skills', [])
    
    result = agent.skill_tool.assess_skills(current_skills, required_skills)
    return jsonify(result)

if __name__ == '__main__':
    print("🚀 Enhanced Project Ideas AI Agent Starting...")
    print("📦 Features Loaded:")
    print("   ✅ Google Search (Tech Trends)")
    print("   ✅ GitHub Project Search")
    print("   ✅ Budget Calculator")
    print("   ✅ Skill Assessment")
    print("   ✅ Session Management")
    print("   ✅ User Preferences")
    print("\n🌐 Server running on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
