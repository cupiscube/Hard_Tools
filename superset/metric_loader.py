# from idlelib import query
from urllib.parse import quote

import requests
# import json
# from urllib.parse import urljoin
# import ast
# import copy
# import os
# import typer
# from pycparser.ply.cpp import tokens
#
# from superset_warm_cash import params
from utils.session import setup_session
from utils.dashboard import get_dashboard, create_dashboard, duplicate_dashboard_with_charts_and_layout
from utils.chart import get_charts_from_layout, clone_charts
from utils.dataset import get_dataset, create_dataset, create_new_metrics, get_metrics
from utils.database import create_db

from metric_sample import kpi_metrics

from utils.config import KEYCLOAK_URL, KEYCLOAK_REALM, KEYCLOAK_CLIENT_ID, KEYCLOAK_CLIENT_SECRET



# setup_session >> create_db >> create dataset >> load metrics

cookie = ".eJy9VsmSo0gS_ZUxnafaiAAkUbfUAoIUQbETMTaWxiZBECBlog3a-t_HUVZ1V82c-jIntgj35_78PeL32dvho-yr2ddDKvryn7O3uph9nc0VlGNNQYf5ci4dZJylqSZlGKVYLZC6XBRZuTwo6mEul6WKD0ukLdAyRwgvUglLGBeqrKqpkqeFImtzVUkXaI6VQs6kcqGkKkZZWsCnZXaQs1zCB4QOOJtjGeVzdamq8gyAXPvy4xPN9ChOeSpKeCg7eDql1wtg_n32j8vs679m5WBVmZHXTm354WgiUpu92XlqvjaPTv1S-6IIzfpep1g0Zv0yN9fWPdTP-6wVXtyRuyefz57sKqEc3YhciHLHEhKsUBxaI5OZ4Qr9yqRHaCc6MTvpN8gHa15qh29lwreDEzSKE2x7sxVVsTbndpBjOzBVJ8gftn-vaRJJqa5JaYyEyU8PMtKHzRuVjNvHfm29F0YD2E14d1RZQCrmo5bGFO8Dr2K8uTgb0bC1pDIeSiRgFR31lnGzhr3nXLanuk_Fzrvn4-m2l6OK-mqXYVWiidVQLMS-1a6ZIa7M1wYW632W2DdPIpbnQ59aHTHADFdOsYayzp3ijkVsTpgUwNNSTgSpUcNad9gH7kA4BUwuYrWEbKw3ZGxkGzNOx3DaK5XJy4RpDbkGljxxVmX3fDcWyUrkHRHFGknQZWniJZ944aeaxiHUGFVsQy_EsEfmS5LNdb6PtzLkuxBMWicmjWPold2692kvjckw7bU_a-kzQ5NZ7F4y2TozLK75YM7jwby91lYBOD7rj7SKYiKevev6Om-1niVwL_qaGVELfPWAb8jwQ-QD6qYeTrkyzNpnH3_aDzFRFuuHJ8eGNqTJuSoMccsg3wG4z9tozORooDg6AFYONY8mPy_MjqDciIYcR9I-8SCW-z9Y3Ni7pLFSJ4nU_8zPf6-D_FcaF2If_8LhhcZqxXB4mfIChivU1Kex-gE9AX2wM0vyS76zbqwVPfMB75Snm9aupjmtpytopDF3K-gFO2dGePye98hiVKXxfcojIP850zXMEuh5K8Q0T8XOQgzqz1r9wnyYr8arIFZvbq0KvlUp1vCT-50lWAt9aKMmkaMRYkAtT50AF7-uBW45jR-f36AvkLtLEyYyof25xzP063dcoCF0znbi8BeGX-P9qAHmsqGtLuWt_pHJ7IVh7VoYMLsGOTNf5RmWpni3vC12UD_Kd1PfLwuzVassDiedILI5yiQ2FbJGLQlyBXQCs3wEnVQc9NywIBwYrwTbrCrHoHO3aZ76_a69ho6uzDaE74NVQwyY_40Q9iCBh9iguVwCjd3BV8Bn8sGe-GtBy9KnbkjgKmSM6kkj4BGys5YkJ6aA4ahQ4J8ZIbJbqoAu7jSo2mfff5qfIIyI20S-KZC23_V_cQZ-42xyRPlR2scUkfE44WohvuIYBObNEySwWseIGtvYKoyfN6A7YeqeoLH0U32sAhcdGS8awHQn7RbiuJI9oJpivYbYdxLQu81fRlBI4_j_r_qKmo4rzvjU9wY4DMF3XAX4qoFP8F_WkjF8sGArEZ5jFpw_-V-_PJ7_k9h9zg4Br6a8GcggyTa3JfBtMXFPOWCqEafgaZSDbwdFa4_bH7NkPXvzdzFMvemsW2ZEk49kZoP0ILT0cPKbaNKvB5rVr9N_aPK9v9s7pyGALTxGRlRlvka8EK29aPJwiIUtbhuktbF9cQL4F4E_s00Fc2DCnMDMtlQmgS7swMVkZMJpigF8525utrc_OYC-7ce_PVdr_ycs4Ie_nYfdYly8H6sby4LcMNjrQDz__bZpGp5nCXlNciSDM5YkOodsfzWMgyjjw6LLaYP7q-reXzXHYt7BPw-vo7Zm98qniZdrcTH45GR85PtSKTZBWfSqHHwh8asXHTLPabZM8-MA8RBmuH89EhtrRx_v9vpie48ex2-JtbGX-G3p5fO3eJOKdYoy4Rir9aNZDnCKkW_vaTdKl6AM7Qc6I5ei4MWlX3ho55uFg8d2n70GPGh4WuFT9_5OUsv86K91QXbOcc5R6al10qxedq_v74b01lV74-hf60OZcm-0rFbvltfIdTZSJhdF5nan681ajIfc2jXUypSP_iGCmHps0W2_mV6Mv3nri2j6Wl5rL3C2mv37j-8HrLfzx-lWF-UHHLuOeV1-acohF6e0-XECe-sv6WU6lHV96sqPg_oqrbT56rhOsJ3NU2W9CRdyxGd__AeYDHuI.aR2Wtg.kaGOT5rZY11-hNKLoil06qcEwhg"
COOKIES = {
    "session": cookie
}
# SUPERSET_URL = "http://10.100.100.50:8088"
SUPERSET_URL = "http://172.16.82.66:8088"
session = requests.Session()

