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
import webhook_settings
import product_settings
from threading import Thread
from selenium import webdriver
from chromedriver_py import binary_path as driver_path
from lxml import html
import wx
from wx.lib.mixins.listctrl import CheckListCtrlMixin, ListCtrlAutoWidthMixin

stockdict = {}
sku_dict = {}
bestbuylist = []
bbdict = {}
products = []

#set all URLs to be "out of stock" to begin
def return_data(path):
    with open(path,"r") as file:
        data = json.load(file)
    file.close()
    return data

def write_data(path,data):
    with open(path, "w") as file:
        json.dump(data, file)
    file.close()

def set_data(path, val1, val2):
    data = return_data(path)
    data.update({val1: val2})

    write_data(path, data)

webhook_dict = return_data("./data/webhooks.json")
urldict = return_data("./data/products.json")

class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin, ListCtrlAutoWidthMixin):

    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, wx.ID_ANY, style=wx.LC_REPORT |
                wx.SUNKEN_BORDER)
        CheckListCtrlMixin.__init__(self)
        ListCtrlAutoWidthMixin.__init__(self)

class Amazon:

    def __init__(self, url, hook):
        self.url = url
        self.hook = hook
        webhook_url = webhook_dict[hook]
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument('log-level=3')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--user-agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36"')
        options.add_argument("headless")
        driver = webdriver.Chrome(executable_path=driver_path, chrome_options=options)
        driver.get(url)

        html = driver.page_source
        if "To discuss automated access to Amazon data please contact api-services-support@amazon.com." in html:
            print("Amazons Bot Protection is preventing this call.")
            app_log.AppendText("Amazons Bot Protection prevented a refresh." + '\n')
        else: 
            status_raw = driver.find_element_by_xpath("//div[@id='olpOfferList']")
            status_text = status_raw.text
            title_raw = driver.find_element_by_xpath("//h1[@class='a-size-large a-spacing-none']")
            title_text = title_raw.text
            title = title_text
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            if "Currently, there are no sellers that can deliver this item to your location." not in status_text:
                print("[" + current_time + "] " + "In Stock: (Amazon.com) " + title + " - " + url)
                slack_data = {'content': "[" + current_time + "] " +  title + " in stock at Amazon - " + url}
                app_log.AppendText("[" + current_time + "] " +  title + " in stock at Amazon - " + url + '\n')
                if stockdict.get(url) == 'False':
                    response = requests.post(
                    webhook_url, data=json.dumps(slack_data),
                    headers={'Content-Type': 'application/json'})
                stockdict.update({url: 'True'})
            else:
                print("[" + current_time + "] " + "Sold Out: (Amazon.com) " + title)
                #app_log.AppendText("[" + current_time + "] " + "Sold Out: (Amazon.com) " + title + '\n')
                stockdict.update({url: 'False'})
        driver.quit()

class BH:

    def __init__(self, url, hook):
        self.url = url
        self.hook = hook
        webhook_url = webhook_dict[hook]
        page = requests.get(url)
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        if page.status_code == 200:
            if "Add to Cart" in page.text:
                print("[" + current_time + "] " + "In Stock: (bhphotovideo.com) " + url)
                slack_data = {'content': "[" + current_time + "] " + url + " in stock at B&H"}
                app_log.AppendText("[" + current_time + "] " + "In Stock: (bhphotovideo.com) " + url + '\n')
                if stockdict.get(url) == 'False':
                    response = requests.post(
                                             webhook_url, data=json.dumps(slack_data),
                                             headers={'Content-Type': 'application/json'})
                stockdict.update({url: 'True'})
            else:
                print("[" + current_time + "] " + "Sold Out: (bhphotovideo.com) " + url)
                #app_log.AppendText("[" + current_time + "] " + "Sold Out: (bhphotovideo.com) " + url + '\n')
                stockdict.update({url: 'False'})

