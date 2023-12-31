import jwt


def jwt_token_validate(token):
    jwt_secret_key = '35c67738-33db-4d1c-8987-d43811e04d17'
    header = jwt.get_unverified_header(token)
    payload = jwt.decode(jwt=token, key=jwt_secret_key, algorithms=header.get('alg'))

    return payload, header


class LtsUser:
    uid = None
    id = None
    pk = None
    username = ''
    is_staff = False
    is_active = False
    is_superuser = False

    def __init__(self, username, uid):
        self.username = username
        self.uid = uid

    def __str__(self):
        return self.username
