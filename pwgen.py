""" 
pwgen-lite
Minimalistic password generator in Python.

"""
import secrets
import string

# Allowed charchters for now 
ALPHABET = string.ascii_letters + string.digits

def generate_password(length: int) -> str:
    """
    Generate a password of given length using secure randomness
    """
    return "".join(secrets.choice(ALPHABET) for _ in range(length))


def main():
    raw = input("Enter password length: ").strip()

    if not raw.isdigit():
        print("INvalid input. Please enter a valid positive number. ")
        return
    
    length = int(raw)

    if length <= 0:
        print("Length must be greater then 0.")
        return 
    
    password = generate_password(length)
    print("Generated password:", password)

    
if __name__ == "__main__":
    main()