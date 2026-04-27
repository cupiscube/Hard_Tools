import time
import datetime

import pandas as pd
import requests
from requests.auth import HTTPBasicAuth

# Get table
main_excel_path = r'./data'
tokens_path = r'./data'

df = pd.read_excel(f'{main_excel_path}/New tags and projects list_Toggl.xlsx', sheet_name='1.2-User-specific tags', index_col='Activity type')
tags_format = pd.read_excel(f'{main_excel_path}/New tags and projects list_Toggl.xlsx', sheet_name='Tags - Format')
projects = pd.read_excel(f'{main_excel_path}/New tags and projects list_Toggl.xlsx', sheet_name='Projects')
clients = pd.read_excel(f'{main_excel_path}/New tags and projects list_Toggl.xlsx', sheet_name='Client Name')
tokens = pd.read_excel(f'{tokens_path}/API Tokens.xlsx', sheet_name='API Token')

# rep_fix = pd.read_excel('./report_fix.xlsx', sheet_name='tags_report')
rep_fix = None

people = df.columns
# people = people[:-1]
# people = ['BADA']
# people = ['BADA'] #, 'SMVE']
people = [
    'BADA', # \/
    'AIVI', # \/
    'BODM', # \/
    'CHAL', # \/
    'DIDA', # \/
    'KURO', # \/
    'AMAN', # \/
    'NIRO', # \/
    'PRAR', # \/
    'SMVE', # \/
    'TODA', # \/
    'VAEL', # \/
    'ANAS', # \/
    'NIAL', # \/
    'KAAN', # \/
    'LAOK', # \/
]

pass

class Requests:
    def __init__(self):
        self.req_number = 0

    def wait(self):
        self.req_number += 1
        if self.req_number < 29:
            print(f'Осталось {30 - self.req_number} запросов в текущий час!!!')
            return True
        else:
            self.req_number = 0
            print(f'I am sleeping!!! {datetime.datetime.now().time()}')
            time.sleep(60*61)
            return True



auths = {}
for p in people:
    token = tokens.loc[tokens['Столбец1'] == p, 'API Token'].values[0]
    auths[p] = (token, "api_token")

personalized_tags = {}
for p in people:
#     tags_1 = [
# "AT: Bacteriology-Catalog",
# "AT: Benchmark-Book",
# "AT: Brochures",
# "AT: Conference",
# "AT: Data&Systems",
# "AT: Ecosystem-of-Systems",
# "AT: Global-Partnership",
# "AT: IFCC",
# "AT: Lab-Academy",
# "AT: Lab-Avatar",
# "AT: Lab-Calculator",
# "AT: Lab-Data-ARAB",
# "AT: Lab-Catalog Horizontals",
# "AT: Lab-Data-Matching",
# "AT: Lab-Data-Technical-Charts",
# "AT: Lab-Efficiency-Workshop",
# "AT: Lab-Flow",
# "AT: Lab-Passports",
# "AT: Local-Catalog",
# "AT: Marketing",
# "AT: ML",
# "AT: More-Data",
# "AT: MSC",
# "AT: Project-Management",
# "AT: Sorting-Logic",
# "AT: Tender-Management",
# "AT: TPC",
# "AT: Transformation",
# "AT: Unified-Production-Concept",
# "AT: N/A"
#     ]
#     tags_2 = [
#             "AT: Assessment on site",
#             "AT: Bank operations",
#             "AT: Benchmark-Book",
#             "AT: Business requirements",
#             "AT: Business trip",
#             "AT: Client's data handling",
#             "AT: Commercialization",
#             "AT: Contract-Heatmap",
#             "AT: Design",
#             "AT: HR-management",
#             "AT: HR-recruiting",
#             "AT: Internal-Admin",
#             "AT: Lab-Efficiency-Workshop",
#             "AT: Lab-Flow",
#             "AT: Lab-Horizontals",
#             "AT: Lab-Modeling",
#             "AT: Make-up",
#             "AT: Methodology",
#             "AT: ML",
#             "AT: Presale",
#             "AT: Presentations",
#             "AT: Project-Management",
#             "AT: Recruiting",
#             "AT: Reports",
#             "AT: Scientific research",
#             "AT: Sorting Logic",
#             "AT: TPC",
#             "AT: Travel Support",
#             "AT: Tutorship",
#             "AT: Validation",
#             "AT: Weekly meeting",
#             "AT: N / A",
#     ]
#     tags = list(set(tags_2) - set(tags_1))
#     personalized_tags[p] = tags #  + tags_format['Tags - Format'].to_list()
    # personalized_tags[p] = df.loc[df[p] == 1].index.to_list() + tags_format['Tags - Format'].to_list()
    tags = []
    personalized_tags[p] = tags






