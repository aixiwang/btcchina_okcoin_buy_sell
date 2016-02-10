#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
import time
import re
import hmac
import hashlib
import base64
import httplib
import json
import sys
import urllib2

class BTCChina():
    def __init__(self,access=None,secret=None):
        self.access_key=access
        self.secret_key=secret
        self.conn=httplib.HTTPSConnection("api.btcc.com")
 
    def _get_tonce(self):
        return int(time.time()*1000000)
 
    def _get_params_hash(self,pdict):
        pstring=""
        # The order of params is critical for calculating a correct hash
        fields=['tonce','accesskey','requestmethod','id','method','params']
        for f in fields:
            if pdict[f]:
                if f == 'params':
                    # Convert list to string, then strip brackets and spaces
                    # probably a cleaner way to do this
                    param_string=re.sub("[\[\] ]","",str(pdict[f]))
                    param_string=re.sub("'",'',param_string)
                    param_string=re.sub("True",'1',param_string)
                    param_string=re.sub("False",'',param_string)
                    param_string=re.sub("None",'',param_string)
                    pstring+=f+'='+param_string+'&'
                else:
                    pstring+=f+'='+str(pdict[f])+'&'
            else:
                pstring+=f+'=&'
        pstring=pstring.strip('&')
 
        # now with correctly ordered param string, calculate hash
        phash = hmac.new(self.secret_key, pstring, hashlib.sha1).hexdigest()
        return phash
 
    def _private_request(self,post_data):
        try:
            #fill in common post_data parameters
            tonce=self._get_tonce()
            post_data['tonce']=tonce
            post_data['accesskey']=self.access_key
            post_data['requestmethod']='post'
     
            # If ID is not passed as a key of post_data, just use tonce
            if not 'id' in post_data:
                post_data['id']=tonce

            pd_hash=self._get_params_hash(post_data)
     
            # must use b64 encode        
            auth_string='Basic '+base64.b64encode(self.access_key+':'+pd_hash)
            headers={'Authorization':auth_string,'Json-Rpc-Tonce':str(tonce)}
     
            #post_data dictionary passed as JSON
            #print 'post_data:',json.dumps(post_data)
            #print 'headers:',headers
            self.conn.request("POST",'/api_trade_v1.php',json.dumps(post_data),headers)
            response = self.conn.getresponse()
     
            # check response code, ID, and existence of 'result' or 'error'
            # before passing a dict of results
            if response.status == 200:
                # this might fail if non-json data is returned
                resp_dict = json.loads(response.read())
     
                # The id's may need to be used by the calling application,
                # but for now, check and discard from the return dict
                if str(resp_dict['id']) == str(post_data['id']):
                    if 'result' in resp_dict:
                        return 0,resp_dict['result']
                    elif 'error' in resp_dict:
                        return 0,resp_dict['error']
            else:
                # not great error handling....
                print "status:",response.status
                print "reason:",response.reason
     
            return -1,0
        except:
            print '_private_request exception'
            return -2,0
 
    '''
    get account info, return
        {
          "result": {
            "profile": {
              "username": "btc",
              "trade_password_enabled": true,
              "otp_enabled": true,
              "trade_fee": 0,
              "trade_fee_cnyltc": 0,
              "trade_fee_btcltc": 0,
              "daily_btc_limit": 10,
              "daily_ltc_limit": 300,
              "btc_deposit_address": "123myZyM9jBYGw5EB3wWmfgJ4Mvqnu7gEu",
              "btc_withdrawal_address": "123GzXJnfugniyy7ZDw3hSjkm4tHPHzHba",
              "ltc_deposit_address": "L12ysdcsNS3ZksRrVWMSoHjJgcm5VQn2Tc",
              "ltc_withdrawal_address": "L23GzXJnfugniyy7ZDw3hSjkm4tHPHzHba",
              "api_key_permission": 3
            },
            "balance": {
              "btc": {
                "currency": "BTC",
                "symbol": "\u0e3f",
                "amount": "100.00000000",
                "amount_integer": "10000000000",
                "amount_decimal": 8
              },
              "ltc": {
                "currency": "LTC",
                "symbol": "\u0141",
                "amount": "0.00000000",
                "amount_integer": "0",
                "amount_decimal": 8
              },
              "cny": {
                "currency": "CNY",
                "symbol": "\u00a5",
                "amount": "50000.00000",
                "amount_integer": "5000000000",
                "amount_decimal": 5
              }
            },
            "frozen": {
              "btc": {
                "currency": "BTC",
                "symbol": "\u0e3f",
                "amount": "0.00000000",
                "amount_integer": "0",
                "amount_decimal": 8
              },
              "ltc": {
                "currency": "LTC",
                "symbol": "\u0141",
                "amount": "0.00000000",
                "amount_integer": "0",
                "amount_decimal": 8
              },
              "cny": {
                "currency": "CNY",
                "symbol": "\u00a5",
                "amount": "0.00000",
                "amount_integer": "0",
                "amount_decimal": 5
              }
            }
            "loan": {
              "btc": {
                "currency":"BTC",
                "symbol":"\u0e3f",
                "amount":"0.00000000",
                "amount_integer":"0",
                "amount_decimal":8
              },
              "cny":{
                "currency":"CNY",
                "symbol":"\u00a5",
                "amount":"0.00000",
                "amount_integer":"0",
                "amount_decimal":5
              }
            }
          },
          "id": "1"
        }
    '''
    def get_account_info(self,post_data={}):
        post_data['method']='getAccountInfo'
        post_data['params']=[]
        return self._private_request(post_data)
 
    def get_market_depth2(self,limit=10, market="btccny", post_data={}):
        post_data['method']='getMarketDepth2'
        post_data['params']=[limit, market]
        return self._private_request(post_data)
 
    def buy(self, price, amount, market="btccny", post_data={}):
        amountStr = "{0:.4f}".format(round(amount,4))
        post_data['method']='buyOrder2'
        if price == None:
            priceStr = None
        else:
            priceStr = "{0:.4f}".format(round(price,4))
        post_data['params']=[priceStr, amountStr, market]
        return self._private_request(post_data)
 
    def sell(self, price, amount, market="btccny", post_data={}):
        amountStr = "{0:.4f}".format(round(amount,4))
        post_data['method']='sellOrder2'
        if price == None:
            priceStr = None
        else:
            priceStr = "{0:.4f}".format(round(price,4))
        post_data['params']=[priceStr, amountStr, market]
        return self._private_request(post_data)
 
    def cancel(self,order_id, market = "btccny", post_data={}):
        post_data['method']='cancelOrder'
        post_data['params']=[order_id, market]
        return self._private_request(post_data)
 
    def request_withdrawal(self,currency,amount,post_data={}):
        post_data['method']='requestWithdrawal'
        post_data['params']=[currency,amount]
        return self._private_request(post_data)
 
    def get_deposits(self,currency='BTC',pending=True,post_data={}):
        post_data['method']='getDeposits'
        post_data['params']=[currency,pending]
        return self._private_request(post_data)
 
    def get_orders(self,id=None,open_only=True,market="btccny",details=True,post_data={}):
        # this combines getOrder and getOrders
        if id is None:
            post_data['method']='getOrders'
            post_data['params']=[open_only, market]
        else:
            post_data['method']='getOrder'
            post_data['params']=[id, market,details]
        return self._private_request(post_data)
 
    def get_withdrawals(self,id='BTC',pending=True,post_data={}):
        # this combines getWithdrawal and getWithdrawals
        try:
            id = int(id)
            post_data['method']='getWithdrawal'
            post_data['params']=[id]
        except:
            post_data['method']='getWithdrawals'
            post_data['params']=[id,pending]
        return self._private_request(post_data)
 
    def get_transactions(self,trans_type='all',limit=10,post_data={}):
        post_data['method']='getTransactions'
        post_data['params']=[trans_type,limit]
        return self._private_request(post_data)

