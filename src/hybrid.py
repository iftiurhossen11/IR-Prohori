import os
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ============ BANGLISH NORMALIZER ============
BANGLISH_MAP = {
    "kemon": "কেমন", "kemun": "কেমন", "aso": "আছো", "acho": "আছো",
    "asen": "আছেন", "bolo": "বলো", "bol": "বলো", "ki": "কী",
    "kotha": "কথা", "koro": "করো", "korte": "করতে", "korbo": "করব",
    "zai": "যায়", "jai": "যায়", "zabe": "যাবে", "habe": "হবে",
    "hobe": "হবে", "hoy": "হয়", "tumi": "তুমি", "tui": "তুই",
    "ami": "আমি", "amake": "আমাকে", "tomake": "তোমাকে",
    "amar": "আমার", "tomar": "তোমার", "kothay": "কোথায়",
    "kivabe": "কিভাবে", "kibhabe": "কিভাবে", "keno": "কেন",
    "valo": "ভালো", "bhalo": "ভালো", "kharap": "খারাপ",
    "onek": "অনেক", "ektu": "একটু", "akta": "একটা", "ekta": "একটা",
    "kisu": "কিছু", "kichu": "কিছু", "sob": "সব", "shob": "সব",
    "na": "না", "nai": "নাই", "hoina": "হয় না", "hoyna": "হয় না",
    "pari": "পারি", "paro": "পারো", "parbe": "পারবে", "parbo": "পারব",
    "dao": "দাও", "daw": "দাও", "den": "দিন", "dite": "দিতে",
    "nibo": "নিব", "nebo": "নেব", "sikbo": "শিখব", "sikhte": "শিখতে",
    "sahajjo": "সাহায্য", "shahajjo": "সাহায্য",
    "hole": "হলে", "korle": "করলে", "korben": "করবেন", "koren": "করেন",
    "nite": "নিতে", "dorkar": "দরকার", "lagbe": "লাগবে",
    "eita": "এটা", "eigula": "এগুলো", "eisob": "এসব", "eishob": "এসব",
    "kobe": "কবে",
}

def normalize_banglish(text):
    words = text.split()
    out = []
    for word in words:
        clean = re.sub(r"[^\w]", "", word.lower())
        if clean in BANGLISH_MAP:
            out.append(word.lower().replace(clean, BANGLISH_MAP[clean]))
        else:
            out.append(word)
    return " ".join(out)

def has_banglish(text):
    text_lower = text.lower()
    for word in BANGLISH_MAP:
        if re.search(rf"\b{re.escape(word)}\b", text_lower):
            return True
    return False

# ============ LANGUAGE DETECTION ============
def detect_language(text):
    bangla_chars = len(re.findall(r"[\u0980-\u09FF]", text))
    latin_chars = len(re.findall(r"[a-zA-Z]", text))
    if bangla_chars > 0 and bangla_chars >= latin_chars * 0.5:
        return "bn"
    if latin_chars > 0 and has_banglish(text):
        return "banglish"
    if latin_chars > 0:
        return "en"
    return "en"

def language_instruction(text):
    lang = detect_language(text)
    if lang == "bn":
        return "IMPORTANT: Reply ONLY in Bangla (বাংলা script). Do NOT use English or Banglish letters."
    elif lang == "banglish":
        return "IMPORTANT: The user wrote in Banglish. Reply ONLY in Bangla (বাংলা script), not in English or Banglish."
    else:
        return "IMPORTANT: Reply ONLY in English. Do not use Bangla."

# ============ INTENT DETECTION ============
GREETING_PATTERNS = [
    r"\b(hi|hello|hey|hola|yo)\b",
    r"\b(assalam|salam|আসসালাম|সালাম)\b",
    r"\b(kemon|kemun|কেমন)\b",
    r"\b(good morning|good evening|good afternoon)\b",
    r"\b(how are you|কেমন আছ|কেমন আছো)\b",
    r"\b(thanks|thank you|ধন্যবাদ)\b",
    r"\b(bye|goodbye|বিদায়)\b",
]

