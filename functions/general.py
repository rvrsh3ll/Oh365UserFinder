from colorama import Fore, Style, init

def definitions():
    global info, close, success, fail
    info, fail, close, success = (
        Fore.YELLOW + Style.BRIGHT,
        Fore.RED + Style.BRIGHT,
        Style.RESET_ALL,
        Fore.GREEN + Style.BRIGHT,
    )

def banner():
    print(Fore.YELLOW + Style.BRIGHT + "")
    print("   ____  __   _____ _____ ______   __  __                  _______           __          ")
    print("  / __ \\/ /_ |__  // ___// ____/  / / / /_______  _____   / ____(_)___  ____/ /__  _____")
    print(" / / / / __ \\ /_ </ __ \\/___ \\   / / / / ___/ _ \\/ ___/  / /_  / / __ \\/ __  / _ \\/ ___/ ")
    print("/ /_/ / / / /__/ / /_/ /___/ /  / /_/ (__  )  __/ /     / __/ / / / / / /_/ /  __/ /     ")
    print("\\____/_/ /_/____/\\____/_____/   \\____/____/\\___/_/     /_/   /_/_/ /_/\\__,_/\\___/_/     \n")
    print("                                   Version 1.1.2                                         "
    )
    print("                               A project by The Mayor                                    ")
    print("                        Oh365UserFinder.py -h to get started                            \n"+ Style.RESET_ALL)
    print("-" * 90)