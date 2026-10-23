# 词云

这里涉及到一个很重要的知识点，中文分词

1 首先安装jieba分词包

+ pip install jieba

2 然后做一个yes-minister的中文txt（yes_minister_cn），放在文件夹中

3 正式编程之前，还需要下载一个中文字体包，[地址是这个](https://s3-us-west-2.amazonaws.com/notion-static/b869cb0c7f4e4c909a069eaebbd2b7ad/simsun.ttf)。点击链接就直接下载了，文件名就是simsun.ttf


```python
f_cn = open('yes_minister_cn.txt',encoding = 'GB18030') # mac电脑的编码是GB18030，windows可以改成utf-8
```


```python
text_cn = f_cn.read()
```


```python
f_cn.close()
```


```python
text_cn[:50]
```




    '本剧叙述在野党影子内阁成员Jim Hacker在帮助本党大选获胜之后担任行政事务部（DAA）部长的职'



下面这一段代码很重要了，就是分词


```python
import jieba
```


```python
text_cn_word = "/".join(jieba.cut(text_cn))
```

    Building prefix dict from the default dictionary ...
    Loading model from cache C:\Users\denve\AppData\Local\Temp\jieba.cache
    Loading model cost 0.362 seconds.
    Prefix dict has been built successfully.
    


```python
print(text_cn_word[:100])
```

    本剧/叙述/在野党/影子内阁/成员/Jim/ /Hacker/在/帮助/本/党/大选/获胜/之后/担任/行政/事务部/（/DAA/）/部长/的/职务/，/从此/开始/与/以部/秘书/Sir/ /Hum
    


```python
!pip install wordcloud
```

    Requirement already satisfied: wordcloud in C:\Users\denve\anaconda3\Lib\site-packages (1.9.6)
    Requirement already satisfied: numpy>=1.19.3 in C:\Users\denve\anaconda3\Lib\site-packages (from wordcloud) (2.4.6)
    Requirement already satisfied: pillow in C:\Users\denve\anaconda3\Lib\site-packages (from wordcloud) (12.3.0)
    Requirement already satisfied: matplotlib in C:\Users\denve\anaconda3\Lib\site-packages (from wordcloud) (3.11.0)
    Requirement already satisfied: contourpy>=1.0.1 in C:\Users\denve\anaconda3\Lib\site-packages (from matplotlib->wordcloud) (1.3.3)
    Requirement already satisfied: cycler>=0.10 in C:\Users\denve\anaconda3\Lib\site-packages (from matplotlib->wordcloud) (0.12.1)
    Requirement already satisfied: fonttools>=4.22.0 in C:\Users\denve\anaconda3\Lib\site-packages (from matplotlib->wordcloud) (4.63.0)
    Requirement already satisfied: kiwisolver>=1.3.1 in C:\Users\denve\anaconda3\Lib\site-packages (from matplotlib->wordcloud) (1.4.9)
    Requirement already satisfied: packaging>=20.0 in C:\Users\denve\anaconda3\Lib\site-packages (from matplotlib->wordcloud) (26.0)
    Requirement already satisfied: pyparsing>=3 in C:\Users\denve\anaconda3\Lib\site-packages (from matplotlib->wordcloud) (3.2.5)
    Requirement already satisfied: python-dateutil>=2.7 in C:\Users\denve\anaconda3\Lib\site-packages (from matplotlib->wordcloud) (2.9.0.post0)
    Requirement already satisfied: six>=1.5 in C:\Users\denve\anaconda3\Lib\site-packages (from python-dateutil>=2.7->matplotlib->wordcloud) (1.17.0)
    

现在按照英文词云的套路text_cn进行分词，看看效果


```python
from wordcloud import WordCloud  # 关键代码1
```


```python
wordcloud = WordCloud().generate(text_cn_word) # 关键代码2
```


```python
%pylab inline
```

    %pylab is deprecated, use %matplotlib inline and import the required libraries.
    Populating the interactive namespace from numpy and matplotlib
    


```python
import matplotlib.pyplot as plt
```


```python
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
```




    (np.float64(-0.5), np.float64(399.5), np.float64(199.5), np.float64(-0.5))




    
![png](output_20_1.png)
    


为什么会这样呢？

问题在哪里呢？这就需要我们之前下载的中文字体上场了，因为wordcloud默认的字体是英文的，中文就只有框框了


```python
# 那就一起把以上的代码再重新输入一遍吧，再把字体加入
'''
from wordcloud import WordCloud
wordcloud_cn = WordCloud(font_path="simsun.ttf").generate(text_cn_word)
%pylab inline
import matplotlib.pyplot as plt
plt.imshow(wordcloud_cn, interpolation='bilinear')
plt.axis('off')
'''
# 那就一起把以上的代码再重新输入一遍吧，再把字体和屏蔽词加入
from wordcloud import WordCloud
import matplotlib.pyplot as plt
%pylab inline

# 1. 定义屏蔽词集合（填入需要过滤的字词）
my_stopwords = {'的', '了', '和', '在', '也', '与'}

# 2. 在 WordCloud 构造函数中加入 stopwords 参数
wordcloud_cn = WordCloud(
    font_path="simsun.ttf",
    stopwords=my_stopwords,
    background_color="white"
).generate(text_cn_word)

# 3. 绘图展示
plt.imshow(wordcloud_cn, interpolation='bilinear')
plt.axis('off')
```

    %pylab is deprecated, use %matplotlib inline and import the required libraries.
    Populating the interactive namespace from numpy and matplotlib
    




    (np.float64(-0.5), np.float64(399.5), np.float64(199.5), np.float64(-0.5))




    
![png](output_23_2.png)
    


好了！是不是感觉自己很不错呢

接下来，你还能想到哪些比较实用的改进呢？

## 给词云加上特定的形状


```python
big_pic = imread('bg2.jpg')
```


```python
wordcloud_cn_x = WordCloud(mask=big_pic,width=500,height=300, background_color= 'white',scale=2.5, font_path="simsun.ttf").generate(text_cn_word)
plt.imshow(wordcloud_cn_x)
plt.axis('off')
```




    (np.float64(-0.5), np.float64(2559.5), np.float64(2414.5), np.float64(-0.5))




    
![png](output_28_1.png)
    



```python
wordcloud_cn_x.to_file('yes_minister_x.jpg')
```




    <wordcloud.wordcloud.WordCloud at 0x289aa560c20>



## 注意：以下有wordcloud所有参数的设置，供大家作业的时候参考，修改词云效果。


```python
# class wordcloud.WordCloud(font_path=None, width=400, height=200, margin=2, ranks_only=None, prefer_horizontal=0.9,mask=None, scale=1, color_func=None, max_words=200, min_font_size=4, stopwords=None, random_state=None,background_color='black', max_font_size=None, font_step=1, mode='RGB', relative_scaling=0.5, regexp=None, collocations=True,colormap=None, normalize_plurals=True)
```

基于以上设置作业

font_path : string //字体路径，需要展现什么字体就把该字体路径+后缀名写上，如：font_path = '黑体.ttf'

width : int (default=400) //输出的画布宽度，默认为400像素

height : int (default=200) //输出的画布高度，默认为200像素

prefer_horizontal : float (default=0.90) //词语水平方向排版出现的频率，默认 0.9 （所以词语垂直方向排版出现频率为 0.1 ）

mask : nd-array or None (default=None) //如果参数为空，则使用二维遮罩绘制词云。如果 mask 非空，设置的宽高值将被忽略，遮罩形状被 mask 取代。除全白（#FFFFFF）的部分将不会绘制，其余部分会用于绘制词云。如：bg_pic = imread('读取一张图片.png')，背景图片的画布一定要设置为白色（#FFFFFF），然后显示的形状为不是白色的其他颜色。可以用ps工具将自己要显示的形状复制到一个纯白色的画布上再保存，就ok了。

scale : float (default=1) //按照比例进行放大画布，如设置为1.5，则长和宽都是原来画布的1.5倍。

min_font_size : int (default=4) //显示的最小的字体大小

font_step : int (default=1) //字体步长，如果步长大于1，会加快运算但是可能导致结果出现较大的误差。

max_words : number (default=200) //要显示的词的最大个数

stopwords : set of strings or None //设置需要屏蔽的词，如果为空，则使用内置的STOPWORDS

background_color : color value (default=”black”) //背景颜色，如background_color='white',背景颜色为白色。

max_font_size : int or None (default=None) //显示的最大的字体大小

mode : string (default=”RGB”) //当参数为“RGBA”并且background_color不为空时，背景为透明。

relative_scaling : float (default=.5) //词频和字体大小的关联性

color_func : callable, default=None //生成新颜色的函数，如果为空，则使用 self.color_func

regexp : string or None (optional) //使用正则表达式分隔输入的文本

collocations : bool, default=True //是否包括两个词的搭配

colormap : string or matplotlib colormap, default=”viridis” //给每个单词随机分配颜色，若指定color_func，则忽略该方法。



fit_words(frequencies)  //根据词频生成词云
generate(text)  //根据文本生成词云
generate_from_frequencies(frequencies[, ...])   //根据词频生成词云
generate_from_text(text)    //根据文本生成词云
process_text(text)  //将长文本分词并去除屏蔽词（此处指英语，中文分词还是需要自己用别的库先行实现，使用上面的 fit_words(frequencies) ）
recolor([random_state, color_func, colormap])   //对现有输出重新着色。重新上色会比重新生成整个词云快很多。
to_array()  //转化为 numpy array
to_file(filename)   //输出到文件


```python
# 在分词阶段，我新加了词语的过滤
```
