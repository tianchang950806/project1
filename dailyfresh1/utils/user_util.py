import hashlib
from django.shortcuts import render,redirect
from django.core.urlresolvers import reverse


def my_md5(value):
    m=hashlib.md5()
    m.update(value.encode('utf-8'))
    return m.hexdigest()


def my_login(func):
    def inner(*args,**kwargs):
        login_user_id=args[0].session.get('login_user_id')
        if login_user_id:
            return func(*args,**kwargs)
        else:
            resp=redirect(reverse('user:login'))
            resp.set_cookie('url_dest',args[0].get_full_path())
            return resp
    return inner



