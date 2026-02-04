"""
Example Agent: CI/CD Test Runner
Demonstrates real-world Agentic Commerce usage
"""

import requests
import time
from datetime import datetime


class TestRunnerAgent:
    """
    Production CI/CD agent that needs USDC for automated testing
    Demonstrates autonomous economic decision-making
    """

    def __init__(self, name: str, wallet: str):
        self.name = name
        self.wallet = wallet
        self.base_url = "https://web-production-19f04.up.railway.app"

    def get_pricing(self):
        """Agent autonomously queries pricing options"""
        print(f"[{self.name}] Querying pricing options...")
        start = time.time()

        response = requests.get(f"{self.base_url}/pricing")
        pricing = response.json()

        elapsed = (time.time() - start) * 1000  # ms
        print(f"[{self.name}] ✅ Got pricing in {elapsed:.0f}ms")

        return pricing

    def calculate_optimal_tier(self, tests_needed: int, usdc_per_test: int = 10):
        """
        Agent autonomously calculates which tier is more economical
        This is the core of Agentic Commerce - autonomous decision-making
        """
        print(f"\n[{self.name}] 🤖 Analyzing requirements...")
        print(f"  Tests needed: {tests_needed}")
        print(f"  USDC per test: {usdc_per_test}")

        total_usdc = tests_needed * usdc_per_test
        print(f"  Total USDC required: {total_usdc}")

        pricing = self.get_pricing()

        free_tier = pricing['tiers']['free']
        premium_tier = pricing['tiers']['premium']

        # Calculate time needed with free tier
        free_requests_needed = total_usdc / free_tier['amount_usdc']
        free_days_needed = free_requests_needed * (free_tier['cooldown_hours'] / 24)

        # Calculate cost with premium tier
        premium_requests_needed = total_usdc / premium_tier['amount_usdc']
        premium_cost_eth = premium_requests_needed * premium_tier['cost_eth']

        print(f"\n[{self.name}] 📊 Cost Analysis:")
        print(f"  Free tier option:")
        print(f"    - Requests needed: {free_requests_needed:.1f}")
        print(f"    - Time required: {free_days_needed:.1f} days")
        print(f"    - Cost: FREE")
        print(f"  Premium tier option:")
        print(f"    - Requests needed: {premium_requests_needed:.1f}")
        print(f"    - Time required: <1 minute")
        print(f"    - Cost: {premium_cost_eth:.4f} ETH")

        # Agent makes autonomous decision
        if free_days_needed > 1:  # If free tier takes >1 day
            decision = "premium"
            reason = f"Time-critical: Free tier would take {free_days_needed:.1f} days"
        else:
            decision = "free"
            reason = "Cost-optimal: Free tier is sufficient"

        print(f"\n[{self.name}] ✅ Decision: {decision.upper()}")
        print(f"  Reason: {reason}")

        return {
            'tier': decision,
            'reason': reason,
            'cost_eth': premium_cost_eth if decision == 'premium' else 0
        }

    def request_usdc(self, tier: str = 'free', payment_tx: str = None):
        """Agent autonomously requests USDC"""
        endpoint = f"{self.base_url}/request-premium" if tier == 'premium' else f"{self.base_url}/request"

        data = {
            'agent_name': self.name,
            'wallet_address': self.wallet,
            'reason': f'Automated testing for CI/CD (decided {tier} tier autonomously)'
        }

        if tier == 'premium':
            data['payment_tx'] = payment_tx or f"0xPAID_auto_{int(time.time())}"

        print(f"\n[{self.name}] 💰 Requesting USDC from {tier} tier...")
        response = requests.post(endpoint, json=data)
        result = response.json()

        if result.get('success'):
            print(f"[{self.name}] ✅ Success!")
            print(f"  Amount: {result.get('amount')}")
            print(f"  Tier: {result.get('tier')}")
            if tier == 'premium':
                print(f"  Payment verified: {result.get('payment_verified')}")
        else:
            print(f"[{self.name}] ❌ Failed: {result.get('error')}")

        return result

    def run(self, tests_needed: int = 5):
        """
        Full autonomous workflow demonstrating Agentic Commerce
        """
        print("=" * 60)
        print(f"🤖 AGENT AUTONOMOUS WORKFLOW")
        print(f"Agent: {self.name}")
        print(f"Time: {datetime.now()}")
        print("=" * 60)

        # Step 1: Analyze requirements and make decision
        decision = self.calculate_optimal_tier(tests_needed)

        # Step 2: Execute decision
        result = self.request_usdc(
            tier=decision['tier'],
            payment_tx=f"0xPAID_{self.name}_{int(time.time())}" if decision['tier'] == 'premium' else None
        )

        # Step 3: Summary
        print("\n" + "=" * 60)
        print("🎯 SUMMARY")
        print("=" * 60)
        print(f"  Decision made by: AGENT (autonomous)")
        print(f"  Decision time: <1 second")
        print(f"  Human intervention: NONE")
        print(f"  Tier selected: {decision['tier']}")
        print(f"  Result: {'SUCCESS' if result.get('success') else 'FAILED'}")
        print("\n💡 This is Agentic Commerce:")
        print("  • Agent evaluated options autonomously")
        print("  • Agent made economic decision based on algorithm")
        print("  • Agent executed payment (if needed) and received service")
        print("  • Zero human involvement required")
        print("=" * 60)


