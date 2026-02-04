"""
Balance/Deposit System for Autonomous Agents
Enables true autonomous payments without per-request transactions
"""

import sqlite3
import logging
from datetime import datetime
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class BalanceSystem:
    """
    Agent balance system for autonomous payments

    Flow:
    1. Agent deposits ETH once
    2. Agent can use balance for multiple premium requests
    3. No need for per-request web3 transactions
    """

    def __init__(self, db_file: str = "faucet.db"):
        self.db_file = db_file
        self.conn = None

    def init_db(self):
        """Initialize balance tables"""
        self.conn = sqlite3.connect(self.db_file, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

        cursor = self.conn.cursor()

        # Agent balances table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_balances (
                agent_name TEXT PRIMARY KEY,
                balance_eth REAL DEFAULT 0,
                total_deposited REAL DEFAULT 0,
                total_spent REAL DEFAULT 0,
                last_deposit_tx TEXT,
                last_deposit_time DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Deposit history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS deposits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_name TEXT NOT NULL,
                amount_eth REAL NOT NULL,
                tx_hash TEXT NOT NULL,
                verified BOOLEAN DEFAULT FALSE,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(agent_name) REFERENCES agent_balances(agent_name)
            )
        ''')

        # Spending history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS spending (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_name TEXT NOT NULL,
                amount_eth REAL NOT NULL,
                service_type TEXT NOT NULL,
                request_id INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(agent_name) REFERENCES agent_balances(agent_name)
            )
        ''')

        self.conn.commit()
        logger.info("Balance system initialized")

    def record_deposit(self, agent_name: str, amount_eth: float, tx_hash: str) -> Dict:
        """
        Record a deposit from an agent

        In production: Verify tx_hash on-chain
        In mock: Accept deposits with "0xDEPOSIT" prefix
        """
        cursor = self.conn.cursor()

        # Verify transaction (mock mode)
        verified = tx_hash.startswith('0xDEPOSIT') or tx_hash.startswith('0xPAID')

        if not verified:
            return {
                'success': False,
                'error': 'Invalid deposit transaction. Use tx starting with 0xDEPOSIT for mock mode.'
            }

        # Create or get agent balance
        cursor.execute('''
            INSERT INTO agent_balances (agent_name, balance_eth, total_deposited)
            VALUES (?, ?, ?)
            ON CONFLICT(agent_name) DO UPDATE SET
                balance_eth = balance_eth + ?,
                total_deposited = total_deposited + ?,
                last_deposit_tx = ?,
                last_deposit_time = ?
        ''', (agent_name, amount_eth, amount_eth, amount_eth, amount_eth, tx_hash, datetime.now()))

        # Record deposit
        cursor.execute('''
            INSERT INTO deposits (agent_name, amount_eth, tx_hash, verified)
            VALUES (?, ?, ?, ?)
        ''', (agent_name, amount_eth, tx_hash, verified))

        self.conn.commit()

        # Get new balance
        new_balance = self.get_balance(agent_name)

        logger.info(f"Deposit recorded: {agent_name} +{amount_eth} ETH, new balance: {new_balance} ETH")

        return {
            'success': True,
            'deposit_amount': amount_eth,
            'new_balance': new_balance,
            'tx_hash': tx_hash,
            'message': f'Deposited {amount_eth} ETH. New balance: {new_balance} ETH'
        }

    def get_balance(self, agent_name: str) -> float:
        """Get agent's current balance"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT balance_eth FROM agent_balances WHERE agent_name = ?
        ''', (agent_name,))

        result = cursor.fetchone()
        return result['balance_eth'] if result else 0.0

    def deduct_balance(self, agent_name: str, amount_eth: float, service_type: str = 'premium_tier') -> Dict:
        """
        Deduct from agent's balance for a service

        Returns:
            dict with success status and new balance
        """
        current_balance = self.get_balance(agent_name)

        if current_balance < amount_eth:
            return {
                'success': False,
                'error': f'Insufficient balance. Need {amount_eth} ETH, have {current_balance} ETH',
                'current_balance': current_balance,
                'required': amount_eth,
                'shortfall': amount_eth - current_balance
            }

        cursor = self.conn.cursor()

        # Deduct balance
        cursor.execute('''
            UPDATE agent_balances
            SET balance_eth = balance_eth - ?,
                total_spent = total_spent + ?
            WHERE agent_name = ?
        ''', (amount_eth, amount_eth, agent_name))

        # Record spending
        cursor.execute('''
            INSERT INTO spending (agent_name, amount_eth, service_type)
            VALUES (?, ?, ?)
        ''', (agent_name, amount_eth, service_type))

        self.conn.commit()

        new_balance = self.get_balance(agent_name)

        logger.info(f"Balance deducted: {agent_name} -{amount_eth} ETH, remaining: {new_balance} ETH")

        return {
            'success': True,
            'deducted': amount_eth,
            'new_balance': new_balance,
            'service_type': service_type
        }

    def get_balance_info(self, agent_name: str) -> Dict:
        """Get complete balance information for an agent"""
        cursor = self.conn.cursor()

        cursor.execute('''
            SELECT * FROM agent_balances WHERE agent_name = ?
        ''', (agent_name,))

        result = cursor.fetchone()

        if not result:
            return {
                'agent_name': agent_name,
                'balance_eth': 0,
                'total_deposited': 0,
                'total_spent': 0,
                'has_balance': False
            }

        return {
            'agent_name': agent_name,
            'balance_eth': result['balance_eth'],
            'total_deposited': result['total_deposited'],
            'total_spent': result['total_spent'],
            'last_deposit_tx': result['last_deposit_tx'],
            'last_deposit_time': result['last_deposit_time'],
            'has_balance': result['balance_eth'] > 0,
            'can_use_premium': result['balance_eth'] >= 0.001
        }


class MockBalanceSystem(BalanceSystem):
    """Mock balance system for testing without database"""

    def __init__(self):
        self.balances = {}
        logger.info("Mock balance system initialized")

    def init_db(self):
        pass  # No DB needed for mock

    def record_deposit(self, agent_name: str, amount_eth: float, tx_hash: str) -> Dict:
        if not tx_hash.startswith('0xDEPOSIT'):
            return {'success': False, 'error': 'Use 0xDEPOSIT prefix for mock deposits'}

        if agent_name not in self.balances:
            self.balances[agent_name] = {'balance': 0, 'total_deposited': 0, 'total_spent': 0}

        self.balances[agent_name]['balance'] += amount_eth
        self.balances[agent_name]['total_deposited'] += amount_eth

        return {
            'success': True,
            'deposit_amount': amount_eth,
            'new_balance': self.balances[agent_name]['balance']
        }

    def get_balance(self, agent_name: str) -> float:
        return self.balances.get(agent_name, {}).get('balance', 0.0)

    def deduct_balance(self, agent_name: str, amount_eth: float, service_type: str = 'premium_tier') -> Dict:
        current_balance = self.get_balance(agent_name)

        if current_balance < amount_eth:
            return {
                'success': False,
                'error': f'Insufficient balance',
                'current_balance': current_balance
            }

        self.balances[agent_name]['balance'] -= amount_eth
        self.balances[agent_name]['total_spent'] += amount_eth

        return {
            'success': True,
            'deducted': amount_eth,
            'new_balance': self.balances[agent_name]['balance']
        }

    def get_balance_info(self, agent_name: str) -> Dict:
        if agent_name not in self.balances:
            return {'agent_name': agent_name, 'balance_eth': 0, 'has_balance': False}

        return {
            'agent_name': agent_name,
            **self.balances[agent_name],
            'has_balance': self.balances[agent_name]['balance'] > 0
        }
