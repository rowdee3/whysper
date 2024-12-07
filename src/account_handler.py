import random
import hasher
import csv_handler
from os.path import exists
from colorama import Fore, Style, init #type : ignore
from string import digits

def register_account(debug):
    
    """
    This is a large function that allows a user to create a username and password that gets added to 
    the accounts.csv file. It will also call upon a function to hash the password before storing it 
    in the csv file.

    Parameters
    -----------
    debug : bool
        outputs what the program is currently doing

    Returns
    --------
    bool
        whether the account was successfully generated or not.

    """

    init(autoreset=True)

    # Check if csv file exists. 
    file_exists = exists("../data/accounts.csv")
    if file_exists:
        if debug:
            print(Fore.GREEN + "csv file found!")
    else:
        print(Fore.RED + "csv NOT FOUND!\nPlease restart Whisper to generate a new data folder.")
        return False

    #make a unique account id for this account.
    accid_is_unique = False
    while not accid_is_unique:
        accid = "AC00"
        
        accid_unique = ''.join(random.choice(digits) for i in range(8))

        accid += accid_unique

        if csv_handler.check_if_accid_exists(accid):
            if debug:
                print(Fore.GREEN + "unique account id created.")
            accid_is_unique = True


    user_name = input("@; Please enter a new username: ")

    while True:

        pass_meets_spec = False

        while not pass_meets_spec:

            pass_word = input("@' Please enter a password: ")
            pass_conf = input("@; Please re-enter your password: ")

            if pass_word != pass_conf:
                print(Fore.RED + "Passwords do not match!")
            else:  
                if pass_conf.__len__() <= 12:
                    print(Fore.RED + "Password length must be or exceed 12 characters.")
                else:
                    username_confirmed = False
                    pass_meets_spec = True

        while not username_confirmed:

            try:
                u_input = str(input("@; Are you sure you want " + Fore.BLUE + user_name + Fore.WHITE +" to be your username? (Y/N) "))

                match u_input:

                    case "Y":
                        username_confirmed = True

                    case "N":
                        user_name = input("@; Please enter a new username: ")

                    case _:
                        raise ValueError
                            
            except ValueError:
                print(Fore.RED + "Please enter either Y or N.")

        break

    if debug:
        print(Fore.GREEN + "Username confirmed.")
        print(Fore.GREEN + "Passwords match, hashing...")
    
    hashed_pass, p_salt = hasher.hash_pass(debug, nh_pass=pass_conf)
    #hashed_pass = hasher.hash_pass2(debug=True, nh_pass=pass_conf)

    if debug:
        print(Fore.GREEN + "Unique ID is " + accid)
        print(Fore.GREEN + "attempting to add account to csv now...")

    if csv_handler.new_entry(accid, user_name, hashed_pass, p_salt):
        print(Fore.RED + "Username already exists!")
        return False
    else:
        return True
