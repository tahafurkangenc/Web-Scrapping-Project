from flask import Flask , render_template ,request
import requests
from bs4 import BeautifulSoup
URL='https://scholar.google.com/scholar?q=blockchain' 
headers={"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 OPR/107.0.0.0"}

#response = requests.get(URL)
#html_content = response.content
#soup_res=BeautifulSoup(html_content,"lxml")
#print(soup_res)
app=Flask(__name__)
@app.route("/")
def index():
 #database'e kayıtlı sayfalar buradan gözükecek
 return render_template("anasayfa.html")

@app.route("/sonuclar", methods=["GET","POST"])
def sonuc(): 
 #return "deneme"
 #print(str(icerik.find(id='gs_res_ccl_mid')))
 if request.method == "POST":
  print("SONUC-> https://scholar.google.com/scholar?q="+request.form.get("inputText").strip().replace(' ','+'))
  URL="https://scholar.google.com/scholar?q="+request.form.get("inputText").strip().replace(' ','+')
 # Child ayırmaya çalışacağım
 #print(icerik.find(id='gs_bdy'))
 sayfa = requests.get(URL)
 icerik = BeautifulSoup(sayfa.content,'lxml')   
 alt_divler=icerik.find(id='gs_res_ccl_mid').find_all("div",class_='gs_r gs_or gs_scl')
 #print(len(alt_divler))
 pdf_links=[]
 for alt_div in alt_divler:
  for work_div in alt_div.find_all("div",class_='gs_ggs gs_fl'):
   print(work_div.find("a").find("span").text)
   print(work_div.find("a")["href"])
   if str(work_div.find("a").find("span").text).strip()=="[PDF]":
    pdf_links.append(work_div.find("a")["href"])
 #for i in pdf_links: #PDF linkleri kontrolü
  #print(i)
   #print("Div class ismi ->"+ work_div.get("class_"))
   
 print(len(alt_divler))
  
 #return str(icerik)
 return render_template("anasayfa.html",pdf_links=pdf_links)
 #return str(soup_res)
if __name__=="__main__":
 app.run(debug=True)
 #4 mart 6:49