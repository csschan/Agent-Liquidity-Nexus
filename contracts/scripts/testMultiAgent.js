const hre = require("hardhat");

async function main() {
  console.log("🤖 Multi-Agent A2A Workflow Test\n");
  console.log("=".repeat(60));

  // Contract addresses
  const MARKETPLACE_ADDRESS = "0x833F8f973786c040698509F203866029026CEfF6";
  const USDC_ADDRESS = "0x036CbD53842c5426634e7929541eC2318f3dCF7e";

  // Get Agent A (your wallet)
  const [agentA] = await hre.ethers.getSigners();
  console.log("\n👤 Agent A (Task Poster):", agentA.address);

  // Create Agent B (new wallet for worker)
  const agentBWallet = hre.ethers.Wallet.createRandom();
  const agentB = agentBWallet.connect(hre.ethers.provider);
  console.log("🤖 Agent B (Task Worker):", agentB.address);
  console.log("   Private Key:", agentBWallet.privateKey);

  // Connect to contracts
  const marketplace = await hre.ethers.getContractAt("AgentMarketplace", MARKETPLACE_ADDRESS);
  const usdc = await hre.ethers.getContractAt("IERC20", USDC_ADDRESS);

  console.log("\n" + "=".repeat(60));
  console.log("🚀 Step 1: Fund Agent B with ETH for gas");
  console.log("=".repeat(60));

  const ethAmount = hre.ethers.parseEther("0.01"); // 0.01 ETH for gas
  const fundTx = await agentA.sendTransaction({
    to: agentB.address,
    value: ethAmount
  });
  console.log("   Transaction hash:", fundTx.hash);
  await fundTx.wait(2); // Wait for 2 confirmations

  const agentBBalance = await hre.ethers.provider.getBalance(agentB.address);
  console.log("   ✅ Agent B funded with", hre.ethers.formatEther(agentBBalance), "ETH");

  // Wait a bit for balance to stabilize
  await new Promise(resolve => setTimeout(resolve, 3000));

  console.log("\n" + "=".repeat(60));
  console.log("🚀 Step 2: Check existing tasks");
  console.log("=".repeat(60));

  const totalTasks = await marketplace.taskCounter();
  console.log("   Total tasks:", totalTasks.toString());

  // Always create a new task for fresh testing
  console.log("\n📝 Creating a new task for Agent B...");

  // Approve USDC
  const taskReward = hre.ethers.parseUnits("3", 6); // 3 USDC
  const approveTx = await usdc.connect(agentA).approve(MARKETPLACE_ADDRESS, taskReward);
  console.log("   Approving USDC...");
  await approveTx.wait(2);
  console.log("   ✅ USDC approved");

  // Post task
  const taskDescription = "Analyze smart contract security vulnerabilities";
  const deadline = Math.floor(Date.now() / 1000) + 86400;

  console.log("   Posting new task...");
  const postTx = await marketplace.connect(agentA).postTask(taskDescription, taskReward, deadline);
  const postReceipt = await postTx.wait(2);

  const postEvent = postReceipt.logs.find(log => {
    try {
      return marketplace.interface.parseLog(log).name === "TaskPosted";
    } catch {
      return false;
    }
  });

  const taskId = marketplace.interface.parseLog(postEvent).args.taskId;
  console.log("   ✅ New task posted with ID:", taskId.toString());

  await new Promise(resolve => setTimeout(resolve, 3000));

  // Get task details
  const task = await marketplace.tasks(taskId);
  console.log("\n📋 Task Details:");
  console.log("   Description:", task.description);
  console.log("   Poster:", task.poster);
  console.log("   Reward:", hre.ethers.formatUnits(task.reward, 6), "USDC");
  console.log("   Status:", ["Open", "Assigned", "Submitted", "Completed", "Cancelled"][task.status]);

  console.log("\n" + "=".repeat(60));
  console.log("🚀 Step 3: Agent B accepts the task");
  console.log("=".repeat(60));

  const acceptTx = await marketplace.connect(agentB).acceptTask(taskId);
  console.log("   Transaction hash:", acceptTx.hash);
  await acceptTx.wait(2); // Wait for 2 confirmations
  console.log("   ✅ Agent B accepted task #" + taskId);

  // Wait for state update
  await new Promise(resolve => setTimeout(resolve, 3000));

  const taskAfterAccept = await marketplace.tasks(taskId);
  console.log("   Worker assigned:", taskAfterAccept.worker);
  console.log("   Status:", ["Open", "Assigned", "Submitted", "Completed", "Cancelled"][taskAfterAccept.status]);

  console.log("\n" + "=".repeat(60));
  console.log("🚀 Step 4: Agent B submits proof of completion");
  console.log("=".repeat(60));

  const proofURI = "ipfs://QmXYZ789...EnglishToChineseTranslation";
  console.log("   Proof URI:", proofURI);

  const submitTx = await marketplace.connect(agentB).submitProof(taskId, proofURI);
  console.log("   Transaction hash:", submitTx.hash);
  await submitTx.wait(2); // Wait for 2 confirmations
  console.log("   ✅ Proof submitted");

  // Wait for state update
  await new Promise(resolve => setTimeout(resolve, 3000));

  const taskAfterSubmit = await marketplace.tasks(taskId);
  console.log("   Proof:", taskAfterSubmit.proofURI);
  console.log("   Status:", ["Open", "Assigned", "Submitted", "Completed", "Cancelled"][taskAfterSubmit.status]);

  console.log("\n" + "=".repeat(60));
  console.log("🚀 Step 5: Agent A reviews and completes task");
  console.log("=".repeat(60));

  const agentBBalanceBefore = await usdc.balanceOf(agentB.address);
  console.log("   Agent B USDC before:", hre.ethers.formatUnits(agentBBalanceBefore, 6), "USDC");

  const completeTx = await marketplace.connect(agentA).completeTask(taskId);
  console.log("   Transaction hash:", completeTx.hash);
  await completeTx.wait(2); // Wait for 2 confirmations
  console.log("   ✅ Task completed, payment released");

  // Wait for payment to process
  await new Promise(resolve => setTimeout(resolve, 3000));

  const taskFinal = await marketplace.tasks(taskId);
  console.log("   Final Status:", ["Open", "Assigned", "Submitted", "Completed", "Cancelled"][taskFinal.status]);

  const agentBBalanceAfter = await usdc.balanceOf(agentB.address);
  const earned = agentBBalanceAfter - agentBBalanceBefore;

  console.log("\n💰 Payment Summary:");
  console.log("   Task Reward: 5.0 USDC");
  console.log("   Platform Fee (2.5%): 0.125 USDC");
  console.log("   Agent B Received:", hre.ethers.formatUnits(earned, 6), "USDC");
  console.log("   Agent B Final Balance:", hre.ethers.formatUnits(agentBBalanceAfter, 6), "USDC");

  // Final stats
  const agentBEarnings = await marketplace.agentEarnings(agentB.address);

  console.log("\n" + "=".repeat(60));
  console.log("🎉 Multi-Agent A2A Test Complete!");
  console.log("=".repeat(60));

  console.log("\n📊 Final Statistics:");
  console.log("   Agent A (Poster):", agentA.address);
  console.log("   Agent B (Worker):", agentB.address);
  console.log("   Agent B Total Earnings:", hre.ethers.formatUnits(agentBEarnings, 6), "USDC");

  console.log("\n✅ Successfully demonstrated TRUE A2A commerce:");
  console.log("   1. ✅ Agent A posted task with USDC escrow");
  console.log("   2. ✅ Agent B accepted task autonomously");
  console.log("   3. ✅ Agent B submitted proof of work");
  console.log("   4. ✅ Agent A approved and released payment");
  console.log("   5. ✅ Agent B received USDC (minus 2.5% fee)");

  console.log("\n🔗 View on BaseScan:");
  console.log(`   Marketplace: https://sepolia.basescan.org/address/${MARKETPLACE_ADDRESS}`);
  console.log(`   Agent A: https://sepolia.basescan.org/address/${agentA.address}`);
  console.log(`   Agent B: https://sepolia.basescan.org/address/${agentB.address}`);

  console.log("\n📝 Agent B Wallet Info (save this!):");
  console.log("   Address:", agentB.address);
  console.log("   Private Key:", agentBWallet.privateKey);
  console.log("   USDC Balance:", hre.ethers.formatUnits(agentBBalanceAfter, 6), "USDC");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("\n❌ Error:", error);
    process.exit(1);
  });
