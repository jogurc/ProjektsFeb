import requests
from flask import Flask, render_template, request, redirect
import sqlite3
import json

def select_sql(cmd, vals=None):
  conn = sqlite3.connect('flask.db')
  c = conn.cursor()
  if vals:
      res = c.execute(cmd, vals).fetchall()
  else:
      res = c.execute(cmd).fetchall()
  conn.commit()
  conn.close()
  return res

def insert_sql(cmd, vals=None):
   conn = sqlite3.connect('flask.db')
   c = conn.cursor()
   res = c.execute(cmd, vals).fetchall() 
   conn.commit() 
   conn.close()
   return res

app = Flask(__name__)

@app.route("/")
def sakums():
  select_sql("CREATE TABLE IF NOT EXISTS Lietotaji (\
    lietotajs_ID INTEGER PRIMARY KEY AUTOINCREMENT, \
    lietotajvards TEXT NOT NULL, \
    parole TEXT NOT NULL, \
    filmas_mekletas INT, \
    filmas_saglabatas TEXT)")

  select_sql("DROP TABLE IF EXISTS Session")

  return render_template("sakums.html")

@app.route("/sakums_admin")
def sakums_admin():
  return render_template("sakums_admin.html")

@app.route("/sakums_lietotajs")
def sakums_lietotajs():
  return render_template("sakums_lietotajs.html")

@app.route("/konts_registreties")
def konts_registreties_redirect():
  return render_template("konts_registreties.html")

@app.route("/konts_registreties_apstrade", methods = ["GET","POST"])
def konts_registreties_apstrade():
  jauns_lietotajs = {}
  if request.method == "POST":
    jauns_lietotajs["lietotajvards"] = request.form["lietotajvards"]
    jauns_lietotajs["parole"] = request.form["parole"]
    insert_sql("INSERT INTO Lietotaji (lietotajvards, parole, filmas_mekletas, filmas_saglabatas) VALUES (?, ?, ?, ?)",[
      jauns_lietotajs["lietotajvards"],
      jauns_lietotajs["parole"],
      0,
      None
      ])
  else:
    return render_template("konts_registreties.html")
  return redirect("/")

@app.route("/konts_pieslegties")
def konts_pieslegties_redirect():
  return render_template("konts_pieslegties.html")

@app.route("/konts_pieslegties_apstrade", methods = ["POST", "GET"])
def konts_pieslegties_apstrade():
    pieslegties_konts = {}
    lietotajvards_result = None 
    parole_result = None 
    if request.method == "POST":
      pieslegties_konts["lietotajvards"] = request.form["lietotajvards"]
      pieslegties_konts["parole"] = request.form["parole"]
      lietotajvards_result = select_sql("SELECT lietotajvards FROM Lietotaji WHERE lietotajvards = ?", (pieslegties_konts["lietotajvards"],))
      parole_result = select_sql("SELECT parole FROM Lietotaji WHERE parole = ?", (pieslegties_konts["parole"],))
      if lietotajvards_result and parole_result:
        select_sql("DROP TABLE IF EXISTS Session")
        select_sql("CREATE TABLE IF NOT EXISTS Session (\
        konts_ID INTEGER PRIMARY KEY AUTOINCREMENT, \
        lietotajvards TEXT NOT NULL, \
        parole TEXT NOT NULL, \
        filmas_mekletas INT, \
        filmas_saglabatas TEXT)")
        insert_sql("INSERT INTO Session (lietotajvards, parole, filmas_mekletas, filmas_saglabatas) VALUES (?, ?, ?, ?)" ,[
          pieslegties_konts["lietotajvards"],
          pieslegties_konts["parole"],
          0,
          None
        ])
        return redirect("/sakums_lietotajs")
      else: 
        return render_template("konts_pieslegties.html")
    else:
      return render_template("konts_pieslegties.html")

@app.route("/konts_pieslegties_admin")
def konts_pieslegties_admin():
  return render_template("konts_pieslegties_admin.html")

