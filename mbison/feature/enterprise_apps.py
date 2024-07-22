# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/feature/enterprise_apps.ipynb.

# %% auto 0
__all__ = ['App_API_Exception', 'get_app_by_id', 'get_app_versions', 'get_app_source_by_version', 'get_all_apps',
           'DomoEnterpriseApp', 'DomoEnterpriseApps']

# %% ../../nbs/feature/enterprise_apps.ipynb 2
from dataclasses import dataclass, field
import datetime as dt

from typing import List
import os

import mbison.client.core as dmda
import mbison.feature.users as dmdu
import mbison.utils as dmut

# %% ../../nbs/feature/enterprise_apps.ipynb 6
class App_API_Exception(dmda.API_Exception):
    def __init__(self, res, message= None):
        super().__init__(res = res,message = message)

def get_app_by_id(auth: dmda.DomoAuth, design_id: str, debug_api: bool = False):

    endpoint = f"/api/apps/v1/designs/{design_id}"

    res = dmda.domo_api_request(
        endpoint=endpoint,
        request_type="get",
        auth=auth,
        debug_api=debug_api,
    )

    return res

# %% ../../nbs/feature/enterprise_apps.ipynb 8
def get_app_versions(auth: dmda.DomoAuth, design_id, debug_api: bool = False):

    endpoint = f"/domoapps/designs/{design_id}/versions"

    return dmda.domo_api_request(
        endpoint=endpoint, auth=auth, request_type="get", debug_api=debug_api
    )

# %% ../../nbs/feature/enterprise_apps.ipynb 10
def get_app_source_by_version(
    auth: dmda.DomoAuth,
    download_path,
    design_id,
    version,
    debug_api: bool = False,
):

    download_path = dmut.change_suffix(download_path, ".zip")

    endpoint = f"/domoapps/designs/{design_id}/versions/{version}/assets"

    res = dmda.domo_api_stream_request(
        endpoint=endpoint,
        request_type="get",
        auth=auth,
        debug_api=debug_api,
        download_path=download_path,
    )

    if not res.is_success:
        raise App_API_Exception(res = res, message = f"unable to download assets for {design_id}")

    return res

# %% ../../nbs/feature/enterprise_apps.ipynb 12
def get_all_apps(auth: dmda.DomoAuth, debug_api: bool = False):

    endpoint = "/api/apps/v1/designs"

    params = {
        "checkAdminAuthority" : True, 
        "deleted": False,
        "direction" : "desc",
        # "parts" : "owners,creator,thumbnail",
        "search" : "",
        "withPermission" : "ADMIN"}


    res = dmda.domo_api_request(
        endpoint=endpoint,
        request_type="get",
        params=params,
        auth=auth,
        debug_api=debug_api,
    )


    return res

# %% ../../nbs/feature/enterprise_apps.ipynb 14
@dataclass
class DomoEnterpriseApp:
    auth: dmda.DomoAuth = field(repr=False)
    id: str
    name: str
    owner: dmdu.DomoUser
    created_dt: dt.datetime
    lastmodified_dt: dt.datetime
    versions: List[str]
    current_version: str
    referencing_cards: List[dict]

    @classmethod
    def _from_json(cls, obj, auth: dmda.DomoAuth, debug_api: bool = False):

        domo_user = None

        try:
            if obj["owner"]:
                domo_user = dmdu.DomoUser.get_by_id(
                    user_id=obj["owner"], auth=auth, debug_api=debug_api
                )

        except dmdu.User_API_Exception as e:
            print(e)

        return cls(
            auth=auth,
            id=obj["id"],
            name=obj["name"],
            owner=domo_user,
            created_dt=obj["createdDate"],
            lastmodified_dt=obj["updatedDate"],
            versions=obj["versions"],
            current_version=obj["latestVersion"],
            referencing_cards=obj["referencingCards"],
        )

    @classmethod
    def get_by_id(
        cls,
        design_id,
        auth: dmda.DomoAuth,
        debug_api: bool = False,
        return_raw: bool = False,
    ):
        res = get_app_by_id(auth=auth, design_id=design_id, debug_api=debug_api)

        if return_raw:
            return res

        return cls._from_json(obj=res.response, auth=auth, debug_api=debug_api)

    def get_source_code(
        self,
        version: str = None,
        debug_api: bool = False,
        download_folder="./EXPORT/",
        file_name=None,
    ):

        file_name = file_name or f"{self.id} - {version or self.current_version}.zip"
        file_name = dmut.change_suffix(file_name, ".zip")

        download_path = os.path.join(download_folder, file_name)
        
        return get_app_source_by_version(
            auth=self.auth,
            download_path=download_path,
            design_id=self.id,
            version=version or self.current_version,
            debug_api=debug_api,
        )


    def get_versions(self, debug_api: bool = False, return_raw: bool = False):

        res = get_app_versions(auth=self.auth, design_id=self.id, debug_api=debug_api)
        if return_raw:
            return res

        self.versions = res.response
        return self.versions

# %% ../../nbs/feature/enterprise_apps.ipynb 17
@dataclass
class DomoEnterpriseApps:
    auth : dmda.DomoAuth = field(repr = False)
    enterprise_apps : List[DomoEnterpriseApp] = None

    def get_apps(self, debug_api : bool = False , return_raw: bool = False):
        res = get_all_apps(auth = self.auth, debug_api= debug_api)

        if return_raw:
            return res
        
        self.enterprise_apps = [DomoEnterpriseApp._from_json(auth = self.auth, obj = obj) for obj in res.response]
        return self.enterprise_apps
