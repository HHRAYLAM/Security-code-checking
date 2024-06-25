const path = require("path");
const HDWalletProvider = require("@truffle/hdwallet-provider");
require("dotenv").config();

const mnemonic = process.env.MNEMONIC;
const infuraApiKey = process.env.INFURA_API_KEY;

module.exports = {
  networks: {
    development: {
      host: "127.0.0.1", // Ganache 或本地以太坊节点的主机
      port: 7545, // Ganache 或本地以太坊节点的端口
      network_id: "5777", // 任何网络都可连接
    },
    lineaSepolia: {
      provider: () =>
        new HDWalletProvider(
          mnemonic,
          `wss://linea-sepolia.infura.io/ws/v3/${infuraApiKey}`
        ),
      network_id: 59141, // Linea Sepolia 测试网络的网络ID
      gas: 5500000, // 设置 gas 限制
      gasPrice: 10000000000, // 设置 gas 价格
      confirmations: 2, // 设置确认数
      timeoutBlocks: 200, // 设置超时区块数
    },
    lineaMainnet: {
      provider: () =>
        new HDWalletProvider(
          mnemonic,
          `wps://linea-mainnet.infura.io/v3/${infuraApiKey}`
        ),
      network_id: 59144, // Linea 主网的网络ID
      gas: 5500000, // 设置 gas 限制
      gasPrice: 10000000000, // 设置 gas 价格
      confirmations: 2, // 设置确认数
      timeoutBlocks: 200, // 设置超时区块数
    },
  },
  compilers: {
    solc: {
      version: "0.8.0", // Solidity 编译器版本
      settings: {
        optimizer: {
          enabled: true,
          runs: 200,
        },
      },
    },
  },
};
