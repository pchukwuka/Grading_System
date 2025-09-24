#!/usrbin/python3

"""
Database module for Smart Grading and Feedback System - OOP Version
Handles all database operations using SQLite with Object-Oriented Design
"""

import sqlite3
import os
import random
import string
from datetime import datetime

class DatabaseManager:
    """Manages all database operations for the Smart Grading System"""

    def __init__(self, db_file="smart_grading.db"):
        """Initialize database manager with database file path"""
        self.db_file = db_file

    def get_connection(self):
        """Create and return database connection"""
        try:
            conn = sqlite3.connect(self.db_file)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            return conn
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            return None

    def initialize_database(self):
        """Create all necessary tables for the application"""
        conn = self.get_connection()
        if not conn:
            return False

        try:
            cursor = conn.cursor()

            # Create users table with login_code for students
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    role TEXT NOT NULL CHECK (role IN ('teacher', 'student')),
                    username TEXT UNIQUE,
                    password TEXT,
                    login_code TEXT UNIQUE,
                    created_by INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY (created_by) REFERENCES users (id)
                )
            ''')

            # Create assignments table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS assignments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    teacher_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    due_date TIMESTAMP,
                    total_points INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY (teacher_id) REFERENCES users (id)
                )
            ''')

            # Create questions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    assignment_id INTEGER NOT NULL,
                    question_text TEXT NOT NULL,
                    question_type TEXT NOT NULL CHECK (question_type IN ('objective', 'subjective')),
                    correct_answer TEXT,
                    points INTEGER DEFAULT 1,
                    options TEXT,  -- JSON string for multiple choice options
                    question_order INTEGER DEFAULT 0,
                    FOREIGN KEY (assignment_id) REFERENCES assignments (id)
                )
            ''')

            # Create submissions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS submissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    assignment_id INTEGER NOT NULL,
                    student_id INTEGER NOT NULL,
                    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_score REAL DEFAULT 0,
                    max_score INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'submitted',
                    submission_count INTEGER DEFAULT 1,
                    FOREIGN KEY (assignment_id) REFERENCES assignments (id),
                    FOREIGN KEY (student_id) REFERENCES users (id),
                    UNIQUE(assignment_id, student_id)
                )
            ''')

            # Create answers table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS answers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    submission_id INTEGER NOT NULL,
                    question_id INTEGER NOT NULL,
                    student_answer TEXT,
                    score REAL DEFAULT 0,
                    feedback TEXT,
                    answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (submission_id) REFERENCES submissions (id),
                    FOREIGN KEY (question_id) REFERENCES questions (id)
                )
            ''')

            # Create default teacher accounts if they don't exist
            self._create_default_teachers(cursor)

            conn.commit()
            print("Database initialized successfully!")
            return True

        except sqlite3.Error as e:
            print(f"Database initialization error: {e}")
            return False
        finally:
            conn.close()

    def _create_default_teachers(self, cursor):
        """Create default teacher accounts"""
        default_teachers = [
            ('Mr. Kevin', 'Kevin', 'password123'),
            ('Mrs. Peace', 'Peace', 'password123')
        ]

        for name, username, password in default_teachers:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO users (name, role, username, password)
                    VALUES (?, ?, ?, ?)
                ''', (name, 'teacher', username, password))
            except sqlite3.Error:
                continue

    def generate_login_code(self, length=6):
        """Generate a unique login code for students"""
        while True:
            # Generate random code with letters and numbers
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

            # Check if code already exists
            conn = self.get_connection()
            if not conn:
                return None

            try:
                cursor = conn.cursor()
                cursor.execute('SELECT id FROM users WHERE login_code = ?', (code,))
                if not cursor.fetchone():
                    return code
            except sqlite3.Error:
                return None
            finally:
                conn.close()

    def verify_teacher(self, username, password):
        """Verify teacher credentials"""
        conn = self.get_connection()
        if not conn:
            return None

        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, role, username
                FROM users
                WHERE username = ? AND password = ? AND role = 'teacher' AND is_active = 1
            ''', (username, password))

            user = cursor.fetchone()
            return dict(user) if user else None

        except sqlite3.Error as e:
            print(f"Teacher verification error: {e}")
            return None
        finally:
            conn.close()

    def verify_student(self, name, login_code):
        """Verify student credentials using name and login code"""
        conn = self.get_connection()
        if not conn:
            return None

        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, role, login_code
                FROM users
                WHERE LOWER(name) = LOWER(?) AND login_code = ? AND role = 'student' AND is_active = 1
            ''', (name.strip(), login_code.upper()))

            user = cursor.fetchone()
            return dict(user) if user else None

        except sqlite3.Error as e:
            print(f"Student verification error: {e}")
            return None
        finally:
            conn.close()

    def add_student(self, name, teacher_id):
        """Add a new student and return their login code"""
        conn = self.get_connection()
        if not conn:
            return None

        try:
            # Generate unique login code
            login_code = self.generate_login_code()
            if not login_code:
                return None

            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (name, role, login_code, created_by)
                VALUES (?, ?, ?, ?)
            ''', (name.strip(), 'student', login_code, teacher_id))

            conn.commit()
            return login_code

        except sqlite3.IntegrityError:
            print(f"Student with name '{name}' might already exist.")
            return None
        except sqlite3.Error as e:
            print(f"Error adding student: {e}")
            return None
        finally:
            conn.close()

    def get_students_by_teacher(self, teacher_id):
        """Get all students created by a specific teacher"""
        conn = self.get_connection()
        if not conn:
            return []

        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, login_code, created_at, is_active
                FROM users
                WHERE created_by = ? AND role = 'student'
                ORDER BY name
            ''', (teacher_id,))

            return [dict(row) for row in cursor.fetchall()]

        except sqlite3.Error as e:
            print(f"Error fetching students: {e}")
            return []
        finally:
            conn.close()

    def get_all_students(self):
        """Get all active students"""
        conn = self.get_connection()
        if not conn:
            return []

        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, login_code, created_at
                FROM users
                WHERE role = 'student' AND is_active = 1
                ORDER BY name
            ''', )

            return [dict(row) for row in cursor.fetchall()]

        except sqlite3.Error as e:
            print(f"Error fetching all students: {e}")
            return []
        finally:
            conn.close()

    def deactivate_student(self, student_id, teacher_id):
        """Deactivate a student (soft delete)"""
        conn = self.get_connection()
        if not conn:
            return False

        try:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users
                SET is_active = 0
                WHERE id = ? AND created_by = ? AND role = 'student'
            ''', (student_id, teacher_id))

            conn.commit()
            return cursor.rowcount > 0

        except sqlite3.Error as e:
            print(f"Error deactivating student: {e}")
            return False
        finally:
            conn.close()

    def save_assignment(self, assignment_data):
        """Save assignment with questions to database"""
        conn = self.get_connection()
        if not conn:
            return False

        try:
            cursor = conn.cursor()

            # Calculate total points
            total_points = sum(q['points'] for q in assignment_data['questions'])

            # Insert assignment
            cursor.execute('''
                INSERT INTO assignments (title, description, teacher_id, total_points, due_date)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                assignment_data['title'],
                assignment_data['description'],
                assignment_data['teacher_id'],
                total_points,
                assignment_data.get('due_date')
            ))

            assignment_id = cursor.lastrowid

            # Insert questions
            for i, question in enumerate(assignment_data['questions']):
                cursor.execute('''
                    INSERT INTO questions
                    (assignment_id, question_text, question_type, correct_answer, points, options, question_order)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    assignment_id,
                    question['text'],
                    question['type'],
                    question.get('correct_answer', ''),
                    question['points'],
                    question.get('options', ''),
                    i + 1
                ))

            conn.commit()
            return assignment_id

        except sqlite3.Error as e:
            print(f"Error saving assignment: {e}")
            return False
        finally:
            conn.close()

    def get_assignments(self, teacher_id=None, include_inactive=False):
        """Get assignments (all or by teacher)"""
        conn = self.get_connection()
        if not conn:
            return []

        try:
            cursor = conn.cursor()

            base_query = '''
                SELECT a.*, u.name as teacher_name
                FROM assignments a
                JOIN users u ON a.teacher_id = u.id
            '''

            conditions = []
            params = []

            if not include_inactive:
                conditions.append("a.is_active = 1")

            if teacher_id:
                conditions.append("a.teacher_id = ?")
                params.append(teacher_id)

            if conditions:
                base_query += " WHERE " + " AND ".join(conditions)

            base_query += " ORDER BY a.created_at DESC"

            cursor.execute(base_query, params)
            return [dict(row) for row in cursor.fetchall()]

        except sqlite3.Error as e:
            print(f"Error fetching assignments: {e}")
            return []
        finally:
            conn.close()

    def get_assignment_questions(self, assignment_id):
        """Get all questions for an assignment"""
        conn = self.get_connection()
        if not conn:
            return []

        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM questions
                WHERE assignment_id = ?
                ORDER BY question_order, id
            ''', (assignment_id,))

            return [dict(row) for row in cursor.fetchall()]

        except sqlite3.Error as e:
            print(f"Error fetching questions: {e}")
            return []
        finally:
            conn.close()

    def save_submission(self, submission_data):
        """Save student submission with answers"""
        conn = self.get_connection()
        if not conn:
            return False

        try:
            cursor = conn.cursor()

            # Get assignment questions for grading
            questions = self.get_assignment_questions(submission_data['assignment_id'])
            if not questions:
                return False

            # Calculate scores
            total_score = 0
            max_score = sum(q['points'] for q in questions)

            # Insert or update submission
            cursor.execute('''
                INSERT OR REPLACE INTO submissions
                (assignment_id, student_id, total_score, max_score, submission_count)
                VALUES (?, ?, ?, ?,
                    COALESCE((SELECT submission_count + 1 FROM submissions
                              WHERE assignment_id = ? AND student_id = ?), 1))
            ''', (
                submission_data['assignment_id'],
                submission_data['student_id'],
                0,  # Will update after calculating
                max_score,
                submission_data['assignment_id'],
                submission_data['student_id']
            ))

            submission_id = cursor.lastrowid

            # Process answers and calculate scores
            for i, question in enumerate(questions):
                student_answer = submission_data['answers'].get(str(i), '')
                score, feedback = self._grade_answer(question, student_answer)
                total_score += score

                cursor.execute('''
                    INSERT OR REPLACE INTO answers
                    (submission_id, question_id, student_answer, score, feedback)
                    VALUES (?, ?, ?, ?, ?)
                ''', (submission_id, question['id'], student_answer, score, feedback))

            # Update total score
            cursor.execute('''
                UPDATE submissions
                SET total_score = ?
                WHERE id = ?
            ''', (total_score, submission_id))

            conn.commit()
            return True

        except sqlite3.Error as e:
            print(f"Error saving submission: {e}")
            return False
        finally:
            conn.close()

    def _grade_answer(self, question, student_answer):
        """Grade individual answer and provide feedback"""
        score = 0
        feedback = ""

        if question['question_type'] == 'objective':
            if student_answer.upper().strip() == question['correct_answer'].upper().strip():
                score = question['points']
                feedback = "Correct! Well done."
            else:
                feedback = f"Incorrect. The correct answer is {question['correct_answer']}."
        else:
            # Subjective grading (basic implementation)
            if student_answer.strip():
                # Simple keyword-based scoring
                word_count = len(student_answer.split())
                if word_count >= 10:  # Minimum effort check
                    score = question['points'] * 0.8  # 80% for good effort
                    feedback = "Good response! Your answer shows understanding."
                elif word_count >= 5:
                    score = question['points'] * 0.6  # 60% for basic effort
                    feedback = "Adequate response. Consider providing more detail."
                else:
                    score = question['points'] * 0.3  # 30% for minimal effort
                    feedback = "Brief response. Please elaborate for full credit."
            else:
                feedback = "No answer provided."

        return score, feedback

    def get_student_submissions(self, student_id):
        """Get all submissions for a student"""
        conn = self.get_connection()
        if not conn:
            return []

        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT s.*, a.title, a.total_points, u.name as teacher_name
                FROM submissions s
                JOIN assignments a ON s.assignment_id = a.id
                JOIN users u ON a.teacher_id = u.id
                WHERE s.student_id = ?
                ORDER BY s.submitted_at DESC
            ''', (student_id,))

            return [dict(row) for row in cursor.fetchall()]

        except sqlite3.Error as e:
            print(f"Error fetching submissions: {e}")
            return []
        finally:
            conn.close()

    def get_submission_details(self, submission_id):
        """Get detailed submission with answers and feedback"""
        conn = self.get_connection()
        if not conn:
            return None

        try:
            cursor = conn.cursor()

            # Get submission info
            cursor.execute('''
                SELECT s.*, a.title, u.name as student_name
                FROM submissions s
                JOIN assignments a ON s.assignment_id = a.id
                JOIN users u ON s.student_id = u.id
                WHERE s.id = ?
            ''', (submission_id,))

            submission = cursor.fetchone()
            if not submission:
                return None

            submission = dict(submission)

            # Get answers with questions
            cursor.execute('''
                SELECT a.*, q.question_text, q.question_type, q.correct_answer, q.points
                FROM answers a
                JOIN questions q ON a.question_id = q.id
                WHERE a.submission_id = ?
                ORDER BY q.question_order, q.id
            ''', (submission_id,))

            submission['answers'] = [dict(row) for row in cursor.fetchall()]
            return submission

        except sqlite3.Error as e:
            print(f"Error fetching submission details: {e}")
            return None
        finally:
            conn.close()
