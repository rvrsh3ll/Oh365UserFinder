#!/usr/bin/python3

import requests as o365request
import argparse
import time
import textwrap
import sys
from colorama import Fore, Style, init
from functions.general import banner
from functions.enum import enum_domain, single_email, email_list, pwspray


def definitions():
    global info, close, success, fail
    info, fail, close, success = (
        Fore.YELLOW + Style.BRIGHT,
        Fore.RED + Style.BRIGHT,
        Style.RESET_ALL,
        Fore.GREEN + Style.BRIGHT,
    )


def options():
    opt_parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """---Validate a Domain Name in O365---
python3 Oh365Finder.py -d mayorsec.com\n
---Validate a single email---
python3 Oh365UserFinder.py -e test@test.com\n
---Validate a list of emails and write to file---
python3 Oh365UserFinder.py -r testemails.txt -w valid.txt\n
---Validate a list of emails, write to file and timeout between requests---
python3 Oh365UserFinder.py -r emails.txt -w validemails.txt -t 30\n
---Validate a list of emails and write to CSV---
python3 Oh365UserFinder.py -r emails.txt -c validemails.csv -t 30\n
---Password Spray a list of emails using GRAPH--- (Can be used to identify valid account credentials with MFA enabled)
python3 Oh365UserFinder.py -p <password> --pwspray --elist <listname>\n
---Password Spray a list of emails using GRAPH with lockout policy timer---
python3 Oh365UserFinder.py -p <password> --pwspray --elist <listname> --lockout <time>\n

"""
        ),
    )
    opt_parser.add_argument("-d", "--domain", help="Validate if a domain exists")
    opt_parser.add_argument(
        "-e", "--email", help="Runs o365UserFinder against a single email"
    )
    opt_parser.add_argument("-r", "--read", help="Reads email addresses from file")
    opt_parser.add_argument(
        "-t", "--timeout", help="Set timeout between checks to avoid false positives"
    )
    opt_parser.add_argument("-w", "--write", help="Writes valid emails to text file")
    opt_parser.add_argument("-c", "--csv", help="Writes valid emails to a .csv file")
    opt_parser.add_argument(
        "-v", "--verbose", help="Prints output verbosely", action="store_true"
    )
    opt_parser.add_argument(
        "-gs",
        "--pwspray",
        help="Password sprays a list of accounts using GRAPH",
        action="store_true",
    )
    opt_parser.add_argument(
        "-l", "--lockout", help="Sets the lockout timer if known (in minutes)"
    )

    # opt_parser.add_argument(
    #     '-ps', '--pwspray', help='Password sprays a list of accounts using RST', action='store_true')
    opt_parser.add_argument("-p", "--password", help="Password to be tested")
    opt_parser.add_argument("-el", "--elist", help="Valid emails to be tested")
    global args
    args = opt_parser.parse_args()
    if len(sys.argv) == 1:
        opt_parser.print_help()
        opt_parser.exit()


ms_url = "https://login.microsoftonline.com/common/GetCredentialType"


def main():
    if args.timeout is not None:
        print(
            info
            + f"[info] Timeout set to {args.timeout} seconds between requests.\n"
            + close
        )
    counter = 0
    timeout_counter = 0
    print(
        Fore.YELLOW
        + Style.BRIGHT
        + f"\n[info] Starting Oh365 User Finder at {time.ctime()}\n"
        + Style.RESET_ALL
    )
    if args.email is not None:
        single_email(args, o365request, ms_url)
    elif args.read is not None:
        email_list(args, o365request, ms_url, counter, timeout_counter)
    elif args.domain is not None:
        enum_domain(args, o365request)
    elif args.pwspray:
        pwspray(args, o365request, ms_url, counter)
    else:
        sys.exit()


def new_func():
    return 60


if __name__ == "__main__":
    try:
        init()
        definitions()
        banner()
        options()
        main()

    except KeyboardInterrupt:
        print("\nYou either fat fingered this, or meant to do it. Either way, goodbye!")
        quit()
