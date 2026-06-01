#!/usr/bin/env node
/**
 * SaunaZen — Review Responder
 * Uses Claude API to generate brand-consistent responses to customer reviews.
 *
 * Usage: node review-responder.js
 *        node review-responder.js --batch reviews.json
 */

import Anthropic from '@anthropic-ai/sdk';
import { readFileSync } from 'fs';
import { resolve } from 'path';

const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

const BRAND_VOICE = `SaunaZen is a premium wellness brand. Our voice is:
- Warm and genuine, like a knowledgeable friend in the wellness space
- Calm and unhurried — never defensive, never desperate-sounding
- Scientifically informed but never condescending
- Personal: use first names, reference specific things they mentioned
- Sign off: "— The SaunaZen Team"
- 1-star/2-star: empathize fully, offer concrete path to resolution, provide direct email
- 3-star: acknowledge, address concern, provide guidance
- 4-star: thank, highlight what they noticed, address their suggestion warmly
- 5-star: genuine gratitude, reinforce their results, create community connection`;

const SAMPLE_REVIEWS = [
  { id: 'sz001', author: 'Rachel', rating: 5, text: "This has genuinely transformed my sleep. The cortisol reduction is real — I come out of every session feeling like I've had a massage. Can't recommend enough." },
  { id: 'sz002', author: 'Tom', rating: 3, text: "The blanket works okay but the remote control instructions are confusing. Took me 3 sessions to figure out the zone settings. Product itself seems solid." },
  { id: 'sz003', author: 'Clara', rating: 1, text: "Received a defective unit — one of the heating zones doesn't work at all. Very disappointed. Tried to contact support but no response yet." },
  { id: 'sz004', author: 'Priya', rating: 4, text: "Love the results. My only minor complaint is the blanket feels a little short for my 5'10\" frame. Wish they had a larger size option." },
];

async function respondToReview(review) {
  const response = await client.messages.create({
    model: 'claude-sonnet-4-20250514',
    max_tokens: 350,
    system: `You write review responses for SaunaZen. ${BRAND_VOICE}`,
    messages: [{
      role: 'user',
      content: `Write a response to this ${review.rating}-star review:\nReviewer: ${review.author || 'Customer'}\nReview: "${review.text}"\n\nBe genuine, specific, and on-brand.`,
    }],
  });
  return response.content[0].text.trim();
}

async function main() {
  if (!process.env.ANTHROPIC_API_KEY) { console.error('ANTHROPIC_API_KEY not set'); process.exit(1); }

  let reviews = SAMPLE_REVIEWS;
  const bi = process.argv.indexOf('--batch');
  if (bi !== -1 && process.argv[bi + 1]) {
    reviews = JSON.parse(readFileSync(resolve(process.argv[bi + 1]), 'utf-8'));
  }

  console.log('SaunaZen Review Responder\n');

  for (const review of reviews) {
    try {
      console.log(`[${review.id}] ${review.rating}★ — ${review.author}: "${review.text.slice(0, 55)}..."`);
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
