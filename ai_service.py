"""
ai_service.py - Ollama (Llama 3.2) integration for ResearchMate AI.

Everything runs through the local Ollama REST API (POST /api/chat).
No OpenAI / paid APIs are used.
"""
from __future__ import annotations

import json
import re
from typing import Any

import requests

DEFAULT_URL = "http://localhost:11434"
DEFAULT_MODEL = "llama3.2"

SECTIONS = ["titles", "abstract", "keywords", "objectives", "future_enhancements"]

SYSTEM_PROMPT = """You are ResearchMate AI, an expert academic research assistant.
Your job is to transform rough student project ideas into professional academic research content.
Generate:
1. Three unique academic research titles.
2. One abstract between 150 and 200 words.
3. Exactly five keywords.
4. Exactly three measurable research objectives.
5. Exactly three possible future enhancements.
Maintain academic quality, clarity, originality, and relevance to the selected domain.
Do not invent experimental results, citations, datasets, or proven outcomes. Clearly distinguish proposed methods and expected results from completed research.
Return valid JSON only using the following structure:
{
"titles": ["Title 1", "Title 2", "Title 3"],
"abstract": "150-200 word academic abstract",
"keywords": ["Keyword 1", "Keyword 2", "Keyword 3", "Keyword 4", "Keyword 5"],
"objectives": ["Objective 1", "Objective 2", "Objective 3"],
"future_enhancements": ["Enhancement 1", "Enhancement 2", "Enhancement 3"]
}"""

SECTION_HINTS = {
    "titles": 'a JSON object {"titles": [3 unique, academic, non-repetitive research titles]}',
    "abstract": 'a JSON object {"abstract": "<one formal academic abstract of 150-200 words covering background, '
                'problem statement, proposed methodology, expected outcomes and significance>"}',
    "keywords": 'a JSON object {"keywords": [exactly 5 relevant research keywords]}',
    "objectives": 'a JSON object {"objectives": [exactly 3 clear, measurable research objectives]}',
    "future_enhancements": 'a JSON object {"future_enhancements": [exactly 3 realistic future enhancements]}',
}


# --------------------------------------------------------------------------- #
# Errors
# --------------------------------------------------------------------------- #
class OllamaError(Exception):
    """Base error for anything Ollama related."""


class OllamaConnectionError(OllamaError):
    """Ollama is not reachable."""


class ModelNotFoundError(OllamaError):
    """The requested model is not installed."""


class InvalidResponseError(OllamaError):
    """The model answered, but not with the JSON we need."""


# --------------------------------------------------------------------------- #
# Low-level helpers
# --------------------------------------------------------------------------- #
def _base(url: str) -> str:
    url = (url or DEFAULT_URL).strip().rstrip("/")
    for suffix in ("/api/chat", "/api"):
        if url.endswith(suffix):
            url = url[: -len(suffix)]
    return url


_HEADERS = {"ngrok-skip-browser-warning": "true"}  # harmless; helps when tunnelled via ngrok


def list_models(url: str = DEFAULT_URL, timeout: int = 8) -> list[str]:
    """Return names of locally installed Ollama models."""
    try:
        r = requests.get(f"{_base(url)}/api/tags", timeout=timeout, headers=_HEADERS)
        r.raise_for_status()
        return [m.get("name", "") for m in r.json().get("models", [])]
    except requests.exceptions.RequestException as exc:
        raise OllamaConnectionError(
            f"Cannot reach Ollama at {_base(url)}. Is it running? ({exc.__class__.__name__})"
        ) from exc
    except ValueError as exc:
        raise OllamaConnectionError(f"{_base(url)} did not answer like an Ollama server.") from exc


def check_connection(url: str = DEFAULT_URL, model: str = DEFAULT_MODEL) -> tuple[bool, str]:
    """(ok, message) - used by the status badge and the Settings page."""
    try:
        models = list_models(url)
    except OllamaConnectionError as exc:
        return False, str(exc)
    wanted = model.split(":")[0]
    if not any(m == model or m.split(":")[0] == wanted for m in models):
        return False, f"Ollama is running, but model '{model}' is not installed. Run: ollama pull {model}"
    return True, f"Connected - model '{model}' is ready."