@app.route("/konts_pieslegties_admin_apstrade", methods = ["POST", "GET"])
def konts_pieslegties_apstrade_admin():
  select_sql("DROP TABLE IF EXISTS Admin")

  select_sql("CREATE TABLE IF NOT EXISTS Admin (\
    lietotajs_ID INTEGER PRIMARY KEY AUTOINCREMENT, \
    lietotajvards TEXT NOT NULL, \
    parole TEXT NOT NULL)")

  insert_sql("INSERT INTO Admin (lietotajvards, parole) VALUES (?, ?)" ,[
  "Galvenais",
  2468
  ])
  pieslegties_konts = {}
  lietotajvards_result = None 
  parole_result = None 
  if request.method == "POST":
    pieslegties_konts["lietotajvards"] = request.form["lietotajvards"]
    pieslegties_konts["parole"] = request.form["parole"]
    lietotajvards_result = select_sql("SELECT lietotajvards FROM Admin WHERE lietotajvards = ?", (pieslegties_konts["lietotajvards"],))
    parole_result = select_sql("SELECT parole FROM Admin WHERE parole = ?", (pieslegties_konts["parole"],))
    if lietotajvards_result and parole_result:
      return redirect("/sakums_admin")
    else: 
      return render_template("konts_pieslegties_admin.html")
  else:
    return render_template("konts_pieslegties_admin.html")

@app.route('/visi_lietotaji')
def visi_lietotaji():
  rezultats = select_sql("SELECT * FROM Lietotaji")
  return render_template("visi_lietotaji.html", rezultats = rezultats)

@app.route("/rezultats_redirect", methods = ["GET", "POST"])
def rezultats_redirect():
  filma = {}
  if request.method == "POST":
    filma["nosaukums"] = request.form["nosaukums"]
    filma["nosaukums"] = filma["nosaukums"].replace(" ", "+")
    response = requests.get("http://www.omdbapi.com/?t=" + filma["nosaukums"] + "&apikey=ac26b569")
    if response.status_code == 200:
      x = response.json()
      x = [x]
      rezultats = json.dumps(x, indent=4)
      print(rezultats)
      select_sql("DROP TABLE IF EXISTS Filma")
      select_sql("CREATE TABLE IF NOT EXISTS Filma (\
      filma_ID INTEGER PRIMARY KEY AUTOINCREMENT, \
      Title TEXT NOT NULL, \
      Year TEXT NOT NULL, \
      Rated TEXT NOT NULL, \
      Released TEXT NOT NULL, \
      Runtime TEXT NOT NULL, \
      Genre TEXT NOT NULL, \
      Director TEXT NOT NULL, \
      Writer TEXT NOT NULL, \
      Actors TEXT NOT NULL, \
      Plot TEXT NOT NULL, \
      Language TEXT NOT NULL, \
      Country TEXT NOT NULL, \
      Awards TEXT NOT NULL, \
      Poster TEXT NOT NULL)")
      insert_sql("INSERT INTO Filma (Title, Year, Rated, Released, Runtime, Genre, Director, Writer, Actors, Plot, Language, Country, Awards, Poster) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", [
        x[0]["Title"],
        x[0]["Year"],
        x[0]["Rated"],
        x[0]["Released"],
        x[0]["Runtime"],
        x[0]["Genre"],
        x[0]["Director"],
        x[0]["Writer"],
        x[0]["Actors"],
        x[0]["Plot"],
        x[0]["Language"],
        x[0]["Country"],
        x[0]["Awards"],
        x[0]["Poster"]
      ])
      session = select_sql("SELECT * FROM Session")
      rezultats = select_sql("SELECT * FROM Lietotaji WHERE lietotajvards = ?", (session[0][1],))
      filmas_mekletas = rezultats[0][3]
      insert_sql("UPDATE Lietotaji SET filmas_mekletas = ? WHERE lietotajvards = ?", (filmas_mekletas + 1, session[0][1]))
      return redirect("/rezultats") 

  return render_template("sakums_lietotajs.html")

