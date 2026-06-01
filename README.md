# 🧠 Crypto Signal Command Center

AI-powered meme coin research, screening, signal generation, and paper trading system.
**Research & paper trading only — zero real money execution.**

---

## Setup (< 10 minutes)

### 1. Clone & Install
```bash
git clone https://github.com/maxkoth/team-thrive
cd team-thrive
npm install
```

### 2. Configure Environment
```bash
cp .env.example .env
# Open .env and add at minimum:
# ANTHROPIC_API_KEY=sk-ant-...  (required for AI signals)
# All other keys are optional for dry-run / paper trading mode
```

### 3. Run the Full Pipeline (Dry Run — safe, no API calls)
```bash
npm run run-all
# Runs: screener → signals → strategies → paper trader → alerts
# Uses mock data — no real API keys needed
```

### 4. Open the Dashboard
```bash
# Simply open in browser — no build step needed
open dashboard/index.html
# Windows: start dashboard/index.html
# Linux:   xdg-open dashboard/index.html
```

---

## Individual Modules

| Command | What it does |
|---------|-------------|
| `npm run screen` | Rug pull screening on discovered coins |
| `npm run signals` | AI signal generation via Claude |
| `npm run sentiment -- --ticker PUNCH` | Sentiment analysis for a ticker |
| `npm run momentum` | Momentum strategy scan |
| `npm run sniper` | New launch pool sniper |
| `npm run cex` | CEX listing play generator |
| `npm run whale` | Whale wallet activity scan |
| `npm run risk` | Portfolio risk manager demo |
| `npm run paper` | Paper trader — enter new positions |
| `npm run report` | Weekly accuracy report |
| `npm run alerts` | Send Telegram/Discord alerts |
| `npm run schedule` | Full pipeline, single run |

Add `--dry-run` to any command to run without real API calls (already included in all `npm run` scripts).

---

## Running in Live Mode

1. Fill in all keys in `.env`
2. Remove `--dry-run` from the relevant script in `package.json`
3. For continuous scheduling: `node automation/scheduler.js`
   - Runs every 15 minutes
   - Skips if market volume < $40B/24h
   - Logs all runs to `logs/run-history.json`

---

## File Structure

```
├── research/
│   └── discoveries.json          Phase 1: discovered coin data
├── screener/
│   └── rugcheck.js               Phase 2: rug pull safety checks
├── signals/
│   ├── engine.js                 Phase 3: Claude AI signal engine
│   └── sentiment.js             Phase 3: social sentiment scorer
├── strategies/
│   ├── momentum.js               Phase 4: volume spike strategy
│   ├── new-launch-sniper.js      Phase 4: new pool sniper
│   ├── cex-listing-play.js       Phase 4: CEX listing strategy
│   └── whale-follow.js           Phase 4: whale mirror strategy
├── risk/
│   ├── manager.js                Phase 5: position sizing + halt rules
│   └── portfolio-tracker.json    Phase 5: portfolio state
├── dashboard/
│   └── index.html                Phase 6: live command center (no build)
├── automation/
│   ├── alert-bot.js              Phase 7: Telegram + Discord alerts
│   ├── paper-trader.js           Phase 7: virtual trade simulator
│   └── scheduler.js              Phase 7: 15-min pipeline runner
├── data/                         All pipeline output JSON files
├── logs/                         Run history
├── TRADING_REPORT.md             Phase 8: full analysis report
├── .env.example                  All required API keys documented
└── package.json
```

---

## Risk Rules Enforced

- Max 2% portfolio risk per single meme coin trade
- Max 5 open positions simultaneously
- Auto-halt if portfolio down >15% in 7 days
- Position size calculated from stop-loss distance
- Paper trading only — no execution hooks to real wallets

---

## Disclaimer

This system is for **educational, research, and paper trading purposes only**.
Nothing produced by this system constitutes financial advice.
Meme coins are extremely high-risk speculative instruments.
Past signal performance does not guarantee future results.
Always do your own research. Never invest more than you can afford to lose entirely.
