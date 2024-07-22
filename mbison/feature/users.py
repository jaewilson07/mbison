# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/feature/users.ipynb.

# %% auto 0
__all__ = ['User_API_Exception', 'get_user_by_id', 'DomoUser']

# %% ../../nbs/feature/users.ipynb 1
from dataclasses import dataclass , field

import mbison.client.core as dmda

# %% ../../nbs/feature/users.ipynb 4
class User_API_Exception(dmda.API_Exception):
    def __init__(self, res, message= None):

        super().__init__(res = res,message = message)

# %% ../../nbs/feature/users.ipynb 5
def get_user_by_id(user_id, auth : dmda.DomoAuth , debug_api: bool = False):

    endpoint = f"/api/content/v3/users/{user_id}"

    params = {"includeDetails": True}

    res = dmda.domo_api_request(
        auth= auth,
        endpoint=endpoint,
        request_type= "GET",
        params = params,
        debug_api= debug_api,
    )


    if not res.is_success and res.status == 404 :
        raise User_API_Exception(res, message = f"unable to find user - {user_id}")

    return res

# %% ../../nbs/feature/users.ipynb 7
@dataclass
class DomoUser:
    auth :dmda.DomoAuth = field(repr = False)
    id: str
    display_name: str
    role_id: int
    email : str

    @classmethod
    def from_json(cls, obj, auth : dmda.DomoAuth):
        return cls(
            auth = auth, 
            id = obj['id'],
            display_name = obj['displayName'],
            role_id = obj['roleId'],
            email = obj['detail']['email']
        )
    
    @classmethod
    def get_by_id(cls, user_id, auth, debug_api : bool = False, return_raw :bool = False):
        res = get_user_by_id(user_id = user_id, auth =auth, debug_api = debug_api)

        if return_raw:
            return res
        
        return cls.from_json(obj = res.response , auth = auth)
