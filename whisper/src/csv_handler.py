import csv
import pandas as pd
from debug_messages import print_debug

def create_accounts_csv():

    """
    Function to create the accounts csv.

    Paramaters
    ----------
    None

    Returns
    --------
    None

    """

    with open('../data/accounts.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        field = ['accid', 'username', 'password_hash', 'pass_salt']            
        writer.writerow(field)   

def check_if_username_exists(username):
     
    """
     Checks to see if a username is already in the file.

     Parameters
     ----------
     username : str
        the username of an account

     Returns
     -------
     bool
        True or False
    """
    with open('../data/accounts.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if username == row[1]:
                return True
    return False

def check_if_accid_exists(accid):

    #needs some work

    df = pd.read_csv('../data/accounts.csv')
    accids = df['accid']

    if accid in accids:
        return False
    else:
        return True
    
def get_user_hash(debug, user_name):
    
    """
    A function to get the stored hash value from accounts.csv

    Parameters
    -----------
    debug : bool
        allows for outputting debug messages

    user_name : str
        allows us to locate what hash we want

    Returns
    ---------
    hex
        returns the hex value of the hash.
    """

    if check_if_username_exists(user_name):
        
        with open('../data/accounts.csv', 'r') as file:
            reader = csv.reader(file)
            
            for row in reader:
                if row[1] == user_name:
                    return row[2]

def new_entry(accid, username, hpass, salt):

    """
    Function to add a new account to the accounts csv file.

    Paramaters
    -----------
    username : str
        the username of the new account
    
    hpass : hex
        the hex of the hashed password of the account

    salt : str
        the salt value used to hash the password.

    Returns
    --------

    bool
        if the file succeeds in creating the new account a True is returned otherwise, False.
    """
    row = [accid, username, hpass, salt]
    with open('../data/accounts.csv', 'a') as file:
        writer = csv.writer(file)
        writer.writerow(row)
    return True

def get_salt_from_csv(user_name):
    """
    A function to grab the salt value associated with an account.

    Parameters
    ------------
    user_name : str
        the account we want to grab the salt for

    Returns
    -----------
    str
        returns the salt value as a string

    """

    
    with open('../data/accounts.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if user_name == row[1]:
                return row[3]


def delete_entry_from_csv(*args, **kwargs):

    #TO-DO

    pass


 