const hre = require("hardhat");

async function main() {
  console.log("🧪 Testing AgentMarketplace A2A Workflow\n");
  console.log("=".repeat(60));

  // Contract addresses from deployment
  const MARKETPLACE_ADDRESS = "0x833F8f973786c040698509F203866029026CEfF6";
  const USDC_ADDRESS = "0x036CbD53842c5426634e7929541eC2318f3dCF7e";

  // Get signer (Agent A)
  const [agentA] = await hre.ethers.getSigners();
  console.log("\n👤 Agent A (Tester):", agentA.address);

  // Connect to contracts
  const marketplace = await hre.ethers.getContractAt("AgentMarketplace", MARKETPLACE_ADDRESS);
  const usdc = await hre.ethers.getContractAt("IERC20", USDC_ADDRESS);

  // Check balances
  console.log("\n📊 Initial State:");
  const usdcBalance = await usdc.balanceOf(agentA.address);
  console.log("   USDC Balance:", hre.ethers.formatUnits(usdcBalance, 6), "USDC");

  const ethBalance = await hre.ethers.provider.getBalance(agentA.address);
  console.log("   ETH Balance:", hre.ethers.formatEther(ethBalance), "ETH");

  if (usdcBalance === 0n) {
    console.log("\n❌ Error: No USDC balance. Please get testnet USDC first.");
    process.exit(1);
  }

  // Test parameters
  const taskReward = hre.ethers.parseUnits("5", 6); // 5 USDC
  const taskDescription = "Translate document from English to Chinese";
  const deadline = Math.floor(Date.now() / 1000) + 86400; // 24 hours

  console.log("\n" + "=".repeat(60));
  console.log("🚀 Step 1: Approve USDC for marketplace");
  console.log("=".repeat(60));

  const approveTx = await usdc.approve(MARKETPLACE_ADDRESS, taskReward);
  console.log("   Transaction hash:", approveTx.hash);
  await approveTx.wait();
  console.log("   ✅ Approved 5 USDC");

  console.log("\n" + "=".repeat(60));
  console.log("🚀 Step 2: Agent A posts a task");
  console.log("=".repeat(60));
  console.log("   Description:", taskDescription);
  console.log("   Reward: 5 USDC");
  console.log("   Deadline: 24 hours");

  const postTx = await marketplace.postTask(taskDescription, taskReward, deadline);
  console.log("   Transaction hash:", postTx.hash);
  const postReceipt = await postTx.wait();

  // Get task ID from event
  const postEvent = postReceipt.logs.find(log => {
    try {
      return marketplace.interface.parseLog(log).name === "TaskPosted";
    } catch {
      return false;
    }
  });

  const taskId = marketplace.interface.parseLog(postEvent).args.taskId;
  console.log("   ✅ Task posted with ID:", taskId.toString());

  // Check task details
  const task = await marketplace.tasks(taskId);
  console.log("\n📋 Task Details:");
  console.log("   Poster:", task.poster);
  console.log("   Reward:", hre.ethers.formatUnits(task.reward, 6), "USDC");
  console.log("   Status:", ["Open", "Assigned", "Submitted", "Completed", "Cancelled"][task.status]);

  console.log("\n" + "=".repeat(60));
  console.log("🚀 Step 3: Agent A accepts the task (simulating Agent B)");
  console.log("=".repeat(60));
  console.log("   Note: Using same account for testing");

  const acceptTx = await marketplace.acceptTask(taskId);
  console.log("   Transaction hash:", acceptTx.hash);
  await acceptTx.wait();
  console.log("   ✅ Task accepted");

  // Check updated task
  const taskAfterAccept = await marketplace.tasks(taskId);
  console.log("   Assigned to:", taskAfterAccept.worker);
  console.log("   Status:", ["Open", "Assigned", "Submitted", "Completed", "Cancelled"][taskAfterAccept.status]);

  console.log("\n" + "=".repeat(60));
  console.log("🚀 Step 4: Submit proof of completion");
  console.log("=".repeat(60));

  const proofURI = "ipfs://QmTest123...CompletedTranslationDocument";
  console.log("   Proof URI:", proofURI);

  const submitTx = await marketplace.submitProof(taskId, proofURI);
  console.log("   Transaction hash:", submitTx.hash);
  await submitTx.wait();
  console.log("   ✅ Proof submitted");

  // Check updated task
  const taskAfterSubmit = await marketplace.tasks(taskId);
  console.log("   Proof URI:", taskAfterSubmit.proofURI);
  console.log("   Status:", ["Open", "Assigned", "Submitted", "Completed", "Cancelled"][taskAfterSubmit.status]);

  console.log("\n" + "=".repeat(60));
  console.log("🚀 Step 5: Agent A completes task and releases payment");
  console.log("=".repeat(60));

  const balanceBefore = await usdc.balanceOf(agentA.address);

  const completeTx = await marketplace.completeTask(taskId);
  console.log("   Transaction hash:", completeTx.hash);
  await completeTx.wait();
  console.log("   ✅ Task completed and payment released");

  // Check final task status
  const taskFinal = await marketplace.tasks(taskId);
  console.log("   Final Status:", ["Open", "Assigned", "Submitted", "Completed", "Cancelled"][taskFinal.status]);

  // Check balances
  const balanceAfter = await usdc.balanceOf(agentA.address);
  const earned = balanceAfter - balanceBefore;

  console.log("\n📊 Final State:");
  console.log("   USDC returned:", hre.ethers.formatUnits(earned, 6), "USDC");
  console.log("   Platform fee (2.5%):", hre.ethers.formatUnits(taskReward - earned, 6), "USDC");
  console.log("   New USDC Balance:", hre.ethers.formatUnits(balanceAfter, 6), "USDC");

  // Get marketplace stats
  const totalTasks = await marketplace.taskCounter();
  console.log("\n📈 Marketplace Stats:");
  console.log("   Total Tasks Created:", totalTasks.toString());

  console.log("\n" + "=".repeat(60));
  console.log("🎉 A2A Workflow Test Complete!");
  console.log("=".repeat(60));
  console.log("\n✅ All functions tested successfully:");
  console.log("   1. ✅ Approve USDC");
  console.log("   2. ✅ Post Task (Agent A)");
  console.log("   3. ✅ Accept Task (Agent B)");
  console.log("   4. ✅ Submit Proof (Agent B)");
  console.log("   5. ✅ Complete Task & Release Payment (Agent A)");

  console.log("\n🔗 View on BaseScan:");
  console.log(`   https://sepolia.basescan.org/address/${MARKETPLACE_ADDRESS}`);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("\n❌ Error:", error);
    process.exit(1);
  });
