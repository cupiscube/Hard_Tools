"""
Script-3 · Пуш изменений в Toggl по diff_tpc.xlsx

Единственный источник истины — diff_tpc.xlsx (выход Script-2), листы:
    tags | projects | clients,  колонки: user | name | doing | right_variant
    doing ∈ {add, replace, delete}

Целевой Excel («New tags and projects list_Toggl.xlsx») здесь больше НЕ читается:
персонализированные теги, кросс-джойн клиент×проект и хардкоды Bernhoven убраны.
Если лист персонализированных тегов вернётся — эта логика живёт в Script-2,
скрипт-пушер её знать не должен.

Из внешних файлов нужны только два:
    diff_tpc.xlsx    — что делать
    API Tokens.xlsx  — чем делать (лист 'API Token': Abbreviation | API Token)
"""

import datetime
import itertools
import threading
import time

import pandas as pd
import requests

# ============ config ============ #
DATA_DIR    = r'./togle/data'
DIFF_PATH   = f'{DATA_DIR}/diff_tpc.xlsx'
TOKENS_PATH = f'{DATA_DIR}/API Tokens.xlsx'

# None -> все пользователи, которые встречаются в diff_tpc.xlsx.
# Список -> только они (например ['GOBE']), даже если в diff есть другие.
ONLY_USERS = None

# True -> ничего не пишем в Toggl, только печатаем план. Прогони так хотя бы раз.
DRY_RUN = False

# Порядок действий внутри пользователя. Важен:
#   клиентов создаём ДО проектов (иначе проекту некуда прицепиться),
#   проекты удаляем ДО клиентов (иначе останутся проекты без клиента).
PHASES = (
    ('clients',  ('add', 'replace')),
    ('projects', ('add', 'replace', 'delete')),
    ('clients',  ('delete',)),
    ('tags',     ('add', 'replace', 'delete')),
)

# Лимит запросов Toggl API: после REQ_LIMIT запросов спим SLEEP_SECONDS.
REQ_LIMIT     = 28
SLEEP_SECONDS = 60 * 61

TOGGL_API = 'https://api.track.toggl.com/api/v9'

# Пишем в один поток вывода из нескольких потоков — без замка строки рвутся.
_PRINT_LOCK = threading.Lock()
_DRY_IDS = itertools.count(1)


def log(msg):
    with _PRINT_LOCK:
        print(msg, flush=True)


# ============ входные данные ============ #
def load_diff(path=None):
    """Три листа diff'а. Пустые name отбрасываем, doing нормализуем."""
    path = path or DIFF_PATH
    sheets = {}
    for sheet in ('tags', 'projects', 'clients'):
        df = pd.read_excel(path, sheet_name=sheet)
        missing = {'user', 'name', 'doing', 'right_variant'} - set(df.columns)
        if missing:
            raise KeyError(f'{path}[{sheet}]: нет колонок {sorted(missing)}')
        df = df.dropna(subset=['user', 'name']).copy()
        df['doing'] = df['doing'].astype(str).str.strip().str.lower()
        bad = sorted(set(df['doing']) - {'add', 'replace', 'delete'})
        if bad:
            raise ValueError(f'{path}[{sheet}]: неизвестные значения doing: {bad}')
        sheets[sheet] = df
    return sheets


def load_tokens(users, path=None):
    """{user: (token, 'api_token')}. Пользователей без токена пропускаем с предупреждением."""
    path = path or TOKENS_PATH
    tokens = pd.read_excel(path, sheet_name='API Token')
    auths = {}
    for u in users:
        row = tokens.loc[tokens['Abbreviation'] == u, 'API Token']
        if row.empty or pd.isna(row.values[0]):
            log(f'⚠ {u}: нет API-токена в {path} — пользователь пропущен')
            continue
        auths[u] = (row.values[0], 'api_token')
    return auths


def client_of(project_name):
    """Клиент выводится из имени проекта: 'Regiolab: Lab-Data' -> 'Regiolab'.

    Раньше связка project->client бралась из кросс-джойна целевого Excel.
    Теперь единственный источник — сам diff, а соглашение об именовании
    'Client: Suffix' то же, что использует Script-2.
    """
    name = str(project_name)
    if ':' not in name:
        return None
    return name.split(':', 1)[0].strip() or None


