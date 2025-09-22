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

SCRIPT_VERSION = "1.2.2"
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

# display Help
def help():
    """Displays help information about the script."""
    help_text = """
    🔥 Firebase Checker is tool to test Firebase security misconfigurations in both Android APK files and web applications:
    
    📱 TESTING MODES:
    - APK File Analysis: Automatically extract Firebase config from Android apps
    - Manual Web App Testing: Test web applications by entering Firebase details manually

    🔍 SECURITY CHECKS PERFORMED:
    ✅ Realtime Database Security Testing
    ✅ Anonymous Authentication Security Testing
    ✅ Remote Config Security Testing
    ✅ Firebase Storage Security Testing

    📋 USAGE:

    1. Basic APK Testing:
       python3 firebase-checker.py
       → Choose option 1 → Enter APK path

    2. Web Application Testing:
       python3 firebase-checker.py  
       → Choose option 2 → Enter Firebase details manually

    - For more information, visit: https://github.com/Suryesh/Firebase_Checker
    - And for live Bug Bounty session join our Discord server and subscribe to our channel.
    
    Youtube: https://www.youtube.com/@suryesh_92
    Discord : https://discord.com/invite/EfgnVNbh3N
    """
    print(colored(help_text, 'cyan'))

# Chooese testing method
def get_testing_method():
    """Ask user if they want to test APK or enter details manually."""
    print(colored("\nChoose testing method:", 'cyan'))
    print(colored("1. Test APK file", 'green'))
    print(colored("2. Enter Firebase details manually", 'green'))
    
    while True:
        choice = input(colored("\nEnter your choice (1 or 2): ", 'yellow')).strip()
        if choice == '1':
            return 'apk'
        elif choice == '2':
            return 'manual'
        else:
            print(colored("Invalid choice! Please enter 1 or 2.", 'red'))

def get_manual_input():
    """Get Firebase details from user manually."""
    print(colored("\nEnter Firebase details (press Enter to skip if not available):", 'cyan'))
    
    app_id = input(colored("App ID (format: 1:123456789:android:abcdef123456): ", 'yellow')).strip()
    if not app_id:
        app_id = None
    
    firebase_url = input(colored("Firebase URL (format: https://project-id.firebaseio.com): ", 'yellow')).strip()
    if not firebase_url:
        firebase_url = None
    
    google_api_key = input(colored("Google API Key (format: AIzaSyD...): ", 'yellow')).strip()
    if not google_api_key:
        google_api_key = None
    
    storage_bucket = input(colored("Storage Bucket (format: project-id.appspot.com): ", 'yellow')).strip()
    if not storage_bucket:
        storage_bucket = None
    
    return app_id, firebase_url, google_api_key, storage_bucket

# Email Generator
def generate_random_email():
    """Generates a random email address."""
    username = str(uuid.uuid4())[:10]
    domain = random.choice(["gmail.com", "yahoo.com", "outlook.com", "protonmail.com"])
    return f"{username}@{domain}"

# Extract info from apk file
def extract_info_from_apk(apk_path):
    """Extracts App ID, Firebase URL, and Google API Key from an APK file."""
    result = subprocess.run(['strings', apk_path], capture_output=True, text=True)
    strings_output = result.stdout

    app_id_match = re.search(r'1:(\d+):android:([a-f0-9]+)', strings_output)
    firebase_url_match = re.search(r'https://[a-zA-Z0-9-]+\.firebaseio\.com', strings_output)
    google_api_key_match = re.search(r'AIza[0-9A-Za-z-_]{35}', strings_output)
    storage_bucket_match = re.search(r'([a-zA-Z0-9-]+)\.appspot\.com', strings_output)

    app_id = app_id_match.group(0) if app_id_match else None
    firebase_url = firebase_url_match.group(0) if firebase_url_match else None
    google_api_key = google_api_key_match.group(0) if google_api_key_match else None
    storage_bucket = storage_bucket_match.group(0) if storage_bucket_match else None

    return app_id, firebase_url, google_api_key, storage_bucket

def send_alert(message):
    """Prints alert messages in red."""
    print(colored(f"ALERT : {message}", 'red'))

def execute_curl_command(curl_cmd):
    """Executes a curl command and prints the output."""
    print(colored(f"\nExecuting Curl Command: {curl_cmd}", 'blue'))
    result = subprocess.run(curl_cmd, shell=True, capture_output=True, text=True)
    print(colored(f"\nCurl Output:\n{result.stdout}", 'magenta'))
    return result.stdout

