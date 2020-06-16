import madrid
from flask import Flask
from flask import request
from flask import redirect
from flask import render_template
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

app = Flask(__name__)


@app.route("/")
def hello():
    queryStringDict = request.args
    if "zsb" not in queryStringDict:
        return redirect("/?zsb=Montecarmelo,Las Tablas,Mirasierra,Fuencarral", code=302)

    zsbs = queryStringDict["zsb"].split(",")
    figs, date = madrid.paint_madrid(zsbs)
    datas = [fig for fig in figs.values()]
    return render_template("hello.html", datas=datas, date=date)
