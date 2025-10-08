"""
Cosmic Council MVP Database Layer
Simple SQLite implementation for MVP.
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path


class SimpleDatabase:
    """Simple SQLite database for the MVP."""
    
    def __init__(self, db_path: str = "cosmic_council_mvp.db"):
        """Initialize the database."""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Create the database tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Problems table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS problems (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                problem_text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending'
            )
        ''')
        
        # Solutions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS solutions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                problem_id INTEGER,
                enterprise_name TEXT NOT NULL,
                solution_text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (problem_id) REFERENCES problems (id)
            )
        ''')
        
        # Problem sessions table (for tracking complete problem-solving sessions)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS problem_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                problem_id INTEGER,
                all_solutions TEXT,  -- JSON string of all solutions
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (problem_id) REFERENCES problems (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"📊 Database initialized: {self.db_path}")
    
    def save_problem(self, problem: str) -> int:
        """Save a problem and return its ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO problems (problem_text) VALUES (?)", 
            (problem,)
        )
        problem_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        print(f"💾 Problem saved with ID: {problem_id}")
        return problem_id
    
    def save_solution(self, problem_id: int, enterprise_name: str, solution: str) -> int:
        """Save a solution for a problem."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO solutions (problem_id, enterprise_name, solution_text) VALUES (?, ?, ?)",
            (problem_id, enterprise_name, solution)
        )
        solution_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        print(f"💾 Solution saved for {enterprise_name}")
        return solution_id
    
    def save_problem_session(self, problem_id: int, all_solutions: Dict[str, str]) -> int:
        """Save a complete problem-solving session."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        solutions_json = json.dumps(all_solutions)
        cursor.execute(
            "INSERT INTO problem_sessions (problem_id, all_solutions) VALUES (?, ?)",
            (problem_id, solutions_json)
        )
        session_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        print(f"💾 Problem session saved with ID: {session_id}")
        return session_id
    
    def get_problem(self, problem_id: int) -> Optional[Dict[str, Any]]:
        """Get a problem by ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, problem_text, created_at, status FROM problems WHERE id = ?",
            (problem_id,)
        )
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return {
                "id": row[0],
                "problem_text": row[1],
                "created_at": row[2],
                "status": row[3]
            }
        return None
    
    def get_solutions_for_problem(self, problem_id: int) -> List[Dict[str, Any]]:
        """Get all solutions for a problem."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT enterprise_name, solution_text, created_at FROM solutions WHERE problem_id = ? ORDER BY created_at",
            (problem_id,)
        )
        rows = cursor.fetchall()
        
        conn.close()
        
        return [
            {
                "enterprise_name": row[0],
                "solution_text": row[1],
                "created_at": row[2]
            }
            for row in rows
        ]
    
    def get_recent_problems(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent problems."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, problem_text, created_at, status FROM problems ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )
        rows = cursor.fetchall()
        
        conn.close()
        
        return [
            {
                "id": row[0],
                "problem_text": row[1],
                "created_at": row[2],
                "status": row[3]
            }
            for row in rows
        ]
    
    def get_database_stats(self) -> Dict[str, int]:
        """Get database statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Count problems
        cursor.execute("SELECT COUNT(*) FROM problems")
        problem_count = cursor.fetchone()[0]
        
        # Count solutions
        cursor.execute("SELECT COUNT(*) FROM solutions")
        solution_count = cursor.fetchone()[0]
        
        # Count sessions
        cursor.execute("SELECT COUNT(*) FROM problem_sessions")
        session_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "problems": problem_count,
            "solutions": solution_count,
            "sessions": session_count
        }
