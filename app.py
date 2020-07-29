import os
import ssl

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import requests
from dash.dependencies import Input, Output


def named_fig(key, dict, name="", kind="line"):
    df = dict[key]
    return df.plot(title=name if name != "" else key, kind=kind)


# dataframes keys
confirmed_cases_14d_key = "casos_confirmados_ultimos_14dias"
tia_14d_key = "tasa_incidencia_acumulada_ultimos_14dias"
confirmed_cases_dayone_key = "casos_confirmados_totales"
tia_dayone_key = "tasa_incidencia_acumulada_total"
cam_confirmed_cases_dayone_key = "madrid_casos_confirmados_totales"
cam_confirmed_cases_14d_key = "madrid_casos_confirmados_ultimos_14dias"
new_cases_dayone_key = "new_cases"
top_10_zsb_14d_key = "top_10_zsb_14d"
zone_key = "zona_basica_salud"
date_key = "fecha_informe"

figures_keys = [
    confirmed_cases_14d_key,
    tia_14d_key,
    confirmed_cases_dayone_key,
    tia_dayone_key,
]
cam_zone_key = "cam"
local_csv = os.environ["LOCAL_CSV"]
ssl._create_default_https_context = ssl._create_unverified_context
source = (
    "./data/covid19_tia_zonas_basicas_salud.csv"
    if local_csv
    else "https://datos.comunidad.madrid/catalogo/dataset/b3d55e40-8263-4c0b-827d-2bb23b5e7bab/resource/b7b9edb4-0c70-47d3-9c64-8c4913830a24/download/covid19_tia_zonas_basicas_salud.csv"
)
big_df_pre_july_2nd = pd.read_csv(
    source, sep=";", encoding="latin_1", decimal=",", parse_dates=[date_key],
).fillna(0.0)


source = (
    "./data/covid19_tia_zonas_basicas_salud_s.csv"
    if local_csv
    else "https://datos.comunidad.madrid/catalogo/dataset/b3d55e40-8263-4c0b-827d-2bb23b5e7bab/resource/43708c23-2b77-48fd-9986-fa97691a2d59/download/covid19_tia_zonas_basicas_salud_s.csv"
)
big_df_post_july_2nd = pd.read_csv(
    source, sep=";", encoding="latin_1", decimal=",", parse_dates=[date_key],
).fillna(0.0)

big_df = pd.concat([big_df_pre_july_2nd, big_df_post_july_2nd])

big_df.drop_duplicates([date_key, zone_key], inplace=True)

all_zsbs = big_df[[zone_key]].drop_duplicates()

max_date = big_df[date_key].max()

figure_dfs = {}
for key in figures_keys:
    df = big_df.pivot(index=date_key, columns=zone_key, values=key)
    df.loc[:, cam_zone_key] = df.sum(axis=1)
    figure_dfs[key] = df

pd.options.plotting.backend = "plotly"

dfs = {}

all_zsb_14d_df = (
    big_df[big_df[date_key] == max_date][
        [zone_key, tia_14d_key, confirmed_cases_14d_key]
    ]
    .set_index(zone_key)
    .sort_values(by=[tia_14d_key, confirmed_cases_14d_key], ascending=False)
)

top_10_zsb_14d_df = all_zsb_14d_df.head(10)

default_zones_df = top_10_zsb_14d_df.head(4)

dfs.update(
    {top_10_zsb_14d_key: top_10_zsb_14d_df[[tia_14d_key, confirmed_cases_14d_key]]}
)

dfs.update(
    {cam_confirmed_cases_14d_key: figure_dfs[confirmed_cases_14d_key][cam_zone_key]}
)

dfs.update(
    {
        cam_confirmed_cases_dayone_key: figure_dfs[confirmed_cases_dayone_key][
            cam_zone_key
        ]
    }
)

dfs.update(
    {new_cases_dayone_key: figure_dfs[confirmed_cases_dayone_key][cam_zone_key].diff()}
)

