"""
Mock模式Flask服务器 - 用于测试，不需要真实RPC
改进版：添加错误处理和日志
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

app = Flask(__name__)
CORS(app)

# 初始化组件
try:
    db = Database("faucet.db")
    db.init_db()
    verifier = MockVerifier()
    faucet = MockUSDCFaucet()
    logger.info("✅ 组件初始化成功")
except Exception as e:
    logger.error(f"组件初始化失败: {e}")

FAUCET_AMOUNT = 10
COOLDOWN_HOURS = 24

@app.route('/')
def index():
    try:
        stats = db.get_stats()
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Agent USDC Faucet - Mock Mode</title>
            <style>
                body {{
                    font-family: monospace;
                    max-width: 800px;
                    margin: 50px auto;
                    padding: 20px;
                    background: #0a0a0a;
                    color: #00ff00;
                }}
                h1 {{ color: #ffff00; }}
                .stat {{ margin: 10px 0; }}
                .code {{
                    background: #1a1a1a;
                    padding: 15px;
                    border-left: 3px solid #00ff00;
                    overflow-x: auto;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <h1>🚰 Agent USDC Faucet (Mock Mode)</h1>
            <p style="color: #ff9900;">⚠️ Test Mode - Returns mock transaction hashes</p>

            <h2>📊 Stats</h2>
            <div class="stat">Total Requests: <span style="color:#ffff00">{stats['total_requests']}</span></div>
            <div class="stat">Total USDC: <span style="color:#ffff00">{stats['total_usdc']}</span></div>
            <div class="stat">Success Rate: <span style="color:#ffff00">{stats['success_rate']}%</span></div>

            <h2>🧪 Test API</h2>
            <div class="code">
curl -X POST https://web-production-19f04.up.railway.app/request \\
  -H "Content-Type: application/json" \\
  -d '{{
    "agent_name": "TestAgent",
    "wallet_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1",
    "reason": "Testing faucet"
  }}'
            </div>

            <h2>🔗 Endpoints</h2>
            <ul>
                <li><a href="/health">/health</a> - Health check</li>
                <li><a href="/stats">/stats</a> - Stats (JSON)</li>
            </ul>

            <p style="margin-top: 50px; color: #666;">
                Built for <a href="https://moltbook.com/post/57a023bc-d6b5-423e-9959-32614a77450a" style="color:#00aaff">#USDCHackathon</a> by Galeon 🦞
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
        if db.is_in_cooldown(agent_name, COOLDOWN_HOURS):
            return jsonify({
                'success': False,
                'error': f'Cooldown active. Wait 24h between requests.'
            }), 429

        # 验证
        if not verifier.verify_agent(agent_name):
            return jsonify({'success': False, 'error': 'Verification failed'}), 403

        # 发送USDC
        tx_hash = faucet.send_usdc(wallet_address, FAUCET_AMOUNT)

        # 记录
        db.record_request(
            agent_name=agent_name,
            wallet_address=wallet_address,
            reason=reason,
            amount=FAUCET_AMOUNT,
            tx_hash=tx_hash,
            moltbook_proof="",
            success=True
        )

        logger.info(f"✅ Request from {agent_name}: {tx_hash}")

        return jsonify({
            'success': True,
            'amount': f'{FAUCET_AMOUNT} USDC',
            'tx_hash': tx_hash,
            'explorer': f'https://sepolia.etherscan.io/tx/{tx_hash}',
            'message': f'✅ Sent {FAUCET_AMOUNT} testnet USDC (Mock mode)',
            'note': 'This is mock mode - no real blockchain transactions'
        }), 200

    except Exception as e:
        logger.error(f"Request error: {e}")
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
