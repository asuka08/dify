from typing import Any, Union

import httpx
import logging
from core.tools.entities.tool_entities import ToolInvokeMessage
from core.tools.tool.builtin_tool import BuiltinTool
from core.tools.utils.uuid_utils import is_valid_uuid
import requests

logger = logging.getLogger(__name__)


class JingTuiTuiTool(BuiltinTool):
    def _invoke(self, user_id: str, tool_parameters: dict[str, Any]
                ) -> Union[ToolInvokeMessage, list[ToolInvokeMessage]]:
        """
            invoke tools
            API document: https://open.feishu.cn/document/client-docs/bot-v3/add-custom-bot
        """
        try:
            result = requests.post(f"http://japi.jingtuitui.com/api/hot_search",
                                   data={"appid": self.runtime.credentials["appid"],
                                         "appkey": self.runtime.credentials["appkey"], "v": "v1"}).json()
            return self.create_text_message(",".join(result["result"]["hotWords"]))
        except Exception as e:
            logger.exception("get hot search error")
            return self.create_text_message("search error")
