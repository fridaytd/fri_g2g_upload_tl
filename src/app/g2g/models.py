import re
from urllib.parse import urlparse, parse_qs

from pydantic import BaseModel, RootModel
from typing import Generic, TypeVar, Literal

T = TypeVar("T", bound=BaseModel)


class ResponseResult(BaseModel, Generic[T]):
    results: list[T]


class Response(BaseModel, Generic[T]):
    code: int
    messages: list[str]
    payload: ResponseResult[T]
    request_id: str


class CatName(BaseModel):
    en: str
    id: str
    ko: str | None = None


class Category(BaseModel):
    cat_name: CatName
    cat_id: str
    service_id: str
    created_at: int
    updated_at: int
    sort_order: int


class Brand(BaseModel):
    brand_id: str
    service_id: str
    brand_img_url: str
    services: list[str]
    brand_tags: list[str]
    total_offer: int


class Keyword(BaseModel):
    en: str
    keyword_id: str
    keyword_category: str
    default_name: str
    seo_term: str | None = None


class KeywordDict(RootModel[dict[str, Keyword]]):
    def __getitem__(self, item):
        return self.root[item]


class MarketingTitle(BaseModel):
    en: str | None = None
    id: str | None = None


class Cat(BaseModel):
    service_id: str
    brand_id: str
    seo_term_alias: str | None = None
    marketing_title: MarketingTitle | None = None
    cat_path: str | None = None


class SeoTerm(BaseModel):
    seo_term: str
    seo_term_alias: str | None = None


class CategoryJson(RootModel[dict[str, Cat | SeoTerm]]):
    pass


class KeywordRelation(BaseModel):
    relation_id: str
    service_id: str
    brand_id: str
    region_id: str


class DpdCollection(BaseModel):
    collection_id: str
    sort_order: int
    is_primary_img: bool


class ChildrenCollection(BaseModel):
    collection_id: str
    dataset_id: str
    parent_id: str
    value: str
    description: dict
    sort_order: int
    total_children: int
    children: list["ChildrenCollection"]
    product_tags: list[str]
    dpd_collections: list[DpdCollection]
    is_multi_layer: bool


class CollectionLabel(BaseModel):
    id: str | None = None
    en: str


class Collection(BaseModel):
    collection_id: str
    is_grouping: bool | None = None
    is_multiselect: bool
    value: str
    label: CollectionLabel
    sort_order: int
    input_field: str
    is_required: bool
    is_updatable: bool
    is_multi_layer: bool
    created_at: int | None = None
    updated_at: int | None = None
    is_feature: bool
    children: list[ChildrenCollection]


#################
#
# URL
#
class URlQuery(BaseModel):
    service_id: str
    brand_id: str
    root_id: str
    cat_id: str
    cat_path: str
    relation_id: str
    region_id: str | None = None

    @staticmethod
    def from_url(url: str) -> "URlQuery":
        parsed_url = urlparse(url)
        query_dict = parse_qs(parsed_url.query)

        single_query_dict = {}
        for k, v in query_dict.items():
            single_query_dict[k] = v[0]

        return URlQuery.model_validate(single_query_dict)


#################
#
# Create offer payload
#


class DeliverySpeedDetail(BaseModel):
    min: int
    max: int
    delivery_time: int


class SalesTerritorySettings(BaseModel):
    settings_type: Literal["global"] = "global"
    countries: list[str] = []


class OfferAttribute(BaseModel):
    collection_id: str
    dataset_id: str


class ExternalImagesMapping(BaseModel):
    image_name: str
    image_url: str

    @staticmethod
    def from_str(str: str) -> list["ExternalImagesMapping"]:
        pattern = r"\(([^)]*)\)\(([^)]*)\)"

        external_image_mapppings: list[ExternalImagesMapping] = []
        for phrase in str.split("\n"):
            match = re.match(pattern, phrase)
            if match:
                external_image_mapppings.append(
                    ExternalImagesMapping(
                        image_name=match.group(1), image_url=match.group(2)
                    )
                )

        return external_image_mapppings


