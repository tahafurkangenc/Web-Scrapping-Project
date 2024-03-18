from flask import Flask , render_template
import os
import requests
from bs4 import BeautifulSoup
from spellchecker import SpellChecker
URL='https://dergipark.org.tr/tr/search?q=yapay+zeka&section=articles' 
headers={"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 OPR/107.0.0.0"}
sayfa = requests.get(URL)

#response = requests.get(URL)
#html_content = response.content
#soup_res=BeautifulSoup(html_content,"lxml")
#print(soup_res)

def duzeltme(metin):
 metin=metin.replace("~","")
  # SpellChecker nesnesi oluşturma
 spellchecker = SpellChecker()
  # Hatalı kelimeleri bulma
  #hatali_kelimeler = spellchecker.unknown(["artifcal","intellicenge"])
 metin_split=metin.split(" ")
 print(len(metin_split))
 if(len(metin_split)==1):
  print("duzeltilmis hal : "+ str(spellchecker.correction(metin)))
  return str(spellchecker.correction(metin))
 else:
  metin_correction=[]
  for kelimeler in metin_split:
   print("kelimeler :"+ kelimeler+"---")
   print("correction "+ str(spellchecker.correction(kelimeler)))
   metin_correction.append(spellchecker.correction(kelimeler))
   print(spellchecker.candidates(kelimeler))
  print("duzeltilmis hal "+str(" ".join(metin_correction)))
  return str(" ".join(metin_correction))

icerik = BeautifulSoup(sayfa.content,'lxml')   
app=Flask(__name__)
@app.route("/")
def index():
 #print(str(icerik.find(class_='article-cards')))
 metin = "~artifcal intellienge"
 if '~' in metin:
  return duzeltme(metin)
 alt_divler=icerik.find(class_='article-cards').find_all("div",class_='card article-card dp-card-outline')
 print(len(alt_divler))
 makale_datas=[]
 i=0
 for alt_div in alt_divler:
   #print(str(alt_div.find("a").text).strip())
   #print(alt_div.find("a")["href"])
   makale_data={}
   makale_data["makale_isim"]=str(alt_div.find("a").text).strip()
   makale_data["makale_site_URL"]=alt_div.find("a")["href"]
   makale_data['makale_URL']=alt_div.find("a")["href"]
   makale_icerik=BeautifulSoup(requests.get(makale_data["makale_URL"]).content,'lxml')
   makale_data['PDF_URL']="https://dergipark.org.tr"+makale_icerik.find(id='article-toolbar').find("a",title="Makale PDF linki")["href"]
   makale_data['makale_yazar']=str(makale_icerik.find("p",class_='article-authors').text).replace("\n","").replace("  ","").strip() #tam bitmedi
   makale_data['makale_tur']=str(makale_icerik.find("div",id='article-main-portlet').find("div",class_='kt-portlet__head kt-portlet__head--lg').find("div",class_='kt-portlet__head-title').text).strip()
   makale_data["makale_ID"]=i
   #makale_data["makale_tarih"]=str(makale_icerik.find("table",class_='record_properties table').find_all("tr"))
   makale_data["makale_tarih"]=""
   for tr in makale_icerik.find("table",class_='record_properties table').find_all("tr"):
    #print("tr.th -> "+ str(tr.find("th").text)+" ~~ tr.td -> "+ str(tr.find("td").text))
    if str(tr.find("th").text).strip() == "Yayımlanma Tarihi":
     makale_data["makale_tarih"]=str(tr.find("td").text).strip()
     break
   
   

   print("Makale ID : "+str(makale_data["makale_ID"]))
   print("Makale isim : "+makale_data["makale_isim"])
   print("Makale Site : "+makale_data["makale_site_URL"])
   print("Makale PDF URL : "+makale_data["PDF_URL"])
   print("Makale Yazar : "+makale_data["makale_yazar"])
   print("Makale Tur : "+makale_data["makale_tur"])
   print("Makale Yayımlanma Tarihi : "+makale_data["makale_tarih"])
   #(requests.get(makale_data["PDF_URL"]).content)
   dosya_adi = "PDF_number"+str(i)+".pdf"
   kaydetme_yolu = os.path.join("C:\\Users\\asus\\Desktop\\PDF ler", dosya_adi)

   if not os.path.exists(kaydetme_yolu):
     response = requests.get(makale_data["PDF_URL"])
   
     with open(kaydetme_yolu, "wb") as f:
       f.write(response.content)
       print(f"{dosya_adi} dosyası indirildi.")
   else:
     print(f"{dosya_adi} dosyası zaten mevcut.")
   
   i=i+1
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
#6 mart 9:15