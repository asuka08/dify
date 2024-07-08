import logging
from typing import Any, Union

import requests

from core.tools.entities.tool_entities import ToolInvokeMessage
from core.tools.tool.builtin_tool import BuiltinTool

logger = logging.getLogger(__name__)


class TopHubGoodsHotSearchTool(BuiltinTool):
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
                "yjvQDpjobg": "淘宝/天猫·热销总榜 ",
                "ARe1QZ2e7n": "拼多多·实时热销榜",
                "YqoXzV6dOD": "京东·热销总榜"
            }
            for key, value in search_maps.items():
                headers = {'Authorization': self.runtime.credentials["apikey"]}
                endpoint = f"/nodes/{key}"
                url = f"{baseurl}{endpoint}"
                r = requests.get(url, headers=headers).json()
                data = []
                for d in r["data"]["items"][:20]:
                    data.append(f'{d["rank"]}.{d["title"]}')
                data_str = "\n".join(data)
                result += f'来源:{value}, 数据:{data_str}\n'
            return self.create_text_message(result)
        except Exception as e:
            logger.exception("get hot search error")
            return self.create_text_message("search error")
