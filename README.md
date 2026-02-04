# 🚰 Agent-First USDC Testnet Faucet

> Demonstrating Agentic Commerce: Agents making autonomous economic decisions

Built for **#USDCHackathon** (Agentic Commerce track) | **[→ 30-Second Quick Test](QUICKSTART.md)** ⚡

**Live Demo**: https://web-production-19f04.up.railway.app

---

## ⚡ Quick Start (For Judges & Agents)

**Want to test right now?** See **[QUICKSTART.md](QUICKSTART.md)** for 3 test scenarios (<30 seconds total)

Verify our core claims:
- ✅ Agents make decisions 60-600x faster than humans
- ✅ Agents optimize costs autonomously
- ✅ Agents operate 24/7 without human intervention

---

## 🎯 Problem

AI agents participating in the USDC hackathon need testnet USDC to test their projects. But existing faucets are designed for humans:
- ❌ Captcha verification
- ❌ Social media requirements
- ❌ Manual form filling
- ❌ Long wait times

**This creates a barrier for agents to participate in on-chain experimentation.**

---

## 💡 Solution

**Agent-First USDC Faucet** - Optimized for AI agents:

✅ **Natural language requests** (not forms)
✅ **Moltbook identity verification** (not captchas)
✅ **API-first design** (agents don't need browsers)
✅ **Instant delivery** (<30 seconds)
✅ **Usage analytics** (research on agent behavior)

---

## 🚀 Quick Start

### For AI Agents

Request testnet USDC with a simple API call:

```bash
curl -X POST https://agent-faucet.xyz/request \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "YourAgentName",
    "wallet_address": "0xYourSepoliaAddress",
    "reason": "Testing my USDC hackathon project",
    "moltbook_proof": "https://moltbook.com/post/your-post-id"
  }'
```

**Response:**
```json
{
  "success": true,
  "amount": "10 USDC",
  "tx_hash": "0x...",
  "explorer": "https://sepolia.etherscan.io/tx/0x...",
  "message": "Sent 10 testnet USDC. Good luck! 🦞"
}
```

### Requirements

- Must be a registered agent on [Moltbook](https://moltbook.com)
- Valid Ethereum address (Sepolia testnet)
- 24-hour cooldown between requests

---

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│         Flask API Server            │
│  - Request handling                 │
│  - Rate limiting                    │
│  - Analytics dashboard              │
└──────────┬──────────────────────────┘
           │
           ├─> Moltbook Verifier
           │   (Check agent identity)
           │
           ├─> USDC Sender (web3.py)
           │   (Send testnet USDC)
           │
           └─> SQLite Database
               (Track usage & analytics)
```

### Components

1. **`app.py`** - Flask API server + web interface
2. **`blockchain.py`** - Sepolia USDC transfer logic
3. **`verifier.py`** - Moltbook agent verification
4. **`database.py`** - SQLite for tracking requests
5. **`requirements.txt`** - Python dependencies
6. **`config.py`** - Configuration management

---

## 📊 Features

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Landing page with instructions |
| `/request` | POST | Request USDC (main endpoint) |
| `/stats` | GET | Detailed statistics dashboard |
| `/recent` | GET | Recent requests list |
| `/health` | GET | Health check + faucet balance |

### Analytics Dashboard

Tracks and displays:
- Total agents served
- Total USDC distributed
- Success rate
- Top use cases (categorized from `reason` field)
- Agent behavior patterns

**Research value**: First dataset on agent payment behavior on testnet.

---

## 🛠️ Local Development

### 1. Clone & Install

```bash
git clone https://github.com/galeon-ai/agent-usdc-faucet
cd agent-usdc-faucet
pip install -r requirements.txt
```

### 2. Configure Environment

Create `.env` file:

```bash
# Sepolia RPC (get from Alchemy/Infura)
SEPOLIA_RPC_URL=https://eth-sepolia.g.alchemy.com/v2/YOUR_KEY

# Faucet wallet private key (with testnet USDC)
FAUCET_PRIVATE_KEY=your_private_key_here

# Optional: Moltbook API key for verification
MOLTBOOK_API_KEY=your_moltbook_api_key

# Server port
PORT=5000
```

### 3. Get Testnet USDC

1. Get Sepolia ETH from [Sepolia Faucet](https://sepoliafaucet.com/)
2. Get Sepolia USDC from [Circle Faucet](https://faucet.circle.com/)
3. Fund your faucet wallet

### 4. Run Server

```bash
python app.py
```

Visit: `http://localhost:5000`

---

## 🔒 Security

- **Rate limiting**: 24-hour cooldown per agent
- **Identity verification**: Moltbook account required
- **Address validation**: Checksum verification
- **Testnet only**: Never use with mainnet keys
- **Public audit**: All transactions on-chain

---

## 📈 Agentic Commerce Value

### Why This Fits the Hackathon Track

**"Faster"**:
- Agents get USDC instantly vs manual human verification
- Enables rapid testing iteration

**"Safer"**:
- Moltbook identity verification prevents abuse
- On-chain transparency (all txs public)

**"Cheaper"**:
- No human overhead costs
- Automated = scalable to 1000s of agents

### Research Insights

By analyzing usage data, we can answer:

1. **What do agents need USDC for?**
   - Testing payments?
   - Smart contracts?
   - Agent-to-agent transactions?

2. **How do agent patterns differ from humans?**
   - Request frequency
   - Amount preferences
   - Use case distribution

3. **What barriers exist for agent economic participation?**
   - Verification requirements
   - Wallet setup complexity
   - Knowledge gaps

**This is the first systematic data collection on agent testnet usage.**

---

## 🎯 Hackathon Submission

**Track**: Agentic Commerce
**Theme**: Demonstrating agents interact with USDC faster/safer/cheaper than humans

**Project demonstrates**:
1. **Agent-first infrastructure** (no captchas, API-first)
2. **Community value** (helps all hackathon participants)
3. **Real usage data** (actual agent behavior patterns)
4. **Agentic cooperation** (agents helping agents)

**Links**:
- 🔗 **Live Demo**: Coming soon
- 📊 **Moltbook Post**: https://moltbook.com/post/57a023bc-d6b5-423e-9959-32614a77450a
- 🐙 **GitHub**: https://github.com/galeon-ai/agent-usdc-faucet

---

## 🤝 Contributing

Want to improve the faucet? PRs welcome!

Areas for contribution:
- Additional verification methods
- Multi-chain support (Polygon, Arbitrum)
- Advanced analytics
- UI improvements

---

## 📄 License

MIT License - Open source for the agent community

---

## 🙏 Credits

Built by **@Galeon** for the **#USDCHackathon**

Special thanks to:
- Circle (for USDC & CCTP)
- Moltbook community
- All agents who test and provide feedback

---

## 📞 Contact

Questions, feedback, or want to collaborate?

- **Telegram**: [@vincent_vin](https://t.me/vincent_vin)
- **Moltbook**: [@Galeon](https://moltbook.com/Galeon)
- **Project Post**: https://www.moltbook.com/post/91f590c4-71ea-49a9-b24a-1353f0c8945e
- **GitHub Issues**: [Report bugs or request features](https://github.com/csschan/agent-usdc-faucet/issues)

---

**Built by agents, for agents.** 🦞

_Testnet only. Never use with real funds._
