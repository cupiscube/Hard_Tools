# from idlelib import query
from urllib.parse import quote

import requests
import json
from urllib.parse import urljoin
import ast
import copy
import os
import typer
from pycparser.ply.cpp import tokens


KEYCLOAK_URL = 'https://uaa.gontardcie.online'
KEYCLOAK_REALM = 'GCIE'
KEYCLOAK_CLIENT_ID = 'superset-test'
KEYCLOAK_CLIENT_SECRET = 'LIy28VOsENAr97Sqba67BdbuM5zILwe8'

SOURCE_SUPERSET_URL = "http://10.100.100.50:8088"  # Без /superset в конце
# SOURCE_SUPERSET_URL = "https://dss.gontardcie.online"
# SOURCE_SUPERSET_URL = "http://159.100.244.234:8088"
# SOURCE_SUPERSET_URL = "https://dss.gontardcie.online"

# TARGET_SUPERSET_URL = "http://10.100.100.50:8088"  # Без /superset в конце
# TARGET_SUPERSET_URL = "https://dss.gontardcie.online"
# TARGET_SUPERSET_URL = "http://159.100.244.234:8088"
# TARGET_SUPERSET_URL = "https://dss.gontardcie.online"
TARGET_SUPERSET_URL = "http://172.16.82.66:8088"

SOURCE_DASHBOARD_ID = 92

NEW_TABLE_NAME = "demo_superset_labavatar" # None # "demo_superset_labavatar_TEST"
NEW_SCHEME_NAME = "labavatar_dev" # None #"demo_0"
NEW_DASHBOARD_TITLE = "Labavatar [DEMO]"


