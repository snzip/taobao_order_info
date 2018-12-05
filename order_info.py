
# coding: utf-8

import requests
import re
import json
import pandas as pd
import time
import datetime
from tkinter import *
from tkinter import messagebox
import sys

from taobao_climber import login_run

def conversion(cookie,queryBizType,commentStatus,dateBegin,dateEnd,auctionStatus,sellerNick,tradeDissension,time_i):
    root.destroy()
# 订单类型
    if queryBizType == "机票订单":
        queryBizType = 1400
    elif queryBizType == "数字订单":
        queryBizType = 1500
    elif queryBizType == "理财订单":
        queryBizType = 3000
    elif queryBizType == "网游订单":
        queryBizType = 900
    elif queryBizType == "酒店订单":
        queryBizType = 710
    elif queryBizType == "保险订单":
        queryBizType = 1102
    elif queryBizType == "企采订单":
        queryBizType = "corpMarket"
    else:
        queryBizType = ""

# 评价状态
    if commentStatus == "双方已评":
        commentStatus = "ALL_COMMENT"
    elif commentStatus == "需我评价":
        commentStatus = "I_HAS_NOT_COMMENT"
    elif commentStatus == "我已评价":
        commentStatus = "I_HAS_COMMENT"
    elif commentStatus == "对方已评":
        commentStatus = "OTHER_HAS_COMMENT"
    else:
        commentStatus = "ALL"

# 起始时间
    try:
        online_dt = datetime.datetime.strptime(dateBegin, "%Y-%m-%d %H:%M:%S")
        dateBegin = int(time.mktime(online_dt.timetuple()))
        dateBegin = dateBegin * 1000
    except:
        dateBegin = 0

# 结束时间
    try:
        online_dt = datetime.datetime.strptime(dateEnd, "%Y-%m-%d %H:%M:%S")
        dateEnd = int(time.mktime(online_dt.timetuple()))
        dateEnd = dateEnd * 1000
    except:
        dateEnd = 0

# 交易状态
    if auctionStatus == "等待买家付款":
        auctionStatus = "NOT_PAID"
    elif auctionStatus == "付款确认中":
        auctionStatus = "PAY_PENDING"
    elif auctionStatus == "买家已付款":
        auctionStatus = "PAID"
    elif auctionStatus == "卖家已发货":
        auctionStatus = "SEND"
    elif auctionStatus == "交易成功":
        auctionStatus = "SUCCESS"
    elif auctionStatus == "交易关闭":
        auctionStatus = "DROP"
    elif auctionStatus == "退款中的订单":
        auctionStatus = "REFUNDING"
        
# 卖家昵称
    sellerNick = sellerNick
    
# 售后服务
    if tradeDissension == "已投诉":
        tradeDissension = "ACCUSED"
    elif tradeDissension == "退款中":
        tradeDissension ="REFUNDING"
    else:
        tradeDissension = "ALL"

    run(cookie,queryBizType,commentStatus,dateBegin,dateEnd,auctionStatus,sellerNick,tradeDissension,time_i)
        
