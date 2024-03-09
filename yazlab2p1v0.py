from flask import Flask , render_template ,request
import requests
import os
import random
from bs4 import BeautifulSoup
import pymongo
from pymongo import MongoClient
URL='https://dergipark.org.tr/tr/search?q=yapay+zeka&section=articles' 
headers={"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 OPR/107.0.0.0"}
connect=MongoClient("mongodb://localhost:27017")
database=connect["yazlab2p1db"]
collection=database["makale_database"] 
#response = requests.get(URL)
#html_content = response.content
#soup_res=BeautifulSoup(html_content,"lxml")
#print(soup_res)
app=Flask(__name__)
@app.route("/")
def index():
 #database'e kayıtlı sayfalar buradan gözükecek
 makale_db=collection.find()
 return render_template("anasayfa.html",makale_datas=makale_db)

@app.route("/sonuclar", methods=["GET","POST"])
def sonuc(): 
 #return "deneme"
 #print(str(icerik.find(id='gs_res_ccl_mid')))
 if request.method == "POST":
  print("SONUC-> https://dergipark.org.tr/tr/search?q="+request.form.get("inputText").strip().replace(' ','+')+"&section=articles")
  URL="https://dergipark.org.tr/tr/search?q="+request.form.get("inputText").strip().replace(' ','+')+"&section=articles"
 # Child ayırmaya çalışacağım
 #print(icerik.find(id='gs_bdy'))
 sayfa = requests.get(URL)
 icerik = BeautifulSoup(sayfa.content,'lxml')   
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
   makale_icerik=BeautifulSoup(requests.get(makale_data["makale_site_URL"]).content,'lxml')
   makale_data['PDF_URL']="https://dergipark.org.tr"+makale_icerik.find(id='article-toolbar').find("a",title="Makale PDF linki")["href"]
   makale_data['makale_yazar']=str(makale_icerik.find("p",class_='article-authors').text).replace("\n","").replace("  ","").strip() #tam bitmedi
   makale_data['makale_tur']=str(makale_icerik.find("div",id='article-main-portlet').find("div",class_='kt-portlet__head kt-portlet__head--lg').find("div",class_='kt-portlet__head-title').text).strip()
   makale_data["makale_ozet"]=str(makale_icerik.find("div",id="article_tr").find("div",class_="article-abstract data-section").text).replace("\nÖz\n","").replace("\n"," ")
   makale_data["makale_yayinciadi"]="Dergi Park"
   makale_data["makale_anahtarkelimeler_tarayici"]=request.form.get("inputText").strip()
   makale_data["makale_alintisayisi"]=random.randint(1,50)
   #anahtar kelimelerin eklenmesi
   makale_data["makale_anahtarkelimeler"]=makale_icerik.find("div",id="article_tr").find("div",class_="article-keywords data-section")
   if  makale_data["makale_anahtarkelimeler"]!= None :
    makale_data["makale_anahtarkelimeler"]=str(makale_data["makale_anahtarkelimeler"].text).replace("Anahtar Kelimeler\n","").replace("\n"," ")
   #makale_data["makale_tarih"]=str(makale_icerik.find("table",class_='record_properties table').find_all("tr"))
   #referans eklenmesi
   makale_data["makale_referanslar"]=[]
   if  makale_icerik.find("div",id="article_tr").find("div",class_="article-citations data-section")!= None:
     for referans_xml in makale_icerik.find("div",id="article_tr").find("div",class_="article-citations data-section").find("ul",class_='fa-ul').find_all("li"):
      makale_data['makale_referanslar'].append(str(referans_xml.text).strip())
   #tarih eklenmesi
   makale_data["makale_tarih"]=""
   for tr in makale_icerik.find("table",class_='record_properties table').find_all("tr"):
    #print("tr.th -> "+ str(tr.find("th").text)+" ~~ tr.td -> "+ str(tr.find("td").text))
    if str(tr.find("th").text).strip() == "Yayımlanma Tarihi":
     makale_data["makale_tarih"]=str(tr.find("td").text).strip()
     break

   if collection.find_one({"PDF_URL":makale_data["PDF_URL"]},{"makale_ID":1 , "_id":0}) !=None: # database_de kayıtlı ise
    makale_data["makale_ID"]=collection.find_one({"PDF_URL":makale_data["PDF_URL"]},{"makale_ID":1 , "_id":0}).get("makale_ID",None)
    print("makale database'de kayıtlı")
   else:
    #makaleye ID atanması
    test_ID=0
    while True:
     if collection.find_one({"makale_ID":test_ID}) == None:
      makale_data["makale_ID"]=test_ID
      break
     else:
      test_ID=test_ID+1
  
   print("Makale ID : "+str(makale_data["makale_ID"]))
   print("Makale isim : "+makale_data["makale_isim"])
   print("Makale Site : "+makale_data["makale_site_URL"])
   print("Makale PDF URL : "+makale_data["PDF_URL"])
   
   print("Makale Yazar : "+makale_data["makale_yazar"])
   print("Makale Tur : "+makale_data["makale_tur"])
   print("Makale Yayimlanma Tarihi : "+makale_data["makale_tarih"])
   print("Makale Ozet : "+makale_data["makale_ozet"])
   print("Makale Anahtar Kelimeler : "+str(makale_data["makale_anahtarkelimeler"]))
   print("Makale Tarayici Anahtar Kelimeler : "+ makale_data["makale_anahtarkelimeler_tarayici"])
   print("Makale Yayinci Adi : "+makale_data['makale_yayinciadi'])
   print("Makale Alinti Sayisi : "+str(makale_data["makale_alintisayisi"]))
   print("Makale Referanslar :=>")
   for ref in makale_data["makale_referanslar"]:
    print("    Referans "+str(makale_data["makale_referanslar"].index(ref))+" : "+ ref)
   print("*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*")
   
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
   print(collection.find_one({"PDF_URL":makale_data["PDF_URL"]},{"PDF_URL":1 , "_id":0}))
   if collection.find_one({"PDF_URL":makale_data["PDF_URL"]},{"PDF_URL":1 , "_id":0}) !=None:
    print("aynisi var")
    deneme=collection.find_one({"PDF_URL":makale_data["PDF_URL"]},{"makale_ID":1 , "_id":0}).get("makale_ID",None)
    print("       deneme : "+str(deneme))
   else:
    print("veri tabaninda kayitli degil")
    collection.insert_one(makale_data)
   makale_datas.append(makale_data)
   #if str(alt_div.find("a").find("span").text).strip()=="[PDF]":
    #pdf_links.append(alt_div.find("a")["href"])

 #for i in pdf_links: #PDF linkleri kontrolü
  #print(i)
   #print("Div class ismi ->"+ work_div.get("class_"))
   
 print(len(alt_divler))

  
 #return str(icerik)
 return render_template("anasayfa.html",makale_datas=makale_datas)
 #return str(soup_res)

@app.route("/sonuclar/<int:makale_ID>")
def sonuc_page(makale_ID):
 return render_template("makalebilgileri.html",makale_data_JSON=collection.find_one({"makale_ID":makale_ID}))

if __name__=="__main__":
 app.run(debug=True)
 #9 mart 5:14