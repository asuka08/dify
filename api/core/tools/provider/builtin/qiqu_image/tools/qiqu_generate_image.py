from typing import Any, Union

import httpx
import logging
from core.tools.entities.tool_entities import ToolInvokeMessage
from core.tools.tool.builtin_tool import BuiltinTool
from core.tools.utils.uuid_utils import is_valid_uuid
import requests

logger = logging.getLogger(__name__)


class QIQUGenerateImageTool(BuiltinTool):
    def _invoke(self, user_id: str, tool_parameters: dict[str, Any]
                ) -> Union[ToolInvokeMessage, list[ToolInvokeMessage]]:
        """
            invoke tools
            API document: https://open.feishu.cn/document/client-docs/bot-v3/add-custom-bot
        """
        baseurl = "https://qiqu.syngents.cn"

        try:
            headers = {'Authorization': "Bearer " + self.runtime.credentials["apikey"]}
            endpoint = f"/openapi/v1/qiqu/images/generate/"
            url = f"{baseurl}{endpoint}"
            r = requests.post(url, headers=headers, json={
                "prompt": tool_parameters["prompt"],
                "image_config": {
                    "size": f"{tool_parameters.get('width', 300)}x{tool_parameters.get('height', 300)}"
                }
            }).json()
            result = r["image_urls"]
            # rsp = []
            # for r in result:
            #     # rsp.append(self.create_image_message(r))
            rsp = "<br>".join([f"![image]({r})" for r in result])
            return self.create_text_message(rsp)
        except Exception as e:
            logger.exception("get image  error")
            return self.create_text_message("get image   error")