class CreateOfferPayload(BaseModel):
    seller_id: str
    delivery_method_ids: list = []
    delivery_speed: Literal["instant", "manual"] = "manual"
    delivery_speed_details: list[DeliverySpeedDetail]
    qty: int
    description: str
    currency: str
    min_qty: int
    low_stock_alert_qty: int
    sales_territory_settings: SalesTerritorySettings
    title: str
    offer_attributes: list[OfferAttribute]
    external_images_mapping: list[ExternalImagesMapping]
    unit_price: float
    other_pricing: list = []
    wholesale_details: list = []
    other_wholesale_details: list = []
    service_id: str
    brand_id: str
    region_id: str | None = None
    offer_type: str = "public"


class CreatedOffer(BaseModel):
    offer_id: str
    seller_id: str
    service_id: str
    brand_id: str
    region_id: str
    relation_id: str
    offer_type: str
    offer_attributes: list[OfferAttribute]
    offer_title_collection_tree: list[str]
    primary_img_attributes: list
    offer_group: str
    title: str
    description: str
    api_qty: int
    low_stock_alert_qty: int
    available_qty: int
    min_qty: int
    actual_qty: int
    currency: str
    unit_price: float
    other_pricing: list
    unit_name: str
    qty_metric: str
    wholesale_details: list
    other_wholesale_details: list
    is_official: bool
    delivery_mode: list
    delivery_method_ids: list[str]
    delivery_speed: str
    delivery_speed_details: list[DeliverySpeedDetail]
    sales_territory_settings: SalesTerritorySettings
    cat_path: str
    cat_id: str
    ancestor_id: str
    status: str
    created_at: int
    updated_at: int
    seller_updated_at: int
    external_images_mapping: list[ExternalImagesMapping]


class CreatedOfferResponse(BaseModel):
    code: int
    messages: list[str]
    payload: CreatedOffer
    request_id: str


#################
#
# Get Offer Payload
#


class SellerRanking(BaseModel):
    seller_ranking_id: str
    seller_ranking_name: str
    commission_rates: float


class OfferValue(BaseModel):
    collection_id: str
    dataset_id: str
    value: str


class ExternalImgDomain(BaseModel):
    website_name: str
    domains: list[str]


# class DeliveryMethodDetails(BaseModel):
#     pass  # Can be extended based on actual data structure


class Offer(BaseModel):
    offer_id: str
    offer_currency: str
    converted_unit_price: float
    decimal_places: int
    display_currency: str
    display_price: float
    is_sold_out: bool
    is_expired: bool
    is_legacy: bool
    delisted_reason: str
    delisted_remark: str
    relation_id: str
    service_id: str
    brand_id: str
    region_id: str
    offer_type: str
    title: str
    offer_title_collection_tree: list[str]
    description: str
    offer_group: str
    offer_attributes: list[OfferValue]
    offer_group_attributes: dict = {}
    primary_img_attributes: list = []
    inventory_label_settings: list = []
    inventory_csv_filename: str
    inventory_csv_header: str
    commission_rates: list[SellerRanking]
    actual_qty: int
    available_qty: int
    reserved_qty: int
    api_qty: int
    low_stock_alert_qty: int
    min_qty: int
    unit_name: str
    unit_quantity: int
    unit_price: float
    formatted_unit_price: str
    other_pricing: list = []
    cost_pricing: dict = {}
    status: str
    seller_id: str
    username: str
    avatar: str
    user_avatar: str
    user_level: int
    is_online: bool
    is_official: bool
    delivery_mode: list = []
    delivery_method_ids: list = []
    delivery_method_details: list = []
    supported_countries: list = []
    wholesale_details: list = []
    other_wholesale_details: list = []
    cost_wholesale_details: list = []
    delivery_speed: str
    delivery_speed_details: list[DeliverySpeedDetail]
    satisfaction_rate: float
    total_rating: int
    listing_duration: str
    sales_territory_settings: SalesTerritorySettings
    cat_path: str
    cat_id: str
    root_id: str
    created_at: int
    updated_at: int
    external_images_mapping: list[ExternalImagesMapping] = []
    total_success_order: int
    description_images: list = []
    offer_insurance: str
    external_img_domains: list[ExternalImgDomain]
    max_external_img: int


class GetOfferResponse(BaseModel):
    code: int
    messages: list[str]
    payload: Offer
    request_id: str


#################
#
# Bulk Update
#


class BulkUpdateStat(BaseModel):
    success: int
    fail: int


class BulkUpdateResponse(BaseModel):
    code: int
    messages: list[str]
    payload: BulkUpdateStat
    request_id: str
