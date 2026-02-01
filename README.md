# Projura Project Ideas AI Agent 🚀

An intelligent AI agent powered by Google's Gemini API with **built-in tools**, **custom tools**, **advanced memory management**, and **secure email authentication** that helps you:
- 🎯 Generate innovative project ideas with real-time trend research
- 🗺️ Create detailed roadmaps with GitHub project analysis
- ✅ Assess project feasibility with skill assessment and budget calculation
- 💾 Track your session history with timestamps
- 🛠️ Use standalone tools for quick calculations
- 🔐 Secure registration and email-verified authentication system

## 🌟 Key Features

### Authentication System (🔐 NEW!)
- **Email Registration**: Secure signup with name, email, and password
- **Email Verification**: Automatic 6-digit verification code sent via email
- **Secure Login**: Password hashing with bcrypt
- **JWT Token Management**: Secure session management with JWT tokens
- **User Profiles**: Persistent user data storage
- **Session Management**: Remember user login across sessions

### Built-in Tools
- **Web Search / Tech Trends Research**: Automatically searches for latest technology trends when generating ideas
- **Real-time Industry Insights**: Provides current market information and popular technologies

### Custom Tools
- **GitHub Project Search**: Finds similar open-source projects on GitHub
  - View stars, languages, and descriptions
  - Learn from existing implementations
  - Get inspired by successful projects

- **Budget Calculator**: Estimates project costs with detailed breakdown
  - Development costs
  - Infrastructure and hosting
  - Tools and licenses
  - 20% contingency buffer
  - Monthly burn rate calculation

- **Skill Assessment Tool**: Analyzes your skill gaps
  - Proficiency score (0-100%)
  - Matched vs missing skills
  - Estimated learning time
  - Difficulty level assessment
  - Personalized recommendations

### Memory & Session Management
- **Session Tracking**: All interactions are saved with timestamps
- **Conversation History**: View your complete interaction history
- **Persistent Storage**: Database-backed storage with SQLite
- **User Preferences**: Store and retrieve user preferences
- **Conversation Summarization**: Get quick summaries of your sessions
- **Multi-user Support**: Each user has isolated session data

## 📊 Concepts Demonstrated

### Currently Implemented

1. **Agent powered by LLM** 
   - Uses Google's Gemini 2.5 Flash model
   - Intelligent decision-making and content generation

2. **Built-in Tools** 
   - Web Search for tech trends
   - Real-time information retrieval

3. **Custom Tools** 
   - GitHub API integration
   - Budget calculator with cost breakdown
   - Skill assessment algorithm

4. **Sessions & Memory** 
   - Session management with timestamps
   - Conversation history tracking
   - Interaction categorization (ideas, roadmaps, assessments)
   - Persistent database storage

5. **Authentication System** 
   - Email-based user registration
   - Email verification with 6-digit codes
   - Secure password hashing with bcrypt
   - JWT token-based session management
   - Multi-user support with isolated data

6. **Basic Observability** 
   - Interaction counting
   - Session tracking
   - Error handling and logging
   - User activity logging

## Project Structure

```
projura-agent/
├── main.py                    # CLI version of the agent
├── web_agent.py               # Flask web application with auth & tools
├── database.py                # SQLite database management & models
├── email_service.py           # Email sending and verification system
├── jwt_manager.js             # JWT token management (frontend)
├── requirements.txt           # Python dependencies
├── templates/
│   ├── index.html             # Main dashboard (after auth)
│   ├── login.html             # Login page
│   ├── signup.html            # User registration page
│   ├── verify_email.html      # Email verification page
│   └── history.html           # Session history page
├── Flow_Diagram.md            # Authentication flow diagrams
├── README_AUTHENTICATION.md   # Authentication system docs
├── LICENSE                    # MIT License
├── README.md                  # This file
└── __pycache__/               # Python cache directory
```


## 🚀 Quick Start

### 1. Get Google API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key

### 2. Install Dependencies


# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
.\venv\Scripts\activate

# For Powershell Terminal
./venv/Scripts/Activate.ps1

# Install required packages
pip install -r requirements.txt


### 3. Configure API Key

Create a `.env` file in the project root:

