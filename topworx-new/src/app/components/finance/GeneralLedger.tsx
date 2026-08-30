import React, { useState } from 'react';
import { Button, Card, Col, Input, InputNumber, Modal, Row, Select, Table, Typography } from 'antd';
import { BankOutlined, PlusOutlined } from '@ant-design/icons';

const mockLedgerEntries = [
  {
    id: 1,
    date: '2024-04-22',
    description: 'فروش محصول A',
    account: 'حساب‌های دریافتنی',
    debit: 50000,
    credit: 0,
    balance: 50000,
  },
  {
    id: 2,
    date: '2024-04-22',
    description: 'فروش محصول A',
    account: 'فروش',
    debit: 0,
    credit: 50000,
    balance: -50000,
  },
  {
    id: 3,
    date: '2024-04-21',
    description: 'خرید مواد اولیه',
    account: 'موجودی کالا',
    debit: 30000,
    credit: 0,
    balance: 30000,
  },
  {
    id: 4,
    date: '2024-04-21',
    description: 'خرید مواد اولیه',
    account: 'حساب‌های پرداختنی',
    debit: 0,
    credit: 30000,
    balance: -30000,
  },
];

const accountTypes = [
  'دارایی‌ها',
  'بدهی‌ها',
  'سرمایه',
  'درآمد',
  'هزینه',
];

export const GeneralLedger: React.FC = () => {
  const [openDialog, setOpenDialog] = useState(false);
  const [newEntry, setNewEntry] = useState({
    date: '',
    description: '',
    account: '',
    debit: '',
    credit: '',
  });

  const handleAddEntry = () => {
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setNewEntry({
      date: '',
      description: '',
      account: '',
      debit: '',
      credit: '',
    });
  };

  const handleSaveEntry = () => {
    // در اینجا تراکنش جدید ذخیره می‌شود
    handleCloseDialog();
  };

  return (
    <Card>
      <div>
        <div>
          <Typography.Title level={4}>
            <AccountBalance style={{  mr: 1  }} />
            دفتر کل عمومی
          </Typography.Title>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={handleAddEntry}
          >
            ثبت تراکنش جدید
          </Button>
        </div>

        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>تاریخ</TableCell>
                <TableCell>شرح</TableCell>
                <TableCell>حساب</TableCell>
                <TableCell align="right">بدهکار</TableCell>
                <TableCell align="right">بستانکار</TableCell>
                <TableCell align="right">مانده</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {mockLedgerEntries.map((entry) => (
                <TableRow key={entry.id}>
                  <TableCell>{entry.date}</TableCell>
                  <TableCell>{entry.description}</TableCell>
                  <TableCell>{entry.account}</TableCell>
                  <TableCell align="right">
                    {entry.debit > 0 ? entry.debit.toLocaleString() : '-'}
                  </TableCell>
                  <TableCell align="right">
                    {entry.credit > 0 ? entry.credit.toLocaleString() : '-'}
                  </TableCell>
                  <TableCell 
                    align="right"
                    style={{ 
                      color: entry.balance >= 0 ? 'success.main' : 'error.main',
                     }}
                  >
                    {Math.abs(entry.balance).toLocaleString()}
                    {entry.balance < 0 ? ' (CR)' : ' (DR)'}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>

        {/* Dialog برای ثبت تراکنش جدید */}
        <Modal open={false} onCancel={() => {}} footer={null}>
          <div>ثبت تراکنش جدید</div>
          <div>
            <Row gutter={[16, 16]}>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="تاریخ"
                  type="date"
                  value={newEntry.date}
                  onChange={(e) => setNewEntry({ ...newEntry, date: e.target.value })}
                  InputLabelProps={{ shrink: true }}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <FormControl fullWidth>
                  <InputLabel>نوع حساب</span>
                  <Select
                    value={newEntry.account}
                    label="نوع حساب"
                    onChange={(e) => setNewEntry({ ...newEntry, account: e.target.value })}
                  >
                    {accountTypes.map((type) => (
                      <MenuItem key={type} value={type}>
                        {type}
                      </Select.Option>
                    ))}
                  </Select>
                </div>
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="شرح تراکنش"
                  multiline
                  rows={3}
                  value={newEntry.description}
                  onChange={(e) => setNewEntry({ ...newEntry, description: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="مبلغ بدهکار"
                  type="number"
                  value={newEntry.debit}
                  onChange={(e) => setNewEntry({ ...newEntry, debit: e.target.value })}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="مبلغ بستانکار"
                  type="number"
                  value={newEntry.credit}
                  onChange={(e) => setNewEntry({ ...newEntry, credit: e.target.value })}
                />
              </Col>
            </Row>
          </div>
          <div>
            <Button onClick={handleCloseDialog}>انصراف</Button>
            <Button onClick={handleSaveEntry} variant="contained">
              ثبت تراکنش
            </Button>
          </div>
        </Modal>
      </div>
    </Card>
  );
}; 