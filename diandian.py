#!/usr/bin/env python
#coding:utf-8

import urllib
import urllib2
import cookielib
import re
import sys
import os
import time
import json
import webbrowser

usr = ''
pwd = ''

url_login  = 'http://www.diandian.com/login'
url_delete = 'http://www.diandian.com/delete'
url_logout = 'http://www.diandian.com/logout?formKey='
url_create_blog = 'http://www.diandian.com/new/blog'

class Diandian:
    def __init__(self,usr,pwd):
        self.usr = usr
        self.pwd = pwd
        cj = cookielib.CookieJar()
        handler = urllib2.HTTPCookieProcessor(cj)
        self.opener = urllib2.build_opener(handler)
        urllib2.install_opener(self.opener) 
        
    def login(self):
        postdata = {
            'account':self.usr,
            'password':self.pwd,
            'persistent':1
        }
        req = urllib2.Request(url_login,urllib.urlencode(postdata))
        jump = self.opener.open(req)
        page = jump.read()
        
        self.form_key = re.compile(r"window.DDformKey = '(.*?)'").findall(page)[0]
        self.blog_link_list = re.compile(r'<a\s+href="(.*?)"><span\s+class="pop-menu-extra\s+blog-move-icon">').findall(page)
        self.blog_name_list = re.compile(r'<span class="nav-blog-name">(.*?)</span>').findall(page)
        self.blog_domain_list = [re.compile(r'http://www.diandian.com/dianlog/(.*)').findall(i)[0] for i in self.blog_link_list]
        self.blog_rss_list  = ['http://'+ i +'.diandian.com/rss' for i in self.blog_domain_list]
        #print self.blog_domain_list
        #print self.blog_rss_list
        #self.blog_id_list   = re.compile(r'id="pop-blog-(.*?)"').findall(page)
        #print self.form_key
        


    def show_blog_list(self):
        blog_numbers = len(self.blog_name_list)
        print 'Your blogs:'
        for i in xrange(blog_numbers):
            print i,':',self.blog_name_list[i]


    def get_essay_id_list(self,link_item):
        cur_link  = self.blog_link_list[link_item]

        jump = self.opener.open(cur_link)
        page = jump.read()

        page_rss = urllib.urlopen(self.blog_rss_list[link_item]).read()
        #item_list = re.compile(r'<item>(.*?)</item>').findall(page_rss)
        #print item_list
        self.title_list = re.compile(r'<title>(.*?)</title>').findall(page_rss)[2:]
        self.essay_link_list = re.compile(r'<link>(.*?)</link>').findall(page_rss)[2:]
        self.id_list = re.compile(r'<a class="feed-cmt" data-nid="(.*?)"').findall(page)
        #print len(self.id_list)

    def get_all_essays(self):
        blog_number = len(self.blog_link_list)

        lst = []
        for i in xrange(blog_number):
            self.get_essay_id_list(i)
            lst.extend(self.title_list)
            
        self.title_list = lst

    def post_new_essay(self,title,content,link_item):
            
        postdata = {
            'formKey':self.form_key,
            'title':title,
            'content':content,
            'privacy':0,
            'setTop':'false',
            'creativeCommonsEnable':'false',
            'creativeCommonsType':'by_nc_nd',
            'syncToWeibo':'false',
            'syncToQqWeibo':'false',
            'syncToDouban':'false',
            'syncToQzone':'false',
            'syncToRenren':'false',
            'syncToFacebook':'false',
            'syncToTwitter':'false',
            'syncToFlickr':'false'
        }
        
        
        req = urllib2.Request(self.blog_link_list[link_item] + '/new/text',urllib.urlencode(postdata))
        jump = self.opener.open(req)

        
    def post_new_vedio(self,link,blog):
        """support Youku tudou.."""
        url_search = 'http://www.diandian.com/new/videosearch'
        postdata = {
            'formKey':self.form_key,
            'html_url':link    
        }
        
        req  = urllib2.Request(url_search,urllib.urlencode(postdata))
        jump = self.opener.open(req)
        p    = json.load(jump)
        
        
        video_name     = re.compile(r'<title>(.*?)</title>').findall(urllib.urlopen(link).read())[0]
        try:
            video_name = video_name.decode('gbk').encode('utf-8')
        except:
            pass
            
        video_desc     = p['video_desc']
        video_img_url  = p['video_img_url']
        video_video_id = p['video_video_id']
        code           = p['code']
        msg            = p['msg']
        content        = '''<p>%s</p>'''%video_name 
        
        #blogUrl    = re.compile(r'http://www.diandian.com/dianlog/(.*)').findall(self.blog_link_list[blog])[0]
        blogUrl    = self.blog_domain_list[blog]
        url_save   = '''http://www.diandian.com/dianlog/%s/new/video'''%blogUrl
        postdata = {
            'formKey':self.form_key,
            'video_name':video_name,
            'video_desc':video_desc,
            'video_img_url':video_img_url,
            'video_video_id':video_video_id,
            'code':code,
            'msg':msg,
            'content':content,
            'privacy':0,
            'setTop':'false',
            'creativeCommonsEnable':'false',
            'creativeCommonsType':'by_nc_nd',
            'syncToWeibo':'false',
            'syncToQqWeibo':'false',
            'syncToDouban':'false',
            'syncToQzone':'false',
            'syncToRenren':'false',
            'syncToFacebook':'false',
            'syncToTwitter':'false',
            'syncToFlickr':'false',
            'type':'video',
            'blogUrl':blogUrl,
            'autoSaveId':0,
            'autoSaveType':0
        }
                
        req   = urllib2.Request(url_save,urllib.urlencode(postdata))     
        jump  = self.opener.open(req)
        p     = json.load(jump)

        if p['errCode'] == "0":
            return 0
        else:
            return -1
        
    def show_essay_list(self):
        title_number = len(self.title_list)
        for i in xrange(title_number):
            print i,':',self.title_list[i]


        
        
    def delete_essay(self,del_item):

        postdata = {
            'formKey':self.form_key,
            'feed_id':self.id_list[del_item]
        }

        req = urllib2.Request(url_delete,urllib.urlencode(postdata))
        self.opener.open(req)

    def delete_all_essay(self):
        #root here,it is so dangerous
        pass


    def get_essay_content(self,blog,item):
        #url  = self.blog_link_list[blog]
        #jump = self.opener.open(url)
        #page = jump.read()
        self.get_essay_id_list(blog)
        #links = re.compile(r'<a href="(.*?)".*?class="link-to-post"\s+title="查看文章').findall(page)
        #item_link = links[item]
        webbrowser.open(self.essay_link_list[item])
        
        
    def logout(self):
        url = url_logout + self.form_key
        self.opener.open(url)
        


    def create_new_blog(self,name,url):
        url_check = 'http://www.diandian.com/check_if_blog_url_is_available?'
        url_check += str(int(time.time() * 1000))

        postdata_check = {
                'formKey':self.form_key,
                'blogUrl':url
            }
        req  = urllib2.Request(url_check,urllib.urlencode(postdata_check))
        jump = self.opener.open(req)
        p = json.load(jump)
        
        if p['status_code'] == "-9":
            return -1 #failed
        
        
        postdata = {
            'formKey':self.form_key,
            'blogName':name,
            'blogUrl':url
            }
        
        req  = urllib2.Request(url_create_blog,urllib.urlencode(postdata))
        jump = self.opener.open(req)
        return 0

    