def compare_human_vs_agent():
    """Demonstrate the speed difference between human and agent"""
    print("\n" + "=" * 60)
    print("⏱️  HUMAN vs AGENT COMPARISON")
    print("=" * 60)

    print("\n👨 HUMAN WORKFLOW:")
    print("  1. Open browser and navigate to faucet (30s)")
    print("  2. Read pricing tiers (60s)")
    print("  3. Calculate ROI manually or guess (300s)")
    print("  4. Fill form and submit (30s)")
    print("  5. Wait for confirmation (30s)")
    print("  TOTAL: ~7 minutes (420 seconds)")
    print("  Reliability: Depends on human availability, timezone")

    print("\n🤖 AGENT WORKFLOW:")
    agent = TestRunnerAgent(
        name="ComparisonAgent",
        wallet="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1"
    )

    start = time.time()
    decision = agent.calculate_optimal_tier(tests_needed=5)
    agent.request_usdc(tier=decision['tier'])
    elapsed = time.time() - start

    print(f"\n  TOTAL: {elapsed:.1f} seconds")
    print("  Reliability: 24/7, deterministic")

    speedup = 420 / elapsed
    print(f"\n🚀 AGENT IS {speedup:.0f}X FASTER")
    print("=" * 60)


if __name__ == "__main__":
    # Example 1: Small job (free tier optimal)
    print("\n📝 EXAMPLE 1: Small Testing Job")
    agent1 = TestRunnerAgent(
        name="SmallTestAgent",
        wallet="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1"
    )
    agent1.run(tests_needed=1)  # Needs 10 USDC

    time.sleep(2)

    # Example 2: Large job (premium tier optimal)
    print("\n\n📝 EXAMPLE 2: Large CI/CD Job")
    agent2 = TestRunnerAgent(
        name="ProductionCIAgent",
        wallet="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1"
    )
    agent2.run(tests_needed=50)  # Needs 500 USDC

    time.sleep(2)

    # Example 3: Human vs Agent comparison
    compare_human_vs_agent()

    print("\n\n✅ Demo complete!")
    print("\nThis script demonstrates:")
    print("  1. Agents querying pricing autonomously")
    print("  2. Agents calculating optimal economic decisions")
    print("  3. Agents executing payments and receiving services")
    print("  4. Quantifiable speed advantage over humans")
    print("\n🦞 This is Agentic Commerce in action!")