app = dash.Dash(
    "Covid Madrid by Tesla Cool Lab",
    external_stylesheets=[dbc.themes.FLATLY],
    external_scripts=["static/js.js"],
)


@app.callback(Output("figures", "children"), [Input("zones", "value")])
def update_zones(zones):

    if not len(zones):
        return []
    dfs = {}

    for key, df in figure_dfs.items():
        dfs.update({key: df[zones]})

    dfs.update(
        {new_cases_dayone_key: figure_dfs[confirmed_cases_dayone_key][zones].diff()}
    )

    figures = [
        dbc.Col(
            dcc.Graph(
                figure=named_fig(
                    confirmed_cases_14d_key, dfs, "Casos confirmados 14 días",
                ),
            ),
            lg=6,
        ),
        dbc.Col(
            dcc.Graph(
                figure=named_fig(tia_14d_key, dfs, "Tasa incidencia acumulada 14 días",)
            ),
            lg=6,
        ),
        dbc.Col(
            dcc.Graph(
                figure=named_fig(
                    confirmed_cases_dayone_key, dfs, "Casos confirmados totales",
                )
            ),
            lg=6,
        ),
        dbc.Col(
            dcc.Graph(figure=named_fig(new_cases_dayone_key, dfs, "Nuevos casos",)),
            lg=6,
        ),
        dbc.Col(
            dcc.Graph(
                figure=named_fig(
                    tia_dayone_key, dfs, "Tasa incidencia acumulada día cero",
                )
            ),
            lg=6,
        ),
    ]
    return figures


app.layout = dbc.Container(
    [
        html.H1("Información epidemiológica Covid - 19"),
        html.Hr(),
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
                "Hasta el 1 de julio de 2020 los registros de datos correspondientes a cada fecha de informe se han añadido diariamente. ",
                html.Em(
                    "A partir del 2 de julio de 2020 la actualización pasa a ser semanal."
                ),
            ],
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
        html.H2("Comunidad de Madrid"),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(
                        figure=named_fig(
                            top_10_zsb_14d_key,
                            dfs,
                            "Top 10 zonas sanitarias básicas 14 días",
                            "barh",
                        )
                    ),
                    lg=6,
                ),
                dbc.Col(
                    dcc.Graph(
                        figure=named_fig(
                            cam_confirmed_cases_14d_key,
                            dfs,
                            "Comunidad de Madrid: casos confirmados 14 días",
                        )
                    ),
                    lg=6,
                ),
                dbc.Col(
                    dcc.Graph(
                        figure=named_fig(
                            new_cases_dayone_key,
                            dfs,
                            "Comunidad de Madrid: nuevos casos",
                        ),
                    ),
                    lg=6,
                ),
                dbc.Col(
                    dcc.Graph(
                        figure=named_fig(
                            cam_confirmed_cases_dayone_key,
                            dfs,
                            "Comunidad de Madrid: casos confirmados totales",
                        ),
                    ),
                    lg=6,
                ),
            ],
        ),
        html.H2("Por zonas sanitarias básicas"),
        html.Hr(),
        html.Label("Seleccione zonas sanitarias básicas"),
        dcc.Dropdown(
            id="zones",
            options=[
                {"label": row[zone_key], "value": row[zone_key]}
                for _, row in all_zsbs.iterrows()
            ],
            value=[zone_key for zone_key in default_zones_df.index],
            multi=True,
        ),
        dbc.Row(id="figures"),
        html.Hr(),
        html.P(
            [
                "Hecho con 🐍 en ",
                html.A("Tesla Cool Lab", href="https://teslacoollab.com/"),
            ],
            className="text-center",
        ),
    ],
    fluid=True,
)


server = app.server

if __name__ == "__main__":
    app.run_server(debug=True, use_reloader=True)  # Turn off reloader if inside Jupyter
