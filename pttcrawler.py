#coding=utf-8
import sys
import requests
import io
import json
from bs4 import BeautifulSoup
from datetime import datetime

# diable https waring and then get session
requests.packages.urllib3.disable_warnings()
rs = requests.session()

fileName=""

def PageCount(PttName):
    res = rs.get('https://www.ptt.cc/bbs/'+PttName+'/index.html', verify=False)
    soup = BeautifulSoup(res.text, 'html.parser')
    ALLpageURL = soup.select('.btn.wide')[1]['href'] # get '上一頁' URL
    ALLpage = int(getPageNumber(ALLpageURL))+1
    return ALLpage

#return page number. ex: 3366
def getPageNumber(content):
    startIndex = content.find('index')
    endIndex = content.find('.html')
    pageNumber = content[startIndex+5:endIndex]
    return pageNumber
   
def crawler(PttName, ParsingPage):
    ALLpage=PageCount(PttName)
    articleNum = 0

    #start to scratch
    for number in range(ALLpage, ALLpage-int(ParsingPage), -1):
        res = rs.get('https://www.ptt.cc/bbs/'+PttName+'/index'+str(number)+'.html', verify=False)
        soup = BeautifulSoup(res.text, 'html.parser')
 #       print(soup.select('div.title'))
        for tag in soup.select('div.title'):
            try:
                atag = tag.find('a')  # 抓取每一頁的<a>
     #           print(atag)
                if(atag):
                    URL = atag['href']
                    link = 'https://www.ptt.cc'+URL
                    articleNum += 1
                    parseGos(link, articleNum)
            except:
                print('error: at Page ' + URL)

def parseGos(link, articleNum):
#    res = rs.get('https://www.ptt.cc/bbs/Tech_Job/M.1467951744.A.792.html', verify=False)
    res = rs.get(link, verify=False)
    soup = BeautifulSoup(res.text, 'html.parser')

    #get article author
    author = soup.select('.article-meta-value')[0].text
    codecAuthor = author.encode(sys.stdin.encoding, "replace").decode(sys.stdin.encoding)
    
    #get article title
    title = soup.select('.article-meta-value')[2].text
    codecTitle = title.encode(sys.stdin.encoding, "replace").decode(sys.stdin.encoding)

    #get article date
    date = soup.select('.article-meta-value')[3].text
    codecDate = date.encode(sys.stdin.encoding, "replace").decode(sys.stdin.encoding)

    #get content
    content = soup.find(id="main-content").text
    target_content = u'※ 發信站: 批踢踢實業坊(ptt.cc),'
    content = content.split(target_content)
    content = content[0].split(date)
    main_content = content[1].replace('\n', '  ').replace('\t', '  ')
    codecMainContent = main_content.encode(sys.stdin.encoding, "replace").decode(sys.stdin.encoding)

    #message
    allNum, like, hate, comment, message = 0,0,0,0,{}
    for tag in soup.select('div.push'):
        allNum += 1
        push_tag = tag.find('span', {'class': 'push-tag'}).text
        codecPush_tag = push_tag.encode(sys.stdin.encoding, "replace").decode(sys.stdin.encoding)
        push_userid = tag.find('span', {'class': 'push-userid'}).text
        codecPush_userid = push_userid.encode(sys.stdin.encoding, "replace").decode(sys.stdin.encoding)
        push_content = tag.find('span', {'class': 'push-content'}).text
        codecPush_content = push_content.encode(sys.stdin.encoding, "replace").decode(sys.stdin.encoding)
        codecPush_content = codecPush_content[2:]  # remove space
        push_ipdatetime = tag.find('span', {'class': 'push-ipdatetime'}).text
        codecPush_ipdatetime = push_ipdatetime.encode(sys.stdin.encoding, "replace").decode(sys.stdin.encoding)
        codecPush_ipdatetime = removeChars(codecPush_ipdatetime, '\n')

        
        message[allNum] = {"狀態": codecPush_tag, "留言者": codecPush_userid,
                        "留言內容": codecPush_content, "留言時間": codecPush_ipdatetime}

        if codecPush_tag == u'推 ':
            like += 1
        elif codecPush_tag == u'噓 ':
            hate += 1
        else:
            comment += 1

    messageNum = {"like": like, "hate": hate, "comment": comment, "allNum": allNum}

    d = {"a_num": articleNum, "b_author": codecAuthor, "c_title": codecTitle,
         "d_date": codecDate, "e_like": like, "f_hate": hate, "g_comment": comment,
         "h_content": codecMainContent, "i_message": message}
    json_data = json.dumps(d, ensure_ascii=False, indent=4, sort_keys=True)+'\n'
    storeArticleData(json_data)

def storeArticleData(data):
    with open(fileName, 'a') as f:
        f.write(data)

def removeChars(content, deleteChars):
    for c in deleteChars:
        content = content.replace(c, '')
    return content.rstrip();


#program starts from here
if __name__ == "__main__":
    PttName = str(sys.argv[1])  # [BoardName]
    ParsingPage = int(sys.argv[2]) # [PageNums]
    fileName = 'data-' + PttName + '-' + datetime.now().strftime('%Y-%m-%d-%H-%M-%S')+'.json'

    storeArticleData("### Below is the data format ###\n")
    storeArticleData("a_num: 文章編號(第幾篇文章)\n")
    storeArticleData("b_author: 文章作者\n")
    storeArticleData("c_title: 文章標題\n")
    storeArticleData("d_date: 發文日期\n")
    storeArticleData("e_like: 文章推文個數\n")
    storeArticleData("f_hate: 文章噓文個數\n")
    storeArticleData("g_comment: 文章留言個數(不是推文和噓文)\n")
    storeArticleData("h_content: 文章內容\n")
    storeArticleData("i_message: 留言內容\n")
    storeArticleData("################################\n\n")

    print('############## start      crawling ' + PttName+  '   ##############')
    crawler(PttName, ParsingPage)