clients['key'] = 1
projects['key'] = 1
df_cross = pd.merge(clients, projects, how='left', on='key')
df_filtered = df_cross[df_cross.apply(
    lambda row: row['Client Name'] in row['Projects'], axis=1
)]
df_filtered = df_filtered.drop('key', axis=1)
df = pd.merge(clients.drop('key', axis=1), df_filtered, on='Client Name', how='left')



df.rename(columns={'Projects': 'project_name', 'Client Name': 'client_name'}, inplace=True)

# bernhoven = {'client_name': ['Siemens-Bernhoven', 'Siemens-Bernhoven', 'Siemens-Bernhoven', 'Siemens-Bernhoven'],
#              'project_name': ['Bernhoven-Assessment', 'Bernhoven-Lab-Avatar', 'Bernhoven-Lab-Calculator', 'Bernhoven-Transformation']}
# bernhoven_df = pd.DataFrame.from_dict(bernhoven)
# df = pd.merge(df, bernhoven_df, on=['client_name', 'project_name'], how='outer')







# bernhoven = {'client_name': ['BC Europe&UK', 'BC SWLP', 'BC WoE'],
#              'project_name': ['BC Europe&UK-BI', 'BC SWLP-KPI Compliance', 'BC WoE-KPI Compliance']}



# bernhoven = {'client_name': ['Alrijne', 'Alrijne', 'Alrijne'],
#              'project_name': ['Alrijne-General', 'Alrijne-Hospital-Lab-Design', 'Alrijne-Tender Support']}

# bernhoven = {'client_name': ['BC 6S', 'BC Cork&Kerry', 'BC Fr Bordeaux', 'BC Fr Bordeaux'],
#              'project_name': ['BC 6S-KPI Compliance', 'BC Cork&Kerry-KPI Compliance', 'BC Fr Bordeaux-General', 'BC Fr Bordeaux-Tender Support']}

# bernhoven = {'client_name': ['Dicoon', 'Dicoon', 'Dicoon', 'Dicoon'],
#              'project_name': ['Dicoon-Assessment', 'Dicoon-Lab-Avatar', 'Dicoon-Lab-Calculator', 'Dicoon-Lab-Data']}

# bernhoven = {'client_name': ['GCG', 'GCG'],
#              'project_name': ['GCG-Benchmark-Tool', 'GCG-KPI Compliance']}

# bernhoven = {'client_name': ['Regiolab'],
#              'project_name': ['Regiolab-General']}

#
# bernhoven = {'client_name': ['Certe', 'StreekLab'],
#              'project_name': ['Certe-Tender management', 'StreekLab-Tender management']}
# replacement_project = { 'Certe-Tender management': 'Certe-Tender Support',
#                         'StreekLab-Tender management': 'StreekLab-Tender Support'}

# bernhoven = {'client_name': ['TEST_CLIENT_1', 'TEST_CLIENT_2'],
#              'project_name': ['TEST_PROJ_1', 'TEST_PROJ_2']}
# replacement_project = { 'TEST_PROJ_1': 'TEST_PROJ_1_REPLACED',
#                         'TEST_PROJ_2': 'TEST_PROJ_2_REPLACED'}





tags_to_delete = ['AT: Benchmark-Book']
projects_to_delete = ["GCG-Benchmarking tool"]

# tags = ['AT: Cito-list', 'AT: Contract', 'Format: Meeting with Hospital']
#
#
# for p in personalized_tags:
#     personalized_tags[p] = tags



# tags = ['AT: Assessment on site',
#              'AT: Make-up', 'AT: Methodology',
#              'AT: Presentations',
#              'AT: Project-Management',
#              'AT: Reports',
#              'AT: Tutorship',
#              'AT: Validation']
#
# for p in personalized_tags:
#     personalized_tags[p] = tags

# TODO: + LAOK personal_tags






# df = pd.DataFrame.from_dict(bernhoven)
# df = pd.merge(df, bernhoven_df, on=['client_name', 'project_name'], how='outer')
#
# df = df.loc[(df['client_name']=='Potential Client') & (df['project_name']=='Potential Client-Project')]






# df = df.loc[df['client_name']=='Siemens-Bernhoven']
# df = df.loc[(df['client_name']=='BC SWLP') & (df['project_name']=='BC SWLP-BI')]






