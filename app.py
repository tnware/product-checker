# https://github.com/tnware/product-checker
# by Tyler Woods
# coded for Bird Bot and friends
# https://tylermade.net
import requests
import time
import json
from datetime import datetime
import urllib.parse as urlparse
from urllib.parse import parse_qs
import csv
stockdict = {}
sku_dict = {}
bestbuylist = []
targetlist = []
walmartlist = []
bhlist = []
bbdict = {}

webhook_dict = {
"webhook_1": "https://discordapp.com/api/webhooks/.../.../webhook1",
"webhook_2": "https://discordapp.com/api/webhooks/.../.../webhook2",
"webhook_3": "https://discordapp.com/api/webhooks/.../.../webhook3"

}

urldict = {
"https://www.bhphotovideo.com/c/product/1496116-REG/nintendo_hadskabaa_switch_with_neon_blue.html": "webhook_1",
"https://www.target.com/p/nintendo-switch-with-neon-blue-and-neon-red-joy-con/-/A-77464001": "webhook_2",
"https://www.walmart.com/ip/Nintendo-Switch-Console-with-Gray-Joy-Con/994790027": "webhook_3"

}

class Target:

    def __init__(self, url, hook):
        self.url = url
        self.hook = hook
        webhook_url = webhook_dict[hook]
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        page = requests.get(url)
        al = page.text
        title = al[al.find('"twitter":{"title":') + 20 : al.find('","card')]
        #print(title)
        if "Temporarily out of stock" in page.text:
            print("[" + current_time + "] " + "Sold Out: (Target.com) " + title)
            stockdict.update({url: 'False'})
        else: 
            print("[" + current_time + "] " + "In Stock: (Target.com) " + title + " - " + url)
            slack_data = {'content': current_time + " " + title + " in stock at Target - " + url}
            if stockdict.get(url) == 'False':
                response = requests.post(
                webhook_url, data=json.dumps(slack_data),
                headers={'Content-Type': 'application/json'})
            stockdict.update({url: 'True'})
        #print(stockdict)

class BestBuy:

    def __init__(self, sku, hook):
        self.sku = sku
        self.hook = hook
        webhook_url = webhook_dict[hook]
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        url = "https://www.bestbuy.com/api/tcfb/model.json?paths=%5B%5B%22shop%22%2C%22scds%22%2C%22v2%22%2C%22page%22%2C%22tenants%22%2C%22bbypres%22%2C%22pages%22%2C%22globalnavigationv5sv%22%2C%22header%22%5D%2C%5B%22shop%22%2C%22buttonstate%22%2C%22v5%22%2C%22item%22%2C%22skus%22%2C" + sku + "%2C%22conditions%22%2C%22NONE%22%2C%22destinationZipCode%22%2C%22%2520%22%2C%22storeId%22%2C%22%2520%22%2C%22context%22%2C%22cyp%22%2C%22addAll%22%2C%22false%22%5D%5D&method=get"
        headers2 = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
        "cache-control": "max-age=0",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.69 Safari/537.36"
        }
        page = requests.get(url, headers=headers2)
        link = "https://www.bestbuy.com/site/" + sku + ".p?skuId=" + sku
        al = page.text
        search_string = '"skuId":"' + sku + '","buttonState":"'
        stock_status = al[al.find(search_string) + 33 : al.find('","displayText"')]
        product_name = sku_dict.get(sku)
        if stock_status == "SOLD_OUT":
            print("[" + current_time + "] " + "Sold Out: (BestBuy.com) " + product_name)
            stockdict.update({sku: 'False'})
        elif stock_status == "CHECK_STORES":
            print(product_name + " sold out @ BestBuy (check stores status)")
            stockdict.update({sku: 'False'})
        else: 
            if stock_status == "ADD_TO_CART":
                print("[" + current_time + "] " + "In Stock: (BestBuy.com) " + product_name + " - " + url)
                slack_data = {'content': current_time + " " + product_name + " In Stock @ BestBuy " + link}
                if stockdict.get(sku) == 'False':
                    response = requests.post(
                    webhook_url, data=json.dumps(slack_data),
                    headers={'Content-Type': 'application/json'})
                stockdict.update({sku: 'True'})
                #print(stockdict)

class Walmart:

    def __init__(self, url, hook):
        self.url = url
        self.hook = hook
        webhook_url = webhook_dict[hook]
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        page = requests.get(url)
        if page.status_code == 200:
            if "Add to cart" in page.text:
                print("[" + current_time + "] " + "In Stock: (Walmart.com) " + url)
                slack_data = {'content': current_time + " " + url + " in stock at Walmart"}
                if stockdict.get(url) == 'False':
                    response = requests.post(
                    webhook_url, data=json.dumps(slack_data),
                    headers={'Content-Type': 'application/json'})
                stockdict.update({url: 'True'})
            else: 
                print("[" + current_time + "] " + "Sold Out: (Walmart.com) " + url)
                stockdict.update({url: 'False'})

class BH:

    def __init__(self, url, hook):
        self.url = url
        self.hook = hook
        webhook_url = webhook_dict[hook]
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        page = requests.get(url)
        if page.status_code == 200:
            if "Add to Cart" in page.text:
                print("[" + current_time + "] " + "In Stock: (bhphotovideo.com) " + url)
                slack_data = {'content': current_time + " " + url + " in stock at B&H"}
                if stockdict.get(url) == 'False':
                    response = requests.post(
                                             webhook_url, data=json.dumps(slack_data),
                                             headers={'Content-Type': 'application/json'})
                stockdict.update({url: 'True'})
            else:
                print("[" + current_time + "] " + "Sold Out: (bhphotovideo.com) " + url)
                stockdict.update({url: 'False'})

for url in urldict:
    hook = urldict[url]
    if "bestbuy.com" in url:
        print("BestBuy URL detected " + hook)
        parsed = urlparse.urlparse(url)
        sku = parse_qs(parsed.query)['skuId']
        sku = sku[0]
        bestbuylist.append(sku)
        headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
        "cache-control": "max-age=0",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.69 Safari/537.36"
        }
        page = requests.get(url, headers=headers)
        al = page.text
        title = al[al.find('<title >') + 8 : al.find(' - Best Buy</title>')]
        sku_dict.update({sku: title})
        bbdict.update({sku: hook})

    elif "target.com" in url:
        targetlist.append(url)
        print("Target URL detected " + hook)
    elif "walmart.com" in url:
        walmartlist.append(url)
        print("Walmart URL detected " + hook)
    elif "bhphotovideo.com" in url:
        bhlist.append(url)
        print("B&H URL detected " + hook)

for url in urldict:
    stockdict.update({url: 'False'}) #set all URLs to be "out of stock" to begin
for sku in sku_dict:
    stockdict.update({sku: 'False'}) #set all SKUs to be "out of stock" to begin
while True:

# Target
    for url in targetlist:
        try:
            hook = urldict[url]
            Target(url, hook)
        except:
            print("Some problem occurred. Skipping instance...")

# Best Buy
    for sku in bestbuylist:
        try:
            hook = bbdict[sku]
            BestBuy(sku, hook)
        except:
            print("Some problem occurred. Skipping instance...")

# BH
    for url in bhlist:
        hook = urldict[url]
        BH(url, hook)

# Walmart            
    for url in walmartlist:
        try:
            hook = urldict[url]
            Walmart(url, hook)
            time.sleep(5)
        except:
            print("Some problem occurred. Skipping instance...")
            time.sleep(2)

    time.sleep(1)