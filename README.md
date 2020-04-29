# Get webhook notifications when products come in stock. 

### Supports

- Target
- BestBuy (having issues as of 4/29)
- B&H Photo/Video
- Walmart (requires a waiting period between page loads or a rotating proxy (not supported within the script) to get accurate stock results)


## How To Use


### Webhooks:
CURRENTLY ONLY SUPPORTS DISCORD CHANNELS.

To add a different webhook provider, you must update the JSON payload that's being sent from each class: `slack_data = {'content': current_time + " " + title + " in stock at Target - " + url}` usually "content" will need to be changed, check the documentation for your webhook provider.

Add your webhook URL(s) to the script in the following format:
```
webhook_dict = {
"webhook_1": "https://discordapp.com/api/webhooks/.../.../webhook1",
"webhook_2": "https://discordapp.com/api/webhooks/.../.../webhook2",
"webhook_3": "https://discordapp.com/api/webhooks/.../.../webhook3"

}
```
You don't need more than one webhook URL, but this is useful if you are tracking multiple products, you can streamline your notifications so you can mute certain channels when you don't want to get notifications about their stock but still want the script to run it.


### Adding URLs:

URLs are tracked in a separate dictionary:

While the URL is important, the name of the webhook is equally important:
```
urldict = {
"https://www.bhphotovideo.com/c/product/1496116-REG/nintendo_hadskabaa_switch_with_neon_blue.html": "webhook_1",
"https://www.target.com/p/nintendo-switch-with-neon-blue-and-neon-red-joy-con/-/A-77464001": "webhook_2",
"https://www.walmart.com/ip/Nintendo-Switch-Console-with-Gray-Joy-Con/994790027": "webhook_3"

}
```

Add new URLs and classify them with a webhook type specified in the webhook dictionary

`"http://product.url": "webhook_name"`

You can assign more than one url to a webhook, so for example send all nintendo switch links to webhook_1, and then send an oculus rift link to webhook_2. You could split it up by product or by site, or just have them all go to the same webhook.


### Finally:

Run the script and watch the console/watch for discord notifications


I have had a few issues receiving consistent in-stock status for normal products so I added a 5sec delay to each walmart link. Not positive if it even helps, but if you bash walmart too quickly you will be returned "out of stock" without hesitation.

I can't guarantee the accuracy of this script as it's concstantly evolving and things break when new features are added. This certainly checks best buy stock, and i get tons of notifications about switch lites at target, but that's all i can vouch for.


# Notes:

There will always be a delay after each walmart link. If you have lots of walmart links and want to adjust that delay, search for `time.sleep(5)` in the walmart section of the end of the file and change the 5 to a different number. Remember if you load pages too quickly the stock is automatically considered out of stock and you will not receive a notification even if it comes in stock. 


The file by default loops ever 1second because it assumes you have walmart links at the end which add more time to the delay. If you don't have any walmart links and it's reloading too quickly, change the time from `time.sleep(1)` at the very end of the file to something more like 10. 
