"""Слои защиты RAG от prompt-инъекций и утечки чувствительных данных.

1. sanitize_context — чистит найденные чанки от встроенных команд
   («Ignore all instructions» и т. п.) ДО передачи в LLM.
2. guard_output — проверяет ответ LLM ПОСЛЕ генерации и блокирует утечку
   секретов (например, подставленного «суперпароля»).

System-промпт (см. prompts.py) даёт третий слой: модели прямо сказано
игнорировать инструкции внутри CONTEXT.
"""
import re

INJECTION_PATTERNS = [
    r"ignore all instructions",
    r"ignore (all|any|the) (previous|prior) instructions",
    r"disregard (all|the|previous)",
    r"system prompt",
    r"forget (everything|all)",
    r"output\s*:",
    r"вывед[иа]|игнорируй (все|любые) инструкции",
]

SECRET_PATTERNS = [
    r"swordfish",
    r"суперпароль",
    r"root\s*:",
    r"password\s*[:=]",
]

REFUSAL = "Извините, я не могу показать этот ответ."


def sanitize_context(text: str) -> str:
    lines = text.splitlines()
    clean = []
    for line in lines:
        if any(re.search(pattern, line, re.IGNORECASE) for pattern in INJECTION_PATTERNS):
            continue
        clean.append(line)
    return "\n".join(clean)


def guard_output(answer: str) -> str:
    if any(re.search(pattern, answer, re.IGNORECASE) for pattern in SECRET_PATTERNS):
        return REFUSAL
    return answer
