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

from .utils.session import setup_session
from .utils.dashboard import get_dashboard, create_dashboard, duplicate_dashboard_with_charts_and_layout
from .utils.chart import get_charts_from_layout, clone_charts
from .utils.dataset import get_dataset, create_dataset, create_new_metrics, get_metrics


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


session_1 = requests.Session()
session_2 = requests.Session()




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
