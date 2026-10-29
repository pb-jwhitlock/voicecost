"""Vendor + extraction rules for VoiceCost.

Each item is extracted with a regex run against the collapsed DOM text of the
page (see fetch.py). If the regex does not match, the price is recorded as
UNKNOWN - we never fall back to a hard-coded number.

Normalized units:
  agent / stt -> USD per minute of audio/call
  tts         -> USD per 1M characters
"""

N = r"([0-9]+(?:\.[0-9]+)?)"          # a number
NC = r"([0-9][0-9,]*(?:\.[0-9]+)?)"   # a number that may contain commas

PER_MIN = 1.0
PER_HR = 1 / 60
PER_1K = 1000.0
PER_1M = 1.0

V = []

def vendor(id, name, site, pages, items=(), cats=(), note=None, status="active"):
    V.append(dict(id=id, name=name, site=site, pages=pages, items=list(items),
                  categories=list(cats) or sorted({i["category"] for i in items}),
                  note=note, status=status))

def item(category, product, page, pattern, factor, unit, note=None, group=1,
         high_group=None, currency="USD", compute=None, tier=None, headline=False, scope=None):
    return dict(category=category, product=product, page=page, pattern=pattern,
                factor=factor, unit=unit, note=note, group=group, high_group=high_group,
                currency=currency, compute=compute, tier=tier, headline=headline, scope=scope)

# ----------------------------------------------------------------- agent platforms
vendor("vapi", "Vapi", "https://vapi.ai", {"vapi": "https://vapi.ai/pricing"}, [
    item("agent", "Vapi hosting fee (platform only)", "vapi",
         r"Pre-paid, \$" + N + r"/min Vapi hosting", PER_MIN, "$/min",
         note="Platform fee only. STT, LLM, TTS and telephony are passed through at cost on top.",
         tier="Pay as you go", headline=True),
], note="Orchestration platform: you bring (or pick) STT, LLM and TTS providers, billed at cost on top of the hosting fee.")

vendor("retell", "Retell AI", "https://www.retellai.com", {"retell": "https://www.retellai.com/pricing"}, [
    item("agent", "Retell voice agent, all-in range", "retell",
         r"\$" + N + r"-\$" + N + r" ?/ ?min(?:ute)? for AI Voice Agents", PER_MIN, "$/min",
         high_group=2, note="Advertised all-in range depending on LLM, voice and telephony choices.",
         tier="Pay as you go", headline=True),
    item("agent", "Retell Voice Infra (platform only)", "retell",
         r"Retell Voice Infra \$" + N + r"/minute", PER_MIN, "$/min",
         note="Infrastructure component only; LLM, TTS and telephony are added per minute."),
])

vendor("bland", "Bland AI", "https://www.bland.ai", {"bland": "https://www.bland.ai/pricing"}, [
    item("agent", "Bland talk time (Start plan)", "bland",
         r"Talk Time Rate \$" + N + r"/min \$" + N + r"/min", PER_MIN, "$/min",
         note="All-in talk-time rate ($0 platform fee).", tier="Start", headline=True),
    item("agent", "Bland talk time (Build plan)", "bland",
         r"Talk Time Rate \$" + N + r"/min \$" + N + r"/min", PER_MIN, "$/min", group=2,
         note="Requires the $299/month Build platform fee.", tier="Build"),
])

vendor("synthflow", "Synthflow", "https://synthflow.ai", {"synthflow": "https://synthflow.ai/pricing"}, [
    item("agent", "Synthflow enterprise minimum contract", "synthflow",
         r"Enterprise contracts start at \$" + NC + r" annually", None, "$/year minimum",
         note="Only an annual contract minimum is published; no per-minute rate.", headline=True),
], note="Pricing page lists enterprise contracts only. Per-minute price is not public.")

