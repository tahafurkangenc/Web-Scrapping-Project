from flask import Flask , render_template ,request
import requests
import os
import random
from bs4 import BeautifulSoup
import pymongo
from pymongo import MongoClient
from datetime import datetime
URL='https://dergipark.org.tr/tr/search?q=yapay+zeka&section=articles' 
headers={"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 OPR/107.0.0.0"}
connect=MongoClient("mongodb://localhost:27017")
database=connect["yazlab2p1db"]
collection=database["makale_database"] 
#response = requests.get(URL)
#html_content = response.content
#soup_res=BeautifulSoup(html_content,"lxml")
#print(soup_res)

def turkce_tarih_to_datetime(turkce_tarih):
    turkce_aylar = {
        'ocak': 'January',
        'şubat': 'February',
        'mart': 'March',
        'nisan': 'April',
        'mayıs': 'May',
        'haziran': 'June',
        'temmuz': 'July',
        'ağustos': 'August',
        'eylül': 'September',
        'ekim': 'October',
        'kasım': 'November',
        'aralık': 'December'
    }

    # Türkçe tarihi boşluklara göre ayır
    parcalar = turkce_tarih.split()

    # Ay adını İngilizce'ye çevir
    parcalar[1] = turkce_aylar.get(parcalar[1].lower())

    # İngilizce tarihe çevir
    ingilizce_tarih = ' '.join(parcalar)
    
    # Tarihi çözümle
    try:
        datetime_obj = datetime.strptime(ingilizce_tarih, '%d %B %Y')
        return datetime_obj
    except ValueError:
        print("Geçersiz tarih formatı!")
        return None

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
 try:   
  alt_divler=icerik.find(class_='article-cards').find_all("div",class_='card article-card dp-card-outline')
  print(len(alt_divler))
 except Exception as e:
  alt_divler=[]
 makale_datas=[]
 i=0
 for alt_div in alt_divler:
   #print(str(alt_div.find("a").text).strip())
   #print(alt_div.find("a")["href"])
   makale_data={}
   makale_data["makale_isim"]=str(alt_div.find("a").text).strip()
   makale_data["makale_site_URL"]=alt_div.find("a")["href"]
   makale_icerik=BeautifulSoup(requests.get(makale_data["makale_site_URL"]).content,'lxml')
   
   try:
    makale_data['PDF_URL']="https://dergipark.org.tr"+makale_icerik.find(id='article-toolbar').find("a",title="Makale PDF linki")["href"]
   except Exception as e:
    print("Hata : " + str(e))
    makale_data["PDF_URL"]=""

   try:
    makale_data['makale_yazar']=str(makale_icerik.find("p",class_='article-authors').text).replace("\n","").replace("  ","").strip() #tam bitmedi
   except Exception as e:
    print("Hata : " + str(e))
    makale_data["makale_yazar"]=""
  
   try:
    makale_data['makale_tur']=str(makale_icerik.find("div",id='article-main-portlet').find("div",class_='kt-portlet__head kt-portlet__head--lg').find("div",class_='kt-portlet__head-title').text).strip()
   except Exception as e:
    print("Hata : " + str(e))
    makale_data["makale_tur"]=""

   try:
    makale_data["makale_ozet"]=str(makale_icerik.find("div",id="article_tr").find("div",class_="article-abstract data-section").text).replace("\nÖz\n","").replace("\n"," ")
   except Exception as e:
    print("Hata : " + str(e))
    makale_data["makale_ozet"]=""
   try:
    makale_data["makale_anahtarkelimeler_tarayici"]=request.form.get("inputText").strip()
   except Exception as e:
    print("Hata : " + str(e))
    makale_data["makale_anahtarkelimeler_tarayici"]=""


   makale_data["makale_yayinciadi"]="Dergi Park"
   
   makale_data["makale_alintisayisi"]=random.randint(1,50)
   
   #anahtar kelimelerin eklenmesi
   try:
    makale_data["makale_anahtarkelimeler"]=makale_icerik.find("div",id="article_tr").find("div",class_="article-keywords data-section")
    if  makale_data["makale_anahtarkelimeler"]!= None :
     makale_data["makale_anahtarkelimeler"]=str(makale_data["makale_anahtarkelimeler"].text).replace("Anahtar Kelimeler\n","").replace("\n"," ")
     #makale_data["makale_tarih"]=str(makale_icerik.find("table",class_='record_properties table').find_all("tr"))
   except Exception as e:
    print("Hata : " + str(e))
    makale_data["makale_anahtarkelimeler"]=""

   #referans eklenmesi
   makale_data["makale_referanslar"]=[]
   try: 
    if  makale_icerik.find("div",id="article_tr").find("div",class_="article-citations data-section")!= None:
      for referans_xml in makale_icerik.find("div",id="article_tr").find("div",class_="article-citations data-section").find("ul",class_='fa-ul').find_all("li"):
       makale_data['makale_referanslar'].append(str(referans_xml.text).strip())
      makale_data["makale_alintisayisi"]=len(makale_data["makale_referanslar"])
      print("Alinti Sayisi Güncellendi")
   except Exception as e:
    print("Hata : " + str(e))
    makale_data["makale_referanslar"]=[]

   #tarih eklenmesi
   makale_data["makale_tarih"]=""
   try:
    for tr in makale_icerik.find("table",class_='record_properties table').find_all("tr"):
     #print("tr.th -> "+ str(tr.find("th").text)+" ~~ tr.td -> "+ str(tr.find("td").text))
     if str(tr.find("th").text).strip() == "Yayımlanma Tarihi":
      makale_data["makale_tarih"]=turkce_tarih_to_datetime(str(tr.find("td").text).strip())
      break
   except Exception as e:
    print("Hata : " + str(e))
    makale_data["makale_tarih"]=""


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
   print("Makale Yayimlanma Tarihi : "+str(makale_data["makale_tarih"]))
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
   '''
   dosya_adi = "PDF_number"+str(i)+".pdf"
   kaydetme_yolu = os.path.join("C:\\Users\\asus\\Desktop\\PDF ler", dosya_adi)

   if not os.path.exists(kaydetme_yolu):
     response = requests.get(makale_data["PDF_URL"])
   
     with open(kaydetme_yolu, "wb") as f:
       f.write(response.content)
       print(f"{dosya_adi} dosyası indirildi.")
   else:
     print(f"{dosya_adi} dosyası zaten mevcut.")
    '''
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

