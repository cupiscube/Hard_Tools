import requests
import json
import copy

def get_dashboard(dashboard_id, SUPERSET_URL, session):
    url = f"{SUPERSET_URL}/api/v1/dashboard/{dashboard_id}"
    res = session.get(url)
    res.raise_for_status()
    return res.json()["result"]


def create_dashboard(title, SUPERSET_URL, session):
    payload = {
        "dashboard_title": title,
        "published": True
    }
    url = f"{SUPERSET_URL}/api/v1/dashboard/"
    res = session.post(url, json=payload)
    res.raise_for_status()
    return res.json()["id"]


def duplicate_dashboard_with_charts_and_layout(original_dashboard_id,
                                               new_dashboard_id,
                                               chart_id_map,
                                               new_dataset_id,
                                               SOURCE_SUPERSET_URL,
                                               TARGET_SUPERSET_URL,
                                               session_1,
                                               session_2):
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





