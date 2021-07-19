import math
import os
import ssl

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objects as go
import requests
from dash.dependencies import Input, Output
from plotly.subplots import make_subplots


def dual_fig(key, dict, y_left_column, y_right_column, name=""):
    df = dict[key]
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(x=df.index, y=df[y_left_column], name=y_left_column),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df[y_right_column], name=y_right_column),
        secondary_y=True,
    )
    fig.update_layout(title_text=name, hovermode="x")
    return fig


def named_fig(key, dict, name="", kind="line"):
    df = dict[key]
    return df.plot(title=name if name != "" else key, kind=kind)


# dataframes keys
confirmed_cases_14d_key = "casos_confirmados_ultimos_14dias"
tia_14d_key = "tasa_incidencia_acumulada_ultimos_14dias"
confirmed_cases_dayone_key = "casos_confirmados_totales"
tia_dayone_key = "tasa_incidencia_acumulada_total"
cam_confirmed_cases_dayone_key_pre_july_2nd = (
    "madrid_casos_confirmados_totales_pre_july_2nd"
)
cam_confirmed_cases_14d_pre_july_2nd_key = (
    "madrid_casos_confirmados_ultimos_14dias_pre_july_2nd"
)
cam_confirmed_cases_dayone_post_july_2nd_key = (
    "madrid_casos_confirmados_totales_post_july_2nd"
)
cam_confirmed_cases_14d_post_july_2nd_key = (
    "madrid_casos_confirmados_ultimos_14dias_post_july_2nd"
)
new_cases_dayone_pre_july_2nd_key = "new_cases_pre_july_2nd"
new_cases_dayone_key_post_july_2nd = "new_cases_post_july_2nd"
zone_key = "zona_basica_salud"
date_key = "fecha_informe"

figures_keys = [
    confirmed_cases_14d_key,
    tia_14d_key,
    confirmed_cases_dayone_key,
    tia_dayone_key,
]
cam_zone_key = "cam"
cam_new_cases_key = "nuevos casos CAM"
growth_rate_key = "tasa de crecimiento"

try:
    local_csv = os.environ["LOCAL_CSV"] == "1"
except KeyError:
    local_csv = False

source = "./data/covid19_tia_zonas_basicas_salud.csv"
big_df_pre_july_2nd = (
    pd.read_csv(
        source, sep=";", encoding="latin_1", decimal=",", parse_dates=[date_key],
    )
    .fillna(0.0)
    .drop_duplicates([date_key, zone_key], inplace=False)
)

ssl._create_default_https_context = ssl._create_unverified_context
source = (
    "./data/covid19_tia_zonas_basicas_salud_s.csv"
    if local_csv
    else "https://datos.comunidad.madrid/catalogo/dataset/b3d55e40-8263-4c0b-827d-2bb23b5e7bab/resource/43708c23-2b77-48fd-9986-fa97691a2d59/download/covid19_tia_zonas_basicas_salud_s.csv"
)

big_df_post_july_2nd = (
    pd.read_csv(
        source, sep=";", encoding="latin_1", decimal=",", parse_dates=[date_key],
    )
    .fillna(0.0)
    .drop_duplicates([date_key, zone_key], inplace=False)
)

mask = big_df_post_july_2nd[date_key] >= "2020-07-07"

big_df_post_july_2nd = big_df_post_july_2nd.loc[mask]

all_zsbs = big_df_post_july_2nd[[zone_key]].drop_duplicates()

max_date = big_df_post_july_2nd[date_key].max()

figure_dfs_pre_july_2nd = {}
for key in figures_keys:
    df = big_df_pre_july_2nd.pivot(index=date_key, columns=zone_key, values=key)
    df.loc[:, cam_zone_key] = df.sum(axis=1)
    figure_dfs_pre_july_2nd[key] = df

figure_dfs_post_july_2nd = {}
for key in figures_keys:
    df = big_df_post_july_2nd.pivot(index=date_key, columns=zone_key, values=key)
    df.loc[:, cam_zone_key] = df.sum(axis=1)
    figure_dfs_post_july_2nd[key] = df

pd.options.plotting.backend = "plotly"

dfs = {}

sorted_by_tia_14d_df = (
    big_df_post_july_2nd[big_df_post_july_2nd[date_key] == max_date][
        [zone_key, tia_14d_key, confirmed_cases_14d_key]
    ]
    .set_index(zone_key)
    .sort_values(by=[tia_14d_key, confirmed_cases_14d_key], ascending=True)
)

max_tia = math.ceil(sorted_by_tia_14d_df[tia_14d_key].max())

default_zones_df = sorted_by_tia_14d_df.tail(4)

new_cases_dayone_post_july_df = (
    figure_dfs_post_july_2nd[confirmed_cases_dayone_key][cam_zone_key]
    .diff()
    .to_frame()
    .rename(columns={cam_zone_key: cam_new_cases_key})
)

new_cases_dayone_post_july_df[growth_rate_key] = new_cases_dayone_post_july_df[
    cam_new_cases_key
].pct_change()

dfs = {
    cam_confirmed_cases_14d_pre_july_2nd_key: figure_dfs_pre_july_2nd[
        confirmed_cases_14d_key
    ][cam_zone_key],
    cam_confirmed_cases_dayone_key_pre_july_2nd: figure_dfs_pre_july_2nd[
        confirmed_cases_dayone_key
    ][cam_zone_key],
    cam_confirmed_cases_14d_post_july_2nd_key: figure_dfs_post_july_2nd[
        confirmed_cases_14d_key
    ][cam_zone_key],
    cam_confirmed_cases_dayone_post_july_2nd_key: figure_dfs_post_july_2nd[
        confirmed_cases_dayone_key
    ][cam_zone_key],
    new_cases_dayone_pre_july_2nd_key: figure_dfs_pre_july_2nd[
        confirmed_cases_dayone_key
    ][cam_zone_key].diff(),
    new_cases_dayone_key_post_july_2nd: new_cases_dayone_post_july_df,
}