def get_id(pageNum,cookie,queryBizType,commentStatus,dateBegin,dateEnd,auctionStatus,sellerNick,tradeDissension):
    url = "https://buyertrade.taobao.com/trade/itemlist/asyncBought.htm?action=itemlist/BoughtQueryAction&event_submit_do_query=1&_input_charset=utf8"
    headers = {
        "cookie": cookie,
        "origin": "https://buyertrade.taobao.com",
        "referer": "https://buyertrade.taobao.com/trade/itemlist/list_bought_items.htm",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36"
    }
    if pageNum == 1:
        prePageNo = 1
    else:
        prePageNo = pageNum - 1
    data = {
        "buyerNick": "",
        "dateBegin": str(dateBegin),  # 开始日期：时间戳
        "dateEnd": str(dateEnd),    # 结束日期：时间戳
        "lastStartRow": "",
        "logisticsService": "",
        "options": 0,
        "orderStatus":"", 
        "pageNum": pageNum,
        "pageSize": 15,
        "queryBizType": "",    #订单类型 ："":全部、1400：机票订单、1500：数字订单、3000：理财订单、900：网游订单、710：酒店订单、1102：保险订单、"corpMarket":企采订单
        "queryOrder": "desc",
        "rateStatus": "",
        "refund": "",
        "sellerNick":sellerNick, 
        "commentStatus": "ALL", # 评价状态："ALL":全部、"ALL_COMMENT"：双方已评、"I_HAS_NOT_COMMENT":需我评价、"I_HAS_COMMENT":我以评价、"OTHER_HAS_COMMENT":对方已评
        "auctionStatus": auctionStatus,# 交易状态："ALL":全部、"NOT_PAID"：等待买家付款、"PAY_PENDING"：付款确认中、"PAID":买家已付款、"SEND":卖家已发货、"SUCCESS":交易成功、"DROP":交易关闭、"REFUNDING":退款中的订单
        "tradeDissension":tradeDissension ,# 售后服务："ALL":全部、 "ACCUSED":已投诉、"REFUNDING":退款中
        "prePageNo": prePageNo
    }
    response = requests.post(url,headers=headers,data=data)
    for i in response.json()["mainOrders"]:
        yield i["id"]

def get_result_tmail(response):
    detail_re = re.compile(r"var detailData = (.*?)</script>",re.DOTALL)
    li = detail_re.findall(response)
    return json.loads(li[0])
def get_result_taobao(response):
    detail_re = re.compile(r"var data = (.*?)</script>",re.DOTALL)
    li = detail_re.findall(response)
    a = li[0].strip().lstrip("JSON.parse('").strip().rstrip("');").replace('\\"','\"')
    return json.loads(a)


def get_detail_tmail(result):
    # basic
    try:
        address = result["basic"]["lists"][0]["content"][0]["text"]
    except:
        address = None
    try:
        buy_message = result["basic"]["lists"][1]["content"][0]["text"]
    except:
        buy_message = None
    try:
        order_number = result["basic"]["lists"][2]["content"][0]["text"]
    except:
        order_number = None

    # 商家信息
    try:
        seller_name = re.findall(r"title=(.*?)>",result["basic"]["lists"][3]["content"][0]["text"])[0]
    except:
        seller_name = None
    try:
        rel_name = result["basic"]["lists"][3]["content"][1]["moreList"][0]["content"][0]["text"]
    except:
        rel_name = None
    try:
        city = result["basic"]["lists"][3]["content"][1]["moreList"][1]["content"][0]["text"]
    except:
        city = None
    try:
        seller_mob = result["basic"]["lists"][3]["content"][1]["moreList"][2]["content"][0]["text"]
    except:
        seller_mob = None

    # 商品信息
    try:
        companyName = result["orders"]["list"][0]["logistic"]["content"][0]["companyName"]
    except:
        companyName = None
    try:
        mailNo = result["orders"]["list"][0]["logistic"]["content"][0]["mailNo"]
    except:
        mailNo = None
    try:
        url = result["orders"]["list"][0]["logistic"]["content"][0]["url"]
    except:
        url = None
    try:
        color_classification = result["orders"]["list"][0]["status"][0]["subOrders"][0]["itemInfo"]["skuText"][0]["content"][0]["text"]
    except:
        color_classification = None
    try:
        priceInfo = result["orders"]["list"][0]["status"][0]["subOrders"][0]["priceInfo"][0]["text"]
    except:
        priceInfo = None
    
    # 动作
    try:
        take_goods = result["stepbar"]["options"][0]["time"]
    except:
        take_goods = None
    try:
        payment_to_Alipay = result["stepbar"]["options"][1]["time"]
    except IndexError:
        payment_to_Alipay = None
    try:
        seller_deliver = result["stepbar"]["options"][2]["time"]
    except IndexError:
        seller_deliver = None
    try:
        confirmation_of_receipt = result["stepbar"]["options"][3]["time"]
    except IndexError:
        confirmation_of_receipt = None

    # 备忘
    try:
        memo = re.findall(r"<span>(.*?)</span>",result["overStatus"]["memo"][0]["content"][0]["text"])[0]
    except:
        memo = None
    try:
        statusInfo = result["overStatus"]["status"]["content"][0]["text"]
    except:
        statusInfo = None
    alipayAccount = None
    shipType = "快递"
    mail = None
    try:
        title = result["orders"]["list"][0]["status"][0]["subOrders"][0]["itemInfo"]["title"]
    except:
        title = "title"
    return {title:[address,buy_message,order_number,seller_name,rel_name,city,seller_mob,companyName,mailNo,url,color_classification,priceInfo,take_goods,payment_to_Alipay,seller_deliver,confirmation_of_receipt,memo,statusInfo,alipayAccount,shipType,mail]}

