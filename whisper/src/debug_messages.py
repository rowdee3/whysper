from colorama import Fore, Style, Back, init

init(autoreset=True)

def print_debug(fail, message):

    if fail:
        print("[ " + Fore.RED + "X " + Fore.WHITE + "] " + message)
    else:
        print("[ " + Fore.GREEN + "OK " + Fore.WHITE + "] " + message)