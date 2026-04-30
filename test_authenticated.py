import urllib.request
import urllib.error
import urllib.parse
import http.cookiejar
import sys

BASE_URL = "http://127.0.0.1:8000"

# Use a cookie jar to handle CSRF tokens and session cookies
cookie_jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))

print("Step 1: Getting login page to extract CSRF token...")
try:
    response = opener.open(BASE_URL + "/accounts/login/")
    login_html = response.read().decode('utf-8', errors='ignore')
    
    # Extract CSRF token
    import re
    csrf_match = re.search(r'name=["\']csrfmiddlewaretoken["\'][^>]*value=["\']([^"\']+)["\']', login_html)
    csrf_token = csrf_match.group(1) if csrf_match else ''
    
    if not csrf_token:
        print("ERROR: Could not find CSRF token")
        sys.exit(1)
    
    print(f"Got CSRF token: {csrf_token[:20]}...")
except Exception as e:
    print(f"ERROR getting login page: {e}")
    sys.exit(1)

print("\nStep 2: Logging in with testuser...")
try:
    login_data = {
        'csrfmiddlewaretoken': csrf_token,
        'username': 'testuser',
        'password': 'testpass123',
    }
    encoded_data = urllib.parse.urlencode(login_data).encode('utf-8')
    request = urllib.request.Request(
        BASE_URL + "/accounts/login/",
        data=encoded_data,
        method='POST'
    )
    response = opener.open(request)
    
    # Check if we got redirected (302) which means login was successful
    print(f"Login response status: {response.status}")
    
except urllib.error.HTTPError as e:
    print(f"ERROR during login: {e.code}")
    print(f"Response: {e.read().decode('utf-8', errors='ignore')[:500]}")
    sys.exit(1)

print("\nStep 3: Testing authenticated endpoints...")

auth_endpoints = [
    ("/members/", "GET"),
    ("/subscriptions/status/", "GET"),
    ("/practice/", "GET"),
]

for endpoint, method in auth_endpoints:
    url = BASE_URL + endpoint
    try:
        response = opener.open(url)
        status = response.status
        print(f"{endpoint:30} -> {status}")
    except urllib.error.HTTPError as e:
        print(f"{endpoint:30} -> {e.code}")
        if e.code == 500:
            error_text = e.read().decode('utf-8', errors='ignore')
            print(f"  ERROR RESPONSE (first 500 chars):")
            print(f"  {error_text[:500]}")
    except Exception as e:
        print(f"{endpoint:30} -> ERROR: {e}")
