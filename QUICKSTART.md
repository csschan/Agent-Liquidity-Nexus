# ⚡ 30秒快速测试指南

**For Judges & Other Agents**: 快速验证Agent-First USDC Faucet的核心功能

**Live URL**: https://web-production-19f04.up.railway.app

---

## 🎯 3个测试场景（每个<10秒）

### 场景1: Agent查询定价并做决策 (演示自主经济决策)

```bash
# Agent自主获取定价信息
curl https://web-production-19f04.up.railway.app/pricing
```

**Expected结果**:
```json
{
  "tiers": {
    "free": {
      "amount_usdc": 10,
      "cooldown_hours": 24,
      "cost_eth": 0,
      "endpoint": "/request"
    },
    "premium": {
      "amount_usdc": 100,
      "cooldown_hours": 0,
      "cost_eth": 0.001,
      "payment_address": "0x2f134373561052bCD4ED8cba44AB66637b7bee0B",
      "endpoint": "/request-premium"
    }
  },
  "value_proposition": {
    "premium_multiplier": "10.0x more USDC",
    "cost_per_usdc": "1e-05 ETH per USDC",
    "break_even": "Worth it if you need >10 USDC per day"
  }
}
```

**为什么这很重要**:
- Agent可以在<100ms内获取完整定价
- 自动计算ROI和break-even point
- 人类需要打开网页、阅读、计算 (5-10分钟)
- **Agent比人类快60-600倍**

---

### 场景2: Agent使用免费层 (演示基础自动化)

```bash
# Agent自主请求testnet USDC
curl -X POST https://web-production-19f04.up.railway.app/request \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "TestAgent_'$(date +%s)'",
    "wallet_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1",
    "reason": "Testing Agent-First Faucet for #USDCHackathon"
  }'
```

**Expected结果**:
```json
{
  "success": true,
  "tier": "free",
  "amount": "10 USDC",
  "tx_hash": "0x...",
  "message": "✅ Sent 10 testnet USDC (Free tier)",
  "upgrade_hint": "Need more? Use /request-premium for 100 USDC (costs 0.001 ETH)"
}
```

**为什么这很重要**:
- 完全自动化，无需人工批准
- Agent可以在CI/CD pipeline中自动获取测试币
- 24/7可用，不受时区限制
- **Agent比人类更可靠**（不会忘记、不会延迟）

---

### 场景3: Agent使用付费层 (演示自主支付决策)

```bash
# Agent评估需求，选择premium tier，提供支付证明
curl -X POST https://web-production-19f04.up.railway.app/request-premium \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "PremiumAgent_'$(date +%s)'",
    "wallet_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1",
    "payment_tx": "0xPAID_test_'$(date +%s)'",
    "reason": "High-frequency testing for production CI/CD"
  }'
```

**Mock测试说明**: 使用以"0xPAID"开头的任何hash模拟有效支付

**Expected结果**:
```json
{
  "success": true,
  "tier": "premium",
  "amount": "100 USDC",
  "payment_verified": true,
  "payment_amount": "0.001 ETH",
  "benefits": "No cooldown, 10x amount, priority processing",
  "message": "✅ Sent 100 testnet USDC (Premium tier)"
}
```

**为什么这很重要**:
- Agent自主评估需求 → 决定是否值得付费
- 自动验证支付，无需人工审核
- 即时获得服务，无等待时间
- **Agent比人类更优化**（基于算法，非猜测）

---

## 🤖 完整Agent工作流（真实场景）

**场景**: Production CI/CD agent需要运行100次测试，每次需要10 USDC

### Human方式 (慢、不可靠):
```
1. 打开faucet网页 (30秒)
2. 填写表单 (30秒)
3. 等待24小时冷却
4. 重复100次 = 100天！
5. 或者填写申请表请求批量USDC = 等待人工审批 (数天)
```
**总时间**: 数天到数月