@app.route("/listeleme", methods=["GET","POST"])
def listeleme():
 minIDNumber = request.form['minNumber']
 maxIDNumber = request.form['maxNumber']
 dateInput = request.form['dateInput']
 dateInput2 = request.form['dateInput2']
 minAlintiNumber = request.form['minNumber2']
 maxAlintiNumber = request.form['maxNumber2']
 sortField = request.form['sortField']
 sortOrder = request.form['sortOrder']
 isim_filter = request.form.get('isimFilterInput')
 ozet_filter = request.form.get('ozetFilterInput')
 yazar_filter = request.form.get('yazarFilterInput')
 tur_filter = request.form.get('turFilterInput')
 anahtar_kelime_filter = request.form.get('anahtarKelimeInput')
 arama_kelime_filter= request.form.get('aramaKelimeInput')

 # Formdan alınan bilgileri konsola bastırma
 print(f"En Küçük Sayı: {minIDNumber}")
 print(f"En Büyük Sayı: {maxIDNumber}")
 print(f"Tarih: {dateInput}")
 print(f"Tarih (2. Giriş): {dateInput2}")
 print(f"En Küçük Sayı (2. Giriş): {minAlintiNumber}")
 print(f"En Büyük Sayı (2. Giriş): {maxAlintiNumber}")
 print(f"Sıralama Alanı: {sortField}")
 print(f"Sıralama Yönü: {sortOrder}")
 # Alınan değerleri kullanarak işlemleri gerçekleştir
 # Burada sadece değerleri ekrana bastırıyoruz
 print("İsim Filtre: "+ isim_filter)
 print("Özet Filtre: "+ ozet_filter)
 print("Yazar Filtre: "+ yazar_filter)
 print("Tür Filtre: "+ tur_filter)
 print("Anahtar Kelime Filtre: " +anahtar_kelime_filter)
 print("Arama Kelime Filtre: " +anahtar_kelime_filter)
 database_sorgusu={}
 if minIDNumber != "" or maxIDNumber !="":
  print("deger girilmiş")
  database_sorgusu["makale_ID"]={}
  if minIDNumber !="":
   database_sorgusu["makale_ID"]["$gte"]=int(minIDNumber)
  if maxIDNumber !="":
   database_sorgusu["makale_ID"]["$lte"]=int(maxIDNumber)
 else:
  print("girilen deger yok")
 
 if minAlintiNumber != "" or maxAlintiNumber !="":
  print("deger girilmiş")
  database_sorgusu["makale_alintisayisi"]={}
  if minAlintiNumber !="":
   database_sorgusu["makale_alintisayisi"]["$gte"]=int(minAlintiNumber)
  if maxAlintiNumber !="":
   database_sorgusu["makale_alintisayisi"]["$lte"]=int(maxAlintiNumber)
 else:
  print("girilen deger yok")

 if dateInput != "" or dateInput2 !="":
  print("deger girilmiş")
  database_sorgusu["makale_tarih"]={}
  if dateInput !="":
   database_sorgusu["makale_tarih"]["$gte"]=datetime.strptime(dateInput, '%Y-%m-%d')
  if dateInput2 !="":
   database_sorgusu["makale_tarih"]["$lte"]=datetime.strptime(dateInput2, '%Y-%m-%d')
 else:
  print("girilen tarih degeri yok") 

 if isim_filter !="":
  print("makale_isim deger girilmis")
  database_sorgusu["makale_isim"]={}
  database_sorgusu["makale_isim"]["$regex"]=isim_filter
  database_sorgusu["makale_isim"]["$options"]="i"
 
 if ozet_filter !="":
  print("makale_ozet deger girilmis")
  database_sorgusu["makale_ozet"]={}
  database_sorgusu["makale_ozet"]["$regex"]=ozet_filter
  database_sorgusu["makale_ozet"]["$options"]="i"

 if yazar_filter !="":
  print("makale_yazar deger girilmis")
  database_sorgusu["makale_yazar"]={}
  database_sorgusu["makale_yazar"]["$regex"]=yazar_filter
  database_sorgusu["makale_yazar"]["$options"]="i"

 if tur_filter !="":
  print("makale_tur deger girilmis")
  database_sorgusu["makale_tur"]=tur_filter
  if "~" in tur_filter:
   tur_filter=tur_filter.replace("~","")
   database_sorgusu["makale_tur"]={}
   database_sorgusu["makale_tur"]["$regex"]=tur_filter
   database_sorgusu["makale_tur"]["$options"]="i"

 if anahtar_kelime_filter !="":
  print("makale_anahtarkelimeler deger girilmis")
  database_sorgusu["makale_anahtarkelimeler"]={}
  database_sorgusu["makale_anahtarkelimeler"]["$regex"]=anahtar_kelime_filter
  database_sorgusu["makale_anahtarkelimeler"]["$options"]="i"

 if arama_kelime_filter !="":
  print("makale_anahtarkelimeler_tarayici deger girilmis")
  database_sorgusu["makale_anahtarkelimeler_tarayici"]={}
  database_sorgusu["makale_anahtarkelimeler_tarayici"]["$regex"]=arama_kelime_filter
  database_sorgusu["makale_anahtarkelimeler_tarayici"]["$options"]="i"
 print(database_sorgusu)
 '''
 for i in collection.find(database_sorgusu).sort(sortField,int(sortOrder)):
    print("ID : "+str(i.get("makale_ID")))
    print("Alinti Sayisi : "+ str(i.get("makale_alintisayisi")))
 '''
    
 return render_template("anasayfa.html",makale_datas=collection.find(database_sorgusu).sort(sortField,int(sortOrder)))

