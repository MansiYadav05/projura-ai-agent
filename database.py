"""
Database setup and models for Project Tracker
Using SQLite for simplicity
"""

import sqlite3
from datetime import datetime
import json
from typing import Dict, List, Optional

class Database:
    """Database handler for project tracking"""
    
    def __init__(self, db_path='projects.db'):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        return conn
    
    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create users table for authentication
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                is_verified INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create email_verification table for verification codes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_verification (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                verification_code TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                is_used INTEGER DEFAULT 0,
                FOREIGN KEY (email) REFERENCES users (email)
            )
        ''')
        
        # Create projects table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                project_name TEXT NOT NULL,
                description TEXT NOT NULL,
                domain TEXT,
                skill_level TEXT,
                available_time TEXT,
                budget TEXT,
                status TEXT DEFAULT 'planning',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create project_analysis table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS project_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                analysis_type TEXT NOT NULL,
                analysis_data TEXT NOT NULL,
                ai_recommendation TEXT,
                next_step TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        ''')
        
        # Create project_milestones table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS project_milestones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                milestone_name TEXT NOT NULL,
                description TEXT,
                target_date TEXT,
                status TEXT DEFAULT 'pending',
                completed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        ''')
        
        # Create project_progress table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS project_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                progress_percentage INTEGER DEFAULT 0,
                current_phase TEXT,
                notes TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # ===== PROJECT CRUD OPERATIONS =====
    
    def create_project(self, user_id: str, project_data: Dict) -> int:
        """Create a new project"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO projects 
            (user_id, project_name, description, domain, skill_level, 
             available_time, budget, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            project_data.get('project_name'),
            project_data.get('description'),
            project_data.get('domain'),
            project_data.get('skill_level'),
            project_data.get('available_time'),
            project_data.get('budget'),
            'planning'
        ))
        
        project_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return project_id
    
    def get_project(self, project_id: int) -> Optional[Dict]:
        """Get project by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def get_user_projects(self, user_id: str) -> List[Dict]:
        """Get all projects for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT * FROM projects WHERE user_id = ? ORDER BY updated_at DESC',
            (user_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def update_project(self, project_id: int, updates: Dict):
        """Update project details"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Build dynamic update query
        set_clause = ', '.join([f"{key} = ?" for key in updates.keys()])
        values = list(updates.values())
        values.append(project_id)
        
        cursor.execute(f'''
            UPDATE projects 
            SET {set_clause}, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', values)
        
        conn.commit()
        conn.close()
    
    def delete_project(self, project_id: int):
        """Delete a project and all related data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM project_analysis WHERE project_id = ?', (project_id,))
        cursor.execute('DELETE FROM project_milestones WHERE project_id = ?', (project_id,))
        cursor.execute('DELETE FROM project_progress WHERE project_id = ?', (project_id,))
        cursor.execute('DELETE FROM projects WHERE id = ?', (project_id,))
        
        conn.commit()
        conn.close()
    
    # ===== PROJECT ANALYSIS OPERATIONS =====
    
    def save_analysis(self, project_id: int, analysis_type: str, 
                     analysis_data: Dict, ai_recommendation: str, 
                     next_step: str) -> int:
        """Save project analysis"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO project_analysis 
            (project_id, analysis_type, analysis_data, ai_recommendation, next_step)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            project_id,
            analysis_type,
            json.dumps(analysis_data),
            ai_recommendation,
            next_step
        ))
        
        analysis_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return analysis_id
    
    def get_project_analyses(self, project_id: int) -> List[Dict]:
        """Get all analyses for a project"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM project_analysis 
            WHERE project_id = ? 
            ORDER BY created_at DESC
        ''', (project_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        analyses = []
        for row in rows:
            analysis = dict(row)
            analysis['analysis_data'] = json.loads(analysis['analysis_data'])
            analyses.append(analysis)
        
        return analyses
    
    def get_latest_analysis(self, project_id: int) -> Optional[Dict]:
        """Get the most recent analysis"""
        analyses = self.get_project_analyses(project_id)
        return analyses[0] if analyses else None
    
    # ===== MILESTONE OPERATIONS =====
    
    def add_milestone(self, project_id: int, milestone_data: Dict) -> int:
        """Add a milestone to project"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO project_milestones 
            (project_id, milestone_name, description, target_date, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            project_id,
            milestone_data.get('milestone_name'),
            milestone_data.get('description'),
            milestone_data.get('target_date'),
            milestone_data.get('status', 'pending')
        ))
        
        milestone_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return milestone_id
    
    def get_project_milestones(self, project_id: int) -> List[Dict]:
        """Get all milestones for a project"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM project_milestones 
            WHERE project_id = ? 
            ORDER BY created_at ASC
        ''', (project_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def update_milestone(self, milestone_id: int, status: str):
        """Update milestone status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        completed_at = datetime.now() if status == 'completed' else None
        
        cursor.execute('''
            UPDATE project_milestones 
            SET status = ?, completed_at = ?
            WHERE id = ?
        ''', (status, completed_at, milestone_id))
        
        conn.commit()
        conn.close()
    
    # ===== PROGRESS TRACKING =====
    
    def update_progress(self, project_id: int, progress_data: Dict):
        """Update project progress"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Check if progress record exists
        cursor.execute(
            'SELECT id FROM project_progress WHERE project_id = ?',
            (project_id,)
        )
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute('''
                UPDATE project_progress 
                SET progress_percentage = ?, current_phase = ?, notes = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE project_id = ?
            ''', (
                progress_data.get('progress_percentage'),
                progress_data.get('current_phase'),
                progress_data.get('notes'),
                project_id
            ))
        else:
            cursor.execute('''
                INSERT INTO project_progress 
                (project_id, progress_percentage, current_phase, notes)
                VALUES (?, ?, ?, ?)
            ''', (
                project_id,
                progress_data.get('progress_percentage'),
                progress_data.get('current_phase'),
                progress_data.get('notes')
            ))
        
        conn.commit()
        conn.close()
    
    def get_progress(self, project_id: int) -> Optional[Dict]:
        """Get current project progress"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM project_progress 
            WHERE project_id = ? 
            ORDER BY updated_at DESC 
            LIMIT 1
        ''', (project_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    # ===== STATISTICS =====
    
    def get_user_statistics(self, user_id: str) -> Dict:
        """Get user project statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Total projects
        cursor.execute(
            'SELECT COUNT(*) as total FROM projects WHERE user_id = ?',
            (user_id,)
        )
        total = cursor.fetchone()['total']
        
        # Projects by status
        cursor.execute('''
            SELECT status, COUNT(*) as count 
            FROM projects 
            WHERE user_id = ? 
            GROUP BY status
        ''', (user_id,))
        
        status_counts = {row['status']: row['count'] for row in cursor.fetchall()}
        
        # Completed milestones
        cursor.execute('''
            SELECT COUNT(*) as completed
            FROM project_milestones pm
            JOIN projects p ON pm.project_id = p.id
            WHERE p.user_id = ? AND pm.status = 'completed'
        ''', (user_id,))
        
        completed_milestones = cursor.fetchone()['completed']
        
        conn.close()
        
        return {
            'total_projects': total,
            'planning': status_counts.get('planning', 0),
            'in_progress': status_counts.get('in_progress', 0),
            'completed': status_counts.get('completed', 0),
            'on_hold': status_counts.get('on_hold', 0),
            'completed_milestones': completed_milestones
        }
    
    # ===== USER AUTHENTICATION =====
    
    def create_user(self, email: str, name: str, password_hash: str) -> Dict:
        """Create a new user account"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO users (email, name, password_hash, is_verified)
                VALUES (?, ?, ?, 0)
            ''', (email.lower(), name, password_hash))
            
            user_id = cursor.lastrowid
            conn.commit()
            
            return {
                'success': True,
                'user_id': user_id,
                'email': email.lower(),
                'name': name
            }
        except sqlite3.IntegrityError:
            conn.close()
            return {'success': False, 'message': 'Email already registered'}
        finally:
            conn.close()
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE email = ?', (email.lower(),))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def verify_user_email(self, email: str) -> bool:
        """Mark user email as verified"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users 
            SET is_verified = 1, updated_at = CURRENT_TIMESTAMP
            WHERE email = ?
        ''', (email.lower(),))
        
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        
        return success
    
    def create_verification_code(self, email: str, code: str, expires_at: str) -> bool:
        """Store verification code for email"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO email_verification (email, verification_code, expires_at)
                VALUES (?, ?, ?)
            ''', (email.lower(), code, expires_at))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error creating verification code: {e}")
            return False
        finally:
            conn.close()
    
    def verify_code(self, email: str, code: str) -> bool:
        """Verify the email verification code"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM email_verification
            WHERE email = ? AND verification_code = ? 
            AND is_used = 0 
            AND datetime(expires_at) > datetime('now')
            ORDER BY created_at DESC
            LIMIT 1
        ''', (email.lower(), code))
        
        result = cursor.fetchone()
        
        if result:
            # Mark as used
            cursor.execute('''
                UPDATE email_verification
                SET is_used = 1
                WHERE id = ?
            ''', (result['id'],))
            conn.commit()
            conn.close()
            return True
        
        conn.close()
        return False


# Initialize database instance
db = Database()
