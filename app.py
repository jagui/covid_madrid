import base64
from io import BytesIO
import madrid
from flask import Flask
from flask import request
from flask import redirect
from flask import render_template
from matplotlib.figure import Figure

app = Flask(__name__)


@app.route("/")
def hello():
    queryStringDict = request.args
    if "zsb" not in queryStringDict:
        return redirect("/?zsb=Montecarmelo,Las Tablas,Mirasierra,Fuencarral", code=302)

    zsbs = queryStringDict["zsb"].split(",")
    fig, date = madrid.paint_madrid(zsbs)
    buf = BytesIO()
    fig.savefig(buf, format="png")
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return render_template("hello.html", data=data, date=date)
