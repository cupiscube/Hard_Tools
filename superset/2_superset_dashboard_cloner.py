# from idlelib import query
from urllib.parse import quote

import requests
import json
from urllib.parse import urljoin
import ast
import copy
import os
import typer

# from pycparser.ply.cpp import tokens

from utils.session import setup_session
from utils.dashboard import get_dashboard, create_dashboard, duplicate_dashboard_with_charts_and_layout
from utils.chart import get_charts_from_layout, clone_charts
from utils.dataset import get_dataset, create_dataset, create_new_metrics, get_metrics


from utils.config import KEYCLOAK_URL, KEYCLOAK_REALM, KEYCLOAK_CLIENT_ID, KEYCLOAK_CLIENT_SECRET, COOKIES


# SOURCE_SUPERSET_URL = "http://10.100.100.50:8088"  # Без /superset в конце
# SOURCE_SUPERSET_URL = "https://dss.gontardcie.online"
# SOURCE_SUPERSET_URL = "http://159.100.244.234:8088"
# SOURCE_SUPERSET_URL = "https://dss.gontardcie.online"
SOURCE_SUPERSET_URL = "http://172.16.82.66:8088"

# TARGET_SUPERSET_URL = "http://10.100.100.50:8088"  # Без /superset в конце
# TARGET_SUPERSET_URL = "https://dss.gontardcie.online"
# TARGET_SUPERSET_URL = "http://159.100.244.234:8088"
# TARGET_SUPERSET_URL = "https://dss.gontardcie.online"
TARGET_SUPERSET_URL = "http://172.16.82.66:8088"

SOURCE_DASHBOARD_ID = 7
NEW_TABLE_NAME = "labflow_superset_labavatar" # None # "demo_superset_labavatar_TEST"
NEW_SCHEME_NAME = "simulation" # None #"demo_0"
NEW_DASHBOARD_TITLE = "Lab Data v2.2"


session_1 = requests.Session()
session_2 = requests.Session()

new_db_id = 10
admin_user_id = 2 # BADA

# old scheme.table_name : new scheme.table_name
dataset_map = {
        'reports.check_guc_not_matched_reagents': 'reports.check_guc_not_matched_reagents_v2',
        'reports.check_local_catalog_v': 'reports.check_local_catalog_v_v2',
        'reports.all_reagents_guc_report': 'reports.all_reagents_guc_report_v2',
        'reports.category_analyzer_test_reagent': 'reports.category_analyzer_test_reagent_v2',
        'reports.check_guc_reagents': 'reports.check_guc_reagents_v2',
        'reports.check_guc_biomaterials': 'reports.check_guc_biomaterials_v2',
        'reports.check_guc_analyzers': 'reports.check_guc_analyzers_v2',
        'reports.check_global_catalog_v': 'reports.check_global_catalog_v_v2',
        'reports.check_local_analyzers_v': 'reports.check_local_analyzers_v_v2',
        'reports.guc_check_analyzer_category': 'reports.guc_check_analyzer_category_v2',
        'reports.lab_data_checker': 'reports.lab_data_checker',
}


def find_dataset(session,
                 SUPERSET_URL: str,
                 scheme: str,
                 table: str,
                 db_id: int
                 ):
    datasets = session.get(f"{SUPERSET_URL}/api/v1/dataset").json()['result']
    for dataset in datasets:
        ds_id_ = dataset['id']
        ds_scheme_ = dataset['schema']
        ds_table_ = dataset['table_name']
        db_id_ = dataset['database'].get('id')
        if db_id == db_id_ and scheme == ds_scheme_ and table == ds_table_:
            return ds_id_




