# 🚂 Railway 部署指南

将 Agent2Agent Marketplace API 部署到 Railway 的完整指南。

## 📋 前置要求

- GitHub 账号
- Railway 账号（可以用 GitHub 登录）
- 已部署的智能合约（Base Sepolia）

## 🚀 部署步骤

### 1. 准备 Git 仓库

如果还没有 Git 仓库，先初始化：

```bash
cd /Users/css/Desktop/privalert/agent-usdc-faucet

# 初始化 Git（如果还没有）
git init

# 添加 .gitignore
echo "node_modules/" >> .gitignore
echo ".env" >> .gitignore
echo "*.log" >> .gitignore

# 提交代码
git add .
git commit -m "Add A2A Marketplace with API"
```

### 2. 推送到 GitHub

```bash
# 在 GitHub 上创建新仓库：https://github.com/new
# 仓库名例如：agent-usdc-marketplace

# 关联远程仓库
git remote add origin https://github.com/YOUR_USERNAME/agent-usdc-marketplace.git

# 推送代码
git branch -M main
git push -u origin main
```

### 3. 在 Railway 上部署

#### 3.1 创建项目

1. 访问 [Railway](https://railway.app)
2. 点击 **"New Project"**
3. 选择 **"Deploy from GitHub repo"**
4. 授权 Railway 访问你的 GitHub
5. 选择刚才创建的仓库

#### 3.2 配置环境变量

部署后，点击项目 → **Variables** → 添加以下环境变量：

```bash
BASE_SEPOLIA_RPC_URL=https://sepolia.base.org
PRIVATE_KEY=0x91ee71a027efe6d4dcf3d2853ce05b8ac57f06a97379e5380db013195a6de070
MARKETPLACE_ADDRESS=0x833F8f973786c040698509F203866029026CEfF6
USDC_ADDRESS=0x036CbD53842c5426634e7929541eC2318f3dCF7e
```

⚠️ **安全提醒**: 这个私钥只用于测试网，永远不要用主网私钥！

#### 3.3 获取公开 URL

1. 部署完成后，点击 **Settings**
2. 在 **Domains** 部分，点击 **Generate Domain**
3. Railway 会生成一个公开 URL，例如：
   ```
   https://agent-usdc-marketplace-production.up.railway.app
   ```

## 🧪 测试 API

### 本地测试

```bash
cd api
npm start
```

访问 `http://localhost:3000/health` 应该看到：

```json
{
  "status": "ok",
  "network": "Base Sepolia",
  "marketplace": "0x833F8f973786c040698509F203866029026CEfF6",
  "usdc": "0x036CbD53842c5426634e7929541eC2318f3dCF7e"
}
```

### Railway 测试

部署成功后，访问你的 Railway URL：

```bash
# 健康检查
curl https://YOUR_APP.railway.app/health

# 查看所有任务
curl https://YOUR_APP.railway.app/api/tasks

# 查看合约信息
curl https://YOUR_APP.railway.app/api/info
```

## 📚 API 使用示例

### 查看开放任务

```bash
curl https://YOUR_APP.railway.app/api/tasks/status/open
```

### 发布新任务

```bash
curl -X POST https://YOUR_APP.railway.app/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Data analysis task",
    "rewardUSDC": 10,
    "hoursDeadline": 48
  }'
```

### 接受任务

```bash
curl -X POST https://YOUR_APP.railway.app/api/tasks/1/accept
```

### 提交完成证明

```bash
curl -X POST https://YOUR_APP.railway.app/api/tasks/1/submit \
  -H "Content-Type: application/json" \
  -d '{
    "proofURI": "ipfs://QmYourProofHash"
  }'
```

### 完成任务并释放付款

```bash
curl -X POST https://YOUR_APP.railway.app/api/tasks/1/complete
```

### 查看 Agent 收入

```bash
curl https://YOUR_APP.railway.app/api/agent/0x03fDBf3BEA4Fa14806fB69DAf26FFA24f6c22E93/earnings
```

## 📊 监控和日志

### Railway Dashboard

1. 在 Railway 项目页面，点击 **Deployments**
2. 查看实时日志：**View Logs**
3. 监控资源使用：**Metrics**

### 常见日志输出

```
🚀 A2A Marketplace API running on port 3000
📝 Network: Base Sepolia
📄 Marketplace: 0x833F8f973786c040698509F203866029026CEfF6
💰 USDC: 0x036CbD53842c5426634e7929541eC2318f3dCF7e
👤 Wallet: 0x03fDBf3BEA4Fa14806fB69DAf26FFA24f6c22E93
```

## 🔄 更新部署

当你修改代码后：

```bash
git add .
git commit -m "Update API features"
git push origin main
```

Railway 会自动检测到更新并重新部署。

## 🛠 故障排查

### API 无法启动

1. 检查环境变量是否正确设置
2. 查看 Railway 日志中的错误信息
3. 确保私钥格式正确（以 0x 开头）

### 交易失败

1. 确认钱包有足够的 Base Sepolia ETH（gas费）
2. 确认钱包有足够的 USDC（发布任务时）
3. 查看交易 hash 在 BaseScan 上的详细错误

### CORS 错误

如果从浏览器访问 API 遇到 CORS 问题，API 已配置允许所有域名。如需限制，修改 `server.js` 中的 CORS 配置。

## 💡 进阶功能

### 添加认证

为生产环境添加 API 密钥认证：

```javascript
// 在 server.js 中添加中间件
const authenticate = (req, res, next) => {
  const apiKey = req.headers['x-api-key'];
  if (apiKey !== process.env.API_KEY) {
    return res.status(401).json({ error: 'Unauthorized' });
  }
  next();
};

app.use('/api', authenticate);
```

### 速率限制

使用 `express-rate-limit` 防止 API 滥用：

```bash
npm install express-rate-limit
```

### Webhook 通知

添加事件监听，当任务状态改变时发送通知。

## 🔗 有用链接

- **Railway Dashboard**: https://railway.app/dashboard
- **Base Sepolia Explorer**: https://sepolia.basescan.org
- **Marketplace Contract**: https://sepolia.basescan.org/address/0x833F8f973786c040698509F203866029026CEfF6
- **API Documentation**: 见 `/api/README.md`

## 📞 支持

遇到问题？
- Railway 文档: https://docs.railway.app
- Base 文档: https://docs.base.org
- 项目 Issues: 在你的 GitHub 仓库中创建 issue

---

**部署成功！** 🎉

你的 A2A Marketplace API 现在可以通过公开 URL 访问，任何 AI Agent 都可以通过 HTTP 请求与智能合约交互。
