from pydantic import BaseModel, ConfigDict
from typing import Annotated, Self, Final
from gspread.worksheet import Worksheet

from .g_sheet import gsheet_client
from ..decorators import retry_on_fail
from .enums import ProcessType


COL_META_FIELD_NAME: Final[str] = "col_name_xxx"


class ColSheetModel(BaseModel):
    # Model config
    model_config = ConfigDict(arbitrary_types_allowed=True)

    sheet_id: str
    sheet_name: str
    index: int

    @classmethod
    def get_worksheet(
        cls,
        sheet_id: str,
        sheet_name: str,
    ) -> Worksheet:
        spreadsheet = gsheet_client.open_by_key(sheet_id)
        worksheet = spreadsheet.worksheet(sheet_name)

        return worksheet

    @classmethod
    def mapping_fields(cls) -> dict:
        mapping_fields = {}
        for field_name, field_info in cls.model_fields.items():
            if hasattr(field_info, "metadata"):
                for metadata in field_info.metadata:
                    if COL_META_FIELD_NAME in metadata:
                        mapping_fields[field_name] = metadata[COL_META_FIELD_NAME]
                        break

        return mapping_fields

    @classmethod
    def get(
        cls,
        sheet_id: str,
        sheet_name: str,
        index: int,
    ) -> Self:
        mapping_dict = cls.mapping_fields()

        query_value = []

        for _, v in mapping_dict.items():
            query_value.append(f"{v}{index}")

        worksheet = cls.get_worksheet(sheet_id=sheet_id, sheet_name=sheet_name)

        model_dict = {
            "index": index,
            "sheet_id": sheet_id,
            "sheet_name": sheet_name,
        }

        query_results = worksheet.batch_get(query_value)
        count = 0
        for k, _ in mapping_dict.items():
            model_dict[k] = query_results[count].first()
            if isinstance(model_dict[k], str):
                model_dict[k] = model_dict[k].strip()
            count += 1
        return cls.model_validate(model_dict)

    @classmethod
    def batch_get(
        cls,
        sheet_id: str,
        sheet_name: str,
        indexes: list[int],
    ) -> list[Self]:
        worksheet = cls.get_worksheet(
            sheet_id=sheet_id,
            sheet_name=sheet_name,
        )
        mapping_dict = cls.mapping_fields()

        result_list: list[Self] = []

        query_value = []
        for index in indexes:
            for _, v in mapping_dict.items():
                query_value.append(f"{v}{index}")

        query_results = worksheet.batch_get(query_value)

        count = 0

        for index in indexes:
            model_dict = {
                "index": index,
                "sheet_id": sheet_id,
                "sheet_name": sheet_name,
            }

            for k, _ in mapping_dict.items():
                model_dict[k] = query_results[count].first()
                if isinstance(model_dict[k], str):
                    model_dict[k] = model_dict[k].strip()
                count += 1

            result_list.append(cls.model_validate(model_dict))
        return result_list

    @classmethod
    @retry_on_fail(max_retries=3, sleep_interval=30)
    def batch_update(
        cls,
        sheet_id: str,
        sheet_name: str,
        list_object: list[Self],
    ) -> None:
        worksheet = cls.get_worksheet(
            sheet_id=sheet_id,
            sheet_name=sheet_name,
        )
        mapping_dict = cls.mapping_fields()
        update_batch = []

        for object in list_object:
            model_dict = object.model_dump(mode="json")

            for k, v in mapping_dict.items():
                update_batch.append(
                    {
                        "range": f"{v}{object.index}",
                        "values": [[model_dict[k]]],
                    }
                )

        if len(list_object) > 0:
            worksheet.batch_update(update_batch)

    @retry_on_fail(max_retries=3, sleep_interval=30)
    def update(
        self,
    ) -> None:
        mapping_dict = self.mapping_fields()
        model_dict = self.model_dump(mode="json")

        worksheet = self.get_worksheet(
            sheet_id=self.sheet_id, sheet_name=self.sheet_name
        )

        update_batch = []
        for k, v in mapping_dict.items():
            update_batch.append(
                {
                    "range": f"{v}{self.index}",
                    "values": [[model_dict[k]]],
                }
            )

        worksheet.batch_update(update_batch)


