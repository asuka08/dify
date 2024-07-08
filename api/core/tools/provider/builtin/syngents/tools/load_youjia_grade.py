import io
import logging
from typing import Any, Union

import pandas as pd
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
        file_url = tool_parameters.get('file_url', '')

        try:
            result = ""
            scores = self.read_excel(file_url)
            brain_types, sorted_learning_types, scores_prompt = self.compute_scores_and_classify(scores)
            midway_msg = f"我们根据您的测评表从“左脑”、“左脑优点”、“右脑”、“右脑优点”四个维度、“听觉型”、“视觉型”、“体觉型”三个类型进行分数计算。以下是您的得分结果：{scores_prompt}"
            result = f"{midway_msg}"
            return self.create_text_message(result)
        except Exception as e:
            logger.exception("get data error")
            return self.create_text_message("get data error")

    def compute_scores_and_classify(self, scores_array):
        total_scores = sum(scores_array)
        # 对应的学习类型
        learning_types = ["听觉型", "视觉型", "体觉型"]

        left_brain_score = sum(scores_array[:10])
        left_brain_good_score = sum(scores_array[:5])
        right_brain_score = sum(scores_array[10:])
        right_brain_good_score = sum(scores_array[10:15])

        print(left_brain_score, right_brain_score)
        left_brain_score[-1], right_brain_score[-1] = right_brain_score[-1], left_brain_score[-1]  # 修正体觉的左右脑分数
        left_brain_good_score[-1], right_brain_good_score[-1] = right_brain_good_score[-1], left_brain_good_score[-1]
        print(left_brain_score, right_brain_score)

        scores_prompt = f"""
            听觉得分：{total_scores[0]}分；视觉得分：{total_scores[1]}分；体觉得分：{total_scores[2]}分；

            听觉-左脑得分：{left_brain_score[0]}分；听觉-右脑得分：{right_brain_score[0]}分；
            听觉-左脑优点得分：{left_brain_good_score[0]}分；听觉-右脑优点得分：{right_brain_good_score[0]}分；

            视觉-左脑得分：{left_brain_score[1]}分；视觉-右脑得分：{right_brain_score[1]}分；
            视觉-左脑优点得分：{left_brain_good_score[1]}分；视觉-右脑优点得分：{right_brain_good_score[1]}分；

            体觉-左脑得分：{left_brain_score[2]}分；体觉-右脑得分：{right_brain_score[2]}分；
            体觉-左脑优点得分：{left_brain_good_score[2]}分；体觉-右脑优点得分：{right_brain_good_score[2]}分；
        """

        brain_types = ["听觉型", "视觉型", "体觉型"]
        for i in range(3):
            brain_type = "：左高右低" if left_brain_score[i] > right_brain_score[i] else "：右高左低"
            brain_types[i] = brain_types[i] + brain_type

            # 将学习类型和分数打包为元组列表
        scored_learning_types = list(zip(learning_types, total_scores))
        # print(scored_learning_types)
        # 对列表进行排序，基于分数从大到小
        sorted_learning_types = sorted(scored_learning_types, key=lambda x: x[1], reverse=True)
        sorted_learning_types = [sorted_learning_types[i][0] for i in range(len(sorted_learning_types))]

        return brain_types, sorted_learning_types, scores_prompt

    def read_excel(self, file_url):
        response = requests.get(file_url)
        df = pd.read_excel(io.BytesIO(response.content))
        df.head()

        scores_df = df[['Unnamed: 2', 'Unnamed: 6', 'Unnamed: 10']]

        scores_df = scores_df.dropna().applymap(lambda x: ''.join(filter(str.isdigit, str(x))))

        def clean_and_convert_to_float(x):
            cleaned = ''.join(filter(str.isdigit, str(x)))
            return float(cleaned) if cleaned else None

        scores_df_cleaned = scores_df.applymap(clean_and_convert_to_float)
        scores_df_cleaned.dropna(how='all', inplace=True)
        scores_array = scores_df_cleaned.to_numpy()

        return scores_array