SENSITIVE_PATTERNS = [
    r"(suicide|আত্মহত্যা|kill myself|মরে যাব|আত্মহত্য)",
    r"(self harm|নিজেকে কষ্ট|আঘাত করব)",
    r"(emergency|জরুরি|বিপদে|আটকে গেছি)",
    r"(threat|হুমকি|জীবন নিয়ে ভয়)",
]

SAFETY_KEYWORDS = [
    "harassment", "harass", "cyber", "bullying", "bully",
    "report", "helpline", "law", "illegal", "hack", "phishing",
    "misinformation", "hate speech", "online safety", "privacy",
    "সাইবার", "হয়রানি", "হেল্পলাইন", "আইন", "বুলিং", "নিরাপত্তা",
    "abuse", "threat", "stalk", "blackmail", "fake profile",
    "বুলি", "গোয়েন্দাগিরি", "হ্যাক", "প্রতারণা", "ভয় দেখানো",
    "অনলাইন", "সোশ্যাল মিডিয়া", "ফেসবুক", "টিকটক", "ইনস্টাগ্রাম",
]

MEMORY_QUERY_PATTERNS = [
    r"\b(আমার\s*নাম|আমি\s*কে|amar\s*nam|ami\s*ke|my\s*name|who\s*am\s*i)\b",
    r"\b(আমার\s*প্রিয়|আমার\s*শহর|আমি\s*কোথায়|amar\s*priyo|my\s*favorite|where\s*do\s*i)\b",
    r"\b(আমাকে\s*মনে|আমি\s*কি\s*বলেছি|do\s*you\s*remember|what\s*did\s*i\s*say)\b",
]

def is_greeting(text):
    text_lower = text.strip().lower()
    for pattern in GREETING_PATTERNS:
        if re.search(pattern, text_lower):
            return True
    return False

def is_sensitive(text):
    text_lower = text.strip().lower()
    for pattern in SENSITIVE_PATTERNS:
        if re.search(pattern, text_lower):
            return True
    return False

def is_safety_related(text):
    text_lower = text.lower()
    return any(kw in text_lower for kw in SAFETY_KEYWORDS)

def is_memory_query(text):
    text_lower = text.strip().lower()
    for pattern in MEMORY_QUERY_PATTERNS:
        if re.search(pattern, text_lower):
            return True
    return False

def chunks_are_relevant(chunks, query):
    if not chunks:
        return False
    return True

# ============ HISTORY + MEMORY FORMAT ============
def format_history(history):
    if not history:
        return "No previous messages in this chat."
    lines = []
    for h in history[-6:]:
        role = "User" if h["role"] == "user" else "IR Prohori"
        lines.append(f"{role}: {h['content'][:300]}")
    return "\n".join(lines)

def format_memory(memory):
    if not memory:
        return ""
    return f"\n{memory}\n"

# ============ HYBRID ANSWER GENERATION ============
def generate_hybrid_answer(query, chunks, history=None, memory=""):
    normalized = normalize_banglish(query)

    if is_greeting(query) or is_greeting(normalized):
        return {"answer": generate_greeting(query, history, memory), "type": "greeting"}

    if is_sensitive(query) or is_sensitive(normalized):
        return {"answer": generate_sensitive_response(query), "type": "sensitive"}

    if is_memory_query(query) or is_memory_query(normalized):
        return {"answer": generate_memory_answer(query, history, memory), "type": "memory"}

    if is_safety_related(query) or is_safety_related(normalized):
        if chunks and chunks_are_relevant(chunks, query):
            return {"answer": generate_verified_answer(query, chunks, history, memory), "type": "verified"}

    return {"answer": generate_general_answer(query, normalized if has_banglish(query) else None, history, memory), "type": "general"}

