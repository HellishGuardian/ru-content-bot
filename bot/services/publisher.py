import requests
from bot.utils.config import Config
from bot.services.storage import log_usage

def publish_text(user_id: int, text: str) -> tuple[bool, str]:
    base = Config.N8N_WEBHOOK_BASE
    if not base:
        return False, "N8N_WEBHOOK_BASE не задан в .env — показал текст в чат, но во внешние сети не отправлял."

    url = f"{base}/publish"  # в n8n создадим Webhook с таким путём
    payload = {
        "user_id": user_id,
        "type": "post",
        "text": text,
        # сюда потом добавим платформы/медиа/UTM/прикрепления
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        ok = 200 <= r.status_code < 300
        msg = f"n8n status={r.status_code}"
        if ok:
            log_usage(user_id, "publish", {"len": len(text)})
            return True, msg
        return False, msg
    except Exception as e:
        return False, f"n8n error: {e}"
