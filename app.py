import base64
from io import BytesIO
import madrid
from flask import Flask
from flask import request
from flask import redirect
from matplotlib.figure import Figure

app = Flask(__name__)


@app.route("/")
def hello():
    queryStringDict = request.args
    if "zsb" not in queryStringDict:
        return redirect("/?zsb=Montecarmelo,Las Tablas,Mirasierra,Fuencarral", code=302)

    zsbs = queryStringDict["zsb"].split(",")
    fig = madrid.paint_madrid(zsbs)
    buf = BytesIO()
    fig.savefig(buf, format="png")
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    html = """<div style="display:flex;align-items:center;flex-flow:column">
                <div>
                    <p>Datos actualizados desde la <a href="https://datos.comunidad.madrid/catalogo/dataset/covid19_tia_zonas_basicas_salud">Comunidad de Madrid</a>.</p>
                    <p>Para mostrar otras zonas sanitarias básicas modifica la url.</p></du
                    <p>Mapa disponible <a href="https://comunidadmadrid.maps.arcgis.com/apps/PublicInformation/index.html?appid=7db220dc2e0a40b4a928df661a89762e">aquí</a>.</p>
                </div>
                <div>"""
    html += f"<img src='data:image/png;base64,{data}'/></div><div>"
    return html
