import requests


def get_access_token(KEYCLOAK_URL,
                     KEYCLOAK_REALM,
                     KEYCLOAK_CLIENT_ID,
                     KEYCLOAK_CLIENT_SECRET):
    token_url = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token"
    payload = {
        "grant_type": "password",
        "scope": "openid",
        "client_id": KEYCLOAK_CLIENT_ID,
        "client_secret": KEYCLOAK_CLIENT_SECRET,
        "email": "dbatrakov@gontardcie.com",
        "username": "dbatrakov",
        "password": "JbqIhxa2yBVa"
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    res = requests.post(token_url, data=payload, headers=headers)
    return res.json()["access_token"], res.json()["refresh_token"]


def setup_session(session,
                  SUPERSET_URL,
                  KEYCLOAK_URL,
                  KEYCLOAK_REALM,
                  KEYCLOAK_CLIENT_ID,
                  KEYCLOAK_CLIENT_SECRET,
                  COOKIES):
    access_token, _ = get_access_token(KEYCLOAK_URL=KEYCLOAK_URL,
                                       KEYCLOAK_REALM=KEYCLOAK_REALM,
                                       KEYCLOAK_CLIENT_ID=KEYCLOAK_CLIENT_ID,
                                       KEYCLOAK_CLIENT_SECRET=KEYCLOAK_CLIENT_SECRET)
    # Login via browser -> f12 -> Application -> Cookie -> Session
    session_cookie = COOKIES.get('session')
    session.cookies.set("session", session_cookie)
    me_url = f"{SUPERSET_URL}/api/v1/me/"
    print("me_url =", me_url)
    res = session.get(me_url,
                      timeout=5,
                      # allow_redirects=False
                      )
    res.raise_for_status()
    print(f'✅ Авторизован как: {res.json().get('result').get('username')}')