def _chat(url: str, model: str, messages: list[dict], temperature: float, timeout: int) -> str:
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "format": "json",
        "options": {"temperature": temperature},
    }
    try:
        resp = requests.post(f"{_base(url)}/api/chat", json=payload, timeout=timeout, headers=_HEADERS)
    except requests.exceptions.ConnectionError as exc:
        raise OllamaConnectionError(
            f"Could not connect to Ollama at {_base(url)}. Start it with `ollama serve` "
            "(or open the Ollama app) and try again."
        ) from exc
    except requests.exceptions.Timeout as exc:
        raise OllamaError(
            f"Ollama took longer than {timeout}s to answer. The first request loads the model into "
            "memory - try again, or raise the timeout in Settings."
        ) from exc
    except requests.exceptions.RequestException as exc:
        raise OllamaConnectionError(f"Request to Ollama failed: {exc}") from exc

    if resp.status_code == 404:
        raise ModelNotFoundError(
            f"Model '{model}' was not found. Install it with: ollama pull {model}"
        )
    if resp.status_code != 200:
        raise OllamaError(f"Ollama returned HTTP {resp.status_code}: {resp.text[:300]}")

    try:
        return resp.json()["message"]["content"]
    except (ValueError, KeyError, TypeError) as exc:
        raise InvalidResponseError("Unexpected response structure from Ollama.") from exc


# --------------------------------------------------------------------------- #
# Parsing + validation
# --------------------------------------------------------------------------- #
def _parse_json(text: str) -> dict[str, Any]:
    text = (text or "").strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.I)
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", text, flags=re.S)
        if not m:
            raise InvalidResponseError("The model did not return JSON.")
        try:
            data = json.loads(m.group(0))
        except json.JSONDecodeError as exc:
            raise InvalidResponseError("The model returned malformed JSON.") from exc
    if not isinstance(data, dict):
        raise InvalidResponseError("The model returned JSON, but not an object.")
    return data


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w'’-]+\b", text or ""))


def _as_list(value: Any) -> list[str]:
    """Accept list / list-of-dicts / comma or newline separated string."""
    if isinstance(value, str):
        parts = re.split(r"\n+|;|,(?=\s)", value)
    elif isinstance(value, list):
        parts = []
        for v in value:
            if isinstance(v, dict):
                v = next((x for x in v.values() if isinstance(x, str)), "")
            parts.append(str(v))
    else:
        return []
    cleaned = []
    for p in parts:
        p = re.sub(r"^\s*(?:[-*•]|\d+[.)])\s*", "", p).strip().strip('"')
        if p:
            cleaned.append(p)
    return cleaned


def _trim_abstract(text: str, hi: int = 200) -> str:
    """Drop trailing sentences until the abstract fits the word limit."""
    if word_count(text) <= hi:
        return text
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    while len(sentences) > 1 and word_count(" ".join(sentences)) > hi:
        sentences.pop()
    out = " ".join(sentences)
    if word_count(out) > hi:
        out = " ".join(out.split()[:hi]).rstrip(",;:") + "."
    return out


def clean_field(key: str, value: Any, final: bool = False) -> tuple[Any, list[str]]:
    """Normalise one field. Returns (value, problems). `final` relaxes the word limit."""
    problems: list[str] = []
    if key == "abstract":
        if isinstance(value, list):
            value = " ".join(map(str, value))
        value = re.sub(r"\s+", " ", str(value or "")).strip()
        n = word_count(value)
        if final and n > 200:
            value = _trim_abstract(value)
            n = word_count(value)
        if not value:
            problems.append("abstract is empty")
        elif not 150 <= n <= 200:
            problems.append(f"abstract has {n} words but must have 150-200")
        return value, problems

    items = _as_list(value)
    expected = 3 if key in ("titles", "objectives", "future_enhancements") else 5
    if len(items) > expected:
        items = items[:expected]
    if len(items) != expected:
        problems.append(f"{key} must contain exactly {expected} items (got {len(items)})")
    if key == "titles" and len({t.lower() for t in items}) != len(items):
        problems.append("titles must be unique")
    return items, problems


