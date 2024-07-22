# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/feature/codeengine.ipynb.

# %% auto 0
__all__ = ['get_packages', 'get_package_by_id', 'get_package_versions', 'get_package_version_by_id',
           'DomoCodeEngine_PackageVersion', 'DomoCodeEngine_Package', 'DomoCodeEngine_Packages']

# %% ../../nbs/feature/codeengine.ipynb 2
from dataclasses import dataclass, field

from typing import List
import datetime as dt

import mbison.client.core as dmda

# %% ../../nbs/feature/codeengine.ipynb 6
def get_packages(auth: dmda.DomoAuth, debug_api : bool = False):
    endpoint = "/api/codeengine/v2/packages"

    res = dmda.domo_api_request(endpoint = endpoint,
                                auth=auth, request_type="get",
                                debug_api= debug_api
                                )

    return res

# %% ../../nbs/feature/codeengine.ipynb 8
def get_package_by_id(auth: dmda.DomoAuth, package_id, debug_api : bool = False):
        
        endpoint = f"/api/codeengine/v2/packages/{package_id}"
                
        return dmda.domo_api_request(endpoint=endpoint, request_type = 'get', auth=auth, debug_api=debug_api)


# %% ../../nbs/feature/codeengine.ipynb 10
def get_package_versions(auth: dmda.DomoAuth, package_id, debug_api : bool = False):
        """each package can have one or many version"""
        
        endpoint = f"/api/codeengine/v2/packages/{package_id}/versions/"

        params = {"parts" : " functions,code"}
                
        return dmda.domo_api_request(endpoint=endpoint, request_type = 'get', auth=auth,params=params, debug_api=debug_api)


def get_package_version_by_id(auth: dmda.DomoAuth, package_id, version, debug_api : bool = False):
        
        endpoint = f"/api/codeengine/v2/packages/{package_id}/versions/{version}"

        params = {"parts" : " functions,code"}
                
        return dmda.domo_api_request(endpoint=endpoint, request_type = 'get', auth=auth,params=params, debug_api=debug_api)


# %% ../../nbs/feature/codeengine.ipynb 14
@dataclass 
class DomoCodeEngine_PackageVersion:
    """one package can have multiple versions"""
    
    auth : dmda.DomoAuth = field(repr = False)
    package_id: str
    version : str
    code : str
    created_by : dict
    created_on_dt : dt.datetime
    updated_by : dict
    updated_on_dt : dt.datetime

    @classmethod
    def from_json(cls, auth: dmda.DomoAuth, obj):
        return cls(
            auth = auth,
            package_id = obj['packageId'],
            version = obj['version'],
            code = obj["code"],
            created_by = obj["createdBy"],
            created_on_dt = obj["createdOn"],
            updated_by = obj["updatedBy"],
            updated_on_dt = obj["updatedOn"],
        )
    
    @classmethod
    def get_by_id(cls, auth : dmda.DomoAuth, package_id : str , version: str, return_raw : bool = False, debug_api: bool=  False):

        res = get_package_version_by_id(auth = auth, package_id = package_id, 
                                  version = version, debug_api = debug_api)

        if return_raw:
            return res

        return cls.from_json(
            auth = auth,
            obj = res.response
        )



# %% ../../nbs/feature/codeengine.ipynb 16
@dataclass
class DomoCodeEngine_Package:
    auth: dmda.DomoAuth = field(repr=False)
    id: str
    name: str
    environment: str
    availability: str
    owner: dict

    created_on_dt: dt.datetime
    updated_on_dt: dt.datetime

    source: str

    current_version: str = None
    description: str = None
    language: str = None

    dce_versions: List[DomoCodeEngine_PackageVersion] = None
    dce_current_version: DomoCodeEngine_PackageVersion = None

    @classmethod
    def from_json(cls, auth: dmda.DomoAuth, obj):

        return cls(
            auth=auth,
            id=obj["id"],
            name=obj["name"],
            language=obj["language"],
            environment=obj["environment"],
            availability=obj["availability"],
            owner=obj["owner"],
            created_on_dt=obj["createdOn"],
            updated_on_dt=obj["updatedOn"],
            source=obj["packageSource"],
            description=obj.get("description"),
            current_version=obj.get("versions")[0]["version"],
        )

    @classmethod
    def get_by_id(
        cls,
        auth: dmda.DomoAuth,
        package_id,
        debug_api: bool = False,
        return_raw: bool = False,
    ):
        res = get_package_by_id(auth=auth, package_id=package_id, debug_api=debug_api)

        if return_raw:
            return res

        return cls.from_json(auth=auth, obj=res.response)

    def get_versions(self, debug_api: bool = False, return_raw: bool = False):

        res = get_package_versions(
            auth=self.auth, package_id=self.id, debug_api=debug_api
        )

        if return_raw:
            return res

        self.dce_versions = [
            DomoCodeEngine_PackageVersion.from_json(auth=self.auth, obj=obj)
            for obj in res.response
        ]

        return self.dce_versions

    def get_current_version(self, debug_api: bool = False, return_raw: bool = False):

        res = DomoCodeEngine_PackageVersion.get_by_id(
            auth=self.auth,
            package_id=self.id,
            version=self.current_version,
            debug_api=debug_api,
            return_raw=return_raw,
        )

        if return_raw:
            return res

        self.dce_current_version = res

        return self.dce_current_version

# %% ../../nbs/feature/codeengine.ipynb 18
@dataclass
class DomoCodeEngine_Packages:
    auth: dmda.DomoAuth = field(repr = False)
    packages : List[dict] = field(repr = False, default = None)

    dce_packages:  List[DomoCodeEngine_Package] = field(default_factory=lambda : [])

    def get_packages(self, debug_api: bool = False, return_raw : bool = False):
        res = get_packages(auth = self.auth, debug_api = debug_api)

        if return_raw:
            return res

        self.packages = res.response
        
        self.dce_packages = [DomoCodeEngine_Package.from_json(auth=self.auth , obj = obj) for obj in self.packages]

        return self.dce_packages
