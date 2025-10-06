import time

import numpy as np
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth

# Get table
df = pd.read_excel('./New tags and projects list_Toggl.xlsx', sheet_name='1.2-User-specific tags', index_col='Activity type')
tags_format = pd.read_excel('./New tags and projects list_Toggl.xlsx', sheet_name='Tags - Format')
projects = pd.read_excel('./New tags and projects list_Toggl.xlsx', sheet_name='Projects')
clients = pd.read_excel('./New tags and projects list_Toggl.xlsx', sheet_name='Client Name')
tokens = pd.read_excel('./New tags and projects list_Toggl.xlsx', sheet_name='Toggle tokens')

people = df.columns
# people = people[:-1]
# people = ['BADA']
# people = ['BADA'] #, 'SMVE']
people = [
    # 'BADA', # \/
    # 'AIVI', # - # \/
    # 'BODM', # \/
    # 'CHAL', # \/
    # 'DIDA', # - # \/
    # 'KURO', # \/
    # 'AMAN', # \/
    # 'NIRO', # \/
    # 'PRAR', # \/
    # 'SMVE', # \/
    # 'TODA', # \/
    # 'VAEL', # \/
    # 'ANAS', # \/
    # 'NIAL', # \/
]

class Requests:
    def __init__(self):
        self.req_number = 0

    def wait(self):
        self.req_number += 1
        if self.req_number < 29:
            return True
        else:
            self.req_number = 0
            print('I am sleeping!!!')
            time.sleep(60*61)
            return True



auths = {}
for p in people:
    token = tokens.loc[tokens['Name'] == p, 'Token'].values[0]
    auths[p] = (token, "api_token")

personalized_tags = {}
for p in people:
    tags = [
        'AT: Business trip',
        'AT: Presale',
        'AT: Travel Support',
    ]
    personalized_tags[p] = df.loc[df[p] == 1].index.to_list() + tags_format['Tags - Format'].to_list() + tags



    # if p == 'ANAS':
    #     tags = [
    #         "AT: Assessment on site",
    #         "AT: Bank operations",
    #         "AT: Benchmark-Book",
    #         "AT: Business requirements",
    #         "AT: Business trip",
    #         "AT: Client's data handling",
    #         "AT: Commercialization",
    #         "AT: Contract-Heatmap",
    #         "AT: Design",
    #         "AT: HR-management",
    #         "AT: HR-recruiting",
    #         "AT: Internal-Admin",
    #         "AT: Lab-Efficiency-Workshop",
    #         "AT: Lab-Flow",
    #         "AT: Lab-Horizontals",
    #         "AT: Lab-Modeling",
    #         "AT: Make-up",
    #         "AT: Methodology",
    #         "AT: ML",
    #         "AT: Presale",
    #         "AT: Presentations",
    #         "AT: Project-Management",
    #         "AT: Recruiting",
    #         "AT: Reports",
    #         "AT: Scientific research",
    #         "AT: Sorting Logic",
    #         "AT: TPC",
    #         "AT: Travel Support",
    #         "AT: Tutorship",
    #         "AT: Validation",
    #         "AT: Weekly meeting",
    #         "AT: N / A",
    #     ]
    # elif p == 'NIAL':
    #     tags = [
    #         "AT: Bank operations",
    #         "AT: Commercialization",
    #         "AT: HR-management",
    #         "AT: HR-recruiting",
    #         "AT: Internal-Admin",
    #         "AT: Internal-reports",
    #         "AT: Invoicing",
    #         "AT: Make-up",
    #         "AT: Methodology",
    #         "AT: Office maintenance",
    #         "AT: Pre-Invoicing",
    #         "AT: Presale",
    #         "AT: Presentations",
    #         "AT: Project-Management",
    #         "AT: Recruiting",
    #         "AT: Travel Support",
    #         "AT: Validation",
    #         "AT: Weekly meeting",
    #         "AT: N/A",
    #     ]
    # else:
    #     tags = []
    #
    # personalized_tags[p] = tags

clients['key'] = 1
projects['key'] = 1
df_cross = pd.merge(clients, projects, how='left', on='key')
df_filtered = df_cross[df_cross.apply(
    lambda row: row['Client Name'] in row['Projects'], axis=1
)]
df_filtered = df_filtered.drop('key', axis=1)
df = pd.merge(clients.drop('key', axis=1), df_filtered, on='Client Name', how='left')



