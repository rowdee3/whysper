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
    row = [accid, username, hpass.hex(), salt]
    with open('../data/accounts.csv', 'a') as file:
        writer = csv.writer(file)
        writer.writerow(row)
    return True



 