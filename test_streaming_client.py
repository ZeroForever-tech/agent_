import requests
import json

def test_streaming_output():
    """测试流式输出效果"""
    url = "http://localhost:8000/api/v1/math/sqrt/stream"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    # 使用简单问题进行测试
    data = {
        "user_question": "什么是二次根式？"
    }
    
    print("开始测试流式输出效果...")
    print("=" * 50)
    
    try:
        # 发送POST请求，启用流式传输
        response = requests.post(url, headers=headers, data=json.dumps(data), stream=True)
        
        # 检查响应状态码
        if response.status_code != 200:
            print(f"请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            return
        
        print("开始接收流式数据:")
        # 逐行读取响应
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                # SSE数据以"data: "开头
                if decoded_line.startswith('data: '):
                    # 提取JSON数据
                    json_data = decoded_line[6:]  # 移除"data: "前缀
                    try:
                        event_data = json.loads(json_data)
                        event_type = event_data.get('type', 'unknown')
                        event_content = event_data.get('data', '')
                        
                        print(f"[{event_type}]: {event_content}")
                        
                        # 如果收到完成信号，则结束
                        if event_type == 'complete':
                            print("=" * 50)
                            print("流式传输完成!")
                            break
                    except json.JSONDecodeError:
                        print(f"无法解析事件数据: {json_data}")
                
    except Exception as e:
        print(f"测试过程中发生错误: {e}")


def test_regular_non_streaming():
    """测试非流式接口以作对比"""
    url = "http://localhost:8000/api/v1/math/sqrt"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    data = {
        "user_question": "什么是二次根式？"
    }
    
    print("\n开始测试非流式接口...")
    print("=" * 50)
    
    try:
        # 发送POST请求
        response = requests.post(url, headers=headers, data=json.dumps(data))
        
        # 检查响应状态码
        if response.status_code != 200:
            print(f"请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            return
        
        # 打印响应内容
        result = response.json()
        print("响应内容:")
        print(f"Answer: {result['answer']}")
        print(f"Related Knowledge: {result['related_knowledge']}")
        print("=" * 50)
        print("非流式传输完成!")
                
    except Exception as e:
        print(f"测试过程中发生错误: {e}")


if __name__ == "__main__":
    print("SSE流式输出测试客户端")
    print("请确保服务端已在运行 (localhost:8000)")
    
    # 测试流式接口
    test_streaming_output()
    
    # 测试非流式接口作对比
    test_regular_non_streaming()
    
    print("\n所有测试完成!")