# ============ работа с Toggl ============ #
class UserRequests:
    def __init__(self, user, auth):
        self.user = user
        self.auth = auth
        self.req_counter = 0
        self.lock = threading.Lock()
        self.tags = None
        self.projects = None
        self.clients = None
        self.stats = {'add': 0, 'replace': 0, 'delete': 0, 'skipped': 0, 'failed': 0}
        self.workspace_id = self.get_workspace_id()

    # ---- rate limit ----
    def wait(self):
        with self.lock:
            self.req_counter += 1
            if self.req_counter < REQ_LIMIT:
                log(f'⏳ {self.user}: {REQ_LIMIT - self.req_counter} requests left in this window')
                return
            self.req_counter = 0
            log(f'😴 {self.user}: sleeping until quota resets... {datetime.datetime.now().time()}')
            time.sleep(SLEEP_SECONDS)
            log(f'👁️ {self.user}: awake! {datetime.datetime.now().time()}')

    # ---- HTTP ----
    def _get(self, url, params=None):
        self.wait()
        r = requests.get(url, auth=self.auth, params=params)
        r.raise_for_status()
        return r.json()

    def _post(self, url, data):
        if DRY_RUN:
            log(f'🟡 {self.user}: [DRY-RUN] POST {url} {data}')
            return f'DRY-{next(_DRY_IDS)}'   # синтетический id, чтобы связки в кэше не рвались
        self.wait()
        r = requests.post(url, json=data, auth=self.auth)
        r.raise_for_status()
        return r.json()['id']

    def _put(self, url, data):
        if DRY_RUN:
            log(f'🟡 {self.user}: [DRY-RUN] PUT {url} {data}')
            return True
        self.wait()
        r = requests.put(url, json=data, auth=self.auth)
        if r.status_code != 200:
            log(f'❌ {self.user}: PUT {r.status_code}: {r.text}')
            return False
        return True

    def _delete(self, url):
        if DRY_RUN:
            log(f'🟡 {self.user}: [DRY-RUN] DELETE {url}')
            return True
        self.wait()
        r = requests.delete(url, auth=self.auth)
        r.raise_for_status()
        return True

    def get_workspace_id(self):
        log(f'📡 {self.user}: retrieving workspace ID...')
        data = self._get(f'{TOGGL_API}/me')
        ws = data.get('default_workspace_id')
        if not ws:
            raise RuntimeError(f'{self.user}: не удалось получить default_workspace_id')
        log(f'✅ {self.user}: workspace ID {ws}')
        return ws

    # ---- кэши состояния ----
    # Кэш обновляется при каждом create/replace/delete: иначе клиент, созданный
    # в этом же прогоне, не находится при создании проекта (именно на этом
    # спотыкался прежний скрипт — новые клиенты из add попадали в
    # "Client ... not found", и все их проекты не создавались).
    def get_all_tags(self):
        self.tags = self._get(f'{TOGGL_API}/workspaces/{self.workspace_id}/tags') or []
        return self.tags

    def get_all_projects(self):
        self.projects = self._get(f'{TOGGL_API}/workspaces/{self.workspace_id}/projects') or []
        return self.projects

    def get_all_clients(self):
        self.clients = self._get(f'{TOGGL_API}/workspaces/{self.workspace_id}/clients') or []
        return self.clients

    @staticmethod
    def _find(items, name):
        for it in items:
            if it['name'] == name:
                return it
        return None

    # ============ Tags ============ #
    def create_tag(self, name, _right=None):
        if self.tags is None:
            self.get_all_tags()
        if self._find(self.tags, name):
            log(f'➖ {self.user}: tag already exists: {name}')
            return 'skipped'
        tag_id = self._post(f'{TOGGL_API}/workspaces/{self.workspace_id}/tags', {'name': name})
        self.tags.append({'id': tag_id, 'name': name})
        log(f'✅ {self.user}: created tag: {name}')
        return 'add'

    def replace_tag(self, old_name, new_name):
        if self.tags is None:
            self.get_all_tags()
        tag = self._find(self.tags, old_name)
        if tag is None:
            if self._find(self.tags, new_name):
                log(f'➖ {self.user}: tag already renamed: {new_name}')
                return 'skipped'
            log(f'❌ {self.user}: tag {old_name} not found')
            return 'failed'
        url = f'{TOGGL_API}/workspaces/{self.workspace_id}/tags/{tag["id"]}'
        if not self._put(url, {'name': new_name}):
            return 'failed'
        tag['name'] = new_name
        log(f'✅ {self.user}: renamed tag: {old_name} -> {new_name}')
        return 'replace'

    def delete_tag(self, name, _right=None):
        if self.tags is None:
            self.get_all_tags()
        tag = self._find(self.tags, name)
        if tag is None:
            log(f'➖ {self.user}: tag {name} already absent')
            return 'skipped'
        self._delete(f'{TOGGL_API}/workspaces/{self.workspace_id}/tags/{tag["id"]}')
        self.tags.remove(tag)
        log(f'✅ {self.user}: deleted tag: {name}')
        return 'delete'

    # ============ Clients ============ #
    def create_client(self, name, _right=None):
        if self.clients is None:
            self.get_all_clients()
        if self._find(self.clients, name):
            log(f'➖ {self.user}: client already exists: {name}')
            return 'skipped'
        client_id = self._post(f'{TOGGL_API}/workspaces/{self.workspace_id}/clients', {'name': name})
        self.clients.append({'id': client_id, 'name': name})
        log(f'✅ {self.user}: created client: {name}')
        return 'add'

    def replace_client(self, old_name, new_name):
        if self.clients is None:
            self.get_all_clients()
        client = self._find(self.clients, old_name)
        if client is None:
            if self._find(self.clients, new_name):
                log(f'➖ {self.user}: client already renamed: {new_name}')
                return 'skipped'
            log(f'❌ {self.user}: client {old_name} not found')
            return 'failed'
        url = f'{TOGGL_API}/workspaces/{self.workspace_id}/clients/{client["id"]}'
        if not self._put(url, {'name': new_name}):
            return 'failed'
        client['name'] = new_name
        log(f'✅ {self.user}: renamed client: {old_name} -> {new_name}')
        return 'replace'

    def delete_client(self, name, _right=None):
        if self.clients is None:
            self.get_all_clients()
        client = self._find(self.clients, name)
        if client is None:
            log(f'➖ {self.user}: client {name} already absent')
            return 'skipped'
        self._delete(f'{TOGGL_API}/workspaces/{self.workspace_id}/clients/{client["id"]}')
        self.clients.remove(client)
        log(f'✅ {self.user}: deleted client: {name}')
        return 'delete'

    # ============ Projects ============ #
    def create_project(self, name, _right=None):
        if self.projects is None:
            self.get_all_projects()
        if self.clients is None:
            self.get_all_clients()
        if self._find(self.projects, name):
            log(f'➖ {self.user}: project already exists: {name}')
            return 'skipped'

        client_name = client_of(name)
        if client_name is None:
            log(f'❌ {self.user}: не разобрать клиента из имени проекта "{name}" '
                  f'(ожидается "Client: Suffix")')
            return 'failed'
        client = self._find(self.clients, client_name)
        if client is None:
            log(f'❌ {self.user}: client {client_name} not found — project {name} skipped')
            return 'failed'

        data = {
            'name': name,
            'client_id': client['id'],
            'active': True,
            'is_private': True,
        }
        project_id = self._post(f'{TOGGL_API}/workspaces/{self.workspace_id}/projects', data)
        self.projects.append({'id': project_id, 'name': name})
        log(f'✅ {self.user}: created project: {name} (client {client_name})')
        return 'add'

    def replace_project(self, old_name, new_name):
        if self.projects is None:
            self.get_all_projects()
        project = self._find(self.projects, old_name)
        if project is None:
            if self._find(self.projects, new_name):
                log(f'➖ {self.user}: project already renamed: {new_name}')
                return 'skipped'
            log(f'❌ {self.user}: project {old_name} not found')
            return 'failed'
        url = f'{TOGGL_API}/workspaces/{self.workspace_id}/projects/{project["id"]}'
        if not self._put(url, {'name': new_name}):
            return 'failed'
        project['name'] = new_name
        log(f'✅ {self.user}: renamed project: {old_name} -> {new_name}')
        return 'replace'

    def delete_project(self, name, _right=None):
        if self.projects is None:
            self.get_all_projects()
        project = self._find(self.projects, name)
        if project is None:
            log(f'➖ {self.user}: project {name} already absent')
            return 'skipped'
        self._delete(f'{TOGGL_API}/workspaces/{self.workspace_id}/projects/{project["id"]}')
        self.projects.remove(project)
        log(f'✅ {self.user}: deleted project: {name}')
        return 'delete'

    # ============ применение diff'а ============ #
    HANDLERS = {
        'tags':     {'add': 'create_tag',     'replace': 'replace_tag',     'delete': 'delete_tag'},
        'clients':  {'add': 'create_client',  'replace': 'replace_client',  'delete': 'delete_client'},
        'projects': {'add': 'create_project', 'replace': 'replace_project', 'delete': 'delete_project'},
    }

    def apply(self, kind, rep_fix, actions):
        """Применяет строки diff'а данного вида для перечисленных действий."""
        for action in actions:
            rows = rep_fix.loc[rep_fix['doing'] == action]
            if rows.empty:
                continue
            method = getattr(self, self.HANDLERS[kind][action])
            for _, row in rows.iterrows():
                name = row['name']
                right = row['right_variant']
                if action == 'replace' and (pd.isna(right) or str(right).strip() == ''):
                    log(f'❌ {self.user}: {kind}/replace без right_variant: {name}')
                    self.stats['failed'] += 1
                    continue
                try:
                    outcome = method(name, right)
                except Exception as e:
                    log(f'❌ {self.user}: {kind}/{action} "{name}" — {e}')
                    outcome = 'failed'
                self.stats[outcome] = self.stats.get(outcome, 0) + 1