class UserRequests:
    def __init__(self, user: str, token: str):
        self.user = user
        self.token = token
        self.req_number = 0

    def wait(self):
        self.req_number += 1
        if self.req_number < 29:
            print(f'Осталось {30 - self.req_number} запросов в текущий час!!!')
            return True
        else:
            self.req_number = 0
            print(f'I am sleeping!!! {datetime.datetime.now().time()}')
            time.sleep(60*61)
            return True

    def get_workspace_id(self, auth):
        print("📡 Получаем workspace ID...")
        if self.wait():
            pass
        me_response = requests.get("https://api.track.toggl.com/api/v9/me", auth=auth)
        if me_response.status_code != 200:
            pass
            print("❌ Ошибка при получении информации. Проверьте API токен.")
            exit(1)
        workspace_id = me_response.json().get("default_workspace_id")
        print(f"✅ Workspace ID: {workspace_id}")
        return workspace_id




# ============ Projects ============ #
def create_project(auth, workspace_id, name, client_id, req_access, new_name=None): #, colour_id):
    url = f"https://api.track.toggl.com/api/v9/workspaces/{workspace_id}/projects"
    # Check if it is already done
    if req_access.wait():
        pass
    resp = requests.get(url, auth=auth)
    resp_j = resp.json()
    for project in resp_j:
        if project["name"] == name:
            return project['id']

    if client_id is None:
        return None
    if pd.isnull(name):
        return None
    else:
        data = {
            "name": name,
            "client_id": client_id,
            "active": True,
            "is_private": True,
            # "color": str(colour_id),
        }
        if req_access.wait():
            pass
        resp = requests.post(url, json=data, auth=auth)
        resp.raise_for_status()
        project_id = resp.json()["id"]
        print(f"✅ Создан проект: {name} (для клиента ID {client_id})")
        return project_id

def replace_project(auth, workspace_id, client_id, old_name, new_name, req_access): #, colour_id):
    url = f"https://api.track.toggl.com/api/v9/workspaces/{workspace_id}/projects"
    # Check if it is already done
    resp = requests.get(url, auth=auth)
    resp_j = resp.json()
    for project in resp_j:
        if project["name"] == old_name:
            data = {
                "name": new_name,
            }
            url = f"https://api.track.toggl.com/api/v9/workspaces/{workspace_id}/projects/{project['id']}"
            if req_access.wait():
                pass
            resp = requests.put(url, json=data, auth=auth)
            resp.raise_for_status()
            # project_id = resp.json()["id"]
            print(f"✅ Изменен проект: {old_name} на {new_name} (для клиента ID {client_id})")
            return project['id']
    print(f"❌ Проект {old_name} не найден")

def delete_projects(auth, workspace_id, req_access, project_names: list):
    url = f"https://api.track.toggl.com/api/v9/workspaces/{workspace_id}/projects"
    resp = requests.get(url, auth=auth)
    resp.raise_for_status()
    projects = resp.json()

    project_dict = {}
    for project in projects:
        if project["name"] in project_names:
            project_dict[project["name"]] = project["id"]
    if len(project_dict) == 0:
        print(f'There is no {project_names} tag in this workspace')
        return None
    for project in project_dict:
        project_id = project_dict[project]
        del_url = f"https://api.track.toggl.com/api/v9/workspaces/{workspace_id}/projects/{project_id}"
        if req_access.wait():
            pass
        del_resp = requests.delete(del_url, auth=auth)
        if del_resp.status_code == 200:
            print(f"✅ Удалён проект: {project}")
        else:
            print(f"❌ Ошибка при удалении проекта {project}: {del_resp.status_code}")

def delete_all_projects(auth, workspace_id, req_access):
    url = f"https://api.track.toggl.com/api/v9/workspaces/{workspace_id}/projects"
    resp = requests.get(url, auth=auth)
    resp.raise_for_status()
    projects = resp.json()

    for project in projects:
        project_id = project["id"]
        del_url = f"https://api.track.toggl.com/api/v9/workspaces/{workspace_id}/projects/{project_id}"
        if req_access.wait():
            pass
        del_resp = requests.delete(del_url, auth=auth)
        # archive_resp = requests.put(del_url, json={'active': False}, auth=auth)
        if del_resp.status_code == 200:
            print(f"✅ Удален проект: {project['name']}")
        else:
            print(f"❌ Ошибка при удалении проекта {project['name']}: {del_resp.status_code}")
