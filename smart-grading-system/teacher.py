"""
Teacher class for Smart Grading and Feedback System - OOP Version
Handles all teacher-related operations using Object-Oriented Design
"""

import json
from user import User, MenuManager, PerformanceCalculator, DisplayFormatter

class Teacher(User):
    """Teacher class with all teacher-specific functionality"""
    
    def __init__(self, user_data, db_manager):
        """Initialize teacher with user data and database manager"""
        super().__init__(user_data, db_manager)
        self.menu_manager = MenuManager(self)
        self._setup_menu()
    
    def _setup_menu(self):
        """Set up teacher menu options"""
        self.menu_manager.add_option("1", "Manage Students", self.manage_students)
        self.menu_manager.add_option("2", "Create Assignment", self.create_assignment)
        self.menu_manager.add_option("3", "View My Assignments", self.view_my_assignments)
        self.menu_manager.add_option("4", "View Student Submissions", self.view_student_submissions)
        self.menu_manager.add_option("5", "Generate Reports", self.generate_reports)
        self.menu_manager.add_option("6", "Assignment Statistics", self.view_assignment_statistics)
        self.menu_manager.add_option("7", "Logout", self.logout)
    
    def show_menu(self):
        """Display teacher menu and handle operations"""
        self.menu_manager.run_menu_loop("Teacher Dashboard")
    
    def logout(self):
        """Handle teacher logout"""
        print("Logging out...")
        return "logout"
    
    def manage_students(self):
        """Manage students (add, view, deactivate)"""
        self.display_header("Student Management")
        
        while True:
            print("\n--- Student Management ---")
            print("1. Add New Student")
            print("2. View My Students")
            print("3. View All Students")
            print("4. Deactivate Student")
            print("5. Back to Main Menu")
            
            choice = self.validate_input(
                "Select option (1-5): ",
                "choice",
                valid_choices=["1", "2", "3", "4", "5"]
            )
            
            if choice == "1":
                self._add_student()
            elif choice == "2":
                self._view_my_students()
            elif choice == "3":
                self._view_all_students()
            elif choice == "4":
                self._deactivate_student()
            elif choice == "5":
                break
            
            if choice != "5":
                self.wait_for_input()
    
    def _add_student(self):
        """Add a new student and generate login code"""
        print("\n--- Add New Student ---")
        
        while True:
            student_name = self.validate_input(
                "Enter student's full name: ",
                "string",
                min_length=2,
                max_length=100
            )
            
            if not student_name:
                return
            
            # Validate name format (only letters and spaces)
            if not all(c.isalpha() or c.isspace() for c in student_name):
                print("Name should contain only letters and spaces!")
                continue
            
            # Add student to database
            login_code = self.db_manager.add_student(student_name, self.id)
            
            if login_code:
                print(f"\n{'='*50}")
                print(f"Student Added Successfully!")
                print(f"{'='*50}")
                print(f"Name: {student_name}")
                print(f"Login Code: {login_code}")
                print(f"{'='*50}")
                print("IMPORTANT: Please provide this login code to the student.")
                print("They will need their exact name and this code to login.")
                
                if not self.confirm_action("Add another student?"):
                    break
            else:
                print("Failed to add student. Name might already exist.")
                if not self.confirm_action("Try again?"):
                    break
    
    def _view_my_students(self):
        """View students added by this teacher"""
        print("\n--- My Students ---")
        
        students = self.db_manager.get_students_by_teacher(self.id)
        
        if not students:
            print("You haven't added any students yet.")
            return
        
        # Display students in a table format
        headers = ["ID", "Name", "Login Code", "Status", "Date Added"]
        widths = [5, 25, 12, 10, 12]
        
        print(DisplayFormatter.format_table_header(headers, widths))
        
        for student in students:
            status = "Active" if student['is_active'] else "Inactive"
            date_added = DisplayFormatter.format_date(student['created_at'])
            
            row = [
                student['id'],
                student['name'],
                student['login_code'],
                status,
                date_added
            ]
            
            print(DisplayFormatter.format_table_row(row, widths))
        
        print(f"\nTotal Students: {len(students)}")
        
        # Option to view student details
        if self.confirm_action("View detailed student performance?"):
            self._view_student_performance()
    
    def _view_all_students(self):
        """View all students in the system"""
        print("\n--- All Students in System ---")
        
        students = self.db_manager.get_all_students()
        
        if not students:
            print("No students registered in the system.")
            return
        
        headers = ["ID", "Name", "Login Code", "Date Added"]
        widths = [5, 30, 12, 15]
        
        print(DisplayFormatter.format_table_header(headers, widths))
        
        for student in students:
            date_added = DisplayFormatter.format_date(student['created_at'])
            
            row = [
                student['id'],
                student['name'],
                student['login_code'],
                date_added
            ]
            
            print(DisplayFormatter.format_table_row(row, widths))
        
        print(f"\nTotal Students: {len(students)}")
    
    def _deactivate_student(self):
        """Deactivate a student"""
        print("\n--- Deactivate Student ---")
        
        students = self.db_manager.get_students_by_teacher(self.id)
        active_students = [s for s in students if s['is_active']]
        
        if not active_students:
            print("No active students to deactivate.")
            return
        
        print("Your active students:")
        headers = ["ID", "Name", "Login Code"]
        widths = [5, 30, 12]
        
        print(DisplayFormatter.format_table_header(headers, widths))
        
        for student in active_students:
            row = [student['id'], student['name'], student['login_code']]
            print(DisplayFormatter.format_table_row(row, widths))
        
        student_id = self.validate_input(
            "\nEnter student ID to deactivate: ",
            "integer",
            min_length=1
        )
        
        if student_id:
            # Find student name for confirmation
            student = next((s for s in active_students if s['id'] == student_id), None)
            if student:
                if self.confirm_action(f"Deactivate {student['name']}?"):
                    if self.db_manager.deactivate_student(student_id, self.id):
                        print(f"Student {student['name']} has been deactivated.")
                    else:
                        print("Failed to deactivate student.")
                else:
                    print("Deactivation cancelled.")
            else:
                print("Invalid student ID.")
    
    def _view_student_performance(self):
        """View performance of a specific student"""
        students = self.db_manager.get_students_by_teacher(self.id)
        
        if not students:
            print("No students to view.")
            return
        
        student_id = self.validate_input(
            "Enter student ID: ",
            "integer",
            min_length=1
        )
        
        if student_id:
            submissions = self.db_manager.get_student_submissions(student_id)
            if submissions:
                student_name = next((s['name'] for s in students if s['id'] == student_id), "Unknown")
                self._display_student_performance(student_name, submissions)
            else:
                print("No submissions found for this student.")
    
    def create_assignment(self):
        """Create a new assignment with questions"""
        self.display_header("Create New Assignment")
        
        print("Let's create a new assignment step by step.\n")
        
        # Get assignment basic information
        assignment_data = self._get_assignment_info()
        if not assignment_data:
            return
        
        # Add questions to assignment
        questions = self._create_questions()
        if not questions:
            print("No questions added. Assignment not created.")
            return
        
        assignment_data['questions'] = questions
        assignment_data['teacher_id'] = self.id
        
        # Save assignment to database
        assignment_id = self.db_manager.save_assignment(assignment_data)
        
        if assignment_id:
            print(f"\n{'='*50}")
            print("Assignment Created Successfully!")
            print(f"{'='*50}")
            print(f"Title: {assignment_data['title']}")
            print(f"Questions: {len(questions)}")
            print(f"Total Points: {sum(q['points'] for q in questions)}")
            print(f"Assignment ID: {assignment_id}")
            print(f"{'='*50}")
        else:
            print("Failed to create assignment. Please try again.")
    
    def _get_assignment_info(self):
        """Get basic assignment information"""
        title = self.validate_input(
            "Assignment title: ",
            "string",
            min_length=3,
            max_length=100
        )
        if not title:
            return None
        
        description = self.validate_input(
            "Assignment description (optional, press Enter to skip): ",
            "string",
            min_length=0,
            max_length=500
        )
        if description is None:
            return None
        
        return {
            'title': title,
            'description': description if description else "No description provided"
        }
    
    def _create_questions(self):
        """Create questions for the assignment"""
        questions = []
        question_num = 1
        
        print("\nNow let's add questions to your assignment.")
        print("You can create both objective (multiple choice) and subjective (essay) questions.\n")
        
        while True:
            print(f"\n--- Question {question_num} ---")
            
            question_data = self._create_single_question()
            if not question_data:
                if questions:  # If we have some questions already
                    if self.confirm_action("Stop adding questions and save assignment?"):
                        break
                else:
                    return None
            else:
                questions.append(question_data)
                question_num += 1
                
                if not self.confirm_action("Add another question?"):
                    break
        
        return questions
    
    def _create_single_question(self):
        """Create a single question"""
        # Get question text
        question_text = self.validate_input(
            "Enter question text: ",
            "string",
            min_length=5,
            max_length=1000
        )
        if not question_text:
            return None
        
        # Get question type
        print("\nQuestion types:")
        print("1. Objective (Multiple choice, True/False)")
        print("2. Subjective (Essay, Short answer)")
        
        type_choice = self.validate_input(
            "Select question type (1 or 2): ",
            "choice",
            valid_choices=["1", "2"]
        )
        if not type_choice:
            return None
        
        question_type = 'objective' if type_choice == '1' else 'subjective'
        
        # Get points
        points = self.validate_input(
            "Points for this question: ",
            "integer",
            min_length=1,
            max_length=100
        )
        if points is None:
            return None
        
        question_data = {
            'text': question_text,
            'type': question_type,
            'points': points
        }
        
        # Handle objective questions
        if question_type == 'objective':
            objective_data = self._create_objective_question()
            if objective_data:
                question_data.update(objective_data)
            else:
                return None
        
        return question_data
    
    def _create_objective_question(self):
        """Create objective question options and correct answer"""
        print("\nObjective Question Setup:")
        print("1. Multiple Choice (A, B, C, D)")
        print("2. True/False (A, B)")
        
        obj_type = self.validate_input(
            "Select type (1 or 2): ",
            "choice",
            valid_choices=["1", "2"]
        )
        if not obj_type:
            return None
        
        if obj_type == '1':
            # Multiple choice
            options = []
            option_labels = ['A', 'B', 'C', 'D']
            
            print("\nEnter four options:")
            for i, label in enumerate(option_labels):
                option_text = self.validate_input(
                    f"Option {label}: ",
                    "string",
                    min_length=1,
                    max_length=200
                )
                if not option_text:
                    return None
                options.append(f"{label}. {option_text}")
            
            correct_choice = self.validate_input(
                "Correct answer (A, B, C, or D): ",
                "choice",
                valid_choices=["A", "B", "C", "D"]
            )
            if not correct_choice:
                return None
            
            return {
                'options': json.dumps(options),
                'correct_answer': correct_choice
            }
        
        else:
            # True/False
            correct_choice = self.validate_input(
                "Correct answer (A for True, B for False): ",
                "choice",
                valid_choices=["A", "B"]
            )
            if not correct_choice:
                return None
            
            return {
                'options': json.dumps(["A. True", "B. False"]),
                'correct_answer': correct_choice
            }
    
    def view_my_assignments(self):
        """View assignments created by this teacher"""
        self.display_header("My Assignments")
        
        assignments = self.db_manager.get_assignments(teacher_id=self.id)
        
        if not assignments:
            print("You haven't created any assignments yet.")
            return
        
        # Display assignments in table format
        headers = ["ID", "Title", "Points", "Created", "Status"]
        widths = [5, 30, 8, 12, 8]
        
        print(DisplayFormatter.format_table_header(headers, widths))
        
        for assignment in assignments:
            status = "Active" if assignment['is_active'] else "Inactive"
            created_date = DisplayFormatter.format_date(assignment['created_at'])
            
            row = [
                assignment['id'],
                assignment['title'],
                assignment['total_points'],
                created_date,
                status
            ]
            
            print(DisplayFormatter.format_table_row(row, widths))
        
        print(f"\nTotal Assignments: {len(assignments)}")
        
        # Option to view assignment details
        if self.confirm_action("View assignment details?"):
            assignment_id = self.validate_input(
                "Enter assignment ID: ",
                "integer",
                min_length=1
            )
            if assignment_id:
                self._view_assignment_details(assignment_id)
    
    def _view_assignment_details(self, assignment_id):
        """View detailed information about an assignment"""
        questions = self.db_manager.get_assignment_questions(assignment_id)
        
        if not questions:
            print("Assignment not found or has no questions.")
            return
        
        assignments = self.db_manager.get_assignments(teacher_id=self.id)
        assignment = next((a for a in assignments if a['id'] == assignment_id), None)
        
        if not assignment:
            print("Assignment not found.")
            return
        
        print(f"\n--- Assignment Details ---")
        print(f"Title: {assignment['title']}")
        print(f"Description: {assignment['description']}")
        print(f"Total Points: {assignment['total_points']}")
        print(f"Number of Questions: {len(questions)}")
        print(f"Created: {DisplayFormatter.format_date(assignment['created_at'])}")
        
        print(f"\n--- Questions ---")
        
        for i, question in enumerate(questions, 1):
            print(f"\nQuestion {i} ({question['points']} points):")
            print(f"Type: {question['question_type'].title()}")
            print(f"Text: {question['question_text']}")
            
            if question['question_type'] == 'objective' and question['options']:
                try:
                    options = json.loads(question['options'])
                    print("Options:")
                    for option in options:
                        print(f"  {option}")
                    print(f"Correct Answer: {question['correct_answer']}")
                except json.JSONDecodeError:
                    print("  Error displaying options")
    
    def view_student_submissions(self):
        """View student submissions for assignments"""
        self.display_header("Student Submissions")
        
        # Show teacher's assignments
        assignments = self.db_manager.get_assignments(teacher_id=self.id)
        
        if not assignments:
            print("You haven't created any assignments yet.")
            return
        
        print("Your assignments:")
        headers = ["ID", "Title", "Points", "Created"]
        widths = [5, 35, 8, 12]
        
        print(DisplayFormatter.format_table_header(headers, widths))
        
        for assignment in assignments:
            created_date = DisplayFormatter.format_date(assignment['created_at'])
            row = [
                assignment['id'],
                assignment['title'],
                assignment['total_points'],
                created_date
            ]
            print(DisplayFormatter.format_table_row(row, widths))
        
        assignment_id = self.validate_input(
            "\nEnter assignment ID to view submissions: ",
            "integer",
            min_length=1
        )
        
        if assignment_id:
            self._view_assignment_submissions(assignment_id)
    
    def _view_assignment_submissions(self, assignment_id):
        """View submissions for a specific assignment"""
        # Get all students and their submissions for this assignment
        students = self.db_manager.get_all_students()
        
        print(f"\n--- Submissions for Assignment ID {assignment_id} ---")
        
        submissions_found = False
        
        for student in students:
            submissions = self.db_manager.get_student_submissions(student['id'])
            assignment_submissions = [s for s in submissions if s['assignment_id'] == assignment_id]
            
            if assignment_submissions:
                submissions_found = True
                submission = assignment_submissions[0]  # Should be only one per student per assignment
                
                percentage = DisplayFormatter.format_percentage(
                    submission['total_score'],
                    submission['max_score']
                )
                
                print(f"\nStudent: {student['name']}")
                print(f"Score: {DisplayFormatter.format_score(submission['total_score'], submission['max_score'])}")
                print(f"Percentage: {percentage}")
                print(f"Submitted: {DisplayFormatter.format_date(submission['submitted_at'])}")
        
        if not submissions_found:
            print("No submissions found for this assignment.")
        
        # Option to view detailed submission
        if submissions_found and self.confirm_action("View detailed submission feedback?"):
            student_name = self.validate_input("Enter student name: ", "string", 2, 100)
            if student_name:
                self._view_detailed_submission(assignment_id, student_name)
    
    def _view_detailed_submission(self, assignment_id, student_name):
        """View detailed submission with answers and feedback"""
        # Find student
        students = self.db_manager.get_all_students()
        student = next((s for s in students if s['name'].lower() == student_name.lower()), None)
        
        if not student:
            print("Student not found.")
            return
        
        # Get student's submission for this assignment
        submissions = self.db_manager.get_student_submissions(student['id'])
        submission = next((s for s in submissions if s['assignment_id'] == assignment_id), None)
        
        if not submission:
            print("No submission found for this student and assignment.")
            return
        
        # Get detailed submission
        submission_details = self.db_manager.get_submission_details(submission['id'])
        
        if not submission_details:
            print("Submission details not found.")
            return
        
        print(f"\n--- Detailed Submission ---")
        print(f"Student: {submission_details['student_name']}")
        print(f"Assignment: {submission_details['title']}")
        print(f"Total Score: {DisplayFormatter.format_score(submission_details['total_score'], submission_details['max_score'])}")
        
        percentage = DisplayFormatter.format_percentage(
            submission_details['total_score'],
            submission_details['max_score']
        )
        print(f"Percentage: {percentage}")
        print(f"Submitted: {DisplayFormatter.format_date(submission_details['submitted_at'])}")
        
        print(f"\n--- Question-by-Question Analysis ---")
        
        for i, answer in enumerate(submission_details['answers'], 1):
            print(f"\n--- Question {i} ---")
            print(f"Question: {answer['question_text']}")
            print(f"Student Answer: {answer['student_answer'] if answer['student_answer'] else 'No answer provided'}")
            
            if answer['question_type'] == 'objective' and answer['correct_answer']:
                print(f"Correct Answer: {answer['correct_answer']}")
            
            score_display = DisplayFormatter.format_score(answer['score'], answer['points'])
            print(f"Points Earned: {score_display}")
            print(f"Feedback: {answer['feedback']}")
    
    def generate_reports(self):
        """Generate various performance reports"""
        self.display_header("Generate Reports")
        
        while True:
            print("\n--- Available Reports ---")
            print("1. Class Performance Summary")
            print("2. Individual Student Report")
            print("3. Assignment Performance Analysis")
            print("4. My Students Overview")
            print("5. Back to Main Menu")
            
            choice = self.validate_input(
                "Select report type (1-5): ",
                "choice",
                valid_choices=["1", "2", "3", "4", "5"]
            )
            
            if choice == "1":
                self._generate_class_summary()
            elif choice == "2":
                self._generate_individual_student_report()
            elif choice == "3":
                self._generate_assignment_analysis()
            elif choice == "4":
                self._generate_students_overview()
            elif choice == "5":
                break
            
            if choice != "5":
                self.wait_for_input()
    
    def _generate_class_summary(self):
        """Generate class performance summary"""
        print("\n--- Class Performance Summary ---")
        
        # Get all assignments by this teacher
        assignments = self.db_manager.get_assignments(teacher_id=self.id)
        if not assignments:
            print("No assignments created yet.")
            return
        
        # Get all students
        students = self.db_manager.get_all_students()
        
        print(f"Total Students in System: {len(students)}")
        print(f"Total Assignments Created: {len(assignments)}")
        
        # Calculate overall statistics
        all_submissions = []
        for student in students:
            submissions = self.db_manager.get_student_submissions(student['id'])
            # Only include submissions for this teacher's assignments
            teacher_submissions = [s for s in submissions if any(a['id'] == s['assignment_id'] for a in assignments)]
            all_submissions.extend(teacher_submissions)
        
        if not all_submissions:
            print("No submissions to analyze yet.")
            return
        
        stats = PerformanceCalculator.calculate_class_statistics(all_submissions)
        
        print(f"\n--- Overall Statistics ---")
        print(f"Total Submissions: {stats['total_submissions']}")
        print(f"Class Average: {stats['average_score']:.1f}%")
        print(f"Highest Score: {stats['highest_score']:.1f}%")
        print(f"Lowest Score: {stats['lowest_score']:.1f}%")
        print(f"Pass Rate (≥60%): {stats['pass_rate']:.1f}%")
        
        # Grade distribution
        grade_counts = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
        for submission in all_submissions:
            if submission['max_score'] > 0:
                percentage = (submission['total_score'] / submission['max_score']) * 100
                grade = PerformanceCalculator.get_grade_letter(percentage)
                grade_counts[grade] += 1
        
        print(f"\n--- Grade Distribution ---")
        for grade, count in grade_counts.items():
            percentage_of_total = (count / len(all_submissions)) * 100 if all_submissions else 0
            print(f"Grade {grade}: {count} students ({percentage_of_total:.1f}%)")
    
    def _generate_individual_student_report(self):
        """Generate detailed report for a specific student"""
        print("\n--- Individual Student Report ---")
        
        students = self.db_manager.get_students_by_teacher(self.id)
        if not students:
            print("You haven't added any students yet.")
            return
        
        print("Your students:")
        headers = ["ID", "Name", "Login Code"]
        widths = [5, 30, 12]
        
        print(DisplayFormatter.format_table_header(headers, widths))
        
        for student in students:
            if student['is_active']:
                row = [student['id'], student['name'], student['login_code']]
                print(DisplayFormatter.format_table_row(row, widths))
        
        student_id = self.validate_input(
            "\nEnter student ID: ",
            "integer",
            min_length=1
        )
        
        if student_id:
            # Find student name
            student = next((s for s in students if s['id'] == student_id), None)
            if not student:
                print("Student not found.")
                return
            
            submissions = self.db_manager.get_student_submissions(student_id)
            
            if not submissions:
                print(f"No submissions found for {student['name']}.")
                return
            
            self._display_student_performance(student['name'], submissions)
    
    def _display_student_performance(self, student_name, submissions):
        """Display detailed student performance"""
        print(f"\n--- Performance Report for {student_name} ---")
        
        # Filter submissions for this teacher's assignments only
        teacher_assignments = self.db_manager.get_assignments(teacher_id=self.id)
        teacher_assignment_ids = [a['id'] for a in teacher_assignments]
        relevant_submissions = [s for s in submissions if s['assignment_id'] in teacher_assignment_ids]
        
        if not relevant_submissions:
            print("No submissions for your assignments.")
            return
        
        headers = ["Assignment", "Score", "Percentage", "Grade", "Date"]
        widths = [25, 12, 12, 8, 12]
        
        print(DisplayFormatter.format_table_header(headers, widths))
        
        total_score = 0
        total_possible = 0
        
        for submission in relevant_submissions:
            percentage = PerformanceCalculator.calculate_percentage(
                submission['total_score'],
                submission['max_score']
            )
            grade = PerformanceCalculator.get_grade_letter(percentage)
            score_display = DisplayFormatter.format_score(
                submission['total_score'],
                submission['max_score']
            )
            submitted_date = DisplayFormatter.format_date(submission['submitted_at'])
            
            row = [
                submission['title'],
                score_display,
                f"{percentage:.1f}%",
                grade,
                submitted_date
            ]
            
            print(DisplayFormatter.format_table_row(row, widths))
            
            total_score += submission['total_score']
            total_possible += submission['max_score']
        
        # Overall performance
        if total_possible > 0:
            overall_percentage = (total_score / total_possible) * 100
            overall_grade = PerformanceCalculator.get_grade_letter(overall_percentage)
            grade_description = PerformanceCalculator.get_grade_description(overall_percentage)
            
            print("-" * sum(widths))
            print(f"Overall Performance: {overall_percentage:.1f}% (Grade {overall_grade} - {grade_description})")
            print(f"Total Score: {total_score:.1f}/{total_possible}")
            print(f"Assignments Completed: {len(relevant_submissions)}")
    
    def _generate_assignment_analysis(self):
        """Analyze performance by assignment"""
        print("\n--- Assignment Performance Analysis ---")
        
        assignments = self.db_manager.get_assignments(teacher_id=self.id)
        if not assignments:
            print("No assignments created yet.")
            return
        
        print("Select an assignment to analyze:")
        headers = ["ID", "Title", "Points", "Created"]
        widths = [5, 35, 8, 12]
        
        print(DisplayFormatter.format_table_header(headers, widths))
        
        for assignment in assignments:
            created_date = DisplayFormatter.format_date(assignment['created_at'])
            row = [
                assignment['id'],
                assignment['title'],
                assignment['total_points'],
                created_date
            ]
            print(DisplayFormatter.format_table_row(row, widths))
        
        assignment_id = self.validate_input(
            "\nEnter assignment ID: ",
            "integer",
            min_length=1
        )
        
        if assignment_id:
            self._analyze_single_assignment(assignment_id)
    
    def _analyze_single_assignment(self, assignment_id):
        """Analyze performance for a single assignment"""
        # Get assignment info
        assignments = self.db_manager.get_assignments(teacher_id=self.id)
        assignment = next((a for a in assignments if a['id'] == assignment_id), None)
        
        if not assignment:
            print("Assignment not found.")
            return
        
        print(f"\n--- Analysis for '{assignment['title']}' ---")
        
        # Get all submissions for this assignment
        students = self.db_manager.get_all_students()
        assignment_submissions = []
        
        for student in students:
            submissions = self.db_manager.get_student_submissions(student['id'])
            for submission in submissions:
                if submission['assignment_id'] == assignment_id:
                    submission['student_name'] = student['name']
                    assignment_submissions.append(submission)
        
        if not assignment_submissions:
            print("No submissions found for this assignment.")
            return
        
        # Calculate statistics
        stats = PerformanceCalculator.calculate_class_statistics(assignment_submissions)
        
        print(f"Total Submissions: {stats['total_submissions']}")
        print(f"Average Score: {stats['average_score']:.1f}%")
        print(f"Highest Score: {stats['highest_score']:.1f}%")
        print(f"Lowest Score: {stats['lowest_score']:.1f}%")
        print(f"Pass Rate (≥60%): {stats['pass_rate']:.1f}%")
        
        # Show individual scores
        print(f"\n--- Individual Scores ---")
        headers = ["Student", "Score", "Percentage", "Grade"]
        widths = [25, 12, 12, 8]
        
        print(DisplayFormatter.format_table_header(headers, widths))
        
        # Sort by score descending
        sorted_submissions = sorted(
            assignment_submissions,
            key=lambda s: s['total_score'] / s['max_score'] if s['max_score'] > 0 else 0,
            reverse=True
        )
        
        for submission in sorted_submissions:
            percentage = PerformanceCalculator.calculate_percentage(
                submission['total_score'],
                submission['max_score']
            )
            grade = PerformanceCalculator.get_grade_letter(percentage)
            score_display = DisplayFormatter.format_score(
                submission['total_score'],
                submission['max_score']
            )
            
            row = [
                submission['student_name'],
                score_display,
                f"{percentage:.1f}%",
                grade
            ]
            
            print(DisplayFormatter.format_table_row(row, widths))
    
    def _generate_students_overview(self):
        """Generate overview of all students managed by this teacher"""
        print("\n--- My Students Overview ---")
        
        students = self.db_manager.get_students_by_teacher(self.id)
        if not students:
            print("You haven't added any students yet.")
            return
        
        active_students = [s for s in students if s['is_active']]
        inactive_students = [s for s in students if not s['is_active']]
        
        print(f"Total Students Added: {len(students)}")
        print(f"Active Students: {len(active_students)}")
        print(f"Inactive Students: {len(inactive_students)}")
        
        # Performance summary for active students
        print(f"\n--- Active Students Performance ---")
        headers = ["Name", "Login Code", "Submissions", "Avg Score", "Best Grade"]
        widths = [20, 12, 12, 12, 10]
        
        print(DisplayFormatter.format_table_header(headers, widths))
        
        for student in active_students:
            submissions = self.db_manager.get_student_submissions(student['id'])
            
            # Filter for this teacher's assignments
            teacher_assignments = self.db_manager.get_assignments(teacher_id=self.id)
            teacher_assignment_ids = [a['id'] for a in teacher_assignments]
            relevant_submissions = [s for s in submissions if s['assignment_id'] in teacher_assignment_ids]
            
            if relevant_submissions:
                # Calculate average score
                total_score = sum(s['total_score'] for s in relevant_submissions)
                total_possible = sum(s['max_score'] for s in relevant_submissions)
                avg_percentage = (total_score / total_possible) * 100 if total_possible > 0 else 0
                
                # Find best grade
                best_percentage = max(
                    (s['total_score'] / s['max_score']) * 100 for s in relevant_submissions if s['max_score'] > 0
                ) if relevant_submissions else 0
                best_grade = PerformanceCalculator.get_grade_letter(best_percentage)
                
                row = [
                    student['name'],
                    student['login_code'],
                    len(relevant_submissions),
                    f"{avg_percentage:.1f}%",
                    best_grade
                ]
            else:
                row = [
                    student['name'],
                    student['login_code'],
                    0,
                    "N/A",
                    "N/A"
                ]
            
            print(DisplayFormatter.format_table_row(row, widths))
    
    def view_assignment_statistics(self):
        """View detailed statistics for assignments"""
        self.display_header("Assignment Statistics")
        
        assignments = self.db_manager.get_assignments(teacher_id=self.id)
        if not assignments:
            print("No assignments created yet.")
            return
        
        print("Assignment Statistics Summary:")
        headers = ["ID", "Title", "Submissions", "Avg Score", "Difficulty"]
        widths = [5, 25, 12, 12, 12]
        
        print(DisplayFormatter.format_table_header(headers, widths))
        
        for assignment in assignments:
            # Get submissions for this assignment
            students = self.db_manager.get_all_students()
            assignment_submissions = []
            
            for student in students:
                submissions = self.db_manager.get_student_submissions(student['id'])
                assignment_submissions.extend([s for s in submissions if s['assignment_id'] == assignment['id']])
            
            submission_count = len(assignment_submissions)
            
            if assignment_submissions:
                # Calculate average score
                total_score = sum(s['total_score'] for s in assignment_submissions)
                total_possible = sum(s['max_score'] for s in assignment_submissions)
                avg_percentage = (total_score / total_possible) * 100 if total_possible > 0 else 0
                
                # Determine difficulty level
                if avg_percentage >= 80:
                    difficulty = "Easy"
                elif avg_percentage >= 60:
                    difficulty = "Medium"
                else:
                    difficulty = "Hard"
                
                avg_display = f"{avg_percentage:.1f}%"
            else:
                avg_display = "N/A"
                difficulty = "N/A"
            
            row = [
                assignment['id'],
                assignment['title'],
                submission_count,
                avg_display,
                difficulty
            ]
            
            print(DisplayFormatter.format_table_row(row, widths))
        
        print(f"\nTotal Assignments: {len(assignments)}")