class BestBuy:

    def __init__(self, sku, hook):
        self.sku = sku
        self.hook = hook
        webhook_url = webhook_dict[hook]
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
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        if stock_status == "SOLD_OUT":
            print("[" + current_time + "] " + "Sold Out: (BestBuy.com) " + product_name)
            #app_log.AppendText("[" + current_time + "] " + "Sold Out: (BestBuy.com) " + product_name + '\n')
            stockdict.update({sku: 'False'})
        elif stock_status == "CHECK_STORES":
            print(product_name + " sold out @ BestBuy (check stores status)")
            stockdict.update({sku: 'False'})
        else: 
            if stock_status == "ADD_TO_CART":
                print("[" + current_time + "] " + "In Stock: (BestBuy.com) " + product_name + " - " + link)
                app_log.AppendText("[" + current_time + "] " + "In Stock: (BestBuy.com) " + product_name + " - " + link + '\n')
                slack_data = {'content': "[" + current_time + "] " +  product_name + " In Stock @ BestBuy " + link}
                if stockdict.get(sku) == 'False':
                    response = requests.post(
                    webhook_url, data=json.dumps(slack_data),
                    headers={'Content-Type': 'application/json'})
                stockdict.update({sku: 'True'})
                #print(stockdict)

class Gamestop:

    def __init__(self, url, hook):
        self.url = url
        self.hook = hook
        webhook_url = webhook_dict[hook]
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument('log-level=3')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--user-agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36"')
        options.add_argument("headless")
        driver = webdriver.Chrome(executable_path=driver_path, chrome_options=options)
        driver.get(url)

        html = driver.page_source

        status_raw = driver.find_element_by_xpath("//div[@class='add-to-cart-buttons']")
        status_text = status_raw.text
        title_raw = driver.find_element_by_xpath("//h1[@class='product-name h2']")
        title_text = title_raw.text
        title = title_text
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        if "ADD TO CART" in status_text:
            print("[" + current_time + "] " + "In Stock: (Gamestop.com) " + title + " - " + url)
            app_log.AppendText("[" + current_time + "] " + "In Stock: (Gamestop.com) " + title + " - " + url + '\n')
            slack_data = {'content': "[" + current_time + "] " +  title + " in stock at Gamestop - " + url}
            if stockdict.get(url) == 'False':
                response = requests.post(
                webhook_url, data=json.dumps(slack_data),
                headers={'Content-Type': 'application/json'})
            stockdict.update({url: 'True'})
        else:
            print("[" + current_time + "] " + "Sold Out: (Gamestop.com) " + title)
            #app_log.AppendText("[" + current_time + "] " + "Sold Out: (Gamestop.com) " + title + '\n')
            stockdict.update({url: 'False'})
        driver.quit()

class Target:

    def __init__(self, url, hook):
        self.url = url
        self.hook = hook
        webhook_url = webhook_dict[hook]
        page = requests.get(url)
        al = page.text
        title = al[al.find('"twitter":{"title":') + 20 : al.find('","card')]
        #print(title)
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        if "Temporarily out of stock" in page.text:
            print("[" + current_time + "] " + "Sold Out: (Target.com) " + title)
            #app_log.AppendText("[" + current_time + "] " + "Sold Out: (Target.com) " + title + '\n')
            stockdict.update({url: 'False'})
        else: 
            print("[" + current_time + "] " + "In Stock: (Target.com) " + title + " - " + url)
            app_log.AppendText("[" + current_time + "] " + "In Stock: (Target.com) " + title + " - " + url + '\n')
            slack_data = {'content': "[" + current_time + "] " +  title + " in stock at Target - " + url}
            if stockdict.get(url) == 'False':
                response = requests.post(
                webhook_url, data=json.dumps(slack_data),
                headers={'Content-Type': 'application/json'})
            stockdict.update({url: 'True'})
        #print(stockdict)

