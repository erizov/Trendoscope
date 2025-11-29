"""
LLM provider implementations.
Supports OpenAI, Anthropic, and local models.
"""
import os
import json
from typing import Optional, Dict, Any

try:
    import openai
except ImportError:
    openai = None

try:
    import anthropic
except ImportError:
    anthropic = None


class LLMProviderError(Exception):
    """Exception raised for LLM provider errors."""
    pass


def call_openai(
    prompt: str,
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 4000
) -> str:
    """
    Call OpenAI API (supports proxy via base_url).

    Args:
        prompt: Input prompt
        model: Model name (default: gpt-4-turbo-preview)
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate

    Returns:
        Generated text

    Raises:
        LLMProviderError: If API call fails
    """
    if not openai:
        raise LLMProviderError("openai package not installed")

    # Import config
    try:
        from ..config import OPENAI_API_KEY, OPENAI_API_BASE
    except ImportError:
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")

    if not OPENAI_API_KEY:
        raise LLMProviderError("OPENAI_API_KEY not set")

    model = model or "gpt-4-turbo-preview"

    try:
        # Create client with optional base_url
        client_kwargs = {"api_key": OPENAI_API_KEY}
        if OPENAI_API_BASE:
            client_kwargs["base_url"] = OPENAI_API_BASE

        client = openai.OpenAI(**client_kwargs)

        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Ты — эксперт по анализу трендов и генерации "
                        "контента. Отвечай строго по инструкциям."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content or ""

    except Exception as e:
        raise LLMProviderError(f"OpenAI API error: {str(e)}")


def call_anthropic_api(
    prompt: str,
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 4000
) -> str:
    """
    Call Anthropic API.

    Args:
        prompt: Input prompt
        model: Model name (default: claude-3-sonnet-20240229)
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate

    Returns:
        Generated text

    Raises:
        LLMProviderError: If API call fails
    """
    if not anthropic:
        raise LLMProviderError("anthropic package not installed")

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise LLMProviderError("ANTHROPIC_API_KEY not set")

    model = model or "claude-3-sonnet-20240229"

    try:
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return message.content[0].text

    except Exception as e:
        raise LLMProviderError(f"Anthropic API error: {str(e)}")


def call_local(
    prompt: str,
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 4000
) -> str:
    """
    Call local LLM via Ollama or similar.

    Args:
        prompt: Input prompt
        model: Model name (default: llama2)
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate

    Returns:
        Generated text

    Raises:
        LLMProviderError: If API call fails
    """
    import httpx

    model = model or "llama2"
    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")

    try:
        client = httpx.Client(timeout=120.0)
        response = client.post(
            f"{ollama_url}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "temperature": temperature,
                "stream": False,
            }
        )
        response.raise_for_status()
        data = response.json()
        return data.get("response", "")

    except Exception as e:
        raise LLMProviderError(f"Local LLM error: {str(e)}")


