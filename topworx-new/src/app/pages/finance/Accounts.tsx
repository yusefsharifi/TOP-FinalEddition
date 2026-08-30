import React from 'react';
import { Card, Table, Typography } from 'antd';

const mockAccounts = [
  {
    id: 1,
    name: 'Cash',
    type: 'Asset',
    balance: 50000,
    lastTransaction: '2024-04-22',
  },
  {
    id: 2,
    name: 'Accounts Receivable',
    type: 'Asset',
    balance: 25000,
    lastTransaction: '2024-04-21',
  },
  {
    id: 3,
    name: 'Accounts Payable',
    type: 'Liability',
    balance: -15000,
    lastTransaction: '2024-04-20',
  },
];

export const Accounts: React.FC = () => {
  return (
    <div>
      <Typography.Title level={2}>
        Accounts
      </Typography.Title>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Type</TableCell>
              <TableCell align="right">Balance</TableCell>
              <TableCell>Last Transaction</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {mockAccounts.map((account) => (
              <TableRow key={account.id}>
                <TableCell>{account.name}</TableCell>
                <TableCell>{account.type}</TableCell>
                <TableCell align="right" style={{ 
                  color: account.balance >= 0 ? 'success.main' : 'error.main',
                 }}>
                  ${Math.abs(account.balance).toLocaleString()}
                  {account.balance < 0 ? ' (DR)' : ' (CR)'}
                </TableCell>
                <TableCell>{account.lastTransaction}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}; 