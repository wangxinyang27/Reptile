# _*_ coding: utf-8 _*_
import os.path
import warnings
import re
import json
import requests
import subprocess
import datetime
from util.base_fromxx import BaseCatch
warnings.filterwarnings("ignore",category=DeprecationWarning)


class CatchFrom(BaseCatch):
    # please use firefox
    def __init__(self, ID):
        super().__init__(url_name='BiliBili_video', type_='bv')
        # The general bv number is represented by letters and numbers together
        if isinstance(ID, int):
            self.serial_number = self.type_ + str(ID)
        elif isinstance(ID, str):
            self.serial_number = self.type_.upper() + ID
        else:
            raise OSError("Bv numbers of this format type are not supported")

        self.url = self.url_dir.get(self.url_name.lower()) + self.serial_number

        self.header_ = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36 Edg/102.0.1245.33'
        }
        self.video_dir = ""
        self.audio_dir = ""


    def _extract_fromcode(self, show_inf=False):
        self._get_code_frompage(self.url)
        # name of video
        label_title = '<h1 title="(.*?)" class="video-title tit">'
        self.video_label = re.findall(label_title, self.data)
        # play volume
        label_play_volume = '<span title="总播放数(.*?)" class="view item">'
        self.play_volume = re.findall(label_play_volume, self.data)

        self.video_label[0] = self.video_label[0].replace(' ', '')  # remove the spaces in the video name
        print("-" * 80)
        print("视频名：{}，播放量：{}".format(self.video_label[0], self.play_volume[0]))

        input("The above are the video obtained, press Enter to start the download")

        res = requests.get(url=self.url, headers=self.header_)

        res.encoding = res.apparent_encoding
        self.html = res.text
        # print(self.html)

        json_data = re.findall('<script>window.__playinfo__=(.*?)</script>', self.html)[0]

        if len(json_data) == 0:
            raise OSError("No video found, please try another bv numbers")

        json_data = json.loads(json_data)

        '''Extract audio'''
        self.audio_url = json_data['data']['dash']['audio'][0]['backupUrl'][0]
        '''Extract video'''
        self.video_url = json_data['data']['dash']['video'][0]['backupUrl'][0]

        self.header_['Referer'] = self.url

    def _check_downloadpath(self, print_=False):
        pass

    @staticmethod
    def _print_download_path():
        # we had finished its function in other
        pass

    def notes(self):
        style = '%Y-%m-%d %H:%M:%S'
        now = datetime.datetime.now().strftime(style)
        with open((os.getcwd() + "/Video/download_notes.txt"), 'r') as f:
            note = f.read()
        with open((os.getcwd() + "/Video/download_notes.txt"), 'w') as f:
            note += ("-" * 25 + now + "-" * 25 + "\n")
            note += ("搜索视频名：{}\t".format(self.video_label[0]))
            # print(note)
            f.write(note)

    def download(self, time_side=0.5):
        self._extract_fromcode()

        video_name = "Video"
        audio_name = "Audio"

        self.video_dir = self.path_splicing(video_name)
        self.audio_dir = self.path_splicing(audio_name)

        if not os.path.exists(self.video_dir):
            os.mkdir(self.video_dir)

        if not os.path.exists(self.audio_dir):
            os.mkdir(self.audio_dir)

        # an audio
        r3 = requests.get(url=self.audio_url, headers=self.header_)
        audio_data = r3.content
        with open(self.audio_dir + '/' + self.video_label[0] + '_audio.mp3', mode='wb') as f:
            f.write(audio_data)
        self.Procession(audio_name, [1, 2])
        # a video without sound
        r4 = requests.get(url=self.video_url, headers=self.header_)
        video_data = r4.content
        with open(self.video_dir + '/' + self.video_label[0] + '_video.mp4', mode='wb') as f:
            f.write(video_data)
        self.Procession(video_name, [1, 2])

        r3.close()
        r4.close()

        self._composite()

        self.notes()

    def _composite(self, save_mp3=True, save_mp4=False):

        # Next we combine the two
        video = self.path_splicing(self.video_label[0], 'Video') + '_video.mp4'
        audio = self.path_splicing(self.video_label[0], 'Audio') + '_audio.mp3'
        # print(video,audio)

        # A video without sound doesn't make much sense, so we replace it with the video after compositing
        target = self.path_splicing(self.video_label[0], 'Video')

        cmd = f'ffmpeg -i {video} -i {audio} -acodec copy -vcodec copy {self.video_label[0][:2] + ".mp4"} -loglevel quiet'
        subprocess.call(cmd, shell=True)
        # Under the default option, we keep the audio, that is, the file in mp3 format
        self.Procession('composite', [1, 2])
        if not save_mp4:
            os.remove(video)
        if not save_mp3:
            os.remove(audio)

        # print(self.video_label[0][:2])
        os.rename(self.video_label[0][:2] + '.mp4', target + '.mp4')

    @staticmethod
    def path_splicing(str_p, file_name=""):
        # A simple function for paths (absolute) by virtue of audio, raw video and composite video
        abs_path = os.getcwd()

        if file_name != "":
            return abs_path + "/" + file_name + "/" + str_p
        else:
            return abs_path + "/" + str_p