# ######################## SESSION ######################## #
# Login via browser -> f12 -> Application -> Cookie -> Session
cookie = ".eJydVtuSozgS_ZUNP29NCATY9JsLF1gUiOJutLFRYS7mjl0GX2Bi_n0TV_X09M6-9D7ZCCnz5DmZB_2-eD-cs75YfBvOl-yfi_cyXXxboKWE5ThZcXglZKlwwEISZ0uM90uM0AEny1iWZQnJqcjzK0nCqxXCh2wvJbEoJhwvSMkKrVKZTw_SSkrh5AFzS5SJ6VKUVhkvHjjMZbG8lDiJ5zn5cEglQZIyAaHVKuH3aAFALn12_kTDw2NzTPZNBg9ZB0_H_WUAyL8v_jEsvv1rkY16EWtJaZW660-EoyXpSeeIiUJyq1yXbpP6pLyVe76pSbmWiKLffPVkxG3jhB29Ofh0crAt-Di4Upw22ZbtqPfMhb4-Mcw0u1EvDN19c6dS0qHfIB_sWZdW9YJpZfNm9XIzq7wnbVOkCpFML-HpJhrNTY4s5VZGuwDtVRntQ64h1fFOpwjRitysjY0NRf9ItRqwE8Gc1iPbmBNTkMg0XzQ8-x6FL0NU6Y0JaybPWnPyecuzkVn5JZw9Jdic6z6mW-eWTMergYMicsUu5kUU7fQ64pvGaOVLrDUX5sojC9U-3plXB1HdcYGnVuUYYIbfKuJlLu7sOe6UhuSBiXm0jSra0JKrWWuPgGmkVTQAdo6ViDN5taZTjQFbFU0PTCjbrWdMCuQa2Y7Ma0XWPdamdPfcJB1tUoVDwDKadUlmXapjGfHRjVY1jqZ8oJ59M0uEKE_uhpfzLPQH5tnY2gQlnQBX9dzOZ6OQjvNZ87OWPtZkzEJ7iLF-YnxzSUYihSO5vpZ6Cjg-6w_kIuJp8-Cu68uklXu2g_9NXzItaEGvHvCNMX9vkpHrZg7nXDHw_-DxL-chJheH6uGhsSaP-92pSLXmGkO-gwu1tcEU42CM-OAAWCuoeSLVaUk6yiVaMCZ8gIydA7Hsv2GxQ2fYh0K526H-r_r89z7If4nCtDHCnzQcolAsGO8Pc17AcIGa-n0onoETmA92YrtkSLb6lbVNz1zAO-fp5r3Pc5-W8y_MSE22z8AFO8Wan3_lzVnIFfvwNudpIP8pVmWe7YDztmnmfkq3Oseg_rhVB-ZCf9VOAbF68qIX8K7Y8zL_0H6rN6wFHtqg3uFgghhQy2NOQIuf94K2VRTeP98BL5C72-9YEzfyn2ccTb184Wph7RRvm8MPDD_H-14D9GUdtSpKWvUcY7ZmvHxJNehdjZ6YK1Yxj-Z416RNt1A_l2xn3gfQUL_GWjDrGZOaUz1fV_3PPpv36o-5qnxkbRIuqnJkhBFH597eNK2lIMHSKGjmNNTTW0sLalN7EdjsXe3XPIRORTdpbfLmYGo2gnlDVuhPhleL5kQGOsE8eGvwk1yErpoeHH2v9VfzVifFdXXZ2P7cW54fULsOXNLMPQj-gT6xwXwKdApK8IGBVT6GuIAtEmBWhQh6DvyLM9tIgFm8RV7xmNV9aM9cgy4O1BRh8DnB3LACPAXRjTlELS2ikmvNjc-bG3Izp4hnm3rm_k99fzWvVVPQws8DLSji_1Gf7TvU9WHG5l7Feuc-MBIMGMCP02LmHPJwhue0zKsHy2MVnTFq_hRNETZbtYi8h8edPvV-uTHQxORtzgiJSEG7WUOIA_Gc2vCCypx00NYXo9a_P75VrVjEof__5JVc7lknqt4k4D2p8hzAjCH4RvXwjfryr9n_dOr4nOIE5G91Rq15A9-dohGJwO2cr7Y08IwKeC4RuHrCmSHg3ESYtv6POlvw_4qVlkew4SWjOdkDBe-0FK6kVdEaIS1pqJYUcFKI_-nPP-r8xbySg_VrulvnJmgIfvhben3ug_vlxLbK1C_FTtZ4E39s3Uwv-lUVXMmHqBDfxlkjupm_Vd5WeZd-OLa1e-uPG5keSGQl-Tt5nqqQ09qCLT8OTzyePDmc7i4zKvdtGhXzOpynHB-Z5iRdtuyRI2_e8kFz5fp2PL2qcjVOvXZ_ul7CJW-8kG0e6MjB5ElKK6Pyrp5L1F65Hc3TU7I_vwzHs1YhaiT3-p2sy2KbE6E_WPthdf9oNJ-o9MkYWy_-cDrtPnGnnN3f27fVShe5az2s3oXXdT4OgfrWdc6rpnNm7AqarHSvnkEcombapQ1LsfPTQnwmguBt3i6HrdR6x0N_Kd6uwcY7bxSSYVHsngo_vWf53uX9g2PVV7F7jXY3uFst_v3H1wXr_XQ-Xss0O8O1K0_K7KnOxqQ57uvvN7D3ftgP86WMcUNpNreNSAuU3_JKeetlyRWW4YhjkS3--A_0tXhf.aS36MA.7PxEAz5SgSK1UW0SSGY8WuB2rJ0"
cookie_source = ".eJydVtuSozgS_ZUNP29NCATY9JsLF1gUiOJutLFRYS7mjl0GX2Bi_n0TV_X09M6-9D7ZCCnz5DmZB_2-eD-cs75YfBvOl-yfi_cyXXxboKWE5ThZcXglZKlwwEISZ0uM90uM0AEny1iWZQnJqcjzK0nCqxXCh2wvJbEoJhwvSMkKrVKZTw_SSkrh5AFzS5SJ6VKUVhkvHjjMZbG8lDiJ5zn5cEglQZIyAaHVKuH3aAFALn12_kTDw2NzTPZNBg9ZB0_H_WUAyL8v_jEsvv1rkY16EWtJaZW660-EoyXpSeeIiUJyq1yXbpP6pLyVe76pSbmWiKLffPVkxG3jhB29Ofh0crAt-Di4Upw22ZbtqPfMhb4-Mcw0u1EvDN19c6dS0qHfIB_sWZdW9YJpZfNm9XIzq7wnbVOkCpFML-HpJhrNTY4s5VZGuwDtVRntQ64h1fFOpwjRitysjY0NRf9ItRqwE8Gc1iPbmBNTkMg0XzQ8-x6FL0NU6Y0JaybPWnPyecuzkVn5JZw9Jdic6z6mW-eWTMergYMicsUu5kUU7fQ64pvGaOVLrDUX5sojC9U-3plXB1HdcYGnVuUYYIbfKuJlLu7sOe6UhuSBiXm0jSra0JKrWWuPgGmkVTQAdo6ViDN5taZTjQFbFU0PTCjbrWdMCuQa2Y7Ma0XWPdamdPfcJB1tUoVDwDKadUlmXapjGfHRjVY1jqZ8oJ59M0uEKE_uhpfzLPQH5tnY2gQlnQBX9dzOZ6OQjvNZ87OWPtZkzEJ7iLF-YnxzSUYihSO5vpZ6Cjg-6w_kIuJp8-Cu68uklXu2g_9NXzItaEGvHvCNMX9vkpHrZg7nXDHw_-DxL-chJheH6uGhsSaP-92pSLXmGkO-gwu1tcEU42CM-OAAWCuoeSLVaUk6yiVaMCZ8gIydA7Hsv2GxQ2fYh0K526H-r_r89z7If4nCtDHCnzQcolAsGO8Pc17AcIGa-n0onoETmA92YrtkSLb6lbVNz1zAO-fp5r3Pc5-W8y_MSE22z8AFO8Wan3_lzVnIFfvwNudpIP8pVmWe7YDztmnmfkq3Oseg_rhVB-ZCf9VOAbF68qIX8K7Y8zL_0H6rN6wFHtqg3uFgghhQy2NOQIuf94K2VRTeP98BL5C72-9YEzfyn2ccTb184Wph7RRvm8MPDD_H-14D9GUdtSpKWvUcY7ZmvHxJNehdjZ6YK1Yxj-Z416RNt1A_l2xn3gfQUL_GWjDrGZOaUz1fV_3PPpv36o-5qnxkbRIuqnJkhBFH597eNK2lIMHSKGjmNNTTW0sLalN7EdjsXe3XPIRORTdpbfLmYGo2gnlDVuhPhleL5kQGOsE8eGvwk1yErpoeHH2v9VfzVifFdXXZ2P7cW54fULsOXNLMPQj-gT6xwXwKdApK8IGBVT6GuIAtEmBWhQh6DvyLM9tIgFm8RV7xmNV9aM9cgy4O1BRh8DnB3LACPAXRjTlELS2ikmvNjc-bG3Izp4hnm3rm_k99fzWvVVPQws8DLSji_1Gf7TvU9WHG5l7Feuc-MBIMGMCP02LmHPJwhue0zKsHy2MVnTFq_hRNETZbtYi8h8edPvV-uTHQxORtzgiJSEG7WUOIA_Gc2vCCypx00NYXo9a_P75VrVjEof__5JVc7lknqt4k4D2p8hzAjCH4RvXwjfryr9n_dOr4nOIE5G91Rq15A9-dohGJwO2cr7Y08IwKeC4RuHrCmSHg3ESYtv6POlvw_4qVlkew4SWjOdkDBe-0FK6kVdEaIS1pqJYUcFKI_-nPP-r8xbySg_VrulvnJmgIfvhben3ug_vlxLbK1C_FTtZ4E39s3Uwv-lUVXMmHqBDfxlkjupm_Vd5WeZd-OLa1e-uPG5keSGQl-Tt5nqqQ09qCLT8OTzyePDmc7i4zKvdtGhXzOpynHB-Z5iRdtuyRI2_e8kFz5fp2PL2qcjVOvXZ_ul7CJW-8kG0e6MjB5ElKK6Pyrp5L1F65Hc3TU7I_vwzHs1YhaiT3-p2sy2KbE6E_WPthdf9oNJ-o9MkYWy_-cDrtPnGnnN3f27fVShe5az2s3oXXdT4OgfrWdc6rpnNm7AqarHSvnkEcombapQ1LsfPTQnwmguBt3i6HrdR6x0N_Kd6uwcY7bxSSYVHsngo_vWf53uX9g2PVV7F7jXY3uFst_v3H1wXr_XQ-Xss0O8O1K0_K7KnOxqQ57uvvN7D3ftgP86WMcUNpNreNSAuU3_JKeetlyRWW4YhjkS3--A_0tXhf.aS36MA.7PxEAz5SgSK1UW0SSGY8WuB2rJ0"
cookie_target = ".eJy9VsmSo0gS_ZUxnafaiAAkUbfUAoIUQbETMTaWxiZBECBlog3a-t_HUVZ1V82c-jIntgj35_78PeL32dvho-yr2ddDKvryn7O3uph9nc0VlGNNQYf5ci4dZJylqSZlGKVYLZC6XBRZuTwo6mEul6WKD0ukLdAyRwgvUglLGBeqrKqpkqeFImtzVUkXaI6VQs6kcqGkKkZZWsCnZXaQs1zCB4QOOJtjGeVzdamq8gyAXPvy4xPN9ChOeSpKeCg7eDql1wtg_n32j8vs679m5WBVmZHXTm354WgiUpu92XlqvjaPTv1S-6IIzfpep1g0Zv0yN9fWPdTP-6wVXtyRuyefz57sKqEc3YhciHLHEhKsUBxaI5OZ4Qr9yqRHaCc6MTvpN8gHa15qh29lwreDEzSKE2x7sxVVsTbndpBjOzBVJ8gftn-vaRJJqa5JaYyEyU8PMtKHzRuVjNvHfm29F0YD2E14d1RZQCrmo5bGFO8Dr2K8uTgb0bC1pDIeSiRgFR31lnGzhr3nXLanuk_Fzrvn4-m2l6OK-mqXYVWiidVQLMS-1a6ZIa7M1wYW632W2DdPIpbnQ59aHTHADFdOsYayzp3ijkVsTpgUwNNSTgSpUcNad9gH7kA4BUwuYrWEbKw3ZGxkGzNOx3DaK5XJy4RpDbkGljxxVmX3fDcWyUrkHRHFGknQZWniJZ944aeaxiHUGFVsQy_EsEfmS5LNdb6PtzLkuxBMWicmjWPold2692kvjckw7bU_a-kzQ5NZ7F4y2TozLK75YM7jwby91lYBOD7rj7SKYiKevev6Om-1niVwL_qaGVELfPWAb8jwQ-QD6qYeTrkyzNpnH3_aDzFRFuuHJ8eGNqTJuSoMccsg3wG4z9tozORooDg6AFYONY8mPy_MjqDciIYcR9I-8SCW-z9Y3Ni7pLFSJ4nU_8zPf6-D_FcaF2If_8LhhcZqxXB4mfIChivU1Kex-gE9AX2wM0vyS76zbqwVPfMB75Snm9aupjmtpytopDF3K-gFO2dGePye98hiVKXxfcojIP850zXMEuh5K8Q0T8XOQgzqz1r9wnyYr8arIFZvbq0KvlUp1vCT-50lWAt9aKMmkaMRYkAtT50AF7-uBW45jR-f36AvkLtLEyYyof25xzP063dcoCF0znbi8BeGX-P9qAHmsqGtLuWt_pHJ7IVh7VoYMLsGOTNf5RmWpni3vC12UD_Kd1PfLwuzVassDiedILI5yiQ2FbJGLQlyBXQCs3wEnVQc9NywIBwYrwTbrCrHoHO3aZ76_a69ho6uzDaE74NVQwyY_40Q9iCBh9iguVwCjd3BV8Bn8sGe-GtBy9KnbkjgKmSM6kkj4BGys5YkJ6aA4ahQ4J8ZIbJbqoAu7jSo2mfff5qfIIyI20S-KZC23_V_cQZ-42xyRPlR2scUkfE44WohvuIYBObNEySwWseIGtvYKoyfN6A7YeqeoLH0U32sAhcdGS8awHQn7RbiuJI9oJpivYbYdxLQu81fRlBI4_j_r_qKmo4rzvjU9wY4DMF3XAX4qoFP8F_WkjF8sGArEZ5jFpw_-V-_PJ7_k9h9zg4Br6a8GcggyTa3JfBtMXFPOWCqEafgaZSDbwdFa4_bH7NkPXvzdzFMvemsW2ZEk49kZoP0ILT0cPKbaNKvB5rVr9N_aPK9v9s7pyGALTxGRlRlvka8EK29aPJwiIUtbhuktbF9cQL4F4E_s00Fc2DCnMDMtlQmgS7swMVkZMJpigF8525utrc_OYC-7ce_PVdr_ycs4Ie_nYfdYly8H6sby4LcMNjrQDz__bZpGp5nCXlNciSDM5YkOodsfzWMgyjjw6LLaYP7q-reXzXHYt7BPw-vo7Zm98qniZdrcTH45GR85PtSKTZBWfSqHHwh8asXHTLPabZM8-MA8RBmuH89EhtrRx_v9vpie48ex2-JtbGX-G3p5fO3eJOKdYoy4Rir9aNZDnCKkW_vaTdKl6AM7Qc6I5ei4MWlX3ho55uFg8d2n70GPGh4WuFT9_5OUsv86K91QXbOcc5R6al10qxedq_v74b01lV74-hf60OZcm-0rFbvltfIdTZSJhdF5nan681ajIfc2jXUypSP_iGCmHps0W2_mV6Mv3nri2j6Wl5rL3C2mv37j-8HrLfzx-lWF-UHHLuOeV1-acohF6e0-XECe-sv6WU6lHV96sqPg_oqrbT56rhOsJ3NU2W9CRdyxGd__AeYDHuI.aR2Wtg.kaGOT5rZY11-hNKLoil06qcEwhg"