# Checkings files type in bucket
def get_file_type(filename):
    """Dynamically detect file type from extension or content."""
    media_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', 
                       '.mp4', '.avi', '.mov', '.mkv', '.webm',
                       '.mp3', '.wav', '.ogg', '.m4a',
                       '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip', '.rar']
    
    data_extensions = ['.json', '.xml', '.txt', '.csv', '.log']
    file_ext = os.path.splitext(filename.lower())[1]
    
    if file_ext in media_extensions:
        return 'media'
    elif file_ext in data_extensions:
        return 'data'
    elif any(keyword in filename.lower() for keyword in ['config', 'settings', 'data', 'user', 'profile']):
        return 'data'
    else:
        return 'unknown'

# Download data from bucket
def download_file(bucket_name, file_path, file_type):
    """Download a file from Firebase Storage."""
    try:
        encoded_path = quote(file_path, safe='')
        test_url = f"https://firebasestorage.googleapis.com/v0/b/{bucket_name}/o/{encoded_path}"
        
        response = requests.get(test_url, timeout=10)
        if response.status_code == 200:
            file_info = response.json()
            download_tokens = file_info.get('downloadTokens')
            
            if download_tokens:
                download_url = f"{test_url}?alt=media&token={download_tokens}"
                download_response = requests.get(download_url, timeout=30)
                
                if download_response.status_code == 200:
                    # Create downloads directory if it doesn't exist
                    os.makedirs('downloads', exist_ok=True)
                    
                    # Create subdirectory structure if path has folders
                    safe_path = re.sub(r'[^a-zA-Z0-9./_-]', '_', file_path)
                    download_path = os.path.join('downloads', safe_path)
                    
                    # Create directories if needed
                    os.makedirs(os.path.dirname(download_path), exist_ok=True)
                    
                    with open(download_path, 'wb') as f:
                        f.write(download_response.content)
                    
                    file_size = len(download_response.content)
                    return f"Downloaded successfully: {download_path} ({file_size} bytes)"
                else:
                    return f"Download failed: {download_response.status_code}"
            else:
                return "No download token available"
        else:
            return f"File access denied: {response.status_code}"
    except Exception as e:
        return f"Download error: {str(e)}"
    
# testing file is accessible or not
def test_file_access(bucket_name, file_path, file_type):
    """Test file access based on file type."""
    try:
        encoded_path = quote(file_path, safe='')
        test_url = f"https://firebasestorage.googleapis.com/v0/b/{bucket_name}/o/{encoded_path}"
        
        response = requests.get(test_url, timeout=10)
        if response.status_code == 200:
            file_info = response.json()
            download_tokens = file_info.get('downloadTokens')
            
            if download_tokens:
                download_url = f"{test_url}?alt=media&token={download_tokens}"
                
                if file_type == 'media':
                    # For media files, test download
                    download_response = requests.get(download_url, timeout=10)
                    if download_response.status_code == 200:
                        return "Media file downloadable"
                    else:
                        return f"Media download failed: {download_response.status_code}"
                else:
                    # For data files, fetch and display content
                    download_response = requests.get(download_url, timeout=10)
                    if download_response.status_code == 200:
                        content = download_response.text
                        if len(content) > 500:  # Truncate long content
                            content = content[:500] + "..."
                        return f"Data file accessible. Content preview: {content}"
                    else:
                        return f"Data access failed: {download_response.status_code}"
            else:
                return "No download token"
        else:
            return f"Access denied: {response.status_code}"
    except Exception as e:
        return f"File test failed: {str(e)}"

