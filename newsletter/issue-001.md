# VoiceCost #1: The real price per minute, checked daily, with receipts

<!--
SUBJECT LINE OPTIONS
1. The real price per minute, checked daily, with receipts
2. That $0.05/min voice agent? Our example came to $0.0916
3. What a voice AI call actually costs (with sources)

PREVIEW TEXT OPTIONS
1. Why the headline per-minute price is only half the story, plus the cheapest STT, TTS and agent rates today.
2. How to use VoiceCost in 4 steps, and one call priced line by line.
3. Platform fee + STT + LLM + TTS + phone line: we added it up so you don't have to.

All figures: VoiceCost snapshot 2026-10-21 (data/latest.json), read from each vendor's public pricing page.
-->

Hi, and welcome to the first VoiceCost email.

**The real price per minute, checked daily, with receipts.** Many pricing roundups copy a vendor's headline price once and never update it. VoiceCost rechecks each tracked vendor's official pricing page every day (24 vendors so far, 20 with prices we could verify), saves a dated history and a changes log, and helps you add up the all-in cost of a minute. Daily tracking started on October 20, 2026, so the history is young, but it grows every morning.

## How to use VoiceCost (4 steps)

1. **Price your call in the [calculator](https://voicecost.net/index.html#calculator).** Pick your speech-to-text, LLM, platform, voice and phone line. Enter call length and monthly volume to get the cost per call and per month.
2. **Compare two vendors.** Pages like [Vapi vs Retell](https://voicecost.net/compare/vapi-vs-retell.html) put their prices side by side.
3. **Check a vendor page.** Each one shows prices, the vendor's own units, a source link and a price-history line.
4. **Watch the [changes log](https://voicecost.net/changes.html).** Every detected price change is logged with the date and the old and new numbers.

New to voice AI? The [Start here guide](https://voicecost.net/start-here.html) walks through all of this.

## What a voice agent call really costs

A platform's per-minute fee often doesn't include speech-to-text, the LLM, text-to-speech, or the phone line. Here's one stack, priced line by line.

**Example only.** It uses Oct 21, 2026 prices and assumes an inbound call where the agent talks 50% of the time at about 800 characters per spoken minute.

| Piece | Choice | $/min |
|---|---|---|
| Platform | [Vapi](https://vapi.ai/?aff=johnwg) hosting | $0.0500 |
| Speech-to-text | Deepgram Nova-3 streaming | $0.0048 |
| LLM | GPT 4.1 mini (Retell's published per-minute rate) | $0.0128 |
| Text-to-speech | [ElevenLabs](https://try.elevenlabs.io/zwx7c5awvwsw) Flash / Turbo, $40/1M chars × 400 chars/min | $0.0160 |
| Telephony | Twilio inbound (rate listed by Vapi) | $0.0080 |
| **Total** | | **$0.0916** |

The $0.05 headline is only about 55% of the real cost per minute. A 5-minute call comes to about **$0.46**, not $0.25. (Vapi passes model costs through at cost, so your LLM line may differ from Retell's list price.)

## The numbers today (snapshot Oct 21, 2026)

- **Cheapest speech-to-text:** Soniox async at $0.10/hr ($0.0017/min). For streaming, Soniox real-time is $0.12/hr ($0.002/min). *(soniox.com/pricing)*
- **Cheapest text-to-speech:** Amazon Polly Standard and Google Cloud Standard voices, both $4 per 1M characters. These are older, basic voices. The cheapest newer option we track is Speechmatics TTS at $11 per 1M characters. *(AWS Polly, Google Cloud and Speechmatics pricing pages)*
- **Cheapest voice agent pricing:** LiveKit Agents at $0.01/min, which covers the platform only. The lowest bundled rates are $0.05/min for Ultravox and OpenAI gpt-live-1, and each comes with its own extras. Retell advertises all-in calls from $0.07 to $0.31/min. *(each vendor's pricing page)*
- **Price changes since Oct 20:** Only Gladia moved. Its two USD-converted rates went up 0.2% because the euro exchange rate changed, and its euro prices stayed the same. None of the list prices we track changed.

Prices still unconfirmed today (PlayHT, Hume, LMNT, OpenAI TTS, Synthflow) are marked Unknown on the site. We never guess.

## Tell me what to track

[Open VoiceCost](https://voicecost.net/) and try your own numbers. **Hit reply** and tell me which vendor, model or comparison you want added. Every reply gets read.

Got this from a friend? [Get the weekly voice AI price changes. Free.](https://voicecost.beehiiv.com/subscribe)

**Pricing this out for your business?** Get a free assessment from Points Beyond. We build voice agents and automation for small and medium-sized businesses. [Get a free assessment](https://pointsbeyond.ai/contact/?utm_source=voicecost&utm_medium=referral&utm_campaign=newsletter-001)

John Whitlock, VoiceCost · [Points Beyond](https://pointsbeyond.ai/?utm_source=voicecost&utm_medium=referral&utm_campaign=newsletter-001)

*Disclosure: the ElevenLabs and Vapi links are affiliate links, and I may earn a commission at no cost to you. My company, Points Beyond, sells voice agent setup services. VoiceCost comparisons use only published vendor prices, and neither influences the numbers.*
