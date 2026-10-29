# VoiceCost #2: Deepgram's Nova-3 promo is gone, so our example call rose to $0.0945/min

<!--
SUBJECT LINE OPTIONS
1. Deepgram's Nova-3 promo is gone, so our example call rose to $0.0945/min
2. AssemblyAI launched text-to-speech at $15 per 1M characters
3. Cartesia's agent minutes are on sale at $0.03 (through Dec 31)

PREVIEW TEXT OPTIONS
1. Plus AssemblyAI's new $15/1M-character voice, a Cartesia sale, and who is shutting down.
2. Deepgram streaming went from $0.0048 to $0.0077 a minute. Here's what that does to a real call.

All figures: VoiceCost daily snapshots 2026-10-20 to 2026-10-29 (data/snapshots, data/changes), read from each vendor's public pricing page.
-->

Hi, it's John with this week's VoiceCost update.

**Short version: a quiet stretch, then a busy two days.** VoiceCost checked every tracked vendor's pricing page each day from October 20 to October 29. Through October 27 the only movement was exchange-rate drift. Then on October 28 and 29 several vendors changed their pricing pages: one promotion ended, one sale started, one new voice launched, and several products are retiring or already gone. We now track 24 vendors and 66 price lines.

## What moved

- **[Deepgram](https://voicecost.net/vendors/deepgram.html?utm_source=newsletter&utm_medium=email&utm_campaign=issue-002) Nova-3 streaming: $0.0048 → $0.0077/min.** Through October 28, Deepgram's page showed Nova-3 Monolingual at a limited-time "current price" of $0.0048/min next to a "regular price" of $0.0077. Its redesigned page now lists a single pay-as-you-go rate of $0.0077/min. Flux English streaming went from $0.0065 to $0.0077 the same way.
- **New: [AssemblyAI](https://voicecost.net/vendors/assemblyai.html?utm_source=newsletter&utm_medium=email&utm_campaign=issue-002) text-to-speech, $15 per 1M characters.** AssemblyAI-TTS-1 launched October 27. That's the same list price as OpenAI's tts-1, and well under [ElevenLabs](https://try.elevenlabs.io/zwx7c5awvwsw) Flash / Turbo at $40.
- **[Cartesia](https://voicecost.net/vendors/cartesia.html?utm_source=newsletter&utm_medium=email&utm_campaign=issue-002) managed voice agents: on sale at $0.03/min.** This is a promotional price through December 31, 2026. The regular price on the page is still $0.06/min. Telephony ($0.014/min on Cartesia numbers) and LLM usage are billed on top.
- **[Speechmatics](https://voicecost.net/vendors/speechmatics.html?utm_source=newsletter&utm_medium=email&utm_campaign=issue-002) pre-recorded: the page now shows list rates.** Melia 1 is listed at $0.24/hr, Enhanced at $0.75/hr and Standard at $0.45/hr, roughly double what the page showed last week ($0.12, $0.38 and $0.23). The page now labels these as list rates before its 33% model-training discount and volume discounts of up to 25%, so check which rate you actually qualify for.
- **Exchange-rate drift:** [Gladia](https://voicecost.net/vendors/gladia.html?utm_source=newsletter&utm_medium=email&utm_campaign=issue-002) charges in euros (€0.68/hr real-time, €0.16/hr Solaria-3 async, both unchanged). In dollars, real-time slipped from $0.012710/min on Oct 20 to $0.012617, and Solaria-3 async from $0.002991 to $0.002969, under 1%.

Every daily entry is in the [changes log](https://voicecost.net/changes.html?utm_source=newsletter&utm_medium=email&utm_campaign=issue-002).

## Our example call: now $0.0945 a minute

Our example stack (an inbound call where the agent talks 50% of the time at about 800 characters per spoken minute) on the Oct 29 snapshot:

| Piece | Choice | $/min |
|---|---|---|
| Platform | [Vapi](https://vapi.ai/?aff=johnwg) hosting | $0.0500 |
| Speech-to-text | Deepgram Nova-3 streaming | $0.0077 |
| LLM | GPT 4.1 mini (Retell's published per-minute rate) | $0.0128 |
| Text-to-speech | [ElevenLabs](https://try.elevenlabs.io/zwx7c5awvwsw) Flash / Turbo, $40/1M chars × 400 chars/min | $0.0160 |
| Telephony | Twilio inbound (rate listed by Vapi) | $0.0080 |
| **Total** | | **$0.0945** |

That's up from $0.0916, all of it from Deepgram's promo ending. A 5-minute call is now about **$0.47**.

## This week's tip: watch the LLM line

Once you've picked a platform, the LLM is the piece that swings your cost the most. The per-minute LLM rates Retell publishes run from $0.008 (GPT 5 mini) to $0.045 (GPT 4.1), with Gemini 3.0 Flash at $0.016 and Claude 4.5 haiku at $0.025 in between.

Keep everything else in the stack above the same and only swap the model:

- **GPT 5 mini:** $0.0897/min, or about $0.45 for a 5-minute call.
- **GPT 4.1 mini (our example):** $0.0945/min, or about $0.47.
- **GPT 4.1:** $0.1267/min, or about $0.63.

That's a 41% jump in cost per minute from the model choice alone. The $0.037 spread between those LLM rates is wider than the range for any other piece we track once the platform is set. Test the cheapest model that handles your calls well before you upgrade. (Vapi passes model costs through at cost, so your LLM line there may differ from Retell's list price.) Try your own mix in the [calculator](https://voicecost.net/index.html?utm_source=newsletter&utm_medium=email&utm_campaign=issue-002#calculator), or compare platforms with [Vapi vs Retell](https://voicecost.net/compare/vapi-vs-retell.html?utm_source=newsletter&utm_medium=email&utm_campaign=issue-002).

Retiring or gone: AssemblyAI is retiring its Voice Agent API and no longer prices it, and Hume is sunsetting its TTS and voice APIs (access ends November 13, 2026) after removing its public pricing page. LMNT and PlayHT are discontinued. OpenAI's tts-1 ($15 per 1M characters) and tts-1-hd ($30) have published prices again, but OpenAI shuts both down on January 6, 2027. We never guess: a price shows only when the vendor publishes it.

## Tell me what to track

[Open VoiceCost](https://voicecost.net/?utm_source=newsletter&utm_medium=email&utm_campaign=issue-002) and try your own numbers. **Hit reply** and tell me which vendor, model or comparison you want added. Every reply gets read.

Got this from a friend? [Get the weekly voice AI price changes. Free.](https://voicecost.beehiiv.com/subscribe)

**Pricing this out for your business?** Get a free AI Opportunity Assessment from Points Beyond. We build voice agents and automation for small and medium-sized businesses. [Get a free AI Opportunity Assessment](https://pointsbeyond.ai/contact/?utm_source=voicecost&utm_medium=referral&utm_campaign=newsletter-002)

John Whitlock, VoiceCost · Built by [Points Beyond](https://pointsbeyond.ai/?utm_source=voicecost&utm_medium=referral&utm_campaign=newsletter-002)

*Disclosure: the ElevenLabs and Vapi links are affiliate links, and I may earn a commission at no cost to you. My company, Points Beyond, sells voice agent setup services. VoiceCost comparisons use only published vendor prices, and neither influences the numbers.*