# ============ Projects ============ #

# ============ Clients ============ #
def create_client(auth, workspace_id, name, req_access):
    # Check if it is already done
    if req_access.wait():
        pass
    url = f'https://api.track.toggl.com/api/v9/workspaces/{workspace_id}/clients'
    resp = requests.get(url, auth=auth)
    resp_j = resp.json()
    for client in resp_j:
        if client["name"] == name:
            return client['id']
    # if it is absent
    url = f"https://api.track.toggl.com/api/v9/workspaces/{workspace_id}/clients"
    data = {"name": name}
    if req_access.wait():
        pass
    resp = requests.post(url, json=data, auth=auth)
    if resp.status_code == 200:
        print(f"✅ Создан клиент: {name}")
        client_id = resp.json()["id"]
        return client_id
    else:
        print(f"❌ Ошибка при создании клиента {name}: {resp.status_code}, {resp.text}")
        return None

def replace_client(auth, workspace_id, old_name, new_name, req_access):
    # Check if it is already done
    if req_access.wait():
        pass
    url = f'https://api.track.toggl.com/api/v9/workspaces/{workspace_id}/clients'
    resp = requests.get(url, auth=auth)
    resp_j = resp.json()
    for client in resp_j:
        if client["name"] == old_name:
            url = f'https://api.track.toggl.com/api/v9/workspaces/{workspace_id}/clients/{client["id"]}'
            data = {"name": new_name}
            if req_access.wait():
                pass
            resp = requests.put(url, json=data, auth=auth)
            if resp.status_code == 200:
                print(f"✅ Изменен клиент: {old_name} на {new_name}")
                return client['id']
            else:
                print(f"❌ Ошибка при изменении клиента {old_name}: {resp.status_code}, {resp.text}")
                return None
    print(f"❌ Клиент {old_name} не найден")

def delete_clients(auth, workspace_id, req_access, clients_names: list):
    url = f"https://api.track.toggl.com/api/v9/workspaces/{workspace_id}/clients"
    resp = requests.get(url, auth=auth)
    resp.raise_for_status()
    clients = resp.json()

    client_dict = {}
    for client in clients:
        if client["name"] in clients_names:
            client_dict[client["name"]] = client["id"]
    if len(client_dict) == 0:
        print(f'There is no {clients_names} tag in this workspace')
        return None
    for client in client_dict:
        project_id = client_dict[client]
        del_url = f"https://api.track.toggl.com/api/v9/workspaces/{workspace_id}/clients/{project_id}"
        if req_access.wait():
            pass
        del_resp = requests.delete(del_url, auth=auth)
        if del_resp.status_code == 200:
            print(f"✅ Удалён проект: {client}")
        else:
            print(f"❌ Ошибка при удалении клиента {client}: {del_resp.status_code}")

def delete_all_clients(auth, workspace_id, req_access):
    url = f"https://api.track.toggl.com/api/v9/workspaces/{workspace_id}/clients"
    resp = requests.get(url, auth=auth)
    resp.raise_for_status()
    clients = resp.json()

    for client in clients:
        client_id = client["id"]
        del_url = f"https://api.track.toggl.com/api/v9/workspaces/{workspace_id}/clients/{client_id}"
        if req_access.wait():
            pass
        del_resp = requests.delete(del_url, auth=auth)
        if del_resp.status_code == 200:
            print(f"✅ Удалён клиент: {client['name']}")
        else:
            print(f"❌ Ошибка при удалении клиента {client['name']}: {del_resp.status_code}")
# ============ Clients ============ #

# ============ Tags ============ #
def create_tags(auth, workspace_id, tag_list, req_access):
    created_tags = []
    for tag_name in tag_list:
        url = f"https://api.track.toggl.com/api/v9/workspaces/{workspace_id}/tags"
        data = {"name": tag_name}
        if req_access.wait():
            pass
        resp = requests.post(url, json=data, auth=auth)
        if resp.status_code == 200:
            print(f"✅ Создан тэг: {tag_name}")
            created_tags.append(tag_name)
        elif resp.status_code == 400 and "already exists" in resp.text:
            print(f"⚠️ Тэг уже существует: {tag_name}")
        else:
            print(f"❌ Ошибка при создании тэга {tag_name}: {resp.status_code} {resp.text}")
    return created_tags

