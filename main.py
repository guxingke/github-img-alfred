# coding: utf8

"""复制图片/截图 --> Github 处理逻辑"""

__author__ = 'admin@guxingke.com'

import os
import time
import subprocess

import clipboard

from config import (
    GITHUB_REPO, LOCAL_GIT_REPO_PATH, SUBDIR
)


IMG_TPL = '<img src=\"{}\" width=\"{}\" height=\"{}\" />'
IMG_TPL = '![{}]({})'


CLIPBOARD_EXCEPTIONS = (
    clipboard.WriteFileError,
    clipboard.FileTypeUnsupportedError,
    clipboard.NotImageError
)


class ImgSizeError(Exception):

    """获取图片大小异常"""

    def __init__(self):
        super(ImgSizeError, self).__init__('获取图片大小异常!')


def process():
    """主流程"""

    # 检查相关配置是否已配置
    if not all((GITHUB_REPO,LOCAL_GIT_REPO_PATH,SUBDIR)):
        notice('请先设置相关配置!')
        open_with_editor('config.py')
        return

    try:
        img_path = clipboard.get_pasteboard_img_path()
    except CLIPBOARD_EXCEPTIONS as error:
        notice(str(error))
        return

    file_name = os.path.split(img_path)[-1]
    file_type = file_name.split('.')[-1]
    if file_type == 'tiff':
        new_img_path = '/tmp/{}.png'.format(int(time.time()))
        # tiff --> png
        _convert_to_png(img_path, new_img_path)
        img_path = new_img_path

    # 获取图片尺寸
    width, height = _get_img_size(img_path)

    try:
        cmd = 'cp {} {}'.format(img_path, LOCAL_GIT_REPO_PATH + '/' + SUBDIR, LOCAL_GIT_REPO_PATH)
        
        os.system(cmd)

        # 完整的图片URI
        img_file_name = os.path.split(img_path)[-1]
        img_uri = '{}/{}/{}'.format(GITHUB_REPO, SUBDIR,  img_file_name)

        notice('上传成功!')
    except Exception as error:
        notice('上传图片异常!{}'.format(str(error)))
        return

    # markdown使用html格式,保证图片大小
    markdown_img = IMG_TPL.format(img_file_name, img_uri)

    # 写入剪贴板
    write_to_pasteboard(markdown_img)

    # 打印出markdown格式的图片地址
    print_pasteboard_content()


def _get_img_size(img_path):
    """获取图片尺寸

    :param img_path: 图片路径
    """
    width = os.popen("sips -g pixelWidth %s | awk -F: '{print $2}'"
                     % img_path).read()
    height = os.popen("sips -g pixelHeight %s | awk -F: '{print $2}'"
                      % img_path).read()
    try:
        width = int(width.strip())
        height = int(height.strip())
    except ValueError:
        raise ImgSizeError()
    return width, height


def _convert_to_png(src_path, dest_path):
    """转换图片格式为png

    :param src_path: 源文件
    :param dest_path: 目标文件
    """
    os.system('sips -s format png {} --out {}'.format(src_path, dest_path))


def write_to_pasteboard(text):
    """内容写入剪贴板

    :param text: 写入内容
    """
    os.system('echo \'{}\' | pbcopy'.format(text))


def print_pasteboard_content():
    """从剪贴板打印出内容"""
    write_command = (
        'osascript -e \'tell application '
        '"System Events" to keystroke "v" using command down\''
    )
    os.system(write_command)


def notice(msg, title='上传图片通知'):
    """通知

    :param msg: 通知消息
    :param title: 通知标题
    """
    os.system('osascript -e \'display notification "{}" with title "{}"\''.format(msg, title))



def open_with_editor(file_path):
    """打开配置文件

    :param file_path: 文件路径
    """
    os.system('open -b "com.apple.TextEdit" "./{}"'.format(file_path))



def main():
    """main"""
    process()

if __name__ == '__main__':
    main()
