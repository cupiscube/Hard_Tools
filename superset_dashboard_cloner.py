import requests
import json
import copy
import os
import typer
from pycparser.ply.cpp import tokens

app = typer.Typer()

SUPERSET_URL = "superset_url"  # или твой адрес

KEYCLOAK_URL = 'kc_url'
KEYCLOAK_REALM = 'kc_realm'
KEYCLOAK_CLIENT_ID = 'kc_cl_id'
KEYCLOAK_CLIENT_SECRET = 'kc_cl_secret'

def get_access_token():
    token_url = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token"
    payload = {
        "grant_type": "password",
        "scope": "openid",
        "client_id": KEYCLOAK_CLIENT_ID,
        "client_secret": KEYCLOAK_CLIENT_SECRET,
        "email": "email",
        "username": "user",
        "password": "password"
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    res = requests.post(token_url, data=payload, headers=headers)
    res.raise_for_status()
    return res.json()["access_token"], res.json()["refresh_token"]

session = requests.Session()

SOURCE_DASHBOARD_ID = 27
NEW_TABLE_NAME = "demo_superset_labavatar"
NEW_DASHBOARD_TITLE = "Labavatar [DEMO]"

def setup_session():
    access_token, _ = get_access_token()

    # Login via browser -> f12 -> Application -> Cookie -> Session
    session_cookie = input('Pls, enter here your session cookie (Login via browser -> f12 -> Application -> Cookie -> Session): ')
    session.cookies.set("session", session_cookie)

    # Теперь session содержит куку
    me_url = f"{SUPERSET_URL}/api/v1/me/"
    res = session.get(me_url)
    res.raise_for_status()
    print(f'✅ Авторизован как: {res.json().get('result').get('username')}')

def get_dashboard(dashboard_id):
    url = f"{SUPERSET_URL}/api/v1/dashboard/{dashboard_id}"

    res = session.get(url)
    res.raise_for_status()
    return res.json()["result"]

from urllib.parse import quote

def get_charts(dashboard_id):
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

def get_charts_from_layout(layout):
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


def get_dataset(dataset_id):
    url = f"{SUPERSET_URL}/api/v1/dataset/{dataset_id}"
    res = session.get(url)
    res.raise_for_status()
    return res.json()["result"]

def create_dataset(base_dataset, new_table_name):
    payload = {
        "database": base_dataset["database"]["id"],
        "schema": base_dataset["schema"],
        "table_name": new_table_name,
        "sql": base_dataset.get("sql"),
        # "extra": base_dataset.get("extra"),
        "is_managed_externally": False,
        "owners": [base_dataset.get("owners")[0].get("id")],
    }
    url = f"{SUPERSET_URL}/api/v1/dataset/"
    res = session.post(url, json=payload)
    print(res.json())
    res.raise_for_status()
    return res.json()["id"]

def copy_metrics(base_dataset_id, new_dataset_id):
    # Получаем метрики из старого датасета
    base_url = f"{SUPERSET_URL}/api/v1/dataset/{base_dataset_id}"
    res = session.get(base_url)
    res.raise_for_status()
    base_data = res.json()["result"]
    metrics = base_data["metrics"]

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

def clone_charts(charts, new_dataset_id):
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

        # Owners → список ID
        if "owners" in new_chart:
            new_chart["owners"] = [o["id"] for o in new_chart["owners"] if "id" in o]

        # Params → строка JSON
        if isinstance(new_chart.get("params"), dict):
            new_chart["params"] = json.dumps(new_chart["params"])
        elif isinstance(new_chart.get("params"), str):
            try:
                json.loads(new_chart["params"])
            except json.JSONDecodeError:
                new_chart["params"] = json.dumps({})

        # Создание чарта
        chart_url = f"{SUPERSET_URL}/api/v1/chart/"
        cres = session.post(chart_url, json=new_chart)
        cres.raise_for_status()

        new_id = cres.json()["id"]
        new_chart_ids.append(new_id)
        id_mapping[chart_id] = new_id

    return new_chart_ids, id_mapping

def create_dashboard(title):
    payload = {
        "dashboard_title": title,
        "published": True
    }
    url = f"{SUPERSET_URL}/api/v1/dashboard/"
    res = session.post(url, json=payload)
    res.raise_for_status()
    return res.json()["id"]

def duplicate_dashboard_with_charts_and_layout(original_dashboard_id, new_dashboard_id, chart_id_map, new_dataset_id):
    """
    Копирует layout дашборда, обновляет chartId в layout, сохраняет новый layout
    и обновляет каждый график, привязывая его к новому дашборду.
    """
    # 1. Получаем оригинальный layout
    res = session.get(f"{SUPERSET_URL}/api/v1/dashboard/{original_dashboard_id}")
    res.raise_for_status()
    orig_dashboard = res.json()["result"]
    orig_position_data = orig_dashboard["position_json"]
    if isinstance(orig_position_data, str):
        orig_position_data = json.loads(orig_position_data)

    # 2. Копируем и обновляем layout
    new_position_data = copy.deepcopy(orig_position_data)

    for component_id, component in new_position_data.items():
        if not isinstance(component, dict):
            continue
        if component.get("type") == "CHART":
            chart_id = component["meta"].get("chartId")
            if chart_id in chart_id_map:
                new_chart_id = chart_id_map[chart_id]
                component["meta"]["chartId"] = new_chart_id
                component["id"] = f"CHART-{new_chart_id}"
                # Можно также обновить sliceName и uuid при необходимости

    # Обновляем metadata (переносим фильтры)
    old_json_metadata_str = orig_dashboard.get("json_metadata") or "{}"
    old_json_metadata = json.loads(old_json_metadata_str)
    # Обновляем json_metadata (переносим native_filter_configuration)
    new_json_metadata = copy.deepcopy(old_json_metadata)
    filters = new_json_metadata.get("native_filter_configuration", [])
    for filter_config in filters:
        targets = filter_config.get("targets", [])
        for target in targets:
            target["datasetId"] = new_dataset_id  # Обновляем на новый datasetId
    new_json_metadata["native_filter_configuration"] = filters

    # 3. Обновляем дашборд с новым layout
    payload = {
        "position_json": json.dumps(new_position_data),
        "json_metadata": json.dumps(new_json_metadata),
        # "css": orig_dashboard["css"],
    }
    update_url = f"{SUPERSET_URL}/api/v1/dashboard/{new_dashboard_id}"
    update_res = session.put(update_url, json=payload)
    try:
        update_res.raise_for_status()
        print(f"✅ Dashboard {new_dashboard_id} layout updated.")
    except requests.exceptions.HTTPError:
        print(f"❌ Dashboard update error: {update_res.text}")
        return

    # 4. Обновляем каждый график: добавляем его к дашборду
    for old_id, new_id in chart_id_map.items():
        chart_url = f"{SUPERSET_URL}/api/v1/chart/{new_id}"
        chart_res = session.get(chart_url)
        chart_res.raise_for_status()
        chart_data = chart_res.json()["result"]

        dashboards = chart_data.get("dashboards", [])
        if new_dashboard_id not in dashboards:
            dashboards.append(new_dashboard_id)
        payload = {
            "dashboards": dashboards
        }
        put_res = session.put(chart_url, json=payload)
        try:
            put_res.raise_for_status()
            print(f"✅ Chart {new_id} linked to dashboard {new_dashboard_id}.")
        except requests.exceptions.HTTPError:
            print(f"❌ Chart {new_id} update error: {put_res.text}")


def main():
    """
    Клонирует дашборд Superset с новым датасетом и чартаами.
    """
    verbose = True
    source_dashboard_id = 27
    new_table_name = "demo_superset_labavatar"
    new_dashboard_title = "Labavatar [DEMO]"
    setup_session()
    if verbose:
        typer.echo("✅ Авторизация через Keycloak выполнена")
    dashboard = get_dashboard(source_dashboard_id)
    layout = json.loads(dashboard["position_json"])
    charts = get_charts_from_layout(layout)
    if verbose:
        typer.echo(f"🔍 Найдено чартов: {len(charts)}")

    charts = get_charts_from_layout(layout)
    print(f"🔍 Найдено чартов: {len(charts)}")

    query_context_dict = json.loads(charts[0]["query_context"])
    source_dataset_id = query_context_dict["datasource"]["id"]

    dataset = get_dataset(source_dataset_id)
    if verbose:
        typer.echo(f"📦 Оригинальный датасет: {dataset['table_name']}")

    new_dataset_id = create_dataset(dataset, new_table_name)

    if verbose:
        typer.echo(f"🆕 Новый датасет создан: ID {new_dataset_id}")

    copy_metrics(source_dataset_id, new_dataset_id)
    if verbose:
        typer.echo("📐 Метрики скопированы")

    new_chart_ids, id_mapping = clone_charts(charts, new_dataset_id)
    if verbose:
        typer.echo("📊 Чарты клонированы")

    new_dashboard_id = create_dashboard(new_dashboard_title)
    duplicate_dashboard_with_charts_and_layout(original_dashboard_id=source_dashboard_id,
                                               new_dashboard_id=new_dashboard_id,
                                               chart_id_map=id_mapping,
                                               new_dataset_id=new_dataset_id)
    typer.echo(f"🎉 Новый дашборд создан! ID: {new_dashboard_id}")

if __name__ == "__main__":
    # app()
    main()