```
GOOGLE_API_KEY=your_actual_api_key_here
JWT_SECRET_KEY=your_secret_key_for_jwt_tokens
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

### 4. Run the Application


python web_agent.py


Then open your browser and navigate to:


http://localhost:5000


### 5. First Time Setup

1. **Create Account**: Click "Sign Up" to register
2. **Verify Email**: Enter the verification code sent to your email (check console if using mock mode)
3. **Login**: Use your credentials to login
4. **Access Dashboard**: Start generating ideas, roadmaps, and feasibility assessments


## 💡 Usage Examples

### Authentication Flow

**New User Registration:**
1. Visit `/signup` page
2. Enter name, email, and password
3. System validates inputs and creates account
4. Verification code sent to email
5. Enter code on `/verify-email` page
6. Redirected to login page
7. Login with verified email and password

**Login:**
1. Enter email and password on `/login`
2. JWT token generated upon successful auth
3. Redirected to `/dashboard`
4. Session persists using JWT token

### 1. Generate Project Ideas (with Trend Research)

**Inputs:**
- Domain: AI/ML
- Skill Level: Intermediate
- Constraints: Must use free tools only
- Include latest tech trends

**AI Actions:**
1. 🔍 Searches web for "AI/ML project ideas trends 2024-2025"
2. 🤖 Generates 5 ideas incorporating latest trends
3. 📝 Provides technologies, timelines, and learning outcomes

**Output Example:**
- Project ideas aligned with current AI trends
- Mention of popular frameworks (LangChain, AutoGen, etc.)
- Real-world applications and use cases

### 2. Create Roadmap (with GitHub Research)

**Input:**
- Project: Build a real-time chat application with React and Firebase
- Search for similar projects on GitHub

**AI Actions:**
1. Searches GitHub for "chat application React Firebase"
2. Finds top 5 similar projects with stars and descriptions
3. Creates comprehensive roadmap learning from existing projects

**Output:**
- Similar projects on GitHub (with stars and links)
- Phase-by-phase implementation plan
- Resources and best practices from community

### 3. Assess Feasibility (with Tools)

**Inputs:**
- Project: E-commerce platform with AI recommendations
- Time: 4 months
- Skills: Python, basic web development
- Budget: Limited
- Type: Web Development

**AI Actions:**
1. **Skill Assessment**: Analyzes Python, web dev vs required e-commerce skills
2. **Budget Calculator**: Estimates $2,400-3,000 for 4 months
3. **AI Analysis**: Comprehensive feasibility evaluation

**Output:**
- Proficiency score: 45% (Moderate difficulty)
- Missing skills: Django/Flask, PostgreSQL, Payment APIs, Docker
- Learning time: 15 weeks
- Budget breakdown with monthly burn rate
- Go/No-Go recommendation with reasoning

### 4. Direct Tool Usage

**GitHub Search:**
- Query: "todo app react typescript"
- Results: Top 5 projects with stars, languages, descriptions

**Budget Calculator:**
- Type: Mobile App, Duration: 6 months
- Output: $4,800 total, $800/month burn rate

**Skill Assessment:**
- Current: Python, JavaScript, React
- Required: Python, Django, PostgreSQL, Docker, AWS
- Score: 60%, Missing: Django, PostgreSQL, Docker, AWS

## 🛠️ API Endpoints

All endpoints accept JSON and return JSON responses.

### Authentication Endpoints

**POST `/api/signup`**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "SecurePassword123"
}
```

**POST `/api/verify-email`**
```json
{
  "email": "john@example.com",
  "verification_code": "123456"
}
```

**POST `/api/login`**
```json
{
  "email": "john@example.com",
  "password": "SecurePassword123"
}
```

**POST `/api/resend-verification`**
```json
{
  "email": "john@example.com"
}
```

**GET `/api/user/profile`**
Returns authenticated user's profile information

**POST `/api/logout`**
Logout the current user and invalidate session

### AI Agent Endpoints

**POST `/generate_ideas`**
```json
{
  "domain": "AI/ML",
  "skill_level": "Intermediate",
  "constraints": "Free tools only",
  "use_trends": true
}
```

**POST `/create_roadmap`**
```json
{
  "project_description": "Mobile fitness tracking app",
  "check_similar": true
}
```

**POST `/assess_feasibility`**
```json
{
  "project_description": "Social media platform",
  "available_time": "6 months",
  "current_skills": "Python, Django, React",
  "budget": "Moderate",
  "project_type": "web_development"
}
```

**GET `/session_summary`**
Returns conversation history and statistics for authenticated user

**POST `/preferences`**
Save user preferences
```json
{
  "theme": "dark",
  "notifications": true
}
```

**GET `/preferences`**
Retrieve user preferences

### Tool Endpoints

**POST `/tools/github_search`**
```json
{
  "query": "react typescript",
  "max_results": 5
}
```