vendor("elevenlabs", "ElevenLabs", "https://elevenlabs.io", {"elevenlabs": "https://elevenlabs.io/pricing/api"}, [
    item("agent", "ElevenLabs Agents (Speech Engine)", "elevenlabs",
         r"Speech Engine Agents \$" + N + r" Price per minute", PER_MIN, "$/min",
         note="Speech models in one agent pipeline; LLM usage may be billed separately.", headline=True),
    item("stt", "Scribe v2 (batch)", "elevenlabs",
         r"Scribe v2 Speech to Text \$" + N + r" Price per hour", PER_HR, "$/hr"),
    item("stt", "Scribe v2 Realtime", "elevenlabs",
         r"Scribe v2 Realtime Speech to Text \$" + N + r" Price per hour", PER_HR, "$/hr", headline=True),
    item("tts", "v4", "elevenlabs",
         r"v4 Text to Speech (?:New )?\$" + N + r" Price per 1K characters", PER_1K, "$/1K chars", headline=True),
    item("tts", "Flash / Turbo", "elevenlabs",
         r"Flash / Turbo Text to Speech (?:New )?\$" + N + r" Price per 1K characters", PER_1K, "$/1K chars"),
    item("tts", "v2 Multilingual", "elevenlabs",
         r"v2 Multilingual Text to Speech (?:New )?\$" + N + r" Price per 1K characters", PER_1K, "$/1K chars"),
])

vendor("deepgram", "Deepgram", "https://deepgram.com", {"deepgram": "https://deepgram.com/pricing"}, [
    item("agent", "Voice Agent API, Standard", "deepgram",
         r"Tier Pay As You Go Growth Standard \$" + N + r"/min", PER_MIN, "$/min", tier="Pay as you go",
         note="Bundled STT + LLM + TTS agent tier.", headline=True),
    item("stt", "Nova-3 Monolingual (streaming, current price)", "deepgram",
         r"Nova-3 Monolingual i [^$]{0,300}?Current price \$" + N + r"/min Regular price \$[0-9.]+/min", PER_MIN, "$/min", tier="Pay as you go",
         note="Page shows a discounted 'current price' next to a higher 'regular price'.", headline=True),
    item("stt", "Flux English (streaming, current price)", "deepgram",
         r"Flux English i [^$]{0,300}?Current price \$" + N + r"/min Regular price \$[0-9.]+/min", PER_MIN, "$/min", tier="Pay as you go"),
    item("tts", "Aura-2", "deepgram",
         r"Aura-2 \$" + N + r"/1k characters", PER_1K, "$/1K chars", tier="Pay as you go", headline=True),
])

vendor("cartesia", "Cartesia", "https://cartesia.ai", {"cartesia": "https://cartesia.ai/pricing"}, [
    item("agent", "Managed voice agents (call duration)", "cartesia",
         r"Call duration \$" + N + r" per minute", PER_MIN, "$/min",
         note="Telephony extra ($0.014/min on Cartesia numbers per page); LLM free for UI agents for a limited time.", headline=True),
    item("tts", "Sonic (Startup plan, $49 / 1.25M credits)", "cartesia",
         r"Startup \$" + N + r" /mo Select Startup " + N + r"M credits / month", None, "plan $/credits",
         compute=lambda m: float(m.group(1)) / float(m.group(2)),
         note="Derived: plan price / included credits; page states 1 credit = 1 character.", headline=True),
    item("tts", "Sonic (Scale plan, $299 / 8M credits)", "cartesia",
         r"Scale \$" + N + r" /mo Select Scale " + N + r"M credits / month", None, "plan $/credits",
         compute=lambda m: float(m.group(1)) / float(m.group(2)),
         note="Derived: plan price / included credits; page states 1 credit = 1 character."),
    item("stt", "Ink (Scale plan)", "cartesia",
         r"One hour of audio is only \$" + N + r" on the Scale plan", PER_HR, "$/hr"),
])

vendor("ultravox", "Ultravox", "https://www.ultravox.ai", {"ultravox": "https://www.ultravox.ai/pricing"}, [
    item("agent", "Ultravox per-minute", "ultravox",
         r"Price Per Minute \$" + N + r" per minute", PER_MIN, "$/min", tier="Pay as you go", headline=True,
         note="First 30 minutes free per page."),
])

