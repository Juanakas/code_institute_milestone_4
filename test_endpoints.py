import urllib.request
import urllib.error
import urllib.parse
import http.cookiejar
import sys

BASE_URL = "http://127.0.0.1:8000"

# Use a cookie jar to handle CSRF tokens
cookie_jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))

ENDPOINTS = [
    ("/", "GET", {}),
    ("/subscriptions/", "GET", {}),
    ("/accounts/signup/", "GET", {}),
    ("/accounts/login/", "GET", {}),
    ("/practice/", "GET", {}),
    ("/members/", "GET", {}),
    # POST requests - get CSRF token first from pricing page
    ("/subscriptions/activate-free/", "POST", {"test": "1"}),
    ("/practice/new/", "POST", {"test": "1"}),
]

print("Testing GET endpoints:")
print("=" * 60)

for endpoint, method, data in ENDPOINTS:
    if method == "GET":
        url = BASE_URL + endpoint
        try:
            response = opener.open(url)
            status = response.status
            print(f"{endpoint:30} -> {status}")
        except urllib.error.HTTPError as e:
            print(f"{endpoint:30} -> {e.code}")
            if e.code == 500:
                print(f"  ERROR RESPONSE (first 500 chars):")
                print(f"  {e.read().decode('utf-8', errors='ignore')[:500]}")
        except Exception as e:
            print(f"{endpoint:30} -> ERROR: {e}")

print("\n\nTesting POST endpoints (may require authentication):")
print("=" * 60)

for endpoint, method, data in ENDPOINTS:
    if method == "POST":
        url = BASE_URL + endpoint
        
        # Try to get a CSRF token first
        try:
            # First GET the page to get CSRF token
            response = opener.open(url)
            content = response.read().decode('utf-8', errors='ignore')
            
            # Extract CSRF token
            import re
            csrf_match = re.search(r'csrfmiddlewaretoken["\']?\s*:\s*["\']([^"\']+)["\']', content)
            csrf_token = csrf_match.group(1) if csrf_match else ''
            
            if not csrf_token:
                csrf_match = re.search(r'name=["\']csrfmiddlewaretoken["\'][^>]*value=["\']([^"\']+)["\']', content)
                csrf_token = csrf_match.group(1) if csrf_match else ''
            
            # POST request
            post_data = {'csrfmiddlewaretoken': csrf_token} if csrf_token else {}
            post_data.update(data)
            
            encoded_data = urllib.parse.urlencode(post_data).encode('utf-8')
            request = urllib.request.Request(url, data=encoded_data, method='POST')
            response = opener.open(request)
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