#-------------------------------------
# get_btcchina
#-------------------------------------
def get_btcchina():
    try:
        f = urllib2.urlopen("https://data.btcchina.com/data/ticker?market=btccny")
        s = f.read()
        f.close()

        if (s[0] != '{'):
            print 'get_btcchina --- invalid data received!'
            return -2,0
        else:
            price = json.loads(s)
            price_time = price["ticker"]["date"]
            price_high = price["ticker"]["high"]
            price_low = price["ticker"]["low"]
            price_buy = price["ticker"]["buy"]
            price_sell = price["ticker"]["sell"]
            price_last = price["ticker"]["last"]
            price_vol = price["ticker"]["vol"]
            return 0, float(price_last)
    except:
        return -1,0   
#================================================
#                   M A I N
#================================================
if __name__ == "__main__":
    access_key="x"
    secret_key="x"


    bc = BTCChina(access_key,secret_key)

 
    ''' These methods have no arguments '''
    #result = bc.get_account_info()
    #print result
     
    #result = bc.get_market_depth2()
    #print result
     
    # NOTE: for all methods shown here, the transaction ID could be set by doing
    #result = bc.get_account_info(post_data={'id':'stuff'})
    #print result
     
    ''' buy and sell require price (CNY, 5 decimals) and amount (LTC/BTC, 8 decimals) '''
    #result = bc.buy(500,1)
    #print result
    #result = bc.sell(500,1)
    #print result
     
    ''' cancel requires id number of order '''
    #result = bc.cancel(2)
    #print result
     
    ''' request withdrawal requires currency and amount '''
    #result = bc.request_withdrawal('BTC',0.1)
    #print result
     
    ''' get deposits requires currency. the optional "pending" defaults to true '''
    #result = bc.get_deposits('BTC',pending=False)
    #print result
     
    ''' get orders returns status for one order if ID is specified,
        otherwise returns all orders, the optional "open_only" defaults to true '''
    #result = bc.get_orders(2)
    #print result
    #result = bc.get_orders(open_only=True)
    #print result
     
    ''' get withdrawals returns status for one transaction if ID is specified,
        if currency is specified it returns all transactions,
        the optional "pending" defaults to true '''
    #result = bc.get_withdrawals(2)
    #print result
    #result = bc.get_withdrawals('BTC',pending=True)
    #print result
     
    ''' Fetch transactions by type. Default is 'all'. 
        Available types 'all | fundbtc | withdrawbtc | fundmoney | withdrawmoney | 
        refundmoney | buybtc | sellbtc | tradefee'
        Limit the number of transactions, default value is 10 '''
    #result = bc.get_transactions('all',10)
    #print result
    if len(sys.argv) == 2:
        if (sys.argv[1] == "accountinfo"):
            ret_code,resp = bc.get_account_info()
            ret_code2,v = get_btcchina()
            if ret_code == 0 and ret_code2 == 0:
                try:
                
                    b = round(float(resp['balance']['btc']['amount']),4)
                    q = round(float(resp['balance']['cny']['amount']),2)
                    q2 = round(b*v + q)
                    print str(ret_code) + '\t' + 'btc=' + str(b) + '\t\t' + 'cny=' + str(q) + '\t\t' + 'balance=' + str(q2)
                except:
                    print '-1\t0\t0\t0'

    if len(sys.argv) >= 3:
        if (sys.argv[1] == "buy"):
            ret_code,resp = bc.buy(None,float(sys.argv[2]))
            print str(ret_code) + '\t'+ str(resp)
        elif (sys.argv[1] == "sell"):
            ret_code,resp = bc.sell(None,float(sys.argv[2]))
            print str(ret_code) + '\t'+str(resp)
    
 