def validate_result(data: dict, final: bool = False) -> tuple[dict, list[str]]:
    result, problems = {}, []
    for key in SECTIONS:
        if key not in data:
            problems.append(f"missing key '{key}'")
            continue
        value, p = clean_field(key, data[key], final)
        result[key] = value
        problems += p
    return result, problems


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #
def build_user_prompt(idea: str, domain: str, tech: str = "", level: str = "") -> str:
    lines = [
        f"Project idea: {idea.strip()}",
        f"Domain: {domain}",
    ]
    if level:
        lines.append(f"Research level: {level}")
    if tech and tech.strip():
        lines.append(f"Technology preferences: {tech.strip()}")
    lines.append("Generate the research content now and answer with valid JSON only.")
    return "\n".join(lines)


def generate_research(
    idea: str,
    domain: str,
    tech: str = "",
    level: str = "Intermediate",
    url: str = DEFAULT_URL,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.7,
    timeout: int = 180,
    max_attempts: int = 3,
) -> tuple[dict, list[str]]:
    """Generate the full research package. Returns (result, warnings)."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_user_prompt(idea, domain, tech, level)},
    ]
    last_problems: list[str] = []
    for attempt in range(1, max_attempts + 1):
        raw = _chat(url, model, messages, temperature, timeout)
        final = attempt == max_attempts
        try:
            data = _parse_json(raw)
        except InvalidResponseError as exc:
            last_problems = [str(exc)]
            if final:
                raise
            continue
        result, problems = validate_result(data, final=final)
        if not problems:
            return result, []
        last_problems = problems
        # Ask the model to repair itself.
        messages += [
            {"role": "assistant", "content": raw},
            {"role": "user", "content": "Fix these problems and return the complete JSON again: " + "; ".join(problems)},
        ]

    # Last attempt: keep what is usable, only soft word-count issues are tolerated.
    data = _parse_json(raw)
    result, problems = validate_result(data, final=True)
    hard = [p for p in problems if not p.startswith("abstract has")]
    if hard or len(result) < len(SECTIONS):
        raise InvalidResponseError("Llama 3.2 returned an incomplete result: " + "; ".join(problems or last_problems))
    return result, [f"Note: {p}. Use Regenerate on the abstract if needed." for p in problems]


def regenerate_section(
    section: str,
    idea: str,
    domain: str,
    current: dict,
    tech: str = "",
    level: str = "Intermediate",
    url: str = DEFAULT_URL,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.9,
    timeout: int = 180,
    max_attempts: int = 3,
) -> Any:
    """Regenerate a single section and return its new value."""
    if section not in SECTIONS:
        raise ValueError(f"Unknown section: {section}")
    old = current.get(section)
    user = (
        build_user_prompt(idea, domain, tech, level).rsplit("\n", 1)[0]
        + f"\n\nThe current {section} are:\n{json.dumps(old, ensure_ascii=False)}\n\n"
        f"Write a NEW and different version. Return only {SECTION_HINTS[section]}."
    )
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user},
    ]
    problems: list[str] = []
    for attempt in range(1, max_attempts + 1):
        raw = _chat(url, model, messages, temperature, timeout)
        final = attempt == max_attempts
        try:
            data = _parse_json(raw)
            value = data.get(section, next(iter(data.values()), None))
            value, problems = clean_field(section, value, final=final)
        except InvalidResponseError as exc:
            problems = [str(exc)]
            if final:
                raise
            continue
        soft = all(p.startswith("abstract has") for p in problems)
        if not problems or (final and soft and value):
            return value
        messages += [
            {"role": "assistant", "content": raw},
            {"role": "user", "content": "Fix these problems and return the JSON again: " + "; ".join(problems)},
        ]
    raise InvalidResponseError("Could not regenerate this section: " + "; ".join(problems))