def get_title_content(fp):
    if not os.path.exists(fp):
        return -1
        
    title = os.path.basename(fp)
    with open(fp,'r') as f:
        content = f.read()

    try:
        content = content.decode('gbk').encode('utf-8')
    except:
        pass
    
    return title,content

def get_title_content_link(url):
        #get decode
    content = urllib.urlopen(url).read()
    title =re.compile(r'<title>(.*?)</title>').findall(content)[0]
    try:
        title = title.decode('gbk').encode('utf-8')
        content = content.decode('gbk').encode('utf-8')
    except:
        pass
    
    if title:
        return title,content
    return -1
    
    
def usage():
    _usage = """
.........................
.      DianDian.py      .
.           _by Zuckonit.
.........................
usage:
    -sb  show all blog
    -se  [which blog] show [all] essays
    -pe  title content whichblog
         post new essay
    -fpe filepath whichblog
         post new essay by file
    -lpe link whichblog
         post new essay by link
    -pv  link blogitem
         post a video by link
         (Youku,Tudou,Ku6,六间房，56,Qiyi,sohu,音悦台，Bilili)
    -de  whichblog whichessay
         delete essay
    -cb  blogname urlname
         create a new blog
    -gc  whichblog essayitem
         open the essay in browser
    -h   see the usage
    """
    print _usage
    
def main():
    opt  = sys.argv
    argc = len(opt)
    if argc == 1:
        usage()
        return
    
    demo = Diandian(usr,pwd)
    demo.login()
    if opt[1] == '-sb':#show blog list
        demo.show_blog_list()
        
    elif opt[1] == '-se':#show essay list
        if argc < 3:
            demo.get_all_essays()
            demo.show_essay_list()
        else:
            demo.get_essay_id_list(int(opt[2]))
            demo.show_essay_list()
            
    elif opt[1] == '-pe':#post essay
        if argc > 4:
            try:
                opt[2] = opt[2].decode('gbk').encode('utf-8')
                opt[3] = opt[3].decode('gbk').encode('utf-8')
            except:
                pass
            
            demo.post_new_essay(opt[2],opt[3],int(opt[4]))
        else:
            usage()
            
    elif opt[1] == '-fpe':
        if argc > 3:
            val = get_title_content(opt[2])
            if val == -1:
                print 'file %s not exist'%opt[2]
                return
            demo.post_new_essay(val[0],val[1],int(opt[3]))
        else:
            usage()
    
    elif opt[1] == '-lpe':
        if argc > 3:
            val = get_title_content_link(opt[2])
            if val == -1:
                pass
            else:
                demo.post_new_essay(val[0],val[1],int(opt[3]))
        else:
            usage()
            
    elif opt[1] == '-pv':
        if argc > 3:
            val = demo.post_new_vedio(opt[2],int(opt[3]))
            if val == -1:
                print 'error'
        else:
            usage()
           
    elif opt[1] == '-de':
        if argc > 2:
            demo.get_essay_id_list(int(opt[2]))
            demo.delete_essay(int(opt[3]))
        else:
            usage()

    elif opt[1] == '-cb':
        if argc > 3:
            val = demo.create_new_blog(opt[2],opt[3])
            if val == -1:
                print 'This url has been used , please change another one'
        else:
            usage()

    elif opt[1] == '-gc':
        if argc > 3:
            demo.get_essay_content(int(opt[2]),int(opt[3]))
        else:
            usage()
            
    
    else:
        usage()
    demo.logout()


main()
