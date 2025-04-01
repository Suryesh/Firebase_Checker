import subprocess
import re
import requests
import sys
import json
import os
import random
import uuid
from termcolor import colored
import readline

SCRIPT_VERSION = "1.2.0"
REMOTE_SCRIPT_URL = "https://raw.githubusercontent.com/Suryesh/Firebase_Checker/main/firebase-checker.py"

BANNER = r"""
   _____         __                  _______           __          
  / __(_)______ / /  ___ ____ ___   / ___/ /  ___ ____/ /_____ ____
 / _// / __/ -_) _ \/ _ `(_-</ -_) / /__/ _ \/ -_) __/  '_/ -_) __/
/_/ /_/_/  \__/_.__/\_,_/___/\__/  \___/_//_/\__/\__/_/\_\\__/_/   
                                                                    
                  This tool is built by Suryesh v: {}""".format(SCRIPT_VERSION)

def print_banner():
    print(colored(BANNER, 'cyan'))
    print(colored("               	YouTube: https://www.youtube.com/@suryesh_92\n", 'yellow'))

def check_for_updates():
    try:
        response = requests.get(REMOTE_SCRIPT_URL)
        if response.status_code == 200:
            remote_version = re.search(r'SCRIPT_VERSION = "(\d+\.\d+\.\d+)"', response.text)
            if remote_version and remote_version.group(1) != SCRIPT_VERSION:
                print(colored(f"\nUpdate available: v{remote_version.group(1)}", 'green'))
                if input(colored("Update now? (y/n): ", 'yellow')).lower() == 'y':
                    with open(__file__, 'w') as f:
                        f.write(response.text)
                    print(colored("Update successful! Please restart.", 'green'))
                    sys.exit(0)
    except Exception:
        pass

def help():
    """Displays help information about the script."""
    help_text = """
    This tool analyzes APK files for Firebase-related vulnerabilities, such as:
    - Open Firebase databases
    - Unauthorized Firebase signup
    - Firebase Remote Config misconfigurations

    Usage:
    -h, --help    python3 firebase-checker.py -h
    To Run        python3 firebase-checker.py
    
    - Now Enter your apk or give directory path where your apk located like /home/{username}/path/gmail.apk
    - For more information, visit: https://github.com/Suryesh/Firebase_Checker
    - And for live Bug Bounty session join our Discord server and subscribe to our channel.
    
    Youtube: https://www.youtube.com/@suryesh_92
    Discord : https://discord.com/invite/EfgnVNbh3N
    """
    print(colored(help_text, 'cyan'))

# Email Generator
def generate_random_email():
    """Generates a random email address."""
    username = str(uuid.uuid4())[:10]
    domain = random.choice(["gmail.com", "yahoo.com", "outlook.com", "protonmail.com"])
    return f"{username}@{domain}"

# Information extract from apk file
def extract_info_from_apk(apk_path):
    """Extracts App ID, Firebase URL, and Google API Key from an APK file."""
    result = subprocess.run(['strings', apk_path], capture_output=True, text=True)
    strings_output = result.stdout

    app_id_match = re.search(r'1:(\d+):android:([a-f0-9]+)', strings_output)
    firebase_url_match = re.search(r'https://[a-zA-Z0-9-]+\.firebaseio\.com', strings_output)
    google_api_key_match = re.search(r'AIza[0-9A-Za-z-_]{35}', strings_output)

    app_id = app_id_match.group(0) if app_id_match else None
    firebase_url = firebase_url_match.group(0) if firebase_url_match else None
    google_api_key = google_api_key_match.group(0) if google_api_key_match else None

    return app_id, firebase_url, google_api_key

def send_alert(message):
    """Prints alert messages in red."""
    print(colored(f"ALERT : {message}", 'red'))

def execute_curl_command(curl_cmd):
    """Executes a curl command and prints the output."""
    print(colored(f"\nExecuting: {curl_cmd}", 'blue'))
    result = subprocess.run(curl_cmd, shell=True, capture_output=True, text=True)
    print(colored(f"\nCurl Output:\n{result.stdout}", 'magenta'))
    return result.stdout

# Vulnerability check in apk file
def check_firebase_vulnerability(firebase_url, google_api_key, app_id, apk_name):
    """Checks for Firebase vulnerabilities, including open databases and unauthorized signup."""
    vulnerabilities = []
    
    if firebase_url:
        try:
            response = requests.get(f"{firebase_url}/.json", timeout=5)
            if response.status_code == 200:
                vulnerabilities.append("Open Firebase database detected")
                send_alert(f"Open Firebase database detected in {apk_name}. URL: {firebase_url}")
                execute_curl_command(f"curl {firebase_url}/.json")
            else:
                vulnerabilities.append("Firebase database is not openly accessible")
        except requests.RequestException:
            vulnerabilities.append("Failed to check Firebase database")

    if google_api_key and app_id:
        project_id = app_id.split(':')[1]
        url = f"https://firebaseremoteconfig.googleapis.com/v1/projects/{project_id}/namespaces/firebase:fetch?key={google_api_key}"
        body = {"appId": app_id, "appInstanceId": "required_but_unused_value"}

        try:
            response = requests.post(url, json=body, timeout=5)
            if response.status_code == 200 and response.json().get("state") != "NO_TEMPLATE":
                vulnerabilities.append("Firebase Remote Config is enabled")
                send_alert(f"Firebase Remote Config enabled in {apk_name}. URL: {url}")
                execute_curl_command(f"curl -X POST '{url}' -H 'Content-Type: application/json' -d '{json.dumps(body)}'")
            else:
                vulnerabilities.append("Firebase Remote Config is disabled or inaccessible")
        except requests.RequestException as e:
            vulnerabilities.append(f"Failed to check Firebase Remote Config: {str(e)}")
    
    return vulnerabilities

