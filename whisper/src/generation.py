import csv
import csv_handler
from debug_messages import print_debug
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

                print_debug(True, "Data directory not found.")
                print_debug(False, "Data directory created.")

            except OSError as e:
                if debug:
                    print_debug(False, "/data/ exists.")

            try:
                mkdir('../data/misc/')

                print_debug(True, "Misc directory not found.")
                print_debug(False, "Misc directory created.")

            except OSError as r:
                if debug:
                    print_debug(False, "/data/misc/ exists. ")

            #Using os.path.exists we check if the csv file exists, if not  we set file_exits to False, otherwise its True
            file_exists = exists("../data/accounts.csv")

            if not file_exists:
                print_debug(True, "'accounts.csv' has not been found and will be made.")

                try:
                    csv_handler.create_accounts_csv()
                except:
                    print_debug(False + "A Fatal error has occurred whilst creating the CSV.\nPress Any key to close the program.")
                    input()
                    exit()
                
                if debug:
                    print_debug(False, "'accounts.csv' created.")

                return True

            else:
                if debug:
                    print_debug(False, "'accounts.csv' exists'")
                return True
    except:
        print(Fore.RED + "An error has occured during csv generation.")
        return False

