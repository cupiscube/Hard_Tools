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

TARGET_SUPERSET_URL = "http://10.100.100.50:8088"  # Без /superset в конце
# TARGET_SUPERSET_URL = "https://dss.gontardcie.online"
# TARGET_SUPERSET_URL = "http://159.100.244.234:8088"
# TARGET_SUPERSET_URL = "https://dss.gontardcie.online"

SOURCE_DASHBOARD_ID = 92
NEW_TABLE_NAME = "labflow_superset_labavatar" # None # "demo_superset_labavatar_TEST"
NEW_SCHEME_NAME = "simulation" # None #"demo_0"
NEW_DASHBOARD_TITLE = "LabFlow LA (Simulation)"


# ######################## SESSION ######################## #
# Login via browser -> f12 -> Application -> Cookie -> Session
cookie = ".eJy9VsmSo0gS_ZUxnSfbggAkUTdtIEgRJGKNaBtLY5NYAqQUaIG2_vdxlFXdWdOnusyJLcL9-Xv-nPhj8n64ZG0--dZdrtm_J-9FOvk2mckpUuTpbCbP54dEFBUkzqQERQd8ULK5hOJMSNB0Ks0TCc-UBM9maTafijJWEjESszgSxCxSJJyISoazeSLMUllOY3keJXieHOYCVuYxFoXZXMqm0TTD4jySkCTLMznD0ySbAJBrm10-0WB45Kck4hk8ZA08naJrB5D_mPyrm3z7fZL1Rh5rSWEVhuMNukAKvdWbvZys9KNVLAqHp55e3IsI80ovFlN9Zdw99byLa74PGnLfi-fzXrQlT_RvREx5tmUhcZdC4BkDE5lmc_XK0MMzQ5XoDfoN8sGaRWGVG5G43p0MtLfWkLPmebrSp6abCMRdiKTc3E3IS0MfRaqCokDgenl6kMETzHWCTXfx2K2Mj1SrRuy5ORyRGXgP5iCZYlvYufYAcTtrrRbmCg2spg9W64i6G0yxWcDecyKa495Tut3fk-F024l-Th25ibGMaGhUFHO-q5VrrPErc5SeBWobh-Ztj4ixd0bMqsAAM1xLihUhbuwx7pAGOsTVJeaSmpaEk0KoWG33gKknJQVMtsAKJJhYrchQiSZmJR28cS_KwsWIaQW5ehbq47s8a57vhjRc8qQhPF0JCFhGoy7JqEt5Kswyr5lmcBPrnRnsa1IgRPEG7dyjTIekY2sqk4AiOmwelqYL414akP6597OWNtYUkQV2F4vGmWF-TXp9GvT67bUwUsDxWb-v5BQT_uSuaYukVloWwj1vC6b5NejVAr4-xg-e9EIzcjjmijGrnzx-2Q8xhThQD0-NNaWPwnOeavwWQ76DA7XV_hCLfk-xfwCsJdQ86OV5pjdESDS_T7CPduEeYtn_wGIH-y4KpCIMUftVn_9dB_mvNEj5LvhJw44Gcs6w1415AcMVamqjQL4AJ-APdmZh0iVb48Zq3jIH8I55mnHtcuzTYryCRyp9uwQu2DnWvCMLhDwK7mN8DnnPsapgFgLXNedjH6VbQ2BQd1yrHXOgr6p9DjFafWPk8C2PsIKfmm8Nzmqov_arUPQHiAE1PP0BGvy8FjQtafD4_AZ8QO4mChmPufLXnr2mXr_jquHdOd7yw98Yfo73owbox4rWKkpq9RKLbMGwck016FmNnJkjlzFGY7xbUqdb4FtItiPf3Uyv5TwOvNEfAlkfRRLoElkJNXETCfwhs_II_shL5oBnXK9nZc7ZeplbGp3aVfX07XfPVXSwRbYm5c5dVkSjHVlzbvZItlwTvJYg8NYd5olkuUlvjrrV4GH06Rfi2hIZ_AK82LHSE60VQlZAAcNRoqA702DO1FQCP9ypm9dP3r_0jev5xK58R-eCstu2f2tWeshaJwItj2gXUIEMxxFXDfElSyPQZ3tOXKO2NL8ytY3EyvMa_MZ1dc9pgL7Ux3KYngMr0wow3Um9gTg2MnuhoFgtIPaduPRulosBnFFZzv-rvrSgw7Jk5ch7BRp6HdFsCfQqQE-8c1kNM_rB3A0iZYKZe_7Uf7V4PP8jgf3sHZhFmJZVT3okmqUJc2rPR-1pCZgKoaQlzOKS5dRNa3PY_Ogl48nNr2IYuWmMW6z54_yI9UpQXc9QvXHO-KNv9-BV9Tr-f8Z596vcWRUBbN7R1_w8dhSy94TV3h9nN8TCRmlqpDax2Vmuh4iDEFvn0Ac69An0bE3hP6hy07UxGRi3qrSHeXPX15vbXxoAb7vhl_tq5XzBAnPwt-W6cT1FdwUsBG0e7-CosoqFzH2nlimo5apbN8p8e1rswvRtYxnL0l6trNvWLPnLpQvRzCqrj1fLC64w341UteIH3ry6Fz4dYtnq1JsoDTMa6Leh3_j12soM5S23LEd5OG8fCc1ux9JKpx1Tp9vrNro3VMzq3Ut0U27vyrpgwlkanM4MV-1xGeRvRnUhsgU5X-7Bcd33nJg0mHmIkaucn82loLzpiqo7xTU7v784nn417lPztTCXlfNCpZs96yJjNl2LZ2Yp2dsjfFSOoRyYHZBGu4jvb6vVKVor_TGq5f5D-VjWp1t1WmE77T40sX0EvWhe-lO_NDPz9YPt9XmoldIj1OZ1f8SkIUaLP-ZRYcOZavKfP78frN7Pl9OtSLMLHLeOSZG9VFmf8FNU_Th5vbdd1I2HMbfzCGsSEPc23_pN-7gr2dZUN624w6k2-fO__fF15A.aJxWBg.6j1K4xoeeUCGl5y6J1Xj7IxDunY"

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
def create_dataset(base_dataset, new_table_name, new_scheme_name=NEW_SCHEME_NAME, SUPERSET_URL=TARGET_SUPERSET_URL, session=session_2):
    payload = {
        "database": base_dataset["database"]["id"],
        "schema": new_scheme_name,
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
