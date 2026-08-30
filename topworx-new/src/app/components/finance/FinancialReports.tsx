import React, { useState } from 'react';
import { Button, Card, Col, Input, InputNumber, Modal, Row, Select, Table, Tabs, Tag, Typography } from 'antd';
import { BankOutlined, BarChartOutlined, CreditCardOutlined, DownloadOutlined, FileTextOutlined, MailOutlined, PrinterOutlined, RiseOutlined } from '@ant-design/icons';

const mockFinancialReports = {
  incomeStatement: {
    revenue: 1250000,
    costOfGoods: 750000,
    grossProfit: 500000,
    operatingExpenses: 300000,
    operatingIncome: 200000,
    otherIncome: 15000,
    otherExpenses: 5000,
    netIncome: 210000,
  },
  balanceSheet: {
    assets: {
      currentAssets: 450000,
      fixedAssets: 800000,
      totalAssets: 1250000,
    },
    liabilities: {
      currentLiabilities: 300000,
      longTermLiabilities: 400000,
      totalLiabilities: 700000,
    },
    equity: {
      capital: 400000,
      retainedEarnings: 150000,
      totalEquity: 550000,
    },
  },
  cashFlow: {
    operatingActivities: 180000,
    investingActivities: -50000,
    financingActivities: -30000,
    netCashFlow: 100000,
  },
};

const reportTypes = [
  'صورت سود و زیان',
  'ترازنامه',
  'صورت جریان نقدی',
  'گزارش بودجه',
  'گزارش دارایی‌ها',
  'گزارش مطالبات',
  'گزارش بدهی‌ها',
];

const exportFormats = [
  'PDF',
  'Excel',
  'Word',
  'CSV',
];

