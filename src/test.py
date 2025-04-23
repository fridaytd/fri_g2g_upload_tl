import asyncio

from app.config import config
from pydoll.browser.options import Options

from app.brw.brw import G2GBrowser
from app.paths import USER_DIR_PATH
from app.g2g.crwl_api import crwl_g2g_api_client
from app.g2g.utils import decode_jwt


async def test():
    # options = Options()
    # options.add_argument("--start-maximized")
    # options.add_argument(f"--user-data-dir={str(USER_DIR_PATH)}")
    # async with G2GBrowser.init(options=options) as brw_xx:
    #     await brw_xx.waiting_for_login()

    #     token = await brw_xx.get_access_token_in_safe()

    #     print(
    #         crwl_g2g_api_client.bulk_update(
    #             offer_id="G1745368731015OT",
    #             status="live",
    #             token=token,
    #             user_id=decode_jwt(token).sub,
    #         )
    #     )

    dpd_collection_ids = ["a837ebae", "9c3e3e10", "e2fdcf93", "0c832872"]
    print(crwl_g2g_api_client.attributes_search(dpd_collection_ids))


if __name__ == "__main__":
    asyncio.run(test())
