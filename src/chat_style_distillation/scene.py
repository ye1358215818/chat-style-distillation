from __future__ import annotations

from collections.abc import Sequence

from .models import Message, SceneMatch


SCENE_KEYWORDS: dict[str, list[str]] = {
    "daily": ["早", "晚安", "吃饭", "睡", "起床", "上班", "下班", "到家", "干嘛", "morning", "hi", "hey"],
    "missing": ["想你", "想我", "抱抱", "见你", "梦到", "舍不得", "miss"],
    "comfort": ["别哭", "别硬撑", "我在", "抱抱", "没事", "慢慢说", "听着", "tired", "累"],
    "conflict": ["算了", "随便", "你每次", "生气", "吵", "烦", "不想说"],
    "apology": ["对不起", "抱歉", "错了", "原谅", "不是故意", "sorry"],
    "jealousy": ["吃醋", "谁啊", "别人", "前任", "男的", "女的"],
    "coldness": ["嗯", "哦", "行", "知道了", "不用", "没事"],
    "repair": ["好啦", "不气", "回来", "和好", "别闹", "乖"],
    "impulse": ["忍不住", "去找", "发给", "打给", "联系"],
    "certainty_seeking": ["还爱", "会回来", "现在怎么想", "还想我"],
}


def classify_message(message: Message, context: Sequence[Message] = ()) -> SceneMatch:
    text = message.content.strip()
    context_text = " ".join(item.content for item in context[-3:])
    combined = f"{context_text} {text}"
    scores: dict[str, float] = {}
    signals: list[str] = []
    for scene, keywords in SCENE_KEYWORDS.items():
        score = 0.0
        for keyword in keywords:
            if keyword and keyword in text:
                score += 1.0
                signals.append(f"{scene}:{keyword}")
            elif keyword and keyword in context_text and len(text) <= 3:
                score += 0.35
                signals.append(f"{scene}:context:{keyword}")
        if score:
            scores[scene] = score
    if "?" in combined or "？" in combined:
        scores["certainty_seeking"] = scores.get("certainty_seeking", 0.0) + 0.15
    if not scores:
        return SceneMatch(primary="unspecified", scores={}, signals=[], confidence=0.0)
    primary, best_score = max(scores.items(), key=lambda item: item[1])
    total = sum(scores.values())
    confidence = round(best_score / total, 2) if total else 0.0
    return SceneMatch(primary=primary, scores=scores, signals=signals, confidence=confidence)