class Walmart:

    def __init__(self, url, hook):
        self.url = url
        self.hook = hook
        webhook_url = webhook_dict[hook]
        page = requests.get(url)
        tree = html.fromstring(page.content)
        title_raw = tree.xpath("//h1[@class='prod-ProductTitle font-normal']")
        title = title_raw[0].text
        price_raw = tree.xpath("//span[@class='price display-inline-block arrange-fit price price--stylized']//span[@class='price-characteristic']")
        price = price_raw[0].text
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        if page.status_code == 200:
            if "Add to cart" in page.text:
                print("[" + current_time + "] " + "In Stock: (Walmart.com) " + title + " for $" + price + " - " + url)
                app_log.AppendText("[" + current_time + "] " + "In Stock: (Walmart.com) " + title + " for $" + price + " - " + url + '\n')
                slack_data = {'content': "[" + current_time + "] " + title + " in stock at Walmart for $" + price + " - " + url}
                if stockdict.get(url) == 'False':
                    try:
                        response = requests.post(
                        webhook_url, data=json.dumps(slack_data),
                        headers={'Content-Type': 'application/json'})
                    except:
                        print("Webhook sending failed. Invalid URL configured.")
                stockdict.update({url: 'True'})
            else: 
                print("[" + current_time + "] " + "Sold Out: (Walmart.com) " + title)
                #app_log.AppendText("[" + current_time + "] " + "Sold Out: (Walmart.com) " + title + '\n')
                stockdict.update({url: 'False'})

class ChangeWebhookDialog(wx.Dialog):

    def __init__(self, *args, **kw):
        super(ChangeWebhookDialog, self).__init__(*args, **kw)

        self.InitUI()
        self.SetSize((250, 200))
        self.SetTitle("Change Webhook Assignment")


    def InitUI(self):
        webhook_dict = return_data("./data/webhooks.json")
        pnl = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        sb = wx.StaticBox(pnl, label='Select a Webhook Destintion')
        sbs = wx.StaticBoxSizer(sb, orient=wx.VERTICAL)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        global combo
        combo = wx.ComboBox(pnl)
        hbox1.Add(combo, flag=wx.LEFT, border=5)
        for k in webhook_dict:
            combo.Append(k)
        sbs.Add(hbox1)

        pnl.SetSizer(sbs)

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        okButton = wx.Button(self, label='Ok')
        closeButton = wx.Button(self, label='Close')
        hbox2.Add(okButton)
        hbox2.Add(closeButton, flag=wx.LEFT, border=5)

        vbox.Add(pnl, proportion=1,
            flag=wx.ALL|wx.EXPAND, border=5)
        vbox.Add(hbox2, flag=wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=10)

        self.SetSizer(vbox)

        okButton.Bind(wx.EVT_BUTTON, self.update)
        closeButton.Bind(wx.EVT_BUTTON, self.OnClose)

    def update(self, e):
        try:
            selected = prod_list.GetFocusedItem()
            i = selected
            url = prod_list.GetItemText(i, col=0)
            new_webhook_key = combo.GetSelection()
            new_webhook = combo.GetString(new_webhook_key)
            print(url, new_webhook)
            urldict.update({url: new_webhook})
            set_data("./data/products.json", url, new_webhook)
            prod_list.SetItem(i, 1, new_webhook)
            num = prod_list.GetItemCount()
        except:
            print("An error ocurred. Did you select a URL before clicking Edit?")
        self.Destroy()

    def OnClose(self, e):

        self.Destroy()

