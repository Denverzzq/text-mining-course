## 在deepseek api平台申请API，拿到API-key；然后交一点钱，很便宜的。


```python
# https://platform.deepseek.com/transactions
# 此处使用了Gemini的api
```

![image.png](image.png)


```python
import requests
import json

# 定义Gemini API的URL和headers
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent"
API_KEY = "xxxxxxxxxxxxxxxxxxxxxxx"  #直接复制过来
```


```python
# 准备prompt和论文文本
paper_text = """
随着肿瘤免疫微环境（Tumor Immune Microenvironment, TIME）研究的深入，
T细胞耗竭（T cell exhaustion）被认为是限制免疫治疗效果的关键机制之一。
本研究基于免疫编辑理论，提出了一种基于单细胞RNA测序（scRNA-seq）的T细胞状态动态识别方法。
具体而言，我们使用Seurat与Monocle3等生物信息学工具对50例非小细胞肺癌患者的肿瘤样本进行细胞亚群聚类和轨迹分析，
结合pseudotime推断T细胞从激活到耗竭的转化过程。此外，借助CellChat软件构建细胞间通讯网络，
进一步识别可能诱导T细胞耗竭的免疫抑制信号通路，如PD-1/PD-L1和TGF-β路径。研究结果揭示了T细胞功能衰竭的关键节点，并为个体化免疫治疗提供了潜在靶点。
"""

prompt = f"""
请从以下科技论文文本中提取包含理论、方法、工具的实体或专业术语，以json字典的格式输出:
如果可以抽取实体，请你进行，并且讲出如何识别
{paper_text}
"""
```


```python
# 准备请求数据
data = {
    "contents": [
        {
            "parts": [
                {"text": prompt}
            ]
        }
    ],
    "generationConfig": {
        "temperature": 0.3
    }
}

headers = {
    "Content-Type": "application/json",
    "x-goog-api-key": API_KEY
}

# 发送请求
response = requests.post(GEMINI_API_URL, headers=headers, data=json.dumps(data))
```


```python
# 处理响应
if response.status_code == 200:
    result = response.json()
    try:
        entities = result['candidates'][0]['content']['parts'][0]['text']
        print("提取到的实体和专业术语:")
        print(entities)
    except (KeyError, IndexError):
        print("无法解析API响应，原始响应:")
        print(result)
else:
    print(f"请求失败，状态码: {response.status_code}")
    print(response.text)

```

    提取到的实体和专业术语:
    根据您提供的科技论文文本，以下是提取的包含“理论”、“方法”、“工具”的实体及专业术语，并以 JSON 字典格式输出。同时，在 JSON 之后附上了识别这些实体的方法和依据。
    
    ### JSON 字典输出
    
    ```json
    {
      "理论": [
        "肿瘤免疫微环境",
        "T细胞耗竭",
        "免疫编辑理论"
      ],
      "方法": [
        "T细胞状态动态识别方法",
        "细胞亚群聚类",
        "轨迹分析",
        "pseudotime推断",
        "细胞间通讯网络构建"
      ],
      "工具": [
        "单细胞RNA测序",
        "scRNA-seq",
        "Seurat",
        "Monocle3",
        "CellChat"
      ]
    }
    ```
    
    ---
    
    ### 实体识别方法与依据说明
    
    为了准确从文本中提取出理论、方法和工具类实体，采用了以下识别策略和语言特征分析：
    
    1. **理论 (Theory / Core Concepts) 的识别：**
       * **特征：** 通常表现为领域内的核心科学假说、病理机制或生物学概念。
       * **识别依据：** 文本中直接出现了“免疫编辑理论”这一带有“理论”字眼的实体；同时，“肿瘤免疫微环境 (TIME)”和“T细胞耗竭 (T cell exhaustion)”是支撑整篇研究的生物学基础和核心机制概念，属于宏观的理论背景范畴。
    
    2. **方法 (Method) 的识别：**
       * **特征：** 往往伴随着动宾结构（如“进行...分析”、“推断”）或研究策略的描述，表现为具体的算法、流程或分析手段。
       * **识别依据：** 
         * 文本中明确出现了“提出了一种...动态识别方法”。
         * 通过动作触发词识别出“细胞亚群聚类”、“轨迹分析”、“pseudotime推断”（基于拟时序的推断方法）以及“细胞间通讯网络”（构建网络的方法过程），这些都是数据分析的具体技术路线。
    
    3. **工具 (Tool / Software / Technology) 的识别：**
       * **特征：** 通常是专有名词、软件名称、编程包（Package）或高通量实验技术平台，首字母往往大写或带有版本号。
       * **识别依据：**
         * 实验技术层面：“单细胞RNA测序（scRNA-seq）”被用作底层技术手段。
         * 生物信息学软件层面：文本中明确提到了 `Seurat`、`Monocle3` 和 `CellChat`。这些是单细胞测序数据分析领域知名的 R 语言软件包/软件工具，通过上下文中的“使用...与...等生物信息学工具”和“借助...软件”可以直接精准定位。
    

## 提问：
+ 1，使用deepseek开展工作的感觉如何？
+ 2，你觉得大语言模型的活干的怎么样？
+ 3，还是那个问题，如果可以抽取实体，那么如何识别关系呢？你试试用大语言模型识别下关系？


```python
# 1.使用了Gemini，极大改善了工作条件，多快好省。 2.在没有进行prompt时候，大多数情况勉勉强强，但是多试几次会改善。 3.Gemini给出了方法，在输出部分。
```
