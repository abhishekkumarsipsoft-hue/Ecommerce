# http-log.md

API used: https://dummyjson.com (public, read-only JSON API with fake products, it even has bag categories, so it matches my bags store idea).

Command used for everything: `curl -i <url>`  (`-i` shows the response headers along with the body)

Run date: 10-10-26

---

## 1. Get one product

```
curl -i https://dummyjson.com/products/1
```

Output:
```
HTTP/1.1 200 OK
Date: Tue, 13 Oct 2026 08:20:34 GMT
Content-Type: application/json; charset=utf-8
Transfer-Encoding: chunked
Connection: keep-alive
access-control-allow-credentials: true
Nel: {"report_to":"cf-nel","success_fraction":0.0,"max_age":604800}
etag: W/"5e6-LuZgXJ6APIKHswyRKC9GQ6dxUNE"
strict-transport-security: max-age=15552000; includeSubDomains
vary: Origin, Accept-Encoding
x-content-type-options: nosniff
x-dns-prefetch-control: off
x-download-options: noopen
x-frame-options: SAMEORIGIN
x-ratelimit-limit: 100
x-ratelimit-remaining: 99
x-ratelimit-reset: 1791843140
x-xss-protection: 1; mode=block
Age: 36494
Cache-Control: no-store
cf-cache-status: HIT
Report-To: {"group":"cf-nel","max_age":604800,"endpoints":[{"url":"https://a.nel.cloudflare.com/report/v4?s=oSJsKf3ipMbiL%2FQ5KXvTZzX%2FU1CbWvCfkZYECAOiNE32G6pJBOkrwkLXrE8DIOsu%2BySNWSFJZmw6lHn%2BDg0bQR3BBD9shMkknTD3HV4gCWW2kYCeu8WtNL3yM%2Fz0sn4rltBWDV9M%2F1tHSrhT"}]}
Server: cloudflare
CF-RAY: a49ced02686d06fa-HKG

{"id":1,"title":"Essence Mascara Lash Princess","description":"The Essence Mascara Lash Princess is a popular mascara known for its volumizing and lengthening effects. Achieve dramatic lashes with this long-lasting and cruelty-free formula.","category":"beauty","price":9.99,"discountPercentage":10.48,"rating":2.56,"stock":99,"tags":["beauty","mascara"],"brand":"Essence","sku":"BEA-ESS-ESS-001","weight":4,"dimensions":{"width":15.14,"height":13.08,"depth":22.99},"warrantyInformation":"1 week warranty","shippingInformation":"Ships in 3-5 business days","availabilityStatus":"In Stock","reviews":[{"rating":3,"comment":"Would not recommend!","date":"2025-04-30T09:41:02.053Z","reviewerName":"Eleanor Collins","reviewerEmail":"eleanor.collins@x.dummyjson.com"},{"rating":4,"comment":"Very satisfied!","date":"2025-04-30T09:41:02.053Z","reviewerName":"Lucas Gordon","reviewerEmail":"lucas.gordon@x.dummyjson.com"},{"rating":5,"comment":"Highly impressed!","date":"2025-04-30T09:41:02.053Z","reviewerName":"Eleanor Collins","reviewerEmail":"eleanor.collins@x.dummyjson.com"}],"returnPolicy":"No return policy","minimumOrderQuantity":48,"meta":{"createdAt":"2025-10-09T14:47:01.588Z","updatedAt":"2026-05-23T11:27:41.868Z","barcode":"5784719087687","qrCode":"https://cdn.dummyjson.com/public/qr-code.png"},"images":["https://cdn.dummyjson.com/product-images/beauty/essence-mascara-lash-princess/1.webp"],"thumbnail":"https://cdn.dummyjson.com/product-images/beauty/essence-mascara-lash-princess/thumbnail.webp"}
```

Note: `200 OK` means the server found the product and sent it. `Content-Type: application/json` means the body is JSON, so my React app can parse it with `res.json()`.

---

## 2. Get a list with limit

```
curl -i "https://dummyjson.com/products?limit=3"
```

