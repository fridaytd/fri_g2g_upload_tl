from datetime import datetime

from .sheet.models import SOffer
from .brw.brw import G2GBrowser
from .sheet.enums import ProcessType
from .logger import logger
from .g2g.models import (
    CreateOfferPayload,
    ExternalImagesMapping,
    URlQuery,
    DeliverySpeedDetail,
    SalesTerritorySettings,
    OfferAttribute,
    Collection,
    ChildrenCollection,
)
from .g2g.utils import decode_jwt
from .g2g.crwl_api import crwl_g2g_api_client
from .g2g.enums import OfferStatus

from .update_messages import (
    created_offer_message,
    last_update_message,
    listed_offer_message,
    listed_offer_no_change_message,
    edited_offer_message,
    delisted_offer_message,
    delisted_offer_no_change_message,
)


def __flatten_children(
    children_collection: ChildrenCollection,
) -> dict[str, ChildrenCollection]:
    tmp_dict: dict[str, ChildrenCollection] = {}
    if len(children_collection.children) > 0:
        for child in children_collection.children:
            tmp_dict.update(__flatten_children(child))

    else:
        tmp_dict[children_collection.dataset_id] = children_collection

    return tmp_dict


def __construct_offer_attribute(
    collection: Collection,
    attribute_value: str,
) -> OfferAttribute:
    accepted_attribute_values: set[str] = set()
    for children in collection.children:
        for child in __flatten_children(children).values():
            accepted_attribute_values.add(child.value)
            if attribute_value.strip().lower() == child.value.strip().lower():
                return OfferAttribute(
                    collection_id=child.collection_id, dataset_id=child.dataset_id
                )

    raise Exception(
        f"Attribute {collection.value} only accepts {list(accepted_attribute_values)}. You input {attribute_value}"
    )


def construct_offer_attributes(s_offer: SOffer) -> list[OfferAttribute]:
    url_query = URlQuery.from_url(s_offer.Create_offer_link)

    collections = crwl_g2g_api_client.get_collections(
        service_id=url_query.service_id,
        brand_id=url_query.brand_id,
        region_id=url_query.region_id,
    ).payload.results

    sorted_collections = sorted(collections, key=lambda x: x.sort_order)

    attribute_values = s_offer.get_attribute_dist()

    final_collections: list[Collection] = []

    # Find DPD Collection if existed
    for collection in sorted_collections:
        final_collections.append(collection)
        for child in collection.children:
            if (
                child.value == attribute_values[len(final_collections)]
                and len(child.dpd_collections) > 0
            ):
                collections_attributes_search = crwl_g2g_api_client.attributes_search(
                    [
                        dpd_collection.collection_id
                        for dpd_collection in child.dpd_collections
                    ]
                ).payload.results

                collections_attributes_search = sorted(
                    collections_attributes_search, key=lambda x: x.sort_order
                )
                final_collections.extend(collections_attributes_search)

    offer_attributes: list[OfferAttribute] = []

    if len(attribute_values) < len(final_collections):
        raise Exception(
            f"Missing attributes. You must input enough: {[collection.value for collection in final_collections]}"
        )

    for i, collection in enumerate(final_collections):
        offer_attributes.append(
            __construct_offer_attribute(collection, attribute_values[i + 1])
        )

    return offer_attributes


async def prepare_create_offer_payload(
    brw: G2GBrowser,
    s_offer: SOffer,
) -> CreateOfferPayload:
    token = await brw.get_access_token_in_safe()

    decoded_jwt = decode_jwt(token)

    seller_id: str = decoded_jwt.sub

    external_image_mappings = ExternalImagesMapping.from_str(
        s_offer.media_gallery if s_offer.media_gallery else ""
    )

    delivery_speed_detail = DeliverySpeedDetail(
        min=s_offer.delivery_speed_min,
        max=s_offer.delivery_speed_max,
        delivery_time=s_offer.delivery_time,
    )

    sales_territory_settings = SalesTerritorySettings()

    url_query = URlQuery.from_url(s_offer.Create_offer_link)

    return CreateOfferPayload(
        seller_id=seller_id,
        delivery_method_ids=[],
        delivery_speed="manual",
        delivery_speed_details=[delivery_speed_detail],
        qty=s_offer.stock,
        description=s_offer.description,
        currency=s_offer.currency,
        min_qty=s_offer.minimum_purchase_quantity,
        low_stock_alert_qty=0,
        sales_territory_settings=sales_territory_settings,
        title=s_offer.title,
        offer_attributes=construct_offer_attributes(s_offer),
        external_images_mapping=external_image_mappings,
        unit_price=s_offer.unit_price,
        other_pricing=[],
        wholesale_details=[],
        other_wholesale_details=[],
        service_id=url_query.service_id,
        brand_id=url_query.brand_id,
        region_id=url_query.region_id,
        offer_type="public",
    )


