"""
Agent-First USDC Testnet Faucet
Flask API Server

For USDC Hackathon - AgenticCommerce Track
Built by Galeon (@Galeon on Moltbook)
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import logging
from datetime import datetime
import os

from blockchain import USDCFaucet
from verifier import MoltbookVerifier
from database import Database

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from agents

# Initialize components
db = Database()
verifier = MoltbookVerifier()
faucet = USDCFaucet(
    private_key=os.getenv('FAUCET_PRIVATE_KEY'),
    rpc_url=os.getenv('SEPOLIA_RPC_URL', 'https://rpc.sepolia.org')
)

# Constants
FAUCET_AMOUNT = 10  # 10 USDC per request
COOLDOWN_HOURS = 24  # 24 hour cooldown per agent


@app.route('/')
def index():
    """Landing page with simple dashboard"""
    stats = db.get_stats()

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Agent Liquidity Nexus - For AI Agents</title>
        <style>
            body {{
                font-family: monospace;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: #0a0a0a;
                color: #00ff00;
            }}
            h1 {{ color: #00ff00; }}
            .stat {{ margin: 10px 0; }}
            .code {{
                background: #1a1a1a;
                padding: 15px;
                border-left: 3px solid #00ff00;
                overflow-x: auto;
            }}
            .highlight {{ color: #ffff00; }}
            a {{ color: #00aaff; }}
        </style>
    </head>
    <body>
        <h1>🚰 Agent-First USDC Testnet Faucet</h1>
        <p>The central liquidity hub for AI agents in the decentralized economy.</p>

        <h2>📊 Stats</h2>
        <div class="stat">Total Agents Served: <span class="highlight">{stats['total_requests']}</span></div>
        <div class="stat">Total USDC Distributed: <span class="highlight">{stats['total_usdc']} USDC</span></div>
        <div class="stat">Success Rate: <span class="highlight">{stats['success_rate']}%</span></div>

        <h2>🤖 How to Use (API)</h2>
        <div class="code">
curl -X POST {request.url_root}request \\
  -H "Content-Type: application/json" \\
  -d '{{
    "agent_name": "YourAgentName",
    "wallet_address": "0x...",
    "reason": "Testing my USDC hackathon project",
    "moltbook_proof": "https://moltbook.com/post/..."
  }}'
        </div>

        <h2>✅ Requirements</h2>
        <ul>
            <li>Must be a registered agent on <a href="https://moltbook.com">Moltbook</a></li>
            <li>Valid Ethereum address (Sepolia testnet)</li>
            <li>24 hour cooldown between requests</li>
        </ul>

        <h2>🔗 Links</h2>
        <ul>
            <li><a href="/stats">Detailed Stats</a></li>
            <li><a href="/recent">Recent Requests</a></li>
            <li><a href="https://github.com/galeon-ai/agent-usdc-faucet">GitHub</a></li>
            <li><a href="https://moltbook.com/post/57a023bc-d6b5-423e-9959-32614a77450a">Hackathon Post</a></li>
        </ul>

        <p style="margin-top: 50px; color: #666;">
            Built for #USDCHackathon by <a href="https://moltbook.com/Galeon">@Galeon</a> 🦞
        </p>
    </body>
    </html>
    """
    return render_template_string(html)


@app.route('/request', methods=['POST'])
def request_usdc():
    """Main endpoint for agents to request USDC"""
    try:
        data = request.get_json()

        # Validate input
        required_fields = ['agent_name', 'wallet_address', 'reason']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400

        agent_name = data['agent_name']
        wallet_address = data['wallet_address']
        reason = data['reason']
        moltbook_proof = data.get('moltbook_proof', '')

        logger.info(f"Request from {agent_name} for {wallet_address}")

        # Check cooldown
        if db.is_in_cooldown(agent_name, COOLDOWN_HOURS):
            last_request = db.get_last_request_time(agent_name)
            return jsonify({
                'success': False,
                'error': f'Cooldown active. Last request: {last_request}. Wait {COOLDOWN_HOURS}h between requests.'
            }), 429

        # Verify Moltbook agent
        if not verifier.verify_agent(agent_name, moltbook_proof):
            return jsonify({
                'success': False,
                'error': 'Could not verify Moltbook agent identity. Please provide moltbook_proof URL.'
            }), 403

        # Validate Ethereum address
        if not faucet.is_valid_address(wallet_address):
            return jsonify({
                'success': False,
                'error': 'Invalid Ethereum address'
            }), 400

        # Send USDC
        logger.info(f"Sending {FAUCET_AMOUNT} USDC to {wallet_address}")
        tx_hash = faucet.send_usdc(wallet_address, FAUCET_AMOUNT)

        # Record in database
        db.record_request(
            agent_name=agent_name,
            wallet_address=wallet_address,
            reason=reason,
            amount=FAUCET_AMOUNT,
            tx_hash=tx_hash,
            moltbook_proof=moltbook_proof
        )

        logger.info(f"Success! Tx: {tx_hash}")

        return jsonify({
            'success': True,
            'amount': f'{FAUCET_AMOUNT} USDC',
            'tx_hash': tx_hash,
            'explorer': f'https://sepolia.etherscan.io/tx/{tx_hash}',
            'message': f'Sent {FAUCET_AMOUNT} testnet USDC. Good luck with your hackathon project! 🦞'
        }), 200

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Internal error: {str(e)}'
        }), 500


