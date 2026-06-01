# Crypto Signal System — Trading Report
**Generated:** 2026-06-01 | **System:** Paper Trading / Research Only

---

## 1. Top 5 Coins RIGHT NOW (Ranked by Signal Strength)

| Rank | Symbol | Chain | Signal | Confidence | Opportunity Type | Rug Risk |
|------|--------|-------|--------|------------|-----------------|----------|
| 1 | **PUNCH** | Solana | STRONG_BUY | 84% | Volume Spike (+80,000% since launch) | MEDIUM |
| 2 | **GOATSEUS** | Solana | BUY | 71% | Volume Spike + AI narrative meta | MEDIUM |
| 3 | **FRENS** | Solana | BUY | 67% | New Launch (6 days) | MEDIUM |
| 4 | **SOLIDLAUNCH** | Base | BUY | 67% | New Launch w/ locked LP | LOW |
| 5 | **BONK** | Solana | WATCH | 55% | Whale Accumulation | LOW |

**Sources:** DEXScreener, DEXTools weekly report, CoinGecko Solana meme category, Bitrue trending analysis.

---

## 2. Suggested Paper Trading Portfolio Allocation ($10,000 virtual)

| Symbol | Allocation | Rationale |
|--------|-----------|-----------|
| PUNCH | $800 (8%) | Highest momentum + strong social score |
| GOATSEUS | $600 (6%) | AI agent narrative with established community |
| FRENS | $500 (5%) | New launch with decent liquidity |
| SOLIDLAUNCH | $400 (4%) | Solid fundamentals for a meme coin |
| BONK | $300 (3%) | Safer blue-chip meme, low downside |
| **Cash Reserve** | **$7,400 (74%)** | Risk management buffer |

*Never deploy more than 2% portfolio risk per trade (see `/risk/manager.js` for exact sizing).*

---

## 3. Strategy Performance Analysis (Meme Coin Historical Patterns)

### Which Strategy Works Best for Meme Coins?

**1. New Launch Sniper — Best Risk/Reward**
- Historical win rate on quality-filtered launches: ~55-65%
- Average win: +120-300% | Average loss: -35-50%
- Key edge: being early in the liquidity curve
- Critical filter: LP locked + contract verified + $50k+ liquidity

**2. Momentum (Volume Spike) — Most Consistent**
- Win rate: ~50-60% | Average win: +40-80% | Average loss: -15-25%
- Works best in bull market conditions
- Trailing stop discipline is critical — prevents giving back gains

**3. CEX Listing Play — Highest Single-Trade Potential**
- Binance listing: median +85% day-of, then -35% correction days 2-4
- Strategy: sell 50-70% on listing day, rebuy the dip
- Risk: announcement may already be priced in on smaller coins

**4. Whale Follow — Reliable Signal, Slow Execution**
- Whale buys in meme coins precede >40% moves in ~45% of cases
- Delay between whale buy and retail discovery = your edge
- Best for Solana (fastest block time, Nansen coverage)

**5. CEX Sentiment Momentum — Shortest Edge**
- Social sentiment predicts price 6-12 hours ahead
- Shill detection is critical — coordinated pumps often precede rugs
- Use as confirmation, not primary signal

---

## 4. Tax & Legal Considerations (US Crypto Traders)

### Key Rules (Consult a CPA for your situation)
- **Every crypto-to-crypto trade is a taxable event** — including swapping ETH→meme coin
- **Short-term capital gains** (held < 1 year): taxed as ordinary income (10-37%)
- **Long-term capital gains** (held ≥ 1 year): 0%, 15%, or 20% depending on income
- **Wash sale rule** does NOT currently apply to crypto (no 30-day waiting period) — subject to legislative change
- **DeFi income** (LP fees, staking rewards) = ordinary income at time of receipt
- **Airdrops** = ordinary income at fair market value when received

### Record-Keeping Requirements
- Track: date acquired, cost basis, date sold, sale proceeds for every trade
- Keep records for at least 3 years (7 if income understated by 25%+)
- Use a dedicated address for trading (separates from personal holds)

