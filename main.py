# _*_ coding: utf-8 _*_

import argparse
import importlib

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--list_', type=str, default="", help='Now you can enter multiple cv numbers at once'
    )
    parser.add_argument(
        '--catch_mode', type=str, default = "image_fromcv", help='image_fromcv or video_frombv'
    )
    lower_level = {"image_fromcv":"util_for_cv", "video_frombv":"util_for_bv", "info_fromtieba":"util_for_tieba"}
    opt, _ = parser.parse_known_args()
    list_str = opt.list_.split("/")
    prefix_util = "util" + "." + lower_level[opt.catch_mode] + "."
    # print(prefix_util)
    # print(opt.catch_mode)
    module_ = prefix_util + opt.catch_mode.lower()
    # print(module_)
    module_catch = importlib.import_module(module_)

    # list_int = []
    # for element in list_str:
    #     list_int.append(int(element))

    # print(list_int)
    for single_ in list_str:
        obj = module_catch.CatchFrom(ID=single_).download()
        del obj