app = dash.Dash(
    "Covid Madrid by Tesla Cool Lab",
    external_stylesheets=[dbc.themes.FLATLY],
    external_scripts=["static/js.js"],
)


@app.callback(Output("tia-figure", "figure"), [Input("tia-14d-rangeslider", "value")])
def update_tia(value):
    filtered_tia_14d_zsb_df = sorted_by_tia_14d_df[
        sorted_by_tia_14d_df[tia_14d_key].between(value[0], value[1], inclusive=True)
    ]

    filtered_tia_fig = filtered_tia_14d_zsb_df.plot(
        title=f"Zonas sanitarias con tasa de incidencias acumulada a 14 días entre {value[0]} y {value[1]}",
        kind="bar",
    )
    filtered_tia_fig.update_layout(
        autosize=True, xaxis=dict(tickmode="linear", dtick=1),
    )
    return filtered_tia_fig


@app.callback(Output("figures", "children"), [Input("zones", "value")])
def update_zones(zones):

    if not len(zones):
        return []
    dfs = {}

    for key, df in figure_dfs_post_july_2nd.items():
        dfs.update({key: df[zones]})

    dfs.update(
        {
            new_cases_dayone_key_post_july_2nd: figure_dfs_post_july_2nd[
                confirmed_cases_dayone_key
            ][zones].diff()
        }
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
            dcc.Graph(
                figure=named_fig(
                    new_cases_dayone_key_post_july_2nd, dfs, "Nuevos casos",
                )
            ),
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
                "Mapa disponible ",
                html.A(
                    "aquí",
                    href="https://comunidadmadrid.maps.arcgis.com/apps/PublicInformation/index.html?appid=7db220dc2e0a40b4a928df661a89762e",
                ),
            ]
        ),
        html.H2("Comunidad de Madrid: desde 2 de julio de 2020"),
        html.P(
            [
                "A partir del día 2 julio de 2020 la Comunidad de Madrid publica sus informes de forma semanal. Las siguientes gráficas se nutren de los datos publicados en este ",
                html.A(
                    "enlace",
                    href="https://datos.comunidad.madrid/catalogo/dataset/covid19_tia_zonas_basicas_salud/resource/43708c23-2b77-48fd-9986-fa97691a2d59",
                ),
                ".",
            ]
        ),
        html.Hr(),
        html.Label(
            "Filtre zonas sanitarias básicas por Tasa de Incidencia Acumulada a 14 días"
        ),
        dbc.Row(
            [
                dbc.Col(
                    dcc.RangeSlider(
                        id="tia-14d-rangeslider",
                        min=0,
                        max=max_tia + 100,
                        step=10,
                        value=[max_tia / 2, max_tia],
                        marks={i: str(i) for i in range(0, max_tia + 100, 100)},
                        included=True,
                        allowCross=False,
                    ),
                    lg=12,
                ),
                dbc.Col(dcc.Graph(id="tia-figure"), lg=12,),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(
                        figure=named_fig(
                            cam_confirmed_cases_14d_post_july_2nd_key,
                            dfs,
                            "Comunidad de Madrid: casos confirmados 14 días",
                        )
                    ),
                    lg=6,
                ),
                dbc.Col(
                    dcc.Graph(
                        figure=dual_fig(
                            key=new_cases_dayone_key_post_july_2nd,
                            dict=dfs,
                            y_left_column=cam_new_cases_key,
                            y_right_column=growth_rate_key,
                            name="Comunidad de Madrid: nuevos casos",
                        )
                    ),
                    lg=6,
                ),
                dbc.Col(
                    dcc.Graph(
                        figure=named_fig(
                            cam_confirmed_cases_dayone_post_july_2nd_key,
                            dfs,
                            "Comunidad de Madrid: casos confirmados totales",
                        ),
                    ),
                    lg=6,
                ),
            ],
        ),
        html.H2("Por zonas sanitarias básicas desde el 2 de julio de 2020"),
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
        html.H2("Comunidad de Madrid hasta 1 de julio de 2020"),
        html.Hr(),
        html.P(
            [
                "Hasta el día 1 de julio de 2020 la Comunidad de Madrid publicaba sus datos diariamente. Proporcionamos las gráficas basadas en ",
                html.A(
                    "estos datos",
                    href="https://datos.comunidad.madrid/catalogo/dataset/covid19_tia_zonas_basicas_salud/resource/b7b9edb4-0c70-47d3-9c64-8c4913830a24",
                ),
                " históricos por separado de los datos semanales. ",
                html.Em(
                    "A partir del 2 de julio de 2020 la actualización pasa a ser semanal."
                ),
            ],
        ),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(
                        figure=named_fig(
                            cam_confirmed_cases_14d_pre_july_2nd_key,
                            dfs,
                            "Comunidad de Madrid: casos confirmados 14 días",
                        )
                    ),
                    lg=6,
                ),
                dbc.Col(
                    dcc.Graph(
                        figure=named_fig(
                            new_cases_dayone_pre_july_2nd_key,
                            dfs,
                            "Comunidad de Madrid: nuevos casos",
                        ),
                    ),
                    lg=6,
                ),
                dbc.Col(
                    dcc.Graph(
                        figure=named_fig(
                            cam_confirmed_cases_dayone_key_pre_july_2nd,
                            dfs,
                            "Comunidad de Madrid: casos confirmados totales",
                        ),
                    ),
                    lg=6,
                ),
            ],
        ),
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
    # Turn off reloader if inside Jupyter
    app.run_server(debug=True, use_reloader=True)