vendor("livekit", "LiveKit Agents", "https://livekit.io", {"livekit": "https://livekit.io/pricing"}, [
    item("agent", "Agent session (platform only)", "livekit",
         r"Agent session \$ ?" + N + r" ?/min", PER_MIN, "$/min", headline=True,
         note="Agent hosting only. STT/LLM/TTS inference and telephony billed separately."),
])

vendor("openai", "OpenAI", "https://openai.com", {
    "openai_api": "https://openai.com/api/pricing/",
    "openai_docs": "https://platform.openai.com/docs/pricing",
    "openai_tts1": "https://developers.openai.com/api/docs/models/tts-1",
    "openai_tts1hd": "https://developers.openai.com/api/docs/models/tts-1-hd"}, [
    item("agent", "gpt-live-1 (speech-to-speech)", "openai_docs",
         r"gpt-live-1 \$" + N, PER_MIN, "$/min", headline=True,
         note="Per-minute session price; backend model and tool usage are charged separately."),
    item("stt", "gpt-live-transcribe (streaming)", "openai_docs",
         r"gpt-live-transcribe Live transcription - - \$" + N + r" / minute", PER_MIN, "$/min", headline=True),
    item("stt", "gpt-transcribe (batch)", "openai_docs",
         r"gpt-transcribe Transcription - - \$" + N + r" / minute", PER_MIN, "$/min"),
    item("stt", "gpt-4o-mini-transcribe (estimated)", "openai_docs",
         r"gpt-4o-mini-transcribe Transcription \$[0-9.]+ \$[0-9.]+ \$" + N + r" / minute", PER_MIN, "$/min",
         note="Token-billed; OpenAI's own per-minute estimate."),
    item("tts", "tts-1 (Speech API)", "openai_tts1",
         r"Speech generation Cost / 1M characters \$" + NC, PER_1M, "$/1M chars", headline=True,
         note="Deprecated: OpenAI shuts down tts-1, tts-1-hd and gpt-4o-mini-tts on January 6, 2027 and points to gpt-realtime-2.1-mini (token-billed)."),
    item("tts", "tts-1-hd (Speech API)", "openai_tts1hd",
         r"Speech generation Cost / 1M characters \$" + NC, PER_1M, "$/1M chars",
         note="Deprecated: shuts down January 6, 2027."),
])

vendor("assemblyai", "AssemblyAI", "https://www.assemblyai.com", {"assemblyai": "https://www.assemblyai.com/pricing"}, [
    item("stt", "Universal-Streaming (English)", "assemblyai",
         r"Universal-Streaming High-quality realtime model.{0,220}?\$" + N + r" /hr", PER_HR, "$/hr", headline=True),
    item("stt", "Universal-2 (pre-recorded)", "assemblyai",
         r"Universal-2 Our highly accurate.{0,220}?\$" + N + r" /hr", PER_HR, "$/hr"),
    item("stt", "Universal-3.5 Pro (pre-recorded)", "assemblyai",
         r"Universal-3\.5 Pro The most accurate async.{0,260}?\$" + N + r" /hr", PER_HR, "$/hr"),
    item("tts", "AssemblyAI-TTS-1", "assemblyai",
         r"AssemblyAI-TTS-1(?: New)? Streaming text-to-speech.{0,260}?\$" + NC + r" ?/1M chars", PER_1M, "$/1M chars",
         headline=True, note="Billed on input characters; same rate for cloned voices and EU processing."),
], note="AssemblyAI is retiring its Voice Agent API (no longer priced on the pricing page since Oct 28, 2026); "
        "for voice agents it now points to Universal-3.6 Pro Realtime STT + LLM Gateway + its Text-to-Speech API.")

