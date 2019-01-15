from PIL import Image
from selenium import webdriver
from selenium.webdriver import ActionChains
import re,time,requests,random


class Bili(object):
    def __init__(self):
        self.poslist = []
        self.filename1 = '1new.png'
        self.filename2 = '2new.png'
        self.get_image()

    # 获取图片
    def get_image(self):
        headers = {'User-Agent':"Opera/8.0 (Windows NT 5.1; U; en)"}
        self.driver = webdriver.Chrome()
        self.driver.get('https://passport.bilibili.com/login')
        time.sleep(2)
        rlist = self.driver.find_elements_by_xpath('//div[@class="gt_cut_bg_slice"]')
        #存储各图片位置的列表
        for r in rlist:
            s = r.get_attribute('style')
            #带缺口的图片url
            img = re.findall(r'url\("(.*?)"\)',s)
            pos = re.findall(r'background-position: (.*?)px.*?(\S*?)px',s)
            self.poslist.append(pos[0])
        # 将提交的url地址后缀改为jpg
        img = img[0].replace('webp','jpg')
        img2 = re.findall(r'(.*?)/bg',img)[0]+re.findall(r'gt(.*?)/bg',img)[0]+'.jpg'
        # 保存获取的图片
        with open('1.jpg','wb') as f:
            f.write(requests.get(img).content)
        with open('2.jpg','wb') as f:
            f.write(requests.get(img2).content)
        # driver.quit()
        for i in ('1.jpg','2.jpg'):
            self.get_new_image(i)


    #重组图片
    def get_new_image(self,filename):
        #创建新的空白图片
        to_image = Image.new('RGB',(260,116))
        img = Image.open(filename)
        #分别为储存上下两列的小图片列表
        uplist = []
        bulist = []
        # 把每个位置的图片截取出来
        for i in self.poslist:
            if i[1] == '-58':
                box = (int(i[0][1:]),58,int(i[0][1:])+10,116)
                uplist.append(img.crop(box))
            else:
                box = (int(i[0][1:]),0,int(i[0][1:])+10,58)
                bulist.append(img.crop(box))
        #将图片按顺序进行粘贴
        x_offset = 0
        for up in uplist:
            to_image.paste(up,(x_offset,0))
            x_offset += up.size[0]
        x_offset = 0
        for bu in bulist:
            to_image.paste(bu,(x_offset,56))
            x_offset += bu.size[0]
        to_image.save(filename[0:-4]+'new.png','png')


    #获取缺口位置
    def quekou(self):
        img1 = Image.open(self.filename1)
        img2 = Image.open(self.filename2)
        slist = []
        for i in range(0,img1.size[0]):
            for j in range(0,img1.size[1]):
                rgb1 = img1.load()[i,j]
                rgb2 = img2.load()[i,j]
                if abs(rgb1[0] - rgb2[0])<60 and abs(rgb1[1] - rgb2[1])<60 and abs(rgb1[2] - rgb2[2])<60:
                    pass
                else:
                    slist.append(i)
        s = min(slist)
        self.run(s+2)

    #拖动图片验证码
    def run(self,s):
        #拖动验证码滑块的按钮
        btn = self.driver.find_element_by_xpath('//div[@class="gt_slider_knob gt_show"]')
        llist = []
        #初速度
        v = 25
        #加速度
        a = 2
        #当前位移
        sl = 0
        #时间间隔
        t = 0.2
        while sl <s:
            if sl>0.7*s:
                a = -2
            #没0.2s滑动的长度
            l = v*t+0.5*a*(t**2)
            v = v+a*t
            llist.append(l)
            sl += l
        #输入密码账号
        name = input('请输入账号：')
        pwd = input('请输入密码：')
        self.driver.find_element_by_xpath('//input[@id="login-username"]').send_keys(name)
        self.driver.find_element_by_xpath('//input[@id="login-passwd"]').send_keys(pwd)
        #按住滑动验证码按钮
        ActionChains(self.driver).click_and_hold(btn).perform()
        for i in llist:
            time.sleep(.1)
            ActionChains(self.driver).move_by_offset(xoffset=i,yoffset=0).perform()
        time.sleep(.4)
        ActionChains(self.driver).release().perform()
        time.sleep(.5)
        yan = self.driver.find_element_by_xpath('//span[@class="gt_info_type"]').text
        if '通过' in yan:
            print('验证成功')
        else:
            print('验证失败')


if __name__ == "__main__":
    b = Bili()
    b.quekou()
