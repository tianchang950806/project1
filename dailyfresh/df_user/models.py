#coding=utf-8
from django.db import models

class UserInfo(models.Model):
    uname=models.CharField(max_length=20)
    upwd=models.CharField(max_length=40)
    uemail=models.CharField(max_length=30)
    ureceiver=models.CharField(max_length=20,default='')
    uaddress=models.CharField(max_length=100,default='')
    upostcode=models.CharField(max_length=6,default='')
    uphone=models.CharField(max_length=11,default='')
    # default和blank是python层面的约束，不影响数据库表结构