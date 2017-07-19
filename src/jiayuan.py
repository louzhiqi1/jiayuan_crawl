#!/usr/bin/env python
# encoding: utf-8

from urllib import quote_plus, urlencode
from gzip import GzipFile
from urllib2 import urlopen, Request, HTTPError, URLError, build_opener, HTTPCookieProcessor, install_opener
from bs4 import BeautifulSoup
from json import loads, dumps
from StringIO import StringIO
from cookielib import CookieJar, MozillaCookieJar

import os,time,sys,re,random
global conditions, sex, page, maxid_txt

def read_max_id():
    global maxid_txt
    if os.path.exists(maxid_txt):
        fp = open(maxid_txt, "r")

        maxid = int(fp.read())

        fp.close()

        return maxid
    else:
        return 165850435

def write_ids(new_ids = [], maxid = 165850435):
    #新id往CRM插入
    fp = open("new_ids.txt", "w")

    if len(new_ids) > 0:
        content = ",".join([str(id) for id in new_ids])
    else:
        content = ""

    fp.write(content)

    fp.close()

    #所有的ID记录
    global maxid_txt
    fp = open(maxid_txt, "w")

    fp.write(str(maxid))

    fp.close()

# 处理stc筛选条件
def gen_stc():
    global conditions
    stc = []
    for k, v in conditions.items():
        if k == "4" or k == "5":
            v +=".1"
        stc.append("%s:%s" % (k, v))

    # 下面代表啥我也不知道
    # stc.append("27:1")

    return ",".join(stc)

def gen_data(p):
    params = {}
    params = gen_default_data(p)

    # params['stc'] = quote_plus(gen_stc()).replace("%", "\"%\"")
    params['stc'] = gen_stc()

    post_data = ""
    for k, v in params.items():
        post_data += "&" + k + "=" + v

    return post_data[1:]

def gen_default_data(p):
    global sex, sn
    # sn 排序方式:default(综合排名),charm(魅力),last_login(登录时间)
    # ft 仅显示未联系过的会员
    # p 第几页
    # pt,sv不知道是啥
    params = {}
    params['key'] = ''
    params['sex'] = sex #性别
    params['sn'] = sn
    params['sv'] = '1'
    params['p'] = p
    params['pt'] = '31'
    params['ft'] = 'off'
    params['f'] = 'select'
    params['pri_uid'] = '0'
    params['mt'] = 'u'
    params['listStyle'] = 'bigPhoto'

    return params

def gen_headers(p):
    header = {}
    header['Origin'] = 'http://search.jiayuan.com'
    header['Accept-Encoding'] = 'gzip, deflate'
    header['Accept-Language'] = 'zh-CN,zh;q=0.8'
    header['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104 Safari/537.36 Core/1.53.3103.400 QQBrowser/9.6.11372.400'
    header['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
    header['Accept'] = '*/*'

    default_params = gen_default_data(p)
    default_query = ""
    for k, v in default_params.items():
        default_query += "&" + k + "=" + v

    header['Referer'] = 'http://search.jiayuan.com/v2/index.php?stc='+gen_stc()+default_query
    header['X-Requested-With'] = 'XMLHttpRequest'
    header['Proxy-Connection'] = 'keep-alive'
    header['Host'] = 'search.jiayuan.com'
    header['Progma'] = 'no-cache'

    return header

def work():
    global page
    # 获取到最新的session，免得后面需要session验证
    open_index()

    maxid = read_max_id()

    ids = []
    new_ids = []
    i = 1
    while i <= page:
        ids += get_ids(str(i))
        i+=1

    ids = sorted(ids, reverse = True)

    print ids

    for Uid in ids:
        if Uid > maxid:
            new_ids.append(Uid)

    if len(new_ids) > 0:
        maxid = max(maxid, max(new_ids))

    print new_ids

    write_ids(new_ids, maxid)

def open_index():
    index_php = "http://search.jiayuan.com/v2/index.php"

    cookie = MozillaCookieJar("cookies.txt")

    opener = build_opener(HTTPCookieProcessor(cookie))

    install_opener(opener)

    urlopen(index_php)

    cookie.save(ignore_discard = True, ignore_expires = True)


def get_ids(p):
    cookie = MozillaCookieJar()

    cookie.load('cookies.txt', ignore_discard = True, ignore_expires= True)

    opener = build_opener(HTTPCookieProcessor(cookie))

    send_data = gen_data(p)
    send_header = gen_headers(p)

    print "data:", send_data
    print "header:", send_header

    req = Request('http://search.jiayuan.com/v2/search_v2.php', data = send_data, headers = send_header)
    try:
        response = opener.open(req)
    except HTTPError, e:
        print "server couldn't handle request"
        print "Error code:",e.code
        time.sleep(2)
        sys.exit(-1)
    except URLError, e:
        print "failed to reach the server"
        print "reasen:",e.reason
        sys.exit(-2)

    content = StringIO(response.read())
    response_data = GzipFile(fileobj = content).read()
    json_begin = response_data.find("{")
    json_end = response_data.rfind("}")
    content = response_data[json_begin:json_end]

    users = loads(response_data)['userInfo']

    ids = []

    for user_info in users:
        ids.append(user_info['realUid'])

    return ids

# 判断当前是
def get_choice():
    return random.choice([2,1,2])

def load_config(choice):
    global conditions, sex, page, sn, maxid_txt
    conditions = {}
    if choice == 2:
        config, maxid_txt = "config_f.ini", "maxid_f.txt"
    else:
        config, maxid_txt = "config_m.ini", "maxid_m.txt"

    fp = open(config, "r")

    content = fp.read()
    p = re.compile("(\w+)=([\w\.]*).*")

    match_obj = re.findall(p, content)

    for (key, val) in match_obj:
        if key == "sex":
            sex = val
        elif key == "page":
            page = int(val)
        elif key == "sn":
            sn = val
        else:
            conditions[key] = val

if __name__ == "__main__":
    if len(sys.argv) > 0:
        choice = int(sys.argv[1])
    else:
        choice = 1
    start_time =  time.time()
    load_config(choice)

    

    work()

    print time.time() - start_time