from urllib import request
from PIL import Image
from http import cookiejar
from urllib import parse
import datetime
import json
from bs4 import BeautifulSoup
import time


def getCaptcha(headers):
    captcha_url='http://seat.lib.whu.edu.cn/simpleCaptcha/captcha'
    req=request.Request(captcha_url,headers=headers)
    res=request.urlopen(req)
    with open('captcha.png','wb') as fp:
        fp.write(res.read())
    image=Image.open('captcha.png')
    if image:
        print('验证码已经获取')
    image.show()

def function():
    #个人和预定的信息
    book_url='http://seat.lib.whu.edu.cn/selfRes'
    username='2015302580292'
    password='081152'
    date=datetime.date.today()
    if datetime.datetime.today().hour*60+datetime.datetime.today().minute>=1340:
        date=date+datetime.timedelta(days=1)
    start_time='540'
    end_time='1320'
    # 获取用于登录的cookie
    index_url = 'http://seat.lib.whu.edu.cn/'
    cookie = cookiejar.CookieJar()
    handler = request.HTTPCookieProcessor(cookie)
    opener = request.build_opener(handler)
    index_req = request.Request(index_url)
    index_req.add_header('User-Agent',
                         'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36')
    index_res = opener.open(index_req)
    index_cookie = ''
    for item in cookie:
        index_cookie += item.name + '=' + item.value + ';'
    print(index_cookie)
    # 用获得cookie登录使得此cookie获得注册
    headers={
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36',
        'Cookie':index_cookie
    }
    getCaptcha(headers)    #获取登录的验证码
    captcha=input('请输入登录的验证码')
    login_url='http://seat.lib.whu.edu.cn/auth/signIn'
    login_data={
        'username':username,
        'password':password,
        'captcha':captcha
    }
    login_req=request.Request(login_url,parse.urlencode(login_data).encode(),headers)
    login_res=request.urlopen(login_req)
    #查询所需时间的座位,优先搜索靠窗的
    book=False #假设预定失败
    find=False
    rooms=[6,7,8,9,10,11,12]
    room_dict={6:'二楼西',7:'二楼东',8:'三楼西',9:'四楼西',10:'三楼东',11:'四楼东',12:'三楼自主学习区'}
    for room in rooms:
        print('优先为您搜索靠窗的座位')
        print('正在为您搜索 '+room_dict[room]+' 房间的座位')
        search_url = 'http://seat.lib.whu.edu.cn/freeBook/ajaxSearch'
        search_data = {
            'onDate': date,
            'building': '1',
            'room':room,
            'hour':'null',
            'startMin':start_time,
            'endMin':end_time,
            'power':'null',
            'window':'1',
        }
        search_req=request.Request(search_url,parse.urlencode(search_data).encode(),headers)
        search_res=request.urlopen(search_req)
        search_json=json.loads(search_res.read().decode('utf-8'))
        if search_json['seatNum']!=0:
            find=True
            seat_html=search_json['seatStr']
            seat_soup=BeautifulSoup(seat_html,'html.parser')
            seat_id=seat_soup.li.attrs['id'][-4:]
            seat_num=seat_soup.dt.text
            print('已经帮您找到此房间的 '+seat_num+' 号座位，下面开始尝试预定')
            try:
                getCaptcha(headers)
                captcha=input('请输入预定验证码')
                book_data={
                    'date':date,
                    'seat':seat_id,
                    'start':start_time,
                    'end':end_time,
                    'captcha':captcha
                }
                book_req=request.Request(book_url,parse.urlencode(book_data).encode(),headers)
                book_res=request.urlopen(book_req)
                book_soup=BeautifulSoup(book_res.read().decode('utf-8'),'html.parser')
                results=book_soup.find_all('dd')
                for result in results:
                    if '成功' in result.text:
                        book=True
                    print(result.text)
                break
            except:
                print('发生了未知错误，预定失败,可以重新用次程序尝试一下')
                break
        else:
            print('当前房间没有符合您要求的座位，开始搜索下一间')
    if find==False:
        print('下面开始搜索不靠窗的座位')
        for room in rooms:
            print('正在为您搜索 ' + room_dict[room] + ' 房间的座位')
            search_url = 'http://seat.lib.whu.edu.cn/freeBook/ajaxSearch'
            search_data = {
                'onDate': date,
                'building': '1',
                'room': room,
                'hour': 'null',
                'startMin': start_time,
                'endMin': end_time,
                'power': 'null',
                'window': '0',
            }
            search_req = request.Request(search_url, parse.urlencode(search_data).encode(), headers)
            search_res = request.urlopen(search_req)
            search_json = json.loads(search_res.read().decode('utf-8'))
            if search_json['seatNum'] != 0:
                find =True
                seat_html = search_json['seatStr']
                seat_soup = BeautifulSoup(seat_html, 'html.parser')
                seat_id = seat_soup.li.attrs['id'][-4:]
                seat_num = seat_soup.dt.text
                print('已经帮您找到此房间的 ' + seat_num + ' 号座位，下面开始尝试预定')
                try:
                    getCaptcha(headers)
                    captcha = input('请输入预定验证码')
                    book_data = {
                        'date': date,
                        'seat': seat_id,
                        'start': start_time,
                        'end': end_time,
                        'captcha': captcha
                    }
                    book_req = request.Request(book_url, parse.urlencode(book_data).encode(), headers)
                    book_res = request.urlopen(book_req)
                    book_soup = BeautifulSoup(book_res.read().decode('utf-8'), 'html.parser')
                    results = book_soup.find_all('dd')
                    for result in results:
                        if '成功' in result.text:
                            book = True
                        print(result.text)
                    break
                except:
                    print('发生了未知错误，预定失败,可以重新尝试一下')
                    break
            else:
                print('当前房间没有符合您要求的座位，开始搜索下一间')
    if find==False:
        print('对不起，未找到合适的房间座位')

if __name__=='__main__':
    a=input('1、现在运行，2、定时运行（22：30）')
    if a=='1':
        function()
    if a=='2':
        schedual_time = datetime.datetime(2018, 3, 10, 22, 30, 0)
        loop = 0
        while True:
            if schedual_time <= datetime.datetime.now() < schedual_time + datetime.timedelta(seconds=1):
                loop = 1
                time.sleep(1)
                if loop == 1:
                    function()
                    loop == 0