@app.route("/download/<int:makale_ID_download>")
def downloadwithID(makale_ID_download):
 dosya_JSON = collection.find_one({"makale_ID": makale_ID_download})
 try:
  dosya_adi = dosya_JSON.get("makale_isim")+".pdf"
  kaydetme_yolu = os.path.join("C:\\Users\\asus\\Desktop\\PDF ler", dosya_adi)
  if not os.path.exists(kaydetme_yolu):
    response = requests.get(dosya_JSON.get("PDF_URL"))
    with open(kaydetme_yolu, "wb") as f:
      f.write(response.content)
      print(f"{dosya_adi} dosyası indirildi.")
  else:
    print(f"{dosya_adi} dosyası zaten mevcut.")
 except Exception as e:
  print("Dosya adi sorunu ->"+str(e))
  dosya_adi = "MAKALE_ID_"+str(dosya_JSON.get("makale_ID"))+".pdf"
  kaydetme_yolu = os.path.join("C:\\Users\\asus\\Desktop\\PDF ler", dosya_adi)
  if not os.path.exists(kaydetme_yolu):
    response = requests.get(dosya_JSON.get("PDF_URL"))
    with open(kaydetme_yolu, "wb") as f:
      f.write(response.content)
      print(f"{dosya_adi} dosyası indirildi.")
  else:
    print(f"{dosya_adi} dosyası zaten mevcut.")

 return render_template("anasayfa.html")

if __name__=="__main__":
 app.run(debug=True)
 #14 mart 7:00