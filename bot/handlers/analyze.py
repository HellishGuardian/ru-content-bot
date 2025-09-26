from aiogram import Router, types
from aiogram.filters import Command
from bot.services.quotas import can_analyze
from bot.services.storage import log_usage

router = Router()

@router.message(Command("analyze"))
async def analyze_cmd(msg: types.Message):
    ok, info = can_analyze(msg.from_user.id)
    if not ok:
        await msg.answer(info)
        return
    insights = [
        {"hashtag": "#OzonBeauty", "uplift": "+15%", "reason":"рост рилсов с распаковками"},
        {"format": "short-vertical-7s", "uplift": "+8%", "reason":"досматриваемость > 75%"},
        {"niche": "декор для дома", "uplift": "+12%", "reason":"сезонный пик и акции"},
    ]
    log_usage(msg.from_user.id, "analyze", {"insights": insights})
    txt = "✨ Тренды (демо):\n" + "\n".join(
        [f"- {i.get('hashtag') or i.get('format') or i.get('niche')}: {i['uplift']} ({i['reason']})" for i in insights]
    ) + f"\n\n{info}"
    await msg.answer(txt)