**POST `/tools/budget_calculator`**
```json
{
  "project_type": "mobile_app",
  "duration_months": 3,
  "team_size": 1
}
```

**POST `/tools/skill_assessment`**
```json
{
  "current_skills": ["Python", "JavaScript"],
  "required_skills": ["Python", "Django", "PostgreSQL"]
}
```


## 🎯 Advanced Features

### Authentication & Security
- **Email-based Registration**: Simple signup with email verification
- **Password Security**: Bcrypt hashing with salt
- **JWT Tokens**: Stateless authentication with expiration
- **Email Verification**: Time-limited verification codes (10 min default)
- **Session Management**: Secure session tracking per user

### Session Management
- Every interaction is timestamped and associated with user
- Sessions persist in database (not lost on server restart)
- View complete history with filtering and search
- Categorized by action type (ideas, roadmaps, assessments)
- Multi-user isolation - each user sees only their data

### Tool Integration Flow


Authenticated User Request → AI Agent → Tools (if needed) → Enhanced Response → Store in User Session


Example Flow for Feasibility:
1. User (authenticated via JWT) submits feasibility request
2. Agent extracts project requirements
3. Skill Assessment Tool analyzes gaps
4. Budget Calculator estimates costs
5. AI synthesizes all data
6. Comprehensive report generated
7. Interaction saved to user's session history

### Memory System


-- Users table stores account information
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT UNIQUE,
    password_hash TEXT,
    email_verified BOOLEAN,
    created_at TIMESTAMP
)

-- Sessions table stores conversation history per user
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    created_at TIMESTAMP,
    conversation_history JSON,
    generated_ideas JSON,
    roadmaps JSON,
    feasibility_assessments JSON
)

-- Email verification table
CREATE TABLE email_verification (
    id INTEGER PRIMARY KEY,
    email TEXT,
    verification_code TEXT,
    created_at TIMESTAMP,
    expires_at TIMESTAMP,
    is_used BOOLEAN
)



## 💻 Technical Architecture

### System Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                    Projura AI Agent System                     │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌───────────────────────────────────────────────────────┐     │
│  │              User Authentication Layer                │     │
│  │  • Email Registration with verification               │     │
│  │  • Bcrypt Password Hashing                            │     │
│  │  • JWT Token Management                               │     │
│  └───────────────────────────────────────────────────────┘     │
│                           │                                    │
│                           ▼                                    │
│  ┌───────────────────────────────────────────────────────┐     │
│  │               AI Agent Core (Gemini 2.5)              │     │
│  │  • Project Idea Generation                            │     │
│  │  • Roadmap Creation                                   │     │
│  │  • Feasibility Assessment                             │     │
│  └───────────────────────────────────────────────────────┘     │
│          │                   │                   │             │
│          ▼                   ▼                   ▼             │
│  ┌────────────────┐ ┌──────────────┐ ┌──────────────────┐      │
│  │  Built-in      │ │  Custom      │ │  Custom          │      │
│  │  Tools         │ │  Tools       │ │  Tools           │      │
│  │                │ │              │ │                  │      │
│  │ • Web Search   │ │ • GitHub API │ │ • Budget Calc    │      │
│  │ • Tech Trends  │ │   Integration│ │ • Skill Assess   │      │
│  └────────────────┘ └──────────────┘ └──────────────────┘      │
│                                                                │
│  ┌───────────────────────────────────────────────────────┐     │
│  │        Database & Session Management Layer            │     │
│  │  • SQLite Database                                    │     │
│  │  • User Profiles & Sessions                           │     │
│  │  • Conversation History                               │     │
│  │  • Email Verification Codes                           │     │
│  └───────────────────────────────────────────────────────┘     │
│                                                                │
│  ┌───────────────────────────────────────────────────────┐     │
│  │          Flask Web Application Layer                  │     │
│  │  • REST API Endpoints                                 │     │
│  │  • Web Interface (HTML/CSS/JS)                        │     │
│  │  • Email Service Integration                          │     │
│  └───────────────────────────────────────────────────────┘     │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### Data Flow Diagram

```
1. User Registration/Login
   ├─ Email & Password Validation
   ├─ Bcrypt Hash Verification
   ├─ JWT Token Generation
   └─ Session Creation in DB

2. Authenticated Request
   ├─ JWT Token Verification
   ├─ Session Retrieval
   ├─ Route Handling
   └─ User Context Available

3. AI Processing (with Tools)
   ├─ LLM generates response
   ├─ Tools executed (parallel if needed)
   │  ├─ GitHub API call
   │  ├─ Web search
   │  └─ Calculator computations
   ├─ Results aggregated
   └─ Response synthesized

4. Response & Storage
   ├─ Response sent to user
   ├─ Interaction logged
   ├─ Session updated
   └─ History persisted

5. Session History Access
   ├─ User requests /session_summary
   ├─ Retrieve from DB for user
   ├─ Filter & format
   └─ Return to client
```

