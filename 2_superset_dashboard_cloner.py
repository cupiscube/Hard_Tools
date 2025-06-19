from idlelib import query
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

# SOURCE_SUPERSET_URL = "http://10.100.100.50:8088"  # Без /superset в конце
# SOURCE_SUPERSET_URL = "https://dss.gontardcie.online"
# SOURCE_SUPERSET_URL = "http://159.100.244.234:8088"
SOURCE_SUPERSET_URL = "https://dss.gontardcie.online"

# TARGET_SUPERSET_URL = "http://10.100.100.50:8088"  # Без /superset в конце
# TARGET_SUPERSET_URL = "https://dss.gontardcie.online"
# TARGET_SUPERSET_URL = "http://159.100.244.234:8088"
TARGET_SUPERSET_URL = "https://dss.gontardcie.online"

SOURCE_DASHBOARD_ID = 12
NEW_TABLE_NAME = "demo_superset_labavatar_TEST"
NEW_SCHEME_NAME = "demo_0"
NEW_DASHBOARD_TITLE = "Labavatar [DEMO] [TEST] 2"


# ######################## SESSION ######################## #
# Login via browser -> f12 -> Application -> Cookie -> Session
cookie = ".eJyNVl2TokoS_SsbPm9PFwWozJutgtBSDAoCtbHRwZfyUYW0gAg39r9vYs-9O7P7sg8GUlZlnnMy81h_zD7Ot7TJZt_bW5f-ffaRJ7PvMyFcpotYTMKzIsXnMJFCaXEWwlhR4IMSRTovwzgVJSxE54WIQzldyFG8OMtpLEbzNJ7HKJyn53kYL6VUVmQpXcrpMhIkHCtwKF2k8lxaomSJ5URQsCgKcSQnYQpZowghYQZAuia9_UQDr-wahyyFl7SCt2vYtQD5j9nf2tn3f8zSwcgiLc6t3Di6oy6QXG_06iDHa_1i5av8yBJXz_s8xKzU89VcXxu9q9b7iLODV5H-INb1QbQlVzzdiZiwdEd94rwJnmuMVKSazdSOoodr-irRK_QN8sGeVW4VW5E4qwdxYtEszEbnLEvW-tx0YsHcbAUyusgc-jzwTyhUFRR6AtOL6wPWe9NxseWshv3a-Ey0ErDrozmusDkmGRlQTz1z2DuHzBzN1vK2KIA1Upg9Gbc4GI0ycOwcztaQeeJ9TXaHPh6v9714yoKjXEVYRoEP-zBje650kcY6elQG6qlN5Jv3AyLG4Qg6cVWggBmeRYAVIaqeccfE0ydMEnUIDwrCSC6UlNuAyR5IEbTWxhZojgQTqyUZS9HEtAhGdzqLUn81YVpDroH6-rSWpdVzbUz8NxZXhCVrAYHKaKpLPNWluOaWR3NzdCUTu63lGMADIbo5lXvngsl4aQk2JcoDTACPyWk5nQ08MkxnzfWTSxNpikg9u41Eo6aYdfGgz71Bv7_nRgI4vviflAyisKd2VZPHXGmoD99Zk1PtxKFeDeAbIvxg8SBUk4ZTrghT_tTxl_MQU4g89fyssaYMoV9nicbuEeQ7H4EbP42ReBoCfDoD1gI4j3pRL_SKCLF2GmJ8Qnv_ALHs_8Fie4c29KTc91Hza33-ex_k7wIvYXvvtxq2gSdnFLSc8gKGDjg1oSffQBOYD1pTP27jnXGnnDX0CHinPNW0923q03x6woyU-u4NtKB1pLkX6glZ6PVTfAZ560hVMPVBa87Y1EfJzhAo8I642tIj9FV5yCBGo2-NDH7LQqzgZ813BqMc-PNT6YunEWIAh-d8QA1-3ws1LQLv8fUb6AG5q9CnLGLKX2cOmtr9xMVhrY527PwfDL_H-5MD9GMZcBXFXL1FIl1RrHSJBj2rkZoe5SLCaIp3j3myA72FeDfp3S50DnOEvnqWOLZExlMO89DSwhWtNUKWF0jQs1IA2lPNFUweSNCTfeBk_Mn9l9o57onY5emos6nGchZ57jR3AtlcROLpElkLHPwF4tkyLS4wd1lBjzCLjjvQImN085ZZWjC3MWA6vrnQ3-3T6zx74gdaHEoTByJdI8nc0AziILIx24CTLMgFbm5cbG703hwDTDdlfj4-fueHjcLUCDcx-JDjIvKcyQx6TUfWJmjBHcADVWY6NswoZf8nPzHgZh-Ak4GvyaChAF5XWhr0agF65gjcBDzUcx9kA_G5Oz-Ixj3xVxfz6Vlf2MAbOOG6bBZxC1M1EtCeTtp7OgZN2gDrQgDfA28r0sJ86JUweQDsARzTHAG-PXi0tYmFoLigvRcIT5_ZMA51lCyNAM8DI47BLe1UmtpWokW9AW9hunpggYfuf_ED3vsxyYPxraAFKfZOCTV0W6LZEtQrh3rivUM5eP-DOltEihhTp_7qq_XqsUeC6riG6k6-YX_j_N6v6of1qNjt0SzFE--vkSHvmuGUOGipVG-6BH81-u0tf6HMkxFBPOuMft9KI06t1Q_50lw__KZ2xcU7KuB4_tn2ZF9o_POef8h-uf60zc9xx7G8WLbXQ1Mg13vhH4_M8ZZJf9-Ea_WC2IFZVEz2ZTfmy63AP9rMAELh427MRaQv6Ht8He1FFyf7OEqJ6Hu28xKFc6Urg4fqdMEhRjmNH2u2moe3aoNj3x0_YSRT9GMe7JONes7V5vx-vfSNWF-VneL495ubow5f5l132d5P_WMtLX8IH4Vv48KX9TyhP3qxCu808KudrlTrrWndm_DevwsxzpRdrlxMQ-sCd1hGlu2fB0ftttfDy31xgavD7J__-nl_-Khv13uepDe4VVziPH0p0yFm17D884Lx0bRhO905zl6_ui5boyqsqHY10kcMO0aqpqtBURhsr8NL-pHlTXu9DdOFJGvb-vvra9I03y7Xqg1vCcT_dq1YXqWv08WmeWWw-xXA_BveljNW.aFFI5w.CcPMA-5RmUjZ34gbozV5LGPNrcQ"

