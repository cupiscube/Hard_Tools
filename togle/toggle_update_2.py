import time
import datetime

import numpy as np
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth

import asyncio
import aiohttp



# Get table
main_excel_path = r'C:/Users/DanilBatrakov/Gontard & CIE/Commercial Projects - 2. Time reports'
tokens_path = r'C:/Users/DanilBatrakov/Gontard & CIE/Commercial Projects - 2. Time reports/API Token'

df = pd.read_excel(f'{main_excel_path}/New tags and projects list_Toggl.xlsx', sheet_name='1.2-User-specific tags', index_col='Activity type')
tags_format = pd.read_excel(f'{main_excel_path}/New tags and projects list_Toggl.xlsx', sheet_name='Tags - Format')
projects = pd.read_excel(f'{main_excel_path}/New tags and projects list_Toggl.xlsx', sheet_name='Projects')
clients = pd.read_excel(f'{main_excel_path}/New tags and projects list_Toggl.xlsx', sheet_name='Client Name')

tokens = pd.read_excel(f'{tokens_path}/API Tokens.xlsx', sheet_name='API Token')

rep_tags_fix = pd.read_excel('./diff_tpc.xlsx', sheet_name='tags')
rep_projects_fix = pd.read_excel('./diff_tpc.xlsx', sheet_name='projects')
rep_clients_fix = pd.read_excel('./diff_tpc.xlsx', sheet_name='clients')

