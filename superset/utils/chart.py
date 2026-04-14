from urllib.parse import quote
import json
import copy


def get_charts(dashboard_id, SUPERSET_URL, session):
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

def clone_charts(charts,
                 # new_dataset_id,
                 datasource_map: dict,
                 new_dashboard_id,
                 SUPERSET_URL,
                 session):
    new_chart_ids = []
    id_mapping = {}
    for chart in charts:
        chart_id = chart["id"]
        new_chart = copy.deepcopy(chart)
        query_context = json.loads(chart['query_context'])
        dataset_id = query_context["datasource"]['id']
        # dataset_id = chart["datasource_id"]
        new_dataset_id = datasource_map.get(dataset_id).get("new_ds_id")
        if not new_dataset_id:
            raise Exception(f"There are no new dataset_id in {datasource_map.get(dataset_id)}")
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


def get_charts_from_layout(layout, SUPERSET_URL, session):
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





