# D:\Projects\ru-content-bot\bot\services\generator.py
from __future__ import annotations
import json
import requests
from bot.utils.config import Config


def _template_variants(prompt: str, profile: dict | None):
    """Запасной вариант: простые шаблоны A/B."""
    style = (profile or {}).get("style") or "ru-playful"
    audience = (profile or {}).get("audience") or "ru"
    a = (f"🔥 {prompt}\n\nКороткий лид + буллеты.\n"
         f"• Факт/выгода #1\n• Факт/выгода #2\n• Призыв к действию.\n"
         f"Тон: {style}, аудитория: {audience}.")
    b = (f"🧪 {prompt}\n\nХук-вопрос + мини-история (1 абзац).\n"
         f"В конце — явный CTA и эмодзи.\nТон: {style}, аудитория: {audience}.")
    return {"A": {"text": a, "pred": 0.52}, "B": {"text": b, "pred": 0.56}}


def _bad(s: str) -> bool:
    """
    Фильтр «битых» ответов: слишком коротко, содержит служебное «undefined/json»,
    или выглядит как необработанный JSON.
    """
    x = (s or "").strip()
    xl = x.lower()
    return (
        len(x) < 10
        or "undefined" in xl
        or "json" in xl
        or xl.startswith("{")
        or xl.startswith("[")
    )


def generate_variants(prompt: str, profile: dict | None, *, force_template: bool = False) -> dict:
    """
    Возвращает {"A": {"text": "...", "pred": ...}, "B": {...}}.
    - Если n8n недоступен или пришло «битое» содержимое — возвращает шаблоны.
    """
    if force_template:
        return _template_variants(prompt, profile)

    base = (Config.N8N_WEBHOOK_BASE or "").rstrip("/")
    if base:
        try:
            r = requests.post(
                f"{base}/generate_text",
                json={"prompt": prompt, "profile": profile or {}},
                timeout=40,
            )
            r.raise_for_status()
            data = r.json()

            # Поддержка двух форматов ответа n8n:
            if "variants" in data:
                v = data["variants"]
                A_text = (v.get("A", {}).get("text", "") or "").strip()
                B_text = (v.get("B", {}).get("text", "") or "").strip()
                predA = float(v.get("A", {}).get("pred", 0.55))
                predB = float(v.get("B", {}).get("pred", 0.57))
            else:
                A_text = (data.get("A", "") or "").strip()
                B_text = (data.get("B", "") or "").strip()
                predA = float(data.get("predA", 0.55))
                predB = float(data.get("predB", 0.57))

            # ❗ Подстраховка: если тексты пустые/подозрительные — вернём шаблоны
            if _bad(A_text) or _bad(B_text):
                return _template_variants(prompt, profile)

            return {
                "A": {"text": A_text, "pred": predA},
                "B": {"text": B_text, "pred": predB},
            }
        except Exception:
            # Любая ошибка сети/формата — используем шаблоны
            return _template_variants(prompt, profile)

    # Если N8N_WEBHOOK_BASE не задан
    return _template_variants(prompt, profile)