Output:
```
HTTP/1.1 200 OK
Date: Tue, 13 Oct 2026 08:21:43 GMT
Content-Type: application/json; charset=utf-8
Transfer-Encoding: chunked
Connection: keep-alive
access-control-allow-credentials: true
Nel: {"report_to":"cf-nel","success_fraction":0.0,"max_age":604800}
etag: W/"11bf-tlldaNxTnp0hDgZqUroOj8H12o8"
strict-transport-security: max-age=15552000; includeSubDomains
vary: Origin, Accept-Encoding
x-content-type-options: nosniff
x-dns-prefetch-control: off
x-download-options: noopen
x-frame-options: SAMEORIGIN
x-ratelimit-limit: 100
x-ratelimit-remaining: 99
x-ratelimit-reset: 1791879714
x-xss-protection: 1; mode=block
cf-cache-status: DYNAMIC
Report-To: {"group":"cf-nel","max_age":604800,"endpoints":[{"url":"https://a.nel.cloudflare.com/report/v4?s=IP%2Bf0QgGE5V4htMQtnmbsz%2FwWiQ%2BJGmYW3WLO4ckbMvD00KRXMMQ0YAdc4e3YtW8cjaAp34V%2Bj%2F3QzDg4P8yvcRc5yhiDkXNGwV2DY4JCjvZXLLLywCAE5V%2BHlOLbuTTyt%2FG%2BKl2kE5Y7YL7"}]}
Server: cloudflare
CF-RAY: a49ceeb07a24fe90-SIN

{"products":[{"id":1,"title":"Essence Mascara Lash Princess","description":"The Essence Mascara Lash Princess is a popular mascara known for its volumizing and lengthening effects. Achieve dramatic lashes with this long-lasting and cruelty-free formula.","category":"beauty","price":9.99,"discountPercentage":10.48,"rating":2.56,"stock":99,"tags":["beauty","mascara"],"brand":"Essence","sku":"BEA-ESS-ESS-001","weight":4,"dimensions":{"width":15.14,"height":13.08,"depth":22.99},"warrantyInformation":"1 week warranty","shippingInformation":"Ships in 3-5 business days","availabilityStatus":"In Stock","reviews":[{"rating":3,"comment":"Would not recommend!","date":"2025-04-30T09:41:02.053Z","reviewerName":"Eleanor Collins","reviewerEmail":"eleanor.collins@x.dummyjson.com"},{"rating":4,"comment":"Very satisfied!","date":"2025-04-30T09:41:02.053Z","reviewerName":"Lucas Gordon","reviewerEmail":"lucas.gordon@x.dummyjson.com"},{"rating":5,"comment":"Highly impressed!","date":"2025-04-30T09:41:02.053Z","reviewerName":"Eleanor Collins","reviewerEmail":"eleanor.collins@x.dummyjson.com"}],"returnPolicy":"No return policy","minimumOrderQuantity":48,"meta":{"createdAt":"2025-10-09T14:47:01.588Z","updatedAt":"2026-05-23T11:27:41.868Z","barcode":"5784719087687","qrCode":"https://cdn.dummyjson.com/public/qr-code.png"},"images":["https://cdn.dummyjson.com/product-images/beauty/essence-mascara-lash-princess/1.webp"],"thumbnail":"https://cdn.dummyjson.com/product-images/beauty/essence-mascara-lash-princess/thumbnail.webp"},{"id":2,"title":"Eyeshadow Palette with Mirror","description":"The Eyeshadow Palette with Mirror offers a versatile range of eyeshadow shades for creating stunning eye looks. With a built-in mirror, it's convenient for on-the-go makeup application.","category":"beauty","price":19.99,"discountPercentage":18.19,"rating":2.86,"stock":34,"tags":["beauty","eyeshadow"],"brand":"Glamour Beauty","sku":"BEA-GLA-EYE-002","weight":9,"dimensions":{"width":9.26,"height":22.47,"depth":27.67},"warrantyInformation":"1 year warranty","shippingInformation":"Ships in 2 weeks","availabilityStatus":"In Stock","reviews":[{"rating":5,"comment":"Great product!","date":"2025-04-30T09:41:02.053Z","reviewerName":"Savannah Gomez","reviewerEmail":"savannah.gomez@x.dummyjson.com"},{"rating":4,"comment":"Awesome product!","date":"2025-04-30T09:41:02.053Z","reviewerName":"Christian Perez","reviewerEmail":"christian.perez@x.dummyjson.com"},{"rating":1,"comment":"Poor quality!","date":"2025-04-30T09:41:02.053Z","reviewerName":"Nicholas Bailey","reviewerEmail":"nicholas.bailey@x.dummyjson.com"}],"returnPolicy":"7 days return policy","minimumOrderQuantity":20,"meta":{"createdAt":"2024-12-03T11:29:45.706Z","updatedAt":"2025-08-24T16:52:47.806Z","barcode":"9170275171413","qrCode":"https://cdn.dummyjson.com/public/qr-code.png"},"images":["https://cdn.dummyjson.com/product-images/beauty/eyeshadow-palette-with-mirror/1.webp"],"thumbnail":"https://cdn.dummyjson.com/product-images/beauty/eyeshadow-palette-with-mirror/thumbnail.webp"},{"id":3,"title":"Powder Canister","description":"The Powder Canister is a finely milled setting powder designed to set makeup and control shine. With a lightweight and translucent formula, it provides a smooth and matte finish.","category":"beauty","price":14.99,"discountPercentage":9.84,"rating":4.64,"stock":89,"tags":["beauty","face powder"],"brand":"Velvet Touch","sku":"BEA-VEL-POW-003","weight":8,"dimensions":{"width":29.27,"height":27.93,"depth":20.59},"warrantyInformation":"3 months warranty","shippingInformation":"Ships in 1-2 business days","availabilityStatus":"In Stock","reviews":[{"rating":4,"comment":"Would buy again!","date":"2025-04-30T09:41:02.053Z","reviewerName":"Alexander Jones","reviewerEmail":"alexander.jones@x.dummyjson.com"},{"rating":5,"comment":"Highly impressed!","date":"2025-04-30T09:41:02.053Z","reviewerName":"Elijah Cruz","reviewerEmail":"elijah.cruz@x.dummyjson.com"},{"rating":1,"comment":"Very dissatisfied!","date":"2025-04-30T09:41:02.053Z","reviewerName":"Avery Perez","reviewerEmail":"avery.perez@x.dummyjson.com"}],"returnPolicy":"No return policy","minimumOrderQuantity":22,"meta":{"createdAt":"2025-01-08T18:30:12.844Z","updatedAt":"2025-11-26T14:49:26.980Z","barcode":"8418883906837","qrCode":"https://cdn.dummyjson.com/public/qr-code.png"},"images":["https://cdn.dummyjson.com/product-images/beauty/powder-canister/1.webp"],"thumbnail":"https://cdn.dummyjson.com/product-images/beauty/powder-canister/thumbnail.webp"}],"total":194,"skip":0,"limit":3}
```

