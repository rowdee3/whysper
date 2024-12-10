import string
import hashlib
import argon2
import secrets
from colorama import Fore, init
from debug_messages import print_debug

init(autoreset=True)


def hash_name(user_name):
    """
    Simple function to get the hash of a username.

    Parameters
    -----------
    user_name : str
        the username of the account we want to get.

    Returns
    ---------
    user_hash 

    """

def salt(debug):

    """
    Simple function to generate a salt value to add to our passwords.

    Parameters
    ----------
    debug : bool
        outputs what the program is currently doing. WARNING! MAY REVEAL DATA IF DEBUG IS ENABLED.

    Returns
    ---------
    salt : str
        a combination of random letters and numbers.

    """

    char_set = string.ascii_uppercase + string.ascii_lowercase + string.digits
    #abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789

    if debug:
        print_debug(False, "Generating Salt value now.")
    salt = ''.join(secrets.SystemRandom().choice(char_set) for i in range(16))
    if debug:
        print_debug(False, "Salt has been generated as " + salt + ".")

    return salt


def hash_pass2(debug, nh_pass):

    """
    Hashes the given password using argon2.cffi .

    Parameters
    -----------
    debug : bool
        outputs what the program is currently doing. WARNING! MAY REVEAL DATA IF DEBUG IS ENABLED.
    nh_pass : str
        the non-hashed password.

    Returns:
    -----------
    h_pass : obj
        the hashed equivalent of the password.

    """
    pass

def hash_pass(debug, nh_pass):
    
    """
    Hashes the given password using standard hashlib.

    Parameters
    -----------
    debug : bool
        outputs what the program is currently doing. WARNING! MAY REVEAL DATA IF DEBUG IS ENABLED.
    nh_pass : str
        the non-hashed password.

    Returns:
    -----------
    h_pass : obj
        the hashed equivalent of the password.

    """

    #iterations
    iters = 5_000_000

    password_salt = salt(debug)
    hpass = hashlib.pbkdf2_hmac('sha512', nh_pass.encode(), password_salt.encode(), iters)

    return hpass, password_salt



    
