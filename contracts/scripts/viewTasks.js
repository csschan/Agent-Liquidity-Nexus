const hre = require("hardhat");

async function main() {
  console.log("📋 AgentMarketplace Task Viewer\n");
  console.log("=".repeat(60));

  // Contract addresses
  const MARKETPLACE_ADDRESS = "0x833F8f973786c040698509F203866029026CEfF6";
  const USDC_ADDRESS = "0x036CbD53842c5426634e7929541eC2318f3dCF7e";

  // Connect to contracts
  const marketplace = await hre.ethers.getContractAt("AgentMarketplace", MARKETPLACE_ADDRESS);
  const usdc = await hre.ethers.getContractAt("IERC20", USDC_ADDRESS);

  // Get total tasks
  const totalTasks = await marketplace.taskCounter();
  console.log("\n📊 Marketplace Overview:");
  console.log("   Contract:", MARKETPLACE_ADDRESS);
  console.log("   USDC Token:", USDC_ADDRESS);
  console.log("   Total Tasks:", totalTasks.toString());
  console.log("   Platform Fee: 2.5%");

  // Display all tasks
  console.log("\n" + "=".repeat(60));
  console.log("📝 All Tasks:");
  console.log("=".repeat(60));

  const statusNames = ["Open", "Assigned", "Submitted", "Completed", "Cancelled"];

  for (let i = 1; i <= totalTasks; i++) {
    try {
      const task = await marketplace.tasks(i);

      console.log(`\n🎯 Task #${i}:`);
      console.log("   Description:", task.description);
      console.log("   Poster:", task.poster);
      console.log("   Worker:", task.worker === "0x0000000000000000000000000000000000000000" ? "None" : task.worker);
      console.log("   Reward:", hre.ethers.formatUnits(task.reward, 6), "USDC");
      console.log("   Status:", statusNames[task.status]);
      console.log("   Deadline:", new Date(Number(task.deadline) * 1000).toLocaleString());

      if (task.proofURI) {
        console.log("   Proof:", task.proofURI);
      }
    } catch (error) {
      console.log(`\n❌ Error reading task #${i}:`, error.message);
    }
  }

  // Get open tasks
  console.log("\n" + "=".repeat(60));
  console.log("🔓 Available Tasks (Open):");
  console.log("=".repeat(60));

  let openCount = 0;
  for (let i = 1; i <= totalTasks; i++) {
    const task = await marketplace.tasks(i);
    if (task.status === 0) { // Open
      openCount++;
      console.log(`\n✨ Task #${i}:`);
      console.log("   ${task.description}");
      console.log("   Reward: ${hre.ethers.formatUnits(task.reward, 6)} USDC");
      console.log("   Poster: ${task.poster}");
    }
  }

  if (openCount === 0) {
    console.log("\n   No open tasks available");
  } else {
    console.log(`\n   Total open tasks: ${openCount}`);
  }

  // Get marketplace stats
  const [signer] = await hre.ethers.getSigners();
  const myEarnings = await marketplace.agentEarnings(signer.address);

  console.log("\n" + "=".repeat(60));
  console.log("👤 Your Account:");
  console.log("=".repeat(60));
  console.log("   Address:", signer.address);
  console.log("   Total Earnings:", hre.ethers.formatUnits(myEarnings, 6), "USDC");

  const usdcBalance = await usdc.balanceOf(signer.address);
  console.log("   USDC Balance:", hre.ethers.formatUnits(usdcBalance, 6), "USDC");

  console.log("\n🔗 View on BaseScan:");
  console.log(`   https://sepolia.basescan.org/address/${MARKETPLACE_ADDRESS}`);
  console.log("\n" + "=".repeat(60));
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("\n❌ Error:", error);
    process.exit(1);
  });