### Tools Architecture

```
┌─────────────────────────────────────────┐
│           AI Agent (Gemini)             │
│                                         │
│  ┌─────────────────────────────────┐    │
│  │   Gemini 2.5 Flash LLM          │    │
│  └─────────────────────────────────┘    │
│                                         │
│  ┌──────────────┐  ┌──────────────────┐ │
│  │ Built-in     │  │ Custom Tools     │ │
│  │ Tools        │  │                  │ │
│  │              │  │ • GitHub Search  │ │
│  │ • Web Search │  │ • Budget Calc    │ │
│  │ • Trends     │  │ • Skill Assess   │ │
│  └──────────────┘  └──────────────────┘ │
│                                         │
│  ┌─────────────────────────────────┐    │
│  │ Memory & Session Manager        │    │
│  │ • Per-user session tracking     │    │
│  │ • Database persistence          │    │
│  │ • JWT auth integration          │    │
│  └─────────────────────────────────┘    │
│                                         │
└─────────────────────────────────────────┘
```

## 🎓 Learning Outcomes

By examining this project, you'll learn:

1. **LLM Integration**: How to integrate Google's Gemini API effectively
2. **Tool Creation**: Building custom tools for AI agents
3. **API Integration**: Working with GitHub API and external services
4. **Authentication**: Email verification, password hashing with bcrypt
5. **JWT Tokens**: Implementing stateless authentication
6. **Database Design**: SQLite schema for users, sessions, and verification
7. **Session Management**: Implementing stateful conversations per user
8. **Web Development**: Flask backend with dynamic frontend
9. **Email Service**: Sending verification codes and notifications
10. **Prompt Engineering**: Crafting effective prompts for better results
11. **Error Handling**: Robust error handling in AI applications
12. **Security Best Practices**: API key management, password security, HTTPS

## 🔐 Security Considerations

- **API Key Management**: Never commit `.env` file to Git (already in .gitignore)
- **Password Security**: Uses bcrypt hashing with salt (industry standard)
- **Email Verification**: Prevents spam and ensures valid email addresses
- **JWT Tokens**: Secure, expiring tokens with configurable duration
- **HTTPS**: Use HTTPS in production environments
- **Input Validation**: All user inputs validated server-side
- **Rate Limiting**: Implement rate limiting in production for API endpoints
- **Database Security**: Parameterized queries to prevent SQL injection
- **Session Security**: Secure session keys and HTTPS-only cookies

## 📝 Best Practices

1. **For Authentication:**
   - Always verify email before allowing login
   - Use strong passwords (minimum 6 characters, recommended 12+)
   - Regenerate JWT tokens periodically
   - Implement logout functionality

2. **For Best Results:**
   - Be specific in project descriptions
   - Provide realistic time and skill assessments
   - Use the trend research feature for cutting-edge ideas
   - Check similar GitHub projects before starting

3. **Tool Usage:**
   - Use GitHub search to learn from existing projects
   - Use budget calculator in early planning stages
   - Use skill assessment to create learning roadmaps
   - Review session history to track your planning journey

4. **Workflow Recommendation:**
   ```
   1. Sign Up & Verify Email → Secure account
   2. Login → Access personalized dashboard
   3. Generate Ideas (with trends) → Pick best idea
   4. Create Roadmap (with GitHub) → Understand scope
   5. Assess Feasibility (with tools) → Make decision
   6. Review Session Summary → Refine approach
   ```

##  Future Enhancements

### Ready to Implement
- [ ] **Multi-agent System**: Separate agents for ideas, roadmaps, and feasibility
- [ ] **Parallel Agents**: Execute multiple agents simultaneously
- [ ] **Sequential Workflows**: Chain agents for complex tasks
- [ ] **PostgreSQL Integration**: Replace SQLite with PostgreSQL for scale
- [ ] **MCP (Model Context Protocol)**: Add file system and data access
- [ ] **Long-running Operations**: Implement pause/resume for complex tasks
- [ ] **Password Reset**: Add forgot password functionality
- [ ] **OAuth Integration**: Support Google/GitHub login

