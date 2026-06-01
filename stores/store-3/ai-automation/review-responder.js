#!/usr/bin/env node
/**
 * LinguaFlow — Automated Review Responder
 * Uses Claude API to generate brand-consistent responses to customer reviews.
 *
 * Usage: node review-responder.js
 *        node review-responder.js --batch reviews.json
 */

import Anthropic from '@anthropic-ai/sdk';
import { readFileSync } from 'fs';
import { resolve } from 'path';

const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

const BRAND_VOICE = `LinguaFlow is a confident, empowering tech brand.
Voice guidelines:
- Enthusiastic but grounded — we celebrate real user stories
- Tech-credible: can reference accuracy rates, latency specs, offline capability accurately
- Honest: if a reviewer mentions a real limitation, acknowledge it rather than deflect
- Personal: use customer names, reference their specific use case
- 5-star: celebrate the achievement (they broke a barrier), share their story
- 4-star: thank + address their suggestion with genuine interest
- 3-star: acknowledge the friction, provide the fix, show we care
- 2-star: apologize + diagnose (often setup issues), offer direct support contact
- 1-star: own it, escalate to direct resolution, never argue about specs
- Sign off: "— The LinguaFlow Team"
- Never promise firmware updates or features not currently available`;

const SAMPLE_REVIEWS = [
  { id: 'lf001', author: 'Alex', rating: 5, text: "Used these in Tokyo for a week of business meetings. The Japanese translation is genuinely impressive — even handled some regional dialect. My clients were amazed. Worth every cent." },
  { id: 'lf002', author: 'Maria', rating: 2, text: "The translation is decent but there's a noticeable lag that makes conversations awkward. Also the app crashed twice during setup. Customer service hasn't responded." },
  { id: 'lf003', author: 'Chen', rating: 4, text: "Excellent for travel. Cantonese recognition is good but not perfect with older speakers. The offline mode is a lifesaver. Would love more accent training options." },
  { id: 'lf004', author: 'Priya', rating: 1, text: "Completely stopped working after 10 days. One earbud won't charge. Sent 3 emails. No response. Very disappointed in the product and the company." },
];

async function respondToReview(review) {
  const response = await client.messages.create({
    model: 'claude-sonnet-4-20250514',
    max_tokens: 380,
    system: `You write customer review responses for LinguaFlow AI translation earbuds. ${BRAND_VOICE}`,
    messages: [{
      role: 'user',
      content: `Write a response to this ${review.rating}-star review:\nReviewer: ${review.author}\nReview: "${review.text}"\n\nBe specific to their use case. For tech issues, suggest actionable steps. For positives, celebrate their story.`,
    }],
  });
  return response.content[0].text.trim();
}

async function main() {
  if (!process.env.ANTHROPIC_API_KEY) { console.error('ANTHROPIC_API_KEY not set'); process.exit(1); }

  let reviews = SAMPLE_REVIEWS;
  const bi = process.argv.indexOf('--batch');
  if (bi !== -1 && process.argv[bi + 1]) reviews = JSON.parse(readFileSync(resolve(process.argv[bi + 1]), 'utf-8'));

  console.log('LinguaFlow Review Responder — Powered by Claude\n');
  for (const review of reviews) {
    try {
      console.log(`[${review.id}] ${review.rating}★ — ${review.author}: "${review.text.slice(0, 58)}..."`);
      const resp = await respondToReview(review);
      console.log('RESPONSE:', resp, '\n---\n');
      await new Promise(r => setTimeout(r, 300));
    } catch (e) {
      if (e instanceof Anthropic.APIError) console.error(`API Error ${e.status}: ${e.message}`);
      else throw e;
    }
  }
}

main().catch(e => { console.error(e.message); process.exit(1); });
