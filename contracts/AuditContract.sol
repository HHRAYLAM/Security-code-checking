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
    uint256 public auditFee = 0.01 ether;

    event AuditRecorded(uint256 recordId, string codeHash, address auditor, uint256 timestamp);

    function uploadAuditRecord(string memory _codeHash) public payable {
        require(msg.value >= auditFee, "Insufficient audit fee");

        recordCount++;
        auditRecords[recordCount] = AuditRecord(_codeHash, msg.sender, block.timestamp);

        emit AuditRecorded(recordCount, _codeHash, msg.sender, block.timestamp);
    }

    function setAuditFee(uint256 _newFee) public {
        auditFee = _newFee;
    }
}