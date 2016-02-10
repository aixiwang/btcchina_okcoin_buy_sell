# -*- coding: utf-8 -*-
# OKCoin api
# https://www.okcoin.cn/about/publicApi.do
#
# Contributers: 
# Aixi Wang             aixi.wang@hotmail.com
#----------------------------------------------------
#错误代码 详细描述
#10000 必选参数不能为空
#10001 用户请求过于频繁
#10002 系统错误
#10003 未在请求限制列表中,稍后请重试
#10004 IP限制不能请求该资源
#10005 密钥不存在
#10006 用户不存在
#10007 签名不匹配
#10008 非法参数
#10009 订单不存在
#10010 余额不足
#10011 买卖的数量小于BTC/LTC最小买卖额度
#10012 当前网站暂时只支持btc_cny ltc_cny
#10013 此接口只支持https请求
#10014 下单价格不得≤0或≥1000000
#10015 下单价格与最新成交价偏差过大
#10216 非开放API
#----------------------------------------------------
import sys
import httplib
import urllib
import json
import md5
import time
import urllib2
#from btcdb import *

#from global_setting import *
#-------------------------------------
# get_okcoin_last
#-------------------------------------
class OKCoin():
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
       
    def __signature(self, params):
        s = ''
        #print 'signature params:',params
        for k in sorted(params.keys()):
            s += k + '=' + str(params[k]) + '&'
        data = s + 'secret_key=' + self.api_secret
        return md5.new(data).hexdigest().upper()

    def __tapi_call(self, method, params={}):
        #print 'api-key:' + self.api_key
        #print '__tapi_call params:',params
        params["api_key"] = self.api_key
        
        
        params["sign"] = self.__signature(params)
        headers = {
            "Content-type" : "application/x-www-form-urlencoded",
        }
        #print '__tapi_call:',params
        conn = httplib.HTTPSConnection("www.okcoin.cn", timeout=5)
        params = urllib.urlencode(params)
        s = "/api/v1/%s.do" % method
        #print 's:',s
        #print 'params:',params
        #print 'headers:',headers
        conn.request("POST", s, params, headers)
        response = conn.getresponse()
        data = json.load(response)
        #print 'data:',data
        conn.close()
        return data
        
    def __api_call(self, method, pair):
        conn = httplib.HTTPSConnection("www.okcoin.cn", timeout=5)
        conn.request("GET", "/api/v1/%s.do?symbol=%s" % (method, pair))
        response = conn.getresponse()       
        data = json.load(response)
        conn.close()
        return data

    def get_account_info(self): 
        resp = self.__tapi_call('userinfo',{})
        #print 'resp:',resp
        if resp["result"] == True:
            return 0, float(resp["info"]["funds"]["free"]["cny"]), float(resp["info"]["funds"]["free"]["btc"])
        else:
            return -1,0,0
            
    def get_order_info(self, order_id):
        params = { "symbol": "btc_cny", "order_id" : order_id }
        data = self.__tapi_call('getorder', params)
        
        if data["result"] == True:
            order_status = data["orders"][0]["status"]
            print "order_status =" + str(order_status)
            if (order_status == 2):
                return 0, order_status
            else:
                return -1, 0
        elif data["result"] == False:
            return int(data["errorCode"])*(-1), 0
            
    def trade(self, tpair, ttype, price, amount):
        params = {
            "symbol" : tpair,
            "type"   : ttype,
            "rate"   : price,
            "amount" : amount
        }
        result = self.__tapi_call('trade', params)
        #print str(result)
        return result

    #--------------------------------
    # btc_buy
    #--------------------------------   
    def buy(self, price, amount):
        print '======> ok buy, price=%f, amount=%f' % (price, amount)
        data = self.trade("btc_cny", "buy", price, amount)
        if data["result"] == True:
            #print str(data)
            return 0, data["order_id"]
        else:
            return int(data["error_code"])*(-1), 0
 
    #--------------------------------
    # buy_market
    #--------------------------------   
    def buy_market(self, price):
        print '======> ok buy_market, price=%f' % (price)
        params = {
            'symbol' : 'btc_cny',
            'type'   : 'buy_market',
            'price'   : price,
        }
        data = self.__tapi_call('trade', params)
        print data
        
        if data["result"] == True:
            return 0, data["order_id"]
        else:
            return int(data["error_code"])*(-1), 0

    #--------------------------------
    # buy_market2
    #--------------------------------   
    def buy_market2(self, amount):
        print '======> ok buy_market2, price=%f' % (amount)
        
        ret_code, p = self.get_lastprice()
        if ret_code >= 0:
            price = amount*(p+1)
            
            params = {
                'symbol' : 'btc_cny',
                'type'   : 'buy_market',
                'price'   : price,
            }
            data = self.__tapi_call('trade', params)
            print data
            
            if data["result"] == True:
                return 0, data["order_id"]
            else:
                return int(data["error_code"])*(-1), 0
        else:
            return ret_code, 0
    #--------------------------------
    # sell_market2
    #--------------------------------   
    def sell_market2(self, amount):
        print '======> ok sell_market2, amount=%f' % (amount)
        params = {
            'symbol' : 'btc_cny',
            'type'   : 'sell_market',
            'amount' : amount
        }
        data = self.__tapi_call('trade', params)
        
        if data["result"] == True:
            return 0, data["order_id"]
        else:
            return int(data["error_code"])*(-1), 0
            
    #--------------------------------
    # btc_sell
    #--------------------------------
    def sell(self, price, amount):
        print '======> ok sell, price=%f, amount=%f' % (price, amount)    
        data = self.trade("btc_cny", "sell", price, amount)
        if data["result"] == True:
            return 0, data["order_id"]
        else:
            return int(data["error_code"])*(-1), 0
   
    #--------------------------------
    # cancel_order
    #--------------------------------
    def cancel_order(self, order_id):
        params = { "symbol": "btc_cny", "order_id" : order_id }
        data = self.__tapi_call('cancelorder', params)
        print str(data)
        if data["result"] == True:
            return 0, data["order_id"]
        else:
            return int(data["error_code"])*(-1), 0
            
    #--------------------------------
    # get_okcoin_last
    #--------------------------------
    def get_lastprice(self):
        try:
            f = urllib2.urlopen("https://www.okcoin.cn/api/v1/ticker.do" + '?' + str(time.time()))
            s = f.read()
            f.close()

            if (s[0] != '{'):
                #print 'get_okcoin --- invalid data received!'
                return -2,0
            else:
                price = json.loads(s)
                price_time = price["date"]
                price_high = price["ticker"]["high"]
                price_low = price["ticker"]["low"]
                price_buy = price["ticker"]["buy"]
                price_sell = price["ticker"]["sell"]
                price_last = price["ticker"]["last"]
                price_vol = price["ticker"]["vol"]
                #print "price_last:" + price_last
                return 0, float(price_last)
        except:
            return 0, 0

