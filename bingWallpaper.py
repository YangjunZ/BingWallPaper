#!/usr/bin/env python


import requests
import re
import os
import json
import subprocess
import datetime

STATUS_CODE_200 = 200
bing = 'http://cn.bing.com'

IMAGE_OUT_FOLDER = 'images/'
CUR_PATH = os.path.abspath('.') + '/'


def changeBackground(imageName):
    print 'changeBackground'
    print imageName
    output = subprocess.check_output([ CUR_PATH + "/changeBackgroundImage.sh", CUR_PATH + imageName])
    print output


def getMainPage():
    args = '?mkt=zh-CN'
    response = downloadPage(bing + args)
    if response.status_code != STATUS_CODE_200:
        print 'request bing.com error, return is not ', STATUS_CODE_200
        traceback.print_exc(file=sys.stdout)
    return response.text


def parseMainPage(html):
    pattern = "url:(.*?),"
    rgxRes = re.findall(pattern, html)
    uriList = []

    for item in rgxRes:
        if item:
            uriList.append(fixUri(item))

    return uriList


def imageResolution(uriList):
    # todo change resolution
    return uriList


def fixUri(uri):
    uri = uri.strip()
    if uri.startswith('"') and uri.endswith('"'):
        uri = uri[1:-1]
    if uri.startswith("'") and uri.endswith("'"):
        uri = uri[1:-1]
    prefix_http = 'http://'
    prefix_https = 'https://'
    if not uri.startswith(prefix_http) and not uri.startswith(prefix_https):
        if uri.startswith('/') or uri.startswith('\/') :
            uri = bing + uri
        else:
            uri = bing + '/' + uri
    uri = uri.replace('\\', '')
    return uri


def getImages(uriList):
    # check whether image already exist
    #
    imageNames = []
    for imgUri in uriList:
        # remove args
        if '?' in imgUri:
            imgUri = imgUri[0: imgUri.index('?')]
        items = imgUri.split('/')
        filename = items[-1]

        imgList = os.listdir(IMAGE_OUT_FOLDER)
        if filename in imgList:
            print "[Already exsit]", filename, imgUri
            continue

        # Download
        print '[Downloading]', imgUri, '... '
        imgRsp = downloadPage(imgUri)
        contentType = 'Content-Type'
        if imgRsp.status_code == STATUS_CODE_200:
            if contentType in imgRsp.headers.keys() and imgRsp.headers.get(contentType).startswith('image'):
                imgf = open(IMAGE_OUT_FOLDER + '/' + filename, 'w')
                imgf.write(imgRsp.content)
                imgf.close()
                print '[Writed]', filename, ''
                imageNames.append(filename)
    return imageNames


def downloadPage(uri):
    user_agent = {\
            'Cache-Control': 'no-cache',
            'Referer': 'http://cn.bing.com/?mkt=zh-CN',
            'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'\
        }

    return requests.get(uri)


def loadConfig(filename):
    global IMAGE_OUT_FOLDER
    dic = json.load(open(filename,'r'))
    if dic.has_key('IMAGE_OUT_FOLDER'):
        IMAGE_OUT_FOLDER = dic.get('IMAGE_OUT_FOLDER')

    if not os.path.exists(IMAGE_OUT_FOLDER):
        os.makedirs(IMAGE_OUT_FOLDER)


def main():
    print datetime.datetime.now()
    loadConfig("config.json")

    html = getMainPage()
    uriList = parseMainPage(html)
    uriList = imageResolution(uriList)
    # print uriList
    imageNames = getImages(uriList)
    if len(imageNames) > 0:
        changeBackground(IMAGE_OUT_FOLDER + "/" + imageNames[0])



if __name__ == '__main__':
    main()
