from colorama import Fore, Style, Back, init

init(autoreset=True)

def print_debug(fail, message):

    if fail == None:
        print(message)

    if fail:
        print("[ " + Fore.RED + "X " + Fore.WHITE + "] " + message)
    elif not fail:
        print("[ " + Fore.GREEN + "OK " + Fore.WHITE + "] " + message)
