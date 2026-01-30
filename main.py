"""
Project Ideas AI Agent

"""

import os
from dotenv import load_dotenv
import google.generativeai as genai
from typing import Dict, List
import json

# Load environment variables
load_dotenv()

# Configure Gemini API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

class ProjectIdeasAgent:
    """AI Agent for generating project ideas, roadmaps, and feasibility analysis"""
    
    def __init__(self):
        self.model = genai.GenerativeModel(
    model_name="models/gemini-2.5-flash"
)
        self.chat = None
        self.conversation_history = []
    
    def generate_project_ideas(self, domain: str, skill_level: str, constraints: str = "") -> str:
        """Generate project ideas based on domain and skill level"""
        prompt = f"""
        Generate 5 innovative project ideas for the following specifications:
        
        Domain: {domain}
        Skill Level: {skill_level}
        Additional Constraints: {constraints if constraints else "None"}
        
        For each project idea, provide:
        1. Project Name
        2. Brief Description (2-3 sentences)
        3. Key Technologies Required
        4. Estimated Timeline
        5. Learning Outcomes
        
        Format the response in a clear, structured way.
        """
        
        try:
            response = self.model.generate_content(prompt)
            result = response.text
            self.conversation_history.append({
                "action": "generate_ideas",
                "domain": domain,
                "skill_level": skill_level,
                "response": result
            })
            return result
        except Exception as e:
            return f"Error generating project ideas: {str(e)}"
    
    def create_roadmap(self, project_description: str) -> str:
        """Create a detailed roadmap for a given project"""
        prompt = f"""
        Create a comprehensive project roadmap for the following project:
        
        Project: {project_description}
        
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
        
        Make the roadmap practical and actionable.
        """
        
        try:
            response = self.model.generate_content(prompt)
            result = response.text
            self.conversation_history.append({
                "action": "create_roadmap",
                "project": project_description,
                "response": result
            })
            return result
        except Exception as e:
            return f"Error creating roadmap: {str(e)}"
    
    def assess_feasibility(self, project_description: str, available_time: str, 
                          current_skills: str, budget: str = "Limited") -> str:
        """Assess the feasibility of a project"""
        prompt = f"""
        Assess the feasibility of the following project:
        
        Project Description: {project_description}
        Available Time: {available_time}
        Current Skills: {current_skills}
        Budget: {budget}
        
        Provide a detailed feasibility analysis including:
        
        1. Feasibility Score (1-10 scale with justification)
        2. Technical Feasibility
           - Required skills vs current skills gap
           - Technology complexity assessment
           - Learning curve estimation
        3. Time Feasibility
           - Realistic timeline estimate
           - Time commitment required
           - Comparison with available time
        4. Resource Feasibility
           - Budget requirements
           - Tools and infrastructure needed
           - Alternative low-cost options
        5. Risk Analysis
           - Major risks and challenges
           - Mitigation strategies
        6. Recommendations
           - Go/No-Go decision with reasoning
           - Suggested modifications if needed
           - Alternative approaches
        
        Be honest and practical in your assessment.
        """
        
        try:
            response = self.model.generate_content(prompt)
            result = response.text
            self.conversation_history.append({
                "action": "assess_feasibility",
                "project": project_description,
                "response": result
            })
            return result
        except Exception as e:
            return f"Error assessing feasibility: {str(e)}"
    
    def chat_with_agent(self, user_message: str) -> str:
        """Interactive chat for project consultation"""
        if self.chat is None:
            self.chat = self.model.start_chat(history=[])
        
        system_context = """
        You are a helpful AI assistant specializing in project planning and development.
        You help users brainstorm project ideas, create roadmaps, and assess feasibility.
        Be encouraging, practical, and provide actionable advice.
        """
        
        full_message = f"{system_context}\n\nUser: {user_message}"
        
        try:
            response = self.chat.send_message(user_message)
            return response.text
        except Exception as e:
            return f"Error in chat: {str(e)}"
    
    def get_conversation_history(self) -> List[Dict]:
        """Return the conversation history"""
        return self.conversation_history


def main():
    """Main function to demonstrate the agent"""
    print("=" * 60)
    print("PROJECT IDEAS AI AGENT")
    print("=" * 60)
    print()
    
    agent = ProjectIdeasAgent()
    
    while True:
        print("\nWhat would you like to do?")
        print("1. Generate Project Ideas")
        print("2. Create Project Roadmap")
        print("3. Assess Project Feasibility")
        print("4. Chat with Agent")
        print("5. View Conversation History")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == "1":
            domain = input("Enter domain (e.g., Web Development, AI/ML, Mobile Apps): ")
            skill_level = input("Enter skill level (Beginner/Intermediate/Advanced): ")
            constraints = input("Any constraints? (press Enter to skip): ")
            
            print("\n" + "=" * 60)
            print("GENERATING PROJECT IDEAS...")
            print("=" * 60 + "\n")
            
            result = agent.generate_project_ideas(domain, skill_level, constraints)
            print(result)
        
        elif choice == "2":
            project_desc = input("Enter project description: ")
            
            print("\n" + "=" * 60)
            print("CREATING PROJECT ROADMAP...")
            print("=" * 60 + "\n")
            
            result = agent.create_roadmap(project_desc)
            print(result)
        
        elif choice == "3":
            project_desc = input("Enter project description: ")
            available_time = input("Available time (e.g., 3 months, 10 hours/week): ")
            current_skills = input("Current skills: ")
            budget = input("Budget (Limited/Moderate/Flexible): ")
            
            print("\n" + "=" * 60)
            print("ASSESSING PROJECT FEASIBILITY...")
            print("=" * 60 + "\n")
            
            result = agent.assess_feasibility(project_desc, available_time, current_skills, budget)
            print(result)
        
        elif choice == "4":
            print("\nChat with Agent (type 'back' to return to menu)")
            while True:
                user_input = input("\nYou: ")
                if user_input.lower() == 'back':
                    break
                response = agent.chat_with_agent(user_input)
                print(f"\nAgent: {response}")
        
        elif choice == "5":
            history = agent.get_conversation_history()
            print("\n" + "=" * 60)
            print("CONVERSATION HISTORY")
            print("=" * 60 + "\n")
            if history:
                for idx, entry in enumerate(history, 1):
                    print(f"Entry {idx}: {entry['action']}")
                    print("-" * 60)
            else:
                print("No history yet.")
        
        elif choice == "6":
            print("\nThank you for using Project Ideas AI Agent!")
            break
        
        else:
            print("\nInvalid choice. Please try again.")


if __name__ == "__main__":
    main()
