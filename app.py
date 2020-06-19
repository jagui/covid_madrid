import madrid as madrid
import dash
import dash_core_components as dcc
import dash_html_components as html

figs, max_date = madrid.get_madrid_figs()

app = dash.Dash(
    __name__,
    external_stylesheets=["static/style.css"],
    external_scripts=["static/js.js"],
)

app.layout = html.Div(
    className="container",
    children=[
        html.Div(
            [
                html.H1("Información epidemiológica Covid - 19"),
                html.P(
                    [
                        "Última actualización el ",
                        html.Em(max_date, id="date"),
                        " desde la ",
                        html.A(
                            "Comunidad de Madrid",
                            href="https://datos.comunidad.madrid/catalogo/dataset/covid19_tia_zonas_basicas_salud",
                        ),
                    ]
                ),
                html.P("Para mostrar otras zonas sanitarias básicas modifica la url."),
                html.P(
                    [
                        "Mapa disponible ",
                        html.A(
                            "aquí",
                            href="https://comunidadmadrid.maps.arcgis.com/apps/PublicInformation/index.html?appid=7db220dc2e0a40b4a928df661a89762e",
                        ),
                    ]
                ),
            ]
        ),
        html.Div(
            className="img-container",
            children=[dcc.Graph(figure=fig) for key, fig in figs.items()],
        ),
        html.Div(
            children=[
                html.P(
                    [
                        "Hecho con Python en ",
                        html.A("Tesla Cool Lab", href="https://teslacoollab.com/"),
                    ]
                )
            ]
        ),
    ],
)

server = app.server

if __name__ == "__main__":
    app.run_server(debug=True, use_reloader=True)  # Turn off reloader if inside Jupyter
