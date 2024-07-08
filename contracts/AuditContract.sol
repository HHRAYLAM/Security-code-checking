// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract AuditContract {
    struct AuditRecord {
        string codeHash;
        address auditor;
        uint256 timestamp;
    }

    mapping(uint256 => AuditRecord) public auditRecords;
    uint256 public recordCount;
    uint256 public auditFee = 0.0001 ether;
    address public owner;

    event AuditRecorded(uint256 recordId, string codeHash, address auditor, uint256 timestamp);
    event AuditFeeSet(uint256 newFee);

    constructor() {
        owner = msg.sender; // 合约部署者为合约所有者（管理员）
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Only contract owner can call this function");
        _;
    }

    function uploadAuditRecord(string memory _codeHash) public payable {
        require(msg.value >= auditFee, "Insufficient audit fee");

        recordCount++;
        auditRecords[recordCount] = AuditRecord(_codeHash, msg.sender, block.timestamp);

        emit AuditRecorded(recordCount, _codeHash, msg.sender, block.timestamp);
    }

    function setAuditFee(uint256 _newFee) public onlyOwner {
        auditFee = _newFee;
        emit AuditFeeSet(_newFee);
    }

    function changeOwner(address _newOwner) public onlyOwner {
        owner = _newOwner;
    }
}