vendor("google", "Google Cloud", "https://cloud.google.com", {
    "google_stt": "https://cloud.google.com/speech-to-text/pricing",
    "google_tts": "https://cloud.google.com/text-to-speech/pricing"}, [
    item("stt", "Speech-to-Text V2 Standard (first 500K min)", "google_stt",
         r"Recognition \(sku:3099-B70F-0949\) Standard 0 minute to 500,000 minute \$" + N + r" / 1 minute",
         PER_MIN, "$/min", headline=True),
    item("stt", "V2 Dynamic Batch", "google_stt",
         r"Dynamic Batch Recognition \(sku:7700-6778-EF8E\) Standard¹ \$" + N + r" / 1 minute", PER_MIN, "$/min"),
    item("tts", "Chirp 3: HD voices", "google_tts",
         r"Chirp 3: HD voices \(sku:[A-Z0-9-]+\).{0,60}?\(US\$" + N + r" ?per 1 million characters\)", PER_1M, "$/1M chars", headline=True),
    item("tts", "Neural2 voices", "google_tts",
         r"Neural2 voices \(sku:[A-Z0-9-]+\).{0,60}?\(US\$" + N + r" ?per 1 million characters\)", PER_1M, "$/1M chars"),
    item("tts", "Standard voices", "google_tts",
         r"Standard voices \(sku:[A-Z0-9-]+\).{0,60}?\(US\$" + N + r" ?per 1 million characters\)", PER_1M, "$/1M chars"),
])

vendor("aws", "Amazon (Transcribe / Polly)", "https://aws.amazon.com", {
    "aws_transcribe": "https://aws.amazon.com/transcribe/pricing/",
    "polly": "https://aws.amazon.com/polly/pricing/"}, [
    item("stt", "Transcribe streaming (us-east-1)", "aws_transcribe",
         r"Streaming transcription is priced at \$" + N + r" per minute", PER_MIN, "$/min", headline=True,
         note="Taken from AWS's own worked pricing example for US East (N. Virginia)."),
    item("stt", "Transcribe batch (us-east-1)", "aws_transcribe",
         r"Batch transcription is priced at \$" + N + r" per minute", PER_MIN, "$/min",
         note="Taken from AWS's own worked pricing example for US East (N. Virginia)."),
    item("tts", "Polly Neural", "polly",
         r"Polly’s Neural voices are priced at \$" + N + r" per 1 million characters", PER_1M, "$/1M chars", headline=True),
    item("tts", "Polly Standard", "polly",
         r"Polly’s Standard voices are priced at \$" + N + r" per 1 million characters", PER_1M, "$/1M chars"),
    item("tts", "Polly Generative", "polly",
         r"Polly’s Generative voices are priced at \$" + N + r" per 1 million characters", PER_1M, "$/1M chars"),
])

vendor("azure", "Microsoft Azure Speech", "https://azure.microsoft.com", {
    "azure_speech": "https://azure.microsoft.com/en-us/pricing/details/cognitive-services/speech-services/"}, [
    item("stt", "Standard real-time transcription", "azure_speech",
         r"Standard Transcription Real-time Transcription: \$" + N + r" per hour", PER_HR, "$/hr", headline=True),
    item("stt", "Standard batch transcription", "azure_speech",
         r"Standard Transcription Real-time Transcription: \$[0-9.]+ per hour.{0,120}?Batch Transcription: \$" + N + r" per hour",
         PER_HR, "$/hr"),
    item("tts", "Neural / Neural HD Flash", "azure_speech",
         r"Neural/Neural HD Flash \(real-time and batch\): \$" + N + r" per 1M characters", PER_1M, "$/1M chars", headline=True),
])

vendor("speechmatics", "Speechmatics", "https://www.speechmatics.com", {"speechmatics": "https://www.speechmatics.com/pricing"}, [
    item("stt", "Melia 1 (pre-recorded)", "speechmatics",
         r"General purpose Melia 1 \$" + N + r" / hr", PER_HR, "$/hr", headline=True),
    item("stt", "Enhanced (pre-recorded)", "speechmatics",
         r"mid-sentence\. Enhanced \$" + N + r" / hr", PER_HR, "$/hr"),
    item("stt", "Standard (pre-recorded)", "speechmatics",
         r"More models Standard \$" + N + r" / hr", PER_HR, "$/hr"),
    item("tts", "Speechmatics TTS", "speechmatics",
         r"Text to Speech Natural, low-latency speech synthesis for Voice AI use cases\. \$" + N + r" per 1,000 characters",
         PER_1K, "$/1K chars", headline=True),
], note="Real-time STT rates sit behind an interactive tab and were not readable; pre-recorded rates shown.")

