"""
Mock模式Flask服务器 - 混合定价模型
展示Agentic Commerce能力：免费层 + 付费层
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 尝试导入模块，如果失败使用简化版本
try:
    from blockchain import MockUSDCFaucet
    from verifier import MockVerifier
    from database import Database
    from payment_verifier import MockPaymentVerifier
    from balance_system import MockBalanceSystem
    logger.info("✅ 成功导入所有模块")
except Exception as e:
    logger.error(f"导入模块失败: {e}")
    # 如果导入失败，使用内联版本
    class MockUSDCFaucet:
        def send_usdc(self, addr, amount):
            import hashlib, time
            return "0x" + hashlib.sha256(f"{addr}{amount}{time.time()}".encode()).hexdigest()
        def get_balance(self):
            return 10000.0
        def is_valid_address(self, addr):
            return addr.startswith('0x') and len(addr) == 42
    
    class MockVerifier:
        def verify_agent(self, name, proof=None):
            return True
    
    class Database:
        def __init__(self, *args, **kwargs):
            self.data = []
        def init_db(self):
            pass
        def record_request(self, **kwargs):
            self.data.append(kwargs)
        def is_in_cooldown(self, *args):
            return False
        def get_last_request_time(self, *args):
            return "Never"
        def get_stats(self):
            return {'total_requests': len(self.data), 'total_usdc': len(self.data)*10, 'success_rate': 100.0}
        def get_detailed_stats(self):
            return {**self.get_stats(), 'successful_requests': len(self.data), 'failed_requests': 0, 'unique_agents': len(self.data), 'use_cases': []}

    class MockPaymentVerifier:
        def verify_payment(self, tx_hash, expected_amount_eth=0.001):
            if tx_hash.startswith('0x') and tx_hash[2:].upper().startswith('PAID'):
                return {'verified': True, 'amount_eth': expected_amount_eth, 'from_address': '0x' + '1' * 40}
            return {'verified': False, 'error': 'Mock payment not recognized'}

    class MockBalanceSystem:
        def __init__(self):
            self.balances = {}
        def init_db(self):
            pass
        def record_deposit(self, agent_name, amount_eth, tx_hash):
            if not tx_hash.startswith('0xDEPOSIT'):
                return {'success': False, 'error': 'Use 0xDEPOSIT prefix for mock deposits'}
            if agent_name not in self.balances:
                self.balances[agent_name] = {'balance': 0, 'total_deposited': 0}
            self.balances[agent_name]['balance'] += amount_eth
            self.balances[agent_name]['total_deposited'] += amount_eth
            return {'success': True, 'deposit_amount': amount_eth, 'new_balance': self.balances[agent_name]['balance']}
        def get_balance(self, agent_name):
            return self.balances.get(agent_name, {}).get('balance', 0.0)
        def deduct_balance(self, agent_name, amount_eth, service_type='premium_tier'):
            current = self.get_balance(agent_name)
            if current < amount_eth:
                return {'success': False, 'error': 'Insufficient balance', 'current_balance': current, 'shortfall': amount_eth - current}
            self.balances[agent_name]['balance'] -= amount_eth
            return {'success': True, 'deducted': amount_eth, 'new_balance': self.balances[agent_name]['balance']}
        def get_balance_info(self, agent_name):
            if agent_name not in self.balances:
                return {'agent_name': agent_name, 'balance_eth': 0, 'has_balance': False}
            return {'agent_name': agent_name, 'balance_eth': self.balances[agent_name]['balance'], 'has_balance': True}

app = Flask(__name__)
CORS(app)

# 初始化组件
try:
    db = Database("faucet.db")
    db.init_db()
    verifier = MockVerifier()
    faucet = MockUSDCFaucet()
    payment_verifier = MockPaymentVerifier()
    balance_system = MockBalanceSystem()
    balance_system.init_db()
    logger.info("✅ 组件初始化成功")
except Exception as e:
    logger.error(f"组件初始化失败: {e}")

# 定价配置
FREE_TIER_AMOUNT = 10  # USDC
FREE_TIER_COOLDOWN = 24  # hours
PREMIUM_TIER_AMOUNT = 100  # USDC
PREMIUM_TIER_PRICE = 0.001  # ETH
PAYMENT_ADDRESS = "0x2f134373561052bCD4ED8cba44AB66637b7bee0B"  # 收款地址

@app.route('/')
def index():
    try:
        stats = db.get_stats()
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Agent USDC Faucet - Agentic Commerce Demo</title>
            <style>
                body {{
                    font-family: monospace;
                    max-width: 900px;
                    margin: 50px auto;
                    padding: 20px;
                    background: #0a0a0a;
                    color: #00ff00;
                }}
                h1 {{ color: #ffff00; }}
                h2 {{ color: #00ff00; }}
                .stat {{ margin: 10px 0; }}
                .tier {{
                    background: #1a1a1a;
                    padding: 20px;
                    margin: 20px 0;
                    border-left: 4px solid;
                }}
                .tier-free {{ border-left-color: #00ff00; }}
                .tier-premium {{ border-left-color: #ffaa00; }}
                .tier-title {{ font-size: 18px; font-weight: bold; margin-bottom: 10px; }}
                .tier-free .tier-title {{ color: #00ff00; }}
                .tier-premium .tier-title {{ color: #ffaa00; }}
                .tier-feature {{ margin: 8px 0; padding-left: 20px; }}
                .code {{
                    background: #1a1a1a;
                    padding: 15px;
                    border-left: 3px solid #666;
                    overflow-x: auto;
                    font-size: 11px;
                    margin: 10px 0;
                }}
                .highlight {{ color: #ffff00; font-weight: bold; }}
                .warning {{ color: #ff9900; }}
            </style>
        </head>
        <body>
            <h1>🚰 Agent USDC Faucet</h1>
            <p class="warning">⚠️ Mock Mode - Demonstrating Agentic Commerce</p>

            <div style="background:#1a4d1a;padding:15px;margin:20px 0;border-left:4px solid #00ff00;">
                <strong style="color:#ffff00;">⚡ FOR JUDGES & AGENTS:</strong>
                <a href="https://github.com/csschan/agent-usdc-faucet/blob/main/QUICKSTART.md" style="color:#00ff00;text-decoration:underline;">30-Second Quick Test Guide →</a>
                <br>
                <span style="color:#aaa;">Test all 3 scenarios in <30 seconds. Verify "agents > humans" claims.</span>
            </div>

            <h2>📊 Live Stats</h2>
            <div class="stat">Total Agents Served: <span class="highlight">{stats['total_requests']}</span></div>
            <div class="stat">Total USDC Distributed: <span class="highlight">{stats['total_usdc']}</span> testnet USDC</div>
            <div class="stat">Success Rate: <span class="highlight">{stats['success_rate']}%</span></div>
            <div class="stat">Uptime: <span class="highlight">24/7 Autonomous</span> (no human needed)</div>

            <h2>💰 Service Tiers</h2>

            <div class="tier tier-free">
                <div class="tier-title">🆓 Free Tier</div>
                <div class="tier-feature">• Amount: <span class="highlight">10 USDC</span></div>
                <div class="tier-feature">• Cooldown: <span class="highlight">24 hours</span></div>
                <div class="tier-feature">• Cost: <span class="highlight">Free</span></div>
                <div class="tier-feature">• Use case: Basic testing, casual development</div>
                <div class="code">
curl -X POST https://web-production-19f04.up.railway.app/request \\
  -H "Content-Type: application/json" \\
  -d '{{
    "agent_name": "YourAgent",
    "wallet_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1",
    "reason": "Testing faucet"
  }}'
                </div>
            </div>

            <div class="tier tier-premium">
                <div class="tier-title">⚡ Premium Tier</div>
                <div class="tier-feature">• Amount: <span class="highlight">100 USDC</span> (10x more!)</div>
                <div class="tier-feature">• Cooldown: <span class="highlight">None</span> (unlimited requests)</div>
                <div class="tier-feature">• Cost: <span class="highlight">0.001 ETH</span> (~$2.50)</div>
                <div class="tier-feature">• Use case: CI/CD, high-frequency testing, production agents</div>
                <div class="tier-feature">• Payment: Send 0.001 ETH to <code style="color:#ffaa00">{PAYMENT_ADDRESS}</code></div>
                <div class="code">
# Step 1: Send payment (0.001 ETH to payment address)
# Step 2: Request with payment proof
curl -X POST https://web-production-19f04.up.railway.app/request-premium \\
  -H "Content-Type: application/json" \\
  -d '{{
    "agent_name": "YourAgent",
    "wallet_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1",
    "payment_tx": "0xPAID...",
    "reason": "High-frequency testing"
  }}'

# Mock testing: Use tx hash starting with "0xPAID" for demo
                </div>
            </div>

            <h2>🤖 Why Agentic Commerce?</h2>
            <p style="line-height: 1.6;">
            This demonstrates <span class="highlight">agent economic decision-making</span>:<br>
            • Agents can <strong>choose</strong> between free (limited) and paid (unlimited) tiers<br>
            • Agents can <strong>verify payment</strong> autonomously<br>
            • Agents can <strong>optimize costs</strong> based on their needs<br>
            • Real-world use case: Production agents pay for premium service
            </p>

            <h2>🔗 API Endpoints</h2>
            <ul>
                <li><a href="/health">/health</a> - Health check</li>
                <li><a href="/stats">/stats</a> - Detailed statistics (JSON)</li>
                <li><strong>POST /request</strong> - Free tier (10 USDC, 24h cooldown)</li>
                <li><strong>POST /request-premium</strong> - Premium tier (100 USDC, requires payment)</li>
            </ul>

            <p style="margin-top: 50px; color: #666;">
                Built for <a href="https://www.moltbook.com/post/91f590c4-71ea-49a9-b24a-1353f0c8945e" style="color:#00aaff">#USDCHackathon</a> Agentic Commerce Track by Galeon 🦞
            </p>
            <p style="color: #666;">
                📞 Contact: <a href="https://t.me/vincent_vin" style="color:#00aaff">@vincent_vin</a> on Telegram
            </p>
        </body>
        </html>
        """
    except Exception as e:
        logger.error(f"Index error: {e}")
        return f"<h1>Error: {str(e)}</h1>", 500