Note: `200 OK` again. Query string `limit=3` is how we ask for only 3 items. Content-Type is JSON (a list inside an object this time).

---

## 3. Search for bags

```
curl -i "https://dummyjson.com/products/search?q=bag"
```

Output:
```
HTTP/1.1 200 OK
Date: Tue, 13 Oct 2026 08:22:27 GMT
Content-Type: application/json; charset=utf-8
Transfer-Encoding: chunked
Connection: keep-alive
access-control-allow-credentials: true
Nel: {"report_to":"cf-nel","success_fraction":0.0,"max_age":604800}
etag: W/"1a56-OpCuq7ybQWp7A9VXiUm7nVUvWCw"
strict-transport-security: max-age=15552000; includeSubDomains
vary: Origin, Accept-Encoding
x-content-type-options: nosniff
x-dns-prefetch-control: off
x-download-options: noopen
x-frame-options: SAMEORIGIN
x-ratelimit-limit: 100
x-ratelimit-remaining: 99
x-ratelimit-reset: 1791879754
x-xss-protection: 1; mode=block
cf-cache-status: DYNAMIC
Report-To: {"group":"cf-nel","max_age":604800,"endpoints":[{"url":"https://a.nel.cloudflare.com/report/v4?s=mbn%2FtPTxl8MzPDvkN83OuLF7%2FLv3Rux9MG6bq%2BhaBWoFMR3QhH65EhNL5RIJGIlKgPsPfCjxmdkVG%2FkNRSHz%2F5nz4FBsC61en9CewIrdWypcFCRWVq2bF8gVRl1Cuv5uyIytl%2FG7lSuKLCNs"}]}
Server: cloudflare
CF-RAY: a49cefc3dfd98b92-HKG

{"products":[{"id":172,"title":"Blue Women's Handbag","description":"The Blue Women's Handbag is a stylish and spacious accessory for everyday use. With a vibrant blue color and multiple compartments, it combines fashion and functionality.","category":"womens-bags","price":49.99,"discountPercentage":17.88,"rating":2.92,"stock":76,"tags":["fashion accessories","handbags"],"brand":"Fashionista","sku":"WOM-FAS-BLU-172","weight":7,"dimensions":{"width":14.12,"height":11.89,"depth":25.69},"warrantyInformation":"1 year warranty","shippingInformation":"Ships in 1 week","availabilityStatus":"In Stock","reviews":[{"rating":3,"comment":"Waste of money!","date":"2025-04-30T09:41:02.054Z","reviewerName":"Grace Perry","reviewerEmail":"grace.perry@x.dummyjson.com"},{"rating":3,"comment":"Not worth the price!","date":"2025-04-30T09:41:02.054Z","reviewerName":"Evelyn Sanchez","reviewerEmail":"evelyn.sanchez@x.dummyjson.com"},{"rating":4,"comment":"Highly impressed!","date":"2025-04-30T09:41:02.054Z","reviewerName":"Eli Ward","reviewerEmail":"eli.ward@x.dummyjson.com"}],"returnPolicy":"7 days return policy","minimumOrderQuantity":5,"meta":{"createdAt":"2026-06-27T22:15:50.768Z","updatedAt":"2026-06-28T15:34:32.415Z","barcode":"0558998280008","qrCode":"https://cdn.dummyjson.com/public/qr-code.png"},"images":["https://cdn.dummyjson.com/product-images/womens-bags/blue-women's-handbag/1.webp","https://cdn.dummyjson.com/product-images/womens-bags/blue-women's-handbag/2.webp","https://cdn.dummyjson.com/product-images/womens-bags/blue-women's-handbag/3.webp"],"thumbnail":"https://cdn.dummyjson.com/product-images/womens-bags/blue-women's-handbag/thumbnail.webp"},{"id":173,"title":"Heshe Women's Leather Bag","description":"The Heshe Women's Leather Bag is a luxurious and high-quality leather bag for the sophisticated woman. With a timeless design and durable craftsmanship, it's a versatile accessory.","category":"womens-bags","price":129.99,"discountPercentage":3.87,"rating":4.92,"stock":99,"tags":["fashion accessories","leather bags"],"brand":"Heshe","sku":"WOM-HES-HES-173","weight":3,"dimensions":{"width":28.66,"height":20.56,"depth":6.62},"warrantyInformation":"5 year warranty","shippingInformation":"Ships overnight","availabilityStatus":"In Stock","reviews":[{"rating":5,"comment":"Excellent quality!","date":"2025-04-30T09:41:02.054Z","reviewerName":"Hunter Gordon","reviewerEmail":"hunter.gordon@x.dummyjson.com"},{"rating":4,"comment":"Awesome product!","date":"2025-04-30T09:41:02.054Z","reviewerName":"Mason Parker","reviewerEmail":"mason.parker@x.dummyjson.com"},{"rating":4,"comment":"Awesome product!","date":"2025-04-30T09:41:02.054Z","reviewerName":"William Gonzalez","reviewerEmail":"william.gonzalez@x.dummyjson.com"}],"returnPolicy":"90 days return policy","minimumOrderQuantity":5,"meta":{"createdAt":"2026-05-10T11:36:16.743Z","updatedAt":"2026-05-14T13:38:36.163Z","barcode":"4616258239513","qrCode":"https://cdn.dummyjson.com/public/qr-code.png"},"images":["https://cdn.dummyjson.com/product-images/womens-bags/heshe-women's-leather-bag/1.webp","https://cdn.dummyjson.com/product-images/womens-bags/heshe-women's-leather-bag/2.webp","https://cdn.dummyjson.com/product-images/womens-bags/heshe-women's-leather-bag/3.webp"],"thumbnail":"https://cdn.dummyjson.com/product-images/womens-bags/heshe-women's-leather-bag/thumbnail.webp"},{"id":174,"title":"Prada Women Bag","description":"The Prada Women Bag is an iconic designer bag that exudes elegance and luxury. Crafted with precision and featuring the Prada logo, it's a statement piece for fashion enthusiasts.","category":"womens-bags","price":599.99,"discountPercentage":14.09,"rating":2.71,"stock":75,"tags":["fashion accessories","designer bags"],"brand":"Prada","sku":"WOM-PRA-PRA-174","weight":4,"dimensions":{"width":21.84,"height":22.19,"depth":13.41},"warrantyInformation":"3 year warranty","shippingInformation":"Ships in 1-2 business days","availabilityStatus":"In Stock","reviews":[{"rating":2,"comment":"Would not buy again!","date":"2025-04-30T09:41:02.054Z","reviewerName":"Caleb Perkins","reviewerEmail":"caleb.perkins@x.dummyjson.com"},{"rating":4,"comment":"Great value for money!","date":"2025-04-30T09:41:02.054Z","reviewerName":"Carter Baker","reviewerEmail":"carter.baker@x.dummyjson.com"},{"rating":5,"comment":"Highly recommended!","date":"2025-04-30T09:41:02.054Z","reviewerName":"Lucas Ramirez","reviewerEmail":"lucas.ramirez@x.dummyjson.com"}],"returnPolicy":"60 days return policy","minimumOrderQuantity":1,"meta":{"createdAt":"2025-10-22T00:38:28.734Z","updatedAt":"2026-06-07T06:16:56.982Z","barcode":"9614237439330","qrCode":"https://cdn.dummyjson.com/public/qr-code.png"},"images":["https://cdn.dummyjson.com/product-images/womens-bags/prada-women-bag/1.webp","https://cdn.dummyjson.com/product-images/womens-bags/prada-women-bag/2.webp","https://cdn.dummyjson.com/product-images/womens-bags/prada-women-bag/3.webp"],"thumbnail":"https://cdn.dummyjson.com/product-images/womens-bags/prada-women-bag/thumbnail.webp"},{"id":176,"title":"Women Handbag Black","description":"The Women Handbag in Black is a classic and versatile accessory that complements various outfits. With a timeless black color and functional design, it's a must-have in every woman's wardrobe.","category":"womens-bags","price":59.99,"discountPercentage":11.63,"rating":2.89,"stock":11,"tags":["fashion accessories","handbags"],"brand":"Elegance Collection","sku":"WOM-ELE-WOM-176","weight":6,"dimensions":{"width":29.76,"height":12.34,"depth":15.82},"warrantyInformation":"Lifetime warranty","shippingInformation":"Ships in 1 month","availabilityStatus":"In Stock","reviews":[{"rating":4,"comment":"Very pleased!","date":"2025-04-30T09:41:02.054Z","reviewerName":"Natalie Price","reviewerEmail":"natalie.price@x.dummyjson.com"},{"rating":5,"comment":"Great product!","date":"2025-04-30T09:41:02.054Z","reviewerName":"Emily Johnson","reviewerEmail":"emily.johnson@x.dummyjson.com"},{"rating":1,"comment":"Waste of money!","date":"2025-04-30T09:41:02.054Z","reviewerName":"Henry Hill","reviewerEmail":"henry.hill@x.dummyjson.com"}],"returnPolicy":"60 days return policy","minimumOrderQuantity":9,"meta":{"createdAt":"2026-03-28T09:18:31.387Z","updatedAt":"2026-06-28T07:52:29.821Z","barcode":"4283648448769","qrCode":"https://cdn.dummyjson.com/public/qr-code.png"},"images":["https://cdn.dummyjson.com/product-images/womens-bags/women-handbag-black/1.webp","https://cdn.dummyjson.com/product-images/womens-bags/women-handbag-black/2.webp","https://cdn.dummyjson.com/product-images/womens-bags/women-handbag-black/3.webp"],"thumbnail":"https://cdn.dummyjson.com/product-images/womens-bags/women-handbag-black/thumbnail.webp"}],"total":4,"skip":0,"limit":4}
```

