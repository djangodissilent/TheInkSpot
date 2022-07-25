import re


# This function is checking the strgnth of a password
# to contain a number and both uppercase and lowercase letters
def check_password_strength(password):
    if not (re.fullmatch(r"[A-Za-z0-9@#$%^&+=]{8,}", password)):
        return False
    else:
        return True
