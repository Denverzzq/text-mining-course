# 功勋科学家-黄旭华-传记文本分词

### 现在，可以开启你的小组项目的第一个小小任务啦！就是对一小段有关“功勋科学家”的文本进行分词处理。


```python
# 简单分词
```


```python
import jieba
```


```python
seg_list_huang = jieba.cut('黄旭华，1926年3月12日出生于广东省汕尾市，原籍广东省揭阳市。1949年毕业于上海交通大学。历任北京海军核潜艇研究室副总工程师、中船重工集团公司核潜艇总体研究设计所研究员、名誉所长。1994年当选为中国工程院院士。')
```


```python
print('/'.join(seg_list_huang))
```

    Building prefix dict from the default dictionary ...
    Loading model from cache C:\Users\denve\AppData\Local\Temp\jieba.cache
    Loading model cost 0.380 seconds.
    Prefix dict has been built successfully.
    

    黄旭华/，/1926/年/3/月/12/日出/生于/广东省/汕尾市/，/原籍/广东省/揭阳市/。/1949/年/毕业/于/上海交通大学/。/历任/北京/海军/核潜艇/研究室/副/总工程师/、/中/船/重工/集团公司/核潜艇/总体/研究/设计所/研究员/、/名誉/所长/。/1994/年/当选/为/中国工程院/院士/。
    


```python
# 加入用户词典
```


```python
jieba.load_userdict('dict.txt')
```


```python
seg_list_huang = jieba.cut('黄旭华，1926年3月12日出生于广东省汕尾市，原籍广东省揭阳市。1949年毕业于上海交通大学。历任北京海军核潜艇研究室副总工程师、中船重工集团公司核潜艇总体研究设计所研究员、名誉所长。1994年当选为中国工程院院士。')
```


```python
print('/'.join(seg_list_huang))
```

    黄旭华/，/1926/年/3/月/12/日出/生于/广东省/汕尾市/，/原籍/广东省/揭阳市/。/1949/年/毕业/于/上海交通大学/。/历任/北京/海军/核潜艇/研究室/副/总工程师/、/中船重工集团公司/核潜艇/总体/研究/设计所/研究员/、/名誉/所长/。/1994/年/当选/为/中国工程院院士/。
    


```python
# 加入词典之后，哪些词汇被分出来了呢？
```


```python
# 使用停用词表
```


```python
# stopwords = [line.strip() for line in open('stop_words.txt','r', encoding='utf-8').readlines()]
```


```python
stopwords = open('stop_words.txt','r', encoding='utf-8').read()
stopwords = stopwords.split('\n')
```


```python
stopwords
```




    ['的', '了', '是', '啊', '、', '，', '。', '停用']




```python
seg_list_huang = jieba.cut('黄旭华，1926年3月12日出生于广东省汕尾市，原籍广东省揭阳市。1949年毕业于上海交通大学。历任北京海军核潜艇研究室副总工程师、中船重工集团公司核潜艇总体研究设计所研究员、名誉所长。1994年当选为中国工程院院士。')
```


```python
final = ''
```


```python
for seg in seg_list_huang:
    if seg not in stopwords:
        final+= seg+'/'
```


```python
print(final)
```

    黄旭华/1926/年/3/月/12/日出/生于/广东省/汕尾市/原籍/广东省/揭阳市/1949/年/毕业/于/上海交通大学/历任/北京/海军/核潜艇/研究室/副/总工程师/中船重工集团公司/核潜艇/总体/研究/设计所/研究员/名誉/所长/1994/年/当选/为/中国工程院院士/
    

作业的意义：

+ 你可以处理比较复杂的文本啦

+ 你开始尝试接触和理解，一些具有文化内涵的科技文献资源


```python
# dict对于保证专有名词等不被拆分具有极大意义，实际运用拆分时应当先对其进行定义
```


```python

```