Note: `200 OK`. Search is also just a GET with `q=` in the URL. This is the same thing my store's search box will do.

---

## 4. Products of one category

```
curl -i https://dummyjson.com/products/category/womens-bags
```

Output:
```
HTTP/1.1 200 OK
Date: Tue, 13 Oct 2026 08:23:00 GMT
Content-Type: application/json; charset=utf-8
Transfer-Encoding: chunked
Connection: keep-alive
access-control-allow-credentials: true
Nel: {"report_to":"cf-nel","success_fraction":0.0,"max_age":604800}
etag: W/"210b-iznDkVMCuKb+eJCN62WocjTNeCc"
strict-transport-security: max-age=15552000; includeSubDomains
vary: Origin, Accept-Encoding
x-content-type-options: nosniff
x-dns-prefetch-control: off
x-download-options: noopen
x-frame-options: SAMEORIGIN
x-ratelimit-limit: 100
x-ratelimit-remaining: 99
x-ratelimit-reset: 1791879784
x-xss-protection: 1; mode=block
cf-cache-status: DYNAMIC
Report-To: {"group":"cf-nel","max_age":604800,"endpoints":[{"url":"https://a.nel.cloudflare.com/report/v4?s=Y8kMOuRRnrQPth7SYoQ15rSrlinzAJQGibWcMWkVCzrc%2BOZvfOJFAk%2B5Ebydq4J%2BAsPWOq9TUhHkQx01YgjFj2h8Zggdm4EfvRx%2BbMlECgBrerLwASOG8tCNZJaxYjykZhAIJcb5HT50LHcX"}]}
Server: cloudflare
CF-RAY: a49cf0944dbb1e93-SIN

{"products":[{"id":172,"title":"Blue Women's Handbag","description":"The Blue Women's Handbag is a stylish and spacious accessory for everyday use. With a vibrant blue color and multiple compartments, it combines fashion and functionality.","category":"womens-bags","price":49.99,"discountPercentage":17.88,"rating":2.92,"stock":76,"tags":["fashion accessories","handbags"],"brand":"Fashionista","sku":"WOM-FAS-BLU-172","weight":7,"dimensions":{"width":14.12,"height":11.89,"depth":25.69},"warrantyInformation":"1 year warranty","shippingInformation":"Ships in 1 week","availabilityStatus":"In Stock","reviews":[{"rating":3,"comment":"Waste of money!","date":"2025-04-30T09:41:02.054Z","reviewerName":"Grace Perry","reviewerEmail":"grace.perry@x.dummyjson.com"},{"rating":3,"comment":"Not worth the price!","date":"2025-04-30T09:41:02.054Z","reviewerName":"Evelyn Sanchez","reviewerEmail":"evelyn.sanchez@x.dummyjson.com"},{"rating":4,"comment":"Highly impressed!","date":"2025-04-30T09:41:02.054Z","reviewerName":"Eli Ward","reviewerEmail":"eli.ward@x.dummyjson.com"}],"returnPolicy":"7 days return policy","minimumOrderQuantity":5,"meta":{"createdAt":"2026-06-27T22:15:50.768Z","updatedAt":"2026-06-28T15:34:32.415Z","barcode":"0558998280008","qrCode":"https://cdn.dummyjson.com/public/qr-code.png"},"images":["https://cdn.dummyjson.com/product-images/womens-bags/blue-women's-handbag/1.webp","https://cdn.dummyjson.com/product-images/womens-bags/blue-women's-handbag/2.webp","https://cdn.dummyjson.com/product-images/womens-bags/blue-women's-handbag/3.webp"],"thumbnail":"https://cdn.dummyjson.com/product-images/womens-bags/blue-women's-handbag/thumbnail.webp"},{"id":173,"title":"Heshe Women's Leather Bag","description":"The Heshe Women's Leather Bag is a luxurious and high-quality leather bag for the sophisticated woman. With a timeless design and durable craftsmanship, it's a versatile accessory.","category":"womens-bags","price":129.99,"discountPercentage":3.87,"rating":4.92,"stock":99,"tags":["fashion accessories","leather bags"],"brand":"Heshe","sku":"WOM-HES-HES-173","weight":3,"dimensions":{"width":28.66,"height":20.56,"depth":6.62},"warrantyInformation":"5 year warranty","shippingInformation":"Ships overnight","availabilityStatus":"In Stock","reviews":[{"rating":5,"comment":"Excellent quality!","date":"2025-04-30T09:41:02.054Z","reviewerName":"Hunter Gordon","reviewerEmail":"hunter.gordon@x.dummyjson.com"},{"rating":4,"comment":"Awesome product!","date":"2025-04-30T09:41:02.054Z","reviewerName":"Mason Parker","reviewerEmail":"mason.parker@x.dummyjson.com"},{"rating":4,"comment":"Awesome product!","date":"2025-04-30T09:41:02.054Z","reviewerName":"William Gonzalez","reviewerEmail":"william.gonzalez@x.dummyjson.com"}],"returnPolicy":"90 days return policy","minimumOrderQuantity":5,"meta":{"createdAt":"2026-05-10T11:36:16.743Z","updatedAt":"2026-05-14T13:38:36.163Z","barcode":"4616258239513","qrCode":"https://cdn.dummyjson.com/public/qr-code.png"},"images":["https://cdn.dummyjson.com/product-images/womens-bags/heshe-women's-leather-bag/1.webp","https://cdn.dummyjson.com/product-images/womens-bags/heshe-women's-leather-bag/2.webp","https://cdn.dummyjson.com/product-images/womens-bags/heshe-women's-leather-bag/3.webp"],"thumbnail":"https://cdn.dummyjson.com/product-images/womens-bags/heshe-women's-leather-bag/thumbnail.webp"},{"id":174,"title":"Prada Women Bag","description":"The Prada Women Bag is an iconic designer bag that exudes elegance and luxury. Crafted with precision and featuring the Prada logo, it's a statement piece for fashion enthusiasts.","category":"womens-bags","price":599.99,"discountPercentage":14.09,"rating":2.71,"stock":75,"tags":["fashion accessories","designer bags"],"brand":"Prada","sku":"WOM-PRA-PRA-174","weight":4,"dimensions":{"width":21.84,"height":22.19,"depth":13.41},"warrantyInformation":"3 year warranty","shippingInformation":"Ships in 1-2 business days","availabilityStatus":"In Stock","reviews":[{"rating":2,"comment":"Would not buy again!","date":"2025-04-30T09:41:02.054Z","reviewerName":"Caleb Perkins","reviewerEmail":"caleb.perkins@x.dummyjson.com"},{"rating":4,"comment":"Great value for money!","date":"2025-04-30T09:41:02.054Z","reviewerName":"Carter Baker","reviewerEmail":"carter.baker@x.dummyjson.com"},{"rating":5,"comment":"Highly recommended!","date":"2025-04-30T09:41:02.054Z","reviewerName":"Lucas Ramirez","reviewerEmail":"lucas.ramirez@x.dummyjson.com"}],"returnPolicy":"60 days return policy","minimumOrderQuantity":1,"meta":{"createdAt":"2025-10-22T00:38:28.734Z","updatedAt":"2026-06-07T06:16:56.982Z","barcode":"9614237439330","qrCode":"https://cdn.dummyjson.com/public/qr-code.png"},"images":["https://cdn.dummyjson.com/product-images/womens-bags/prada-women-bag/1.webp","https://cdn.dummyjson.com/product-images/womens-bags/prada-women-bag/2.webp","https://cdn.dummyjson.com/product-images/womens-bags/prada-women-bag/3.webp"],"thumbnail":"https://cdn.dummyjson.com/product-images/womens-bags/prada-women-bag/thumbnail.webp"},{"id":175,"title":"White Faux Leather Backpack","description":"The White Faux Leather Backpack is a trendy and practical backpack for the modern woman. With a sleek white design and ample storage space, it's perfect for both casual and on-the-go styles.","category":"womens-bags","price":39.99,"discountPercentage":15.2,"rating":3.36,"stock":39,"tags":["fashion accessories","backpacks"],"brand":"Urban Chic","sku":"WOM-URB-WHI-175","weight":7,"dimensions":{"width":14.31,"height":23.29,"depth":28.91},"warrantyInformation":"2 year warranty","shippingInformation":"Ships in 1 week","availabilityStatus":"In Stock","reviews":[{"rating":4,"comment":"Awesome product!","date":"2025-04-30T09:41:02.054Z","reviewerName":"Ava Harrison","reviewerEmail":"ava.harrison@x.dummyjson.com"},{"rating":1,"comment":"Not as described!","date":"2025-04-30T09:41:02.054Z","reviewerName":"Liam Garcia","reviewerEmail":"liam.garcia@x.dummyjson.com"},{"rating":5,"comment":"Great value for money!","date":"2025-04-30T09:41:02.054Z","reviewerName":"Cameron Perez","reviewerEmail":"cameron.perez@x.dummyjson.com"}],"returnPolicy":"90 days return policy","minimumOrderQuantity":7,"meta":{"createdAt":"2026-01-28T14:43:17.297Z","updatedAt":"2026-03-03T21:55:58.379Z","barcode":"8983558170212","qrCode":"https://cdn.dummyjson.com/public/qr-code.png"},"images":["https://cdn.dummyjson.com/product-images/womens-bags/white-faux-leather-backpack/1.webp","https://cdn.dummyjson.com/product-images/womens-bags/white-faux-leather-backpack/2.webp","https://cdn.dummyjson.com/product-images/womens-bags/white-faux-leather-backpack/3.webp"],"thumbnail":"https://cdn.dummyjson.com/product-images/womens-bags/white-faux-leather-backpack/thumbnail.webp"},{"id":176,"title":"Women Handbag Black","description":"The Women Handbag in Black is a classic and versatile accessory that complements various outfits. With a timeless black color and functional design, it's a must-have in every woman's wardrobe.","category":"womens-bags","price":59.99,"discountPercentage":11.63,"rating":2.89,"stock":11,"tags":["fashion accessories","handbags"],"brand":"Elegance Collection","sku":"WOM-ELE-WOM-176","weight":6,"dimensions":{"width":29.76,"height":12.34,"depth":15.82},"warrantyInformation":"Lifetime warranty","shippingInformation":"Ships in 1 month","availabilityStatus":"In Stock","reviews":[{"rating":4,"comment":"Very pleased!","date":"2025-04-30T09:41:02.054Z","reviewerName":"Natalie Price","reviewerEmail":"natalie.price@x.dummyjson.com"},{"rating":5,"comment":"Great product!","date":"2025-04-30T09:41:02.054Z","reviewerName":"Emily Johnson","reviewerEmail":"emily.johnson@x.dummyjson.com"},{"rating":1,"comment":"Waste of money!","date":"2025-04-30T09:41:02.054Z","reviewerName":"Henry Hill","reviewerEmail":"henry.hill@x.dummyjson.com"}],"returnPolicy":"60 days return policy","minimumOrderQuantity":9,"meta":{"createdAt":"2026-03-28T09:18:31.387Z","updatedAt":"2026-06-28T07:52:29.821Z","barcode":"4283648448769","qrCode":"https://cdn.dummyjson.com/public/qr-code.png"},"images":["https://cdn.dummyjson.com/product-images/womens-bags/women-handbag-black/1.webp","https://cdn.dummyjson.com/product-images/womens-bags/women-handbag-black/2.webp","https://cdn.dummyjson.com/product-images/womens-bags/women-handbag-black/3.webp"],"thumbnail":"https://cdn.dummyjson.com/product-images/womens-bags/women-handbag-black/thumbnail.webp"}],"total":5,"skip":0,"limit":5}
```