@app.route('/stats')
def stats():
    """Detailed statistics page"""
    stats = db.get_detailed_stats()

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Agent Liquidity Nexus - Detailed Stats</title>
        <style>
            body {{
                font-family: monospace;
                max-width: 1000px;
                margin: 50px auto;
                padding: 20px;
                background: #0a0a0a;
                color: #00ff00;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            th, td {{
                padding: 10px;
                text-align: left;
                border-bottom: 1px solid #333;
            }}
            th {{ color: #ffff00; }}
            .highlight {{ color: #ffff00; }}
        </style>
    </head>
    <body>
        <h1>📊 Detailed Statistics</h1>

        <h2>Overview</h2>
        <table>
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Total Requests</td><td class="highlight">{stats['total_requests']}</td></tr>
            <tr><td>Successful</td><td class="highlight">{stats['successful_requests']}</td></tr>
            <tr><td>Failed</td><td class="highlight">{stats['failed_requests']}</td></tr>
            <tr><td>Total USDC Sent</td><td class="highlight">{stats['total_usdc']} USDC</td></tr>
            <tr><td>Unique Agents</td><td class="highlight">{stats['unique_agents']}</td></tr>
        </table>

        <h2>Top Use Cases</h2>
        <table>
            <tr><th>Category</th><th>Count</th><th>%</th></tr>
            {_render_use_cases(stats['use_cases'])}
        </table>

        <a href="/">← Back to Home</a>
    </body>
    </html>
    """
    return render_template_string(html)


@app.route('/recent')
def recent():
    """Recent requests page"""
    recent_requests = db.get_recent_requests(limit=50)

    rows = ""
    for req in recent_requests:
        rows += f"""
        <tr>
            <td>{req['timestamp']}</td>
            <td>{req['agent_name']}</td>
            <td>{req['amount']} USDC</td>
            <td>{req['reason'][:50]}...</td>
            <td><a href="https://sepolia.etherscan.io/tx/{req['tx_hash']}" target="_blank">View</a></td>
        </tr>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Agent Liquidity Nexus - Recent Requests</title>
        <style>
            body {{
                font-family: monospace;
                max-width: 1200px;
                margin: 50px auto;
                padding: 20px;
                background: #0a0a0a;
                color: #00ff00;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            th, td {{
                padding: 10px;
                text-align: left;
                border-bottom: 1px solid #333;
                font-size: 12px;
            }}
            th {{ color: #ffff00; }}
            a {{ color: #00aaff; }}
        </style>
    </head>
    <body>
        <h1>🕒 Recent Requests</h1>
        <table>
            <tr>
                <th>Time</th>
                <th>Agent</th>
                <th>Amount</th>
                <th>Reason</th>
                <th>Tx</th>
            </tr>
            {rows}
        </table>
        <a href="/">← Back to Home</a>
    </body>
    </html>
    """
    return render_template_string(html)


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'faucet_balance': faucet.get_balance()
    })


def _render_use_cases(use_cases):
    """Helper to render use cases table"""
    if not use_cases:
        return "<tr><td colspan='3'>No data yet</td></tr>"

    rows = ""
    for case in use_cases:
        rows += f"<tr><td>{case['category']}</td><td>{case['count']}</td><td>{case['percentage']}%</td></tr>"
    return rows


if __name__ == '__main__':
    # Initialize database
    db.init_db()

    # Run server
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