### Advanced Features
- [ ] **Context Engineering**: Implement context compaction and optimization
- [ ] **Observability**: Add structured logging with ELK stack
- [ ] **Tracing**: Implement distributed tracing with OpenTelemetry
- [ ] **Metrics**: Track performance metrics and agent effectiveness
- [ ] **Agent Evaluation**: Automated testing and quality metrics
- [ ] **A2A Protocol**: Agent-to-agent communication
- [ ] **RAG Integration**: Add retrieval-augmented generation
- [ ] **Vector Database**: Store and search project embeddings

### User Features
- [ ] Export roadmaps to PDF/Markdown
- [ ] Project templates library
- [ ] Multi-language support
- [ ] Integration with Jira/Trello/Asana
- [ ] Email notifications & digests
- [ ] Collaborative features (share roadmaps)
- [ ] Mobile app version
- [ ] Dark/Light theme toggle

## 📊 Performance Metrics

Current system capabilities:
- **Authentication**: Registration & login in <1 second
- **Response Time**: 2-5 seconds (with tools: 5-10 seconds)
- **Session Storage**: SQLite (persistent across server restarts)
- **Email Delivery**: <1 second (mock) to 5 seconds (SMTP)
- **Tool Accuracy**: 
  - GitHub Search: 95%+ relevant results
  - Budget Calculator: ±15% estimation accuracy
  - Skill Assessment: Context-dependent analysis
- **Concurrent Users**: Supports multiple authenticated sessions
- **Database Transactions**: SQLite with proper transaction handling

## 🔧 Troubleshooting

**Error: API Key not found**
- Ensure `.env` file exists in the project root
- Check that `GOOGLE_API_KEY` is set correctly
- Verify no extra spaces in the API key

**Error: Module not found**
- Run `pip install -r requirements.txt`
- Ensure virtual environment is activated: `.\venv\Scripts\activate`

**Error: Database locked**
- Close all other connections to the database
- Ensure only one web_agent.py instance is running
- Delete `project_database.db` and restart (will lose data)

**Error: models/gemini-pro is not found**
- ✅ Fixed! Now using `gemini-2.5-flash`
- Update web_agent.py if you have old version

**Web UI not loading**
- Check if port 5000 is available
- Try accessing `http://127.0.0.1:5000` instead
- Check firewall settings

**Email verification not received**
- Check console output for verification code in mock mode
- Verify SMTP credentials if using real email
- Check spam/junk folder

**GitHub Search not working**
- GitHub API has rate limits (60 requests/hour without auth)
- Try again after an hour
- Consider adding GitHub token for higher limits

**Login fails with valid credentials**
- Ensure email is verified (check database)
- Clear browser cookies/cache
- Try in private/incognito window

**Tools not executing**
- Check console output for detailed errors
- Verify all dependencies are installed
- Check network connection for GitHub API
- Ensure JWT token is valid and not expired

**Session data lost after restart**
- Sessions are now persistent in SQLite database
- Data should persist across server restarts
- If lost, check database file permissions

## 📚 Resources

- [Google Gemini API Docs](https://ai.google.dev/docs)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [GitHub API Documentation](https://docs.github.com/en/rest)
- [Bcrypt Security](https://pypi.org/project/bcrypt/)
- [JWT Authentication](https://tools.ietf.org/html/rfc7519)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)
- [Email Verification Best Practices](https://www.emailonacid.com/)

## 🤝 Contributing

To enhance this project:

1. **Add New Features:**
   - Create feature branch
   - Implement with tests
   - Update documentation
   - Submit pull request

2. **Add New Tools:**
   - Create a new tool method in `web_agent.py`
   - Add API endpoint
   - Update UI in templates
   - Document in README

3. **Improve Authentication:**
   - Add password reset functionality
   - Implement OAuth (Google, GitHub)
   - Add two-factor authentication (2FA)
   - Add social login

4. **Improve Database:**
   - Migrate to PostgreSQL
   - Add database migrations
   - Implement connection pooling
   - Add backup functionality

5. **Improve Security:**
   - Add rate limiting
   - Implement CSRF protection
   - Add input sanitization
   - Enable HTTPS/SSL

## 📄 License

MIT License 

## 🎉 Acknowledgments

- Google Gemini API for powerful LLM capabilities
- GitHub API for project discovery
- Flask framework for easy web development
- Open-source community for inspiration
- Bcrypt for secure password hashing
- JWT for stateless authentication

**Happy Coding!! 🚀**

*Built with ❤️ using Google Gemini API & Flask*
