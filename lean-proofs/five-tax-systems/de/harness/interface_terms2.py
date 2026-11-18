import os
# The "Ich stimme zu" button is an AJAX (JSF partial) request; repeat it the way the browser sends it.
import urllib.request, urllib.parse, http.cookiejar, re, time
UA = "Mozilla/5.0 (compatible; tax-model-test; non-commercial research)"
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
op.addheaders = [("User-Agent", UA)]
url = "https://www.bmf-steuerrechner.de/interface/einganginterface.xhtml"
time.sleep(60)
s = op.open(url, timeout=60).read().decode("utf-8", "replace")
vs = re.search(r'<form id="uiExternSchnittstelleForm".*?name="javax.faces.ViewState"[^>]*value="([^"]+)"', s, re.S).group(1)
time.sleep(65)
btn = "uiExternSchnittstelleForm:income_ext_interface_hinweis"
data = urllib.parse.urlencode({"uiExternSchnittstelleForm": "uiExternSchnittstelleForm",
    "javax.faces.ViewState": vs, "javax.faces.source": btn, "javax.faces.partial.event": "click",
    "javax.faces.partial.execute": btn + " uiExternSchnittstelleForm", "javax.faces.partial.render": "uiExternSchnittstelleForm",
    "javax.faces.behavior.event": "action", "javax.faces.partial.ajax": "true", btn: "Ich stimme zu"}).encode()
req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
    "Faces-Request": "partial/ajax", "X-Requested-With": "XMLHttpRequest"})
out = op.open(req, timeout=60).read().decode("utf-8", "replace")
open(os.path.expanduser("~/cmp/de/refs/bmf/interface_after_terms2.xml"), "w").write(out)
print("saved", len(out))
