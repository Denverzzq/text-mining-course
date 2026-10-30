## 在deepseek api平台申请API，拿到API-key；然后交一点钱，很便宜的。


```python
# https://platform.deepseek.com/transactions
```

### 以下是一段采用大语言模型处理“心理-身体”病痛文本，细粒度情感/感受/症状实体与实体关系提取的工作


```python
import requests
import json

# DeepSeek API 端点
url = "https://api.deepseek.com/v1/chat/completions"

# 替换为您的 DeepSeek API 密钥
API_KEY = "替换加密" # 直接复制过来

# 请求头，包含 API 密钥和内容类型
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}
```


```python
# 患者描述文本
text = (
    "我今年58岁，退休后感到生活失去了重心，开始出现失眠、头痛和疲乏无力的症状。"
    "后来，皮肤变得异常敏感，连衣服的触碰都像针扎一样疼痛。"
    "我常常感到心慌、胸闷，背部沉重得像压了一块石头。"
    "对光线和声音变得极度敏感，电话铃声都会让我惊恐。"
    "多次到医院检查，结果都显示没有器质性疾病。"
    "我变得不愿出门，不想与人交流，整天把自己关在屋里，拉紧窗帘，感觉生活毫无意义。"
)

# 构建提示词，要求模型提取细粒度情感实体
prompt = (
    "请从以下患者描述中提取出具体的身体部位、症状以及对应的情感状态，"
    "并以 JSON 格式返回，格式如下："
    "{'实体': [{'部位': '...', '症状': '...', '情感': '...'}, ...]}\n\n"
    f"患者描述：{text}"
)
```


```python
# 请求体，包含模型参数和提示词
data = {
    "model": "deepseek-chat",
    "messages": [
        {"role": "user", "content": prompt}
    ],
    "temperature": 0.3
}

try:
    # 发送 POST 请求
    response = requests.post(url, headers=headers, data=json.dumps(data))

    # 检查响应状态码
    if response.status_code == 200:
        # 解析 JSON 响应
        result = response.json()
        # 提取模型生成的内容
        generated_text = result['choices'][0]['message']['content']
        print("细粒度情感实体抽取结果:")
        print(generated_text)
    else:
        # 处理错误响应
        print(f"请求失败，状态码: {response.status_code}")
        print(f"错误信息: {response.text}")

except requests.exceptions.RequestException as e:
    # 处理网络请求异常
    print(f"网络请求失败: {e}")
except json.JSONDecodeError as e:
    # 处理 JSON 解析异常
    print(f"JSON 解析失败: {e}")
except Exception as e:
    # 处理其他异常
    print(f"发生未知错误: {e}")

```

    细粒度情感实体抽取结果:
    {
      "实体": [
        {
          "部位": "头部",
          "症状": "头痛",
          "情感": "生活失去了重心"
        },
        {
          "部位": "全身",
          "症状": "失眠",
          "情感": "生活失去了重心"
        },
        {
          "部位": "全身",
          "症状": "疲乏无力",
          "情感": "生活失去了重心"
        },
        {
          "部位": "皮肤",
          "症状": "异常敏感，衣服触碰像针扎一样疼痛",
          "情感": "痛苦"
        },
        {
          "部位": "心脏",
          "症状": "心慌",
          "情感": "焦虑"
        },
        {
          "部位": "胸部",
          "症状": "胸闷",
          "情感": "焦虑"
        },
        {
          "部位": "背部",
          "症状": "沉重得像压了一块石头",
          "情感": "压抑"
        },
        {
          "部位": "感官（光线和声音）",
          "症状": "极度敏感，电话铃声引发惊恐",
          "情感": "惊恐"
        },
        {
          "部位": "心理/行为",
          "症状": "不愿出门，不想与人交流，把自己关在屋里，拉紧窗帘",
          "情感": "生活毫无意义"
        }
      ]
    }
    

## 提问：
+ 1，请问你觉得大语言模型在识别患者的身体、心理、情感的工作中，表现如何？
+ 2，除了健康领域的情感世界理解与识别，你还能够想到哪些其他重要的领域，可以开展类似的工作呢？


```python

```