def get_detail_taobao(result):
    try:
        address = result["deliveryInfo"]["address"]   # 收货地址
    except:
        address = None
    buy_message = None
    try:
        shipType = result["deliveryInfo"]["shipType"]   # 快递类型
    except:
        shipType = None
    try:
        order_number = result["mainOrder"]["id"] # id
    except:
        order_number = None
    try:
        take_goods = result["orderBar"]["nodes"][0]["date"]
    except:
        take_goods = None
    try:
        payment_to_Alipay = result["orderBar"]["nodes"][1]["date"]
    except:
        payment_to_Alipay = None
    try:
        seller_deliver = result["orderBar"]["nodes"][2]["date"]
    except:
        seller_deliver = None
    try:
        confirmation_of_receipt = result["orderBar"]["nodes"][3]["date"]
    except:
        confirmation_of_receipt = None
    try:
        companyName = result["deliveryInfo"]["logisticsName"]
    except:
        companyName = None
    try:
        mailNo = result["deliveryInfo"]["logisticsNum"]
    except:
        mailNo = None
    try:
        url = result["deliveryInfo"]["asyncLogisticsUrl"]
    except:
        url = None
    # 卖家信息
    try:
        alipayAccount = result["mainOrder"]["seller"]["alipayAccount"]
    except:
        alipayAccount = None
    try:
        rel_name = result["mainOrder"]["seller"]["name"]
    except:
        rel_name = None
    try:
        city = result["mainOrder"]["seller"]["city"]
    except:
        city = None
    try:
        mail = result["mainOrder"]["seller"]["mail"]
    except:
        mail = None
    try:
        seller_mob = result["mainOrder"]["seller"]["phoneNum"]
    except:
        seller_mob = None
    try:
        seller_name = result["mainOrder"]["seller"]["nick"]
    except:
        seller_name = None
    # 订单状态
    try:
        statusInfo = result["mainOrder"]["statusInfo"]["text"]
    except:
        statusInfo = None
    #商品信息
    try:
        color_classification = result["mainOrder"]["subOrders"][0]["itemInfo"]["skuText"][0]["content"]
    except:
        color_classification = None
    try:
        title = result["mainOrder"]["subOrders"][0]["itemInfo"]["title"]
    except:
        title = "title"
    try:
        priceInfo = result["mainOrder"]["totalPrice"][0]["content"][0]["value"]
    except:
        priceInfo = None
    memo = None
    return {title:[address,buy_message,order_number,seller_name,rel_name,city,seller_mob,companyName,mailNo,url,color_classification,priceInfo,take_goods,payment_to_Alipay,seller_deliver,confirmation_of_receipt,memo,statusInfo,alipayAccount,shipType,mail]}


def run(cookie,queryBizType,commentStatus,dateBegin,dateEnd,auctionStatus,sellerNick,tradeDissension,time_i):
    
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9",
        "cookie": cookie,
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36"
    }
    details = {}
    for i in range(1,1000000000):
        fid = get_id(i,cookie,queryBizType,commentStatus,dateBegin,dateEnd,auctionStatus,sellerNick,tradeDissension)
        j = 0
        while True:
            try:
                id_ = next(fid)
                j += 1
                print(id_)
                detail_url = "https://trade.tmall.com/detail/orderDetail.htm?bizOrderId=" + id_
                response = requests.get(detail_url,headers=headers).text
                if "选择其中一个已登录的账户" not in response:
                    result = get_result_tmail(response)
                    detail = get_detail_tmail(result)
                    details.update(detail)
                    time.sleep(int(time_i))
                    continue
                detail_url = "https://trade.taobao.com/trade/detail/trade_order_detail.htm?biz_order_id=" + id_
                response = requests.get(detail_url,headers=headers).text
                if "选择其中一个已登录的账户" in response:
                    save(details)
                    messagebox.showerror("登录","请重新登录")
                    sys.exit()
                result = get_result_taobao(response)
                detail = get_detail_taobao(result)
                details.update(detail)

            except StopIteration:
                if j == 0:
                    return details
                break
            time.sleep(int(time_i))
    save(details)

