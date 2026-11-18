import os
# Show the BMF interface URL: GET the page, then (65 s later, robots.txt Crawl-Delay 60) submit "Ich stimme zu".
import urllib.request, urllib.parse, http.cookiejar, re, time, sys
UA = "Mozilla/5.0 (compatible; tax-model-test; non-commercial research)"
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
op.addheaders = [("User-Agent", UA)]
url = "https://www.bmf-steuerrechner.de/interface/einganginterface.xhtml"
s = op.open(url, timeout=60).read().decode("utf-8", "replace")
m = re.search(r'<form id="uiExternSchnittstelleForm".*?name="javax.faces.ViewState"[^>]*value="([^"]+)"', s, re.S)
vs = m.group(1)
time.sleep(65)
data = urllib.parse.urlencode({"uiExternSchnittstelleForm": "uiExternSchnittstelleForm",
    "uiExternSchnittstelleForm:income_ext_interface_hinweis": "Ich stimme zu",
    "javax.faces.ViewState": vs}).encode()
r = op.open(urllib.request.Request(url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"}), timeout=60)
out = r.read().decode("utf-8", "replace")
open(os.path.expanduser("~/cmp/de/refs/bmf/interface_after_terms.html"), "w").write(out)
print("saved", len(out))
