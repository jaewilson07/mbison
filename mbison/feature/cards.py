# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/feature/cards.ipynb.

# %% auto 0
__all__ = ['optional_parts', 'Cards_API_Exception', 'generate_search_cards_only_apps_filter', 'search_cards', 'get_card_by_id',
           'DomoCard']

# %% ../../nbs/feature/cards.ipynb 2
from dataclasses import dataclass, field

from typing import List, Any
import datetime as dt
from numbers import Number

import mbison.client.core as dmda
import mbison.client.utils as dmut

from nbdev.showdoc import patch_to

# %% ../../nbs/feature/cards.ipynb 7
class Cards_API_Exception(dmda.API_Exception):
    def __init__(self, res, message=None):

        super().__init__(res=res, message=message)

# %% ../../nbs/feature/cards.ipynb 8
def generate_search_cards_only_apps_filter():
    return {
        "includeCardTypeClause": True,
        "cardTypes": ["domoapp", "mason", "custom"],
        "ascending": True,
        "orderBy": "cardTitle",
    }

def search_cards(
    auth: dmda.DomoAuth,
    query: dict = None,
    debug_api: bool = False,
    return_raw: bool = False,
    debug_loop: bool = False,
    limit: int = 100,
    offset: int = 0,
):

    endpoint = "/api/content/v2/cards/adminsummary"
    query = query or {}
    


    def arr_fn(res):
        if res.status == 429:
            return []
        
        return res.response.get("cardAdminSummaries", [])
    
    res = dmda.looper(
        auth=auth,
        arr_fn=arr_fn,
        offset_params={"limit": "limit", "offset": "skip"},
        offset_params_is_header=True,

        request_type="POST",
        endpoint=endpoint,

        debug_api=debug_api,
        return_raw=return_raw,
        debug_loop=debug_loop, 

        # params = params

        body=query,
        limit=limit,
        offset=offset,

    )

    if not res.is_success:
        print(res)
        raise Cards_API_Exception(res=res)

    return res

# %% ../../nbs/feature/cards.ipynb 10
optional_parts = [
    "certification",
    "datasources",
    "domoapp",
    "drillPath",
    "masonData",
    "metadata",
    "owners",
    "problems",
    "properties",
]


def get_card_by_id(card_id, auth: dmda.DomoAuth, optional_parts = 'certification,datasources,drillPath,owners,properties,domoapp', debug_api: bool = False, return_raw: bool = False):
    endpoint = "/api/content/v1/cards/"

    params = {"parts": optional_parts, "urns": card_id}

    res = dmda.domo_api_request(

        auth=auth,

        request_type="GET",
        endpoint=endpoint,

        debug_api=debug_api,
        params=params,

    )

    if not res.is_success:
        raise Cards_API_Exception(res=res)
    
    if return_raw:
        return res
    
    res.response = res.response[0]
    

    return res

# %% ../../nbs/feature/cards.ipynb 13
@dataclass
class DomoCard:
    id: str
    auth: dmda.DomoAuth = field(repr=False)
    title: str = None
    description: str = None
    type: str = None
    urn: str = None
    chart_type: str = None
    dataset_id: str = None

    datastore_id : str = None
    
    domo_collections: List[Any] = None
    domo_source_code : Any = None

    owners: List[any] = None

    def display_url(self) -> str:
        return f"https://{self.auth.domo_instance}.domo.com/kpis/details/{self.id}"
    

    @classmethod
    def _from_json(cls, obj : dict, auth: dmda.DomoAuth):

        card = cls(
            auth=auth,
            id=obj['id'],
            title=obj['title'],
            type= obj['type'],
            urn= obj['urn'],
            description= obj.get('description'),
            owners = obj.get('owners')
        )

        if obj.get('domoapp',{}).get('id'):
            card.datastore_id = obj['domoapp']['id']
    
        return card

    @classmethod
    def get_by_id(
        cls,
        card_id: str,
        auth: dmda.DomoAuth,
        debug_api: bool = False,
        return_raw: bool = False
    ):
        res = get_card_by_id(
            auth=auth,
            card_id=card_id, 
            debug_api=debug_api
        )

        if return_raw:
            return res


        return cls._from_json(res.response, auth)


# %% ../../nbs/feature/cards.ipynb 15
@patch_to(DomoCard)
def get_collections(self, debug_api : bool = False, return_raw: bool = False):
    import mbison.feature.appdb as dmdb
    
    res  = dmdb.get_collections(datastore_id= self.datastore_id, auth = auth, debug_api= debug_api)

    if return_raw:
        return res

    self.domo_collections = [ dmdb.AppDbCollection.get_by_id(collection_id = obj['id'], auth = auth, debug_api = debug_api) for obj in res.response]

    return self.domo_collections


@patch_to(DomoCard)
def get_source_code(self, debug_api : bool = False):
    self.get_collections(debug_api = debug_api)

    collection_name = 'ddx_app_client_code'
    code_collection = next((domo_collection for domo_collection in self.domo_collections if domo_collection.name ==collection_name), None)

    if not code_collection:
        raise dmda.Class_Exception(cls = self, message = f"collection - {collection_name} not found")
    
    self.domo_source_code = code_collection.query_documents(debug_api = True)[0]

    return self.domo_source_code

