import requests
from bs4 import BeautifulSoup

import firebase_admin
from firebase_admin import credentials, firestore
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

from flask import Flask, render_template, request
from datetime import datetime
app = Flask(__name__)


@app.route("/hi")
def course():
    return"<h1>資訊管理導論</h1>"

@app.route("/today")
def today():
    now = datetime.now()
    return render_template("today.html",datetime = str(now))

@app.route("/welcome", methods = ["GET", "POST"])
def welcome():
    user = request.values.get("nick")
    return render_template("welcome.html", name = user)

@app.route("/about")
def about():
    return render_template("aboutme.html")

@app.route("/account",methods = ["GET","POST"])
def account():
    if request.method == "POST":
        user = request.form["user"]
        pwd = request.form["pwd"]
        result = "您輸入的帳號是："+ user + "<br>密碼：" + pwd 
        return result
    else:
        return render_template("account.html")

@app.route("/search",methods = ["GET","POST"])
def search():
    if request.method == "POST":
        cond = request.form["keyword"]
        result = "您輸入的課程關鍵字是：" + cond 
        cond_b = request.form["tcname"]
        result_b = "您輸入的教師關鍵字是：" + cond_b 

        db = firestore.client()
        collection_ref = db.collection("111-1")
        docs = collection_ref.get()
        result = ""
        for doc in docs:
            dict = doc.to_dict()
            if cond in dict["Course"]:
                if cond_b in dict["Leacture"]:
                    result += dict["Leacture"] + "老師開的" + dict["Course"] + "課程,每週" 
                    result += dict["Time"] + "於" + dict["Room"] +"上課<br>"
                    
        if result == "":
            result += "抱歉，查無相關條件的選修課程"
        return result
    else:
        return render_template("search.html")

@app.route("/movie")
def movie():
    url = "http://www.atmovies.com.tw/movie/next/"
    Data = requests.get(url)
    Data.encoding = "utf-8"
    sp = BeautifulSoup(Data.text, "html.parser")
    result = sp.select(".filmListAllX li")
    lastUpdate = sp.find("div", class_="smaller09").text[5:]

    for item in result:
        picture = item.find("img").get("src").replace(" ", "")
        title = item.find("div", class_="filetime").text
        movie_id = item.find("div", class_="filetime").find("a").get("href").replace("/", "").replace("movie", "")
        hyperlink = "http://www.atmovies.com.tw" + item.find("div", class_="filetime").find("a").get("href")
        show = item.find("div", class_="runtime").text.replace("上映日期：", "")
        show = show.replace("片長：", "")
        show = show.replace("分", "")
        showDate = show[0:10]
        showLength = show[13:]

        doc = {
            "title": title,
            "picture": picture,
            "hyperlink": hyperlink,
            "showDate": showDate,
            "showLength": showLength,
            "lastUpdate": lastUpdate
         }

        doc_ref = db.collection("心如電影").document(movie_id)
        doc_ref.set(doc)
    return "近期上映電影已爬蟲及存檔完畢，網站最近更新日期為：" + lastUpdate 

@app.route("/search_movie", methods=["POST","GET"])
def search_movie():
    if request.method == "POST":
        MovieTitle = request.form["MovieTitle"]
        info = ""     
        collection_ref = db.collection("心如電影")
        docs = collection_ref.order_by("showDate").get()    
        for doc in docs:
            if MovieTitle in doc.to_dict()["title"]: 
                info += "片名：" + doc.to_dict()["title"] + "<br>" 
                info += "海報：" + doc.to_dict()["picture"] + "<br>"
                info += "影片介紹：" + doc.to_dict()["hyperlink"] + "<br>"
                info += "片長：" + doc.to_dict()["showLength"] + " 分鐘<br>" 
                info += "上映日期：" + doc.to_dict()["showDate"] + "<br><br>"           
        return info

@app.route("/")
def index():
    homepage = "<h1>李心如 Python 網頁</h1>"
    homepage += "<a href=/hi>Hi~</a><br>"
    homepage += "<a href=/today>顯示日期時間</a><br>"
    homepage += "<a href=/welcome?nick=xinru>傳送使用者暱稱</a><br>"
    homepage += "<a href=/about>李心如簡介網頁</a><br>"
    homepage += "<a href=/account>表單</a><br>"
    homepage += "<br><a href=/search>選修課程查詢</a><br>"
    homepage += "<br><a href=/movie>讀取開眼電影即將上映影片，寫入Firestore</a><br>"
    homepage += "<br><a href=/search_movie>電影查詢</a><br>"
    return homepage

# if __name__ == "__main__":
#     app.run()