import madrid as madrid
import dash
import dash_core_components as dcc
import dash_html_components as html


def named_fig(key, dict, name="", kind="line"):
    df = dict[key]
    return df.plot(title=name if name != "" else key, kind=kind)


dfs, max_date = madrid.get_madrid_dataframes()

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
            children=[
                dcc.Graph(
                    figure=named_fig(
                        madrid.top_10_zsb_14d_key,
                        dfs,
                        "Top 10 zonas sanitarias básicas 14 días",
                        "barh",
                    )
                ),
                dcc.Graph(
                    figure=named_fig(
                        madrid.cam_confirmed_cases_14d_key,
                        dfs,
                        "Comunidad de Madrid: casos confirmados 14 días",
                    )
                ),
                dcc.Graph(
                    figure=named_fig(
                        madrid.cam_confirmed_cases_dayone_key,
                        dfs,
                        "Comunidad de Madrid: casos confirmados totales",
                    )
                ),
                dcc.Graph(
                    figure=named_fig(
                        madrid.confirmed_cases_14d_key,
                        dfs,
                        "Top 4 casos confirmados 14 días",
                    )
                ),
                dcc.Graph(
                    figure=named_fig(
                        madrid.cur_14d_key,
                        dfs,
                        "Top 4: tasa incidencia acumulada 14 días",
                    )
                ),
                dcc.Graph(
                    figure=named_fig(
                        madrid.confirmed_cases_dayone_key,
                        dfs,
                        "Top 4: casos confirmados totales",
                    )
                ),
                dcc.Graph(
                    figure=named_fig(
                        madrid.cur_dayone_key,
                        dfs,
                        "Top 4: tasa incidencia acumulada día cero",
                    )
                ),
            ],
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