@app.route("/rezultats_viesis_redirect", methods = ["GET", "POST"])
def rezultats_viesis_redirect():
  filma = {}
  if request.method == "POST":
    filma["nosaukums"] = request.form["nosaukums"]
    filma["nosaukums"] = filma["nosaukums"].replace(" ", "+")
    response = requests.get("http://www.omdbapi.com/?t=" + filma["nosaukums"] + "&apikey=ac26b569")
    if response.status_code == 200:
      x = response.json()
      x = [x]
      rezultats = json.dumps(x, indent=4)
      print(rezultats)
      select_sql("DROP TABLE IF EXISTS Filma")
      select_sql("CREATE TABLE IF NOT EXISTS Filma (\
      filma_ID INTEGER PRIMARY KEY AUTOINCREMENT, \
      Title TEXT NOT NULL, \
      Year TEXT NOT NULL, \
      Rated TEXT NOT NULL, \
      Released TEXT NOT NULL, \
      Runtime TEXT NOT NULL, \
      Genre TEXT NOT NULL, \
      Director TEXT NOT NULL, \
      Writer TEXT NOT NULL, \
      Actors TEXT NOT NULL, \
      Plot TEXT NOT NULL, \
      Language TEXT NOT NULL, \
      Country TEXT NOT NULL, \
      Awards TEXT NOT NULL, \
      Poster TEXT NOT NULL)")
      insert_sql("INSERT INTO Filma (Title, Year, Rated, Released, Runtime, Genre, Director, Writer, Actors, Plot, Language, Country, Awards, Poster) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", [
        x[0]["Title"],
        x[0]["Year"],
        x[0]["Rated"],
        x[0]["Released"],
        x[0]["Runtime"],
        x[0]["Genre"],
        x[0]["Director"],
        x[0]["Writer"],
        x[0]["Actors"],
        x[0]["Plot"],
        x[0]["Language"],
        x[0]["Country"],
        x[0]["Awards"],
        x[0]["Poster"]
      ])
      return redirect("/rezultats_viesis") 

  return render_template("sakums.html")

@app.route("/rezultats", methods = ["GET", "POST"])
def rezultats_apstrade():
  rezultats = select_sql("SELECT * FROM Filma")
  return render_template("rezultats.html", rezultats=rezultats)

@app.route("/rezultats_viesis", methods = ["GET", "POST"])
def rezultats_viesis_apstrade():
  rezultats = select_sql("SELECT * FROM Filma")
  return render_template("rezultats_viesis.html", rezultats=rezultats)

@app.route("/profils")
def profils():
  session = select_sql("SELECT * FROM Session")
  rezultats = select_sql("SELECT * FROM Lietotaji WHERE lietotajvards = ?", (session[0][1],))
  return render_template("profils.html", rezultats=rezultats)

@app.route("/saglabat_filmu")
def saglabat_filmu():
  filma = select_sql("SELECT Title, Year, Rated, Released, Runtime, Genre, Director, Writer, Actors, Plot, Language, Country, Awards, Poster FROM Filma")
  session = select_sql("SELECT * FROM Session")
  rezultats = select_sql("SELECT * FROM Lietotaji WHERE lietotajvards = ?", (session[0][1],))
  saglabats = filma[0][0]
  if rezultats[0][4] is None:
    insert_sql("UPDATE Lietotaji SET filmas_saglabatas = ? WHERE lietotajvards = ?", (saglabats, session[0][1]))
  else:
    insert_sql("UPDATE Lietotaji SET filmas_saglabatas = ? WHERE lietotajvards = ?", (rezultats[0][4] + ", " + saglabats, session[0][1]))
  return redirect("/sakums_lietotajs")

@app.route("/salidzinat")
def salidzinat():
  return render_template("salidzinat.html")

