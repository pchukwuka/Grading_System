#!/usr/bin/python3

"""
Student class for Smart Grading and Feedback System - OOP Version
Handles all student-related operations using Object-Oriented Design
"""

import json
from user import User, MenuManager, PerformanceCalculator, DisplayFormatter

class Student(User):
    """Student class with all student-specific functionality"""
    
    def __init__(self, user_data, db_manager):
        """Initialize student with user data and database manager"""
        super().__init__(user_data, db_manager)
        self.login_code = user_data.get('login_code', '')
        self.menu_manager = MenuManager(self)
        self._setup_menu()
    
    def _setup_menu(self):
        """Set up student menu options"""
        self.menu_manager.add_option("1", "View Available Assignments", self.view_available_assignments)
        self.menu_manager.add_option("2", "Submit Assignment", self.submit_assignment)
        self.menu_manager.add_option("3", "View My Grades & Feedback", self.view_grades_and_feedback)
        self.menu_manager.add_option("4", "View Performance Summary", self.view_performance_summary)
        self.menu_manager.add_option("5", "View Assignment Details", self.view_assignment_details)
        self.menu_manager.add_option("6", "Logout", self.logout)
    
    def show_menu(self):
        """Display student menu and handle operations"""
        print(f"Login Code: {self.login_code}")  # Show login code for reference
        self.menu_manager.run_menu_loop("Student Dashboard")
    
    def logout(self):
        """Handle student logout"""
        print("Logging out...")
        return "logout"
    
    def view_available_assignments(self):
        """Display all available assignments"""
        self.display_header("Available Assignments")
        
        assignments = self.db_manager.get_assignments()  # Get all assignments
        
        if not assignments:
            print("No assignments available at the moment.")
            return
        
        # Check which assignments this student has already submitted
        my_submissions = self.db_manager.get_student_submissions(self.id)
        submitted_assignment_ids = [s['assignment_id'] for s in my_submissions]
        
        headers = ["ID", "Title", "Teacher", "Points", "Created", "Status"]
        widths = [5, 25, 20, 8, 12, 12]
        
        print(DisplayFormatter.format_table_header(headers, widths))
        
        for assignment in assignments:
            created_date = DisplayFormatter.format_date(assignment['created_at'])
            
            # Check submission status
            if assignment['id'] in submitted_assignment_ids:
                status = "Submitted"
            else:
                status = "Not Started"
            
            row = [
                assignment['id'],
                assignment['title'],
                assignment['teacher_name'],
                assignment['total_points'],
                created_date,
                status
            ]
            
            print(DisplayFormatter.format_table_row(row, widths))
        
        print(f"\nTotal Assignments: {len(assignments)}")
        
        # Show submission statistics
        total_submitted = len([a for a in assignments if a['id'] in submitted_assignment_ids])
        completion_rate = (total_submitted / len(assignments)) * 100 if assignments else 0
        
        print(f"Assignments Submitted: {total_submitted}")
        print(f"Completion Rate: {completion_rate:.1f}%")
    
    def submit_assignment(self):
        """Allow student to submit an assignment"""
        self.display_header("Submit Assignment")
        
        assignments = self.db_manager.get_assignments()
        
        if not assignments:
            print("No assignments available to submit.")
            return
        
        # Show available assignments with submission status
        my_submissions = self.db_manager.get_student_submissions(self.id)
        submitted_assignment_ids = [s['assignment_id'] for s in my_submissions]
        
        print("Available assignments:")
        headers = ["ID", "Title", "Teacher", "Points", "Status"]
        widths = [5, 30, 20, 8, 12]
        
        print(DisplayFormatter.format_table_header(headers, widths))
        
        for assignment in assignments:
            status = "Submitted" if assignment['id'] in submitted_assignment_ids else "Available"
            
            row = [
                assignment['id'],
                assignment['title'],
                assignment['teacher_name'],
                assignment['total_points'],
                status
            ]
            
            print(DisplayFormatter.format_table_row(row, widths))
        
        # Get assignment choice
        assignment_id = self.validate_input(
            "\nEnter assignment ID to submit: ",
            "integer",
            min_length=1
        )
        if not assignment_id:
            return
        
        # Check if assignment exists
        selected_assignment = next((a for a in assignments if a['id'] == assignment_id), None)
        if not selected_assignment:
            print("Invalid assignment ID!")
            return
        
        # Check if already submitted
        if assignment_id in submitted_assignment_ids:
            print(f"\nYou have already submitted '{selected_assignment['title']}'.")
            if not self.confirm_action("Do you want to resubmit? This will replace your previous submission."):
                return
        
        # Get assignment questions
        questions = self.db_manager.get_assignment_questions(assignment_id)
        
        if not questions:
            print("This assignment has no questions!")
            return
        
        # Start assignment submission process
        self._process_assignment_submission(selected_assignment, questions)
    
    def _process_assignment_submission(self, assignment, questions):
        """Process the assignment submission"""
        print(f"\n{'='*60}")
        print(f"    {assignment['title'].upper()}")
        print(f"    Teacher: {assignment['teacher_name']}")
        print(f"{'='*60}")
        print(f"Total Points: {assignment['total_points']}")
        print(f"Number of Questions: {len(questions)}")
        print(f"\nInstructions:")
        print("• Read each question carefully")
        print("• For multiple choice, enter A, B, C, or D")
        print("• For essays, provide detailed answers")
        print("• Type 'skip' to leave a question blank")
        print("• You can review your answers before final submission")
        print(f"{'='*60}")
        
        if not self.confirm_action("Ready to start the assignment?"):
            return
        
        answers = {}
        
        # Process each question
        for i, question in enumerate(questions):
            self.clear_screen()
            self._display_question_progress(i + 1, len(questions), assignment['title'])
            
            answer = self._get_question_answer(question, i)
            if answer is not None:  # None means user cancelled
                answers[str(i)] = answer
            else:
                return  # User cancelled
        
        # Review answers before submission
        if self._review_answers(assignment, questions, answers):
            self._submit_answers(assignment['id'], answers)
    
    def _display_question_progress(self, current, total, assignment_title):
        """Display question progress"""
        progress = (current / total) * 100
        progress_bar = "█" * int(progress // 5) + "░" * (20 - int(progress // 5))
        
        print(f"Assignment: {assignment_title}")
        print(f"Progress: [{progress_bar}] {current}/{total} ({progress:.1f}%)")
        print("-" * 60)
    
    def _get_question_answer(self, question, question_index):
        """Get answer for a single question"""
        print(f"\nQuestion {question_index + 1} ({question['points']} points)")
        print(f"Type: {question['question_type'].title()}")
        print("-" * 40)
        print(f"\n{question['question_text']}")
        
        if question['question_type'] == 'objective':
            return self._get_objective_answer(question)
        else:
            return self._get_subjective_answer(question)
    
    def _get_objective_answer(self, question):
        """Get answer for objective question"""
        if question['options']:
            try:
                options = json.loads(question['options'])
                print("\nOptions:")
                for option in options:
                    print(f"  {option}")
                
                valid_choices = ['A', 'B', 'C', 'D'] if len(options) > 2 else ['A', 'B']
                valid_choices.append('SKIP')
                
                while True:
                    answer = self.validate_input(
                        f"\nYour answer ({'/'.join(valid_choices[:-1])} or 'skip'): ",
                        "choice",
                        valid_choices=valid_choices
                    )
                    
                    if answer is None:  # User cancelled
                        return None
                    elif answer == 'SKIP':
                        return ''
                    else:
                        return answer
                        
            except json.JSONDecodeError:
                print("\nError displaying options.")
                return self.validate_input("Your answer: ", "string", 0, 200)
        else:
            return self.validate_input("Your answer: ", "string", 0, 200)
    
    def _get_subjective_answer(self, question):
        """Get answer for subjective question"""
        print("\nInstructions for essay questions:")
        print("• Write your complete answer")
        print("• Press Enter twice when finished")
        print("• Type 'skip' on first line to skip this question")
        print("-" * 40)
        
        print("\nYour answer:")
        answer_lines = []
        
        first_line = input()
        if first_line.strip().upper() == 'SKIP':
            return ''
        
        answer_lines.append(first_line)
        
        # Continue reading lines until double enter
        consecutive_empty = 0
        while consecutive_empty < 2:
            try:
                line = input()
                if line.strip() == '':
                    consecutive_empty += 1
                else:
                    consecutive_empty = 0
                answer_lines.append(line)
            except KeyboardInterrupt:
                if self.confirm_action("Cancel this question?"):
                    return None
                consecutive_empty = 0
        
        # Remove trailing empty lines
        while answer_lines and answer_lines[-1].strip() == '':
            answer_lines.pop()
        
        answer = '\n'.join(answer_lines)
        
        # Show preview of long answers
        if len(answer) > 100:
            preview = answer[:100] + "..."
            print(f"\nAnswer preview: {preview}")
            if not self.confirm_action("Keep this answer?"):
                return self._get_subjective_answer(question)
        
        return answer
    
    def _review_answers(self, assignment, questions, answers):
        """Review answers before final submission"""
        self.clear_screen()
        print(f"{'='*60}")
        print(f"    REVIEW YOUR ANSWERS")
        print(f"    Assignment: {assignment['title']}")
        print(f"{'='*60}")
        
        for i, question in enumerate(questions):
            answer = answers.get(str(i), '')
            
            print(f"\nQuestion {i+1}: {question['question_text'][:60]}...")
            
            if question['question_type'] == 'objective':
                display_answer = answer if answer else 'No answer'
                print(f"Your answer: {display_answer}")
            else:
                if answer:
                    display_answer = answer[:100] + "..." if len(answer) > 100 else answer
                    display_answer = display_answer.replace('\n', ' ')
                    print(f"Your answer: {display_answer}")
                else:
                    print("Your answer: No answer provided")
        
        print(f"\n{'='*60}")
        answered = len([a for a in answers.values() if a.strip()])
        print(f"Questions answered: {answered}/{len(questions)}")
        
        if answered < len(questions):
            unanswered = len(questions) - answered
            print(f"Warning: {unanswered} questions left blank")
        
        return self.confirm_action("\nSubmit this assignment?")
    
    def _submit_answers(self, assignment_id, answers):
        """Submit the answers to database"""
        print("\nSubmitting assignment...")
        
        submission_data = {
            'assignment_id': assignment_id,
            'student_id': self.id,
            'answers': answers
        }
        
        if self.db_manager.save_submission(submission_data):
            print("\n" + "="*50)
            print("    ASSIGNMENT SUBMITTED SUCCESSFULLY!")
            print("="*50)
            print("Your assignment has been submitted and graded automatically.")
            print("Objective questions are graded immediately.")
            print("You can view your results in 'View My Grades & Feedback'.")
            print("="*50)
        else:
            print("Error submitting assignment. Please try again or contact your teacher.")
    
    def view_grades_and_feedback(self):
        """Display student's grades and feedback"""
        self.display_header("My Grades & Feedback")
        
        submissions = self.db_manager.get_student_submissions(self.id)
        
        if not submissions:
            print("You haven't submitted any assignments yet.")
            print("\nTip: Go to 'View Available Assignments' to see what you can work on!")
            return
        
        # Display submissions table
        headers = ["Assignment", "Score", "Percentage", "Grade", "Teacher", "Date"]
        widths = [25, 12, 12, 8, 15, 12]
        
        print(DisplayFormatter.format_table_header(headers, widths))
        
        for submission in submissions:
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
                submission['teacher_name'],
                submitted_date
            ]
            
            print(DisplayFormatter.format_table_row(row, widths))
        
        print(f"\nTotal Submissions: {len(submissions)}")
        
        # Option to view detailed feedback
        if self.confirm_action("\nView detailed feedback for an assignment?"):
            self._select_and_view_feedback(submissions)
    
    def _select_and_view_feedback(self, submissions):
        """Select and view detailed feedback for an assignment"""
        print("\nYour submissions:")
        
        for i, submission in enumerate(submissions, 1):
            percentage = PerformanceCalculator.calculate_percentage(
                submission['total_score'],
                submission['max_score']
            )
            print(f"{i}. {submission['title']} - {percentage:.1f}%")
        
        choice = self.validate_input(
            f"\nSelect assignment (1-{len(submissions)}): ",
            "integer",
            min_length=1,
            max_length=len(submissions)
        )
        
        if choice and 1 <= choice <= len(submissions):
            selected_submission = submissions[choice - 1]
            self._view_detailed_feedback(selected_submission['id'])
    
    def _view_detailed_feedback(self, submission_id):
        """Display detailed feedback for a specific submission"""
        self.display_header("Detailed Feedback")
        
        submission_details = self.db_manager.get_submission_details(submission_id)
        
        if not submission_details:
            print("Submission details not found.")
            return
        
        # Display submission summary
        percentage = PerformanceCalculator.calculate_percentage(
            submission_details['total_score'],
            submission_details['max_score']
        )
        grade = PerformanceCalculator.get_grade_letter(percentage)
        grade_description = PerformanceCalculator.get_grade_description(percentage)
        
        print(f"Assignment: {submission_details['title']}")
        print(f"Total Score: {DisplayFormatter.format_score(submission_details['total_score'], submission_details['max_score'])}")
        print(f"Percentage: {percentage:.1f}%")
        print(f"Grade: {grade} ({grade_description})")
        print(f"Submitted: {DisplayFormatter.format_date(submission_details['submitted_at'])}")
        
        print(f"\n{'='*60}")
        print("    QUESTION-BY-QUESTION FEEDBACK")
        print(f"{'='*60}")
        
        # Display each question with feedback
        for i, answer in enumerate(submission_details['answers'], 1):
            print(f"\n--- Question {i} ({answer['points']} points) ---")
            print(f"Question: {answer['question_text']}")
            
            # Display student's answer
            if answer['student_answer']:
                if answer['question_type'] == 'objective':
                    print(f"Your Answer: {answer['student_answer']}")
                else:
                    # For subjective, show first 200 characters
                    display_answer = answer['student_answer']
                    if len(display_answer) > 200:
                        display_answer = display_answer[:200] + "..."
                    print(f"Your Answer: {display_answer}")
            else:
                print("Your Answer: No answer provided")
            
            # Show correct answer for objective questions
            if answer['question_type'] == 'objective' and answer['correct_answer']:
                print(f"Correct Answer: {answer['correct_answer']}")
            
            # Display score and feedback
            score_display = DisplayFormatter.format_score(answer['score'], answer['points'])
            print(f"Points Earned: {score_display}")
            print(f"Feedback: {answer['feedback']}")
        
        # Show improvement suggestions
        self._show_improvement_suggestions(submission_details)
    
    def _show_improvement_suggestions(self, submission_details):
        """Show personalized improvement suggestions"""
        percentage = PerformanceCalculator.calculate_percentage(
            submission_details['total_score'],
            submission_details['max_score']
        )
        
        print(f"\n{'='*60}")
        print("    IMPROVEMENT SUGGESTIONS")
        print(f"{'='*60}")
        
        if percentage >= 90:
            print(" Excellent work! You've mastered this material.")
            print("• Continue practicing to maintain this level")
            print("• Consider helping classmates who might be struggling")
        elif percentage >= 80:
            print(" Very good work! You have a strong understanding.")
            print("• Review questions you missed to reach excellence")
            print("• Focus on careful reading of questions")
        elif percentage >= 70:
            print(" Good effort! You're on the right track.")
            print("• Review the material for topics you missed")
            print("• Practice similar questions to improve understanding")
            print("• Consider asking your teacher for additional help")
        elif percentage >= 60:
            print("  You're passing, but there's room for improvement.")
            print("• Schedule a meeting with your teacher for help")
            print("• Review course materials thoroughly")
            print("• Form a study group with classmates")
        else:
            print(" This assignment shows you need additional support.")
            print("• Meet with your teacher as soon as possible")
            print("• Review fundamental concepts")
            print("• Consider tutoring or additional study sessions")
            print("• Don't hesitate to ask questions in class")
        
        # Analyze question types for specific suggestions
        objective_questions = [a for a in submission_details['answers'] if a['question_type'] == 'objective']
        subjective_questions = [a for a in submission_details['answers'] if a['question_type'] == 'subjective']
        
        if objective_questions:
            objective_score = sum(a['score'] for a in objective_questions)
            objective_max = sum(a['points'] for a in objective_questions)
            objective_percentage = (objective_score / objective_max) * 100 if objective_max > 0 else 0
            
            print(f"\nMultiple Choice Performance: {objective_percentage:.1f}%")
            if objective_percentage < 70:
                print("• Focus on reading questions more carefully")
                print("• Eliminate obviously wrong answers first")
                print("• Review key concepts and definitions")
        
        if subjective_questions:
            subjective_score = sum(a['score'] for a in subjective_questions)
            subjective_max = sum(a['points'] for a in subjective_questions)
            subjective_percentage = (subjective_score / subjective_max) * 100 if subjective_max > 0 else 0
            
            print(f"\nEssay/Short Answer Performance: {subjective_percentage:.1f}%")
            if subjective_percentage < 70:
                print("• Provide more detailed explanations")
                print("• Use specific examples to support your points")
                print("• Practice writing clear, organized responses")
    
    def view_performance_summary(self):
        """Display student's overall performance summary"""
        self.display_header("Performance Summary")
        
        submissions = self.db_manager.get_student_submissions(self.id)
        
        if not submissions:
            print("No submissions to analyze yet.")
            print("\nStart by completing some assignments to see your progress!")
            return
        
        # Calculate overall statistics
        total_assignments = len(submissions)
        total_score = sum(s['total_score'] for s in submissions)
        total_possible = sum(s['max_score'] for s in submissions)
        
        overall_percentage = (total_score / total_possible) * 100 if total_possible > 0 else 0
        overall_grade = PerformanceCalculator.get_grade_letter(overall_percentage)
        grade_description = PerformanceCalculator.get_grade_description(overall_percentage)
        
        # Find best and worst performance
        best_submission = max(
            submissions,
            key=lambda s: (s['total_score'] / s['max_score']) * 100 if s['max_score'] > 0 else 0
        )
        worst_submission = min(
            submissions,
            key=lambda s: (s['total_score'] / s['max_score']) * 100 if s['max_score'] > 0 else 0
        )
        
        best_percentage = (best_submission['total_score'] / best_submission['max_score']) * 100 if best_submission['max_score'] > 0 else 0
        worst_percentage = (worst_submission['total_score'] / worst_submission['max_score']) * 100 if worst_submission['max_score'] > 0 else 0
        
        # Display summary
        print(f"{'='*50}")
        print(f"    ACADEMIC PERFORMANCE SUMMARY")
        print(f"{'='*50}")
        print(f"Total Assignments Completed: {total_assignments}")
        print(f"Overall Score: {total_score:.1f}/{total_possible}")
        print(f"Overall Percentage: {overall_percentage:.1f}%")
        print(f"Current Grade: {overall_grade} ({grade_description})")
        
        print(f"\n--- Performance Highlights ---")
        print(f"Best Performance: {best_submission['title']} ({best_percentage:.1f}%)")
        print(f"Needs Attention: {worst_submission['title']} ({worst_percentage:.1f}%)")
        
        # Performance trend analysis
        if len(submissions) >= 3:
            recent_submissions = sorted(submissions, key=lambda s: s['submitted_at'])[-3:]
            trend = self._analyze_performance_trend(recent_submissions)
            print(f"Recent Trend: {trend}")
        
        # Grade distribution
        print(f"\n--- Grade Distribution ---")
        grade_counts = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
        
        for submission in submissions:
            if submission['max_score'] > 0:
                percentage = (submission['total_score'] / submission['max_score']) * 100
                grade = PerformanceCalculator.get_grade_letter(percentage)
                grade_counts[grade] += 1
        
        for grade, count in grade_counts.items():
            if count > 0:
                percentage_of_total = (count / total_assignments) * 100
                print(f"Grade {grade}: {count} assignments ({percentage_of_total:.1f}%)")
        
        # Subject analysis (by teacher)
        self._analyze_performance_by_teacher(submissions)
        
        # Goals and recommendations
        self._show_performance_goals(overall_percentage)
    
    def _analyze_performance_trend(self, recent_submissions):
        """Analyze recent performance trend"""
        scores = []
        for submission in recent_submissions:
            if submission['max_score'] > 0:
                percentage = (submission['total_score'] / submission['max_score']) * 100
                scores.append(percentage)
        
        if len(scores) < 2:
            return "Insufficient data"
        
        # Simple trend analysis
        if scores[-1] > scores[0] + 5:  # 5% improvement threshold
            return " Improving (Keep up the good work!)"
        elif scores[-1] < scores[0] - 5:  # 5% decline threshold
            return " Declining (Consider additional study time)"
        else:
            return " Stable (Consistent performance)"
    
    def _analyze_performance_by_teacher(self, submissions):
        """Analyze performance by teacher/subject"""
        print(f"\n--- Performance by Teacher ---")
        
        # Group submissions by teacher
        teacher_performance = {}
        
        for submission in submissions:
            teacher = submission['teacher_name']
            if teacher not in teacher_performance:
                teacher_performance[teacher] = {'submissions': [], 'total_score': 0, 'total_possible': 0}
            
            teacher_performance[teacher]['submissions'].append(submission)
            teacher_performance[teacher]['total_score'] += submission['total_score']
            teacher_performance[teacher]['total_possible'] += submission['max_score']
        
        # Display performance by teacher
        for teacher, data in teacher_performance.items():
            if data['total_possible'] > 0:
                avg_percentage = (data['total_score'] / data['total_possible']) * 100
                grade = PerformanceCalculator.get_grade_letter(avg_percentage)
                assignment_count = len(data['submissions'])
                
                print(f"{teacher}: {avg_percentage:.1f}% (Grade {grade}) - {assignment_count} assignments")
    
    def _show_performance_goals(self, current_percentage):
        """Show performance goals and recommendations"""
        print(f"\n{'='*50}")
        print("    GOALS & RECOMMENDATIONS")
        print(f"{'='*50}")
        
        if current_percentage >= 90:
            print(" Goal: Maintain Excellence")
            print("• Continue your excellent study habits")
            print("• Challenge yourself with advanced topics")
            print("• Consider becoming a peer tutor")
            
        elif current_percentage >= 80:
            print(" Goal: Achieve Excellence (90%+)")
            print("• Review missed questions more thoroughly")
            print("• Spend extra time on challenging topics")
            print(f"• You need {90 - current_percentage:.1f}% improvement")
            
        elif current_percentage >= 70:
            print(" Goal: Reach Very Good Performance (80%+)")
            print("• Create a regular study schedule")
            print("• Ask questions during class")
            print("• Form study groups with classmates")
            print(f"• You need {80 - current_percentage:.1f}% improvement")
            
        elif current_percentage >= 60:
            print(" Goal: Achieve Good Performance (70%+)")
            print("• Meet with teachers for extra help")
            print("• Review fundamental concepts")
            print("• Consider additional practice exercises")
            print(f"• You need {70 - current_percentage:.1f}% improvement")
            
        else:
            print(" Priority Goal: Reach Passing Grade (60%+)")
            print("• Schedule immediate meetings with teachers")
            print("• Consider tutoring or remedial assistance")
            print("• Review basic concepts thoroughly")
            print(f"• You need {60 - current_percentage:.1f}% improvement")
        
        print(f"\n Remember: Every assignment is an opportunity to improve!")
    
    def view_assignment_details(self):
        """Allow student to view assignment details before attempting"""
        self.display_header("Assignment Details")
        
        assignments = self.db_manager.get_assignments()
        
        if not assignments:
            print("No assignments available.")
            return
        
        # Show available assignments
        print("Available assignments:")
        headers = ["ID", "Title", "Teacher", "Points", "Created"]
        widths = [5, 30, 20, 8, 12]
        
        print(DisplayFormatter.format_table_header(headers, widths))
        
        for assignment in assignments:
            created_date = DisplayFormatter.format_date(assignment['created_at'])
            
            row = [
                assignment['id'],
                assignment['title'],
                assignment['teacher_name'],
                assignment['total_points'],
                created_date
            ]
            
            print(DisplayFormatter.format_table_row(row, widths))
        
        assignment_id = self.validate_input(
            "\nEnter assignment ID to view details: ",
            "integer",
            min_length=1
        )
        if not assignment_id:
            return
        
        self._show_assignment_details(assignment_id)
    
    def _show_assignment_details(self, assignment_id):
        """Show detailed information about an assignment"""
        # Get assignment info
        assignments = self.db_manager.get_assignments()
        selected_assignment = next((a for a in assignments if a['id'] == assignment_id), None)
        
        if not selected_assignment:
            print("Assignment not found.")
            return
        
        # Get assignment questions
        questions = self.db_manager.get_assignment_questions(assignment_id)
        
        if not questions:
            print("Assignment has no questions.")
            return
        
        print(f"\n{'='*60}")
        print(f"    ASSIGNMENT DETAILS")
        print(f"{'='*60}")
        print(f"Title: {selected_assignment['title']}")
        print(f"Teacher: {selected_assignment['teacher_name']}")
        print(f"Total Points: {selected_assignment['total_points']}")
        print(f"Number of Questions: {len(questions)}")
        print(f"Created: {DisplayFormatter.format_date(selected_assignment['created_at'])}")
        
        if selected_assignment['description'] and selected_assignment['description'] != "No description provided":
            print(f"Description: {selected_assignment['description']}")
        
        # Question breakdown
        objective_count = sum(1 for q in questions if q['question_type'] == 'objective')
        subjective_count = sum(1 for q in questions if q['question_type'] == 'subjective')
        
        print(f"\n--- Question Breakdown ---")
        print(f"Multiple Choice/True-False: {objective_count} questions")
        print(f"Essay/Short Answer: {subjective_count} questions")
        
        # Check submission status
        my_submissions = self.db_manager.get_student_submissions(self.id)
        submission = next((s for s in my_submissions if s['assignment_id'] == assignment_id), None)
        
        if submission:
            percentage = PerformanceCalculator.calculate_percentage(
                submission['total_score'],
                submission['max_score']
            )
            print(f"\n--- Your Submission ---")
            print(f"Status: Submitted")
            print(f"Score: {DisplayFormatter.format_score(submission['total_score'], submission['max_score'])}")
            print(f"Percentage: {percentage:.1f}%")
            print(f"Submitted: {DisplayFormatter.format_date(submission['submitted_at'])}")
        else:
            print(f"\n--- Submission Status ---")
            print(f"Status: Not yet submitted")
            
            if self.confirm_action("Would you like to start this assignment now?"):
                self.clear_screen()
                self._process_assignment_submission(selected_assignment, questions)
                return
        
        # Show sample questions if requested
        if self.confirm_action("\nView sample questions?"):
            self._show_sample_questions(questions[:3])  # Show first 3 questions
    
    def _show_sample_questions(self, sample_questions):
        """Show sample questions from an assignment"""
        print(f"\n--- Sample Questions ---")
        
        for i, question in enumerate(sample_questions, 1):
            print(f"\nQuestion {i} ({question['points']} points):")
            print(f"Type: {question['question_type'].title()}")
            print(f"Question: {question['question_text']}")
            
            if question['question_type'] == 'objective' and question['options']:
                try:
                    options = json.loads(question['options'])
                    print("Options:")
                    for option in options:
                        print(f"  {option}")
                except json.JSONDecodeError:
                    pass
        
        if len(sample_questions) == 3:
            remaining = self.db_manager.get_assignment_questions(sample_questions[0]['assignment_id'])
            if len(remaining) > 3:
                print(f"\n... and {len(remaining) - 3} more questions")
