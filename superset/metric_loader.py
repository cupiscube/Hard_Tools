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

# from metric_sample import kpi_metrics

from utils.config import KEYCLOAK_URL, KEYCLOAK_REALM, KEYCLOAK_CLIENT_ID, KEYCLOAK_CLIENT_SECRET, COOKIES



# setup_session >> create_db >> create dataset >> load metrics


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

    db_id = 10  # 7
    base_dataset_id = 46
    table_name = 'lab_data_catalogs_checker'
    schema = 'reports'

    metrics = get_metrics(base_dataset_id=base_dataset_id,
                          SUPERSET_URL=SUPERSET_URL,
                          session=session)
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
                       metrics=metrics)

    print(f'Dataset {dataset_id} with schema {schema} with table {table_name} is updated/created')

    # for database in kpi_metrics["databases"]:
    #     db_name = database["database_name"]
    #     sqlalchemy_uri = database["sqlalchemy_uri"]
    #     # db_id = create_db(session=session,
    #     #                   SUPERSET_URI=SUPERSET_URL,
    #     #                   params={ "db_name": db_name,
    #     #                            "sqlalchemy_uri": sqlalchemy_uri,
    #     #                            "backend": "clickhousedb",})

        # metrics=dataset["metrics"])
        # for dataset in database["datasets"]:
        #     table_name = dataset["table_name"]
        #     schema = dataset["schema"]
        #     dataset_id = create_dataset(SUPERSET_URL=SUPERSET_URL,
        #                                 session=session,
        #                                 params={"database_id": db_id,
        #                                         "table_name": table_name,
        #                                         "db_scheme_name": schema,
        #                                         "sql": "",
        #                                         "owners": [{"id": admin_user_id}]})
        #     create_new_metrics(session=session,
        #                        SUPERSET_URL=SUPERSET_URL,
        #                        dataset_id=dataset_id,
        #                        metrics=dataset["metrics"])
        #     print(f'Dataset {dataset_id} with schema {schema} with table {table_name} is updated/created')





if __name__ == "__main__":
    main()