def send_verification_email(api_key, id_token):
    """Send email verification link using idToken"""
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={api_key}"
    payload = {
        "requestType": "VERIFY_EMAIL",
        "idToken": id_token
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print(colored("\n[+] Verification email sent successfully!", 'green'))
            print("Check the inbox of the registered email")
            return True
        else:
            print(colored(f"\n[!] Failed to send verification (HTTP {response.status_code})", 'red'))
            return False
    except Exception as e:
        print(colored(f"\n[!] Error: {str(e)}", 'red'))
        return False
       
# Unauthorizd signup checker
def check_unauthorized_signup(google_api_key, apk_name):
    """Checks if unauthorized Firebase signup is possible."""
    vulnerabilities = []
    id_token = None
    
    if google_api_key:
        signup_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={google_api_key}"
        user_email = input(colored("Enter email for signup: ", "yellow"))
        signup_payload = json.dumps({"email": user_email, "password": "Test@Pass123", "returnSecureToken": True})

        send_alert(f"Testing unauthorized signup on {signup_url}")
        response = execute_curl_command(f"curl -X POST '{signup_url}' -H 'Content-Type: application/json' -d '{signup_payload}'")
        
        if 'idToken' in response:
            vulnerabilities.append("Unauthorized Firebase signup is enabled")
            send_alert("Unauthorized signup is enabled!...")
            
            response_json = json.loads(response)
            id_token = response_json.get("idToken")
            refresh_token = response_json.get("refreshToken")

           # Send verification email if signup was successful
            if id_token:
                print(colored("\nAttempting to send verification email...", "blue"))
                send_verification_email(google_api_key, id_token)
               
            if refresh_token:
                token_url = f"https://securetoken.googleapis.com/v1/token?key={google_api_key}"
                token_payload = json.dumps({"grant_type": "refresh_token", "refresh_token": refresh_token})
                send_alert("Fetching access token using refresh token...")
                execute_curl_command(f"curl -X POST '{token_url}' -H 'Content-Type: application/json' -d '{token_payload}'")
    
    if id_token:
        lookup_url = f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={google_api_key}"
        lookup_payload = json.dumps({"idToken": id_token})
        send_alert("Fetching account information using idToken...")
        execute_curl_command(f"curl -X POST '{lookup_url}' -H 'Content-Type: application/json' -d '{lookup_payload}'")
    
    return vulnerabilities

# apk processing
def process_apks(input_path):
    """Processes either a folder containing APKs or a single APK file."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(script_dir, input_path)
    
    if os.path.isdir(input_path):
        apk_files = [os.path.join(input_path, f) for f in os.listdir(input_path) if f.endswith('.apk')]
    elif os.path.isfile(input_path) and input_path.endswith('.apk'):
        apk_files = [input_path]
    else:
        print(colored(f"Error: The path '{input_path}' is not a valid APK file or directory containing APKs.", 'red'))
        sys.exit(1)

    for apk_path in apk_files:
        file_name = os.path.basename(apk_path)
        print(colored(f"\nProcessing APK: {file_name}", 'cyan'))
        app_id, firebase_url, google_api_key = extract_info_from_apk(apk_path)

        print(f"App ID: {colored(app_id, 'green')}")
        print(f"Firebase URL: {colored(firebase_url, 'green')}")
        print(f"Google API Key: {colored(google_api_key, 'green')}")

        vulnerabilities = check_firebase_vulnerability(firebase_url, google_api_key, app_id, file_name)
        vulnerabilities.extend(check_unauthorized_signup(google_api_key, file_name))

        print(colored("\nVulnerability Check Results:", 'yellow'))
        for vuln in vulnerabilities:
            print(f"- {colored(vuln, 'red' if 'detected' in vuln or 'enabled' in vuln else 'green')}")

def tab_complete_path(text, state):
    """Enables tab completion for file paths."""
    line = readline.get_line_buffer()
    expanded_path = os.path.expanduser(line)
    matches = [f for f in os.listdir(os.path.dirname(expanded_path) or '.') if f.startswith(os.path.basename(expanded_path))]
    if state < len(matches):
        return matches[state]
    else:
        return None

def get_apk_path():
    """Prompts the user to enter the path to an APK file or folder with tab completion."""
    readline.set_completer(tab_complete_path)
    readline.parse_and_bind("tab: complete")
    return input(colored("Enter the path to the APK file: ", "yellow"))

if __name__ == "__main__":
    check_for_updates()
    if len(sys.argv) == 2 and sys.argv[1] in ["-h", "--help"]:
        print_banner()
        help()
        sys.exit(0)

    print_banner()
    apk_path = get_apk_path()
    process_apks(apk_path)