async def main_flow(
    brw: G2GBrowser,
    s_offer: SOffer,
):
    try:
        if s_offer.Check == ProcessType.LIST.value:
            return await list_flow(brw, s_offer)

        if s_offer.Check == ProcessType.EDIT.value:
            return await edit_flow(brw, s_offer)

        if s_offer.Check == ProcessType.DELIST.value:
            return await delist_flow(brw, s_offer)
    except Exception as e:
        raise Exception(str(e))


async def create_offer_flow(brw: G2GBrowser, s_offer: SOffer):
    logger.info("Create offer")

    create_offer_payload = await prepare_create_offer_payload(brw, s_offer)

    # print(create_offer_payload.model_dump_json())
    # return

    token = await brw.get_access_token_in_safe()
    created_offer = crwl_g2g_api_client.create_offer(
        payload=create_offer_payload,
        token=token,
    ).payload

    now = datetime.now()

    s_offer.Offer_ID = created_offer.offer_id
    s_offer.Note = created_offer_message(now)
    s_offer.Timeline = last_update_message(now)

    s_offer.update()


async def list_flow(
    brw: G2GBrowser,
    s_offer: SOffer,
):
    logger.info("LIST flow")
    if not s_offer.Offer_ID:
        return await create_offer_flow(brw=brw, s_offer=s_offer)

    token = await brw.get_access_token_in_safe()
    g2g_offer = crwl_g2g_api_client.get_offer(
        offer_id=s_offer.Offer_ID, token=token
    ).payload
    if g2g_offer.status != OfferStatus.LIVE.value:
        logger.info("Change offer status to live")
        crwl_g2g_api_client.bulk_update(
            offer_id=s_offer.Offer_ID,
            status=OfferStatus.LIVE.value,
            token=token,
            user_id=decode_jwt(token).sub,
        )
        now = datetime.now()
        s_offer.Timeline = last_update_message(now)
        s_offer.Note = listed_offer_message(now)
        s_offer.update()
    else:
        logger.info("Offer listed. No need to change")
        now = datetime.now()
        s_offer.Timeline = last_update_message(now)
        s_offer.Note = listed_offer_no_change_message(now)
        s_offer.update()


async def edit_flow(
    brw: G2GBrowser,
    s_offer: SOffer,
):
    logger.info("EDIT Flow")
    if s_offer.Offer_ID:
        create_offer_payload = await prepare_create_offer_payload(brw, s_offer)

        token = await brw.get_access_token_in_safe()
        _ = crwl_g2g_api_client.update_offer(
            offer_id=s_offer.Offer_ID,
            payload=create_offer_payload,
            token=token,
        ).payload

        now = datetime.now()

        s_offer.Note = edited_offer_message(now)
        s_offer.Timeline = last_update_message(now)

        s_offer.update()
    else:
        raise Exception("Must include Offer ID to edit")


async def delist_flow(
    brw: G2GBrowser,
    s_offer: SOffer,
):
    logger.info("DELIST Flow")
    if s_offer.Offer_ID:
        token = await brw.get_access_token_in_safe()
        g2g_offer = crwl_g2g_api_client.get_offer(s_offer.Offer_ID, token=token).payload
        if g2g_offer.status == OfferStatus.DELISTED.value:
            logger.info("Offer delisted. No need to change")
            now = datetime.now()
            s_offer.Timeline = last_update_message(now)
            s_offer.Note = delisted_offer_no_change_message(now)
            s_offer.update()
        else:
            logger.info("Change offer status to delist")
            crwl_g2g_api_client.bulk_update(
                offer_id=s_offer.Offer_ID,
                status=OfferStatus.DELISTED.value,
                token=token,
                user_id=decode_jwt(token).sub,
            )
            now = datetime.now()
            s_offer.Timeline = last_update_message(now)
            s_offer.Note = delisted_offer_message(now)
            s_offer.update()

    else:
        raise Exception("Must include Offer ID to delist")