df.rename(columns={'Projects': 'project_name', 'Client Name': 'client_name'}, inplace=True)

bernhoven = {'client_name': ['Siemens-Bernhoven', 'Siemens-Bernhoven', 'Siemens-Bernhoven', 'Siemens-Bernhoven'],
             'project_name': ['Bernhoven-Assessment', 'Bernhoven-Lab-Avatar', 'Bernhoven-Lab-Calculator', 'Bernhoven-Transformation']}
bernhoven_df = pd.DataFrame.from_dict(bernhoven)
df = pd.merge(df, bernhoven_df, on=['client_name', 'project_name'], how='outer')

c_k = {'client_name': ['Cork&Kerry', 'Cork&Kerry'],
             'project_name': ['Cork&Kerry Lab-Avatar', 'Cork&Kerry BI']}
c_k_df = pd.DataFrame.from_dict(c_k)
df = pd.merge(df, c_k_df, on=['client_name', 'project_name'], how='outer')

bc_swlp = {'client_name': ['BC SWLP'],
             'project_name': ['BC SWLP-BI']}
bc_swlp_df = pd.DataFrame.from_dict(bc_swlp)
df = pd.merge(df, bc_swlp_df, on=['client_name', 'project_name'], how='outer')







# bernhoven = {'client_name': ['Potential Client'],
#              'project_name': ['Potential Client-Project']}
# bernhoven_df = pd.DataFrame.from_dict(bernhoven)
# df = pd.merge(df, bernhoven_df, on=['client_name', 'project_name'], how='outer')
#
# df = df.loc[(df['client_name']=='Potential Client') & (df['project_name']=='Potential Client-Project')]






# df = df.loc[df['client_name']=='Siemens-Bernhoven']
# df = df.loc[(df['client_name']=='BC SWLP') & (df['project_name']=='BC SWLP-BI')]

pass

# === Удаление всех проектов ===
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

# === Удаление всех клиентов ===
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

# === Создание клиента ===
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
    # resp.raise_for_status()


# === Создание клиента ===
def replace_client(auth, workspace_id, old_name, new_name, req_access):
    # Check if it is already done
    if req_access.wait():
        pass
    url = f'https://api.track.toggl.com/api/v9/workspaces/{workspace_id}/clients'
    resp = requests.get(url, auth=auth)
    resp_j = resp.json()
    for client in resp_j:
        if client["name"] == old_name:
            url = f'https://api.track.toggl.com/api/v9/workspaces/{workspace_id}/clients/{client['id']}'
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


# === Создание проекта ===
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


# === Создание проекта ===
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

# === Создание новых тегов из списка ===
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
            print(f"❌ Ошибка при создании тэга {tag_name}: {resp.status_code}")
    return created_tags

# === Основной запуск ===
def run(df, personalized_tags:dict[list]=personalized_tags):
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

        for _, row in df.iterrows():
            client_name = row["client_name"]
            project_name = row["project_name"]

            # if client_name in ['Abbott', 'Alrijne', 'BC', 'Certe', 'Cork&Kerry']:
            #     continue

            if client_name not in client_id_map:
                client_id = create_client(auth, workspace_id, client_name, req_access)
                # new_client_name = client_name # f'BC {client_name}'
                # client_id = replace_client(auth, workspace_id, old_name=client_name, new_name=new_client_name)

                client_id_map[client_name] = client_id
            else:
                client_id = client_id_map[client_name]

            # colour_id = clients.loc[clients['Client Name']==client_name, 'Colour_id'].values[0]
            create_project(auth, workspace_id, project_name, client_id, req_access) #, colour_id)
            # new_name = f'BC {project_name}'
            # replace_project(auth, workspace_id, client_id, old_name=project_name, new_name=new_name)



        # delete_all_tags(auth, workspace_id)

        # personalized_tags[man] = ['AT: Internal-Admin']
        # personalized_tags[man].append('AT: Internal-Admin')

        create_tags(auth, workspace_id, personalized_tags[man], req_access)


# === Запуск всего процесса ===
if __name__ == "__main__":
    run(df, personalized_tags)
