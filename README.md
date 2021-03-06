# 微信公众号文章爬取
## 爬取背景
现在是信息泛滥时代，如何从大量数据中提取有价值的信息至关重要。  
故通过爬虫获取自己感兴趣的公众号文章，节约时间成本。

## 遇到的问题
1. 请求容易被网站屏蔽。无论使用哪种方法，请求的时间间隔不要过短（建议10s以上）
2. 方法2的操作会比较复杂，所以一开始的思路是打算通过扫码的方式，即通过方法1的平台接口获取到方法2所要求的的校验信息（包括uin,token,pass_ticket等等），这样就会简单很多。无奈研究了一天未果，故放弃。最终使用了抓包的方式，手动填充校验信息。

## 爬取方法
方法1：使用公众号平台自带的接口
- 优点：直接扫码就能进行爬取
- 缺点：
  1. 容易被屏蔽。每10秒发一次请求，大概到27次就会被限制  
  2. 每次请求只能拿到5条记录，效率低

方法2：使用Fiddler抓取接口信息
- 优点：请求不容易被限制，每次请求能拿到10条记录，效率高
- 缺点：操作复杂，每次爬取之前都需要通过抓包获取token和cookies等信息

## 爬取步骤
针对方法2，只需通过Fiddler抓包，把下面截图的信息复制粘贴到代码的uri(``注意action=getmsg``)和cookies位置即可。  
![image](https://github.com/huangym1/Wx_Article_Spider/blob/master/images/微信截图_20191206232247.png)
![image](https://github.com/huangym1/Wx_Article_Spider/blob/master/images/微信截图_20191206232337.png)

## 爬取结果
- 开始爬取~~~  
![image](https://github.com/huangym1/Wx_Article_Spider/blob/master/images/微信截图_20191204131456.png)  
- 数据入库~~~  
![image](https://github.com/huangym1/Wx_Article_Spider/blob/master/images/微信截图_20191206232707.png)  
- 经过测试，爬取了3个多小时，暂未被封。

## 文章可视化
- 选择公众号，点击确定即可查看对应公众号所有文章列表  
![image](https://github.com/huangym1/Wx_Article_Spider/blob/master/images/微信截图_20191212213314.png)
- 点击查看对应文章内容  
![image](https://github.com/huangym1/Wx_Article_Spider/blob/master/images/微信截图_20191212213359.png)

## TODO
- 文章增量追加：能根据上次爬取文章的更新时间，实现当次新文章的自动入库。
- ~~可视化展示：通过flask框架实现个人收集整理的公众号文章阅读可视化。~~
