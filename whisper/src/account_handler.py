import random
import hasher
import csv_handler
from debug_messages import print_debug
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
            print_debug(False, "'accounts.csv' found.")
    else:
        print_debug(True, "'accounts.csv' has been moved or is missing. Please restart Whisper to generate a new file.")
        return False

    #make a unique account id for this account.
    #this is dumb but it'll do for now.
    accid_is_unique = False
    while not accid_is_unique:
        accid = "AC00"
        
        accid_unique = ''.join(random.choice(digits) for i in range(8))

        accid += accid_unique

        if csv_handler.check_if_accid_exists(accid):
            if debug:
                print_debug(False, "Unique account ID created.")
            accid_is_unique = True

    username_confirmed = False

    while not username_confirmed:

        user_name = input("@; Please enter a username: ")

        if csv_handler.check_if_username_exists(user_name):
            print(Fore.RED + "Username already exists!")
        else:
            username_confirmed = False

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
                continue



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



    if debug:
        print_debug(False, "Username confirmed.")
        print_debug(False, "Passwords match, hashing...")
    
    hashed_pass, p_salt = hasher.hash_pass(debug, pass_word, True, None)

    if debug:
        print_debug(False, "Account generation successful.")

    csv_handler.new_entry(accid, user_name, hashed_pass, p_salt)
    return True

def login_to_dashboard(debug):

    """
    This function allows the user to login to their account and proceeds to start the dashboard.

    Parameters
    -----------
    None

    Returns
    -----------
    bool
        whether the logon attempt was successful.
    
    user_name : str
        the username of the account we logged into 

    """

    while True:
        
        #Check if account exists before carrying on.
        username_confirmed = False
        while not username_confirmed:
            u_input = input("@; Please enter your username: ")

            if csv_handler.check_if_username_exists(u_input) != True:
                print(Fore.RED + "Account not found!")
                return None
            else:
                user_name = u_input
                username_confirmed = True

        u_input = input("@; Please enter your password: ")
        password = u_input

        #Grab the salt value used in the account.
        salt = csv_handler.get_salt_from_csv(user_name)

        if debug:
            print_debug(False, f"Grabbed {salt} from accounts.csv.")

        #Generate a key based on the user given input and compare it to the stored hash value.
        stored_pass = csv_handler.get_user_hash(debug, user_name)
        if debug:
            print_debug(False, "Generating new hash....")
        new_pass = hasher.hash_pass(debug, password, False, salt)

        if debug:
            print_debug(False, f"Old Hash value: {stored_pass}")
            print_debug(False, f"New Hash value: {new_pass}")

        try:
            assert new_pass == stored_pass
            print(Fore.GREEN + f"Logged in as {user_name}.")
            return user_name
        except AssertionError:
            print(Fore.RED + "Passwords do not match!")