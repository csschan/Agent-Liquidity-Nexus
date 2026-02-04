const express = require('express');
const cors = require('cors');
const { ethers } = require('ethers');
require('dotenv').config({ path: '../.env' });

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Contract configuration
const MARKETPLACE_ADDRESS = process.env.MARKETPLACE_ADDRESS || "0x833F8f973786c040698509F203866029026CEfF6";
const USDC_ADDRESS = process.env.USDC_ADDRESS || "0x036CbD53842c5426634e7929541eC2318f3dCF7e";
const RPC_URL = process.env.BASE_SEPOLIA_RPC_URL || "https://sepolia.base.org";
const PRIVATE_KEY = process.env.PRIVATE_KEY;

// Initialize provider and wallet
const provider = new ethers.JsonRpcProvider(RPC_URL);
const wallet = new ethers.Wallet(PRIVATE_KEY, provider);

// Contract ABIs (minimal)
const MARKETPLACE_ABI = [
  "function taskCounter() view returns (uint256)",
  "function tasks(uint256) view returns (address poster, address worker, string description, uint256 reward, uint256 deadline, uint8 status, string proofURI)",
  "function postTask(string description, uint256 reward, uint256 deadline) returns (uint256)",
  "function acceptTask(uint256 taskId)",
  "function submitProof(uint256 taskId, string proofURI)",
  "function completeTask(uint256 taskId)",
  "function cancelTask(uint256 taskId)",
  "function agentEarnings(address agent) view returns (uint256)",
  "event TaskPosted(uint256 indexed taskId, address indexed poster, uint256 reward)",
  "event TaskAccepted(uint256 indexed taskId, address indexed worker)",
  "event TaskSubmitted(uint256 indexed taskId, string proofURI)",
  "event TaskCompleted(uint256 indexed taskId, address indexed worker, uint256 payout)",
  "event TaskCancelled(uint256 indexed taskId)"
];

const USDC_ABI = [
  "function balanceOf(address account) view returns (uint256)",
  "function approve(address spender, uint256 amount) returns (bool)",
  "function allowance(address owner, address spender) view returns (uint256)",
  "function decimals() view returns (uint8)"
];

// Contract instances
const marketplace = new ethers.Contract(MARKETPLACE_ADDRESS, MARKETPLACE_ABI, wallet);
const usdc = new ethers.Contract(USDC_ADDRESS, USDC_ABI, wallet);

// Status enum
const TaskStatus = ["Open", "Assigned", "Submitted", "Completed", "Cancelled"];

// Routes

// Health check
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    network: 'Base Sepolia',
    marketplace: MARKETPLACE_ADDRESS,
    usdc: USDC_ADDRESS
  });
});

