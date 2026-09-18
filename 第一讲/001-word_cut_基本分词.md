## 1 基本操作


```python
!pip install jieba
```

    Requirement already satisfied: jieba in C:\Users\denve\anaconda3\Lib\site-packages (0.42.1)
    


```python
import jieba  # 在命令行里面安装分词软件包jieba # pip install jieba
```


```python
seg_list = jieba.cut("南京大学生都爱南京市长江大桥")
```


```python
print( '    '.join(seg_list))
```

    南京    大学生    都    爱    南京市    长江大桥
    


```python
seg_list = jieba.cut("南京大学生都爱南京市长江大桥")
```


```python
print('*'.join(seg_list))
```

    南京*大学生*都*爱*南京市*长江大桥
    

## 2 加入用户词典


```python
seg_list1 = jieba.cut("吴志祥是南京工业大学青年教师，他对那种二次元小魔仙是无感的，这怎么行？")
```


```python
print('#'.join(seg_list1))
```

    吴志祥#是#南京#工业#大学#青年教师#，#他#对#那种#二次元小魔仙#是#无感#的#，#这#怎么#行#？
    

载入词典


```python
jieba.load_userdict('dict.txt')
```


```python
seg_list = jieba.cut("吴志祥是南京工业最好大学青年教师，经济与管理学院的，他对那种二次元小魔仙是无感的，这怎么行？python看上去还有点人性")
```


```python
print('%'.join(seg_list))
```

    吴志祥%是%南京工业最好大学%青年教师%，%经济%与%管理%学院%的%，%他%对%那种%二次元小魔仙%是%无感%的%，%这%怎么%行%？%python%看上去%还%有点人性
    

## 3 载入停用词表


```python
seg_list = jieba.cut("没有使用停用词表的分词结果，就会有很多没有用的词啊，虚词、感叹词什么的")
```


```python
print('*'.join((seg_list)))
```

    没有*使用*停用*词表*的*分词*结果*，*就*会*有*很多*没有*用*的*词*啊*，*虚词*、*感叹词*什么*的
    

载入停用词表


```python
stopwords = [line.strip() for line in open('stop_words.txt', 'r', encoding='utf-8').readlines()]  
```


```python
seg_list = jieba.cut("使用了停用词表之后啊，效果就好看很多了，什么啊、了、是之类的词就不见了")
```


```python
final = ''
```


```python
for seg in seg_list:
    if seg not in stopwords:
        final += seg+'*'
```


```python
print (final)   # 做实体抽取的时候，停用词表很管用
```

    使用*词表*之后*效果*就*好看*很多*什么*之类*词*就*不见*
    

## 4 jieba分词与SnowNLP分词进行比较


```python
from snownlp import SnowNLP
```


```python
s = SnowNLP(u'质量不大好')
```


```python
print(",".join(s.words))
```

    质量,不大,好
    


```python
ss = jieba.cut('质量不大好')
```


```python
print(",".join(ss))
```

    质量,不大好
    


```python
s1 = SnowNLP(u"吴志祥是南京工业大学青年教师，他对那种二次元小魔仙是无感的，这怎么行？")
```


```python
print(",".join(s1.words))  # 因为snownlp擅长处理英文
```

    吴,志祥,是,南京,工业,大学,青年,教师,，,他,对,那种,二,次,元,小,魔仙,是,无,感,的,，,这,怎么,行,？
    

### 结论：中文分词用jieba

## 5课后作业

+ 你可以使用以下两个片段，完成1-3的操作（我已经运行过一遍，你需要把我删掉的部分重新填上，获得同样的结果，试试看？）
+ 1.“曾经有一份真诚的爱情摆在我的面前，我没有珍惜，等到失去的时候才追悔莫及，人世间最痛苦的事情莫过于此。如果上天能够给我一个重新来过的机会，我会对那个女孩子说三个字：‘我爱你’。如果非要给这份爱加上一个期限，我希望是，一万年”
+ 2.“LSTM（Long Short-Term Memory）是长短期记忆网络，是一种时间递归神经网络，适合于处理和预测时间序列中间隔和延迟相对较长的重要事件。
+ 3.“黄旭华，1926年3月12日出生于广东省汕尾市，原籍广东省揭阳市。1949年毕业于上海交通大学。历任北京海军核潜艇研究室副总工程师、中船重工集团公司核潜艇总体研究设计所研究员、名誉所长。1994年当选为中国工程院院士。”