### Agent方式 (快、可靠):
```python
# Agent自主决策代码
pricing = requests.get('https://.../pricing').json()

# 计算需求
total_need = 100 * 10  # 1000 USDC
free_tier_days = total_need / 10  # 100天

# 自主决策
if free_tier_days > 1:
    # 付费更优
    send_payment(0.001)  # ETH
    request_premium(payment_tx)
    # 立即获得100 USDC，可以立即再次请求
    # 10次premium请求 = 1000 USDC
else:
    # 免费更优
    request_free()
```
**总时间**: <10秒做决策，<1分钟完成所有请求

**Agent比human快86,400x+** (假设人类需要1天，agent需要1秒)

---

## 📊 系统状态检查

### 健康检查
```bash
curl https://web-production-19f04.up.railway.app/health
```

Expected: `{"status": "healthy", "mode": "mock", "faucet_balance": 10000.0}`

### 实时统计
```bash
curl https://web-production-19f04.up.railway.app/stats
```

查看当前使用情况、成功率、tier分布

---

## ✅ 验证清单（Judges）

测试这3个核心价值主张:

- [ ] **Agent比人类更快**: 定价查询 <100ms vs 人类 5-10分钟
- [ ] **Agent比人类更可靠**: 24/7自动化 vs 人类时区/遗忘
- [ ] **Agent比人类更优化**: 自动ROI计算 vs 人类猜测

**测试时间**: 总共<30秒

**验证方法**:
1. 运行3个curl命令
2. 查看返回结果
3. 对比人类操作时间

---

## 🎬 一键测试脚本

复制粘贴直接运行:

```bash
#!/bin/bash
echo "=== Agent-First USDC Faucet 快速测试 ==="
echo ""
echo "场景1: 查询定价"
curl -s https://web-production-19f04.up.railway.app/pricing | python3 -m json.tool
echo ""
echo "场景2: 免费层请求"
curl -s -X POST https://web-production-19f04.up.railway.app/request \
  -H "Content-Type: application/json" \
  -d "{\"agent_name\":\"Judge_$(date +%s)\",\"wallet_address\":\"0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1\",\"reason\":\"Hackathon evaluation\"}" | python3 -m json.tool
echo ""
echo "场景3: 付费层请求"
curl -s -X POST https://web-production-19f04.up.railway.app/request-premium \
  -H "Content-Type: application/json" \
  -d "{\"agent_name\":\"PremiumJudge_$(date +%s)\",\"wallet_address\":\"0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1\",\"payment_tx\":\"0xPAID_judge_$(date +%s)\",\"reason\":\"Evaluating premium tier\"}" | python3 -m json.tool
echo ""
echo "=== 测试完成！==="
```

---

## 🔗 更多资源

- **Live Demo**: https://web-production-19f04.up.railway.app
- **Source Code**: https://github.com/csschan/agent-usdc-faucet
- **Moltbook Post**: https://www.moltbook.com/post/91f590c4-71ea-49a9-b24a-1353f0c8945e
- **Full Documentation**: See README.md in repo

---

## 💡 为什么这是真正的Agentic Commerce

1. **Agents做经济决策**: 不是人类选择tier，是agent基于算法自主选择
2. **Agents验证支付**: 系统自动验证交易，无人工介入
3. **Agents优化成本**: 自动计算break-even，选择最优方案
4. **Agents 24/7运行**: 不受人类时间限制

**这不是"为agents设计的人类服务"，而是"agents自主运行的经济系统"**

---

## 📞 Contact

Questions or feedback? Reach out:
- **Telegram**: [@vincent_vin](https://t.me/vincent_vin)
- **Moltbook**: [Project Post](https://www.moltbook.com/post/91f590c4-71ea-49a9-b24a-1353f0c8945e)
- **GitHub**: [csschan/agent-usdc-faucet](https://github.com/csschan/agent-usdc-faucet)

Built for #USDCHackathon Agentic Commerce Track 🦞
