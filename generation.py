import csv
import csv_handler
from os.path import exists
from os import mkdir
from colorama import Fore, Style, init #type: ignore


"""
This library generates any folders/files we need for our program to work e.g. the data directory and/or the accounts.csv
"""

def generate_csv(debug):

    """A function to generate the data and accounts.csv file

        Paramaters
        ------------
        debug : bool
            outputs what the program is currently doing.

        Returns
        ---------
        bool 
            whether or not the generation has been successful.

    """
    init(autoreset=True)
    exit = False

    try:
        while not exit:

            #check if accounts.csv exists
            if debug:
                print(Fore.WHITE + "Prechecking data.....")

            #We attempt to make the directory whether or not it exists, if it already exists we accept the error and continue as normal.
            try:
                mkdir("../data/")
                print(Fore.RED + "data dir NOT FOUND!")
                print(Fore.GREEN + "data dir made.")
            except OSError as e:
                if debug:
                    print(Fore.GREEN + "data dir exists.")

            #Using os.path.exists we check if the csv file exists, if not  we set file_exits to False, otherwise its True
            file_exists = exists("../data/accounts.csv")

            if not file_exists:
                print(Fore.RED + "accounts.csv NOT FOUND!")
                print(Fore.GREEN + "creating csv file now...")

                csv_handler.create_accounts_csv()
                
                print(Fore.GREEN + "accounts.csv successfully created!")

                return True

            else:
                if debug:
                    print(Fore.GREEN + "accounts.csv exists!")
                return True
    except:
        print(Fore.RED + "An error has occured during csv generation.")
        return False