def replace_tag(auth, workspace_id, old_name, new_name, req_access):
    # Check if it is already done
    if req_access.wait():
        pass
    url = f'https://api.track.toggl.com/api/v9/workspaces/{workspace_id}/tags'
    resp = requests.get(url, auth=auth)
    resp_j = resp.json()
    for tag in resp_j:
        if tag["name"] == old_name:
            url = f'https://api.track.toggl.com/api/v9/workspaces/{workspace_id}/tags/{tag["id"]}'
            data = {"name": new_name}
            if req_access.wait():
                pass
            resp = requests.put(url, json=data, auth=auth)
            if resp.status_code == 200:
                print(f"✅ Изменен тег: {old_name} на {new_name}")
                return tag['id']
            else:
                print(f"❌ Ошибка при изменении тега {old_name}: {resp.status_code}, {resp.text}")
                return None
    print(f"❌ Тег {old_name} не найден")

def delete_tags(auth, workspace_id, req_access, tag_names: list):
    url = f"https://api.track.toggl.com/api/v9/workspaces/{workspace_id}/tags"
    resp = requests.get(url, auth=auth)
    resp.raise_for_status()
    tags = resp.json()
    tags_dict = {}
    for tag in tags:
        if tag["name"] in tag_names:
            tags_dict[tag["name"]] = tag["id"]
    if len(tags_dict) == 0:
        print(f'There is no {tag_names} tag in this workspace')
        return None
    for tag in tags_dict:
        tag_id = tags_dict[tag]
        del_url = f"https://api.track.toggl.com/api/v9/workspaces/{workspace_id}/tags/{tag_id}"
        if req_access.wait():
            pass
        del_resp = requests.delete(del_url, auth=auth)
        if del_resp.status_code == 200:
            print(f"✅ Удалён тэг: {tag}")
        else:
            print(f"❌ Ошибка при удалении тэга {tag}: {del_resp.status_code}")

def delete_all_tags(auth, workspace_id, req_access):
    url = f"https://api.track.toggl.com/api/v9/workspaces/{workspace_id}/tags"
    resp = requests.get(url, auth=auth)
    resp.raise_for_status()
    tags = resp.json()
    for tag in tags:
        tag_id = tag["id"]
        del_url = f"https://api.track.toggl.com/api/v9/workspaces/{workspace_id}/tags/{tag_id}"
        if req_access.wait():
            pass
        del_resp = requests.delete(del_url, auth=auth)
        if del_resp.status_code == 200:
            print(f"✅ Удалён тэг: {tag['name']}")
        else:
            print(f"❌ Ошибка при удалении тэга {tag['name']}: {del_resp.status_code}")
# ============ Tags ============ #

# ============ Reports ============ #
def get_tag_report(auth, workspace_id, req_access):
    url = f"https://api.track.toggl.com/api/v9/workspaces/{workspace_id}/tags"
    resp = requests.get(url, auth=auth)
    resp.raise_for_status()
    tags = resp.json()
    return pd.DataFrame.from_dict(tags)

def get_project_report(auth, workspace_id, req_access):
    url = f"https://api.track.toggl.com/api/v9/workspaces/{workspace_id}/projects"
    resp = requests.get(url, auth=auth)
    resp.raise_for_status()
    projects = resp.json()
    return pd.DataFrame.from_dict(projects)

def get_clients_report(auth, workspace_id, req_access):
    url = f"https://api.track.toggl.com/api/v9/workspaces/{workspace_id}/clients"
    resp = requests.get(url, auth=auth)
    resp.raise_for_status()
    clients = resp.json()
    return pd.DataFrame.from_dict(clients)
# ============ Reports ============ #

# ============ Fix utils ============ #
def fix_tag_list(auth, workspace_id, req_access, rep_fix):
    add_tags = rep_fix.loc[rep_fix['Column1']=='add', 'name'].tolist()
    # update_tags = rep_fix.loc[rep_fix['Column1']=='update', ['name', 'right_variant']].tolist()
    del_tags = rep_fix.loc[rep_fix['Column1'] == 'delete', 'name'].tolist()
    delete_tags(auth, workspace_id, req_access, del_tags)
    # update_tags(auth, workspace_id, req_access, update_tags)
    create_tags(auth, workspace_id, add_tags, req_access)

def fix_project_list(auth, workspace_id, req_access, rep_fix):
    add_tags = rep_fix.loc[rep_fix['Column1']=='add', 'name'].tolist()
    update_tags = rep_fix.loc[rep_fix['Column1'] == 'update', 'name'].tolist()
    del_tags = rep_fix.loc[rep_fix['Column1'] == 'delete', 'name'].tolist()
    delete_tags(auth, workspace_id, req_access, del_tags)
    create_tags(auth, workspace_id, add_tags, req_access)

