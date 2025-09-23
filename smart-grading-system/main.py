#!/usr/bin/python3
"""
Smart Grading and Feedback System - OOP Version
Main application entry point with Object-Oriented Design
"""

import os
import sys
from auth import AuthenticationManager
from teacher import Teacher
from student import Student
from database import DatabaseManager

class SmartGradingApp:
    """Main application class that manages the entire system"""
    
    def __init__(self):
        """Initialize the application"""
        self.db_manager = DatabaseManager()
        self.auth_manager = AuthenticationManager(self.db_manager)
        self.current_user = None
        
    def clear_screen(self):
        """Clear the terminal screen for better user experience"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_welcome(self):
        """Display welcome message and application information"""
        self.clear_screen()
        print("=" * 60)
        print("    SMART GRADING AND FEEDBACK SYSTEM")
        print("    Emene High School - Enugu State")
        print("    Object-Oriented Programming Version")
        print("=" * 60)
        print("\nWelcome to the Smart Grading and Feedback System!")
        print("This application helps teachers manage assignments and")
        print("provides students with automated grading and feedback.")
        print("\nNew Features:")
        print("• Teacher-managed student registration")
        print("• Auto-generated student login codes")
        print("• Object-oriented design for better maintainability")
        print("• Enhanced user experience")
        print("\n" + "=" * 60)
    
    def get_user_role(self):
        """Get user role selection with input validation"""
        while True:
            print("\nPlease select your role:")
            print("1. Teacher")
            print("2. Student")
            print("3. Exit")
            
            choice = input("\nEnter your choice (1-3): ").strip()
            
            if choice == '1':
                return 'teacher'
            elif choice == '2':
                return 'student'
            elif choice == '3':
                return 'exit'
            else:
                print("Invalid choice! Please enter 1, 2, or 3.")
    
    def run(self):
        """Main method to run the application"""
        try:
            # Initialize database
            print("Initializing system...")
            self.db_manager.initialize_database()
            
            # Display welcome screen
            self.display_welcome()
            
            while True:
                # Get user role
                role = self.get_user_role()
                
                if role == 'exit':
                    self.exit_program()
                    break
                
                # Authenticate user
                user_data = self.auth_manager.authenticate_user(role)
                if user_data:
                    self.current_user = self.create_user_object(user_data, role)
                    if self.current_user:
                        self.clear_screen()
                        print(f"Welcome, {self.current_user.get_name()}!")
                        self.current_user.show_menu()
                else:
                    input("\nPress Enter to continue...")
                    self.clear_screen()
                    self.display_welcome()
        
        except KeyboardInterrupt:
            print("\n\nApplication interrupted by user.")
            self.exit_program()
        except Exception as e:
            print(f"\nAn error occurred: {e}")
            print("Please contact system administrator.")
            self.exit_program()
    
    def create_user_object(self, user_data, role):
        """Create appropriate user object based on role"""
        try:
            if role == 'teacher':
                return Teacher(user_data, self.db_manager)
            elif role == 'student':
                return Student(user_data, self.db_manager)
            return None
        except Exception as e:
            print(f"Error creating user object: {e}")
            return None
    
    def exit_program(self):
        """Safely exit the program"""
        self.clear_screen()
        print("=" * 60)
        print("    Thank you for using Smart Grading System!")
        print("    Improving education one grade at a time.")
        print("=" * 60)
        print("\nGoodbye!")
        sys.exit(0)

def main():
    """Main function to start the application"""
    app = SmartGradingApp()
    app.run()

if __name__ == "__main__":
    main()
