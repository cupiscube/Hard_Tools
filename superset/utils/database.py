def create_db(session, SUPERSET_URI, params):
    """
    Create new database in superset.
    :param session: requests.Session()
    :param SUPERSET_URI: "http://superset:8080"
    :param params: {
        "db_name": str,
        "sqlalchemy_uri": str,
        "backend": "clickhousedb" or "postgresql",
        "configuration_method": optional "sqlalchemy_form" by default,
        "expose_in_sqllab": optional True by default,
        "allow_ctas": optional False by default,
        "allow_cvas": optional False by default,
        "allow_dml": optional False by default,
    }
    :return: db_id
    """
    db_payload = {
        "database_name": params["db_name"],
        "sqlalchemy_uri": params["sqlalchemy_uri"],
        "backend": params["backend"],
        # поля, которые часто используются — можно переопределить через params
        # "configuration_method": params.get("configuration_method", "sqlalchemy_form"),
        # "configuration_method":"dynamic_form",
        "configuration_method": "sqlalchemy_form",
        "host": "10.100.100.50",
        "port": "8123",
        "user": "superset",
        "password": "superset",
        "allow_run_async": True,
        # "expose_in_sqllab": params.get("expose_in_sqllab", True),
        # "allow_ctas": params.get("allow_ctas", False),
        # "allow_cvas": params.get("allow_cvas", False),
        # "allow_dml": params.get("allow_dml", False),
        "allows_virtual_table_explore": True,
    }
    # POST /api/v1/database/
    create_url = f"{SUPERSET_URI}/api/v1/database/"
    res_ = session.get(create_url,
                       # headers=headers,
                       timeout=30)
    pass
    try:
        res = session.post(create_url,
                         json=db_payload,
                         # headers=headers,
                         timeout=30)
    except Exception as e:
        return False
    pass
    res.raise_for_status()
    return res.json()["id"]