class GUI(wx.Frame):

    def __init__(self, *args, **kw):
        super(GUI, self).__init__(*args, **kw)

        webhook_dict = return_data("./data/webhooks.json")
        urldict = return_data("./data/products.json")

        for url in urldict:
            stockdict.update({url: 'False'}) 

        for prod in urldict:
            products.append((prod, urldict[prod], "Inactive"))

        panel = wx.Panel(self)

        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        leftPanel = wx.Panel(panel)
        rightPanel = wx.Panel(panel)

        self.log = wx.TextCtrl(rightPanel, style=wx.TE_MULTILINE|wx.TE_READONLY)
        global app_log
        app_log = self.log
        self.list = CheckListCtrl(rightPanel)
        self.list.InsertColumn(0, 'URL', width=540)
        self.list.InsertColumn(1, 'Webhook')
        self.list.SetColumnWidth(col=1, width=100)
        self.list.InsertColumn(2, 'Status')
        global prod_list
        prod_list = self.list
        global idx
        idx = 0

        for i in products:
            index = self.list.InsertItem(idx, i[0])
            self.list.SetItem(index, 1, i[1])
            self.list.SetItem(index, 2, i[2])
            idx += 1

        vbox2 = wx.BoxSizer(wx.VERTICAL)
        icon = wx.StaticBitmap(leftPanel, bitmap=wx.Bitmap('img/icon.png'))
        selBtn = wx.Button(leftPanel, label='Select All')
        desBtn = wx.Button(leftPanel, label='Deselect All')
        whBtn = wx.Button(leftPanel, label='Manage Webhooks')
        addBtn = wx.Button(leftPanel, label='Add Product URL')
        editBtn = wx.Button(leftPanel, label='Edit Highlighted Item')
        appBtn = wx.Button(leftPanel, label='Start Selected Jobs')
        app2Btn = wx.Button(leftPanel, label='Stop All Jobs')
        delBtn = wx.Button(leftPanel, label='Delete Highlighted Item')

        self.Bind(wx.EVT_BUTTON, self.OnSelectAll, id=selBtn.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnDeselectAll, id=desBtn.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnApply, id=appBtn.GetId())
        self.Bind(wx.EVT_BUTTON, self.StopAll, id=app2Btn.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnChangeDepth, id=editBtn.GetId())
        self.Bind(wx.EVT_BUTTON, self.AddURLs, id=addBtn.GetId())
        self.Bind(wx.EVT_BUTTON, self.webhook_button, id=whBtn.GetId())
        self.Bind(wx.EVT_BUTTON, self.DeleteURL, id=delBtn.GetId())

        vbox2.Add(icon, 0, wx.TOP|wx.BOTTOM|wx.LEFT, border=20)
        vbox2.Add(whBtn, 0, wx.BOTTOM, 5)
        vbox2.Add(addBtn, 0, wx.BOTTOM, 5)
        vbox2.Add(editBtn, 0, wx.BOTTOM, 5)
        vbox2.Add(delBtn, 0, wx.BOTTOM, 25)
        vbox2.Add(selBtn, 0, wx.BOTTOM, 5)
        vbox2.Add(desBtn, 0, wx.BOTTOM, 25)
        vbox2.Add(appBtn, 0, wx.BOTTOM, 5)
        vbox2.Add(app2Btn, 0, wx.BOTTOM, 5)

        leftPanel.SetSizer(vbox2)

        vbox.Add(self.list, 4, wx.EXPAND | wx.TOP, 3)
        vbox.Add((-1, 10))
        vbox.Add(self.log, 1, wx.EXPAND)
        vbox.Add((-1, 10))

        rightPanel.SetSizer(vbox)

        hbox.Add(leftPanel, 0, wx.EXPAND | wx.RIGHT, 5)
        hbox.Add(rightPanel, 1, wx.EXPAND)
        hbox.Add((3, -1))

        panel.SetSizer(hbox)

        self.SetTitle('Product Checker')
        self.SetSize((950, 500))
        self.Centre()
    
    def CheckURLs(self, event):
        num = prod_list.GetItemCount()
        for i in range(num):

            if prod_list.IsChecked(i):
                if prod_list.GetItemText(i, col=2) == "Inactive":
                    url = prod_list.GetItemText(i, col=0)
                    hook = prod_list.GetItemText(i, col=1)
                    RunJob(url, hook, i)
            else:
                if prod_list.GetItemText(i, col=2) != "Inactive":
                    prod_list.SetItem(i, 2, "Stopping")
                    colour = wx.Colour(255, 0, 0, 255)
                    prod_list.SetItemTextColour(i, colour)

    def StopAll(self, event):
        num = prod_list.GetItemCount()
        for i in range(num):
            if prod_list.GetItemText(i, col=2) != "Inactive":
                prod_list.SetItem(i, 2, "Stopping")
                colour = wx.Colour(255, 0, 0, 255)
                prod_list.SetItemTextColour(i, colour)


    def AddURLs(self, event):
        urldict = return_data("./data/products.json")
        product_url = wx.GetTextFromUser('Enter a Product URL', 'Insert dialog')
        product_webhook = "None"
        num = prod_list.GetItemCount()
        idx = (num + 1)
        if product_url != '':
            index = prod_list.InsertItem(idx, product_url)
            prod_list.SetItem(index, 1, "None")
            prod_list.SetItem(index, 2, "Inactive")
            idx += 1
            set_data("./data/products.json", product_url, product_webhook)
            urldict = return_data("./data/products.json")

    def DeleteURL(self, event):
        urldict = return_data("./data/products.json")
        selected = prod_list.GetFocusedItem()
        text = prod_list.GetItemText(selected, col=0)
        if selected != -1:
            prod_list.DeleteItem(selected)
            del urldict[text]
            with open("./data/products.json", "w") as file:
                json.dump(urldict, file)
            file.close()
            urldict = return_data("./data/products.json")

    def OnChangeDepth(self, e):
        selected = prod_list.GetFocusedItem()
        if selected != -1:
            cdDialog = ChangeWebhookDialog(None,
                title='Change Webhook')
            cdDialog.ShowModal()
            cdDialog.Destroy()

    def OnClose(self, e):

        self.Destroy()

    def webhook_button(self, e):
        webhook_settings.main()

    def OnSelectAll(self, event):

        num = self.list.GetItemCount()
        for i in range(num):
            self.list.CheckItem(i)

    def OnDeselectAll(self, event):

        num = self.list.GetItemCount()
        for i in range(num):
            self.list.CheckItem(i, False)

    def OnApply(self, event):

        app_log.AppendText("Processing Selections..." + '\n')
        t = Thread(target=self.CheckURLs, args=(self,))
        t.start()