vendor("rev", "Rev AI", "https://www.rev.ai", {"rev": "https://www.rev.ai/pricing"}, [
    item("stt", "Reverb (English)", "rev",
         r"Reverb Transcription \$" + N + r" per hour", PER_HR, "$/hr", headline=True),
    item("stt", "Whisper Large", "rev",
         r"Whisper Large Transcription \$" + N + r" per minute", PER_MIN, "$/min"),
])

vendor("gladia", "Gladia", "https://www.gladia.io", {"gladia": "https://www.gladia.io/pricing"}, [
    item("stt", "Real-time", "gladia",
         r"Real-time rate " + N + r"€/hr", PER_HR, "€/hr", currency="EUR", headline=True),
    item("stt", "Solaria-3 async", "gladia",
         r"Solaria-3 · " + N + r"€/hr", PER_HR, "€/hr", currency="EUR"),
], note="Gladia prices in euros; USD shown is converted at the day's ECB reference rate.")

vendor("soniox", "Soniox", "https://soniox.com", {"soniox": "https://soniox.com/pricing"}, [
    item("stt", "Real-time (streaming), token-based", "soniox",
         r"and \$" + N + r"/hour for real-time", PER_HR, "$/hr", headline=True,
         note="Token-billed; Soniox's own per-hour equivalent."),
    item("stt", "Async (file), token-based", "soniox",
         r"Equivalent to about \$" + N + r"/hour for async", PER_HR, "$/hr",
         note="Token-billed; Soniox's own per-hour equivalent."),
])

vendor("fish", "Fish Audio", "https://fish.audio", {
    "fish_docs": "https://docs.fish.audio/developer-guide/models-pricing/pricing-and-rate-limits",
    "fish_plans": "https://fish.audio/plan/"}, [
    item("tts", "S2.1 Pro API", "fish_docs",
         r"s2\.1-pro \$" + N + r" / M UTF-8 bytes", PER_1M, "$/1M UTF-8 bytes", headline=True,
         note="Billed per UTF-8 byte; equals characters for plain English text, more for other scripts."),
    item("stt", "transcribe-1", "fish_docs",
         r"transcribe-1 \$" + N + r" / audio hour", PER_HR, "$/hr"),
])

vendor("inworld", "Inworld", "https://inworld.ai", {"inworld": "https://inworld.ai/pricing"}, [
    item("tts", "TTS-2 (On-Demand)", "inworld",
         r"On-Demand Evaluation and prototyping \$0 pay as you go TTS-2 \$" + N + r"/1M chars", PER_1M, "$/1M chars", headline=True),
    item("tts", "TTS-2 Flash (On-Demand)", "inworld",
         r"On-Demand Evaluation and prototyping .{0,60}?TTS-2 Flash \$" + N + r"/1M chars", PER_1M, "$/1M chars"),
    item("stt", "STT 1 (On-Demand)", "inworld",
         r"On-Demand Evaluation and prototyping .{0,100}?STT 1 \$" + N + r"/hr", PER_HR, "$/hr"),
])

vendor("rime", "Rime", "https://www.rime.ai", {"rime": "https://www.rime.ai/pricing"}, [
    item("tts", "Mist v3", "rime",
         r"Mist v3 is \$" + N + r" per minute", PER_1K, "$/min (~1K chars)", headline=True,
         note="Page: metered by characters, about 1,000 characters per minute, at $0.03 per 1K characters."),
    item("tts", "Coda v2", "rime",
         r"Coda v2 is \$" + N + r" per minute", PER_1K, "$/min (~1K chars)",
         note="Page: metered by characters, about 1,000 characters per minute."),
    item("stt", "Rime STT", "rime",
         r"then \$" + N + r" per minute\. Text to speech", PER_MIN, "$/min",
         note="Free until Nov 19, 2026 per page; this is the rate from Nov 20."),
])

