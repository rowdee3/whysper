import generation
import account_handler
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
    Temporary dashboard.

    """

    while True:

        menu_string = "1) Login\n2) Create Account\n0) Exit"
        print(Fore.WHITE + menu_string)

        try:
            u_input = int(input("@; "))

            match u_input:

                case 0:
                    exit()

                case 1:
                    print(Fore.RED + "Sorry, that's currently unavaliable :(\n\n")
                    display_title_card()

                case 2:
                     if account_handler.register_account(debug):
                        print(Fore.GREEN + "Account Succesfully created\n")
                        display_title_card()
                     else:
                        print(Fore.RED + "Failed to create account!\n")
                        display_title_card()
                case _:
                    raise ValueError

        except ValueError:
            print(Fore.RED + "Please enter an available option!")


def main():

    display_title_card()
    generation.generate_csv(debug)
    login_menu()

if __name__ == '__main__':
    main()