### Recommended Tax Software
| Tool | Best For | Cost |
|------|---------|------|
| **Koinly** | Multi-chain DeFi + DEX | $49-$279/yr |
| **CoinTracker** | Coinbase integration | $59-$199/yr |
| **TokenTax** | Complex DeFi/meme trades | $65-$2,500/yr |
| **TaxBit** | High volume traders | Custom |

---

## 5. Recommended Tools Stack

### Wallets
| Tool | Use Case |
|------|---------|
| **Phantom** | Solana meme coins, Raydium swaps |
| **Rabby** | EVM chains (Base, ETH), multi-chain |
| **Ledger** | Cold storage for any holds > $500 |

### DEXs & Execution
| Tool | Use Case |
|------|---------|
| **Raydium** | Solana token swaps |
| **Jupiter** | Best execution aggregator on Solana |
| **Uniswap v3** | Base / ETH meme coins |
| **Aerodrome** | Base DEX with deep liquidity |

### Research & Tracking
| Tool | Use Case |
|------|---------|
| **DEXScreener** | Real-time price + volume across all chains |
| **DEXTools** | Chart analysis + pair info |
| **GeckoTerminal** | New pairs + pool analytics |
| **Nansen** | Smart money tracking |
| **Arkham** | Whale wallet intelligence |
| **Birdeye** | Solana token analytics |

### Safety & Screening
| Tool | Use Case |
|------|---------|
| **RugCheck.xyz** | Solana contract safety score |
| **Token Sniffer** | EVM honeypot + contract audit |
| **Honeypot.is** | Real-time honeypot simulation |
| **GoPlus Security** | Multi-chain risk API |

---

## 6. Red Flags Glossary — Common Rug Pull Patterns

| Pattern | Description | Risk Level |
|---------|-------------|-----------|
| **Mint Authority Active** | Dev can print unlimited tokens at any time | INSTANT FAIL |
| **Honeypot** | You can buy but cannot sell | INSTANT FAIL |
| **LP Not Locked** | Dev can remove all liquidity immediately | INSTANT FAIL |
| **Dev Wallet Dump** | Dev sells >10% of supply within 48h of launch | INSTANT FAIL |
| **Fresh Deployer** | Wallet created < 7 days ago — no track record | HIGH RISK |
| **Top-10 Concentration** | Top 10 wallets hold >30% — coordinated dump risk | HIGH RISK |
| **Unlocked Team Tokens** | Large vesting unlocks imminent | HIGH RISK |
| **Copied Contract** | Bytecode matches known rug templates | HIGH RISK |
| **Tax > 5%** | High buy/sell tax can mask backdoor functions | HIGH RISK |
| **Anonymous Team** | No doxxed devs, no audit, brand new project | MEDIUM |
| **Telegram Only** | No Twitter/GitHub — ephemeral community | MEDIUM |
| **Coordinated Shilling** | Same messages from many accounts (bot farms) | MEDIUM |
| **Suspicious Tokenomics** | 50%+ to "marketing" or unlocked team allocation | MEDIUM |
| **Fake Volume** | Wash trading between related wallets to inflate stats | MEDIUM |
| **Celebrity Endorsement** | Paid promotions — usually exit pump near peak | MEDIUM |

---

## 7. System Architecture Summary

```
scheduler.js (every 15min)
  └─► rugcheck.js        → data/screener-results.json
  └─► signals/engine.js  → data/signals.json        (Claude AI)
  └─► momentum.js        → data/momentum-signals.json
  └─► new-launch-sniper  → data/sniper-results.json
  └─► cex-listing-play   → data/cex-listing-strategies.json
  └─► whale-follow.js    → data/whale-activity.json
  └─► paper-trader.js    → data/paper-trades.json
  └─► alert-bot.js       → Telegram + Discord

dashboard/index.html    ← reads all /data/*.json files (auto-refresh 60s)
risk/manager.js         ← enforces position sizing + halt rules
```

---

*This system is for research, education, and paper trading only. Nothing here constitutes financial advice. Meme coins are extremely high-risk speculative assets. Never invest more than you can afford to lose entirely.*