@app.route('/request', methods=['POST'])
def request_usdc():
    try:
        data = request.get_json()
        
        agent_name = data.get('agent_name')
        wallet_address = data.get('wallet_address')
        reason = data.get('reason', 'No reason provided')

        if not agent_name or not wallet_address:
            return jsonify({
                'success': False,
                'error': 'Missing required fields: agent_name, wallet_address'
            }), 400

        # 检查冷却
        if db.is_in_cooldown(agent_name, FREE_TIER_COOLDOWN):
            return jsonify({
                'success': False,
                'error': f'Free tier cooldown active. Wait 24h between requests or use /request-premium',
                'hint': 'Premium tier: 100 USDC, no cooldown, costs 0.001 ETH'
            }), 429

        # 验证
        if not verifier.verify_agent(agent_name):
            return jsonify({'success': False, 'error': 'Verification failed'}), 403

        # 发送USDC (免费层)
        tx_hash = faucet.send_usdc(wallet_address, FREE_TIER_AMOUNT)

        # 记录
        db.record_request(
            agent_name=agent_name,
            wallet_address=wallet_address,
            reason=reason,
            amount=FREE_TIER_AMOUNT,
            tx_hash=tx_hash,
            moltbook_proof="",
            success=True,
            tier='free'
        )

        logger.info(f"✅ [FREE] Request from {agent_name}: {tx_hash}")

        return jsonify({
            'success': True,
            'tier': 'free',
            'amount': f'{FREE_TIER_AMOUNT} USDC',
            'tx_hash': tx_hash,
            'explorer': f'https://sepolia.etherscan.io/tx/{tx_hash}',
            'message': f'✅ Sent {FREE_TIER_AMOUNT} testnet USDC (Free tier)',
            'note': 'Mock mode - no real blockchain transactions',
            'upgrade_hint': 'Need more? Use /request-premium for 100 USDC (costs 0.001 ETH)'
        }), 200

    except Exception as e:
        logger.error(f"Request error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/request-premium', methods=['POST'])
def request_usdc_premium():
    """Premium tier: Pay to get more USDC without cooldown"""
    try:
        data = request.get_json()

        agent_name = data.get('agent_name')
        wallet_address = data.get('wallet_address')
        payment_tx = data.get('payment_tx')  # Payment transaction hash
        reason = data.get('reason', 'No reason provided')

        if not agent_name or not wallet_address or not payment_tx:
            return jsonify({
                'success': False,
                'error': 'Missing required fields: agent_name, wallet_address, payment_tx',
                'hint': 'Send 0.001 ETH to {} first, then provide the tx hash'.format(PAYMENT_ADDRESS)
            }), 400

        # 验证支付
        payment_result = payment_verifier.verify_payment(payment_tx, PREMIUM_TIER_PRICE)

        if not payment_result.get('verified'):
            return jsonify({
                'success': False,
                'error': 'Payment verification failed',
                'details': payment_result.get('error'),
                'hint': 'For mock testing, use tx hash starting with "0xPAID"'
            }), 402  # Payment Required

        # 验证agent身份（可选，premium可以跳过）
        # if not verifier.verify_agent(agent_name):
        #     return jsonify({'success': False, 'error': 'Verification failed'}), 403

        # 发送USDC (付费层 - 10倍金额)
        tx_hash = faucet.send_usdc(wallet_address, PREMIUM_TIER_AMOUNT)

        # 记录
        db.record_request(
            agent_name=agent_name,
            wallet_address=wallet_address,
            reason=reason,
            amount=PREMIUM_TIER_AMOUNT,
            tx_hash=tx_hash,
            moltbook_proof="",
            success=True,
            tier='premium',
            payment_tx=payment_tx,
            payment_amount=payment_result.get('amount_eth', PREMIUM_TIER_PRICE)
        )

        logger.info(f"✅ [PREMIUM] Request from {agent_name}: {tx_hash} (paid {payment_result.get('amount_eth')} ETH)")

        return jsonify({
            'success': True,
            'tier': 'premium',
            'amount': f'{PREMIUM_TIER_AMOUNT} USDC',
            'tx_hash': tx_hash,
            'explorer': f'https://sepolia.etherscan.io/tx/{tx_hash}',
            'message': f'✅ Sent {PREMIUM_TIER_AMOUNT} testnet USDC (Premium tier)',
            'payment_verified': True,
            'payment_amount': f'{payment_result.get("amount_eth", PREMIUM_TIER_PRICE)} ETH',
            'note': 'Mock mode - no real blockchain transactions',
            'benefits': 'No cooldown, 10x amount, priority processing'
        }), 200

    except Exception as e:
        logger.error(f"Premium request error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/pricing')
def pricing():
    """Return pricing information in JSON"""
    try:
        return jsonify({
            'tiers': {
                'free': {
                    'amount_usdc': FREE_TIER_AMOUNT,
                    'cooldown_hours': FREE_TIER_COOLDOWN,
                    'cost_eth': 0,
                    'endpoint': '/request'
                },
                'premium': {
                    'amount_usdc': PREMIUM_TIER_AMOUNT,
                    'cooldown_hours': 0,
                    'cost_eth': PREMIUM_TIER_PRICE,
                    'payment_address': PAYMENT_ADDRESS,
                    'endpoint': '/request-premium'
                }
            },
            'value_proposition': {
                'premium_multiplier': f'{PREMIUM_TIER_AMOUNT / FREE_TIER_AMOUNT}x more USDC',
                'cost_per_usdc': f'{PREMIUM_TIER_PRICE / PREMIUM_TIER_AMOUNT} ETH per USDC',
                'break_even': f'Worth it if you need >{FREE_TIER_AMOUNT} USDC per day'
            }
        })
    except Exception as e:
        logger.error(f"Pricing error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/deposit', methods=['POST'])
def deposit():
    """
    Agent deposits ETH for future autonomous premium requests
    TRUE AUTONOMOUS: Deposit once, use multiple times without per-request transactions
    """
    try:
        data = request.get_json()

        agent_name = data.get('agent_name')
        amount_eth = data.get('amount_eth')
        deposit_tx = data.get('deposit_tx')

        if not all([agent_name, amount_eth, deposit_tx]):
            return jsonify({
                'success': False,
                'error': 'Missing required fields: agent_name, amount_eth, deposit_tx'
            }), 400

        # Record deposit
        result = balance_system.record_deposit(agent_name, float(amount_eth), deposit_tx)

        if result.get('success'):
            logger.info(f"✅ [DEPOSIT] {agent_name}: +{amount_eth} ETH")
            return jsonify({
                **result,
                'message': f'Deposit successful! {amount_eth} ETH added to balance.',
                'usage': f'You can now use /request-premium-balance for autonomous requests'
            }), 200
        else:
            return jsonify(result), 400

    except Exception as e:
        logger.error(f"Deposit error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/balance', methods=['GET'])
def check_balance():
    """Check agent's balance"""
    try:
        agent_name = request.args.get('agent_name')

        if not agent_name:
            return jsonify({
                'success': False,
                'error': 'Missing agent_name parameter'
            }), 400

        balance_info = balance_system.get_balance_info(agent_name)

        return jsonify({
            'success': True,
            **balance_info
        })

    except Exception as e:
        logger.error(f"Balance check error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/request-premium-balance', methods=['POST'])
def request_premium_balance():
    """
    Request premium tier using balance (TRUE AUTONOMOUS)
    No per-request web3 transaction needed!
    """
    try:
        data = request.get_json()

        agent_name = data.get('agent_name')
        wallet_address = data.get('wallet_address')
        reason = data.get('reason', 'Autonomous premium request using balance')

        if not agent_name or not wallet_address:
            return jsonify({
                'success': False,
                'error': 'Missing required fields: agent_name, wallet_address'
            }), 400

        # Check and deduct balance
        deduct_result = balance_system.deduct_balance(agent_name, PREMIUM_TIER_PRICE, 'premium_tier')

        if not deduct_result.get('success'):
            return jsonify({
                **deduct_result,
                'hint': f'Deposit {deduct_result.get("shortfall", PREMIUM_TIER_PRICE)} ETH using /deposit endpoint'
            }), 402  # Payment Required

        # Send USDC (premium tier)
        tx_hash = faucet.send_usdc(wallet_address, PREMIUM_TIER_AMOUNT)

        # Record
        db.record_request(
            agent_name=agent_name,
            wallet_address=wallet_address,
            reason=reason,
            amount=PREMIUM_TIER_AMOUNT,
            tx_hash=tx_hash,
            moltbook_proof="",
            success=True,
            tier='premium_balance',
            payment_tx='balance_deduction',
            payment_amount=PREMIUM_TIER_PRICE
        )

        logger.info(f"✅ [PREMIUM-BALANCE] {agent_name}: {tx_hash} (balance: {deduct_result['new_balance']} ETH remaining)")

        return jsonify({
            'success': True,
            'tier': 'premium_balance',
            'amount': f'{PREMIUM_TIER_AMOUNT} USDC',
            'tx_hash': tx_hash,
            'explorer': f'https://sepolia.etherscan.io/tx/{tx_hash}',
            'message': f'✅ Sent {PREMIUM_TIER_AMOUNT} testnet USDC (Premium tier via balance)',
            'balance_deducted': PREMIUM_TIER_PRICE,
            'remaining_balance': deduct_result['new_balance'],
            'note': 'TRUE AUTONOMOUS: No per-request web3 transaction needed!',
            'benefits': 'Deposited once, used autonomously - this is true Agentic Commerce'
        }), 200

    except Exception as e:
        logger.error(f"Premium balance request error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/stats')
def stats():
    try:
        stats = db.get_detailed_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    try:
        return jsonify({
            'status': 'healthy',
            'mode': 'mock',
            'faucet_balance': faucet.get_balance()
        })
    except Exception as e:
        logger.error(f"Health error: {e}")
        return jsonify({'status': 'error', 'error': str(e)}), 500

# 错误处理
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(e):
    logger.error(f"Server error: {e}")
    return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    logger.info(f"🚀 Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
