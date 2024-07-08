import logging
from typing import Any, Union

import requests

from core.tools.entities.tool_entities import ToolInvokeMessage
from core.tools.tool.builtin_tool import BuiltinTool

logger = logging.getLogger(__name__)


class TopHubTopicAndGoodsHotSearchTool(BuiltinTool):

    def get_hot_info(self, topic, search_maps, num=10):
        result = ""
        baseurl = "https://api.tophubdata.com"
        result += f"{topic}\n"
        for key, value in search_maps.items():
            headers = {'Authorization': self.runtime.credentials["apikey"]}
            endpoint = f"/nodes/{key}"
            url = f"{baseurl}{endpoint}"
            r = requests.get(url, headers=headers).json()
            data = []
            for d in r["data"]["items"][:num]:
                data.append(f'\t\t\t\t{d["rank"]}.{d["title"]}')
            data_str = "\n".join(data)
            result += f'\t\t来源:{value}, 数据:\n{data_str}\n'
        return result

    def _invoke(self, user_id: str, tool_parameters: dict[str, Any]
                ) -> Union[ToolInvokeMessage, list[ToolInvokeMessage]]:
        """
            invoke tools
            API document: https://open.feishu.cn/document/client-docs/bot-v3/add-custom-bot
        """
        baseurl = "https://api.tophubdata.com"

        try:
            result = ""
            topic_search_maps = {
                "x9ozB4KoXb": "今日头条·头条热榜",
                "L4MdA5ldxD": "小红书·热榜",
                "LwkvlBqez1": "豆瓣话题广场·24小时话题趋势",
                "K7GdaMgdQy": "抖音·热搜榜"
            }
            goods_search_maps = {
                "yjvQDpjobg": "淘宝/天猫·热销总榜 ",
                "ARe1QZ2e7n": "拼多多·实时热销榜",
                "YqoXzV6dOD": "京东·热销总榜"
            }
            result += self.get_hot_info("热搜数据如下:", topic_search_maps)
            result += self.get_hot_info("热销数据如下:", goods_search_maps, 20)
            return self.create_text_message(result)
        except Exception as e:
            logger.exception("get hot search error")
            return self.create_text_message("search error")
