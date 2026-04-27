import time
import datetime
import numpy as np
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth
import asyncio
import threading

# Get table
main_excel_path = r'./data'
tokens_path = r'./data'

df = pd.read_excel(f'{main_excel_path}/New tags and projects list_Toggl.xlsx', sheet_name='1.2-User-specific tags',
                   index_col='Activity type')
tags_format = pd.read_excel(f'{main_excel_path}/New tags and projects list_Toggl.xlsx', sheet_name='Tags - Format')
projects = pd.read_excel(f'{main_excel_path}/New tags and projects list_Toggl.xlsx', sheet_name='Projects')
clients = pd.read_excel(f'{main_excel_path}/New tags and projects list_Toggl.xlsx', sheet_name='Client Name')

clients.loc[clients['Client Name']=='Siemens-Bernhoven', 'Client Name'] = 'Bernhoven'

tokens = pd.read_excel(f'{tokens_path}/API Tokens.xlsx', sheet_name='API Token')

rep_tags_fix = pd.read_excel('./data/diff_tpc.xlsx', sheet_name='tags')
rep_projects_fix = pd.read_excel('./data/diff_tpc.xlsx', sheet_name='projects')
rep_clients_fix = pd.read_excel('./data/diff_tpc.xlsx', sheet_name='clients')
# rep_clients_fix = None

people = df.columns
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

auths = {}
for p in people:
    token = tokens.loc[tokens['Столбец1'] == p, 'API Token'].values[0]
    auths[p] = (token, "api_token")

personalized_tags = {}
for p in people:
    personalized_tags[p] = df.loc[df[p] == 1].index.to_list() + tags_format['Tags - Format'].to_list()

clients['key'] = 1
projects['key'] = 1
df_cross = pd.merge(clients, projects, how='left', on='key')
df_filtered = df_cross[df_cross.apply(
    lambda row: row['Client Name'] in row['Projects'], axis=1
)]

df_filtered = df_filtered.drop('key', axis=1)
df = pd.merge(clients.drop('key', axis=1), df_filtered, on='Client Name', how='left')
df.rename(columns={'Projects': 'project_name', 'Client Name': 'client_name'}, inplace=True)

df.loc[df['client_name']=='Bernhoven', 'client_name'] = 'Siemens-Bernhoven'

bernhoven = {'client_name': ['Alrijne'],
             'project_name': ['Alrijne-Tender Management']}
bernhoven_df = pd.DataFrame.from_dict(bernhoven)
df = pd.merge(df, bernhoven_df, on=['client_name', 'project_name'], how='outer')

tags_to_delete = []
projects_to_delete = []
clients_to_delete = []


