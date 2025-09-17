import requests
import json

# 定义请求URL
url = "http://localhost:8848/api/v1/math/sqrt"

# 定义请求头
headers = {
    "Content-Type": "application/json"
}

# 定义请求数据
data = {
    "user_question": "二次根式的数学定义"
}

# 发送POST请求
response = requests.post(url, headers=headers, data=json.dumps(data))

# 打印响
print("状态码:", response.status_code)
print("响应内容:", response.json())