# ----------------------------------------------------------------- unknown / no data
vendor("playht", "PlayHT", "https://play.ht", {"playht": "https://play.ht/pricing/"}, [
    item("tts", "PlayHT TTS", "playht", r"(?!)", PER_1M, "$/1M chars", headline=True),
], note="play.ht no longer resolves in DNS (checked Oct 29, 2026); PlayHT appears to have shut down its public service.",
   status="discontinued")

vendor("hume", "Hume AI", "https://www.hume.ai", {"hume": "https://www.hume.ai/pricing"}, [
    item("tts", "Octave TTS", "hume", r"Octave[^$]{0,80}\$" + N + r" ?(?:per|/) ?1(?:,000|K) characters", PER_1K, "$/1K chars", headline=True),
], note="Hume removed its public pricing page (hume.ai/pricing now redirects to the homepage), so no TTS price is published. "
        "Hume's docs say it is sunsetting the TTS and EVI APIs; access ends November 13, 2026.")

vendor("lmnt", "LMNT", "https://www.lmnt.com", {"lmnt": "https://www.lmnt.com/pricing"}, [
    item("tts", "LMNT TTS", "lmnt", r"(?!)", PER_1M, "$/1M chars", headline=True),
], note="Site says: 'Our speech generation journey has come to an end.' Service appears discontinued.",
   status="discontinued")

# LLM per-minute reference prices (used only as calculator presets). Scraped from Retell's
# public price list, which quotes LLM cost per call-minute.
LLM_PRESETS = [
    ("GPT 5 mini (via Retell list)", "retell", r"GPT 5 mini \$" + N + r"/minute"),
    ("GPT 4.1 mini (via Retell list)", "retell", r"GPT 4\.1 mini \$" + N + r"/minute"),
    ("GPT 4.1 (via Retell list)", "retell", r"GPT 4\.1 \$" + N + r"/minute"),
    ("Claude 4.5 haiku (via Retell list)", "retell", r"Claude 4\.5 haiku \$" + N + r"/minute"),
    ("Gemini 3.0 Flash (via Retell list)", "retell", r"Gemini 3\.0 Flash \$" + N + r"/minute"),
]

# Telephony reference prices (calculator presets), scraped from Vapi's page.
TELEPHONY_PRESETS = [
    ("Twilio inbound (via Vapi list)", "vapi", r"Twilio Inbound \$" + N + r" / min"),
    ("Twilio outbound (via Vapi list)", "vapi", r"Twilio Outbound \$" + N + r" / min"),
    ("Telnyx (via Vapi list)", "vapi", r"Telnyx \$" + N + r" / min"),
]

PAGES = {}
for v in V:
    PAGES.update(v["pages"])

# Agent pricing scope: platform = orchestration fee only; all-in = includes models + telephony;
# bundled = includes speech models (and sometimes LLM) but not necessarily telephony.
AGENT_SCOPE = {
    'Vapi hosting fee (platform only)': 'platform',
    'Retell voice agent, all-in range': 'all-in',
    'Retell Voice Infra (platform only)': 'platform',
    'Bland talk time (Start plan)': 'all-in',
    'Bland talk time (Build plan)': 'all-in',
    'Synthflow enterprise minimum contract': 'all-in',
    'ElevenLabs Agents (Speech Engine)': 'bundled',
    'Voice Agent API, Standard': 'bundled',
    'Managed voice agents (call duration)': 'bundled',
    'Ultravox per-minute': 'bundled',
    'Agent session (platform only)': 'platform',
    'gpt-live-1 (speech-to-speech)': 'bundled',
}
for _v in V:
    for _i in _v['items']:
        if _i['category'] == 'agent':
            _i['scope'] = AGENT_SCOPE.get(_i['product'])
