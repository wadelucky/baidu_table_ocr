#!encoding:utf-8

import requests
import base64
import os
import time
import re

'''
The table ocr is only used for free 50 times a day.
This link is the original instruction: https://ai.baidu.com/ai-doc/OCR/ik3h7xyxf
'''


def get_access_token(client_id, secret_key):
    """
    Every access token is valid for a month, so you need to get a new one in case of expiration.
    You may find instructions from https://ai.baidu.com/ai-doc/REFERENCE/Ck3dwjgn3
    @param client_id: The client id of your account
    @param secret_key: The secret key of your account

    @return: the access token which is valid for now
    """

    host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=' 
    + client_id + '&client_secret=' + secret_key

    response = requests.get(host)
    if response.status_code == 200:  # successfully obtained
        return(response.json()['access_token'])
    else:
        raise('Something is not going well.')


def send_img(filename, token):
    """
    Send the img and get request_id to download the result later.
    @param filename: your image which contains a table(or not)
    @param token: your access_token

    @return: a json format dict which contains the request_id
    """

    request_url = "https://aip.baidubce.com/rest/2.0/solution/v1/form_ocr/request"

    f = open(filename, 'rb')
    img = base64.b64encode(f.read())
    params = {"image":img, "request_type":"excel"}

    request_url = request_url + "?access_token=" + token
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    response = requests.post(request_url, data=params, headers=headers)
    if response.status_code == 200:  # successfully sent
        return response.json()
    else:
        raise('Sending failed.')

def receive_excel(send_json, token):
    """
    Use the request_id to download the result, you shall see the file
    in the same directory.
    @param send_json: a json format dict
    @param token: your access_token

    """

    request_url = 'https://aip.baidubce.com/rest/2.0/solution/v1/form_ocr/get_request_result'
    request_url = request_url + "?access_token=" + token

    headers = {'content-type':'application/x-www-form-urlencoded'}
    params = {'request_id': send_json['result'][0]['request_id']}  # the send_json has an odd structure

    response = requests.post(request_url, data=params, headers=headers)
    if response.status_code == 200:
        print (response.json())
        # use regex to get the URI
        temp = re.findall(r'[\S]+.xls', response.json()['result']['result_data'])[0]
        os.system('curl -O ' +  temp)  # use curl -O to download the file
    else:
        raise('Download failed.')


if __name__ == '__main__':
    current_token = get_access_token('your_client_id', 'your_secret_key')  # use your own stuff
    send_json = send_img('hello_world.png', current_token)  # use your own image filename
    time.sleep(5)  # It will take some time to finish ocr, so please be patient.
    receive_excel(send_json, current_token)
