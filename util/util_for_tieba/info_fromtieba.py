# _*_ coding: utf-8 _*_
import os.path
import re
import time
import asyncio
from util.util_for_tieba.correct_rotation_for_angle import process_images
from pyppeteer import launch
import datetime

from bs4 import BeautifulSoup
import warnings
from util.base_fromxx import BaseCatch
warnings.filterwarnings("ignore",category=DeprecationWarning)

"""     
欲实现功能: 1.在主页中常看的内容检索
          2.按指定吧进行检索
          
          获取的内容包括：来自哪个吧？贴名？主题？评论数？链接？
          各自按指定顺序存于列表中
          
          主页访问热门动态的方式与指定吧内的不同.....
"""


# Crawling infor from tie-ba
class CatchFrom(BaseCatch):
    # please use firefox
    def __init__(self, ID, width=1920, height=1080):
        super().__init__(url_name='Baidu_tieba', type_='f?kw=')
        # search from theme 广东工业大学

        self.serial_ = self.type_ + str(ID)
        self.url = self.url_dir.get(self.url_name.lower()) + self.serial_

        self.ID = ID
        self.width = width
        self.height = height
        self.page = None
        self.browser = None
        self.page_final = None

    async def Setting(self):
        # 浏览器 启动参数
        start_parm = {
            # 启动chrome的路径
            # "executablePath": "/opt/microsoft/msedge/microsoft-edge",  # 使用edge浏览器
            # "executablePath": "/usr/lib/firefox/firefox.sh",  # 使用火狐浏览器
            # 关闭无头浏览器
            "headless": False,  # 设置为True，则不会打开浏览器
            'slowMo': 1.3,  # 通过传入指定的时间
            "args": [
                '--disable-infobars',  # 关闭自动化提示框
                '--window-size=1920,1080',  # 窗口大小
                '--log-level=30',  # 日志保存等级， 建议设置越好越好，要不然生成的日志占用的空间会很大 30为warning级别
                '--no-sandbox',  # 关闭沙盒模式
                '--start-maximized',  # 窗口最大化模式

                # '--proxy-server=http://localhost:1080'  # 代理
                'userDataDir=./userdata'  # 用户文件地址
            ],
        }
        self.browser = await launch(start_parm)
        self.page = await self.browser.newPage()
        await self.page.setUserAgent(
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36 Edg/102.0.1245.33")
        await self.page.setViewport({'width': self.width, 'height': self.height})

        await self.page.goto(self.url)  # 访问网页
        await self.page.waitFor(7000)  # 等待5秒供页面加载完全
        await self.CalculateAngle()   # 实现验证操作
        await self.page.waitFor(8000)  # 验证完成后，再等待5秒进入页面
        self.page_final = await self.page.content()
        # print(self.page_final)
        # await self.page.click(".pagination-current pagination-item ")
        # <span class="pagination-current pagination-item ">1</span>

        # <a href="//tieba.baidu.com/f?kw=%E5%8E%9F%E7%A5%9E%E5%86%85%E9%AC%BC&amp;ie=utf-8&amp;pn=50"
        # class="next pagination-item ">下一页&gt;</a>
        self.page_1 = await self.page.content()

    async def CalculateAngle(self):
        label_image = '.vcode-spin-img'
        rotImg = await self.page.querySelector(label_image)
        if rotImg is not None:
            print("-------------------需要执行验证操作--------------------")
            print("下面显示每次尝试验证：")
            await self.page.waitFor(2000)
            while rotImg:
                img_url = await (await rotImg.getProperty("src")).jsonValue()
                angle = process_images(img_url)[0]
                bottom_line = await (
                    await(await self.page.querySelector(".vcode-spin-bottom")).getProperty("offsetWidth")).jsonValue()
                button_line = await (
                    await(await self.page.querySelector(".vcode-spin-button")).getProperty("offsetWidth")).jsonValue()
                b = bottom_line - button_line
                move_line = angle / 360 * b
                await self.MoveSlider(move_line)
                # 停个3秒
                await asyncio.sleep(3)
                rotImg = await self.page.querySelector('.vcode-spin-img')
        else:
            # print("不需要执行验证操作")
            pass

    async def MoveSlider(self, distance=308):
        # 将距离拆分成两段，模拟正常人的行为
        distance1 = distance - 10
        distance2 = 10
        btn_position = await self.page.evaluate('''
               () =>{
                return {
                 x: document.querySelector('.vcode-spin-button').getBoundingClientRect().x,
                 y: document.querySelector('.vcode-spin-button').getBoundingClientRect().y,
                 width: document.querySelector('.vcode-spin-button').getBoundingClientRect().width,
                 height: document.querySelector('.vcode-spin-button').getBoundingClientRect().height
                 }}
                ''')
        x = btn_position['x'] + btn_position['width'] / 2
        y = btn_position['y'] + btn_position['height'] / 2
        # print(btn_position)
        await self.page.mouse.move(x, y)
        await self.page.mouse.down()
        await self.page.mouse.move(x + distance1, y, {'steps': 30})
        await self.page.waitFor(800)
        await self.page.mouse.move(x + distance1 + distance2, y, {'steps': 20})
        await self.page.waitFor(800)
        await self.page.mouse.up()

    def baidu_login(self):
        asyncio.get_event_loop().run_until_complete(self.Setting())

    def _extract_fromcode(self, show_inf=False):

        self.baidu_login()
        self.data = self.page_final

        print("---------------------验证成功-----------------------")
        print("即将输出条目：")
        # print(type(self.data))
        time.sleep(3)

        self._get_title()  # 获取标题
        self._get_response()  # 获取回复数
        self._get_address()  # 获取帖子地址

    def _get_title(self, show_inf=False):
        # print(self.data)
        self.title_list = []
        self.link_list = []
        if self.ID != 'None':
            label_name = '<a rel="noopener" href="(.*?)" title="(.*?)" target="_blank" class="j_th_tit ">'
        else:
            label_name = '<a class="title feed-item-link" rel="noopener" href="(.*?)" target="_blank" title="(.*?)">'

        res = re.findall(label_name, self.data)

        for i, o in enumerate(res):
            if show_inf:
                print("{}:{}".format(i + 1, o[1]))
            self.title_list.append(o[1])
            self.link_list.append(o[0])

        # print(self.title_list)

    def _get_tiebaname(self):
        if self.ID != 'None':
            self.name = self.ID
        else:
            pass

    def _get_response(self):
        self.response_list = []
        soup = BeautifulSoup(self.data, 'lxml')
        res = soup.find_all('span', attrs={'title': '回复'})
        for index in res:
            self.response_list.append(int(index.text))

    def _get_address(self):
        self.address_link = []
        forward = self.url_dir.get(self.url_name.lower())
        for id_ in self.link_list:
            self.address_link.append(forward + id_[1:])

    def notes(self):
        if not os.path.exists(os.getcwd() + "/Entry"):
            os.mkdir(os.getcwd() + "/Entry")
        style = '%Y-%m-%d %H:%M:%S'
        now = datetime.datetime.now().strftime(style)
        with open((os.getcwd() + "/Entry/search_notes.txt"), 'r') as f:
            note = f.read()
        with open((os.getcwd() + "/Entry/search_notes.txt"), 'w') as f:
            note += ("-" * 25 + now + "-" * 25 + "\n")
            note += ("搜索吧名：{}\t".format(self.ID))
            note += ("搜索条目数：{}\n".format(len(self.link_list)))
            # print(note)
            f.write(note)


    def download(self, time_side=0.5):
        self._extract_fromcode()
        message = ''
        i = 0
        while i < len(self.link_list):
            try:
                message += '{}:{}\n{}[评论]：{}    [链接]：{}\n\n'.format(i + 1, self.title_list[i], '',
                                               self.response_list[i], self.address_link[i])
                i += 1
            except IndexError:
                i += 1
                continue
        message += "---------------------输出结束-----------------------"
        print(message)

        self.notes()


if __name__ == "__main__":
    CatchFrom(ID="").download()