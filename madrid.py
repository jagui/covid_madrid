import ssl

import pandas as pd
import requests


def named_fig(key, df, kind="line") -> dict:
    return {key: df.plot(title=key, kind=kind)}


def get_madrid_figs(zones: list = None):

    if zones == None:
        zones = [
            "Montecarmelo",
            "Mirasierra",
            "Las Tablas",
            "Fuencarral",
        ]

    zone_key = "zona_basica_salud"
    date_key = "fecha_informe"
    confirmed_cases_14d_key = "casos_confirmados_ultimos_14dias"
    cur_14d_key = "tasa_incidencia_acumulada_ultimos_14dias"
    confirmed_cases_dayone_key = "casos_confirmados_totales"
    cur_dayone_key = "tasa_incidencia_acumulada_total"
    figures_keys = [
        confirmed_cases_14d_key,
        cur_14d_key,
        confirmed_cases_dayone_key,
        cur_dayone_key,
    ]
    cam_confirmed_cases_dayone_key = "madrid_casos_confirmados_totales"
    cam_confirmed_cases_14d_key = "madrid_casos_confirmados_ultimos_14dias"
    cam_zone_key = "cam"

    ssl._create_default_https_context = ssl._create_unverified_context
    source = "https://datos.comunidad.madrid/catalogo/dataset/b3d55e40-8263-4c0b-827d-2bb23b5e7bab/resource/b7b9edb4-0c70-47d3-9c64-8c4913830a24/download/covid19_tia_zonas_basicas_salud.csv"
    big_df = pd.read_csv(
        source, sep=";", encoding="latin_1", decimal=",", parse_dates=[date_key],
    ).fillna(0.0)

    max_date = big_df[date_key].max()

    figure_dfs = {}
    for key in figures_keys:
        df = big_df.pivot(index=date_key, columns=zone_key, values=key)
        df.loc[:, cam_zone_key] = df.sum(axis=1)
        figure_dfs[key] = df

    pd.options.plotting.backend = "plotly"

    figs = {}

    all_zsb_14d = (
        big_df[big_df[date_key] == max_date][
            [zone_key, cur_14d_key, confirmed_cases_14d_key]
        ]
        .set_index(zone_key)
        .sort_values(by=[cur_14d_key, confirmed_cases_14d_key], ascending=False)
    )

    top_10_zsb_14d = all_zsb_14d.head(10)

    figs.update(named_fig("top_10_zsb_14d", top_10_zsb_14d, "barh"))

    figs.update(
        named_fig(
            cam_confirmed_cases_14d_key,
            figure_dfs[confirmed_cases_14d_key][cam_zone_key],
        )
    )

    figs.update(
        named_fig(
            cam_confirmed_cases_dayone_key,
            figure_dfs[confirmed_cases_dayone_key][cam_zone_key],
        )
    )

    for key, df in figure_dfs.items():
        figs.update(named_fig(key, df[zones]))

    return figs, max_date