### 1.基本分词


```python
import jieba
```


```python
seg_list1 = jieba.cut("黄旭华，1926年3月12日出生于广东省汕尾市，原籍广东省揭阳市。1949年毕业于上海交通大学。历任北京海军核潜艇研究室副总工程师、中船重工集团公司核潜艇总体研究设计所研究员、名誉所长。1994年当选为中国工程院院士。")
```


```python
print('$'.join(seg_list1))
```

    黄旭华$，$1926$年$3$月$12$日出$生于$广东省$汕尾市$，$原籍$广东省$揭阳市$。$1949$年$毕业$于$上海交通大学$。$历任$北京$海军$核潜艇$研究室$副$总工程师$、$中船重工集团公司$核潜艇$总体$研究$设计所$研究员$、$名誉$所长$。$1994$年$当选$为$中国工程院院士$。
    


```python
seg_list2 = jieba.cut("LSTM（Long Short-Term Memory）是长短期记忆网络，是一种时间递归神经网络，适合于处理和预测时间序列中间隔和延迟相对较长的重要事件。")
```


```python
print('@'.join(seg_list2))
```

    LSTM@（@Long@ @Short@-@Term@ @Memory@）@是@长短期记忆网络@，@是@一种@时间递归神经网络@，@适合@于@处理@和@预测@时间@序列@中@间隔@和@延迟@相对@较长@的@重要@事件@。
    

### 2.加入词典，是针对第二个片段的，希望是能够完整把“长短期记忆网络”这个术语整体分割出来


```python
jieba.load_userdict('dict.txt')
```


```python
seg_list_dict = jieba.cut("LSTM（Long Short-Term Memory）是长短期记忆网络，是一种时间递归神经网络，适合于处理和预测时间序列中间隔和延迟相对较长的重要事件。")
```


```python
print('/'.join(seg_list_dict))
```

    LSTM/（/Long/ /Short/-/Term/ /Memory/）/是/长短期记忆网络/，/是/一种/时间递归神经网络/，/适合/于/处理/和/预测/时间/序列/中/间隔/和/延迟/相对/较长/的/重要/事件/。
    

### 3.加入停用词，针对第一个片段，希望的结果是，结果中不会出现“的、是”等虚词


```python
stopwords = [line.strip() for line in open('stop_words.txt', 'r', encoding='utf-8').readlines()]  
```


```python
seg_list_stopw = jieba.cut("曾经有一份真诚的爱情摆在我的面前，我没有珍惜，等到失去的时候才追悔莫及，人世间最痛苦的事情莫过于此。如果上天能够给我一个重新来过的机会，我会对那个女孩子说三个字：‘我爱你’。如果非要给这份爱加上一个期限，我希望是，一万年")
```


```python
final = ''
```


```python
#这是一行注释，进行分词结果的过滤
for seg in seg_list_stopw:
    if seg not in stopwords:
        final += seg + '/' #叠加，累加
```


```python
print(final)
```

    曾经/有/一份/真诚/爱情/摆在/我/面前/我/没有/珍惜/等到/失去/时候/才/追悔莫及/人世间/最/痛苦/事情/莫过于此/如果/上天/能够/给/我/一个/重新/来/过/机会/我会/对/那个/女孩子/说/三个/字/：/‘/我爱你/’/如果/非要/给/这份/爱/加上/一个/期限/我/希望/一万年/
    

### 4.可以开启你的小组项目的第一个小小任务啦！就是对一小段有关“功勋科学家”的文本进行分词处理。请对以上第三段文本进行分词，并评估分词效果（哪些地方分的好，哪些分的不好）。


```python
#jieba对于“黄旭华”文段拆分效果很好
```


```python
#“/适合/于/处理/和/预测/时间/序列/”，“适合于”应当为一个词，“时间序列”不必拆分
```


```python
#“如果/上天/能够/给/我/一个/重新/来/过/机会/”此处“来”和“过”应当成一个词，即“来过”
```


```python
#
```

好，本次练习结束了，恭喜你！

作业的意义：
+ 成功的进入了文本挖掘（Text Mining）的领域
+ 成功的实现了自己编程0的突破


```python

```


```python

```


```python

```
