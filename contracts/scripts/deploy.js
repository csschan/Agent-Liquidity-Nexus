const hre = require("hardhat");

async function main() {
  console.log("🚀 Deploying AgentMarketplace...\n");

  // Get network name
  const network = hre.network.name;
  console.log("Network:", network);

  // USDC addresses for different networks
  const USDC_ADDRESSES = {
    sepolia: "0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238",      // Ethereum Sepolia
    baseSepolia: "0x036CbD53842c5426634e7929541eC2318f3dCF7e"   // Base Sepolia (Circle's official)
  };

  const USDC_ADDRESS = USDC_ADDRESSES[network] || USDC_ADDRESSES.baseSepolia;

  // Get deployer
  const [deployer] = await hre.ethers.getSigners();
  console.log("Deploying with account:", deployer.address);
  console.log("Account balance:", (await hre.ethers.provider.getBalance(deployer.address)).toString(), "\n");

  // Deploy AgentMarketplace
  const AgentMarketplace = await hre.ethers.getContractFactory("AgentMarketplace");
  const marketplace = await AgentMarketplace.deploy(USDC_ADDRESS);

  await marketplace.waitForDeployment();

  const address = await marketplace.getAddress();

  console.log("✅ AgentMarketplace deployed to:", address);
  console.log("📝 USDC Token:", USDC_ADDRESS);
  console.log("👤 Owner:", deployer.address);

  const explorerUrls = {
    sepolia: `https://sepolia.etherscan.io/address/${address}`,
    baseSepolia: `https://sepolia.basescan.org/address/${address}`
  };
  console.log("\n🔗 Block Explorer:", explorerUrls[network] || explorerUrls.baseSepolia);

  // Save deployment info
  const fs = require('fs');
  const deploymentInfo = {
    network: network,
    contractAddress: address,
    usdcAddress: USDC_ADDRESS,
    owner: deployer.address,
    deployedAt: new Date().toISOString(),
    blockNumber: await hre.ethers.provider.getBlockNumber()
  };

  fs.writeFileSync(
    '../DEPLOYMENT.json',
    JSON.stringify(deploymentInfo, null, 2)
  );

  console.log("\n💾 Deployment info saved to DEPLOYMENT.json");

  // Wait for block confirmations before verifying
  console.log("\n⏳ Waiting for block confirmations...");
  await marketplace.deploymentTransaction().wait(6);

  // Verify on Block Explorer
  console.log("\n🔍 Verifying contract on block explorer...");
  try {
    await hre.run("verify:verify", {
      address: address,
      constructorArguments: [USDC_ADDRESS],
    });
    console.log("✅ Contract verified!");
  } catch (error) {
    console.log("❌ Verification failed:", error.message);
    console.log("You can verify manually later with:");
    console.log(`npx hardhat verify --network ${network} ${address} ${USDC_ADDRESS}`);
  }

  console.log("\n🎉 Deployment complete!");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