def main():
    setup_session(session=session_1,
                  SUPERSET_URL=SOURCE_SUPERSET_URL,
                  KEYCLOAK_URL=KEYCLOAK_URL,
                  KEYCLOAK_REALM=KEYCLOAK_REALM,
                  KEYCLOAK_CLIENT_ID=KEYCLOAK_CLIENT_ID,
                  KEYCLOAK_CLIENT_SECRET=KEYCLOAK_CLIENT_SECRET,
                  COOKIES=COOKIES)
    setup_session(session=session_2,
                  SUPERSET_URL=TARGET_SUPERSET_URL,
                  KEYCLOAK_URL=KEYCLOAK_URL,
                  KEYCLOAK_REALM=KEYCLOAK_REALM,
                  KEYCLOAK_CLIENT_ID=KEYCLOAK_CLIENT_ID,
                  KEYCLOAK_CLIENT_SECRET=KEYCLOAK_CLIENT_SECRET,
                  COOKIES=COOKIES)

    db_res = session_1.get(f"{SOURCE_SUPERSET_URL}/api/v1/database")
    dbs = db_res.json()["result"]
    databases = {}
    for db in dbs:
        databases[db.get("id")] = db.get('database_name')
    print(databases)

    print("✅ Авторизация через Keycloak выполнена")
    dashboard = get_dashboard(dashboard_id=SOURCE_DASHBOARD_ID,
                              SUPERSET_URL=SOURCE_SUPERSET_URL,
                              session=session_1,)
    layout = json.loads(dashboard["position_json"])
    charts = get_charts_from_layout(layout=layout,
                                    SUPERSET_URL=SOURCE_SUPERSET_URL,
                                    session=session_1)
    print(f"🔍 Найдено чартов: {len(charts)}")

    print(f"=== Create datasource map ===")
    # datasource_map is {dataset_id: [chart_id]}
        # base_dataset_id : {
        # old_scheme scheme
        # old_table table_name
        # new_scheme scheme
        # new_table table_name
        # old_db_id
        # new_db_id
        # new_ds_id int
    datasource_map = {}
    for chart in charts:
        query_context = json.loads(chart['query_context'])
        ds_id = query_context.get('datasource').get('id')
        if ds_id in datasource_map:
            continue
        datasource_map[ds_id] = {}
        # 'datasource_name_text' = schema.table_name
        # ds_name = chart['datasource_name_text']

        # chart_id = chart['chart_id']
        datasource_map[ds_id]['new_db_id'] = new_db_id

        dataset = get_dataset(dataset_id=ds_id,
                              SUPERSET_URL=SOURCE_SUPERSET_URL,
                              session=session_1)

        datasource_map[ds_id]['old_scheme'] = dataset['schema']
        datasource_map[ds_id]['old_table'] = dataset['table_name']
        ds_name = f"{datasource_map[ds_id]['old_scheme']}.{datasource_map[ds_id]['old_table']}"

        new_ds_name = dataset_map[ds_name]
        datasource_map[ds_id]['new_scheme'] = new_ds_name.split('.')[0]
        datasource_map[ds_id]['new_table'] = new_ds_name.split('.')[1]

        print(f"scheme={datasource_map[ds_id]['new_scheme']}, table={datasource_map[ds_id]['new_table']}, b_id={new_db_id}")
        if new_db_id == 52:
            pass

        founded = find_dataset(session=session_2,
                               SUPERSET_URL=TARGET_SUPERSET_URL,
                               scheme=datasource_map[ds_id]['new_scheme'],
                               table=datasource_map[ds_id]['new_table'],
                               db_id=new_db_id,
                               )

        if founded:
            datasource_map[ds_id]['new_ds_id'] = founded
            print("📐 Dataset is found")
        else:
            new_ds_id = create_dataset(SUPERSET_URL=TARGET_SUPERSET_URL,
                                        session=session_2,
                                        params={"database_id": new_db_id,
                                                "table_name": datasource_map[ds_id]['new_table'],
                                                "db_scheme_name": datasource_map[ds_id]['new_scheme'],
                                                "sql": "",
                                                "owners": [{"id": admin_user_id}]})
            datasource_map[ds_id]['new_ds_id'] = new_ds_id
            print("📐 Dataset is created")
            metrics = get_metrics(base_dataset_id=ds_id,
                                  SUPERSET_URL=SOURCE_SUPERSET_URL,
                                  session=session_1)
            create_new_metrics(session=session_2,
                               SUPERSET_URL=TARGET_SUPERSET_URL,
                               dataset_id=datasource_map[ds_id]['new_ds_id'],
                               metrics=metrics)
            print("📐 Metrics are copied")

    new_dashboard_id = create_dashboard(title=NEW_DASHBOARD_TITLE,
                                        SUPERSET_URL=TARGET_SUPERSET_URL,
                                        session=session_2)

    new_chart_ids, id_mapping = clone_charts(charts=charts,
                                             datasource_map=datasource_map,
                                             new_dashboard_id=new_dashboard_id,
                                             SUPERSET_URL=TARGET_SUPERSET_URL,
                                             session=session_2)
    print("📊 Charts are cloned")

    # duplicate_dashboard_with_charts_and_layout(original_dashboard_id=SOURCE_DASHBOARD_ID,
    #                                            new_dashboard_id=new_dashboard_id,
    #                                            chart_id_map=id_mapping,
    #                                            new_dataset_id=new_dataset_id)

    duplicate_dashboard_with_charts_and_layout(original_dashboard_id=SOURCE_DASHBOARD_ID,
                                               new_dashboard_id=new_dashboard_id,
                                               chart_id_map=id_mapping,
                                               datasource_map=datasource_map,
                                               SOURCE_SUPERSET_URL=SOURCE_SUPERSET_URL,
                                               TARGET_SUPERSET_URL=TARGET_SUPERSET_URL,
                                               session_1=session_1,
                                               session_2=session_2,
                                               )
    print(f"🎉 Новый дашборд создан! ID: {new_dashboard_id}")




if __name__ == "__main__":
    main()