#================================================
#                   M A I N
#================================================
if __name__ == "__main__":
    global okcoin_id,okcoin_key
    #try:
    if 1:
        #print 'test OKCoin api...'
        okcoin_id = 'xxx'
        okcoin_key = 'xxx'
        okcoin = OKCoin(okcoin_id,okcoin_key)
        ret_code, p = okcoin.get_lastprice()
        
        print ret_code,p
        
        if (sys.argv[1] == "accountinfo"):          
            ret_code, q, b = okcoin.get_account_info()
            if (ret_code >= 0):
                print 'okcoin_accountinfo=%.2f,%.4f' % (q,b)
            else:
                print 'ret_code',ret_code
                print 'okcoin_accountinfo=%f,%f' % (-1,-1)
 
        elif (sys.argv[1] == "buy_market"):
            ret_code, p = okcoin.get_lastprice()
            print ret_code,p
            ret_code, id = okcoin.buy_market2(float(sys.argv[2]))
            print 'ret_code:',ret_code
            print 'id:',id

        elif (sys.argv[1] == "sell_market"):       
            ret_code, id = okcoin.sell_market2(float(sys.argv[2]))
            print 'ret_code:',ret_code
            print 'id:',id

               
    #except Exception,e:
    #    print e
    #    print '-1'
