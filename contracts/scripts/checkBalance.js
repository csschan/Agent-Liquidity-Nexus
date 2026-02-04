const hre = require("hardhat");

async function main() {
  const [signer] = await hre.ethers.getSigners();
  console.log('Address:', signer.address);
  const balance = await hre.ethers.provider.getBalance(signer.address);
  console.log('Balance:', hre.ethers.formatEther(balance), 'ETH');
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