# Firebase Storage vulnerability check
def check_firebase_storage(storage_bucket, source_name):
    """Checks for Firebase Storage vulnerabilities."""
    vulnerabilities = []
    downloadable_files = []
    
    if not storage_bucket:
        vulnerabilities.append(("Storage bucket not provided", "info"))
        return vulnerabilities, downloadable_files
    
    try:
        storage_url = f"https://firebasestorage.googleapis.com/v0/b/{storage_bucket}/o/"
        print(colored(f"\nTesting Firebase Storage Bucket: {storage_bucket}", 'cyan'))
        
        response = requests.get(storage_url, timeout=10)
        
        if response.status_code == 200:
            vulnerabilities.append(("Firebase storage publicly readable - file exposure detected", "vulnerable"))
            send_alert(f"Open Firebase storage detected. Bucket: {storage_bucket}")
            execute_curl_command(f'curl "{storage_url}"')
            
            try:
                data = response.json()
                if 'items' in data:
                    file_count = len(data['items'])
                    vulnerabilities.append((f"Found {file_count} files in storage", "vulnerable"))
                    
                    for item in data['items']:
                        name = item.get('name', 'Unknown')
                        size = item.get('size', 0)
                        file_type = get_file_type(name)
                        
                        access_test = test_file_access(storage_bucket, name, file_type)
                        if "downloadable" in access_test.lower() or "accessible" in access_test.lower():
                            downloadable_files.append((file_type, name, size))
                    
                    if downloadable_files:
                        vulnerabilities.append((f"Accessible files found: {len(downloadable_files)}/{file_count}", "vulnerable"))
                        
                        display_count = min(5, len(downloadable_files))
                        vulnerabilities.append((f"First {display_count} accessible files:", "info"))
                        for i, (file_type, file_path, size) in enumerate(downloadable_files[:display_count]):
                            vulnerabilities.append((f"  {i+1}. {file_path} ({size} bytes) [{file_type}]", "info"))
                        
                        if len(downloadable_files) > display_count:
                            vulnerabilities.append((f"  ... and {len(downloadable_files) - display_count} more files", "info"))
                    else:
                        vulnerabilities.append(("No accessible files found", "secure"))
                            
                else:
                    vulnerabilities.append(("No files found in storage bucket", "secure"))
                    
            except Exception as e:
                vulnerabilities.append((f"Error parsing storage response: {e}", "error"))
                
        elif response.status_code == 400:
            vulnerabilities.append(("Firebase Storage bucket listing disabled - secure", "secure"))
            execute_curl_command(f'curl "{storage_url}"')
        elif response.status_code == 401:
            vulnerabilities.append(("Firebase Storage requires authentication - secure", "secure"))
            execute_curl_command(f'curl "{storage_url}"')
        elif response.status_code == 403:
            vulnerabilities.append(("Firebase Storage access forbidden - secure", "secure"))
            execute_curl_command(f'curl "{storage_url}"')
        elif response.status_code == 404:
            vulnerabilities.append(("Firebase Storage bucket not found", "info"))
            execute_curl_command(f'curl "{storage_url}"')
        else:
            vulnerabilities.append((f"Storage bucket returned HTTP {response.status_code}", "info"))
            execute_curl_command(f'curl "{storage_url}"')
    
    except Exception as e:
        vulnerabilities.append((f"Storage test failed: {str(e)}", "error"))
        try:
            storage_url = f"https://firebasestorage.googleapis.com/v0/b/{storage_bucket}/o/"
            execute_curl_command(f'curl "{storage_url}"')
        except:
            pass
    
    return vulnerabilities, downloadable_files


def offer_file_downloads(storage_bucket, downloadable_files):
    """Offer to download accessible files."""
    if not downloadable_files:
        return
    
    print(colored(f"\n📥 Downloadable Files Found ({len(downloadable_files)} files)", 'green'))
    print(colored("Would you like to download any files?", 'yellow'))
    
    display_count = min(10, len(downloadable_files))
    for i, (file_type, file_path, size) in enumerate(downloadable_files[:display_count], 1):
        print(f"{i}. {file_path} ({size} bytes) [{file_type}]")
    
    option_start = display_count + 1
    print(f"{option_start}. Download all {len(downloadable_files)} files")
    print(f"{option_start + 1}. Show all files list")
    print(f"{option_start + 2}. Skip downloading")
    
    try:
        choice = input(colored("\nEnter your choice (number): ", 'yellow')).strip()
        if choice.isdigit():
            choice_num = int(choice)
            
            if choice_num == option_start:
                print(colored(f"Downloading all {len(downloadable_files)} files...", 'cyan'))
                successful_downloads = 0
                
                for i, (file_type, file_path, size) in enumerate(downloadable_files, 1):
                    print(f"[{i}/{len(downloadable_files)}] Downloading: {file_path}")
                    result = download_file(storage_bucket, file_path, file_type)
                    if "successfully" in result.lower():
                        successful_downloads += 1
                    print(f"  Result: {result}")
                
                print(colored(f"\nDownload completed: {successful_downloads}/{len(downloadable_files)} files successful", 
                             'green' if successful_downloads > 0 else 'yellow'))
                    
            elif choice_num == option_start + 1:
                print(colored(f"\nAll {len(downloadable_files)} accessible files:", 'cyan'))
                for i, (file_type, file_path, size) in enumerate(downloadable_files, 1):
                    print(f"{i}. {file_path} ({size} bytes) [{file_type}]")
                return offer_file_downloads(storage_bucket, downloadable_files)
                    
            elif choice_num == option_start + 2:
                print(colored("Skipping file downloads.", 'blue'))
                
            elif 1 <= choice_num <= display_count:
                file_type, file_path, size = downloadable_files[choice_num - 1]
                print(colored(f"Downloading: {file_path}", 'cyan'))
                result = download_file(storage_bucket, file_path, file_type)
                print(f"Result: {result}")
                more = input(colored("Download another file? (y/n): ", 'yellow')).lower()
                if more == 'y':
                    return offer_file_downloads(storage_bucket, downloadable_files)
                
            else:
                print(colored("Invalid choice. Skipping downloads.", 'red'))
    except Exception as e:
        print(colored(f"Error during download: {e}", 'red'))


