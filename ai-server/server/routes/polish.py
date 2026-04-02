from fastapi import APIRouter, HTTPException
from openai import AsyncOpenAI
from pydantic import BaseModel

from .. import config

router = APIRouter()


class PolishRequest(BaseModel):
    content: str


@router.post("/webrtc/polish")
async def polish_sentence(payload: PolishRequest):
    if not payload.content.strip():
        return {"polishedText": ""}

    if not config.LLM_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="AI 润色未配置 LLM_API_KEY，请在 ai-server/.env 中配置相关参数并重启服务。",
        )

    try:
        client = AsyncOpenAI(
            api_key=config.LLM_API_KEY,
            base_url=config.LLM_BASE_URL,
        )

        system_prompt = """
你是一个专业的手语翻译润色助手。

# Task
我会给你一组手语识别系统输出的零碎词汇（Gloss），请你将它们组合、润色成一句符合中文日常表达习惯的流畅句子。

# Rules
1. 保持原意：不要随意添加无关的细节或过度联想。
2. 纠正语序：手语常使用倒装或宾语前置，请调整为主谓宾结构。
3. 补充虚词：适当补充“的、了、是、在”等助词，使句子连贯。
4. 极简输出：只输出润色后的最终句子，绝对不要包含任何解释、问候语或标点符号的多余前缀。

# Example
输入：我 昨天 医院 去 看病
输出：我昨天去医院看病了。

输入：你 叫 名字 什么
输出：你叫什么名字？
"""
        response = await client.chat.completions.create(
            model=config.LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt.strip()},
                {"role": "user", "content": f"输入：{payload.content.strip()}"},
            ],
            temperature=0.3,
        )

        polished_text = response.choices[0].message.content.strip()
        if polished_text.startswith("输出："):
            polished_text = polished_text[3:]

        return {"polishedText": polished_text}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"AI 服务调用失败: {str(exc)}") from exc
