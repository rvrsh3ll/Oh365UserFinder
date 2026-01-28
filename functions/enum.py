import time
import sys
import re
from colorama import Fore, Style, init

def enum_domain(args, o365request):
    info, fail, close, success = (Fore.YELLOW + Style.BRIGHT,Fore.RED + Style.BRIGHT,Style.RESET_ALL,Fore.GREEN + Style.BRIGHT)
    domain_name = args.domain
    print(info + f"[info] Checking if the {domain_name} exists...\n" + close)
    url = f"https://login.microsoftonline.com/getuserrealm.srf?login=user@{domain_name}"
    request = o365request.get(url)
    # print(request)
    response = request.text
    # print(response)
    valid_response = re.search('"NameSpaceType":"Managed",', response)
    valid_response1 = re.search('"NameSpaceType":"Federated",', response)
    if args.verbose:
        print(domain_name, request, response, valid_response)
    if valid_response:
        print(
            success
            + f"[success] The listed domain {domain_name} exists. Domain is Managed.\n"
            + close
        )
    elif valid_response1:
        print(
            success
            + f"[success] The listed domain {domain_name} exists. Domain is Federated.\n"
            + close
        )
    else:
        print(
            fail
            + f"[info] The listed domain {domain_name} does not exist.\n"
            + close
        )
    print(info + f"[info] Scan completed at {time.ctime()}" + close)

def single_email(args, o365request, ms_url):
    info, fail, close, success = (Fore.YELLOW + Style.BRIGHT,Fore.RED + Style.BRIGHT,Style.RESET_ALL,Fore.GREEN + Style.BRIGHT)
    email = args.email
    s = o365request.session()
    body = '{"Username":"%s"}' % email
    request = o365request.post(ms_url, data=body)
    response_dict = request.json()
    response = request.text
    valid_response = re.search('"IfExistsResult":0,', response)
    valid_response5 = re.search('"IfExistsResult":5,', response)
    valid_response6 = re.search('"IfExistsResult":6,', response)
    invalid_response = re.search('"IfExistsResult":1,', response)
    desktopsso_response = re.search(
        '{"DesktopSsoEnabled":true,"UserTenantBranding":null,"DomainType":3}',
        response,
    )
    throttling = re.search('"ThrottleStatus":1', response)
    if args.verbose:
        print(
            "\n",
            email,
            s,
            body,
            request,
            response_dict,
            response,
            valid_response,
            valid_response5,
            valid_response6,
            invalid_response,
            desktopsso_response,
            "\n",
        )
    if (
        desktopsso_response
        # and not valid_response
        # or valid_response5
        # or valid_response6
    ):
        a = email
        b = " Result -  Desktop SSO Enabled [!]"
        print(info + f"[!] {a:51} {b} " + close)
        pass
    elif invalid_response and not desktopsso_response:
        a = email
        b = " Result - Invalid Email Found! [-]"
        print(fail + f"[-] {a:51} {b}" + close)
    elif valid_response or valid_response5 or valid_response6 and not desktopsso_response:
        a = email
        b = " Result -   Valid Email Found! [+]"
        print(success + f"[+] {a:53} {b} " + close)
    elif throttling:
        print(
            fail
            + "\n[warn] Results suggest O365 is responding with false positives. Retry the scan in 60 seconds."
            + close
        )
        sys.exit()
    elif args.timeout is not None:
        time.sleep(int(args.timeout))

def email_list(args, o365request, ms_url, counter, timeout_counter):
    info, fail, close, success = (Fore.YELLOW + Style.BRIGHT,Fore.RED + Style.BRIGHT,Style.RESET_ALL,Fore.GREEN + Style.BRIGHT)
    with open(args.read) as input_emails:
        for line in input_emails:
            s = o365request.session()
            email_line = line.split()
            email = " ".join(email_line)
            body = '{"Username":"%s"}' % email
            request = o365request.post(ms_url, data=body)
            response = request.text
            valid_response = re.search('"IfExistsResult":0,', response)
            valid_response5 = re.search('"IfExistsResult":5,', response)
            valid_response6 = re.search('"IfExistsResult":6,', response)
            invalid_response = re.search('"IfExistsResult":1,', response)
            throttling = re.search('"ThrottleStatus":1', response)
            desktopsso_response = re.search(
                '{"DesktopSsoEnabled":true,"UserTenantBranding":null,"DomainType":3}',
                response,
            )
            if args.verbose:
                print(
                    "\n",
                    s,
                    email_line,
                    email,
                    body,
                    request,
                    response,
                    valid_response,
                    valid_response5,
                    valid_response6,
                    invalid_response,
                    desktopsso_response,
                    "\n",
                )
            if desktopsso_response:
                a = email
                b = " Result -  Desktop SSO Enabled [!]"
                print(info + f"[!] {a:51} {b} " + close)
            if invalid_response and not desktopsso_response:
                a = email
                b = " Result - Invalid Email Found! [-]"
                print(fail + f"[-] {a:51} {b}" + close)
            if valid_response or valid_response5 or valid_response6:
                a = email
                b = " Result -   Valid Email Found! [+]"
                print(success + f"[+] {a:51} {b}" + close)
                counter = counter + 1
                if args.write is not None:
                    a = email
                    with open(args.write, "a+") as valid_emails_file:
                        valid_emails_file.write(f"{a}\n")
                elif args.csv is not None:
                    a = email
                    with open(args.csv, "a+") as valid_emails_file:
                        valid_emails_file.write(f"{a}\n")
            if throttling:
                if args.timeout is not None:
                    timeout_counter = timeout_counter + 1
                    if timeout_counter == 5:
                        print(
                            fail
                            + f"\n[warn] Results suggest O365 is responding with false positives."
                        )
                        print(
                            fail
                            + f"\n[warn] O365 has returned five false positives.\n"
                        )
                        print(
                            info
                            + f"[info] Oh365UserFinder setting timeout to 10 minutes. You can exit or allow the program to continue running."
                        )
                        time.sleep(int(300))
                        print(info + f"\nScanning will continue in 5 minutes.")
                        time.sleep(int(270))
                        print(info + f"\nContinuing scan in 30 seconds.")
                        time.sleep(int(30))
                        timeout_counter = 0
                        # sys.exit()
                    else:
                        print(
                            fail
                            + f"\n[warn] Results suggest O365 is responding with false positives. Sleeping for {args.timeout} seconds before trying again.\n"
                        )
                        time.sleep(int(args.timeout))

                else:
                    print(
                        fail
                        + "\n[warn] Results suggest O365 is responding with false positives. Restart scan and use the -t flag to slow request times."
                        + close
                    )
                    sys.exit()
            if args.timeout is not None:
                time.sleep(int(args.timeout))
        if counter == 0:
            print(fail + "\n[-] There were no valid logins found. [-]" + close)
            print(info + f"\n[info] Scan completed at {time.ctime()}" + close)
        elif counter == 1:
            print(
                info
                + "\n[info] Oh365 User Finder discovered one valid login account."
                + close
            )
            print(info + f"\n[info] Scan completed at {time.ctime()}" + close)
        else:
            print(
                info
                + f"\n[info] Oh365 User Finder discovered {counter} valid login accounts.\n"
                + close
            )
            print(info + f"\n[info] Scan completed at {time.ctime()}" + close)