@app.route("/salidzinat_redirect", methods = ["GET", "POST"])
def salidzinat_redirect():
  filma1 = {}
  filma2 = {}
  if request.method == "POST":
    filma1["nosaukums1"] = request.form["nosaukums1"]
    filma2["nosaukums2"] = request.form["nosaukums2"]
    filma1["nosaukums1"] = filma1["nosaukums1"].replace(" ", "+")
    filma2["nosaukums2"] = filma2["nosaukums2"].replace(" ", "+")
    response1 = requests.get("http://www.omdbapi.com/?t=" + filma1["nosaukums1"] + "&apikey=ac26b569")
    response2 = requests.get("http://www.omdbapi.com/?t=" + filma2["nosaukums2"] + "&apikey=ac26b569")
    if response1.status_code == 200 and response2.status_code == 200:
      x1 = response1.json()
      x1 = [x1]
      x2 = response2.json()
      x2 = [x2]
      select_sql("DROP TABLE IF EXISTS Filma1")
      select_sql("CREATE TABLE IF NOT EXISTS Filma1 (\
      filma_ID INTEGER PRIMARY KEY AUTOINCREMENT, \
      Title TEXT NOT NULL, \
      Year TEXT NOT NULL, \
      Rated TEXT NOT NULL, \
      Released TEXT NOT NULL, \
      Runtime TEXT NOT NULL, \
      Genre TEXT NOT NULL, \
      Director TEXT NOT NULL, \
      Writer TEXT NOT NULL, \
      Actors TEXT NOT NULL, \
      Plot TEXT NOT NULL, \
      Language TEXT NOT NULL, \
      Country TEXT NOT NULL, \
      Awards TEXT NOT NULL, \
      Poster TEXT NOT NULL)")
      insert_sql("INSERT INTO Filma1 (Title, Year, Rated, Released, Runtime, Genre, Director, Writer, Actors, Plot, Language, Country, Awards, Poster) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", [
        x1[0]["Title"],
        x1[0]["Year"],
        x1[0]["Rated"],
        x1[0]["Released"],
        x1[0]["Runtime"],
        x1[0]["Genre"],
        x1[0]["Director"],
        x1[0]["Writer"],
        x1[0]["Actors"],
        x1[0]["Plot"],
        x1[0]["Language"],
        x1[0]["Country"],
        x1[0]["Awards"],
        x1[0]["Poster"]
      ])

      select_sql("DROP TABLE IF EXISTS Filma2")
      select_sql("CREATE TABLE IF NOT EXISTS Filma2 (\
      filma_ID INTEGER PRIMARY KEY AUTOINCREMENT, \
      Title TEXT NOT NULL, \
      Year TEXT NOT NULL, \
      Rated TEXT NOT NULL, \
      Released TEXT NOT NULL, \
      Runtime TEXT NOT NULL, \
      Genre TEXT NOT NULL, \
      Director TEXT NOT NULL, \
      Writer TEXT NOT NULL, \
      Actors TEXT NOT NULL, \
      Plot TEXT NOT NULL, \
      Language TEXT NOT NULL, \
      Country TEXT NOT NULL, \
      Awards TEXT NOT NULL, \
      Poster TEXT NOT NULL)")
      insert_sql("INSERT INTO Filma2 (Title, Year, Rated, Released, Runtime, Genre, Director, Writer, Actors, Plot, Language, Country, Awards, Poster) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", [
        x2[0]["Title"],
        x2[0]["Year"],
        x2[0]["Rated"],
        x2[0]["Released"],
        x2[0]["Runtime"],
        x2[0]["Genre"],
        x2[0]["Director"],
        x2[0]["Writer"],
        x2[0]["Actors"],
        x2[0]["Plot"],
        x2[0]["Language"],
        x2[0]["Country"],
        x2[0]["Awards"],
        x2[0]["Poster"]
      ])
    return redirect("/salidzinat_rezultats")

  return render_template("salidzinat.html")


@app.route("/salidzinat_rezultats", methods = ["GET", "POST"])
def salidzinat_rezultats():
  rezultats1 = select_sql("SELECT * FROM Filma1")
  rezultats2 = select_sql("SELECT * FROM Filma2")
  return render_template("salidzinat_rezultats.html", rezultats1=rezultats1, rezultats2=rezultats2)


@app.route("/stest")
def info_raw():
  response = requests.get("http://www.omdbapi.com/?s=breaking+bad&apikey=ac26b569")
  if response.status_code == 200:
    x = response.json()
    print("Here should be the info about the show/movie: ")
    print(x)
  else:
    print("Error:", response.status_code)

  return redirect("/")


app.run(host='0.0.0.0', port=8080)