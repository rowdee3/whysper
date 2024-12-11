import string
import hashlib
import argon2
import secrets
import base64
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

    if debug:
        print_debug(False, "Generating Salt value now.")
    salt = secrets.token_hex(32)
    if debug:
        print_debug(False, "Salt has been generated as " + salt + ".")

    return salt


def hash_pass(debug, nh_pass, salt_needed, password_salt):
    
    """
    Hashes the given password using standard hashlib.

    Parameters
    -----------
    debug : bool
        outputs what the program is currently doing. WARNING! MAY REVEAL DATA IF DEBUG IS ENABLED.
    nh_pass : str
        the non-hashed password.
    salt_needed : bool
        whether or not we need to generate a new salt.
    salt : str
        a random assortment of letters and numbers (32 bytes)

    Returns:
    -----------
    h_pass : hex
        the hashed equivalent of the password.

    """

    if salt_needed:
        password_salt = salt(debug)
        hpass = hashlib.pbkdf2_hmac('sha512', nh_pass.encode('utf-8'), password_salt.encode('utf-8'), iterations=10_000_000, dklen=128).hex()
        return hpass, password_salt
    else:
        hpass = hashlib.pbkdf2_hmac('sha512', nh_pass.encode('utf-8'), password_salt.encode('utf-8'), iterations=10_000_000, dklen=128).hex()
        return hpass


    
