from django.shortcuts import render,redirect
from django.core.urlresolvers import reverse
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer,SignatureExpired,BadSignature
from django.core.mail import send_mail
from django.http import *
from .models import *
from utils.user_util import my_md5,my_login
from PIL import Image, ImageDraw, ImageFont
from celery_tasks.tasks import task_send_mail
from django.conf import settings
from io import BytesIO
import hashlib
import random


def register(request):
    context = {'title': '用户注册'}
    return render(request,'df_user/register.html',context)

def register_handle(request):
    uname=request.POST.get('user_name')
    upwd=request.POST.get('pwd')
    ucpwd=request.POST.get('cpwd')
    uemail=request.POST.get('email')

    if not 8 <= len(upwd) <= 20:
        context = {'title': '用户注册', 'error_pwd': '密码长度错误'}
        return render(request, 'df_user/register.html', context)

    if (upwd != ucpwd):
        context = {'title': '用户注册', 'error_cpwd': '密码不一致'}
        return render(request, 'df_user/register.html', context)

    try:
        user = UserInfo.objects.get(uemail=uemail)

    except UserInfo.DoesNotExist:
        user=None
    if user:
        return render(request, 'df_user/register.html', {'error_email': '邮箱重复'})
    #创建对象
    UserInfo.objects.create(uname=uname,upwd=my_md5(upwd),uemail=uemail)
    #注册成功转向登录页面
    return redirect(reverse('user:login'))


def register_exist(request):
    uname=request.GET.get('uname')
    print(uname)
    count=UserInfo.objects.filter(uname=uname).count()
    print(count)
    return JsonResponse({'count':count})



def login(request):
    # del request.session['username']
    remember_uname=request.COOKIES.get('remember_uname','')
    context={'title':'用户登录','remember_uname':remember_uname}
    return render(request,'df_user/login.html',context)

def login_handle(request):
    uname=request.POST.get('username')
    upwd=request.POST.get('pwd')
    remember=request.POST.get('remember')
    verifycode=request.POST.get('verifycode').strip().lower()
    user=UserInfo.objects.filter(uname=uname)

    if verifycode != request.session["validate_code"].lower():
        return render(request, 'df_user/login.html', {'error_verifycode':'验证码错误'})

    if len(user)!=0:
        if my_md5(upwd)==user[0].upwd:
          request.session['login_user_id']=user[0].id
          request.session['login_user_name'] = uname
          url_dest=request.COOKIES.get('url_dest')
          if url_dest:
              resp=HttpResponseRedirect(url_dest)
              resp.delete_cookie('url_dest')
          else:
              resp=redirect(reverse('user:index'))
          if remember=='1':
            resp.set_cookie('remember_uname',uname,3600*24*7)
          else:
            resp.set_cookie('remember_uname', uname, 3600*0)
          return resp

        else:
            context = {'title': '用户登录','error_pwd':'密码错误','uname':uname,'upwd':upwd}
            return render(request, 'df_user/login.html',context)
    else:
        context = {'title': '用户登录', 'error_name': '用户名错误','uname': uname, 'upwd': upwd}
        return render(request, 'df_user/login.html',context)


def validate_code(request):
    # 定义变量，用于画面的背景色、宽、高
    bgcolor = (random.randrange(20, 100), random.randrange(20, 100), 255)
    width = 100
    height = 25
    # 创建画面对象
    im = Image.new('RGB', (width, height), bgcolor)
    # 创建画笔对象
    draw = ImageDraw.Draw(im)
    # 调用画笔的point()函数绘制噪点
    for i in range(0, 200):
        xy = (random.randrange(0, width), random.randrange(0, height))
        fill = (random.randrange(0, 255), random.randrange(0, 255), random.randrange(0, 255))
        draw.point(xy, fill=fill)
    # 定义验证码的备选值
    str1 = 'abcd123efgh456ijklmn789opqr0stuvwxyzABCD123EFGHIJK456LMNOPQRS789TUVWXYZ0'
    # 随机选取4个值作为验证码
    rand_str = ''
    for i in range(0, 4):
        rand_str += str1[random.randrange(0, len(str1))]


    #保存到sesison
    request.session["validate_code"] = rand_str

    # 构造字体对象
    font = ImageFont.truetype(settings.FONT_STYLE, 23)
    # 绘制4个字
    for i in range(4):
        # 构造字体颜色
        fontcolor = (255, random.randrange(0, 255), random.randrange(0, 255))
        draw.text((5+24*i, 2), rand_str[i], font=font, fill=fontcolor)

    # 释放画笔
    del draw

    buf = BytesIO()
    # 将图片保存在内存中，文件类型为png
    im.save(buf, 'png')
    # 将内存中的图片数据返回给客户端，MIME类型为图片png
    return HttpResponse(buf.getvalue(), 'image/png')