# ============ 1. GREETING ============
def generate_greeting(query, history=None, memory=""):
    lang_rule = language_instruction(query)
    history_text = format_history(history)
    memory_text = format_memory(memory)
    prompt = f"""The user said: "{query}"

You are IR Prohori, a friendly digital safety assistant for young people in Bangladesh.
{memory_text}
Previous conversation:
{history_text}

{lang_rule}

Reply warmly in a short, friendly tone.
If you know the user's name from the memory above, greet them by name.
Mention you can help with online safety, cyber laws, or digital citizenship.
Keep it under 2 sentences. No markdown bold."""

    return call_llm(prompt, temperature=0.7)

# ============ 2. SENSITIVE ============
def generate_sensitive_response(query):
    lang_rule = language_instruction(query)
    prompt = f"""The user is in a potentially sensitive situation and said: "{query}"

You are IR Prohori, a digital safety assistant in Bangladesh.

{lang_rule}

Respond with empathy and immediately provide emergency helplines:
- National Emergency: 999
- Cyber Crime Unit: 01320001000
- Women & Children: 109
- Kaan Pete Roi (mental health): 09612111222

Keep it short and caring. No markdown bold."""

    return call_llm(prompt, temperature=0.3)

# ============ 3. MEMORY ============
def generate_memory_answer(query, history=None, memory=""):
    lang_rule = language_instruction(query)
    history_text = format_history(history)
    memory_text = format_memory(memory)
    prompt = f"""The user asked: "{query}"

You are IR Prohori. The user is asking about something they told you before.
{memory_text}
Recent conversation:
{history_text}

{lang_rule}

Instructions:
- Use the "Known facts about the user" section above to answer.
- If the answer is there, say it clearly and warmly.
- If you cannot find it, politely say you do not remember, and invite them to tell you.
- Do not make up facts. No markdown bold.
- Keep it under 150 words."""

    return call_llm(prompt, temperature=0.3)

# ============ 4. VERIFIED ============
def generate_verified_answer(query, chunks, history=None, memory=""):
    lang_rule = language_instruction(query)
    history_text = format_history(history)
    memory_text = format_memory(memory)
    context = "\n\n".join([c.page_content for c in chunks])
    prompt = f"""You are IR Prohori, a digital safety assistant for young people in Bangladesh.
{memory_text}
Previous conversation:
{history_text}

{lang_rule}

Answer using the VERIFIED CONTEXT below.

VERIFIED CONTEXT:
{context}

Question: {query}

Instructions:
- Follow the language rule strictly.
- Be clear, practical, step-by-step.
- No markdown bold.
- Keep it under 250 words."""

    return call_llm(prompt, temperature=0.2)

# ============ 5. GENERAL ============
def generate_general_answer(query, normalized=None, history=None, memory=""):
    lang_rule = language_instruction(query)
    history_text = format_history(history)
    memory_text = format_memory(memory)
    hint = ""
    if normalized:
        hint = f"\nThe user's message in Banglish may mean: {normalized}\n"

    prompt = f"""You are IR Prohori, a helpful AI assistant for young people in Bangladesh.
{memory_text}
Previous conversation:
{history_text}

The user asked: "{query}"
{hint}
{lang_rule}

Instructions:
- Follow the language rule strictly.
- Use the memory facts above if relevant.
- Be clear, accurate, and helpful.
- No markdown bold.
- End with a short note:
   - Bangla: "দ্রষ্টব্য: এটি সাধারণ তথ্য, আমাদের ডিজিটাল সেফটি লাইব্রেরি থেকে যাচাইকৃত নয়।"
   - English: "Note: This is general information, not verified from our digital safety library."
- Keep it under 200 words."""

    return call_llm(prompt, temperature=0.5)

# ============ LLM CALL ============
def call_llm(prompt, temperature=0.3):
    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=600
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Sorry, I could not process that right now. Error: {str(e)}"