# ============ main script ============ #
def resolve_users(diff, only_users=None):
    only_users = ONLY_USERS if only_users is None else only_users
    in_diff = sorted(set().union(*(set(df['user']) for df in diff.values())))
    if only_users:
        unknown = sorted(set(only_users) - set(in_diff))
        if unknown:
            log(f'⚠ Нет строк в diff_tpc.xlsx (нечего делать): {unknown}')
        return [u for u in in_diff if u in set(only_users)]
    return in_diff


def print_plan(diff, users):
    log('============ ПЛАН ============')
    for u in users:
        parts = []
        for kind in ('clients', 'projects', 'tags'):
            counts = diff[kind].loc[diff[kind]['user'] == u, 'doing'].value_counts()
            if len(counts):
                parts.append(f'{kind}: ' + ', '.join(f'{a} {n}' for a, n in counts.items()))
        log(f'  {u}: ' + (' | '.join(parts) if parts else 'нечего делать'))
    if DRY_RUN:
        log('  режим DRY_RUN — ни один запрос на изменение не уйдёт')
    log('==============================')


def process_user(user, user_diff):
    """Обработка одного пользователя в отдельном потоке."""
    try:
        user.get_all_clients()
        user.get_all_projects()
        user.get_all_tags()
        for kind, actions in PHASES:
            user.apply(kind, user_diff[kind], actions)
        log(f'✅ {user.user}: completed! {user.stats}')
    except Exception as e:
        log(f'❌ {user.user}: error — {e}')


def run():
    diff = load_diff()
    users = resolve_users(diff)
    if not users:
        log('В diff_tpc.xlsx нет строк для обработки.')
        return
    auths = load_tokens(users)
    users = [u for u in users if u in auths]
    print_plan(diff, users)

    sessions = []
    for u in users:
        log(f'############################ Starting {u} ############################')
        try:
            sessions.append((UserRequests(user=u, auth=auths[u]),
                             {k: df.loc[df['user'] == u] for k, df in diff.items()}))
        except Exception as e:
            log(f'❌ {u}: не удалось инициализировать — {e}')

    threads = []
    for session, user_diff in sessions:
        # args=, а не lambda: в прежней версии срезы diff'а читались из
        # замыкания в момент запуска потока, и часть пользователей могла
        # получить чужой набор изменений.
        thread = threading.Thread(target=process_user, args=(session, user_diff))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    log('✅ All users processed!')
    for session, _ in sessions:
        log(f'   {session.user}: {session.stats}')


if __name__ == '__main__':
    run()
