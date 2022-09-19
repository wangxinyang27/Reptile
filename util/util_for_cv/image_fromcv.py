# _*_ coding: utf-8 _*_

import os
import re
import requests
import warnings
import datetime
from util.base_fromxx import BaseCatch
warnings.filterwarnings("ignore",category=DeprecationWarning)


# Crawling pictures in Bilibili articles
class CatchFrom(BaseCatch):
    # please use firefox
    def __init__(self, ID):
        super().__init__(url_name='BiliBili_read', type_='cv')

        self.serial_number = self.type_ + str(ID)
        self.url = self.url_dir.get(self.url_name.lower()) + self.serial_number
        self.ID = ID
        self.num = None

    def _extract_fromcode(self, show_inf=False):
        self._get_code_frompage(self.url)
        label = '<img data-src="(.*?)" data-size="(.*?)" width="(.*?)" height="(.*?)">'
        self.result = re.findall(label, self.data)

        if len(self.result) == 0:
            raise OSError("No image found, please try another cv numbers")
        if show_inf:
            print("the num of those images which extracted from source code is: {}".format(len(self.result)))
            print("all of these images are.....")
            for i, o in enumerate(self.result):
                print("{0}: {1}".format(i, o[0]))

    def _check_downloadpath(self, print_=False):
        # Determine whether the format of the download path is correct and add a modification
        for _check_point in self.result:
            # add the prefix to the path of download
            prefix = 'https:'
            if isinstance(_check_point[0], str):
                img_path = prefix + _check_point[0]
            else:
                img_path = prefix + str(_check_point[0])

            # correct the format of downloaded images
            if img_path.find(".jpg@(.*?).webp"):
                img_path = img_path.split("@")[0]
            else:
                raise OSError("The image's download URL doesn't appear to match the pattern")

            self.download_path.append(img_path)

        if print_:
            for i, o in enumerate(self.download_path):
                print("No.{}:{}".format(i, o))

    def notes(self):
        style = '%Y-%m-%d %H:%M:%S'
        now = datetime.datetime.now().strftime(style)
        with open((os.getcwd() + "/Image/download_notes.txt"), 'r') as f:
            note = f.read()
        with open((os.getcwd() + "/Image/download_notes.txt"), 'w') as f:
            note += ("-" * 25 + now + "-" * 25 + "\n")
            note += ("搜索cv号：cv{}\t".format(self.ID))
            note += ("爬取图片数：{}\n".format(self.num))
            # print(note)
            f.write(note)

    def download(self, time_side=0.5):
        self._extract_fromcode()

        image_dir = "Image"
        if not os.path.exists(image_dir):
            os.mkdir(image_dir)
        dict_ = os.listdir(image_dir)
        dict_num = len(dict_)
        image_index = 0 + dict_num

        self.num = dict_num
        self._check_downloadpath(print_=True)

        input("The above are all the pictures obtained, press Enter to start the download")

        for single_path in self.download_path:
            # print(img_path)
            suffix = single_path.split('.')[-1]
            # print(res.status_code)
            res = requests.get(single_path)
            label = 'Image' + '_' + str(image_index + 1)
            self.Procession(label, [1, 3], 10)
            with open(image_dir + '/' + str(image_index) + '.' + suffix, mode='wb') as file:
                file.write(res.content)
            image_index += 1
        self.notes()