def write_log(string):
    try:
        app_log.AppendText((string + '\n'))
    except: 
        print("Failed to output to log - Message: \n " + string)

def amzfunc(url, hook, i):
    print("Thread started -> " + url)
    while True:
        try:
            active_status = prod_list.GetItemText(i, col=2)
            if active_status == "Active":
                try:
                    Amazon(url, hook)
                except:
                    print("Some error ocurred parsing Amazon")
                    write_log("An error ocurred parsing Amazon")
                time.sleep(10)
            else:
                print("Aborting thread")
                colour = wx.Colour(0, 0, 0, 255)
                prod_list.SetItemTextColour(i, colour)
                prod_list.SetItem(i, 2, "Inactive")
                break
        except:
            break
def bestbuyfunc(sku, hook, i):
    print("Thread started -> " + sku)
    while True:
        try:
            active_status = prod_list.GetItemText(i, col=2)
            if active_status == "Active":
                try:
                    BestBuy(sku, hook)
                except:
                    print("Some error ocurred parsing BestBuy")
                    write_log("An error ocurred parsing BestBuy")
                time.sleep(10)
            else:
                print("Aborting thread")
                colour = wx.Colour(0, 0, 0, 255)
                prod_list.SetItemTextColour(i, colour)
                prod_list.SetItem(i, 2, "Inactive")
                break
        except:
            break
def gamestopfunc(url, hook, i):
    print("Thread started -> " + url)
    while True:
        try:
            active_status = prod_list.GetItemText(i, col=2)
            if active_status == "Active":
                try:
                    Gamestop(url, hook)
                except:
                    print("Some error ocurred parsing Gamestop")
                    write_log("An error ocurred parsing Gamestop")
                time.sleep(10)
            else:
                print("Aborting thread")
                colour = wx.Colour(0, 0, 0, 255)
                prod_list.SetItemTextColour(i, colour)
                prod_list.SetItem(i, 2, "Inactive")
                break
        except:
            break
def targetfunc(url, hook, i):
    print("Thread started -> " + url)
    while True:
        try:
            active_status = prod_list.GetItemText(i, col=2)
            if active_status == "Active":
                try:
                    Target(url, hook)
                except:
                    print("Some error ocurred parsing Target")
                    write_log("An error ocurred parsing Target")
                time.sleep(10)
            else:
                print("Aborting thread")
                colour = wx.Colour(0, 0, 0, 255)
                prod_list.SetItemTextColour(i, colour)
                prod_list.SetItem(i, 2, "Inactive")
                break
        except:
            break