Note: `200 OK`, JSON. The category name is part of the URL path, so it is like a "folder" of products.

---

## 5. Product that does not exist (on purpose, 404)

```
curl -i https://dummyjson.com/products/99999
```

Output:
```
HTTP/1.1 404 Not Found
Date: Tue, 13 Oct 2026 08:23:40 GMT
Content-Type: application/json; charset=utf-8
Content-Length: 47
Connection: keep-alive
access-control-allow-credentials: true
etag: W/"2f-G103fHNBKhGWErLBkLpyXDmxfo4"
strict-transport-security: max-age=15552000; includeSubDomains
vary: Origin, Accept-Encoding
x-content-type-options: nosniff
x-dns-prefetch-control: off
x-download-options: noopen
x-frame-options: SAMEORIGIN
x-ratelimit-limit: 100
x-ratelimit-remaining: 98
x-ratelimit-reset: 1791879824
x-xss-protection: 1; mode=block
cf-cache-status: DYNAMIC
Report-To: {"group":"cf-nel","max_age":604800,"endpoints":[{"url":"https://a.nel.cloudflare.com/report/v4?s=UTKQI35ow3%2F4c%2BTvW49HP7xHrLu6N%2BOjEgfeMoElzZrH7ovcLCnbMDS%2BsfP%2Fkjrk2B75gWm4Ls3cZpJJhLn1SFsr3UHsRe7Luo60mxV5goE8yxDkKdlMUYIY6LAbrSUt1t3J6js47Xu9bx0i"}]}
Nel: {"report_to":"cf-nel","success_fraction":0.0,"max_age":604800}
Server: cloudflare
CF-RAY: a49cf18ccea1107e-HKG

{"message":"Product with id '99999' not found"}
```

Note: `404 Not Found` means the URL is valid but no product with that id exists. The body is still JSON with an error message, so `Content-Type: application/json` is there even for errors. In my app I should show "product not found" instead of crashing.

---

## Quick status code cheat (my own summary)

| Code | Meaning |
|------|---------|
| 200 | request worked, data is in the body |
| 404 | thing asked for does not exist |
