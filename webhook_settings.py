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
    print(data)
    write_data(path, data)

webhook_dict = return_data("./data/webhooks.json")

class WebhookSettings(wx.Frame):

    def __init__(self, *args, **kw):
        super(WebhookSettings, self).__init__(*args, **kw)

        self.InitUI()

    def InitUI(self):
        webhook_dict = return_data("./data/webhooks.json")
        panel = wx.Panel(self)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.listbox = wx.ListBox(panel)
        hbox.Add(self.listbox, wx.ID_ANY, wx.EXPAND | wx.ALL, 20)
        for webhook in webhook_dict:
            self.listbox.Append(webhook)

        btnPanel = wx.Panel(panel)
        vbox = wx.BoxSizer(wx.VERTICAL)
        newBtn = wx.Button(btnPanel, wx.ID_ANY, 'New', size=(90, 30))
        renBtn = wx.Button(btnPanel, wx.ID_ANY, 'Update', size=(90, 30))
        delBtn = wx.Button(btnPanel, wx.ID_ANY, 'Delete', size=(90, 30))
        clrBtn = wx.Button(btnPanel, wx.ID_ANY, 'Clear', size=(90, 30))

        self.Bind(wx.EVT_BUTTON, self.NewItem, id=newBtn.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnUpdate, id=renBtn.GetId())
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

        self.SetTitle('Webhook URL Manager')
        #self.Centre()
        self.Raise()

    def NewItem(self, event):

        webhook_dict = return_data("./data/webhooks.json")
        webhook_url = wx.GetTextFromUser('Enter a Webhook URL', 'Insert dialog')
        if webhook_url != '':
            webhook_name = wx.GetTextFromUser('Give the webhook URL a friendly name', 'Insert dialog')
            self.listbox.Append(webhook_name)
            set_data("./data/webhooks.json", webhook_name, webhook_url)
            webhook_dict = return_data("./data/webhooks.json")

    def OnUpdate(self, event):

        webhook_dict = return_data("./data/webhooks.json")
        sel = self.listbox.GetSelection()
        text = self.listbox.GetString(sel)
        webhook_to_modify = webhook_dict[text]
        modified_webhook_url = wx.GetTextFromUser('Update item', 'Update Item dialog', webhook_to_modify)

        if modified_webhook_url != '':
            webhook_dict.update({text: modified_webhook_url})
            set_data("./data/webhooks.json", text, modified_webhook_url)
            webhook_dict = return_data("./data/webhooks.json")
            #self.listbox.Delete(sel)
            #item_id = self.listbox.Insert(renamed, sel)
            #self.listbox.SetSelection(item_id)

    def OnDelete(self, event):
        
        webhook_dict = return_data("./data/webhooks.json")
        sel = self.listbox.GetSelection()
        text = self.listbox.GetString(sel)
        if sel != -1:
            self.listbox.Delete(sel)
            del webhook_dict[text]
            with open("./data/webhooks.json", "w") as file:
                json.dump(webhook_dict, file)
            file.close()
            webhook_dict = return_data("./data/webhooks.json")

    def OnClear(self, event):
        self.listbox.Clear()
        with open("./data/webhooks.json", "w") as file:
            json.dump({}, file)
        file.close()
        webhook_dict = return_data("./data/webhooks.json")


def main():

    app = wx.App()
    ex = WebhookSettings(None)
    ex.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()