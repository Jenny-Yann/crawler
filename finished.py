from urllib.parse import urlencode
import requests
from pyquery import PyQuery as pq
import time
import xlwt
import pandas as pd

base_url = 'https://m.weibo.cn/api/container/getIndex?' 

headers = {           #直接复制request headers？
    'Accept': 'application/json, text/plain, */*',
    'MWeibo-Pwa': '1',
    'Referer': 'https://m.weibo.cn/search?containerid=100103type%3D1%26q%3D%E9%A6%99%E6%B8%AF%E4%BA%8B%E4%BB%B6',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    'X-XSRF-TOKEN': '87d5c4',
}

def get_page(page):       #翻页问题？此处searchall？
    params = {
                       #根据网页填写
       'containerid': '100103type=1&q=香港事件',
       'page_type': 'searchall',
       'page': page,
    }

    url = base_url+urlencode(params)
    try:
        response = requests.get(url,headers=headers)
        if response.status_code == 200:
            #page暂时不明
            return response.json()
    except requests.ConnectionError as e:
        print('ERROR:',e.args)

def parse_page(json):
    print('aaa')
    weibos=[]
    if json:
        items = json.get('data').get('cards')
        #print('aaa')
        for i in items:
            if 'mblog' in i:
                item = i['mblog']
                #print('输出',item)
                if item == None:
                    continue
                weibo = {}
                weibo['id'] = item.get('id')
                weibo['text'] = pq(item.get('text')).text()
                weibo['name'] = item.get('user').get('screen_name')
                if item.get('longText') != None :#要注意微博分长文本与文本，较长的文本在文本中会显示不全，故我们要判断并抓取。
                    weibo['longText'] = item.get('longText').get('longTextContent')
                else:weibo['longText'] =None
                #print(weibo['name'])
                #print(weibo['longText'])
                weibo['attitudes'] = item.get('attitudes_count')
                weibo['comments'] = item.get('comments_count')
                weibo['reposts'] = item.get('reposts_count')
                weibo['time'] = item.get('created_at')   

                weibos.append(weibo)

                   
            

    return weibos

def export_excel(export):
    pf = pd.DataFrame(list(export))
    order = ['id','text','name','longText','attitudes','comments','reposts','time']
    pf = pf[order]
    columns_map = {
        'id':'账号',
        'text':'文本',
        'name':'名称',
        'longText':'长文',
        'attitudes':'点赞数',
        'comments':'评论数',
        'reposts':'转发量',
        'time':'时间'
    }
    pf.rename(columns = columns_map,inplace = True)
   #指定生成的Excel表格名称
    file_path = pd.ExcelWriter('E:/weibos.xlsx')   #根据需要修改表格文件保存路径
   #替换空单元格
    pf.fillna(' ',inplace = True)
   #输出
    pf.to_excel(file_path,encoding = 'utf-8',index = False)
   #保存表格
    file_path.save()

if __name__ == '__main__':
    results=[]
    for page in range(2,10):      #在此处根据需要修改爬取的页面数量：2~n页
        time.sleep(1)    #防止封号
        json = get_page(page) #获取到json数据
        results = parse_page(json)+results

    export_excel(results)
  
  
    
    
    
    

