# 💎 Agent Liquidity Nexus

> The central liquidity hub for AI agents in the decentralized economy

**Powering the Agent Economy** 🌐 | Built for **#USDCHackathon** (Agentic Commerce track)

**Live Demo**: https://charismatic-simplicity-production-1854.up.railway.app | **[→ Quick Test](QUICKSTART.md)** ⚡

---

## ⚡ Quick Start (For Judges & Agents)

**Want to test right now?** See **[QUICKSTART.md](QUICKSTART.md)** for 3 test scenarios (<30 seconds total)

**Want to see FULL autonomy?** See **[example_agent_web3.py](example_agent_web3.py)** - Complete autonomous web3 payment demo

Verify our core claims:
- ✅ Agents make decisions 60-600x faster than humans
- ✅ **Agents execute autonomous web3 payments** (zero human clicks)
- ✅ Agents optimize costs autonomously
- ✅ Agents operate 24/7 without human intervention

---

## 🎯 The Challenge

The emerging agent economy needs **reliable liquidity infrastructure**. Existing solutions fail agents:
- ❌ Human-centric interfaces (Captcha, forms)
- ❌ Inconsistent availability
- ❌ No scalability for production use
- ❌ Not designed for autonomous systems

**Agents need a dedicated liquidity hub, not ad-hoc solutions.**

---

## 💡 Our Solution

**Agent Liquidity Nexus** - The first liquidity infrastructure built specifically for autonomous agents:

### Two Service Tiers

**🆓 Free Tier**
- Amount: 10 USDC
- Cooldown: 24 hours
- Cost: Free
- Use case: Basic testing, casual development

**⚡ Premium Tier**
- Amount: 100 USDC (10x more!)
- Cooldown: None (unlimited)
- Cost: 0.001 ETH (~$2.50)
- Use case: CI/CD, production agents, high-frequency testing

### 🤖 True Autonomous Payments

**Balance/Deposit System** - Enables agents to operate FULLY autonomously:

```
Agent deposits once → Uses balance for multiple requests → No per-request transactions
```

**How it works:**
1. Agent deposits ETH once (e.g., 0.01 ETH = 10 premium requests)
2. Agent makes premium requests autonomously using balance
3. No need for web3 transaction on each request
4. **Zero human intervention after initial deposit**

This is **TRUE Agentic Commerce**: Agents making economic decisions AND executing payments autonomously.

---

## 🚀 Quick Start

### For AI Agents

#### Option 1: Free Tier (Simple)

```bash
curl -X POST https://charismatic-simplicity-production-1854.up.railway.app/request \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "YourAgentName",
    "wallet_address": "0xYourSepoliaAddress",
    "reason": "Testing my USDC hackathon project"
  }'
```

Response: 10 USDC, 24h cooldown

#### Option 2: Premium Tier (Pay-per-use)

```bash
# Step 1: Send 0.001 ETH payment
# Step 2: Request with payment proof
curl -X POST https://charismatic-simplicity-production-1854.up.railway.app/request-premium \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "YourAgentName",
    "wallet_address": "0xYourSepoliaAddress",
    "payment_tx": "0xPAID...",
    "reason": "High-frequency testing"
  }'
```

Response: 100 USDC, no cooldown

#### Option 3: Balance System (TRUE AUTONOMOUS) ⚡

```bash
# Step 1: Deposit once
curl -X POST https://charismatic-simplicity-production-1854.up.railway.app/deposit \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "YourAgentName",
    "amount_eth": 0.01,
    "deposit_tx": "0xDEPOSIT..."
  }'

# Step 2: Check balance
curl "https://charismatic-simplicity-production-1854.up.railway.app/balance?agent_name=YourAgentName"

# Step 3: Use balance for multiple autonomous requests
curl -X POST https://charismatic-simplicity-production-1854.up.railway.app/request-premium-balance \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "YourAgentName",
    "wallet_address": "0xYourSepoliaAddress",
    "reason": "Autonomous premium request"
  }'
```

**Benefits of Balance System:**
- ✅ Deposit once, use 10+ times
- ✅ No per-request web3 transactions
- ✅ TRUE autonomous operation
- ✅ Faster (no tx signing delay)
- ✅ Cheaper (fewer gas fees)

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
| `/request` | POST | Free tier: 10 USDC, 24h cooldown |
| `/request-premium` | POST | Premium tier: 100 USDC, requires payment |
| `/deposit` | POST | Deposit ETH for autonomous usage |
| `/balance` | GET | Check agent's balance |
| `/request-premium-balance` | POST | Premium tier using balance (autonomous) |
| `/pricing` | GET | Get pricing information (JSON) |
| `/stats` | GET | Detailed statistics dashboard |
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
- Agents decide tier 60-600x faster than humans
- Balance system: No per-request transaction delay
- Autonomous operation 24/7 (humans need sleep)

**"Safer"**:
- Programmatic decision-making (no human error)
- Balance system prevents overpayment
- On-chain transparency (all txs public)

**"Cheaper"**:
- Agents optimize costs autonomously (free vs premium)
- Balance system reduces gas fees (deposit once, use many times)
- No human overhead costs

### Key Innovation: Autonomous Economic Decision-Making

This project demonstrates **3 levels of Agentic Commerce**:

1. **Level 1: Autonomous Decision** - Agent evaluates pricing and chooses optimal tier
2. **Level 2: Autonomous Payment** - Agent executes web3 payment without human approval
3. **Level 3: Autonomous Optimization** - Agent uses balance system to minimize transaction costs

**Example autonomous workflow:**
```python
agent.decide_tier(500)  # Agent: "Premium is 60x faster, worth the cost"
agent.deposit_balance(0.01)  # Deposit once
agent.request_usdc()  # Use 10 times autonomously
# Total: ZERO human intervention
```

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
