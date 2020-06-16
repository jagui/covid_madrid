import base64
import datetime
import locale
import math
import string as _string
import typing
from io import BytesIO
import matplotlib
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import requests
import seaborn as sns


def paint_madrid(zones: list = None) -> (dict, datetime.date):
    matplotlib.use("Agg")
    url = "https://datos.comunidad.madrid/catalogo/dataset/b3d55e40-8263-4c0b-827d-2bb23b5e7bab/resource/01a7d2e8-67c1-4000-819d-3356bb514d05/download/covid19_tia_zonas_basicas_salud.json"

    if zones == None:
        zones = [
            "Montecarmelo",
            "Mirasierra",
            "Las Tablas",
            "Fuencarral",
        ]

    zone_key = "zona_basica_salud"

    date_key = "fecha_informe"

    figures_keys = [
        "casos_confirmados_ultimos_14dias",
        "tasa_incidencia_acumulada_ultimos_14dias",
        "casos_confirmados_totales",
        "tasa_incidencia_acumulada_total",
    ]

    rsp = requests.get(url, verify=False)

    if rsp.status_code != 200:
        exit

    data = rsp.json()["data"]

    def equal_strings(a: str, b: str) -> bool:
        cleaner = str.maketrans(
            _string.ascii_uppercase,
            _string.ascii_lowercase,
            _string.punctuation + _string.whitespace,
        )
        return str.translate(a, cleaner) == str.translate(b, cleaner)

    results = {}
    for zone in zones:
        zone_data = [x for x in data if equal_strings(x[zone_key], zone)]
        results[zone] = {}
        for key in figures_keys:
            results[zone][key] = list(
                map(lambda item: item[key] if key in item else 0, zone_data)
            )
            results[zone][date_key] = list(
                map(
                    lambda item: datetime.datetime.strptime(
                        item[date_key], "%Y/%m/%d %H:%M:%S"
                    ),
                    zone_data,
                )
            )

    # locale.setlocale(locale.LC_ALL, "es_ES.utf8")
    max_date = max(
        [d for x in results.values() for k, v in x.items() if k == date_key for d in v]
    ).isoformat()

    graphs_count = len(figures_keys)
    cols_count = 2
    months_locator = mdates.MonthLocator()
    months_formatter = mdates.DateFormatter("%b")
    days_locator = mdates.WeekdayLocator(byweekday=mdates.MONDAY)
    days_formatter = mdates.DateFormatter("%d")
    sns.set()
    sns.set_context("notebook")

    figs = {}

    for i in range(graphs_count):
        fig = plt.figure()
        ax = fig.add_subplot()
        for zone in zones:
            sns.lineplot(date_key, figures_keys[i], label=zone, data=results[zone])
        ax.xaxis.set_major_locator(months_locator)
        ax.xaxis.set_major_formatter(months_formatter)
        ax.xaxis.set_minor_locator(days_locator)
        ax.xaxis.set_minor_formatter(days_formatter)
        ax.xaxis.set_tick_params(which="major", pad=10)
        ax.set_title(figures_keys[i])
        ax.legend()
        fig.tight_layout()
        buf = BytesIO()
        fig.savefig(buf, format="png")
        plt.close(fig)
        data = base64.b64encode(buf.getbuffer()).decode("ascii")
        figs[figures_keys[i]] = data
    plt.close()
    return figs, max_date


if __name__ == "__main__":
    paint_madrid()
    plt.show()
