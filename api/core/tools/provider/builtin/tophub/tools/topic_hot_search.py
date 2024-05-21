from typing import Any, Union

import httpx
import logging
from core.tools.entities.tool_entities import ToolInvokeMessage
from core.tools.tool.builtin_tool import BuiltinTool
from core.tools.utils.uuid_utils import is_valid_uuid
import requests

logger = logging.getLogger(__name__)


class TopHubTopicHotSearchTool(BuiltinTool):
    def _invoke(self, user_id: str, tool_parameters: dict[str, Any]
                ) -> Union[ToolInvokeMessage, list[ToolInvokeMessage]]:
        """
            invoke tools
            API document: https://open.feishu.cn/document/client-docs/bot-v3/add-custom-bot
        """
        baseurl = "https://api.tophubdata.com"

        try:
            result = ""
            search_maps = {
                "x9ozB4KoXb": "今日头条·头条热榜",
                "L4MdA5ldxD": "小红书·热榜",
                "LwkvlBqez1": "豆瓣话题广场·24小时话题趋势",
                "K7GdaMgdQy": "抖音·热搜榜"
            }
            for key, value in search_maps.items():
                headers = {'Authorization': self.runtime.credentials["apikey"]}
                endpoint = f"/nodes/{key}"
                url = f"{baseurl}{endpoint}"
                r = requests.get(url, headers=headers).json()
                data = []
                for d in r["data"]["items"][:10]:
                    data.append(f'{d["rank"]}.{d["title"]}')
                data_str = "\n".join(data)
                result += f'来源:{value}, 数据:{data_str}\n'
            return self.create_text_message(result)
        except Exception as e:
            logger.exception("get hot search error")
            return self.create_text_message("search error")
