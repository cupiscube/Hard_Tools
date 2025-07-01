# Superset
## Superset dashboard cloner
Scrip copies a dashboard from one SS server to another server (it can copy in one server if source server url = target server).
Script has authorization through KeyCloack.

An algorythm of this script:

1. Authorization - get access_token from KeyCloack and get connections with two SS servers.
2. Get source data:
   * Dashboard_id
   * Dashboard chart list
   * Source dataset_id
   * Dataset metric list
   * Dashboard layout, cache, filters etc
3. Create new dataset in the target server.
4. Create metrics (clone from source server).
5. Create new dashboard in the target server.
6. Prepare and copy every chart to the new dashboard. We should change datasource id in every field, update query_context, params, clear fields depend on users. 
7. Prepare layout. we should change every old chart id to a new chart id, reconfigure native_filter_configuration with new dataset_id.
8. Add new charts to the dashboard.

## Superset warm
The problem: When you do export dashboard as zip and export to other server the query_context became to be lost on the export step. Query_context is important when you try to see chart by estimator user through other app.
Script should warm up the dashboard (update or create query_context). But this problem wasn't solved.

# ClickHouse
## clickhouse_size_estimator
Script for calculation CH table size in the Storage.
You should put SQL create table query and expected row number to the input.
In the end you get theoretical size.


