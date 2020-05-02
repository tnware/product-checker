import json
import wx

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

urldict = return_data("./data/products.json")
webhook_dict = return_data("./data/webhooks.json")

class WebhookSettings(wx.Frame):

    def __init__(self, *args, **kw):
        super(WebhookSettings, self).__init__(*args, **kw)

        self.InitUI()
        self.SetSize((750, 300))

    def OnChangeDepth(self, e):

        cdDialog = ChangeWebhookDialog(None,
            title='Change Webhook')
        cdDialog.ShowModal()
        cdDialog.Destroy()

    def InitUI(self):

        panel = wx.Panel(self)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        global listbox
        listbox = wx.ListBox(panel)
        self.listbox = listbox
        hbox.Add(self.listbox, wx.ID_ANY, wx.EXPAND | wx.ALL, 20)
        for url in urldict:
            self.listbox.Append(url)

        btnPanel = wx.Panel(panel)
        vbox = wx.BoxSizer(wx.VERTICAL)
        newBtn = wx.Button(btnPanel, wx.ID_ANY, 'Add URL', size=(90, 30))
        renBtn = wx.Button(btnPanel, wx.ID_ANY, 'Configure', size=(90, 30))
        delBtn = wx.Button(btnPanel, wx.ID_ANY, 'Delete', size=(90, 30))
        clrBtn = wx.Button(btnPanel, wx.ID_ANY, 'Clear', size=(90, 30))

        self.Bind(wx.EVT_BUTTON, self.NewItem, id=newBtn.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnChangeDepth, id=renBtn.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnDelete, id=delBtn.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnClear, id=clrBtn.GetId())
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.OnUpdate)

        vbox.Add((-1, 20))
        vbox.Add(newBtn)
        vbox.Add(renBtn, 0, wx.TOP, 5)
        vbox.Add(delBtn, 0, wx.TOP, 5)
        vbox.Add(clrBtn, 0, wx.TOP, 5)

        btnPanel.SetSizer(vbox)
        hbox.Add(btnPanel, 0.6, wx.EXPAND | wx.RIGHT, 20)
        panel.SetSizer(hbox)

        self.SetTitle('Product URL Manager')
        #self.Centre()
        self.RequestUserAttention()

    def NewItem(self, event):

        urldict = return_data("./data/products.json")
        product_url = wx.GetTextFromUser('Enter a Product URL', 'Insert dialog')
        product_webhook = "None"
        if product_url != '':
            self.listbox.Append(product_url)
            set_data("./data/products.json", product_url, product_webhook)
            urldict = return_data("./data/products.json")

    def OnUpdate(self, event):

        urldict = return_data("./data/products.json")
        webhook_dict = return_data("./data/webhooks.json")
        sel = self.listbox.GetSelection()
        product_url = self.listbox.GetString(sel)
        product_to_update = urldict[product_url]
        updated_product = wx.GetTextFromUser('Update item', 'Update Item dialog', product_to_update)

        if updated_product != '':
            urldict.update({product_url: updated_product})
            set_data("./data/products.json", product_url, updated_product)
            urldict = return_data("./data/products.json")
            #self.listbox.Delete(sel)
            #item_id = self.listbox.Insert(renamed, sel)
            #self.listbox.SetSelection(item_id)

    def OnDelete(self, event):
        
        urldict = return_data("./data/products.json")
        sel = self.listbox.GetSelection()
        text = self.listbox.GetString(sel)
        if sel != -1:
            self.listbox.Delete(sel)
            del urldict[text]
            with open("./data/products.json", "w") as file:
                json.dump(urldict, file)
            file.close()
            urldict = return_data("./data/products.json")

    def OnClear(self, event):
        self.listbox.Clear()
        with open("./data/products.json", "w") as file:
            json.dump({}, file)
        file.close()
        urldict = return_data("./data/products.json")

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
        url_key = listbox.GetSelection()
        if url_key == -1:
            print("An error ocurred. Did you select a URL before clicking configure?")
        else:
            url = listbox.GetString(url_key)
            new_webhook_key = combo.GetSelection()
            new_webhook = combo.GetString(new_webhook_key)
            print(url, new_webhook)
            urldict.update({url: new_webhook})
            set_data("./data/products.json", url, new_webhook)
        self.Destroy()

    def OnClose(self, e):

        self.Destroy()

def main():

    app = wx.App()
    ex = WebhookSettings(None)
    ex.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()