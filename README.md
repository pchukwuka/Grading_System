# Smart Grading and Feedback System

A Python-based command-line application designed to automate the grading process and provide personalized feedback to students at Emene High School, Enugu State, Nigeria.

##  Project Overview

This system addresses the challenges faced by overcrowded classrooms (up to 100 students per class) by:
- Automating objective question grading (multiple choice, true/false)
- Providing instant feedback to students
- Tracking student performance over time
- Reducing teacher administrative burden
- Enabling personalized learning experiences

##  Features

### For Teachers:
- **Assignment Creation**: Create assignments with objective and subjective questions
- **Automated Grading**: Automatic grading for multiple choice and true/false questions
- **Student Management**: View all registered students and their performance
- **Progress Tracking**: Generate detailed reports and analytics
- **Submission Review**: Review and grade student submissions

### For Students:
- **Assignment Viewing**: Browse available assignments
- **Assignment Submission**: Submit answers with immediate objective feedback
- **Grade Tracking**: View grades and detailed feedback
- **Performance Analysis**: Track performance trends and improvements
- **Assignment Preview**: View assignment details before attempting

##  System Requirements

- Python 3.6 or higher
- SQLite (included with Python)
- Command-line interface (Terminal/Command Prompt)

##  Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/pchukwuka/Grading_System.git
   cd smart-grading-system
   ```

2. **Ensure Python 3.6+ is installed:**
   ```bash
   python --version
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

##  How to Run

1. Open your terminal/command prompt
2. Navigate to the project directory
3. Run the main application:
   ```bash
   python main.py
   ```
4. Follow the on-screen prompts to select your role (Teacher/Student)
5. Use the provided default accounts for testing
6. The student login credetials are provided by the teacher

##  Default Test Accounts

### Teachers:
- Username: `Kevin`, Password: `password123` (Mr. Kevin)
- Username: `Peace`, Password: `password123` (Mrs.Peace)


##  Project Structure

```
smart-grading-system/
├── main.py                 # Application entry point
├── auth.py                 # Authentication and input validation
├── database.py             # Database operations and management
├── teacher.py              # Teacher-specific functionality
├── student.py              # Student-specific functionality
├── requirements.txt        # Project dependencies
├── README.md               # Project documentation
└── smart_grading.db        # SQLite database (created automatically)
```

##  Usage Guide

### Teacher Workflow:
1. **Login** with teacher credentials
2. **Create Assignment** - Add questions (objective/subjective)
3. **View Assignments** - Monitor created assignments
4. **Grade & Review** - Check student submissions
5. **Generate Reports** - Analyze class performance

### Student Workflow:
1. **Login** with student credentials provided by the teacher
2. **View Assignments** - Browse available assignments
3. **Submit Answers** - Complete and submit assignments
4. **Check Grades** - View scores and feedback
5. **Track Progress** - Monitor performance trends

##  Database Schema

The system uses SQLite with the following main tables:
- **users** - Teacher and student accounts
- **assignments** - Assignment information
- **questions** - Individual questions within assignments
- **submissions** - Student assignment submissions
- **answers** - Individual question responses

##  Key Features Explained

### Automated Grading
- **Objective Questions**: Instantly graded upon submission
- **Multiple Choice**: A, B, C, D options with single correct answer
- **True/False**: Binary choice questions
- **Scoring**: Immediate point calculation and feedback

### Feedback System
- **Instant Results**: Immediate feedback for objective questions
- **Detailed Reports**: Question-by-question breakdown
- **Performance Trends**: Track improvement over time
- **Personalized Messages**: Contextual feedback based on performance

### Performance Analytics
- **Individual Reports**: Detailed student performance analysis
- **Class Summaries**: Overall class performance metrics
- **Assignment Statistics**: Question-level difficulty analysis
- **Trend Analysis**: Performance improvement tracking

##  Technical Implementation

### Core Technologies:
- **Python 3.6+**: Main programming language
- **SQLite**: Lightweight database for data storage
- **JSON**: Data serialization for complex structures
- **Command Line Interface**: Terminal-based user interaction

### Error Handling:
- Input validation for all user entries
- Database connection error management
- Graceful handling of invalid operations
- User-friendly error messages

### Security Features:
- Password-protected user accounts
- Role-based access control
- Input sanitization
- Session management

##  Future Enhancements

- **Advanced Analytics**: Machine learning for performance prediction
- **File Uploads**: Support for document and image submissions
- **Real-time Notifications**: Instant updates for new assignments

##  Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

##  License

This project is developed for educational purposes at African Leadership College Of Higher Education(ALCHE)

##  Academic Context

This project is part of Peer Learning Project (PLP) 2. It demonstrates:
- **Application Development**: Full-stack Python application
- **Database Integration**: SQLite database design and implementation
- **Problem Solving**: Addressing real-world educational challenges
- **Team Collaboration**: Git-based version control and teamwork

---

**Smart Grading and Feedback System - Improving education one grade at a time.**