people = df.columns
people = [
    'BADA', # \/
    # 'AIVI', # \/
    # 'BODM', # \/
    # 'CHAL', # \/
    # 'DIDA', # \/
    # 'KURO', # \/
    # 'AMAN', # \/
    # 'NIRO', # \/
    # 'PRAR', # \/
    # 'SMVE', # \/
    # 'TODA', # \/
    # 'VAEL', # \/
    # 'ANAS', # \/
    # 'NIAL', # \/
    # 'KAAN', # \/
    # 'LAOK', # \/
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

tags_to_delete = []
projects_to_delete = []
clients_to_delete = []


class UserRequests:
    def __init__(self, user: str, auth, personalized_tags):
        self.user = user
        self.auth = auth
        self.personalized_tags = personalized_tags
        self.req_counter = 0
        self.req_lock = asyncio.Lock()
        self.session = aiohttp.ClientSession()
        self.workspace_id = self.get_workspace_id()
        self.tags = None
        self.projects = None
        self.clients = None

    async def close(self):
        await self.session.close()

    # Shared wait method for rate limiting
    async def wait(self):
        async with self.req_lock:
            self.req_counter += 1
            if self.req_counter < 29:
                print(f"{30 - self.req_counter} requests left in this hour!!!")
                return True
            else:
                self.req_counter = 0
                print(f"I am sleeping!!! {datetime.datetime.now().time()}")
                await asyncio.sleep(60 * 61)
                return True

    async def _get(self, url, params=None):
        await self.wait()
        async with self.session.get(url, auth=self.auth, params=params) as response:
            response.raise_for_status()
            return await response.json()

    async def _post(self, url, data):
        await self.wait()
        async with self.session.post(url, json=data, auth=self.auth) as response:
            response.raise_for_status()
            resp_json = await response.json()
            print(f"✅ {self.user}: Created with ID {resp_json['id']}: {data}")
            return resp_json["id"]

    async def _put(self, url, data):
        await self.wait()
        async with self.session.put(url, json=data, auth=self.auth) as response:
            response.raise_for_status()
            print(f"✅ {self.user}: Updated: {data}")
            return True

    async def _delete(self, url):
        await self.wait()
        async with self.session.delete(url, auth=self.auth) as response:
            response.raise_for_status()
            if response.status == 200:
                print(f"✅ {self.user}: Deleted: {url}")
            else:
                print(f"❌ {self.user}: Error deleting: {url} Status: {response.status}")
            return True

    async def get_workspace_id(self):
        print("📡 Retrieving workspace ID...")
        await self.wait()
        async with self.session.get("https://api.track.toggl.com/api/v9/me", auth=self.auth) as response:
            if response.status != 200:
                print("❌ Error. Check your API token.")
                exit(1)
            data = await response.json()
            self.workspace_id = data.get("default_workspace_id")
            print(f"✅ {self.user}: Workspace ID: {self.workspace_id}")
            return self.workspace_id

    async def get_all_tags(self):
        url = f'https://api.track.toggl.com/api/v9/workspaces/{self.workspace_id}/tags'
        self.tags = await self._get(url)
        return self.tags

    async def get_all_projects(self):
        url = f"https://api.track.toggl.com/api/v9/workspaces/{self.workspace_id}/projects"
        self.projects = await self._get(url)
        return self.projects

    async def get_all_clients(self):
        url = f'https://api.track.toggl.com/api/v9/workspaces/{self.workspace_id}/clients'
        self.clients = await self._get(url)
        return self.clients

    # ============ Projects ============ #
    async def create_project(self, name, client_id):
        if self.projects is None:
            await self.get_all_projects()
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
        project_id = await self._post(url, data)
        print(f"✅ Created project: {name} (for client ID {client_id})")
        return project_id

    async def replace_project(self, old_name, new_name):
        if self.projects is None:
            await self.get_all_projects()
        for project in self.projects:
            if project["name"] == old_name:
                url = f"https://api.track.toggl.com/api/v9/workspaces/{self.workspace_id}/projects/{project['id']}"
                await self._put(url, {"name": new_name})
                print(f"✅ {self.user}: Changed project: {old_name} -> {new_name}")
                return project['id']
        print(f"❌ {self.user}: Project {old_name} not found.")
        return None

    async def delete_project(self, name):
        if self.projects is None:
            await self.get_all_projects()
        for project in self.projects:
            if project["name"] == name:
                url = f"https://api.track.toggl.com/api/v9/workspaces/{self.workspace_id}/projects/{project['id']}"
                await self._delete(url)
                print(f"✅ {self.user}: Deleted project: {name}")
                return True
        print(f"❌ {self.user}: Project {name} not found.")
        return False

    async def delete_all_projects(self):
        if self.projects is None:
            await self.get_all_projects()
        for project in self.projects:
            url = f"https://api.track.toggl.com/api/v9/workspaces/{self.workspace_id}/projects/{project['id']}"
            await self._delete(url)
            print(f"✅ {self.user}: Deleted project: {project['name']}")

    # ============ Clients ============ #
    async def create_client(self, name):
        if self.clients is None:
            await self.get_all_clients()
        for client in self.clients:
            if client["name"] == name:
                return client['id']
        url = f"https://api.track.toggl.com/api/v9/workspaces/{self.workspace_id}/clients"
        data = {"name": name}
        client_id = await self._post(url, data)
        print(f"✅ {self.user}: Created client: {name}")
        return client_id

    async def replace_client(self, old_name, new_name):
        if self.clients is None:
            await self.get_all_clients()
        for client in self.clients:
            if client["name"] == old_name:
                url = f"https://api.track.toggl.com/api/v9/workspaces/{self.workspace_id}/clients/{client['id']}"
                await self._put(url, {"name": new_name})
                print(f"✅ {self.user}: Updated client: {old_name} -> {new_name}")
                return client['id']
        print(f"❌ {self.user}: Client {old_name} not found.")
        return None

    async def delete_client(self, name):
        if self.clients is None:
            await self.get_all_clients()
        for client in self.clients:
            if client["name"] == name:
                url = f"https://api.track.toggl.com/api/v9/workspaces/{self.workspace_id}/clients/{client['id']}"
                await self._delete(url)
                print(f"✅ {self.user}: Deleted client: {name}")
                return True
        print(f"❌ {self.user}: Client {name} not found.")
        return False

    async def delete_all_clients(self):
        if self.clients is None:
            await self.get_all_clients()
        for client in self.clients:
            url = f"https://api.track.toggl.com/api/v9/workspaces/{self.workspace_id}/clients/{client['id']}"
            await self._delete(url)
            print(f"✅ {self.user}: Deleted client: {client['name']}")

    # ============ Tags ============ #
    async def create_tag(self, name):
        if self.tags is None:
            await self.get_all_tags()
        for tag in self.tags:
            if tag["name"] == name:
                return tag['id']
        url = f"https://api.track.toggl.com/api/v9/workspaces/{self.workspace_id}/tags"
        data = {"name": name}
        tag_id = await self._post(url, data)
        print(f"✅ {self.user}: Created tag: {name}")
        return tag_id

    async def replace_tag(self, old_name, new_name):
        if self.tags is None:
            await self.get_all_tags()
        for tag in self.tags:
            if tag["name"] == old_name:
                url = f"https://api.track.toggl.com/api/v9/workspaces/{self.workspace_id}/tags/{tag['id']}"
                await self._put(url, {"name": new_name})
                print(f"✅ {self.user}: Updated tag: {old_name} -> {new_name}")
                return tag['id']
        print(f"❌ Tag {old_name} not found.")
        return None

    async def delete_tag(self, name):
        if self.tags is None:
            await self.get_all_tags()
        for tag in self.tags:
            if tag["name"] == name:
                url = f"https://api.track.toggl.com/api/v9/workspaces/{self.workspace_id}/tags/{tag['id']}"
                await self._delete(url)
                print(f"✅ {self.user}: Deleted tag: {name}")
                return True
        print(f"❌ Tag {name} not found.")
        return False

    async def delete_all_tags(self):
        if self.tags is None:
            await self.get_all_tags()
        for tag in self.tags:
            url = f"https://api.track.toggl.com/api/v9/workspaces/{self.workspace_id}/tags/{tag['id']}"
            await self._delete(url)
            print(f"✅ {self.user}: Deleted tag: {tag['name']}")

    # ============ Reports ============ #
    async def get_tag_report(self):
        url = f"https://api.track.toggl.com/api/v9/workspaces/{self.workspace_id}/tags"
        tags = await self._get(url)
        return pd.DataFrame(tags)

    async def get_project_report(self):
        url = f"https://api.track.toggl.com/api/v9/workspaces/{self.workspace_id}/projects"
        projects = await self._get(url)
        return pd.DataFrame(projects)

    async def get_clients_report(self):
        url = f"https://api.track.toggl.com/api/v9/workspaces/{self.workspace_id}/clients"
        clients = await self._get(url)
        return pd.DataFrame(clients)


    # ============ Fix utils ============ #
    async def fix_tag_list(self, rep_fix):
        add_tags = rep_fix.loc[rep_fix['doing'] == 'add', 'name'].tolist()
        for tag in add_tags:
            await self.create_tag(tag)
        replace_tags = rep_fix.loc[rep_fix['doing'] == 'replace', ['name', 'right_variant']].set_index('name')['right_variant'].to_dict()
        for tag in replace_tags:
            await self.replace_tag(old_name=tag, new_name=replace_tags[tag])
        del_tags = rep_fix.loc[rep_fix['doing'] == 'delete', 'name'].tolist()
        for tag in del_tags:
            await self.delete_tag(tag)

    async def fix_project_list(self, rep_fix):
        add_projects = rep_fix.loc[rep_fix['doing'] == 'add', 'name'].tolist()
        for project in add_projects:
            client_name = df.loc[df['project_name'] == project['name'], 'client_id'].tolist()[0]
            client_id = None
            for client in self.clients:
                if client['name'] == client_name:
                    client_id = client['id']
            if client_id is None:
                print(f"❌ {self.user}: Client {client_name} not found.")
                continue
            await self.create_project(project, client_id)
        replace_projects = rep_fix.loc[rep_fix['doing'] == 'replace', ['name', 'right_variant']].set_index('name')[
            'right_variant'].to_dict()
        for project in replace_projects:
            await self.replace_project(old_name=project, new_name=replace_projects[project])
        del_projects = rep_fix.loc[rep_fix['doing'] == 'delete', 'name'].tolist()
        for project in del_projects:
            await self.delete_project(project)

    async def fix_client_list(self, rep_fix):
        add_clients = rep_fix.loc[rep_fix['doing'] == 'add', 'name'].tolist()
        for client in add_clients:
            await self.create_client(client)
        replace_clients = rep_fix.loc[rep_fix['doing'] == 'replace', ['name', 'right_variant']].set_index('name')[
            'right_variant'].to_dict()
        for client in replace_clients:
            await self.replace_client(old_name=client, new_name=replace_clients[client])
        del_clients = rep_fix.loc[rep_fix['doing'] == 'delete', 'name'].tolist()
        for client in del_clients:
            await self.delete_tag(client)




# ============ main script ============ #
async def run(df, personalized_tags:dict[list]=personalized_tags):
    tags_df_list = []
    projects_df_list = []
    clients_df_list = []
    for man in people:
        print(f'############################ Приступаю к {man} ############################')
        user = UserRequests(user=man,
                            auth=auths[man],
                            personalized_tags=personalized_tags[man])

        pass

        # await user.get_all_tags()
        # await user.get_all_projects()
        await user.get_all_clients()

        await user.fix_client_list(rep_clients_fix)
        # await user.fix_project_list(rep_projects_fix)
        # await user.fix_tag_list(rep_tags_fix)

    #     print("🚀 Create report...")
    #     user_tags = user.get_tag_report(auth, workspace_id, req_access)
    #     user_tags['user'] = man
    #     tags_df_list.append(user_tags)
    #
    #     user_projects = user.get_project_report(auth, workspace_id, req_access)
    #     user_projects['user'] = man
    #     projects_df_list.append(user_projects)
    #
    #     client_projects = user.get_clients_report(auth, workspace_id, req_access)
    #     client_projects['user'] = man
    #     clients_df_list.append(client_projects)
    #
    #
    # tags_report = pd.concat(tags_df_list)
    # projects_report = pd.concat(projects_df_list)
    # clients_report = pd.concat(clients_df_list)
    #
    # with pd.ExcelWriter("report.xlsx") as writer:
    #     tags_report.to_excel(writer, sheet_name="tags_report", index=False)
    #     projects_report.to_excel(writer, sheet_name="projects_report", index=False)
    #     clients_report.to_excel(writer, sheet_name="clients_report", index=False)

if __name__ == "__main__":
    asyncio.run(run(df, personalized_tags))