class UserRequests:
    def __init__(self, user: str, auth, personalized_tags):
        self.df = df
        self.user = user
        self.auth = auth
        self.personalized_tags = personalized_tags
        self.req_counter = 0
        self.lock = threading.Lock()
        self.sleep_event = asyncio.Event()
        self.workspace_id = self.get_workspace_id()
        self.tags = None
        self.projects = None
        self.clients = None

    def wait(self):
        """Синхронный метод с асинхронным сном для одного объекта"""
        with self.lock:
            self.req_counter += 1
            if self.req_counter < 28:
                remaining = 30 - self.req_counter
                print(f"⏳ {self.user}: {remaining} requests left in this hour!!!")
                return True
            else:
                self.req_counter = 0
                print(f"😴 {self.user}: I am sleeping!!! {datetime.datetime.now().time()}")
                # Запускаем асинхронный сон в отдельном потоке
                sleep_thread = threading.Thread(target=self._async_sleep, daemon=True)
                sleep_thread.start()
                sleep_thread.join()  # Ждём, пока поток закончит сон
                print(f"👁️ {self.user}: I am awake! {datetime.datetime.now().time()}")
                return True

    def _async_sleep(self):
        """Запуск асинхронного сна в потоке"""
        try:
            asyncio.run(asyncio.sleep(60 * 61))
        except RuntimeError:
            # Если уже есть running loop, используем threading.Event
            time.sleep(60 * 61)

    def _get(self, url, params=None):
        self.wait()
        response = requests.get(url, auth=self.auth, params=params)
        response.raise_for_status()
        return response.json()

    def _post(self, url, data):
        self.wait()
        response = requests.post(url, json=data, auth=self.auth)
        response.raise_for_status()
        resp_json = response.json()
        print(f"✅ {self.user}: Created with ID {resp_json['id']}: {data}")
        return resp_json["id"]

    def _put(self, url, data):
        self.wait()
        response = requests.put(url, json=data, auth=self.auth)
        if response.status_code != 200:
            print(f"{self.user}: Updated text: {response.text}")
        # response.raise_for_status()
        print(f"✅ {self.user}: Updated: {data}")
        return True

    def _delete(self, url):
        self.wait()
        response = requests.delete(url, auth=self.auth)
        response.raise_for_status()
        if response.status_code == 200:
            print(f"✅ {self.user}: Deleted: {url}")
        else:
            print(f"❌ {self.user}: Error deleting: {url} Status: {response.status_code}")
        return True

    def get_workspace_id(self):
        print(f"📡 {self.user}: Retrieving workspace ID...")
        self.wait()
        response = requests.get("https://api.track.toggl.com/api/v9/me", auth=self.auth)
        if response.status_code != 200:
            print("❌ Error. Check your API token.")
            exit(1)
        data = response.json()
        workspace_id = data.get("default_workspace_id")
        print(f"✅ {self.user}: Workspace ID: {workspace_id}")
        return workspace_id

    def get_all_tags(self):
        url = f'https://api.track.toggl.com/api/v9/workspaces/{self.workspace_id}/tags'
        self.tags = self._get(url)
        return self.tags

    def get_all_projects(self):
        url = f"https://api.track.toggl.com/api/v9/workspaces/{self.workspace_id}/projects"
        self.projects = self._get(url)
        return self.projects

    def get_all_clients(self):
        url = f'https://api.track.toggl.com/api/v9/workspaces/{self.workspace_id}/clients'
        self.clients = self._get(url)
        return self.clients

    # ============ Projects ============ #
    def create_project(self, name, client_id):
        if self.projects is None:
            self.get_all_projects()
        for project in self.projects:
            if project["name"] == name:
                return project['id']
        if client_id is None or pd.isnull(name):
            return None
        url = f"https://api.track.toggl.com/api/v9/workspaces/{self.workspace_id}/projects"
        data = {
            "name": name,
            "client_id": client_id,
            "active": True,
            "is_private": True,
        }
        project_id = self._post(url, data)
        print(f"✅ {self.user}: Created project: {name} (for client ID {client_id})")
        return project_id

    def replace_project(self, old_name, new_name):
        if self.projects is None:
            self.get_all_projects()
        for project in self.projects:
            if project["name"] == old_name:
                url = f"https://api.track.toggl.com/api/v9/workspaces/{self.workspace_id}/projects/{project['id']}"
                self._put(url, {"name": new_name})
                print(f"✅ {self.user}: Changed project: {old_name} -> {new_name}")
                return project['id']
        print(f"❌ {self.user}: Project {old_name} not found.")
        return None

    def delete_project(self, name):
        if self.projects is None:
            self.get_all_projects()
        for project in self.projects:
            if project["name"] == name:
                url = f"https://api.track.toggl.com/api/v9/workspaces/{self.workspace_id}/projects/{project['id']}"
                self._delete(url)
                print(f"✅ {self.user}: Deleted project: {name}")
                return True
        print(f"❌ {self.user}: Project {name} not found.")
        return False

    def delete_all_projects(self):
        if self.projects is None:
            self.get_all_projects()
        for project in self.projects:
            url = f"https://api.track.toggl.com/api/v9/workspaces/{self.workspace_id}/projects/{project['id']}"
            self._delete(url)
            print(f"✅ {self.user}: Deleted project: {project['name']}")

    # ============ Clients ============ #
    def create_client(self, name):
        if self.clients is None:
            self.get_all_clients()
        for client in self.clients:
            if client["name"] == name:
                return client['id']
        url = f"https://api.track.toggl.com/api/v9/workspaces/{self.workspace_id}/clients"
        data = {"name": name}
        client_id = self._post(url, data)
        print(f"✅ {self.user}: Created client: {name}")
        return client_id

    def replace_client(self, old_name, new_name):
        if self.clients is None:
            self.get_all_clients()
        for client in self.clients:
            if client["name"] == old_name:
                url = f"https://api.track.toggl.com/api/v9/workspaces/{self.workspace_id}/clients/{client['id']}"
                self._put(url, {"name": new_name})
                print(f"✅ {self.user}: Updated client: {old_name} -> {new_name}")
                return client['id']
        print(f"❌ {self.user}: Client {old_name} not found.")
        return None

    def delete_client(self, name):
        if self.clients is None:
            self.get_all_clients()
        for client in self.clients:
            if client["name"] == name:
                url = f"https://api.track.toggl.com/api/v9/workspaces/{self.workspace_id}/clients/{client['id']}"
                self._delete(url)
                print(f"✅ {self.user}: Deleted client: {name}")
                return True
        print(f"❌ {self.user}: Client {name} not found.")
        return False

    def delete_all_clients(self):
        if self.clients is None:
            self.get_all_clients()
        for client in self.clients:
            url = f"https://api.track.toggl.com/api/v9/workspaces/{self.workspace_id}/clients/{client['id']}"
            self._delete(url)
            print(f"✅ {self.user}: Deleted client: {client['name']}")

    # ============ Tags ============ #
    def create_tag(self, name):
        if self.tags is None:
            self.get_all_tags()
        for tag in self.tags:
            if tag["name"] == name:
                return tag['id']
        url = f"https://api.track.toggl.com/api/v9/workspaces/{self.workspace_id}/tags"
        data = {"name": name}
        tag_id = self._post(url, data)
        print(f"✅ {self.user}: Created tag: {name}")
        return tag_id

    def replace_tag(self, old_name, new_name):
        if self.tags is None:
            self.get_all_tags()
        for tag in self.tags:
            if tag["name"] == old_name:
                url = f"https://api.track.toggl.com/api/v9/workspaces/{self.workspace_id}/tags/{tag['id']}"
                self._put(url, {"name": new_name})
                print(f"✅ {self.user}: Updated tag: {old_name} -> {new_name}")
                return tag['id']
        print(f"❌ {self.user}: Tag {old_name} not found.")
        return None

    def delete_tag(self, name):
        if self.tags is None:
            self.get_all_tags()
        for tag in self.tags:
            if tag["name"] == name:
                url = f"https://api.track.toggl.com/api/v9/workspaces/{self.workspace_id}/tags/{tag['id']}"
                self._delete(url)
                print(f"✅ {self.user}: Deleted tag: {name}")
                return True
        print(f"❌ {self.user}: Tag {name} not found.")
        return False

    def delete_all_tags(self):
        if self.tags is None:
            self.get_all_tags()
        for tag in self.tags:
            url = f"https://api.track.toggl.com/api/v9/workspaces/{self.workspace_id}/tags/{tag['id']}"
            self._delete(url)
            print(f"✅ {self.user}: Deleted tag: {tag['name']}")

    # ============ Reports ============ #
    def get_tag_report(self):
        url = f"https://api.track.toggl.com/api/v9/workspaces/{self.workspace_id}/tags"
        tags = self._get(url)
        return pd.DataFrame(tags)

    def get_project_report(self):
        url = f"https://api.track.toggl.com/api/v9/workspaces/{self.workspace_id}/projects"
        projects = self._get(url)
        return pd.DataFrame(projects)

    def get_clients_report(self):
        url = f"https://api.track.toggl.com/api/v9/workspaces/{self.workspace_id}/clients"
        clients = self._get(url)
        return pd.DataFrame(clients)

    # ============ Fix utils ============ #
    def fix_tag_list(self, rep_fix):
        add_tags = rep_fix.loc[rep_fix['doing'] == 'add', 'name'].tolist()
        for tag in add_tags:
            self.create_tag(tag)
        replace_tags = rep_fix.loc[rep_fix['doing'] == 'replace', ['name', 'right_variant']].set_index('name')[
            'right_variant'].to_dict()
        for tag in replace_tags:
            self.replace_tag(old_name=tag, new_name=replace_tags[tag])
        del_tags = rep_fix.loc[rep_fix['doing'] == 'delete', 'name'].tolist()
        for tag in del_tags:
            self.delete_tag(tag)

    def fix_project_list(self, rep_fix):
        add_projects = rep_fix.loc[rep_fix['doing'] == 'add', 'name'].tolist()
        for project in add_projects:
            try:
                client_name = self.df.loc[self.df['project_name'] == project, 'client_name'].tolist()[0]
            except IndexError:
                print(f'❌ {self.user}: Client for project "{project}" not found.')
                continue
            client_id = None
            for client in self.clients:
                if client['name'] == client_name:
                    client_id = client['id']
            # if client_id == 214170253 or client_id == 213159504 or client_id == None:
            #     print(f'\n\nBEFORE ERROR {self.user}: {client_name}')
            #     pass
            #     continue
            if client_id is None:
                print(f"❌ {self.user}: Client {client_name} not found.")
                continue
            self.create_project(project, client_id)
        replace_projects = rep_fix.loc[rep_fix['doing'] == 'replace', ['name', 'right_variant']].set_index('name')[
            'right_variant'].to_dict()
        for project in replace_projects:
            self.replace_project(old_name=project, new_name=replace_projects[project])
        del_projects = rep_fix.loc[rep_fix['doing'] == 'delete', 'name'].tolist()
        for project in del_projects:
            self.delete_project(project)

    def fix_client_list(self, rep_fix):
        add_clients = rep_fix.loc[rep_fix['doing'] == 'add', 'name'].tolist()
        for client in add_clients:
            self.create_client(client)
        replace_clients = rep_fix.loc[rep_fix['doing'] == 'replace', ['name', 'right_variant']].set_index('name')[
            'right_variant'].to_dict()
        for client in replace_clients:
            self.replace_client(old_name=client, new_name=replace_clients[client])
        del_clients = rep_fix.loc[rep_fix['doing'] == 'delete', 'name'].tolist()
        for client in del_clients:
            self.delete_client(client)