def forget(request):
     return render(request,'ve_user/forget.html')

def forget_handle(request):
    email=request.POST.get('email')
    name=request.session['login_user_name']
    blog_user=UserInfo.objects.filter(uname=name,uemail=email)
    if blog_user:
        serializer=Serializer(settings.SECRET_KEY,3600)
        info={'confirm':blog_user.values()[0]['id'] }
        token = serializer.dumps(info).decode()
        encryption_url = 'http://192.168.12.191:8888/user/active/%s' % token

        # 发邮件
        subject = '天天生鲜'  # 邮件的标题
        message = ''  # 文本内容
        sender = settings.EMAIL_FROM
        receiver = [email]
        html_message = '<h1>%s,欢迎你成为天天生鲜注册会员</h1>请点击下面链接激活您的账户</br><a href="%s">%s</a>' % (name, encryption_url, encryption_url)  # html内容

        # 发送
        task_send_mail.delay(subject, message, sender, receiver, html_message=html_message)

        return render(request, 'df_user/login.html')
    else:
        return render(request,'ve_user/forget.html',{'msg':'该用户不存在，请确认该邮箱注册过账号'})


def active(request,token):
    serializer = Serializer(settings.SECRET_KEY, 3600)
    try:
        info = serializer.loads(token)
        # 获取激活码用户的id
        user_id = info['confirm']

        # 根据id获取用户信息
        user = UserInfo.objects.get(id=user_id)
        user.is_active = 1
        user.save()
        return render(request,'ve_user/reset.html')
    except SignatureExpired as e:
        return HttpResponse('激活链接已过期')
    except BadSignature as e:
        return HttpResponse('激活链接非法')


def reset(request):
     return render(request,'ve_user/reset.html')

def reset_handle(request):
    pwd1=request.POST.get('newpwd1','')
    pwd2=request.POST.get('newpwd2','')
    email=request.POST.get('email','')

    if pwd1!= pwd2:

        return render(request, 've_user/reset.html', {'msg': '密码不一致！'})
    else:

        user=UserInfo.objects.get(uemail=email)
        user.upwd=my_md5(pwd2)
        user.save()
        return render(request, 'df_user/login.html')

def index(request):
    context = {'title': '用户首页'}
    return render(request, 'df_user/index.html', context)

@my_login
def info(request):
    uname = request.session.get('login_user_name','')
    uid=request.session.get('login_user_id')
    print(uid)
    uphone=UserInfo.objects.filter(id=uid)[0].uphone
    uaddress=UserInfo.objects.filter(id=uid)[0].uaddress
    context={'title':'用户中心','uname':uname,'uphone':uphone,'uaddress':uaddress}
    return render(request, 'df_user/user_center_info.html',context)

@my_login
def order(request):
    context = {'title': '用户中心'}
    return render(request, 'df_user/user_center_order.html',context)


@my_login
def site(request):
    uid = request.session.get('login_user_id')
    user = UserInfo.objects.get(id=uid)
    if request.method=='GET':
        context = {'title': '用户中心', 'user':user}
        return render(request, 'df_user/user_center_site.html', context)

    elif request.method=='POST':
        user.ureceiver=request.POST.get('ureceiver')
        user.uaddress=request.POST.get('uaddress')
        user.upostcode=request.POST.get('upostcode')
        user.uphone=request.POST.get('uphone')
        user.save()
        context = {'title': '用户中心','user':user}
        return render(request, 'df_user/user_center_site.html',context)