COOKIES = {
    "session": cookie,
    "session_source": cookie_source,
    "session_target": cookie_source,
}

def get_access_token():
    token_url = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token"
    payload = {
        "grant_type": "password",
        "scope": "openid",
        "client_id": KEYCLOAK_CLIENT_ID,
        "client_secret": KEYCLOAK_CLIENT_SECRET,
        "email": "dbatrakov@gontardcie.com",
        "username": "dbatrakov",
        "password": "JbqIhxa2yBVa"
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    res = requests.post(token_url, data=payload, headers=headers)
    return res.json()["access_token"], res.json()["refresh_token"]

session_1 = requests.Session()
session_2 = requests.Session()

def setup_session(session, SUPERSET_URL, cookie_key: "session"):
    access_token, _ = get_access_token()
    # Login via browser -> f12 -> Application -> Cookie -> Session
    session_cookie = COOKIES.get(cookie_key)
    session.cookies.set("session", session_cookie)
    me_url = f"{SUPERSET_URL}/api/v1/me/"
    res = session.get(me_url,
                      timeout=5,
                      # allow_redirects=False
                      )
    res.raise_for_status()
    print(f'✅ Авторизован как: {res.json().get('result').get('username')}')

# setup_session(SOURCE_SUPERSET_URL)
# setup_session(TARGET_SUPERSET_URL)
# print("✅ Авторизация через Keycloak выполнена")
# ######################## /SESSION ######################## #

# ######################## GET ######################## #
def get_dashboard(dashboard_id, SUPERSET_URL=SOURCE_SUPERSET_URL, session=session_1):
    url = f"{SUPERSET_URL}/api/v1/dashboard/{dashboard_id}"
    res = session.get(url)
    res.raise_for_status()
    return res.json()["result"]

def get_charts(dashboard_id, SUPERSET_URL=SOURCE_SUPERSET_URL, session=session_1):
    filters = {
        "filters": [
            {"col": "dashboard_id", "opr": "eq", "value": dashboard_id}
        ]
    }
    q_str = quote(json.dumps(filters))
    url = f"{SUPERSET_URL}/api/v1/chart/?q={q_str}"
    res = session.get(url)
    res.raise_for_status()
    return res.json()["result"]

def get_charts_from_layout(layout, SUPERSET_URL=SOURCE_SUPERSET_URL, session=session_1):
    chart_ids = []
    for key, val in layout.items():
        if key.startswith("CHART-") and isinstance(val, dict) and "meta" in val and "chartId" in val["meta"]:
            chart_id = val["meta"]["chartId"]
            if isinstance(chart_id, int):
                chart_ids.append(chart_id)
    charts = []
    for chart_id in chart_ids:
        url = f"{SUPERSET_URL}/api/v1/chart/{chart_id}"
        res = session.get(url)
        res.raise_for_status()
        charts.append(res.json()["result"])
    return charts

def get_dataset(dataset_id, SUPERSET_URL=SOURCE_SUPERSET_URL, session=session_1):
    url = f"{SUPERSET_URL}/api/v1/dataset/{dataset_id}"
    res = session.get(url)
    res.raise_for_status()
    return res.json()["result"]

def get_metrics(base_dataset_id, SUPERSET_URL=SOURCE_SUPERSET_URL, session=session_1):
    # Получаем метрики из старого датасета
    base_url = f"{SUPERSET_URL}/api/v1/dataset/{base_dataset_id}"
    res = session.get(base_url)
    res.raise_for_status()
    base_data = res.json()["result"]
    metrics = base_data["metrics"]
    return metrics
# ######################## /GET ######################## #


# ######################## CREATE ######################## #
def create_dataset(base_dataset, new_table_name, new_scheme_name=NEW_SCHEME_NAME, SUPERSET_URL=TARGET_SUPERSET_URL, session=session_2):
    payload = {
        # TODO: Получение айди базы
        "database": 8, # base_dataset["database"]["id"],
        "schema": new_scheme_name,
        "table_name": new_table_name,
        "sql": base_dataset.get("sql"),
        # "extra": base_dataset.get("extra"),
        "is_managed_externally": False,
        "owners": [base_dataset.get("owners")[0].get("id")],
    }
    url = f"{SUPERSET_URL}/api/v1/dataset/"
    res = session.post(url, json=payload)
    pass
    res.raise_for_status()
    return res.json()["id"]

def create_new_metrics(new_dataset_id, metrics, SUPERSET_URL=TARGET_SUPERSET_URL, session=session_2):
    # Получаем новый датасет
    new_url = f"{SUPERSET_URL}/api/v1/dataset/{new_dataset_id}"
    res = session.get(new_url)
    res.raise_for_status()
    new_data = res.json()["result"]
    allowed_column_fields = {
        "id",
        "advanced_data_type",
        "column_name",
        "description",
        "expression",
        "extra",
        "filterable",
        "groupby",
        "is_active",
        "is_dttm",
        "python_date_format",
        "type",
        "uuid",
        "verbose_name"
    }
    clean_columns = []
    for col in new_data["columns"]:
        clean_col = {k: v for k, v in col.items() if k in allowed_column_fields}
        clean_columns.append(clean_col)
    # Готовим новые метрики
    new_metrics = []
    for metric in metrics:
        if metric.get("metric_name") != 'count':
            new_metrics.append({
                "metric_name": metric["metric_name"],
                "expression": metric["expression"],
                "description": metric.get("description", ""),
                "d3format": metric.get("d3format", ""),
                "verbose_name": metric.get("verbose_name"),
                "warning_text": metric.get("warning_text", ""),
                "extra": metric.get("extra", ""),
            })

    # Собираем payload
    payload = {
        "metrics": new_metrics,
        "columns": clean_columns,
        "description": new_data.get("description", ""),
        "extra": new_data.get("extra", ""),
        "schema": new_data.get("schema", ""),
        "table_name": new_data.get("table_name"),
        "sql": new_data.get("sql", ""),
        "template_params": new_data.get("template_params"),
        "owners": [o["id"] for o in new_data.get("owners", [])],
    }
    # Обновляем датасет
    update_url = f"{SUPERSET_URL}/api/v1/dataset/{new_dataset_id}"
    res = session.put(update_url, json=payload)
    res.raise_for_status()

def create_dashboard(title, SUPERSET_URL=TARGET_SUPERSET_URL, session=session_2):
    payload = {
        "dashboard_title": title,
        "published": True
    }
    url = f"{SUPERSET_URL}/api/v1/dashboard/"
    res = session.post(url, json=payload)
    res.raise_for_status()
    return res.json()["id"]

def clone_charts(charts, new_dataset_id, new_dashboard_id, SUPERSET_URL=TARGET_SUPERSET_URL, session=session_2):
    new_chart_ids = []
    id_mapping = {}
    for chart in charts:
        chart_id = chart["id"]
        new_chart = copy.deepcopy(chart)
        # Удаляем поля, которые нельзя отправлять
        for field in [
            "id", "changed_on", "changed_on_utc", "changed_by_name", "changed_by_url",
            "thumbnail_url", "url", "dashboards", "query_context", "changed_on_delta_humanized",
            "datasource_name_text", "viz_type_translation", "viz_type_description", "result_format",
            "result_type", "cache_timeout", "last_saved_at", "last_saved_by", "tags"
        ]:
            new_chart.pop(field, None)
        # Привязка к новому датасету
        new_chart["datasource_id"] = new_dataset_id
        new_chart["datasource_type"] = "table"

        query_context = chart.get("query_context")
        if not query_context or query_context in ("null", "None"):
            query_context = {}

        # fix datasource in query_context
        if isinstance(query_context, str):
            while isinstance(query_context, str):
                try:
                    query_context = json.loads(query_context)
                except json.JSONDecodeError:
                    query_context = {}

        try:
            query_context['datasource'] = {'id': new_dataset_id, 'type': 'table'}
            # form_data = query_context["form_data"]
            form_data = query_context.get("form_data", {})

            if isinstance(form_data, str):
                while isinstance(form_data, str):
                    try:
                        form_data = json.loads(form_data)
                    except json.JSONDecodeError:
                        form_data = {}
            form_data['datasource'] = f'{new_dataset_id}__table'
            # form_data['datasource'] = {'id': new_dataset_id, 'type': 'table'} # !!!
            form_data['dashboards'] = [new_dashboard_id]
            query_context["form_data"] = form_data
        except:
            print(f'Chart {chart_id} has incorrect query_context data')

        if "queries" not in query_context or not query_context["queries"]:
            query_context["queries"] = [{
                "filters": [],
                "extras": {},
                "columns": [],
                "metrics": [],
            }]

        new_chart["query_context"] = json.dumps(query_context)
        # Owners → список ID
        if "owners" in new_chart:
            new_chart["owners"] = [o["id"] for o in new_chart["owners"] if "id" in o]
        # Params → строка JSON
        params = new_chart.get("params")
        if not params or params in ("null", "None"):
            params = {}
        if isinstance(params, str):
            while isinstance(params, str):
                try:
                    params = json.loads(params)
                except json.JSONDecodeError:
                    params = {}
        # params["datasource"] = f'{new_dataset_id}__table'  # !!!
        params["datasource"] = {'id': new_dataset_id, 'type': 'table'}
        params["dashboards"] = [new_dashboard_id]
        new_chart["params"] = json.dumps(params)

        new_chart["query_context_generation"] = True
        # Создание чарта
        chart_url = f"{SUPERSET_URL}/api/v1/chart/"
        cres = session.post(chart_url, json=new_chart)
        try:
            cres.raise_for_status()
            new_id = cres.json()["id"]
            new_chart_ids.append(new_id)
            id_mapping[chart_id] = new_id
        except:
            pass
            print(f'Chart {chart_id} has incorrect query_context data')
            print(chart_url)
            print(new_chart)

    return new_chart_ids, id_mapping
# ######################## /CREATE ######################## #

# ######################## DUPLICATE ######################## #
def duplicate_dashboard_with_charts_and_layout(original_dashboard_id,
                                               new_dashboard_id,
                                               chart_id_map,
                                               new_dataset_id,
                                               SOURCE_SUPERSET_URL=SOURCE_SUPERSET_URL,
                                               TARGET_SUPERSET_URL=TARGET_SUPERSET_URL,
                                               session_1=session_1,
                                               session_2=session_2):
    """
    Копирует layout дашборда, обновляет chartId в layout, сохраняет новый layout
    и обновляет каждый график, привязывая его к новому дашборду.
    """
    # 1. Получаем оригинальный layout
    res = session_1.get(f"{SOURCE_SUPERSET_URL}/api/v1/dashboard/{original_dashboard_id}")
    res.raise_for_status()
    orig_dashboard = res.json()["result"]
    orig_position_data = orig_dashboard["position_json"]
    if isinstance(orig_position_data, str):
        orig_position_data = json.loads(orig_position_data)

    # 2. Копируем и обновляем layout
    new_position_data = copy.deepcopy(orig_position_data)

    full_chart_id_map = {}
    for component_id, component in orig_position_data.items():
        if not isinstance(component, dict):
            continue
        if component.get("type") == "CHART":
            chart_id = component["meta"].get("chartId")
            if chart_id in chart_id_map:
                new_chart_id = chart_id_map[chart_id]
                new_component_id = f"CHART-{new_chart_id}"
                full_chart_id_map[component_id] = new_component_id
                component["meta"]["chartId"] = new_chart_id
                component["id"] = new_component_id
                new_position_data.pop(component_id)
                new_position_data[new_component_id] = component
                # Можно также обновить sliceName и uuid при необходимости
        elif component.get("type") in ["ROW", "COLUMN", "TABS"]:
            new_children = []
            for child in component["children"]:
                if child in full_chart_id_map:
                    new_chart_id = full_chart_id_map[child] #  chart_id_map[child]
                    new_children.append(new_chart_id)
                else:
                    new_children.append(child)
            new_position_data[component_id]['children'] = new_children

    # Обновляем metadata (переносим фильтры)
    orig_metadata = orig_dashboard["json_metadata"]
    if isinstance(orig_metadata, str):
        while isinstance(orig_metadata, str):
            orig_metadata = json.loads(orig_metadata)
    # Обновляем json_metadata (переносим native_filter_configuration)
    filters = orig_metadata.get("native_filter_configuration", [])
    for i in range(len(filters)):
        filter_config = filters[i]
        targets = filter_config.get("targets", [])
        if targets:
            for ii in range(len(targets)):
                target = targets[ii]
                try:
                    target["datasetId"] = int(new_dataset_id)  # Обновляем на новый datasetId
                    filters[i]["targets"][ii]["datasetId"] = int(new_dataset_id)
                except:
                    pass
    orig_metadata["native_filter_configuration"] = filters

    # 3. Обновляем дашборд с новым layout
    payload = {
        "position_json": json.dumps(new_position_data),
        "json_metadata": json.dumps(orig_metadata),
        # "css": orig_dashboard["css"],
    }
    update_url = f"{TARGET_SUPERSET_URL}/api/v1/dashboard/{new_dashboard_id}"
    update_res = session_2.put(update_url, json=payload)
    try:
        update_res.raise_for_status()
        print(f"✅ Dashboard {new_dashboard_id} layout updated.")
    except requests.exceptions.HTTPError:
        print(f"❌ Dashboard update error: {update_res.text}")
        return

    # 4. Обновляем каждый график: добавляем его к дашборду
    for old_id, new_id in chart_id_map.items():
        chart_url = f"{TARGET_SUPERSET_URL}/api/v1/chart/{new_id}"
        chart_res = session_2.get(chart_url)
        chart_res.raise_for_status()
        chart_data = chart_res.json()["result"]
        dashboards = chart_data.get("dashboards", [])
        if new_dashboard_id not in dashboards:
            dashboards.append(new_dashboard_id)
        payload = {
            "dashboards": dashboards
        }
        put_res = session_2.put(chart_url, json=payload)
        try:
            put_res.raise_for_status()
            print(f"✅ Chart {new_id} linked to dashboard {new_dashboard_id}.")
        except requests.exceptions.HTTPError:
            print(f"❌ Chart {new_id} update error: {put_res.text}")
# ######################## /DUPLICATE ######################## #




def main():
    setup_session(session_1, SOURCE_SUPERSET_URL, 'session_source')
    setup_session(session_2, TARGET_SUPERSET_URL, 'session_target')
    print("✅ Авторизация через Keycloak выполнена")
    dashboard = get_dashboard(SOURCE_DASHBOARD_ID)
    layout = json.loads(dashboard["position_json"])
    charts = get_charts_from_layout(layout)
    print(f"🔍 Найдено чартов: {len(charts)}")

    try:
        query_context_dict = json.loads(charts[0]["query_context"])
    except Exception:
        print(charts[0]["id"])

    # TODO: What if datasource count more then one?

    source_dataset_id = query_context_dict["datasource"]["id"]
    dataset = get_dataset(source_dataset_id)
    print(f"📦 Оригинальный датасет: {dataset['table_name']}")

    if NEW_TABLE_NAME is not None and NEW_SCHEME_NAME is not None:
        new_dataset_id = create_dataset(base_dataset=dataset, new_scheme_name=NEW_SCHEME_NAME, new_table_name=NEW_TABLE_NAME)
    else:
        new_dataset_id = create_dataset(base_dataset=dataset, new_scheme_name=dataset['schema'], new_table_name=dataset['table_name'])
    print(f"🆕 Новый датасет создан: ID {new_dataset_id}")

    old_metrics = get_metrics(source_dataset_id)

    create_new_metrics(new_dataset_id, old_metrics)
    print("📐 Метрики скопированы")

    new_dashboard_id = create_dashboard(NEW_DASHBOARD_TITLE)

    new_chart_ids, id_mapping = clone_charts(charts, new_dataset_id, new_dashboard_id)
    print("📊 Чарты клонированы")

    duplicate_dashboard_with_charts_and_layout(original_dashboard_id=SOURCE_DASHBOARD_ID,
                                               new_dashboard_id=new_dashboard_id,
                                               chart_id_map=id_mapping,
                                               new_dataset_id=new_dataset_id)
    print(f"🎉 Новый дашборд создан! ID: {new_dashboard_id}")




if __name__ == "__main__":
    main()
