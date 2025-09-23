#!/usr/bin/python3

"""
Authentication module for Smart Grading and Feedback System - OOP Version
Handles user login and validation with Object-Oriented Design
"""

import getpass

class AuthenticationManager:
    """Manages user authentication and validation"""

    def __init__(self, db_manager):
        """Initialize with database manager"""
        self.db_manager = db_manager

    def authenticate_user(self, role):
        """
        Authenticate user based on role (teacher or student)
        Returns user data if successful, None if failed
        """
        if role == 'teacher':
            return self._authenticate_teacher()
        elif role == 'student':
            return self._authenticate_student()
        return None

    def _authenticate_teacher(self):
        """Authenticate teacher using username and password"""
        print("\n--- Teacher Login ---")

        max_attempts = 3
        attempts = 0

        while attempts < max_attempts:
            try:
                # Get credentials
                username = self.validate_input("Enter teacher username: ", "string", 1, 50)
                if not username:
                    return None

                # Use getpass for password (hides input)
                try:
                    password = getpass.getpass("Enter password: ")
                except (KeyboardInterrupt, EOFError):
                    print("\nLogin cancelled.")
                    return None

                if not password:
                    print("Password cannot be empty!")
                    attempts += 1
                    continue

                # Verify credentials
                user_data = self.db_manager.verify_teacher(username, password)

                if user_data:
                    print(f"\nLogin successful! Welcome, {user_data['name']}")
                    return user_data
                else:
                    attempts += 1
                    remaining = max_attempts - attempts
                    if remaining > 0:
                        print(f"Invalid credentials! {remaining} attempts remaining.")
                    else:
                        print("Maximum login attempts exceeded!")

            except KeyboardInterrupt:
                print("\nLogin cancelled.")
                return None
            except Exception as e:
                print(f"Login error: {e}")
                attempts += 1

        return None

    def _authenticate_student(self):
        """Authenticate student using name and login code"""
        print("\n--- Student Login ---")
        print("Students: Please enter your full name and the login code")
        print("provided by your teacher.")
        print("\nNote: Login codes are generated when teachers add you to the system.")

        max_attempts = 3
        attempts = 0

        while attempts < max_attempts:
            try:
                # Get student name
                name = self.validate_input("Enter your full name: ", "string", 2, 100)
                if not name:
                    return None

                # Get login code
                login_code = self.validate_input("Enter your login code: ", "string", 4, 10)
                if not login_code:
                    return None

                # Verify credentials
                user_data = self.db_manager.verify_student(name, login_code)

                if user_data:
                    print(f"\nLogin successful! Welcome, {user_data['name']}")
                    return user_data
                else:
                    attempts += 1
                    remaining = max_attempts - attempts
                    if remaining > 0:
                        print(f"Invalid name or login code! {remaining} attempts remaining.")
                        print("Make sure you entered your name exactly as registered.")
                    else:
                        print("Maximum login attempts exceeded!")
                        print("Please contact your teacher for assistance.")

            except KeyboardInterrupt:
                print("\nLogin cancelled.")
                return None
            except Exception as e:
                print(f"Login error: {e}")
                attempts += 1

        return None

    def validate_input(self, prompt, input_type="string", min_length=1, max_length=None, valid_choices=None):
        """
        Validate user input with specified criteria

        Args:
            prompt (str): Input prompt message
            input_type (str): Type of input ('string', 'integer', 'float', 'choice')
            min_length (int): Minimum length/value
            max_length (int): Maximum length/value
            valid_choices (list): Valid choices for 'choice' type

        Returns:
            Validated input or None if cancelled
        """
        while True:
            try:
                user_input = input(prompt).strip()

                # Handle empty input
                if not user_input and min_length > 0:
                    print(f"Input cannot be empty!")
                    continue

                if input_type == "string":
                    if len(user_input) < min_length:
                        print(f"Input must be at least {min_length} characters long!")
                        continue
                    if max_length and len(user_input) > max_length:
                        print(f"Input must be no more than {max_length} characters long!")
                        continue
                    return user_input

                elif input_type == "integer":
                    try:
                        value = int(user_input)
                        if min_length is not None and value < min_length:
                            print(f"Value must be at least {min_length}!")
                            continue
                        if max_length is not None and value > max_length:
                            print(f"Value must be no more than {max_length}!")
                            continue
                        return value
                    except ValueError:
                        print("Please enter a valid number!")
                        continue

                elif input_type == "float":
                    try:
                        value = float(user_input)
                        if min_length is not None and value < min_length:
                            print(f"Value must be at least {min_length}!")
                            continue
                        if max_length is not None and value > max_length:
                            print(f"Value must be no more than {max_length}!")
                            continue
                        return value
                    except ValueError:
                        print("Please enter a valid number!")
                        continue

                elif input_type == "choice":
                    if valid_choices is None:
                        print("No valid choices provided!")
                        return None

                    if user_input.upper() in [choice.upper() for choice in valid_choices]:
                        return user_input.upper()
                    else:
                        print(f"Please choose from: {', '.join(valid_choices)}")
                        continue

            except KeyboardInterrupt:
                print("\nInput cancelled.")
                return None
            except Exception as e:
                print(f"Input error: {e}")
                continue

    def confirm_action(self, message):
        """
        Ask user to confirm an action
        Returns True if confirmed, False otherwise
        """
        while True:
            try:
                choice = input(f"{message} (y/n): ").strip().lower()
                if choice in ['y', 'yes']:
                    return True
                elif choice in ['n', 'no']:
                    return False
                else:
                    print("Please enter 'y' for yes or 'n' for no.")
            except KeyboardInterrupt:
                print("\nAction cancelled.")
                return False
            except Exception:
                print("Please enter 'y' for yes or 'n' for no.")

class InputValidator:
    """Utility class for input validation"""

    @staticmethod
    def is_valid_name(name):
        """Check if name is valid (contains only letters and spaces)"""
        return name and all(c.isalpha() or c.isspace() for c in name) and len(name.strip()) >= 2