# Checking for open database
def check_firebase_vulnerability(firebase_url, google_api_key, app_id, source_name):
    """Checks for Firebase vulnerabilities, including open databases and unauthorized signup."""
    vulnerabilities = []
    
    if firebase_url:
        try:
            response = requests.get(f"{firebase_url}/.json", timeout=5)
            if response.status_code == 200:
                vulnerabilities.append(("Firebase database publicly readable - data exposure detected", "vulnerable"))
                send_alert(f"Open Firebase database detected. URL: {firebase_url}")
                execute_curl_command(f"curl {firebase_url}/.json")
            elif response.status_code == 401:
                vulnerabilities.append(("Firebase database requires authentication - secure", "secure"))
            elif response.status_code == 403:
                vulnerabilities.append(("Firebase database access forbidden - secure", "secure"))
            elif response.status_code == 404:
                vulnerabilities.append(("Firebase database not found", "info"))
            else:
                vulnerabilities.append(("Firebase database is not openly accessible", "secure"))
        except requests.RequestException:
            vulnerabilities.append(("Failed to check Firebase database", "error"))

# checking for remoteconfig file
    if google_api_key and app_id:
        try:
            project_id = app_id.split(':')[1]
            url = f"https://firebaseremoteconfig.googleapis.com/v1/projects/{project_id}/namespaces/firebase:fetch?key={google_api_key}"
            body = {"appId": app_id, "appInstanceId": "required_but_unused_value"}

            response = requests.post(url, json=body, timeout=5)
            if response.status_code == 200 and response.json().get("state") != "NO_TEMPLATE":
                vulnerabilities.append(("Firebase Remote Config is enabled", "vulnerable"))
                send_alert(f"Firebase Remote Config enabled. URL: {url}")
                execute_curl_command(f"curl -X POST '{url}' -H 'Content-Type: application/json' -d '{json.dumps(body)}'")
            else:
                vulnerabilities.append(("Firebase Remote Config is disabled or inaccessible", "secure"))
        except requests.RequestException as e:
            vulnerabilities.append((f"Failed to check Firebase Remote Config: {str(e)}", "error"))
    
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

# checking for anonymous signup
def check_unauthorized_signup(google_api_key, source_name):
    """Checks if unauthorized Firebase signup is possible."""
    vulnerabilities = []
    id_token = None
    
    if not google_api_key:
        vulnerabilities.append(("Google API Key not provided - cannot test signup", "info"))
        return vulnerabilities
    
    signup_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={google_api_key}"
    user_email = input(colored("Enter email for signup: ", "yellow"))
    signup_payload = json.dumps({"email": user_email, "password": "Test@Pass123", "returnSecureToken": True})

    send_alert(f"Testing unauthorized signup on {signup_url}")
    response = execute_curl_command(f"curl -X POST '{signup_url}' -H 'Content-Type: application/json' -d '{signup_payload}'")
    
    if 'idToken' in response:
        vulnerabilities.append(("Unauthorized Firebase signup is enabled - security risk", "vulnerable"))
        send_alert("Unauthorized signup is enabled!...")
        
        try:
            response_json = json.loads(response)
            id_token = response_json.get("idToken")
            refresh_token = response_json.get("refreshToken")

            if id_token:
                print(colored("\nAttempting to send verification email...", "blue"))
                send_verification_email(google_api_key, id_token)
               
            if refresh_token:
                token_url = f"https://securetoken.googleapis.com/v1/token?key={google_api_key}"
                token_payload = json.dumps({"grant_type": "refresh_token", "refresh_token": refresh_token})
                send_alert("Fetching access token using refresh token...")
                execute_curl_command(f"curl -X POST '{token_url}' -H 'Content-Type: application/json' -d '{token_payload}'")
        except:
            vulnerabilities.append(("Error processing signup response", "error"))
    
    if id_token:
        lookup_url = f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={google_api_key}"
        lookup_payload = json.dumps({"idToken": id_token})
        send_alert("Fetching account information using idToken...")
        execute_curl_command(f"curl -X POST '{lookup_url}' -H 'Content-Type: application/json' -d '{lookup_payload}'")
    
    return vulnerabilities

