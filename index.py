import requests
from bs4 import BeautifulSoup

import firebase_admin
from firebase_admin import credentials, firestore
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

from flask import Flask, render_template, request, make_response, jsonify
from datetime import datetime, timezone, timedelta
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
        rate = item.find("div", class_="runtime").text
        test_rate = item.find_all("img")
        for img in test_rate:
            if 'src' in img.attrs:
                if img['src'].endswith('/images/cer_G.gif'):
                    rate = "普遍級(一般觀眾皆可觀賞)"
                elif img['src'].endswith('/images/cer_P.gif') :
                    rate = "保護級(未滿六歲之兒童不得觀賞，六歲以上未滿十二歲之兒童須父母、師長或成年親友陪伴輔導觀賞)"
                elif img['src'].endswith('/images/cer_F2.gif') :
                    rate = "輔導級(未滿十二歲之兒童不得觀賞)"
                elif img['src'].endswith('/images/cer_F5.gif') :
                    rate = "輔導級(未滿十五歲之人不得觀賞)"
                elif img['src'].endswith('/images/cer_R.gif'):
                    rate = "限制級(未滿十八歲之人不得觀賞)"
                else :
                    rate = "尚無電影分級資訊"
        title = item.find("div", class_="filmtitle").text
        movie_id = item.find("div", class_="filmtitle").find("a").get("href").replace("/", "").replace("movie", "")
        hyperlink = "http://www.atmovies.com.tw" + item.find("div", class_="filmtitle").find("a").get("href")
        show = item.find("div", class_="runtime").text.replace("上映日期：", "")
        show = show.replace("片長：", "")
        show = show.replace("分", "")
        showDate = show[0:10]
        showLength = show[13:]

        doc = {
            "title": title,
            "picture": picture,
            "rate": rate,
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
                info += "片名：<a target = _blank href=" + doc.to_dict()["hyperlink"] + ">" + doc.to_dict()["title"] + "</a>" + "<br>" 
                info += "分級資訊：" + doc.to_dict()["rate"] + "<br><br>"
        if info == "":
            info += "查無此電影，<a href = http://www.atmovies.com.tw/movie/next/>前往官網</a>" 
        return info
    else:  
        return render_template("search_movie.html")

@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json(force=True)
    action =  req.get("queryResult").get("action")
    msg =  req.get("queryResult").get("queryText")
    info = "動作：" + action + "； 查詢內容：" + msg
    return make_response(jsonify({"fulfillmentText": info}))


@app.route("/")
def index():
    homepage = "<h1>李心如 Python 網頁</h1>"
    homepage += "<a href=/hi target = _blank>Hi~</a><br>"
    homepage += "<a href=/today target = _blank>顯示日期時間</a><br>"
    homepage += "<a href=/welcome?nick=xinru target = _blank>傳送使用者暱稱</a><br>"
    homepage += "<a href=/about target = _blank>李心如簡介網頁</a><br>"
    homepage += "<a href=/account target = _blank>表單</a><br>"
    homepage += "<a href=/search target = _blank>選修課程查詢</a><br>"
    homepage += "<br><a href=/movie target = _blank>讀取開眼電影即將上映影片，寫入Firestore</a><br>"
    homepage += "<a href=/search_movie target = _blank>電影查詢</a><br>"
    homepage += "<a href=/webhook target = _blank>對話機器人</a><br>"
    return homepage

if __name__ == "__main__":
    app.run()