
def get_dataset(dataset_id, SUPERSET_URL, session):
    url = f"{SUPERSET_URL}/api/v1/dataset/{dataset_id}"
    res = session.get(url)
    res.raise_for_status()
    return res.json()["result"]

def get_metrics(base_dataset_id, SUPERSET_URL, session):
    # Получаем метрики из старого датасета
    base_url = f"{SUPERSET_URL}/api/v1/dataset/{base_dataset_id}"
    res = session.get(base_url)
    res.raise_for_status()
    base_data = res.json()["result"]
    metrics = base_data["metrics"]
    return metrics


def get_dataset_id(session, superset_url, database, schema, table_name):
    url = f"{superset_url}/api/v1/dataset/?q=(page_size:1000)"
    res = session.get(url, timeout=10)
    res.raise_for_status()
    for ds in res.json().get("result", []):
        if (
            # ds.get("database", {}).get("id") == database
            # and
            ds.get("schema") == schema
            and ds.get("table_name") == table_name
        ):
            return ds["id"]
    print(f'There is no table {table_name} in {database}/{schema}')
    return None
    # raise ValueError(f"Не найден датасет: db={database}, schema={schema}, table={table_name}")

def create_dataset(SUPERSET_URL,
                   session,
                   params):
    """
    Create new dataset.
    :param params: {"database_id": int,
                    "table_name": str,
                    "db_scheme_name": str,
                    "sql": optional,
                    "owners": optional list [{"id": int}]}
    :param SUPERSET_URL: https://superset.com
    :param session: requests.Session()
    :return: dataset_id
    """
    payload = {
        "database": params["database_id"],
        "schema": params["db_scheme_name"],
        "table_name": params["table_name"],
        # "sql": params.get("sql", ""),
        # "extra": params.get("extra"),
        # "is_managed_externally": False,,
        # "is_managed_externally": True,
        # "owners": [params.get("owners")[0].get("id")],
    }

    url = f"{SUPERSET_URL}/api/v1/dataset/"
    dataset_id = get_dataset_id(session, SUPERSET_URL,
                                database=params["database_id"],
                                schema=params["db_scheme_name"],
                                table_name=params["table_name"])
    if dataset_id:
        return dataset_id

    pass
    res = session.post(url, json=payload)
    pass
    res.raise_for_status()
    return res.json()["id"]

def create_new_metrics(session, SUPERSET_URL, dataset_id, metrics):
    new_url = f"{SUPERSET_URL}/api/v1/dataset/{dataset_id}"
    res = session.get(new_url)
    res.raise_for_status()
    new_data = res.json()["result"]

    allowed_column_fields = {
        "id",
        "column_name",
        "advanced_data_type",
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
    clean_columns = [{k: v for k, v in col.items() if k in allowed_column_fields} for col in new_data["columns"]]

    new_metrics = []
    for metric in metrics:
        if metric.get("metric_name") != "count":
            new_metrics.append({
                "metric_name": metric["metric_name"],
                "expression": metric["expression"],
                "metric_type": "SQL",
                "verbose_name": metric.get("verbose_name"),
                "description": metric.get("description", ""),
                # "d3format": metric.get("d3format", ""),
                "d3format": metric.get("d3format") or None,
                "warning_text": metric.get("warning_text", ""),
                "extra": metric.get("extra", ""),
            })

    payload = {
        "table_name": new_data.get("table_name"),
        "schema": new_data.get("schema"),
        "sql": new_data.get("sql"),
        "template_params": new_data.get("template_params"),
        "extra": new_data.get("extra"),
        "description": new_data.get("description"),
        # "database": new_data["database"]["id"] if isinstance(new_data["database"], dict) else new_data["database"],
        # "database": {
        #     "id": new_data["database"]["id"] if isinstance(new_data["database"], dict) else new_data["database"]},
        "columns": clean_columns,
        "metrics": new_metrics,
        "owners": [o["id"] for o in new_data.get("owners", [])],
    }

    update_url = f"{SUPERSET_URL}/api/v1/dataset/{dataset_id}"
    res = session.put(update_url, json=payload)
    if res.status_code not in (200, 201) and res.text != '{"message":{"metrics":["One or more metrics already exist"]}}\n':
        pass

    if res.text == '{"message":{"metrics":["One or more metrics already exist"]}}\n':
        print('Metrics are already exist')
        return True
    if res.status_code not in (200, 201):
        print("Ошибка:", res.status_code, res.text)
        res.raise_for_status()
    return True



