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
    # "session": ".eJylVdmSq7YW_ZVbfo5PSwLb0G-ewNAGx8wolXKBGI0Y2mBjSOXfr-g-OTcnqcpQ94HClvZea-2J_cvsktziNpu9drd7_MPskkez11kQBAsSgTiJIhIEIBb5BCUIxkmAgBghkQjJkgeLKIkjEZAoWibcCqFI5MNltOASMUYQIJ4TIsQncYBWEQFiEvJRLEDCEy4g4QotyGoV8onARXCJFkLMrQAJBGEBRERmTMi9jW-fahD7G7RDRS4kC6oqpl9FRhBwIRLnzAfO-RVM5gGMhTlBRAjAKiYhF3zz_IaGfpjRmgQ0Zghxxe7r4N6x8H-Z_aebvf40iwc1C2WSn3LVtEcF6rnSKpWxIFslPeXr3KSRreR9HiBaKPl6qWzV3paaY1hSw6303uCaxuDOvM05D52LaHzAnm5toGurI-awfKbSHYOnrXmSrlTgC-NjNuv8dN1z-o6wJwXaSFqlpFm0VZaaRYA-EnDaMS1Dn_ueAwJJBIELqXKtn_p45tjDa1cbHbfqeyQXk_arJivAt-yFboIRy_bzaJ17vFO60y4rcA567YMrKnG5HzVXy5lvQzht8q2jg9GTsX4cOSfzzUUVogXwPbXwEaXHUryHMr1jUxywK7Whpz0MoKuGyfJUShAzzex99ZEIw-o84Y6RqzBchceWXvpXneo5LHB5HpimQb_6TNMZMk1QQ1KhjwWnIXz1R3vyBbG3njRtGdeAPWU6y-Lq42yMvA0llU6jLQQsy2CqC5nqcq3zk-sU2FUZDmH4EmX4AJcsRy6Ld1x32k6nJ8soTzta6LKTT76-qw-Tr_YZSxvKIofdcxdyaoMRvZNBWbqD8njL1Yjp-IzfETMf6fQjd1Wbk1Jsscd-0zbHslOyerVM3xCiJyUDrKYcTlwhwuVHHn_nzzBh6ErJR41lcQi8Jotk-ggZX2Ky2EpnDDln8JGTMK1XFvOoXJuVUumQyM5AkAOOnsGwzn_ScnaNLnD53PNA-_v6_NGO8d99N6JH97sadr67yDCyu4mXabizmNrAXdxYTth84AZ7pCMH9YFL2mKT6Z14qsl2M_VpPr3ZjBTKYcNygZtQtlPswixw-wmfMt4mlESEPZbrktKpj6KDCjGLOyylDpusrwojYxitslczdpcFSEQfNT-oFJcs_tIpPM4ZGQaL4WM-WA2-t2U1vfru8_OO5YNxV4GHaUjFbz6GLN2_6irZWRMeaPI_Dd_j_RYD68fCLyVASukWcniNkXiPZNazst5gc3ENEZjwHqSMDizfkBymfHcrpWRzBD57VrfOvD46OZuHDl9t7rQF4OT6_NFKeZ_lns0x1EqfZz3Z-1ZWfnyH3PPEzXQahYZ8Dm8Br-1wxmYL6Dut80s983NYajsbaTul10Yf4V0xafkW77_lPRU6i8NOHdnJwmlWKvURys7Ui6FSQMmyVcmeetaZesBgdZfu07dsmp3_j0vUDRtuDUeZ-vjLrthw0DOJCajVG3Lf_OjfO06_Dts-uY63Z_CUDvVBta6Nu7RStxI2oOXbwhv3dVto-4xfi3O841PYIevZHB614Sq-WXfnRfk41smuEWl3sOY-2iuV4MMeq8Vc6E6y8Q6Q69lYK8YaCumb_3wDm1g287gAtyF-pvV-6xjh4a44KDxxlizu7mYnr65bkAZx7GvP_qKWmbhqHu_yuqVVCbPhlGvD5eAUtZPq86A7b25CvDxe0o3hnperZr9038bNwzo9d6YQg_Y9czeKeInWV2mwlH4e210nrDYKSbd0DS9amvi9eFxv6v6NUOhU902F9u5JWu32UPrRPb6nR-VpaMF5QxZueDT11W41qg_PSdlOnP3869fFeGlu9SOP4htblynJ43kRD4TWQfHb5ry0XdBNy1R1Vfuk2f1-Ga8t34TpLeqKfRQK97VZP5h5E6TxJcvbrr4N06bNuq55fXmB4AsEn88CvApAEF5uNY3bF8pMX5jf39nFUd69oL80nLb_Pwf8l8Q___pf09sMgg.aCyFoQ.bQgmucyUbHdbTrU0lswdGL__Mik"
    # "session": ".eJylVduyqkgS_ZUOn3t3UBSonDdFQVBwi1xrYmIHVYBcCmQrqNDR_97JPn07M08T80Bwq8y1VubKql9nH9ktveezb92tT3-efRTJ7NssW7JswVi6kBKEMJLTJZ4vUaLEaLnEC8qomDFBELE8pwtZUJIlXiqikkiiKGYLuqCYYllGKY2VBYSJDMkxZiyT5jgRZXGZiomUZArCGFMhlbNEkeBG2XypMBzL82QGRPp7evvOBsErv7KYp_CSNvB2jfsOKP86-6mbffvXLB3MnOqsOBbm2RsNZBfG3WgcmanG5VisijNPPKN4FrHIK6NYzQ3VfHpae6A1d4LGfjq4bR18kjzsP2yc8HRHQttdo8AzR4KJfuJaT4SXZ4WabTTCL4AHa1bFsdxie8Pgql7WeLobNc8T1ZhbLhPskQnHTYVs9VlEoS_EmiLEAeJGeX3Z4wnDJVmlJx5U8zPRK-BujFFtPG09eh7PgnzULXxwndwuL91RPyFLFSTimpxsVi9b9CvibguIbRm2Jt3XZOc82Xh9HLCfR2e5oaIsRKFZRSLnh1rpqc57clYGEmh3GloPR7BN5wx1qjVEgDPcy0hUEG1OU94xCYyJE2DadVTa3C5QRerTcHBPg11G3XFzQqQQkCVqlT1W2BJJGY3eFCuk4WripALWQEJj-panzde3MQnXnDU2T1QkQJWFqS9s6kt5LY4B6ApMyMMgv8Yhv0BqqFGwHa1x1Vkbmx9dpz5ueGXrfjHFRoE9TLGW-qXlTnUFk-DUUWy2ROQ9G4x5MBiPfWEmwOO7fl_JI9HmX7Vr7gWrlTsJ4ZnfC6L7NfTrDvwGKr44G1Az1XDCoiKpv-r4j3jIiWigZV891pUhDts80fmDAl52Bm21P1LsD5HoZ8C1BM2jUbYLo7ER0_2Bib5wCB3IdfovLqfA6eJAKsJQuP-zP_-5DvD7KEj4Ifihh10UyDkRvW7CBQ49aLrHgXyDmsB8kJaErGM780Fqfidn4DvhNNPa9eTTYrrDjFTGbg21IC3VvQsJUB4Hzyk_B9yWaopIQqh1zfnko2RnIgK6aa115Ay-qpwcctyNrZnDvzwWFfGr5zvwcg36a78KsT9CDtDwNR_Qgx_XQk_LKHh9_wf1AOwmDgmnXPkrxtG1_g9eNXxr6Y5nf3P4Md-fGsCPVVRrAqu1G8VkRUSlT3TwrG635CyXVBSmfA9WJzuoN2K7qd7dwqhhjoTvnrXdk2SPfgHz0JHSw0dVEI5BJB3cixRB7YnuIauOJPDkM3Lz-msfCk4TNvB0KkuMMIHZtjYkh9kS7I3VRbWdRwWqrY0nWhvjaY2RSDbVxOUvvf8r7rGyQYd38XU_p9PcN-aD6v7kRWpUSHM9U_Mmz_qTBxzou9ZPe9k0O_8flmI7HlId35h8_Mt1Y1n07B2ryomMay1XiudeXo3HLeXtIpsXVg7L_tiu7Io84506V-aVa6jjUljYTetosUo-NQV5ilwN0J-n0bNYSCTPicv1dR-Vu329iwh6c42qJ4okcmxJZyFdOKvLkt9eJr5mftzdOt9T6SZwYYNbv8ef-evBc81DyVZ_J0EsIX8_3wnjE--VS5O71-tK9l4H5s61W5NYR7XsD_tUqD-UTb021vXnadkWSbros0-GhMUb7Y2PS1muljwz19k621pt7hdBoF7ANAfP-vDNdKF2W_s92_ubSOpCHl3vz6cRdc5rdA6w82z8yDPmaLBqt99K_nDGH8l7sN9nnxe1bhbe6rF9WVsVb7s3cziv4Eyc_fu3Pw7Gj_Z2fQCfGxyXF1akb1U6MH6Nqz9Pzo97F3fTYfq-FA67Byalnm_2evfpH8qRyo8Bq2O77We__Q7tr7WR.aCyIWg.g0ORXWgm2Vy5B-puqvJ5fi1RC4E"
    "session": "something"}

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












