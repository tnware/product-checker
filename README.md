Starting with the webhooks:

```
webhook_dict = {
"bb_switch": "",
"target_switch": "",
"target_switchlite": "",
"walmart_switch": ""

}
```

Insert a webhook URL per product type if you wish, otherwise put the same webhook URL for all

for example:

```
webhook_dict = {
"bb_switch": "http://webhook.url/123",
"target_switch": "http://webhook.url/123",
"target_switchlite": "http://webhook.url/123",
"walmart_switch": "http://webhook.url/123"

}
```


URLs are tracked in a separate dictionary:

```
urldict = {
"https://www.bestbuy.com/site/nintendo-switch-32gb-console-neon-red-neon-blue-joy-con/6364255.p?skuId=6364255": "bb_switch",
"https://www.target.com/p/nintendo-switch-with-neon-blue-and-neon-red-joy-con/-/A-77464001": "target_switch",
"https://www.target.com/p/nintendo-switch-with-gray-joy-con/-/A-77464002": "target_switch",
```

Add new URLs and classify them with a webhook type specified in the webhook dictionary

`"http://product.url": "webhook_name"`

Insert comma after entries up until the last entry. Default vaules are as follows:

```
urldict = {
"https://www.bestbuy.com/site/nintendo-switch-32gb-console-neon-red-neon-blue-joy-con/6364255.p?skuId=6364255": "bb_switch",
"https://www.target.com/p/nintendo-switch-with-neon-blue-and-neon-red-joy-con/-/A-77464001": "target_switch",
"https://www.target.com/p/nintendo-switch-with-gray-joy-con/-/A-77464002": "target_switch",
"https://www.bestbuy.com/site/nintendo-switch-32gb-console-gray-joy-con/6364253.p?skuId=6364253": "bb_switch",
"https://www.bestbuy.com/site/nintendo-switch-animal-crossing-new-horizons-edition-32gb-console-multi/6401728.p?skuId=6401728": "bb_switch",
"https://www.target.com/p/nintendo-switch-with-neon-blue-and-neon-red-joy-con-discontinued-by-manufacturer/-/A-52189185": "target_switch",
"https://www.target.com/p/nintendo-switch-lite-coral/-/A-79574296": "target_switchlite",
"https://www.target.com/p/nintendo-switch-lite-yellow/-/A-77419249": "target_switchlite",
"https://www.target.com/p/nintendo-switch-lite-gray/-/A-77419246": "target_switchlite",
"https://www.bestbuy.com/site/nintendo-geek-squad-certified-refurbished-switch-gray-joy-con/6376684.p?skuId=6376684": "bb_switch",
"https://www.target.com/p/nintendo-switch-lite-turquoise/-/A-77419248": "target_switchlite",
"https://www.bestbuy.com/site/nintendo-geek-squad-certified-refurbished-switch-neon-red-neon-blue-joy-con/6377113.p?skuId=6377113": "bb_switch",
"https://www.walmart.com/ip/Nintendo-Switch-Console-with-Neon-Blue-Red-Joy-Con/709776123": "walmart_switch",
"https://www.walmart.com/ip/Nintendo-Switch-Bundle-with-Mario-Red-Joy-Con-20-Nintendo-eShop-Credit-Carrying-Case/542896404": "walmart_switch",
"https://www.walmart.com/ip/Nintendo-Switch-Console-with-Gray-Joy-Con/994790027": "walmart_switch"


}
```


Run the script and watch the console/watch for discord notifications


I have had a few issues receiving consistent in-stock status for normal products so I added a 5sec delay to each walmart link. Not positive if it even helps, but if you bash walmart too quickly you will be returned "out of stock" without hesitation.

I can't guarantee the accuracy of this script as it's concstantly evolving and things break when new features are added. This certainly checks best buy stock, and i get tons of notifications about switch lites at target, but that's all i can vouch for.
