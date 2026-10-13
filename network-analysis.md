# network-analysis.md

Website: <https://www.flipkart.com/search?q=bags&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off>
Browser: <Chrome>
Date: <10-10-26>

Steps I did: opened DevTools (F12) -> Network tab -> ticked "Disable cache" -> reloaded the page.

## Numbers (from the status bar at the bottom of the Network tab)
- Total requests: <94 requests>
- Total page size: <4.9 MB transferred> (resources: <Y MB>)
- Load time: <1.54 s>  (DOMContentLoaded <..>, Load <..>)

## Slowest resource
- Name: <search?q=bags&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off>
- Type: <document>
- Time: <583ms>
)

## 3xx / 4xx responses I saw
I filtered with status-code:404, status-code:301, status-code:302 and status-code:304. Nothing showed up for any of them, so on this page I did not see any 3xx or 4xx response. Every request I looked at was 200.

(304 not appearing makes sense because "Disable cache" was on, so the browser did not reuse anything from cache.)

## What I noticed

Most of the 96 requests are product images in .webp format. They are small (about 6 to 16 kB each) and take around 430 to 440 ms each, so they load in parallel and not one after another.
The page HTML itself is the biggest single response at 217 kB and also the slowest, which makes sense because the server first has to build the search results.
This is useful for my bags store: product images should be small and in webp, and the product list should come from the API quickly.#