def fix_client_list(auth, workspace_id, req_access, rep_fix):
    add_tags = rep_fix.loc[rep_fix['Column1']=='add', 'name'].tolist()
    update_tags = rep_fix.loc[rep_fix['Column1'] == 'update', 'name'].tolist()
    del_tags = rep_fix.loc[rep_fix['Column1'] == 'delete', 'name'].tolist()
    delete_tags(auth, workspace_id, req_access, del_tags)
    create_tags(auth, workspace_id, add_tags, req_access)
# ============ Fix utils ============ #




# ============ main script ============ #
def run(df, personalized_tags:dict[list]=personalized_tags):
    tags_df_list = []
    projects_df_list = []
    clients_df_list = []
    for man in people:
        print(f'############################ Приступаю к {man} ############################')
        req_access = Requests()
        auth = auths[man]

        # Получаем workspace_id
        print("📡 Получаем workspace ID...")
        if req_access.wait():
            pass
        me_response = requests.get("https://api.track.toggl.com/api/v9/me", auth=auth)
        if me_response.status_code != 200:
            pass
            print("❌ Ошибка при получении информации. Проверьте API токен.")
            exit(1)
        workspace_id = me_response.json().get("default_workspace_id")
        print(f"✅ Workspace ID: {workspace_id}")

        # print("🔄 Удаление всех проектов...")
        # delete_all_projects(auth, workspace_id)

        # print("🔄 Удаление всех клиентов...")
        # delete_all_clients(auth, workspace_id)


        print("🚀 Создание новых клиентов и проектов...")
        client_id_map = {}

        # for _, row in df.iterrows():
        #     client_name = row["client_name"]
        #     project_name = row["project_name"]
        #
        #     # if client_name in ['Abbott', 'Alrijne', 'BC', 'Certe', 'Cork&Kerry']:
        #     #     continue
        #
        #     if client_name not in client_id_map:
        #         client_id = create_client(auth, workspace_id, client_name, req_access)
        #         # new_client_name = client_name # f'BC {client_name}'
        #         # client_id = replace_client(auth, workspace_id, old_name=client_name, new_name=new_client_name)
        #
        #         client_id_map[client_name] = client_id
        #     else:
        #         client_id = client_id_map[client_name]
        #
        #     # # colour_id = clients.loc[clients['Client Name']==client_name, 'Colour_id'].values[0]
        #
        #     create_project(auth, workspace_id, project_name, client_id, req_access) #, colour_id)
        #
        #     # # new_name = f'BC {project_name}'
        #     # # replace_project(auth, workspace_id, client_id, old_name=project_name, new_name=new_name)
        #
        #     # if project_name in replacement_project:
        #     #     old_name = project_name
        #     #     new_name = replacement_project[project_name]
        #     #     replace_project(auth, workspace_id, client_id, old_name, new_name, req_access)

        # delete_tags(auth, workspace_id, req_access, tags_to_delete)
        # delete_projects(auth, workspace_id, req_access, projects_to_delete)

        # fix_tag_list(auth, workspace_id, req_access, rep_fix.loc[rep_fix['user']==man])

        print("🚀 Создание отчета...")
        user_tags = get_tag_report(auth, workspace_id, req_access)
        user_tags['user'] = man
        tags_df_list.append(user_tags)

        user_projects = get_project_report(auth, workspace_id, req_access)
        user_projects['user'] = man
        projects_df_list.append(user_projects)

        client_projects = get_clients_report(auth, workspace_id, req_access)
        client_projects['user'] = man
        clients_df_list.append(client_projects)


        # delete_all_tags(auth, workspace_id)

        # personalized_tags[man] = ['AT: Internal-Admin']
        # personalized_tags[man].append('AT: Internal-Admin')

        # create_tags(auth, workspace_id, personalized_tags[man], req_access)
    tags_report = pd.concat(tags_df_list)
    projects_report = pd.concat(projects_df_list)
    clients_report = pd.concat(clients_df_list)

    with pd.ExcelWriter("report.xlsx") as writer:
        tags_report.to_excel(writer, sheet_name="tags_report", index=False)
        projects_report.to_excel(writer, sheet_name="projects_report", index=False)
        clients_report.to_excel(writer, sheet_name="clients_report", index=False)


# === Запуск всего процесса ===
if __name__ == "__main__":
    run(df, personalized_tags)