# process firebase testing for web
def process_manual_testing():
    """Process manual Firebase details testing."""
    app_id, firebase_url, google_api_key, storage_bucket = get_manual_input()
    
    print(colored(f"\nTesting Firebase Configuration:", 'cyan'))
    print(f"App ID: {colored(app_id, 'green')}")
    print(f"Firebase URL: {colored(firebase_url, 'green')}")
    print(f"Google API Key: {colored(google_api_key, 'green')}")
    print(f"Firebase Storage Bucket URL: {colored(storage_bucket, 'green')}")

    vulnerabilities = []
    vulnerabilities.extend(check_firebase_vulnerability(firebase_url, google_api_key, app_id, "manual_input"))
    storage_vulns, downloadable_files = check_firebase_storage(storage_bucket, "manual_input")
    vulnerabilities.extend(storage_vulns)
    
    if google_api_key:
        vulnerabilities.extend(check_unauthorized_signup(google_api_key, "manual_input"))
    if downloadable_files:
        offer_file_downloads(storage_bucket, downloadable_files)

    print(colored("\nVulnerability Check Results:", 'yellow'))
    vulnerable_items = [v for v in vulnerabilities if v[1] == "vulnerable"]
    secure_items = [v for v in vulnerabilities if v[1] == "secure"]
    info_items = [v for v in vulnerabilities if v[1] == "info"]
    error_items = [v for v in vulnerabilities if v[1] == "error"]
    
    if vulnerable_items:
        print(colored("\n❌ VULNERABILITIES DETECTED:", 'red'))
        for vuln, _ in vulnerable_items:
            print(f"  - {vuln}")
    
    if secure_items:
        print(colored("\n✅ SECURE CONFIGURATIONS:", 'green'))
        for vuln, _ in secure_items:
            print(f"  - {vuln}")
    
    if info_items:
        print(colored("\nℹ️  INFORMATION:", 'blue'))
        for vuln, _ in info_items:
            print(f"  - {vuln}")
    
    if error_items:
        print(colored("\n⚠️  ERRORS:", 'yellow'))
        for vuln, _ in error_items:
            print(f"  - {vuln}")

# process apk
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
        app_id, firebase_url, google_api_key, storage_bucket = extract_info_from_apk(apk_path)

        print(f"App ID: {colored(app_id, 'green')}")
        print(f"Firebase URL: {colored(firebase_url, 'green')}")
        print(f"Google API Key: {colored(google_api_key, 'green')}")
        print(f"Firebase Storage Bucket URL: {colored(storage_bucket, 'green')}")

        vulnerabilities = []
        vulnerabilities.extend(check_firebase_vulnerability(firebase_url, google_api_key, app_id, file_name))
        storage_vulns, downloadable_files = check_firebase_storage(storage_bucket, file_name)
        vulnerabilities.extend(storage_vulns)
        
        vulnerabilities.extend(check_unauthorized_signup(google_api_key, file_name))

        if downloadable_files:
            offer_file_downloads(storage_bucket, downloadable_files)
        
        vulnerable_items = [v for v in vulnerabilities if v[1] == "vulnerable"]
        secure_items = [v for v in vulnerabilities if v[1] == "secure"]
        info_items = [v for v in vulnerabilities if v[1] == "info"]
        error_items = [v for v in vulnerabilities if v[1] == "error"]
        
        if vulnerable_items:
            print(colored("\n❌ VULNERABILITIES DETECTED:", 'red'))
            for vuln, _ in vulnerable_items:
                print(f"  - {vuln}")
        
        if secure_items:
            print(colored("\n✅ SECURE CONFIGURATIONS:", 'green'))
            for vuln, _ in secure_items:
                print(f"  - {vuln}")
        
        if info_items:
            print(colored("\nℹ️  INFORMATION:", 'blue'))
            for vuln, _ in info_items:
                print(f"  - {vuln}")
        
        if error_items:
            print(colored("\n⚠️  ERRORS:", 'yellow'))
            for vuln, _ in error_items:
                print(f"  - {vuln}")

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

# Main function
if __name__ == "__main__":
    check_for_updates()
    if len(sys.argv) == 2 and sys.argv[1] in ["-h", "--help"]:
        print_banner()
        help()
        sys.exit(0)

    print_banner()
    testing_method = get_testing_method()
    
    if testing_method == 'apk':
        apk_path = get_apk_path()
        process_apks(apk_path)
    else:
        process_manual_testing()