admin_user_id = 2 # BADA


def main():
    setup_session(session=session,
                  SUPERSET_URL=SUPERSET_URL,
                  KEYCLOAK_URL=KEYCLOAK_URL,
                  KEYCLOAK_REALM=KEYCLOAK_REALM,
                  KEYCLOAK_CLIENT_ID=KEYCLOAK_CLIENT_ID,
                  KEYCLOAK_CLIENT_SECRET=KEYCLOAK_CLIENT_SECRET,
                  COOKIES=COOKIES)
    print("✅ Авторизация через Keycloak выполнена")

    for database in kpi_metrics["databases"]:
        db_name = database["database_name"]
        sqlalchemy_uri = database["sqlalchemy_uri"]
        # db_id = create_db(session=session,
        #                   SUPERSET_URI=SUPERSET_URL,
        #                   params={ "db_name": db_name,
        #                            "sqlalchemy_uri": sqlalchemy_uri,
        #                            "backend": "clickhousedb",})
        db_id = 7
        for dataset in database["datasets"]:
            table_name = dataset["table_name"]
            schema = dataset["schema"]
            dataset_id = create_dataset(SUPERSET_URL=SUPERSET_URL,
                                        session=session,
                                        params={"database_id": db_id,
                                                "table_name": table_name,
                                                "db_scheme_name": schema,
                                                "sql": "",
                                                "owners": [{"id": admin_user_id}]})
            create_new_metrics(session=session,
                               SUPERSET_URL=SUPERSET_URL,
                               dataset_id=dataset_id,
                               metrics=dataset["metrics"])
            print(f'Dataset {dataset_id} with schema {schema} with table {table_name} is updated/created')





if __name__ == "__main__":
    main()
