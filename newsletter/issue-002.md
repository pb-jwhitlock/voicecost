# VoiceCost #2: Prices held steady this week (and the one line that swings your cost most)

<!--
SUBJECT LINE OPTIONS
1. Prices held steady this week (and the one line that swings your cost most)
2. A quiet week for voice AI prices: our example call is still $0.0916/min
3. No list price moved this week. Here's where your per-minute cost really hides.

PREVIEW TEXT OPTIONS
1. Zero list-price changes across 24 vendors, plus a cheap way to trim your stacked cost.
2. Only Gladia's dollar figure wobbled, and that was the euro. The bigger lever is your LLM.

All figures: VoiceCost daily snapshots 2026-10-20 to 2026-10-25 (data/snapshots, data/changes), read from each vendor's public pricing page.
-->

Hi, it's John with this week's VoiceCost update.

**Short version: prices held steady.** VoiceCost checked every tracked vendor's pricing page each day from October 20 to October 25, and none of the list prices we track changed. Same 24 vendors, same 65 price lines, no new plans and none removed. A quiet week is still a useful result: if you priced a stack last week, your numbers still hold.

## What moved (barely)

Only one vendor's numbers changed, and it wasn't really a price change. [Gladia](https://voicecost.net/vendors/gladia.html?utm_source=newsletter&utm_medium=email&utm_campaign=issue-002) charges in euros, and we convert to dollars using the European Central Bank's daily reference rate. Its euro prices stayed exactly the same (€0.68/hr real-time and €0.16/hr Solaria-3 async), but the dollar figures drifted with the exchange rate:

- **Real-time:** $0.012710/min on Oct 20, up to $0.012732 on Oct 21, then down to $0.012685 by Oct 23, where it has held.
- **Solaria-3 async:** $0.002991/min on Oct 20, up to $0.002996 on Oct 21, then down to $0.002985 by Oct 23.

That's a move of about 0.2% in total. On a real call it's a rounding error. Every daily entry is in the [changes log](https://voicecost.net/changes.html?utm_source=newsletter&utm_medium=email&utm_campaign=issue-002).

## Our example call: still $0.0916 a minute

Last week's example stack (an inbound call where the agent talks 50% of the time at about 800 characters per spoken minute) comes out the same on the Oct 25 snapshot:

| Piece | Choice | $/min |
|---|---|---|
| Platform | [Vapi](https://vapi.ai/?aff=johnwg) hosting | $0.0500 |
| Speech-to-text | Deepgram Nova-3 streaming | $0.0048 |
| LLM | GPT 4.1 mini (Retell's published per-minute rate) | $0.0128 |
| Text-to-speech | [ElevenLabs](https://try.elevenlabs.io/zwx7c5awvwsw) Flash / Turbo, $40/1M chars × 400 chars/min | $0.0160 |
| Telephony | Twilio inbound (rate listed by Vapi) | $0.0080 |
| **Total** | | **$0.0916** |

A 5-minute call is still about **$0.46**.

## This week's tip: watch the LLM line

Once you've picked a platform, the LLM is the piece that swings your cost the most. The per-minute LLM rates Retell publishes run from $0.008 (GPT 5 mini) to $0.045 (GPT 4.1), with Gemini 3.0 Flash at $0.016 and Claude 4.5 haiku at $0.025 in between.

Keep everything else in the stack above the same and only swap the model:

- **GPT 5 mini:** $0.0868/min, or about $0.43 for a 5-minute call.
- **GPT 4.1 mini (our example):** $0.0916/min, or about $0.46.
- **GPT 4.1:** $0.1238/min, or about $0.62.

That's a 43% jump in cost per minute from the model choice alone. The $0.037 spread between those LLM rates is wider than the range for any other piece we track once the platform is set. Test the cheapest model that handles your calls well before you upgrade. (Vapi passes model costs through at cost, so your LLM line there may differ from Retell's list price.) Try your own mix in the [calculator](https://voicecost.net/index.html?utm_source=newsletter&utm_medium=email&utm_campaign=issue-002#calculator), or compare platforms with [Vapi vs Retell](https://voicecost.net/compare/vapi-vs-retell.html?utm_source=newsletter&utm_medium=email&utm_campaign=issue-002).

Still unconfirmed: PlayHT, Hume, LMNT and OpenAI TTS are marked Unknown on the site because we couldn't verify a published price. We never guess.

## Tell me what to track

[Open VoiceCost](https://voicecost.net/?utm_source=newsletter&utm_medium=email&utm_campaign=issue-002) and try your own numbers. **Hit reply** and tell me which vendor, model or comparison you want added. Every reply gets read.

Got this from a friend? [Get the weekly voice AI price changes. Free.](https://voicecost.beehiiv.com/subscribe)

**Pricing this out for your business?** Get a free assessment from Points Beyond. We build voice agents and automation for small and medium-sized businesses. [Get a free assessment](https://pointsbeyond.ai/contact/?utm_source=voicecost&utm_medium=referral&utm_campaign=newsletter-002)

John Whitlock, VoiceCost · Built by [Points Beyond](https://pointsbeyond.ai/?utm_source=voicecost&utm_medium=referral&utm_campaign=newsletter-002)

*Disclosure: the ElevenLabs and Vapi links are affiliate links, and I may earn a commission at no cost to you. My company, Points Beyond, sells voice agent setup services. VoiceCost comparisons use only published vendor prices, and neither influences the numbers.*
