from flask import Flask , render_template
import requests
from bs4 import BeautifulSoup
URL='https://dergipark.org.tr/tr/search?q=yapay+zeka&section=articles' 
headers={"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 OPR/107.0.0.0"}
sayfa = requests.get(URL)

#response = requests.get(URL)
#html_content = response.content
#soup_res=BeautifulSoup(html_content,"lxml")
#print(soup_res)

icerik = BeautifulSoup(sayfa.content,'lxml')   
app=Flask(__name__)
@app.route("/")
def index():
 print(str(icerik.find(class_='article-cards')))
 alt_divler=icerik.find(class_='article-cards').find_all("div",class_='card article-card dp-card-outline')
 print(len(alt_divler))
 makale_datas=[]
 for alt_div in alt_divler:
   #print(str(alt_div.find("a").text).strip())
   #print(alt_div.find("a")["href"])
   makale_data={}
   makale_data["makale_isim"]=str(alt_div.find("a").text).strip()
   makale_data["makale_site_URL"]=alt_div.find("a")["href"]
   makale_data['makale_URL']=alt_div.find("a")["href"]
   makale_icerik=BeautifulSoup(requests.get(makale_data["makale_URL"]).content,'lxml')
   makale_data['PDF_URL']="https://dergipark.org.tr"+makale_icerik.find(id='article-toolbar').find("a",title="Makale PDF linki")["href"]
   print("Makale isim : "+makale_data["makale_isim"])
   print("Makale Site : "+makale_data["makale_site_URL"])
   print("Makale PDF URL : "+makale_data["PDF_URL"])
   print()
   #if str(alt_div.find("a").find("span").text).strip()=="[PDF]":
    #pdf_links.append(alt_div.find("a")["href"])
 #for i in pdf_links: #PDF linkleri kontrolü
  #print(i)
   #print("Div class ismi ->"+ work_div.get("class_"))
   
 print(len(alt_divler))

 return str(icerik)
 #return render_template("anasayfa.html",pdf_links=pdf_links)
 #return str(soup_res)
if __name__=="__main__":
 app.run(debug=True)
#4 mart 6:49