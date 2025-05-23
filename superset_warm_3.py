from idlelib import query

import requests
import json
from urllib.parse import urljoin
import ast

KEYCLOAK_URL = 'something'
KEYCLOAK_REALM = 'something'
KEYCLOAK_CLIENT_ID = 'something'
KEYCLOAK_CLIENT_SECRET = 'something'

SUPERSET_URL = "something"
# Login via browser -> f12 -> Application -> Cookie -> Session
COOKIES = {
    "session": "something"
}

def get_access_token():
    token_url = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token"
    payload = {
        "grant_type": "password",
        "scope": "openid",
        "client_id": KEYCLOAK_CLIENT_ID,
        "client_secret": KEYCLOAK_CLIENT_SECRET,
        "email": "something",
        "username": "something",
        "password": "something"
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    res = requests.post(token_url, data=payload, headers=headers)
    return res.json()["access_token"], res.json()["refresh_token"]

session = requests.Session()

def setup_session():
    access_token, _ = get_access_token()
    # Login via browser -> f12 -> Application -> Cookie -> Session
    session_cookie = COOKIES.get('session')
    session.cookies.set("session", session_cookie)
    # Теперь session содержит куку
    me_url = f"{SUPERSET_URL}/api/v1/me/"
    print(1234566)
    res = session.get(me_url,
                      timeout=5,
                      # allow_redirects=False
                      )
    print(res.status_code)
    print(res.json())
    res.raise_for_status()
    print(f'✅ Авторизован как: {res.json().get('result').get('username')}')

setup_session()
print("✅ Авторизация через Keycloak выполнена")

# Получение списка всех дашбордов
resp = session.get(urljoin(SUPERSET_URL, "/api/v1/dashboard/"))
dashboards = resp.json().get("result", [])









def get_datasource(params:dict):
    # Извлекаем datasource и разбираем его
    datasource = params.get("datasource")
    if not datasource:
        print(f"[ERROR] chart {chart_id} - отсутствует datasource в params")
    try:
        datasource_id, datasource_type = datasource.split("__")
        datasource_ = {
            "id": int(datasource_id),
            "type": datasource_type
        }
        return datasource_
    except ValueError:
        print(f"[ERROR] chart {chart_id} - некорректный формат datasource: {datasource}")
        return None


def rebuild_query_context(chart, datasource):
    chart_id = chart["id"]
    print(f"▶️ Обрабатываю chart_id={chart_id} ({chart['slice_name']})")

    params_str = chart.get("params")
    if not params_str:
        print(f"  ⚠️ Пропущено: нет params")
        return False
    try:
        params = json.loads(params_str)
        # form_data["datasource_id"] = datasource["id"]
        # form_data["datasource_type"] = datasource["type"]
    except Exception as e:
        print(f"  ❌ Ошибка чтения params: {e}")
        return False

    if isinstance(params, str):
        while isinstance(params, str):
            params = json.loads(params)

    # try:
    #     new_form_data = {
    #         "datasource": params['datasource'], # f"{datasource['id']}__{datasource['type']}",
    #         "viz_type": params['viz_type'],
    #         "metrics": params['metrics'],
    #         "groupby": params['groupby'],
    #         "query_context_generation": True
    #     }
    # except Exception as e:
    #     print(params)
    post = {
              "chart_id": chart["id"],
              "datasource_id": datasource["id"],
              "datasource_type": datasource["type"],
              "form_data": json.dumps(params), # json.dumps(new_form_data), # json.dumps(form_data)
              # "form_data": new_form_data,
            }

    # Отправляем form_data в Superset для получения query_context
    resp = session.post(
        urljoin(SUPERSET_URL, "/api/v1/explore/form_data"),
        # json={"form_data": form_data},
        # json=chart,
        json=post,
        headers={"Content-Type": "application/json"}
    )

    if resp.status_code != 200 and resp.status_code != 201:
        print(f"  ❌ Не удалось получить query_context: {resp.status_code} {resp.text}")
        return False

    key = resp.json().get("key")
    resp2 = session.get(
        urljoin(SUPERSET_URL, f"/api/v1/explore/form_data/{key}"),
        headers={"Content-Type": "application/json"}
    )

    q = resp2.json()
    new_form_data = json.loads(q.get("form_data"))

    new_chart_config_resp = session.get(urljoin(SUPERSET_URL, f"/api/v1/chart/{chart_id}", allow_fragments=True))
    new_chart = new_chart_config_resp.json()
    new_chart_data = new_chart["result"]

    new_params_raw = new_chart_data.get("params", "{}")
    new_params = json.loads(new_params_raw)


    # query_context_2 = new_chart_data.get("query_context")
    # if isinstance(query_context_2, str):
    #     while isinstance(query_context_2, str):
    #         query_context_2 = json.loads(query_context_2)

    query_context_  = new_chart_data.get("query_context")
    # query_context_ = json.loads(query_context_2)
    if isinstance(query_context_, str):
        while isinstance(query_context_, str):
            query_context_ = json.loads(query_context_)
    if isinstance(new_params, str):
        while isinstance(new_params, str):
            new_params = json.loads(new_params)
    if isinstance(new_form_data, str):
        while isinstance(new_form_data, str):
            new_form_data = json.loads(new_form_data)

    return query_context_, new_params, new_form_data



for dash in dashboards:
    dash_id = dash["id"]
    if dash_id != 8:
        continue
    print(f"Обрабатываю дашборд {dash_id} - {dash['dashboard_title']}")
    # Получение информации о дашборде (включая layout)
    dash_detail = session.get(urljoin(SUPERSET_URL, f"/api/v1/dashboard/{dash_id}")).json()
    position_json = dash_detail["result"].get("position_json", {})
    position_data = json.loads(position_json)
    # Сбор всех chart_id из layout
    chart_ids = {
        v["meta"]["chartId"]
        for v in position_data.values()
        if isinstance(v, dict) and "meta" in v and "chartId" in v["meta"]
    }
    print(f"  Найдено графиков: {len(chart_ids)}")
    for chart_id in chart_ids:
        try:
            print(f"    Прогреваю график {chart_id}...")
            # Получаем конфигурацию графика
            chart_config_resp = session.get(urljoin(SUPERSET_URL, f"/api/v1/chart/{chart_id}", allow_fragments=True))
            chart = chart_config_resp.json()
            chart_config_resp.raise_for_status()
            chart_data = chart["result"]
            params_raw = chart_data.get("params", "{}")
            # Преобразуем строку в dict
            try:
                params = json.loads(params_raw)
            except json.JSONDecodeError:
                params = ast.literal_eval(params_raw)
            # ############################# #
            if not chart_data:
                print(f"[ERROR] chart {chart_id} - нет данных в result")
                continue
            if isinstance(params, str):
                while isinstance(params, str):
                    params = json.loads(params)
            datasource = get_datasource(params)
            if datasource == None:
                continue
            # try:
            pass
            new_query_context, new_params, new_form_data = rebuild_query_context(chart_data, datasource)
            pass

            query_context_ = new_query_context


            queries = query_context_.get("queries", []) if query_context_ else []

            # queries_ = [json.dumps(query) for query in queries]
            # put_j = {
            #     "chart_id": chart_id,
            #     "dashboard_id": dash_id,
            #     "extra_filters": json.dumps({"queries": queries, "params": new_params}) # queries  # query_context, # query_context
            # }
            #
            # data_resp = session.put(
            #     urljoin(SUPERSET_URL, f"/api/v1/chart/warm_up_cache"),
            #     json=json.dumps(put_j),
            #     # json=query_context,
            #     headers={"Content-Type": "application/json"},
            #     timeout=20
            # )

            owners = [int(owner_dict['id']) for owner_dict in chart_data['owners']]

            if query_context_ is None:
                query_context_ = {"query_context_generation": True}


            put_j = {
                # "chart_id": chart_id,
                # "dashboard_id": [dash_id],
                # "datasource_id": datasource['id'],
                # "datasource_type": datasource['type'],
                # "datasource": datasource,
                "datasource": f"{datasource['id']}__{datasource['type']}",
                "owners": owners, # chart_data['owners'],
                "params": json.dumps(new_params), # json.dumps(chart_data['params']),
                "query_context": json.dumps(query_context_),
                "slice_name": chart_data['slice_name'],
                "viz_type": new_params["viz_type"]
                # "extra_filters": json.dumps({"queries": queries, "params": new_params}) # queries  # query_context, # query_context
            }

            data_resp = session.put(
                urljoin(SUPERSET_URL, f"/api/v1/chart/{chart_id}"),
                json=put_j,
                # json=query_context,
                headers={"Content-Type": "application/json"},
                timeout=20
            )

            data_resp = data_resp.json()



        except Exception as e:
            print(f"[ERROR] chart {chart_id} - {e}")












