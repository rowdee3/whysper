import generation
import account_handler
from debug_messages import print_debug
from colorama import Fore, Back, Style, init #type: ignore

init(autoreset=True)
debug = True


def display_title_card():

    """
    Displays the title card.
    """

    title_card = "Whisper v0.0.2"
    print(Fore.GREEN + title_card.center(20))
    print(Fore.GREEN + "-------------------")

def login_menu():

    """
    Allows the user to either Login, Create account or exit program.
    Temporary splashscreen.

    """

    user_name = 'Guest'
    menu_string = "1) Login\n2) Create Account\n0) Exit\n"

    while True:

        print(Fore.WHITE + menu_string)

        try:
            u_input = int(input(f"{user_name}@" + Fore.GREEN + "whisper" + Fore.WHITE + "; "))

            if u_input == 0:
                exit()
            elif u_input == 2:
                if account_handler.register_account(debug):
                    print(Fore.GREEN + "Account Succesfully created!\n")
                    display_title_card()
                else:
                    print(Fore.RED + "Failed to create account!\n")
                    display_title_card()
            elif u_input == 1:
                var = account_handler.login_to_dashboard(debug)
                if var == None:
                    display_title_card()
                else:
                    print("")
                    dashboard(var)
            else:
                print(Fore.RED + "Please enter an available option!")
        except ValueError as err:
            print(Fore.RED + "Please enter an available option!")


def dashboard(user_name):
    """
    Main dashboard which allows user to connect to a server. etc etc

    Parameters
    ------------
    user_name : str
        the current user who is logged in.

    Returns
    ---------
    None

    """

    display_title_card()

    menu_string = "1) Connect\n2) Logout\n0) Exit\n"

    while True:

        print(menu_string)        

        try:
            u_input = int(input(Fore.CYAN + f"{user_name}" + Fore.WHITE + "@" + Fore.GREEN + "whisper" + Fore.WHITE + "; "))

            if u_input == 0:
                exit()
            elif u_input == 2:
                login_menu()
            elif u_input == 1:
                print(Fore.RED + "Sorry, unavailable right now! :()")
        except ValueError as e:
            print("Please enter an available option!")



def main():

    display_title_card()
    generation.generate_csv(debug)
    login_menu()

if __name__ == '__main__':
    main()