import generation
import account_handler
from debug_messages import print_debug
from colorama import Fore, Back, Style, init #type: ignore

init(autoreset=True)
debug = False


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

    while True:

        menu_string = "1) Login\n2) Create Account\n0) Exit"
        print(Fore.WHITE + menu_string)

        if user_name != 'Guest':
            u_input = int(input(Fore.CYAN + f"{user_name}" + Fore.WHITE + "@; " ))
        else:
            u_input = int(input(f"{user_name}@; "))

        try:
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
                    user_name = var
                    display_title_card()
            else:
                print(Fore.RED + "Please enter an available option!")
        except ValueError as err:
            print(Fore.RED + "Please enter an available option!")


def main():

    display_title_card()
    generation.generate_csv(debug)
    login_menu()

if __name__ == '__main__':
    main()