def walmartfunc(url, hook, i):
    print("Thread started -> " + url)
    while True:
        try:
            active_status = prod_list.GetItemText(i, col=2)
            if active_status == "Active":
                try:
                    hook = prod_list.GetItemText(i, col=1)
                    Walmart(url, hook)
                except:
                    print("Some error ocurred parsing WalMart")
                    write_log("An error ocurred parsing Walmart")
                time.sleep(10)
            else:
                print("Aborting thread")
                colour = wx.Colour(0, 0, 0, 255)
                prod_list.SetItemTextColour(i, colour)
                prod_list.SetItem(i, 2, "Inactive")
                break
        except:
            break

def RunJob(url, hook, i):

    #Amazon URL Detection
    if "amazon.com" in url:
        active_status = prod_list.GetItemText(i, col=2)
        if "offer-listing" in url:
            if active_status != "Active":
                colour = wx.Colour(0, 255, 0, 255)
                prod_list.SetItemTextColour(i, colour)
                prod_list.SetItem(i, 2, "Active")
                print("Amazon URL detected using Webhook destination " + hook)
                write_log(("Amazon URL detected -> " + hook))
                t = Thread(target=amzfunc, args=(url, hook, i))
                t.start()
                time.sleep(0.5)
        else:
            print("Invalid Amazon link detected. Please use the Offer Listing page.")

   #Target URL Detection
    elif "gamestop.com" in url:
        active_status = prod_list.GetItemText(i, col=2)
        if active_status != "Active":
            colour = wx.Colour(0, 255, 0, 255)
            prod_list.SetItemTextColour(i, colour)
            prod_list.SetItem(i, 2, "Active")
            print("Gamestop URL detected using Webhook destination " + hook)
            write_log(("GameStop URL detected -> " + hook))
            t = Thread(target=gamestopfunc, args=(url, hook, i))
            t.start()
            time.sleep(0.5)

    #BestBuy URL Detection
    elif "bestbuy.com" in url:
        print("BestBuy URL detected using Webhook destination " + hook)
        #app_log.AppendText("BestBuy URL detected using Webhook destination " + hook + '\n')          
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
        active_status = prod_list.GetItemText(i, col=2)
        if active_status != "Active":
            colour = wx.Colour(0, 255, 0, 255)
            prod_list.SetItemTextColour(i, colour)
            prod_list.SetItem(i, 2, "Active")
            print("BestBuy URL detected using Webhook destination " + hook)
            write_log(("BestBuy URL detected -> " + hook))
            t = Thread(target=bestbuyfunc, args=(sku, hook, i))
            t.start()
            time.sleep(0.5)

    #Target URL Detection
    elif "target.com" in url:
        #targetlist.append(url)
        active_status = prod_list.GetItemText(i, col=2)
        if active_status != "Active":
            colour = wx.Colour(0, 255, 0, 255)
            prod_list.SetItemTextColour(i, colour)
            prod_list.SetItem(i, 2, "Active")
            print("Target URL detected using Webhook destination " + hook)
            write_log(("Target URL detected -> " + hook))
            t = Thread(target=targetfunc, args=(url, hook, i))
            t.start()
            time.sleep(0.5)

    #Walmart URL Detection
    elif "walmart.com" in url:
        #walmartlist.append(url)
        active_status = prod_list.GetItemText(i, col=2)
        if active_status != "Active":
            colour = wx.Colour(0, 255, 0, 255)
            prod_list.SetItemTextColour(i, colour)
            prod_list.SetItem(i, 2, "Active")
            print("Walmart URL detected using Webhook destination " + hook)
            write_log(("Walmart URL detected -> " + hook))
            t = Thread(target=walmartfunc, args=(url, hook, i))
            t.start()
            time.sleep(0.5)

    #B&H Photo URL Detection
    elif "bhphotovideo.com" in url:
        #bhlist.append(url)
        print("B&H URL detected using Webhook destination " + hook)
        #app_log.AppendText("B&H URL detected using Webhook destination " + hook + '\n')

def main():
    app = wx.App()
    global ex
    ex = GUI(None)
    ex.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()