COOKIES = {
    "session": cookie
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

def setup_session(session, SUPERSET_URL):
    access_token, _ = get_access_token()
    # Login via browser -> f12 -> Application -> Cookie -> Session
    session_cookie = COOKIES.get('session')
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
def create_dataset(base_dataset, new_table_name, SUPERSET_URL=TARGET_SUPERSET_URL, session=session_2):
    payload = {
        "database": base_dataset["database"]["id"],
        "schema": NEW_SCHEME_NAME, # base_dataset["schema"],
        "table_name": new_table_name,
        "sql": base_dataset.get("sql"),
        # "extra": base_dataset.get("extra"),
        "is_managed_externally": False,
        "owners": [base_dataset.get("owners")[0].get("id")],
    }
    url = f"{SUPERSET_URL}/api/v1/dataset/"
    res = session.post(url, json=payload)
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
        cres.raise_for_status()
        new_id = cres.json()["id"]
        new_chart_ids.append(new_id)
        id_mapping[chart_id] = new_id
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
    setup_session(session_1, SOURCE_SUPERSET_URL)
    setup_session(session_2, TARGET_SUPERSET_URL)
    print("✅ Авторизация через Keycloak выполнена")
    dashboard = get_dashboard(SOURCE_DASHBOARD_ID)
    layout = json.loads(dashboard["position_json"])
    charts = get_charts_from_layout(layout)
    print(f"🔍 Найдено чартов: {len(charts)}")

    try:
        query_context_dict = json.loads(charts[0]["query_context"])
    except Exception:
        print(charts[0]["id"])

    source_dataset_id = query_context_dict["datasource"]["id"]
    dataset = get_dataset(source_dataset_id)
    print(f"📦 Оригинальный датасет: {dataset['table_name']}")

    new_dataset_id = create_dataset(dataset, NEW_TABLE_NAME)
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
