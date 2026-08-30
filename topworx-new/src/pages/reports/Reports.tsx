import React, { useState } from "react";
import { Alert, Card } from 'antd';
import { useReports } from "../../api/reports";
import { ReportTable } from "../../components/reports/ReportTable";
import { ReportFilters } from "../../components/reports/ReportFilters";
import { ReportExportButtons } from "../../components/reports/ReportExportButtons";
import { useNotificationSnackbar } from "../../core/notifications/NotificationSnackbarProvider";
import { Tabs } from 'antd';

const [tab, setTab] = useState("all");
const filtered = data.filter(report => tab === "all" || report.type === tab);

<Tabs value={tab} onChange={(_, v) => setTab(v)}>
  <Tab label="همه" value="all" />
  <Tab label="مالی" value="finance" />
  <Tab label="منابع انسانی" value="hr" />
  <Tab label="فروش" value="sales" />
  <Tab label="پروژه" value="project" />
  <Tab label="سفارشی" value="custom" />
</Tabs>

const { showNotification } = useNotificationSnackbar();

const handleReportGenerated = () => {
  showNotification("گزارش جدید با موفقیت تولید شد", "success");
};

export const Reports: React.FC = () => {
  const [filters, setFilters] = useState({});
  const { data = [], isLoading, refetch } = useReports(filters);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: "success" | "error" }>({ open: false, message: "", severity: "success" });

  return (
    <Card style={{  p: 3  }}>
      <div>
        <ReportFilters filters={filters} onChange={setFilters} />
      </div>
      <ReportExportButtons data={data} />
      <ReportTable data={data} loading={isLoading} />
      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert severity={snackbar.severity}>{snackbar.message}</Alert>
      </div>
    </Card>
  );
};