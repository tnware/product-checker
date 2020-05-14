#/usr/bin/python3
# https://github.com/tnware/product-checker
# by Tyler Woods
# coded for Bird Bot and friends
# https://tylermade.net
# -*- coding: utf-8 -*-
import wx
import wx.xrc
import json
import requests
import time
from datetime import datetime
import urllib.parse as urlparse
from urllib.parse import parse_qs
from threading import Thread
from selenium import webdriver
from chromedriver_py import binary_path as driver_path
from lxml import html
#put maxprice to 0 for defaults (any), set it to a plain number for example 300 with no quotes to ignore anything that is listed over 300.
#only applies to walmart URLs for right now
#maxprice = 300
maxprice = 0

###########################################################################
## Class WebhookManager
###########################################################################

class WebhookManager ( wx.Frame ):

	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Manage Webhooks", pos = wx.DefaultPosition, size = wx.Size( 354,199 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		outer = wx.BoxSizer( wx.VERTICAL )

		self.panel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		box = wx.BoxSizer( wx.HORIZONTAL )

		self.btnPanel = wx.Panel( self.panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		btnbox = wx.BoxSizer( wx.VERTICAL )

		self.newBtn = wx.Button( self.btnPanel, wx.ID_ANY, u"New", wx.DefaultPosition, wx.DefaultSize, 0 )
		btnbox.Add( self.newBtn, 0, wx.ALL, 5 )

		self.renBtn = wx.Button( self.btnPanel, wx.ID_ANY, u"Update", wx.DefaultPosition, wx.DefaultSize, 0 )
		btnbox.Add( self.renBtn, 0, wx.ALL, 5 )

		self.delBtn = wx.Button( self.btnPanel, wx.ID_ANY, u"Delete", wx.DefaultPosition, wx.DefaultSize, 0 )
		btnbox.Add( self.delBtn, 0, wx.ALL, 5 )

		self.clrBtn = wx.Button( self.btnPanel, wx.ID_ANY, u"Clear All", wx.DefaultPosition, wx.DefaultSize, 0 )
		btnbox.Add( self.clrBtn, 0, wx.ALL, 5 )


		self.btnPanel.SetSizer( btnbox )
		self.btnPanel.Layout()
		btnbox.Fit( self.btnPanel )
		box.Add( self.btnPanel, 0, wx.EXPAND |wx.ALL, 5 )

		self.listPanel = wx.Panel( self.panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		lstbox = wx.BoxSizer( wx.VERTICAL )

		#webhookListChoices = []
		self.webhookList = wx.ListBox( self.listPanel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, webhookListChoices, 0 )
		lstbox.Add( self.webhookList, 1, wx.ALL|wx.EXPAND, 5 )


		self.listPanel.SetSizer( lstbox )
		self.listPanel.Layout()
		lstbox.Fit( self.listPanel )
		box.Add( self.listPanel, 1, wx.EXPAND |wx.ALL, 5 )


		self.panel.SetSizer( box )
		self.panel.Layout()
		box.Fit( self.panel )
		outer.Add( self.panel, 1, wx.EXPAND, 5 )


		self.SetSizer( outer )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.newBtn.Bind( wx.EVT_BUTTON, self.NewItem )
		self.renBtn.Bind( wx.EVT_BUTTON, self.OnUpdate )
		self.delBtn.Bind( wx.EVT_BUTTON, self.OnDelete )
		self.clrBtn.Bind( wx.EVT_BUTTON, self.OnClear )

	def __del__( self ):
		pass

	def NewItem(self, event):

		webhook_dict = return_data("./data/webhooks.json")
		webhook_url = wx.GetTextFromUser('Enter a Webhook URL', 'Insert dialog')
		if webhook_url != '':
			webhook_name = wx.GetTextFromUser('Give the webhook URL a friendly name', 'Insert dialog')
			self.webhookList.Append(webhook_name)
			set_data("./data/webhooks.json", webhook_name, webhook_url)
			webhook_dict = return_data("./data/webhooks.json")
			webhookListChoices.append(webhook_name)

	def OnUpdate(self, event):

		webhook_dict = return_data("./data/webhooks.json")
		sel = self.webhookList.GetSelection()
		text = self.webhookList.GetString(sel)
		webhook_to_modify = webhook_dict[text]
		modified_webhook_url = wx.GetTextFromUser('Update item', 'Update Item dialog', webhook_to_modify)

		if modified_webhook_url != '':
			webhook_dict.update({text: modified_webhook_url})
			set_data("./data/webhooks.json", text, modified_webhook_url)
			webhook_dict = return_data("./data/webhooks.json")
			#self.webhookList.Delete(sel)
			#item_id = self.webhookList.Insert(renamed, sel)
			#self.webhookList.SetSelection(item_id)

	def OnDelete(self, event):
		
		webhook_dict = return_data("./data/webhooks.json")
		sel = self.webhookList.GetSelection()
		text = self.webhookList.GetString(sel)
		if sel != -1:
			self.webhookList.Delete(sel)
			del webhook_dict[text]
		with open("./data/webhooks.json", "w") as file:
			json.dump(webhook_dict, file)
			file.close()
		webhook_dict = return_data("./data/webhooks.json")

	def OnClear(self, event):
		self.webhookList.Clear()
		with open("./data/webhooks.json", "w") as file:
			json.dump({}, file)
			file.close()
		webhook_dict = return_data("./data/webhooks.json")


###########################################################################
## Class WebhookDialog
###########################################################################

class WebhookDialog ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Assign Webhook", pos = wx.DefaultPosition, size = wx.Size( 201,103 ), style = wx.DEFAULT_DIALOG_STYLE )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		vbox = wx.BoxSizer( wx.VERTICAL )

		self.pnl = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		vbox.Add( self.pnl, 1, wx.EXPAND |wx.ALL, 5 )

		comboChoices = []
		self.combo = wx.ComboBox( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, comboChoices, 0 )
		vbox.Add( self.combo, 0, wx.ALL|wx.EXPAND, 5 )

		self.okButton = wx.Button( self, wx.ID_ANY, u"Okay", wx.DefaultPosition, wx.DefaultSize, 0 )
		vbox.Add( self.okButton, 0, wx.ALL|wx.EXPAND, 5 )


		self.SetSizer( vbox )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.okButton.Bind( wx.EVT_BUTTON, self.update )
		
		webhook_dict = return_data("./data/webhooks.json")
		for k in webhook_dict:
			self.combo.Append(k)
      
	def update(self, e):
		try:
			selected = ex.list.GetFocusedItem()
			i = selected
			url = ex.list.GetItemText(i, col=0)
			new_webhook_key = self.combo.GetSelection()
			new_webhook = self.combo.GetString(new_webhook_key)
			if new_webhook != "":
				print(url, new_webhook)
				urldict.update({url: new_webhook})
				set_data("./data/products.json", url, new_webhook)
				ex.list.SetItem(i, 1, new_webhook)
				num = ex.list.GetItemCount()
			else:
				print("select a webhook first")
		except:
			print("An error ocurred. Did you select a URL before clicking Edit?")
			self.Close()
		self.Close()


	def OnClose(self, e):

		self.Destroy()

	def __del__( self ):
		pass


###########################################################################
## Class GUI
###########################################################################

class GUI ( wx.Frame ):

	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Product Checker", pos = wx.DefaultPosition, size = wx.Size( 1009,660 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		hbox = wx.BoxSizer( wx.HORIZONTAL )

		self.leftPanel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		vbox2 = wx.BoxSizer( wx.VERTICAL )

		self.icon = wx.StaticBitmap( self.leftPanel, wx.ID_ANY, wx.Bitmap( u"img/icon.png", wx.BITMAP_TYPE_ANY ), wx.DefaultPosition, wx.DefaultSize, 0 )
		vbox2.Add( self.icon, 0, wx.ALL|wx.EXPAND, 15 )

		self.whBtn = wx.Button( self.leftPanel, wx.ID_ANY, u"Manage Webhooks", wx.DefaultPosition, wx.DefaultSize, 0 )
		vbox2.Add( self.whBtn, 0, wx.ALL|wx.EXPAND, 5 )

		self.addBtn = wx.Button( self.leftPanel, wx.ID_ANY, u"Add Product URL", wx.DefaultPosition, wx.DefaultSize, 0 )
		vbox2.Add( self.addBtn, 0, wx.ALL|wx.EXPAND, 5 )

		self.editBtn = wx.Button( self.leftPanel, wx.ID_ANY, u"Edit Highlighted Item", wx.DefaultPosition, wx.DefaultSize, 0 )
		vbox2.Add( self.editBtn, 0, wx.ALL|wx.EXPAND, 5 )

		self.delBtn = wx.Button( self.leftPanel, wx.ID_ANY, u"Delete Highlighted Item", wx.DefaultPosition, wx.DefaultSize, 0 )
		vbox2.Add( self.delBtn, 0, wx.ALL|wx.EXPAND, 5 )

		self.strtAllBtn = wx.Button( self.leftPanel, wx.ID_ANY, u"START All Jobs", wx.DefaultPosition, wx.DefaultSize, 0 )
		vbox2.Add( self.strtAllBtn, 0, wx.ALL|wx.EXPAND, 5 )

		self.app2Btn = wx.Button( self.leftPanel, wx.ID_ANY, u"STOP All Jobs", wx.DefaultPosition, wx.DefaultSize, 0 )
		vbox2.Add( self.app2Btn, 0, wx.ALL|wx.EXPAND, 5 )


		vbox2.Add( ( 0, 0), 1, wx.EXPAND, 5 )


		self.leftPanel.SetSizer( vbox2 )
		self.leftPanel.Layout()
		vbox2.Fit( self.leftPanel )
		hbox.Add( self.leftPanel, 0, wx.EXPAND, 5 )

		self.rightPanel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		vbox = wx.BoxSizer( wx.VERTICAL )

		self.list = wx.ListCtrl( self.rightPanel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_REPORT )
		vbox.Add( self.list, 1, wx.ALL|wx.EXPAND, 5 )

		self.log = wx.TextCtrl( self.rightPanel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( -1,200 ), wx.TE_MULTILINE|wx.TE_READONLY )
		vbox.Add( self.log, 0, wx.ALL|wx.EXPAND, 5 )


		self.rightPanel.SetSizer( vbox )
		self.rightPanel.Layout()
		vbox.Fit( self.rightPanel )
		hbox.Add( self.rightPanel, 1, wx.EXPAND, 5 )


		self.SetSizer( hbox )
		self.Layout()
		self.statusBar = self.CreateStatusBar( 1, wx.STB_SIZEGRIP, wx.ID_ANY )
		self.m_menubar1 = wx.MenuBar( 0 )
		self.menuFile = wx.Menu()
		self.exitItem = wx.MenuItem( self.menuFile, wx.ID_ANY, u"Exit", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuFile.Append( self.exitItem )

		self.m_menubar1.Append( self.menuFile, u"File" )

		self.menuHelp = wx.Menu()
		self.m_menubar1.Append( self.menuHelp, u"Help" )

		self.SetMenuBar( self.m_menubar1 )


		self.Centre( wx.BOTH )

		# Connect Events
		self.whBtn.Bind( wx.EVT_BUTTON, self.OnManageWebhooks )
		self.addBtn.Bind( wx.EVT_BUTTON, self.AddURLs )
		self.editBtn.Bind( wx.EVT_BUTTON, self.OnChangeWebhook )
		self.delBtn.Bind( wx.EVT_BUTTON, self.DeleteURL )
		self.strtAllBtn.Bind( wx.EVT_BUTTON, self.OnRunAll )
		self.app2Btn.Bind( wx.EVT_BUTTON, self.StopAll )
		self.Bind( wx.EVT_MENU, self.OnClose, id = self.exitItem.GetId() )

	def __del__( self ):
		pass


	def CheckURLs(self, event):
		num = ex.list.GetItemCount()
		for i in range(num):

			if ex.list.IsChecked(i):
				if ex.list.GetItemText(i, col=2) == "Inactive":
					url = ex.list.GetItemText(i, col=0)
					hook = ex.list.GetItemText(i, col=1)
					RunJob(url, hook, i)
				else:
					if ex.list.GetItemText(i, col=2) != "Inactive":
						ex.list.SetItem(i, 2, "Stopping")
						colour = wx.Colour(255, 0, 0, 255)
						ex.list.SetItemTextColour(i, colour)


	def RunAll(self, event):
		num = ex.list.GetItemCount()
		for i in range(num):
			if ex.list.GetItemText(i, col=2) == "Inactive":
				url = ex.list.GetItemText(i, col=0)
				hook = ex.list.GetItemText(i, col=1)
				RunJob(url, hook, i)

	def StopAll(self, event):
		num = ex.list.GetItemCount()
		for i in range(num):
			if ex.list.GetItemText(i, col=2) != "Inactive":
				ex.list.SetItem(i, 2, "Stopping")
				colour = wx.Colour(255, 0, 0, 255)
				ex.list.SetItemTextColour(i, colour)


	def AddURLs(self, event):
		urldict = return_data("./data/products.json")
		product_url = wx.GetTextFromUser('Enter a Product URL', 'Insert dialog')
		product_webhook = "None"
		num = ex.list.GetItemCount()
		idx = (num + 1)
		if product_url != '':
			index = ex.list.InsertItem(idx, product_url)
			ex.list.SetItem(index, 1, "None")
			ex.list.SetItem(index, 2, "Inactive")
			idx += 1
			set_data("./data/products.json", product_url, product_webhook)
			urldict = return_data("./data/products.json")

	def DeleteURL(self, event):
		urldict = return_data("./data/products.json")
		selected = ex.list.GetFocusedItem()
		text = ex.list.GetItemText(selected, col=0)
		if selected != -1:
			ex.list.DeleteItem(selected)
			del urldict[text]
			with open("./data/products.json", "w") as file:
				json.dump(urldict, file)
				file.close()
				urldict = return_data("./data/products.json")


	def OnChangeWebhook(self, e):
		webhook_dict = return_data("./data/webhooks.json")
		selected = ex.list.GetFocusedItem()
		if selected != -1:
			whDialog = WebhookDialog(None)
			whDialog.ShowModal()
			whDialog.Destroy()

	def OnManageWebhooks(self, e):
		webhook_dict = return_data("./data/webhooks.json")
		global webhookListChoices
		webhookListChoices = []
		for k in webhook_dict:
			webhookListChoices.append(k)
		whManager = WebhookManager(None)
		whManager.Show()

	def OnClose(self, e):

		self.Destroy()

	def OnSelectAll(self, event):

		num = self.list.GetItemCount()
		for i in range(num):
			self.list.CheckItem(i)

	def OnDeselectAll(self, event):

		num = self.list.GetItemCount()
		for i in range(num):
			self.list.CheckItem(i, False)

	def OnApply(self, event):

		ex.log.AppendText("Processing Selections..." + '\n')
		t = Thread(target=self.CheckURLs, args=(self,))
		t.start()

	def OnRunAll(self, event):
		for url in urldict:
			stockdict.update({url: 'False'}) 
		ex.log.AppendText("Processing Selections..." + '\n')
		t = Thread(target=self.RunAll, args=(self,))
		t.start()

###########################################################################
## Custom init
###########################################################################

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
            print("Amazon's Bot Protection is preventing this call.")
            ex.log.AppendText("Amazon's Bot Protection prevented a refresh." + '\n')
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
                ex.log.AppendText("[" + current_time + "] " +  title + " in stock at Amazon - " + url + '\n')
                if stockdict.get(url) == 'False':
                    response = requests.post(
                    webhook_url, data=json.dumps(slack_data),
                    headers={'Content-Type': 'application/json'})
                stockdict.update({url: 'True'})
            else:
                print("[" + current_time + "] " + "Sold Out: (Amazon.com) " + title)
                #ex.log.AppendText("[" + current_time + "] " + "Sold Out: (Amazon.com) " + title + '\n')
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
                ex.log.AppendText("[" + current_time + "] " + "In Stock: (bhphotovideo.com) " + url + '\n')
                if stockdict.get(url) == 'False':
                    response = requests.post(
                                             webhook_url, data=json.dumps(slack_data),
                                             headers={'Content-Type': 'application/json'})
                stockdict.update({url: 'True'})
            else:
                print("[" + current_time + "] " + "Sold Out: (bhphotovideo.com) " + url)
                #ex.log.AppendText("[" + current_time + "] " + "Sold Out: (bhphotovideo.com) " + url + '\n')
                stockdict.update({url: 'False'})

class BestBuy:

	def __init__(self, sku, orig_url, hook):
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
			#ex.log.AppendText("[" + current_time + "] " + "Sold Out: (BestBuy.com) " + product_name + '\n')
			stockdict.update({sku: 'False'})
		elif stock_status == "CHECK_STORES":
			print(product_name + " sold out @ BestBuy (check stores status)")
			stockdict.update({sku: 'False'})
		else: 
			if stock_status == "ADD_TO_CART":
				print("[" + current_time + "] " + "In Stock: (BestBuy.com) " + product_name + " - " + link)
				ex.log.AppendText("[" + current_time + "] " + "In Stock: (BestBuy.com) " + product_name + " - " + link + '\n')
				#slack_data = {'content': "[" + current_time + "] " +  product_name + " In Stock @ BestBuy " + link}
				slack_data = {
					'username': "BestBuy Bot",
					'avatar_url': "https://github.com/tnware/product-checker/raw/master/img/bestbuy.png",
					'content': "BestBuy Stock Alert:", 
					'embeds': [{ 
						'title': product_name,  
						'description': product_name + " in stock at BestBuy", 
						'url': link, 
						"fields": [
						{
							"name": "Time:",
							"value": current_time
						},
						{
							"name": "Status:",
							"value": "In Stock"
						}
								],
						'thumbnail': { 
							'url': bbimgdict.get(sku)
							}
						}]
					}
				if stockdict.get(orig_url) == 'False':
					response = requests.post(
					webhook_url, data=json.dumps(slack_data),
					headers={'Content-Type': 'application/json'})
				stockdict.update({orig_url: 'True'})
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
		image_raw = driver.find_element_by_xpath("//img[@class='mainImg ae-img']")
		img = image_raw.get_attribute('src')
		now = datetime.now()
		current_time = now.strftime("%H:%M:%S")
		if "ADD TO CART" in status_text:
			print("[" + current_time + "] " + "In Stock: (Gamestop.com) " + title + " - " + url)
			ex.log.AppendText("[" + current_time + "] " + "In Stock: (Gamestop.com) " + title + " - " + url + '\n')
			slack_data = {
				'username': "GameStop Bot",
				'content': "GameStop Stock Alert:", 
				'embeds': [{ 
					'title': title,  
					'description': title + " in stock at GameStop", 
					'url': url, 
					"fields": [
					{
						"name": "Time:",
						"value": current_time
					},
					{
						"name": "Status:",
						"value": "In Stock"
					}
							],
					'thumbnail': { 
						'url': img
						}
					}]
				}
			if stockdict.get(url) == 'False':
				response = requests.post(
				webhook_url, data=json.dumps(slack_data),
				headers={'Content-Type': 'application/json'})
			stockdict.update({url: 'True'})
		else:
			print("[" + current_time + "] " + "Sold Out: (Gamestop.com) " + title)
			#ex.log.AppendText("[" + current_time + "] " + "Sold Out: (Gamestop.com) " + title + '\n')
			stockdict.update({url: 'False'})
		driver.quit()

class Target:

	def __init__(self, url, hook):
		self.url = url
		self.hook = hook
		webhook_url = webhook_dict[hook]
		page = requests.get(url)
		al = page.text
		tree = html.fromstring(page.content)
		imgs = tree.xpath("//img[1]")
		img_raw = str(imgs[0].attrib)
		img = img_raw[20:-2]
		title = al[al.find('"twitter":{"title":') + 20 : al.find('","card')]
        #print(title)
		now = datetime.now()
		current_time = now.strftime("%H:%M:%S")
		if "Temporarily out of stock" in page.text:
			print("[" + current_time + "] " + "Sold Out: (Target.com) " + title)
			#ex.log.AppendText("[" + current_time + "] " + "Sold Out: (Target.com) " + title + '\n')
			stockdict.update({url: 'False'})
		else: 
			print("[" + current_time + "] " + "In Stock: (Target.com) " + title + " - " + url)
			ex.log.AppendText("[" + current_time + "] " + "In Stock: (Target.com) " + title + " - " + url + '\n')
			slack_data = {
				'username': "Target Bot",
				'avatar_url': "https://github.com/tnware/product-checker/raw/master/img/target.png",
				'content': "Target Stock Alert:", 
				'embeds': [{ 
					'title': title,  
					'description': title + " in stock at Target", 
					'url': url, 
					"fields": [
					{
						"name": "Time:",
						"value": current_time
					},
					{
						"name": "Status:",
						"value": "In Stock"
					}
							],
					'thumbnail': { 
						'url': img
						}
					}]
				}
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
		img_raw = tree.xpath("//meta[@property='og:image']/@content")
		img = img_raw[0]
		now = datetime.now()
		current_time = now.strftime("%H:%M:%S")
		if page.status_code == 200:
			if "Add to cart" in page.text:
				print("[" + current_time + "] " + "In Stock: (Walmart.com) " + title + " for $" + price + " - " + url)
				ex.log.AppendText("[" + current_time + "] " + "In Stock: (Walmart.com) " + title + " for $" + price + " - " + url + '\n')
				slack_data = {
					'username': "Walmart Bot",
					'avatar_url': "https://github.com/tnware/product-checker/raw/master/img/walmart.png",
					'content': "Walmart Stock Alert:", 
					'embeds': [{ 
						'title': title,  
						'description': title + " in stock at Walmart for $" + price, 
						'url': url, 
						"fields": [
						{
						"name": "Time:",
						"value": current_time
						},
						{
							"name": "Price:",
							"value": "$" + price
						}
								],
						'thumbnail': { 
							'url': img
							}
						}]
					}
				if stockdict.get(url) == 'False':
					if maxprice != 0:
						if int(price) > maxprice:
							print("in stock but not MSRP")
						else:
							try:
								response = requests.post(
								webhook_url, data=json.dumps(slack_data),
								headers={'Content-Type': 'application/json'})
							except:
								print("Webhook sending failed. Invalid URL configured.")
					else:
						try:
							response = requests.post(
							webhook_url, data=json.dumps(slack_data),
							headers={'Content-Type': 'application/json'})
						except:
							print("Webhook sending failed. Invalid URL configured.")
				stockdict.update({url: 'True'})
			else: 
				print("[" + current_time + "] " + "Sold Out: (Walmart.com) " + title)
				#ex.log.AppendText("[" + current_time + "] " + "Sold Out: (Walmart.com) " + title + '\n')
				stockdict.update({url: 'False'})

def write_log(string):
    try:
        ex.log.AppendText((string + '\n'))
    except: 
        print("Failed to output to log - Message: \n " + string)

def amzfunc(url, hook, i):
    print("Thread started -> " + url)
    while True:
        try:
            active_status = ex.list.GetItemText(i, col=2)
            if active_status == "Active":
                try:
                    Amazon(url, hook)
                except:
                    print("Some error ocurred parsing Amazon")
                    write_log("An error ocurred parsing Amazon")
                time.sleep(10)
            else:
                print("Aborted Thread")
                colour = wx.Colour(0, 0, 0, 255)
                ex.list.SetItemTextColour(i, colour)
                ex.list.SetItem(i, 2, "Inactive")
                break
        except:
            break
def bestbuyfunc(sku, orig_url, hook, i):
    print("Thread started -> " + sku)
    while True:
        try:
            active_status = ex.list.GetItemText(i, col=2)
            if active_status == "Active":
                try:
                    BestBuy(sku, orig_url, hook)
                except:
                    print("Some error ocurred parsing BestBuy")
                    write_log("An error ocurred parsing BestBuy")
                time.sleep(10)
            else:
                print("Aborted Thread")
                colour = wx.Colour(0, 0, 0, 255)
                ex.list.SetItemTextColour(i, colour)
                ex.list.SetItem(i, 2, "Inactive")
                break
        except:
            break
def gamestopfunc(url, hook, i):
    print("Thread started -> " + url)
    while True:
        try:
            active_status = ex.list.GetItemText(i, col=2)
            if active_status == "Active":
                try:
                    Gamestop(url, hook)
                except:
                    print("Some error ocurred parsing Gamestop")
                    write_log("An error ocurred parsing Gamestop")
                time.sleep(10)
            else:
                print("Aborted Thread")
                colour = wx.Colour(0, 0, 0, 255)
                ex.list.SetItemTextColour(i, colour)
                ex.list.SetItem(i, 2, "Inactive")
                break
        except:
            break
def targetfunc(url, hook, i):
    print("Thread started -> " + url)
    while True:
        try:
            active_status = ex.list.GetItemText(i, col=2)
            if active_status == "Active":
                try:
                    Target(url, hook)
                except:
                    print("Some error ocurred parsing Target")
                    write_log("An error ocurred parsing Target")
                time.sleep(10)
            else:
                print("Aborted Thread")
                colour = wx.Colour(0, 0, 0, 255)
                ex.list.SetItemTextColour(i, colour)
                ex.list.SetItem(i, 2, "Inactive")
                break
        except:
            break
def walmartfunc(url, hook, i):
    print("Thread started -> " + url)
    while True:
        try:
            active_status = ex.list.GetItemText(i, col=2)
            if active_status == "Active":
                try:
                    hook = ex.list.GetItemText(i, col=1)
                    Walmart(url, hook)
                except:
                    print("Some error ocurred parsing WalMart")
                    write_log("An error ocurred parsing Walmart")
                time.sleep(10)
            else:
                print("Aborted Thread")
                colour = wx.Colour(0, 0, 0, 255)
                ex.list.SetItemTextColour(i, colour)
                ex.list.SetItem(i, 2, "Inactive")
                break
        except:
            break

def bhfunc(url, hook, i):
    print("Thread started -> " + url)
    while True:
        try:
            active_status = ex.list.GetItemText(i, col=2)
            if active_status == "Active":
                try:
                    hook = ex.list.GetItemText(i, col=1)
                    BH(url, hook)
                except:
                    print("Some error ocurred parsing BH Photo")
                    write_log("An error ocurred parsing BH Photo")
                time.sleep(10)
            else:
                print("Aborted Thread")
                colour = wx.Colour(0, 0, 0, 255)
                ex.list.SetItemTextColour(i, colour)
                ex.list.SetItem(i, 2, "Inactive")
                break
        except:
            break

def RunJob(url, hook, i):

	#Amazon URL Detection
	if "amazon.com" in url:
		try:
			active_status = ex.list.GetItemText(i, col=2)
			if "offer-listing" in url:
				if active_status != "Active":
					colour = wx.Colour(0, 255, 0, 255)
					ex.list.SetItemTextColour(i, colour)
					ex.list.SetItem(i, 2, "Active")
					print("Amazon URL detected using Webhook destination " + hook)
					write_log(("Amazon URL detected -> " + hook))
					t = Thread(target=amzfunc, args=(url, hook, i))
					t.start()
					time.sleep(0.5)
			else:
				print("Invalid Amazon link detected. Please use the Offer Listing page.")
		except:
			print("Error processing URL: " + url)
	#Target URL Detection
	elif "gamestop.com" in url:
		try:
			active_status = ex.list.GetItemText(i, col=2)
			if active_status != "Active":
				colour = wx.Colour(0, 255, 0, 255)
				ex.list.SetItemTextColour(i, colour)
				ex.list.SetItem(i, 2, "Active")
				print("Gamestop URL detected using Webhook destination " + hook)
				write_log(("GameStop URL detected -> " + hook))
				t = Thread(target=gamestopfunc, args=(url, hook, i))
				t.start()
				time.sleep(0.5)
		except:
			print("Error processing URL: " + url)

	#BestBuy URL Detection
	elif "bestbuy.com" in url:
		try:
			print("BestBuy URL detected using Webhook destination " + hook)
			#ex.log.AppendText("BestBuy URL detected using Webhook destination " + hook + '\n')          
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
			tree = html.fromstring(page.content)
			img = tree.xpath('//img[@class="primary-image"]/@src')[0]
			title = al[al.find('<title >') + 8 : al.find(' - Best Buy</title>')]
			sku_dict.update({sku: title})
			bbdict.update({sku: hook})
			bbimgdict.update({sku: img})
			active_status = ex.list.GetItemText(i, col=2)
			if active_status != "Active":
				colour = wx.Colour(0, 255, 0, 255)
				ex.list.SetItemTextColour(i, colour)
				ex.list.SetItem(i, 2, "Active")
				print("BestBuy URL detected using Webhook destination " + hook)
				write_log(("BestBuy URL detected -> " + hook))
				orig_url = url
				t = Thread(target=bestbuyfunc, args=(sku, orig_url, hook, i))
				t.start()
				time.sleep(0.5)
		except:
			print("Error processing URL: " + url)

	#Target URL Detection
	elif "target.com" in url:
		try:
			#targetlist.append(url)
			active_status = ex.list.GetItemText(i, col=2)
			if active_status != "Active":
				colour = wx.Colour(0, 255, 0, 255)
				ex.list.SetItemTextColour(i, colour)
				ex.list.SetItem(i, 2, "Active")
				print("Target URL detected using Webhook destination " + hook)
				write_log(("Target URL detected -> " + hook))
				t = Thread(target=targetfunc, args=(url, hook, i))
				t.start()
				time.sleep(0.5)
		except:
			print("Error processing URL: " + url)

	#Walmart URL Detection
	elif "walmart.com" in url:
		try:
			#walmartlist.append(url)
			active_status = ex.list.GetItemText(i, col=2)
			if active_status != "Active":
				colour = wx.Colour(0, 255, 0, 255)
				ex.list.SetItemTextColour(i, colour)
				ex.list.SetItem(i, 2, "Active")
				print("Walmart URL detected using Webhook destination " + hook)
				write_log(("Walmart URL detected -> " + hook))
				t = Thread(target=walmartfunc, args=(url, hook, i))
				t.start()
				time.sleep(0.5)
		except:
			print("Error processing URL: " + url)

	#B&H Photo URL Detection
	elif "bhphotovideo.com" in url:
		try:
			active_status = ex.list.GetItemText(i, col=2)
			if active_status != "Active":
				colour = wx.Colour(0, 255, 0, 255)
				ex.list.SetItemTextColour(i, colour)
				ex.list.SetItem(i, 2, "Active")
				print("BH Photo URL detected using Webhook destination " + hook)
				write_log(("BH Photo URL detected -> " + hook))
				t = Thread(target=bhfunc, args=(url, hook, i))
				t.start()
				time.sleep(0.5)
		except:
			print("Error processing URL: " + url)

def main():

	app = wx.App()

	global ex
	ex = GUI(None)

	global stockdict
	stockdict = {}

	products = []

	global bestbuylist
	bestbuylist = []

	global bbdict
	bbdict = {}

	global bbimgdict
	bbimgdict = {}

	global sku_dict
	sku_dict = {}

	global webhook_dict
	webhook_dict = return_data("./data/webhooks.json")

	global urldict
	urldict = return_data("./data/products.json")

	#set all URLs to be "out of stock" to begin
	for url in urldict:
		stockdict.update({url: 'False'}) 

	for prod in urldict:
		products.append((prod, urldict[prod], "Inactive"))
	ex.list.InsertColumn(0, 'URL', width=540)
	ex.list.InsertColumn(1, 'Webhook')
	ex.list.SetColumnWidth(col=1, width=100)
	ex.list.InsertColumn(2, 'Status')
	idx = 0
	for i in products:
		index = ex.list.InsertItem(idx, i[0])
		ex.list.SetItem(index, 1, i[1])
		ex.list.SetItem(index, 2, i[2])
		idx += 1

	ex.Show()
	app.MainLoop()


if __name__ == '__main__':
	main()