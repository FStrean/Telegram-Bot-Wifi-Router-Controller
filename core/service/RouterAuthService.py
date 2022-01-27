import requests
import re
import configparser

from core.config.AuthInfo import *
from core.assist.securityJs import *

from core.assist.http import sendRequest

config = configparser.ConfigParser()
config.read('config/url.ini')
    
class RouterAuthService:
    def __init__(self, authInfo : AuthInfo):
        self.authInfo = authInfo
    
    def auth(self, login, password):
        encoder, encrypter = getEncoder(), getEncrypter()
        nn, ee = getKeys()
        
        login = encrypter.call('RsaEncrypt', login, nn, ee)
        password = encoder.call('Base64Encoding', password)
        password = encrypter.call('RsaEncrypt', password, nn, ee)
        
        headers = {'Referer' : config['Router']['url']}
        response = sendRequest(requests.post, 
                               url=config['Router']['url'] + config['Login']['url'].format(login, password), headers=headers)
        
        self.authInfo.setJSessionId(response.cookies)
        self.authInfo.setTokenId(getToken(self.authInfo))
        self.authInfo.setNnKey(nn)
        self.authInfo.setEeKey(ee)
    
    def logout(self):
        headers = {'TokenID' : self.authInfo.tokenId, 
                   'Referer' : config['Router']['url'],
                   'Content-Type' : 'text/plain'}
        
        response = sendRequest(requests.post, 
                    url=config['Router']['url'] + config['Logout']['url'],
                    headers=headers, 
                    cookies=self.authInfo.jSessionId, 
                    data=config['Logout']['command'] + '\r\n')
        
        
def getKeys():
    headers = {'Referer' : config['Router']['url']}
    response = sendRequest(requests.post, 
                           url=config['Router']['url'] + config['Keys']['url'], 
                           headers=headers)
    nn = re.findall(b'nn="(.*)"', response.content)[0].decode('utf-8')
    ee = re.findall(b'ee="(\d*)"', response.content)[0].decode('utf-8')
    
    return nn, ee

def getToken(authInfo : AuthInfo):
    headers = {'Referer' : config['Router']['url']}
    response = sendRequest(requests.get, 
                           url=config['Router']['url'], 
                           headers=headers, 
                           cookies=authInfo.jSessionId)
    
    return re.findall(b'<script type="text\/javascript">var token="(.*)";<\/script>', 
                      response.content)[0].decode('utf-8')