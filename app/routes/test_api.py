import requests

url = "http://127.0.0.1:5000/api/login"

data = {
    "username": "admin",
    "password": "Admin@12345"
}

response = requests.post(
    url,
    json=data
)

print("Status:", response.status_code)
print("Response:")
print(response.text)