export const FinancialReports: React.FC = () => {
  const [selectedTab, setSelectedTab] = useState(0);
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedReport, setSelectedReport] = useState('');
  const [exportFormat, setExportFormat] = useState('PDF');
  const [dateRange, setDateRange] = useState({
    startDate: '',
    endDate: '',
  });

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setSelectedTab(newValue);
  };

  const handleGenerateReport = (reportType: string) => {
    setSelectedReport(reportType);
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedReport('');
    setDateRange({ startDate: '', endDate: '' });
  };

  const handleExportReport = () => {
    // در اینجا گزارش صادر می‌شود
    handleCloseDialog();
  };

  const renderIncomeStatement = () => (
    <div>
      <Typography.Title level={4}>
        صورت سود و زیان
      </Typography.Title>
      <TableContainer component={Paper}>
        <Table>
          <TableBody>
            <TableRow>
              <TableCell><strong>درآمد</strong></TableCell>
              <TableCell align="right">{mockFinancialReports.incomeStatement.revenue.toLocaleString()} تومان</TableCell>
            </TableRow>
            <TableRow>
              <TableCell>هزینه کالای فروش رفته</TableCell>
              <TableCell align="right">({mockFinancialReports.incomeStatement.costOfGoods.toLocaleString()}) تومان</TableCell>
            </TableRow>
            <TableRow style={{  backgroundColor: 'grey.100'  }}>
              <TableCell><strong>سود ناخالص</strong></TableCell>
              <TableCell align="right"><strong>{mockFinancialReports.incomeStatement.grossProfit.toLocaleString()} تومان</strong></TableCell>
            </TableRow>
            <TableRow>
              <TableCell>هزینه‌های عملیاتی</TableCell>
              <TableCell align="right">({mockFinancialReports.incomeStatement.operatingExpenses.toLocaleString()}) تومان</TableCell>
            </TableRow>
            <TableRow style={{  backgroundColor: 'grey.100'  }}>
              <TableCell><strong>سود عملیاتی</strong></TableCell>
              <TableCell align="right"><strong>{mockFinancialReports.incomeStatement.operatingIncome.toLocaleString()} تومان</strong></TableCell>
            </TableRow>
            <TableRow>
              <TableCell>سایر درآمدها</TableCell>
              <TableCell align="right">{mockFinancialReports.incomeStatement.otherIncome.toLocaleString()} تومان</TableCell>
            </TableRow>
            <TableRow>
              <TableCell>سایر هزینه‌ها</TableCell>
              <TableCell align="right">({mockFinancialReports.incomeStatement.otherExpenses.toLocaleString()}) تومان</TableCell>
            </TableRow>
            <TableRow style={{  backgroundColor: 'primary.light', color: 'white'  }}>
              <TableCell><strong>سود خالص</strong></TableCell>
              <TableCell align="right"><strong>{mockFinancialReports.incomeStatement.netIncome.toLocaleString()} تومان</strong></TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </div>
    </div>
  );

  const renderBalanceSheet = () => (
    <div>
      <Typography.Title level={4}>
        ترازنامه
      </Typography.Title>
      <Row gutter={[16, 16]}>
        <Col xs={Math.round(12 / 12 * 24)}>
          <Typography.Title level={5}>
            دارایی‌ها
          </Typography.Title>
          <TableContainer component={Paper}>
            <Table>
              <TableBody>
                <TableRow>
                  <TableCell>دارایی‌های جاری</TableCell>
                  <TableCell align="right">{mockFinancialReports.balanceSheet.assets.currentAssets.toLocaleString()} تومان</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>دارایی‌های ثابت</TableCell>
                  <TableCell align="right">{mockFinancialReports.balanceSheet.assets.fixedAssets.toLocaleString()} تومان</TableCell>
                </TableRow>
                <TableRow style={{  backgroundColor: 'primary.light', color: 'white'  }}>
                  <TableCell><strong>کل دارایی‌ها</strong></TableCell>
                  <TableCell align="right"><strong>{mockFinancialReports.balanceSheet.assets.totalAssets.toLocaleString()} تومان</strong></TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </div>
        </Col>
        <Col xs={Math.round(12 / 12 * 24)}>
          <Typography.Title level={5}>
            بدهی‌ها و سرمایه
          </Typography.Title>
          <TableContainer component={Paper}>
            <Table>
              <TableBody>
                <TableRow>
                  <TableCell>بدهی‌های جاری</TableCell>
                  <TableCell align="right">{mockFinancialReports.balanceSheet.liabilities.currentLiabilities.toLocaleString()} تومان</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>بدهی‌های بلندمدت</TableCell>
                  <TableCell align="right">{mockFinancialReports.balanceSheet.liabilities.longTermLiabilities.toLocaleString()} تومان</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>سرمایه</TableCell>
                  <TableCell align="right">{mockFinancialReports.balanceSheet.equity.capital.toLocaleString()} تومان</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>سود انباشته</TableCell>
                  <TableCell align="right">{mockFinancialReports.balanceSheet.equity.retainedEarnings.toLocaleString()} تومان</TableCell>
                </TableRow>
                <TableRow style={{  backgroundColor: 'primary.light', color: 'white'  }}>
                  <TableCell><strong>کل بدهی‌ها و سرمایه</strong></TableCell>
                  <TableCell align="right"><strong>{(mockFinancialReports.balanceSheet.liabilities.totalLiabilities + mockFinancialReports.balanceSheet.equity.totalEquity).toLocaleString()} تومان</strong></TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </div>
        </Col>
      </Row>
    </div>
  );

  const renderCashFlow = () => (
    <div>
      <Typography.Title level={4}>
        صورت جریان نقدی
      </Typography.Title>
      <TableContainer component={Paper}>
        <Table>
          <TableBody>
            <TableRow>
              <TableCell><strong>فعالیت‌های عملیاتی</strong></TableCell>
              <TableCell align="right">{mockFinancialReports.cashFlow.operatingActivities.toLocaleString()} تومان</TableCell>
            </TableRow>
            <TableRow>
              <TableCell>فعالیت‌های سرمایه‌گذاری</TableCell>
              <TableCell align="right">({Math.abs(mockFinancialReports.cashFlow.investingActivities).toLocaleString()}) تومان</TableCell>
            </TableRow>
            <TableRow>
              <TableCell>فعالیت‌های تأمین مالی</TableCell>
              <TableCell align="right">({Math.abs(mockFinancialReports.cashFlow.financingActivities).toLocaleString()}) تومان</TableCell>
            </TableRow>
            <TableRow style={{  backgroundColor: 'primary.light', color: 'white'  }}>
              <TableCell><strong>جریان نقدی خالص</strong></TableCell>
              <TableCell align="right"><strong>{mockFinancialReports.cashFlow.netCashFlow.toLocaleString()} تومان</strong></TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </div>
    </div>
  );

  return (
    <Card>
      <div>
        <div>
          <Typography.Title level={4}>
            <Assessment style={{  mr: 1  }} />
            گزارشات مالی
          </Typography.Title>
        </div>

        {/* کارت‌های گزارشات */}
        <Row gutter={[16, 16]}>
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center', cursor: 'pointer'  }} onClick={() => handleGenerateReport('صورت سود و زیان')}>
              <Receipt color="primary" style={{  fontSize: 40, mb: 1  }} />
              <Typography.Title level={4}>صورت سود و زیان</Typography.Title>
              <Typography.Text>
                گزارش درآمدها و هزینه‌ها
              </Typography.Text>
            </Card>
          </Col>
          
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center', cursor: 'pointer'  }} onClick={() => handleGenerateReport('ترازنامه')}>
              <AccountBalance color="primary" style={{  fontSize: 40, mb: 1  }} />
              <Typography.Title level={4}>ترازنامه</Typography.Title>
              <Typography.Text>
                گزارش دارایی‌ها و بدهی‌ها
              </Typography.Text>
            </Card>
          </Col>
          
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center', cursor: 'pointer'  }} onClick={() => handleGenerateReport('صورت جریان نقدی')}>
              <TrendingUp color="primary" style={{  fontSize: 40, mb: 1  }} />
              <Typography.Title level={4}>جریان نقدی</Typography.Title>
              <Typography.Text>
                گزارش جریان نقدی
              </Typography.Text>
            </Card>
          </Col>
          
          <Col xs={Math.round(12 / 12 * 24)}>
            <Card style={{  p: 2, textAlign: 'center', cursor: 'pointer'  }} onClick={() => handleGenerateReport('گزارش بودجه')}>
              <Payment color="primary" style={{  fontSize: 40, mb: 1  }} />
              <Typography.Title level={4}>گزارش بودجه</Typography.Title>
              <Typography.Text>
                گزارش بودجه‌بندی
              </Typography.Text>
            </Card>
          </Col>
        </Row>

        {/* تب‌های گزارشات */}
        <div style={{  borderBottom: 1, borderColor: 'divider', mb: 2  }}>
          <Tabs value={selectedTab} onChange={handleTabChange}>
            <Tab label="صورت سود و زیان" />
            <Tab label="ترازنامه" />
            <Tab label="جریان نقدی" />
          </Tabs>
        </div>

        {/* محتوای تب‌ها */}
        <div style={{  mt: 2  }}>
          {selectedTab === 0 && renderIncomeStatement()}
          {selectedTab === 1 && renderBalanceSheet()}
          {selectedTab === 2 && renderCashFlow()}
        </div>

        {/* Dialog برای صادر کردن گزارش */}
        <Modal open={false} onCancel={() => {}} footer={null}>
          <div>صادر کردن گزارش: {selectedReport}</div>
          <div>
            <Row gutter={[16, 16]}>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="تاریخ شروع"
                  type="date"
                  value={dateRange.startDate}
                  onChange={(e) => setDateRange({ ...dateRange, startDate: e.target.value })}
                  InputLabelProps={{ shrink: true }}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <Input
                  fullWidth
                  label="تاریخ پایان"
                  type="date"
                  value={dateRange.endDate}
                  onChange={(e) => setDateRange({ ...dateRange, endDate: e.target.value })}
                  InputLabelProps={{ shrink: true }}
                />
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <FormControl fullWidth>
                  <InputLabel>فرمت صادر کردن</span>
                  <Select
                    value={exportFormat}
                    label="فرمت صادر کردن"
                    onChange={(e) => setExportFormat(e.target.value)}
                  >
                    {exportFormats.map((format) => (
                      <MenuItem key={format} value={format}>
                        {format}
                      </Select.Option>
                    ))}
                  </Select>
                </div>
              </Col>
              <Col xs={Math.round(12 / 12 * 24)}>
                <div>
                  <Button
                    variant="contained"
                    startIcon={<Download />}
                    onClick={handleExportReport}
                  >
                    دانلود
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<Print />}
                    onClick={handleExportReport}
                  >
                    چاپ
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<Email />}
                    onClick={handleExportReport}
                  >
                    ارسال ایمیل
                  </Button>
                </div>
              </Col>
            </Row>
          </div>
          <div>
            <Button onClick={handleCloseDialog}>انصراف</Button>
          </div>
        </Modal>
      </div>
    </Card>
  );
}; 