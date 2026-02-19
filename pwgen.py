""" 
pwgen-lite
Minimalistic password generator in Python.

"""

import argparse
import secrets
import string

# Base character sets
BASE_ALPHABET = string.ascii_letters + string.digits
SYMBOLS = "!@#$%^&*()-_=+[]{}|;:,.<>?/~`"

def generate_password(length: int, use_symbols: bool) -> str:
    """
    Generate a password of given length using secure randomness
    """
    
    alphabet = BASE_ALPHABET + (SYMBOLS if use_symbols else "")
    return "".join(secrets.choice(alphabet) for _ in range(length))

def parse_arguments():
    """
    Parse command-line arguments.
    """

    parser = argparse.ArgumentParser(description="Generate a secure random password.")

    parser.add_argument("length", type=int, help="Length of the password (positive integer)")
    parser.add_argument("--symbols", action="store_true", help="Include symbols in the password")
    return parser.parse_args()                    

def main():
    args = parse_arguments()

    if args.length <= 0:
        print("Error: Length must be a positive integer.")
        return
    
    print(generate_password(args.length, args.symbols))
    
    
if __name__ == "__main__":
    main()