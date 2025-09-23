"""
Base User class for Smart Grading and Feedback System - OOP Version
Contains common functionality for all user types
"""

from abc import ABC, abstractmethod
import os

class User(ABC):
    """Abstract base class for all users in the system"""
    
    def __init__(self, user_data, db_manager):
        """
        Initialize user with data and database manager
        
        Args:
            user_data (dict): User information from database
            db_manager (DatabaseManager): Database manager instance
        """
        self.id = user_data['id']
        self.name = user_data['name']
        self.role = user_data['role']
        self.db_manager = db_manager
        self._user_data = user_data
    
    def get_id(self):
        """Get user ID"""
        return self.id
    
    def get_name(self):
        """Get user name"""
        return self.name
    
    def get_role(self):
        """Get user role"""
        return self.role
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def wait_for_input(self, message="Press Enter to continue..."):
        """Wait for user input before continuing"""
        input(f"\n{message}")
    
    def display_header(self, title):
        """Display a formatted header"""
        print(f"\n{'='*60}")
        print(f"    {title.upper()}")
        print(f"    User: {self.name} ({self.role.title()})")
        print(f"{'='*60}")
    
    def display_menu_header(self, title):
        """Display menu header"""
        print(f"\n--- {title} - {self.name} ---")
    
    def validate_input(self, prompt, input_type="string", min_length=1, max_length=None, valid_choices=None):
        """
        Validate user input with specified criteria
        Delegates to AuthenticationManager's method
        """
        from auth import AuthenticationManager
        auth_manager = AuthenticationManager(self.db_manager)
        return auth_manager.validate_input(prompt, input_type, min_length, max_length, valid_choices)
    
    def confirm_action(self, message):
        """
        Ask user to confirm an action
        Delegates to AuthenticationManager's method
        """
        from auth import AuthenticationManager
        auth_manager = AuthenticationManager(self.db_manager)
        return auth_manager.confirm_action(message)
    
    @abstractmethod
    def show_menu(self):
        """Display the main menu for the user type"""
        pass
    
    @abstractmethod
    def logout(self):
        """Handle user logout"""
        pass

class MenuOption:
    """Class to represent a menu option"""
    
    def __init__(self, number, description, function):
        """
        Initialize menu option
        
        Args:
            number (str): Menu option number
            description (str): Option description
            function (callable): Function to call when option is selected
        """
        self.number = number
        self.description = description
        self.function = function
    
    def display(self):
        """Display the menu option"""
        print(f"{self.number}. {self.description}")
    
    def execute(self):
        """Execute the menu option function"""
        try:
            return self.function()
        except Exception as e:
            print(f"Error executing menu option: {e}")
            return False

class MenuManager:
    """Manages menu display and selection"""
    
    def __init__(self, user):
        """
        Initialize menu manager
        
        Args:
            user (User): User instance
        """
        self.user = user
        self.options = []
    
    def add_option(self, number, description, function):
        """Add a menu option"""
        option = MenuOption(number, description, function)
        self.options.append(option)
    
    def display_menu(self, title):
        """Display the menu"""
        self.user.display_menu_header(title)
        for option in self.options:
            option.display()
    
    def get_user_choice(self):
        """Get and validate user menu choice"""
        valid_choices = [option.number for option in self.options]
        return self.user.validate_input(
            f"\nSelect an option ({'/'.join(valid_choices)}): ",
            "choice",
            valid_choices=valid_choices
        )
    
    def execute_choice(self, choice):
        """Execute the selected menu option"""
        for option in self.options:
            if option.number == choice:
                return option.execute()
        return False
    
    def run_menu_loop(self, title):
        """Run the main menu loop"""
        while True:
            self.display_menu(title)
            choice = self.get_user_choice()
            
            if not choice:
                continue
            
            if choice.upper() == 'Q' or choice == '0':
                break
            
            result = self.execute_choice(choice)
            
            # If logout was selected, break the loop
            if choice == str(len(self.options)) or result == "logout":
                break
            
            self.user.wait_for_input()

class PerformanceCalculator:
    """Utility class for calculating performance metrics"""
    
    @staticmethod
    def calculate_percentage(score, max_score):
        """Calculate percentage score"""
        if max_score == 0:
            return 0
        return (score / max_score) * 100
    
    @staticmethod
    def get_grade_letter(percentage):
        """Get letter grade based on percentage"""
        if percentage >= 90:
            return "A"
        elif percentage >= 80:
            return "B"
        elif percentage >= 70:
            return "C"
        elif percentage >= 60:
            return "D"
        else:
            return "F"
    
    @staticmethod
    def get_grade_description(percentage):
        """Get grade description based on percentage"""
        if percentage >= 90:
            return "Excellent"
        elif percentage >= 80:
            return "Very Good"
        elif percentage >= 70:
            return "Good"
        elif percentage >= 60:
            return "Satisfactory"
        else:
            return "Needs Improvement"
    
    @staticmethod
    def calculate_class_statistics(submissions):
        """Calculate class-wide statistics"""
        if not submissions:
            return {
                'total_submissions': 0,
                'average_score': 0,
                'highest_score': 0,
                'lowest_score': 0,
                'pass_rate': 0
            }
        
        scores = []
        for submission in submissions:
            if submission['max_score'] > 0:
                percentage = (submission['total_score'] / submission['max_score']) * 100
                scores.append(percentage)
        
        if not scores:
            return {
                'total_submissions': len(submissions),
                'average_score': 0,
                'highest_score': 0,
                'lowest_score': 0,
                'pass_rate': 0
            }
        
        passing_scores = [s for s in scores if s >= 60]  # Assuming 60% is passing
        
        return {
            'total_submissions': len(submissions),
            'average_score': sum(scores) / len(scores),
            'highest_score': max(scores),
            'lowest_score': min(scores),
            'pass_rate': (len(passing_scores) / len(scores)) * 100 if scores else 0
        }

class DisplayFormatter:
    """Utility class for formatting display output"""
    
    @staticmethod
    def format_table_row(columns, widths):
        """Format a table row with specified column widths"""
        formatted_columns = []
        for i, column in enumerate(columns):
            width = widths[i]
            if len(str(column)) > width:
                formatted_columns.append(str(column)[:width-3] + "...")
            else:
                formatted_columns.append(f"{str(column):<{width}}")
        return " ".join(formatted_columns)
    
    @staticmethod
    def format_table_header(headers, widths):
        """Format table header with separators"""
        header_row = DisplayFormatter.format_table_row(headers, widths)
        separator = "-" * len(header_row)
        return f"{header_row}\n{separator}"
    
    @staticmethod
    def format_date(date_string):
        """Format date string for display"""
        if not date_string:
            return "N/A"
        try:
            # Assuming date_string is in format "YYYY-MM-DD HH:MM:SS"
            return date_string[:10]  # Return just the date part
        except:
            return str(date_string)[:10]
    
    @staticmethod
    def format_score(score, max_score):
        """Format score for display"""
        return f"{score:.1f}/{max_score}"
    
    @staticmethod
    def format_percentage(score, max_score):
        """Format percentage for display"""
        if max_score == 0:
            return "0.0%"
        percentage = (score / max_score) * 100
        return f"{percentage:.1f}%"
