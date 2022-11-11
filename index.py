from flask import Flask, render_template, request
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

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

@app.route("/")
def index():
    homepage = "<h1>李心如 Python 網頁</h1>"
    homepage += "<a href=/hi>Hi~</a><br>"
    homepage += "<a href=/today>顯示日期時間</a><br>"
    homepage += "<a href=/welcome?nick=xinru>傳送使用者暱稱</a><br>"
    homepage += "<a href=/about>李心如簡介網頁</a><br>"
    homepage += "<a href=/account>表單</a><br>"
    homepage += "<br><a href=/search>選修課程查詢</a><br>"
    return homepage

# if __name__ == "__main__":
#     app.run()