def save(details):
    df = pd.DataFrame(details)
    columns=[
        "收货地址",
        "买家留言",
        "订单编号",
        "商家",
        "真实姓名",
        "城市",
        "联系方式",
        "快递",
        "运单号",
        "快递详情",
        "颜色分类",
        "商品价格",
        "拍下商品",
        "付款到支付宝",
        "卖家发货",
        "确认收货",
        "备忘",
        "订单状态",
        "卖家账户",
        "快递类型",
        "邮箱"
    ]
    df = df.T
    df.columns = columns
    df.to_excel("order_info.xlsx")

if __name__ == "__main__":
    cookie = login_run()
    
    root = Tk()
    root.title('订单导出')
    width = 800
    height = 400
    # 获取屏幕尺寸以计算布局参数，使窗口居屏幕中央
    screenwidth = root.winfo_screenwidth()
    screenheight = root.winfo_screenheight()
    alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
    root.geometry(alignstr)
    root.resizable(width=False, height=False)

    # 订单类型
    Label(root,text="订单类型").place(relx=0.1,rely=0.1)
    queryBizType = Entry(root)
    queryBizType.insert(0,"全部")
    queryBizType.place(relx=0.2,rely=0.1)

    # 评价状态
    Label(root,text="订单类型").place(relx=0.5,rely=0.1)
    commentStatus = Entry(root)
    commentStatus.insert(0,"全部")
    commentStatus.place(relx=0.6,rely=0.1)

    # 起始时间
    Label(root,text="起始时间").place(relx=0.1,rely=0.25)
    dateBegin = Entry(root)
    dateBegin.insert(0,"0")
    dateBegin.place(relx=0.2,rely=0.25)
    Label(root,text="(2018-11-20 11:31:22)").place(relx=0.2,rely=0.32)

    # 结束时间
    now = datetime.datetime.now()
    Label(root,text="结束时间").place(relx=0.5,rely=0.25)
    dateEnd = Entry(root)
    dateEnd.insert(0,now.strftime("%Y-%m-%d %H:%M:%S"))
    dateEnd.place(relx=0.6,rely=0.25)
    Label(root,text="(2018-11-20 11:31:22)").place(relx=0.6,rely=0.32)

    # 交易状态
    Label(root,text="交易状态").place(relx=0.1,rely=0.4)
    auctionStatus = Entry(root)
    auctionStatus.insert(0,"全部")
    auctionStatus.place(relx=0.2,rely=0.4)

    # 卖家昵称
    Label(root,text="卖家昵称").place(relx=0.5,rely=0.4)
    sellerNick = Entry(root)
    sellerNick.place(relx=0.6,rely=0.4)

    # 售后服务
    Label(root,text="售后服务").place(relx=0.1,rely=0.55)
    tradeDissension = Entry(root)
    tradeDissension.insert(0,"全部")
    tradeDissension.place(relx=0.2,rely=0.55)

    # 时间间隔
    Label(root,text="时间间隔/秒").place(relx=0.47,rely=0.55)
    time_i = Entry(root)
    time_i.insert(0,"3")
    time_i.place(relx=0.6,rely=0.55)

    Button(root,text="开始导出",width=10,command=(lambda : conversion(cookie,queryBizType.get(),commentStatus.get(),dateBegin.get(),dateEnd.get(),auctionStatus.get(),sellerNick.get(),tradeDissension.get(),time_i.get()))).place(relx=0.44,rely=0.8)

    root.mainloop()


