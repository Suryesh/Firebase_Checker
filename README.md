# Firebase_Checker

A Firebase Checker is powerful Python tool to analyze APK files for Firebase-related vulnerabilities, such as open Firebase databases, unauthorized Firebase signup, and Firebase Remote Config misconfigurations. This tool is designed for security researchers, developers, and penetration testers to identify potential security risks in Android applications that use Firebase.

# Features

- **Extract Firebase Details:** Automatically extracts Firebase App ID, Firebase URL, and Google API Key from APK files.
- **Check for Open Firebase Databases:** Detects if the Firebase database is publicly accessible.
- **Unauthorized Signup Check:** Tests if unauthorized Firebase signup is possible using the extracted Google API Key.
- **Firebase Remote Config Check:** Identifies if Firebase Remote Config is enabled and accessible.
- **Detailed Reporting:** Provides clear and colored output for vulnerability results.
- **Email Verification:** Sending email verification link to registered email.

# Installation

## Prerequisites

Python 3.x

`requests` library (`pip install requests`)

`termcolor` library (`pip install termcolor`)

## Steps

1. Clone this Repository

```
git clone https://github.com/Suryesh/Firebase_Checker.git && cd Firebase_Checker
```

2. Install the required dependencies:

```
pip install -r requirements.txt
```

3. Now give Executable permission

```
chmod +x firebase-checker.py
```

# Basic Usages

1. Check help for usages

```
python3  firebase-checker.py -h
```
2. Run the script:

```
python3 firebase-checker.py
```

3. Enter the path to the APK file or folder containing APKs when prompted:

```
Enter the path to the APK file or folder containing APKs: /path/to/apk/file.apk
```

4. Now the tool will analyze the APK and display the results.

# PoC - 1

### Help

![Help](img/help.png)

### Vulnerability Checking

![Checking](img/checking.png)

### Detected remote Config misconfiguration

![Remote](img/remote-miscon.png)

### Signup Enable for Unauthorized user

![Signup](img/signup-miscon.png)

### Fetching Register User Information

![User](img/user-info.png)

### Generating Access Token

![Acess](img/access-token-generate.png)

### Vulnerability Detected

![vulnerability](img/vulnerability-check-result.png)


# PoC - 2

![File](img/file-2.png)

![Signup](img/signup-miscon-2.png)

![User](img/user-info-2.png)

![Access](img/access-token-generate-2.png)

![Vulnerability](img/vulnerability-check-result-2.png)


# PoC -3

### API Key in Remote Config file

![Apikey](img/apikey.png)

## Added new email verification features
![Email-sent](img/email_sent.png)

![Email-received](img/email_received.png)

## License
This project is licensed under the MIT License. See the [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) file for details.

 ## 💰 You can help me by Donating
 
  [![BuyMeACoffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-ffdd00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/suryesh_92) [![PayPal](https://img.shields.io/badge/PayPal-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://www.paypal.com/paypalme/Suryesh92) 


## Disclaimer
This tool is intended for educational and ethical testing purposes only. Do not use it for any illegal or unauthorized activities. The author is not responsible for any misuse of this tool.