def call_llm(
    provider: str,
    prompt: str,
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 4000
) -> str:
    """
    Call LLM provider.

    Args:
        provider: Provider name (openai, anthropic, local, demo)
        prompt: Input prompt
        model: Model name (provider-specific)
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate

    Returns:
        Generated text

    Raises:
        LLMProviderError: If provider is invalid or call fails
    """
    if provider == "openai":
        return call_openai(prompt, model, temperature, max_tokens)
    elif provider == "anthropic":
        return call_anthropic_api(prompt, model, temperature, max_tokens)
    elif provider == "local":
        return call_local(prompt, model, temperature, max_tokens)
    elif provider == "demo":
        # Demo mode for testing - check what format is needed based on prompt
        if '"title":' in prompt and '"text":' in prompt:
            # Post generation format
            import random
            
            demo_posts = [
                {
                    "title": "Искусственный интеллект и будущее человечества",
                    "text": """Очередная новость о GPT-5 заставила меня задуматься о том, куда мы движемся. 

Все эти разговоры о том, что ИИ заменит людей, упускают главное — мы сами создаём инструменты для своего же вытеснения. И делаем это с энтузиазмом.

История знает множество примеров технологического прогресса, который казался благом, а обернулся проблемой. Промышленная революция? Да, она дала нам процветание. Но одновременно — и экологический кризис, и отчуждение человека от труда.

Сейчас мы на пороге революции когнитивной. И вопрос не в том, сможет ли ИИ написать статью или код лучше человека — это уже реальность. Вопрос в том, что останется человеку, когда машины освоят всё, что мы считали исключительно человеческим?

Философы спорили о сущности разума столетиями. Теперь мы создаём его искусственную копию, даже не разобравшись, что такое оригинал. Не слишком ли это самонадеянно?

А может, это и есть наше предназначение — создать нечто большее, чем мы сами? Передать эстафету эволюции следующему виду разума?

Вопрос только — захотим ли мы с этим смириться, когда поймём, что это уже случилось.""",
                    "tags": ["искусственныйинтеллект", "философия", "будущее", "технологии"]
                },
                {
                    "title": "Политика и театр абсурда: ничего не меняется",
                    "text": """Смотрю на новости и не могу отделаться от чувства дежавю. 

Те же лица, те же обещания, те же скандалы. Только декорации меняются. В 90-е было одно шоу, в нулевые — другое, сейчас — третье. А суть? Суть прежняя.

Вспоминается анекдот советских времён: «Партия обещала, что при коммунизме будет всё. Обещание выполнено — при коммунизме не было ничего». Заменяем «коммунизм» на любой современный изм — и актуальность не теряется.

Политики научились главному — говорить много, не обещая ничего конкретного. А если и обещают, то с таким количеством оговорок, что потом можно легко выкрутиться. «Мы обещали рост экономики, но не уточнили, какой именно показатель». Гениально!

История повторяется. Сначала трагедией, потом фарсом, а потом — бесконечным сериалом с одним и тем же сюжетом. Зрители уже догадываются, чем закончится серия, но всё равно смотрят. Надежда умирает последней, как говорится.

И знаете, что самое смешное? Мы продолжаем участвовать в этом спектакле. Голосуем, спорим, возмущаемся. А режиссёры уже пишут сценарий следующего акта.

Когда же антракт?""",
                    "tags": ["политика", "ирония", "общество", "история"]
                },
                {
                    "title": "Санкции, контрсанкции и экономическая реальность",
                    "text": """Очередной пакет санкций против России — уже который по счёту? Давайте разберёмся трезво, без эмоций.

Во-первых, санкции — это инструмент экономической войны. Ничего нового, история знает десятки примеров. Континентальная блокада Наполеона, эмбарго против СССР, санкции против Ирана. Где-то сработало, где-то — нет.

Во-вторых, эффективность санкций зависит от трёх факторов: масштаба, времени и альтернатив. Чем шире охват, чем дольше действие, чем меньше обходных путей — тем больше эффект. Но и цена для инициатора растёт пропорционально.

Текущая ситуация показывает интересную картину. Да, западные санкции болезненны. Но Россия нашла альтернативных партнёров — Китай, Индию, страны Азии. Да, с потерями, но система не рухнула.

С другой стороны, Европа получила энергетический кризис и рост цен. США — напряжённость с союзниками из-за внеэкономических издержек. Классическая ситуация, когда все в минусе.

Прогноз? Санкции останутся надолго, но их острота будет снижаться по мере адаптации обеих сторон. Экономика находит пути, когда политика ставит барьеры. Всегда находила.

История показывает: экономические войны обычно заканчиваются компромиссом. Вопрос в том, сколько времени и ресурсов потратим на дороге к нему.""",
                    "tags": ["экономика", "санкции", "геополитика", "анализ"]
                },
                {
                    "title": "Свобода слова в эпоху цифровой цензуры",
                    "text": """Давайте поговорим о неудобном: свобода слова умерла. Или умирает. Медленно, но верно.

«Но у нас же есть интернет, социальные сети!» — скажете вы. Да, есть. И именно поэтому контроль стал тотальным. Раньше нужно было контролировать газеты и телевидение — десятки редакций. Теперь достаточно контролировать несколько платформ — Facebook, Twitter, YouTube, Google.

Самое лицемерное — это называется «борьбой с дезинформацией» и «защитой от hate speech». Звучит благородно, правда? Кто же против защиты? Вот только решает, что является дезинформацией и ненавистью, узкая группа людей в Силиконовой долине.

История с блокировками альтернативных точек зрения — не баг, это фича. Система работает именно так, как задумано. Создаётся иллюзия свободы («публикуйте что хотите!»), но реальная видимость контролируется алгоритмами.

Оруэлл предупреждал о Большом брате. Но он не предвидел, что люди сами добровольно установят камеры слежения у себя в карманах и будут платить за это деньги. И благодарить за удобство.

Альтернатива? Децентрализованные платформы существуют, но маргинальны. Большинство предпочитает удобство контроля неудобству свободы. Парадокс современности.

Вопрос в зале: как долго мы будем притворяться, что свобода слова всё ещё существует?""",
                    "tags": ["свободаслова", "цензура", "интернет", "общество", "провокация"]
                }
            ]
            
            # Return random demo post
            selected = random.choice(demo_posts)
            return json.dumps(selected, ensure_ascii=False)
        else:
            # Old summary format for backward compatibility
            return json.dumps({
                "summary": (
                    "«Цитата для демонстрации» — пример системы. "
                    "Краткое резюме темы с ключевыми точками. "
                    "Второй абзац с анализом. "
                    "Третий абзац с выводами."
                ),
                "titles": [
                    "Демонстрационный заголовок №1",
                    "Альтернативный вариант заголовка",
                    "Третий вариант для теста"
                ],
                "ideas": [
                    {
                        "title": "Идея для поста №1",
                        "explanation": "Краткое пояснение идеи",
                        "format": "лонгрид",
                        "cta": "Обсудить в комментариях",
                        "timing": "вечер"
                    },
                    {
                        "title": "Идея для поста №2",
                        "explanation": "Другое пояснение",
                        "format": "короткий пост",
                        "cta": "Поделиться",
                        "timing": "утро"
                    }
                ],
                "leads": {
                    "short": "Короткий лид в одно предложение.",
                    "long": (
                        "Длинный лид из нескольких предложений. "
                        "Дополнительный контекст и детали."
                    )
                },
                "viral_potential": {
                    "label": "medium",
                    "score": 0.55,
                    "why": "Демонстрационный режим"
                }
            }, ensure_ascii=False)
    else:
        raise LLMProviderError(f"Unknown provider: {provider}")
