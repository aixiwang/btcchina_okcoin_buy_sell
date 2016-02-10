#---------------------------------------------------------------------------------------------
# jy_btcchina.py -- a console tool to do buy/sell for btcchina
#
# BSD license is applied to this code
# Copyright by Aixi Wang (aixi.wang@hotmail.com)
#
#---------------------------------------------------------------------------------------------

import sys
import time
import os
import commands
import btcchina

access_key='xxx'
secret_key='xxx'
    
class _Getch:
    """Gets a single character from standard input.  Does not echo to the
screen."""
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): return self.impl()


class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno(), termios.TCSANOW)
            ch = sys.stdin.read(1)
            sys.stdout.write(ch)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()


getch = _Getch()

#-----------------------
# show_usage
#-----------------------
def show_usage():
    print '---------------------------------------------------------------------'
    print 'a or b: buy, q or s: sell, blank space: info, c: change_unit, x: exit'
    print '---------------------------------------------------------------------'    
#-------------------
# readfile
#-------------------
def readfile(filename):
    f = file(filename,'rb')
    fs = f.read()
    f.close()
    return fs
#-------------------
# writefile
#-------------------
def writefile(filename,content):
    f = file(filename,'wb')
    fs = f.write(content)
    f.close()
    return

#-------------------
# writefile2
#-------------------
def writefile2(filename,content):
    f = file(filename,'ab')
    fs = f.write(content)
    f.close()
    return    
#-------------------
# has_file
#-------------------    
def has_file(filename):
    if os.path.exists(filename):
        return True
    else:
        return False
 
#-------------------
# remove_file
#-------------------   
def remove_file(filename):
    if has_file(filename):
        os.remove(filename)
        
#-------------------
# get_shellcmd_output
#-------------------
def get_shellcmd_output(shell_cmd):
    return commands.getstatusoutput(shell_cmd)    


#-------------------------------
# buy_market
#-------------------------------   
def buy_market(access_key,secret_key,price,amount):
    bc = btcchina.BTCChina(access_key,secret_key)
    i = 3
    ret_code = -1
    while i > 0 and ret_code < 0:
        i = i -1
        ret_code,resp = bc.buy(price,amount)
        if ret_code == 0:
            return ret_code,resp
        time.sleep(1)
    return -1,''
#-------------------------------
# sell_market
#-------------------------------   
def sell_market(access_key,secret_key,price,amount):
    bc = btcchina.BTCChina(access_key,secret_key)

    i = 3
    ret_code = -1
    while i > 0 and ret_code < 0:
        i = i -1
        ret_code,resp = bc.sell(price,amount)
        if ret_code == 0:
            return ret_code,resp
        time.sleep(1)
    return -1,''
    
#-------------------------------
# get_btc_cny
#-------------------------------     
def get_btc_cny(access_key,secret_key):
    bc = btcchina.BTCChina(access_key,secret_key)

    i = 3
    ret_code = -1
    while i > 0 and ret_code < 0:
        i = i -1
        ret_code,resp = bc.get_account_info()
        if ret_code == 0:
            return ret_code,float(resp['balance']['btc']['amount']),float(resp['balance']['cny']['amount'])
        time.sleep(1)
    return -1,0,0
    
#-------------------
# main
#-------------------   
    
if has_file('buy_sell_unit.txt'):
    BUY_SELL_UNIT = readfile('buy_sell_unit.txt')
    print 'BUY_SELL_UNIT:',BUY_SELL_UNIT
else:
    BUY_SELL_UNIT = raw_input('\r\nPlease input buy_sell_unit(BTC):')
    print 'BUY_SELL_UNIT:',BUY_SELL_UNIT
    writefile('buy_sell_unit.txt',str(BUY_SELL_UNIT))

    
show_usage()
i = 0


    

while True:
    i += 1
    ch = getch()
    #sys.stdout.write(ch)
    time.sleep(0.01)
    #if i % 100 == 0:
    if ch == 'a' or ch == 'b':
        print 'Buy ' + BUY_SELL_UNIT

        ret,resp = buy_market(access_key,secret_key,None,float(BUY_SELL_UNIT))
        print 'ret:',ret,' resp:',resp
        
        writefile2('do.txt','buy ' + BUY_SELL_UNIT + '->' + str(resp) + '\r\n')
    elif ch == 'q' or ch == 's':
        ret,resp = sell_market(access_key,secret_key,None,float(BUY_SELL_UNIT))
        print 'ret:',ret,' resp:',resp
        writefile2('do.txt','sell ' + BUY_SELL_UNIT + '->'  + str(resp) + '\r\n')

    elif ch == 'e' or ch == 'd' or ch == ' ':
        ret,v = btcchina.get_btcchina()
        #print 'ret:',ret,' price:',v
        if (ret == 0):
            ret,b,c = get_btc_cny(access_key,secret_key)
            if (ret == 0):
                s2 = ' btc:' + str(b) + ' cny:' + str(c) + ' btc+cny:' + str(b*float(v) + c)
                print s2
                writefile2('do.txt','info ->' + str(s2) + '\r\n')
            else:
                print 'get btc/cny error'
        else:
            print 'get price error'
    elif ch == 'c':
        BUY_SELL_UNIT = raw_input('\r\nPlease input buy_sell_unit(BTC):')
        print 'BUY_SELL_UNIT:',BUY_SELL_UNIT
        
    elif ch == 'x':
        print 'exit'
        sys.exit(0)
    else:
        show_usage()