class SOffer(ColSheetModel):
    Check: Annotated[str, {COL_META_FIELD_NAME: "B"}]
    Note: Annotated[str | None, {COL_META_FIELD_NAME: "C"}] = None
    Timeline: Annotated[str | None, {COL_META_FIELD_NAME: "D"}] = None
    Offer_ID: Annotated[str | None, {COL_META_FIELD_NAME: "E"}] = None
    ADMIN: Annotated[str | None, {COL_META_FIELD_NAME: "F"}] = None
    SELLER: Annotated[str | None, {COL_META_FIELD_NAME: "G"}] = None
    Create_offer_link: Annotated[str, {COL_META_FIELD_NAME: "H"}]
    title: Annotated[str, {COL_META_FIELD_NAME: "I"}]
    description: Annotated[str, {COL_META_FIELD_NAME: "J"}]
    media_gallery: Annotated[str | None, {COL_META_FIELD_NAME: "K"}] = None
    currency: Annotated[str, {COL_META_FIELD_NAME: "L"}]
    unit_price: Annotated[float, {COL_META_FIELD_NAME: "M"}]
    delivery_method: Annotated[str, {COL_META_FIELD_NAME: "N"}]
    stock: Annotated[int, {COL_META_FIELD_NAME: "O"}]
    minimum_purchase_quantity: Annotated[int, {COL_META_FIELD_NAME: "P"}]
    delivery_speed_min: Annotated[int, {COL_META_FIELD_NAME: "Q"}]
    delivery_speed_max: Annotated[int, {COL_META_FIELD_NAME: "R"}]
    delivery_time: Annotated[int, {COL_META_FIELD_NAME: "S"}]
    region: Annotated[str, {COL_META_FIELD_NAME: "T"}]
    attribute_1: Annotated[str | None, {COL_META_FIELD_NAME: "U"}] = None
    attribute_2: Annotated[str | None, {COL_META_FIELD_NAME: "V"}] = None
    attribute_3: Annotated[str | None, {COL_META_FIELD_NAME: "W"}] = None
    attribute_4: Annotated[str | None, {COL_META_FIELD_NAME: "X"}] = None
    attribute_5: Annotated[str | None, {COL_META_FIELD_NAME: "Y"}] = None
    attribute_6: Annotated[str | None, {COL_META_FIELD_NAME: "Z"}] = None
    attribute_7: Annotated[str | None, {COL_META_FIELD_NAME: "AA"}] = None
    attribute_8: Annotated[str | None, {COL_META_FIELD_NAME: "AB"}] = None
    attribute_9: Annotated[str | None, {COL_META_FIELD_NAME: "AC"}] = None
    attribute_10: Annotated[str | None, {COL_META_FIELD_NAME: "AD"}] = None
    relax: Annotated[float, {COL_META_FIELD_NAME: "AE"}] = 0

    def get_attribute_dist(
        self,
    ) -> dict[int, str]:
        attributes: dict[int, str] = {}
        for i in range(1, 11):
            if getattr(self, f"attribute_{i}"):
                attributes[i] = getattr(self, f"attribute_{i}")
        return attributes

    @staticmethod
    def get_run_indexes(sheet_id: str, sheet_name: str, col_index: int) -> list[int]:
        sheet = SOffer.get_worksheet(sheet_id=sheet_id, sheet_name=sheet_name)
        run_indexes = []
        check_col = sheet.col_values(col_index)
        for idx, value in enumerate(check_col):
            idx += 1
            if value in [type.value for type in ProcessType]:
                run_indexes.append(idx)

        return run_indexes