# ============ main script ============ #
def run(df, personalized_tags=personalized_tags):
    tags_df_list = []
    projects_df_list = []
    clients_df_list = []

    users = []
    for man in people:
        print(f'############################ Starting {man} ############################')
        user = UserRequests(user=man,
                            auth=auths[man],
                            personalized_tags=personalized_tags[man])
        users.append(user)

    # Создаём потоки для каждого пользователя
    threads = []
    for user in users:
        cl_fix = rep_clients_fix.loc[rep_clients_fix['user']==user.user]
        tg_fix = rep_tags_fix.loc[rep_tags_fix['user']==user.user]
        pr_fix = rep_projects_fix.loc[rep_projects_fix['user']==user.user]
        pass
        # cl_fix = None


        thread = threading.Thread(target=lambda u=user: process_user(u,
                                                                     rep_clients_fix=cl_fix,
                                                                     rep_tags_fix=tg_fix,
                                                                     rep_projects_fix=pr_fix))
        threads.append(thread)
        thread.start()
        threads.append(thread)

    # Ждём завершения всех потоков
    for thread in threads:
        thread.join()

    print("✅ All users processed!")


def process_user(user, rep_clients_fix, rep_tags_fix, rep_projects_fix):
    """Обработка пользователя в отдельном потоке"""
    try:
        # fix clients
        user.get_all_clients()
        user.fix_client_list(rep_clients_fix)
        # fix projects
        user.get_all_projects()
        user.fix_project_list(rep_projects_fix)
        # fix tags
        # user.get_all_tags()
        # user.fix_tag_list(rep_tags_fix)

        print(f"✅ {user.user}: Completed!")
    except Exception as e:
        print(f"❌ {user.user}: Error - {e}")


if __name__ == "__main__":
    run(df, personalized_tags)
