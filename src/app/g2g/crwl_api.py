from httpx import Client, HTTPStatusError
from typing import Final

from .models import (
    Response,
    Category,
    Brand,
    KeywordDict,
    CategoryJson,
    KeywordRelation,
    Collection,
    CreateOfferPayload,
    CreatedOfferResponse,
    GetOfferResponse,
    BulkUpdateResponse,
)

from ..logger import logger
from ..decorators import retry_on_fail

CRWL_G2G_API_BASE_URL: Final[str] = "https://sls.g2g.com"
G2G_API_VERSION: Final[str] = "v2"


class CrwlG2GAPI:
    def __init__(self) -> None:
        self.client = Client()
        self.base_url = CRWL_G2G_API_BASE_URL
        self.version = G2G_API_VERSION

    @retry_on_fail()
    def get_categories(self) -> Response[Category]:
        res = self.client.get(f"{self.base_url}/offer/category")

        try:
            res.raise_for_status()
        except HTTPStatusError as e:
            logger.error(res.text)
            logger.exception(e)
            res.raise_for_status()

        return Response[Category].model_validate(res.json())

    @retry_on_fail()
    def get_brands(self, category_id: str) -> Response[Brand]:
        res = self.client.get(
            f"{self.base_url}/{self.version}/offer/category/{category_id}/brands?page_size=10000"
        )
        try:
            res.raise_for_status()
        except HTTPStatusError as e:
            logger.error(res.text)
            logger.exception(e)
            res.raise_for_status()

        return Response[Brand].model_validate(res.json())

    @retry_on_fail()
    def get_keywords(
        self,
    ) -> KeywordDict:
        res = self.client.get("https://assets.g2g.com/offer/keyword.json")
        try:
            res.raise_for_status()
        except HTTPStatusError as e:
            logger.error(res.text)
            logger.exception(e)
            res.raise_for_status()

        return KeywordDict.model_validate(res.json())

    @retry_on_fail()
    def get_category_json(
        self,
    ) -> CategoryJson:
        res = self.client.get("https://assets.g2g.com/offer/categories.json")
        try:
            res.raise_for_status()
        except HTTPStatusError as e:
            logger.error(res.text)
            logger.exception(e)
            res.raise_for_status()

        return CategoryJson.model_validate(res.json())

    @retry_on_fail()
    def get_keyword_relation(
        self,
        relation_id: str | None = None,
        service_id: str | None = None,
        brand_id: str | None = None,
        region_id: str | None = None,
    ) -> Response[KeywordRelation]:
        query_params: dict[str, str] = {}

        if relation_id:
            query_params["relation_id"] = relation_id
        if service_id:
            query_params["service_id"] = service_id
        if brand_id:
            query_params["brand_id"] = brand_id
        if region_id:
            query_params["region_id"] = region_id

        res = self.client.get(
            f"{self.base_url}/offer/keyword_relation/search",
            params=query_params,
        )
        try:
            res.raise_for_status()
        except HTTPStatusError as e:
            logger.error(res.text)
            logger.exception(e)
            res.raise_for_status()

        return Response[KeywordRelation].model_validate(res.json())

    @retry_on_fail()
    def get_collections(
        self,
        service_id: str | None = None,
        brand_id: str | None = None,
        region_id: str | None = None,
    ) -> Response[Collection]:
        query_params: dict[str, str] = {"include_searchable_only": "0"}

        if service_id:
            query_params["service_id"] = service_id
        if brand_id:
            query_params["brand_id"] = brand_id
        if region_id:
            query_params["region_id"] = region_id

        res = self.client.get(
            f"{self.base_url}/offer/keyword_relation/collection/",
            params=query_params,
        )

        try:
            res.raise_for_status()
        except HTTPStatusError as e:
            logger.error(res.text)
            logger.exception(e)
            res.raise_for_status()

        return Response[Collection].model_validate(res.json())

    @retry_on_fail()
    def get_product_settings(self, service_id: str, brand_id: str):
        res = self.client.get(
            f"https://sls.g2g.com/offer/product_settings/service/{service_id}/brand/{brand_id}/product_settings"
        )

        print(res.json())

    @retry_on_fail()
    def create_offer(
        self,
        payload: CreateOfferPayload,
        token: str,
    ) -> CreatedOfferResponse:
        headers = {
            "authorization": token,
            "Content-Type": "application/json",
        }
        res = self.client.post(
            f"{self.base_url}/offer",
            headers=headers,
            json=payload.model_dump(mode="json", exclude_none=True),
        )
        try:
            res.raise_for_status()
        except HTTPStatusError as e:
            logger.error(res.text)
            logger.exception(e)
            res.raise_for_status()

        return CreatedOfferResponse.model_validate(res.json())

    @retry_on_fail()
    def get_offer(
        self,
        offer_id: str,
        token,
    ) -> GetOfferResponse:
        headers = {
            "authorization": token,
            "Content-Type": "application/json",
        }
        res = self.client.get(
            f"{self.base_url}/offer/{offer_id}?include_out_of_stock=1&include_inactive=1",
            headers=headers,
        )

        try:
            res.raise_for_status()
        except HTTPStatusError as e:
            logger.error(res.text)
            logger.exception(e)
            res.raise_for_status()

        return GetOfferResponse.model_validate(res.json())

    @retry_on_fail()
    def bulk_update(
        self,
        offer_id: str,
        status: str,
        token: str,
        user_id: str,
    ):
        headers = {
            "authorization": token,
            "Content-Type": "application/json",
        }
        payload = {
            "offer_ids": [offer_id],
            "status": status,
        }
        res = self.client.put(
            f"{self.base_url}/offer/seller/{user_id}/bulk_update",
            headers=headers,
            json=payload,
        )

        try:
            res.raise_for_status()
        except HTTPStatusError as e:
            logger.error(res.text)
            logger.exception(e)
            res.raise_for_status()

        # return BulkUpdateResponse.model_validate(res.json())

    @retry_on_fail()
    def update_offer(
        self,
        offer_id: str,
        payload: CreateOfferPayload,
        token: str,
    ) -> CreatedOfferResponse:
        headers = {
            "authorization": token,
            "Content-Type": "application/json",
        }
        res = self.client.put(
            f"{self.base_url}/offer/{offer_id}",
            headers=headers,
            json=payload.model_dump(mode="json", exclude_none=True),
        )
        try:
            res.raise_for_status()
        except HTTPStatusError as e:
            logger.error(res.text)
            logger.exception(e)
            res.raise_for_status()

        return CreatedOfferResponse.model_validate(res.json())

    @retry_on_fail()
    def attributes_search(self, collection_ids: list[str]) -> Response[Collection]:
        payload = {
            "collection_ids": collection_ids,
        }

        res = self.client.post(
            f"{self.base_url}/offer/keyword_relation/attributes/search", json=payload
        )
        try:
            res.raise_for_status()
        except HTTPStatusError as e:
            logger.error(res.text)
            logger.exception(e)
            res.raise_for_status()

        return Response[Collection].model_validate(res.json())


crwl_g2g_api_client = CrwlG2GAPI()