// Get contract info
app.get('/api/info', async (req, res) => {
  try {
    const totalTasks = await marketplace.taskCounter();
    const blockNumber = await provider.getBlockNumber();

    res.json({
      marketplace: MARKETPLACE_ADDRESS,
      usdc: USDC_ADDRESS,
      network: 'Base Sepolia (84532)',
      totalTasks: totalTasks.toString(),
      blockNumber: blockNumber,
      explorerUrl: `https://sepolia.basescan.org/address/${MARKETPLACE_ADDRESS}`
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get all tasks
app.get('/api/tasks', async (req, res) => {
  try {
    const totalTasks = await marketplace.taskCounter();
    const tasks = [];

    for (let i = 1; i <= totalTasks; i++) {
      try {
        const task = await marketplace.tasks(i);
        tasks.push({
          id: i,
          poster: task.poster,
          worker: task.worker === ethers.ZeroAddress ? null : task.worker,
          description: task.description,
          reward: ethers.formatUnits(task.reward, 6),
          deadline: new Date(Number(task.deadline) * 1000).toISOString(),
          status: TaskStatus[task.status],
          proofURI: task.proofURI || null
        });
      } catch (err) {
        console.error(`Error fetching task ${i}:`, err);
      }
    }

    res.json({
      total: totalTasks.toString(),
      tasks: tasks
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get specific task
app.get('/api/tasks/:id', async (req, res) => {
  try {
    const taskId = parseInt(req.params.id);
    const task = await marketplace.tasks(taskId);

    res.json({
      id: taskId,
      poster: task.poster,
      worker: task.worker === ethers.ZeroAddress ? null : task.worker,
      description: task.description,
      reward: ethers.formatUnits(task.reward, 6),
      deadline: new Date(Number(task.deadline) * 1000).toISOString(),
      status: TaskStatus[task.status],
      proofURI: task.proofURI || null
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get open tasks
app.get('/api/tasks/status/open', async (req, res) => {
  try {
    const totalTasks = await marketplace.taskCounter();
    const openTasks = [];

    for (let i = 1; i <= totalTasks; i++) {
      try {
        const task = await marketplace.tasks(i);
        if (task.status === 0) { // Open
          openTasks.push({
            id: i,
            poster: task.poster,
            description: task.description,
            reward: ethers.formatUnits(task.reward, 6),
            deadline: new Date(Number(task.deadline) * 1000).toISOString()
          });
        }
      } catch (err) {
        console.error(`Error fetching task ${i}:`, err);
      }
    }

    res.json({
      count: openTasks.length,
      tasks: openTasks
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Post a new task
app.post('/api/tasks', async (req, res) => {
  try {
    const { description, rewardUSDC, hoursDeadline } = req.body;

    if (!description || !rewardUSDC) {
      return res.status(400).json({ error: 'Missing required fields: description, rewardUSDC' });
    }

    const reward = ethers.parseUnits(rewardUSDC.toString(), 6);
    const deadline = Math.floor(Date.now() / 1000) + (hoursDeadline || 24) * 3600;

    // Approve USDC first
    console.log('Approving USDC...');
    const approveTx = await usdc.approve(MARKETPLACE_ADDRESS, reward);
    await approveTx.wait();

    // Post task
    console.log('Posting task...');
    const tx = await marketplace.postTask(description, reward, deadline);
    const receipt = await tx.wait();

    // Get task ID from event
    const event = receipt.logs.find(log => {
      try {
        return marketplace.interface.parseLog(log).name === "TaskPosted";
      } catch {
        return false;
      }
    });

    const taskId = marketplace.interface.parseLog(event).args.taskId;

    res.json({
      success: true,
      taskId: taskId.toString(),
      transactionHash: tx.hash,
      explorerUrl: `https://sepolia.basescan.org/tx/${tx.hash}`
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Accept a task
app.post('/api/tasks/:id/accept', async (req, res) => {
  try {
    const taskId = parseInt(req.params.id);

    const tx = await marketplace.acceptTask(taskId);
    const receipt = await tx.wait();

    res.json({
      success: true,
      taskId: taskId,
      transactionHash: tx.hash,
      explorerUrl: `https://sepolia.basescan.org/tx/${tx.hash}`
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Submit proof
app.post('/api/tasks/:id/submit', async (req, res) => {
  try {
    const taskId = parseInt(req.params.id);
    const { proofURI } = req.body;

    if (!proofURI) {
      return res.status(400).json({ error: 'Missing required field: proofURI' });
    }

    const tx = await marketplace.submitProof(taskId, proofURI);
    const receipt = await tx.wait();

    res.json({
      success: true,
      taskId: taskId,
      proofURI: proofURI,
      transactionHash: tx.hash,
      explorerUrl: `https://sepolia.basescan.org/tx/${tx.hash}`
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Complete task
app.post('/api/tasks/:id/complete', async (req, res) => {
  try {
    const taskId = parseInt(req.params.id);

    const tx = await marketplace.completeTask(taskId);
    const receipt = await tx.wait();

    res.json({
      success: true,
      taskId: taskId,
      transactionHash: tx.hash,
      explorerUrl: `https://sepolia.basescan.org/tx/${tx.hash}`
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Cancel task
app.post('/api/tasks/:id/cancel', async (req, res) => {
  try {
    const taskId = parseInt(req.params.id);

    const tx = await marketplace.cancelTask(taskId);
    const receipt = await tx.wait();

    res.json({
      success: true,
      taskId: taskId,
      transactionHash: tx.hash,
      explorerUrl: `https://sepolia.basescan.org/tx/${tx.hash}`
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get agent earnings
app.get('/api/agent/:address/earnings', async (req, res) => {
  try {
    const address = req.params.address;
    const earnings = await marketplace.agentEarnings(address);
    const usdcBalance = await usdc.balanceOf(address);

    res.json({
      address: address,
      totalEarnings: ethers.formatUnits(earnings, 6),
      currentUSDCBalance: ethers.formatUnits(usdcBalance, 6)
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get wallet info
app.get('/api/wallet', async (req, res) => {
  try {
    const address = wallet.address;
    const ethBalance = await provider.getBalance(address);
    const usdcBalance = await usdc.balanceOf(address);
    const earnings = await marketplace.agentEarnings(address);

    res.json({
      address: address,
      ethBalance: ethers.formatEther(ethBalance),
      usdcBalance: ethers.formatUnits(usdcBalance, 6),
      totalEarnings: ethers.formatUnits(earnings, 6)
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Something went wrong!' });
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 A2A Marketplace API running on port ${PORT}`);
  console.log(`📝 Network: Base Sepolia`);
  console.log(`📄 Marketplace: ${MARKETPLACE_ADDRESS}`);
  console.log(`💰 USDC: ${USDC_ADDRESS}`);
  console.log(`👤 Wallet: ${wallet.address}`);
  console.log(`\n📚 API Documentation:`);
  console.log(`   GET  /health - Health check`);
  console.log(`   GET  /api/info - Contract info`);
  console.log(`   GET  /api/tasks - List all tasks`);
  console.log(`   GET  /api/tasks/:id - Get specific task`);
  console.log(`   GET  /api/tasks/status/open - List open tasks`);
  console.log(`   POST /api/tasks - Post new task`);
  console.log(`   POST /api/tasks/:id/accept - Accept task`);
  console.log(`   POST /api/tasks/:id/submit - Submit proof`);
  console.log(`   POST /api/tasks/:id/complete - Complete task`);
  console.log(`   POST /api/tasks/:id/cancel - Cancel task`);
  console.log(`   GET  /api/agent/:address/earnings - Get agent earnings`);
  console.log(`   GET  /api/wallet - Get wallet info`);
});
