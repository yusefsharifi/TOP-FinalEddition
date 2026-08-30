import React, { useState, useMemo } from 'react';
import { Badge, Button, Card, Input, InputNumber, Pagination, Progress, Table, Tag, Tooltip, Typography } from 'antd';
import { EditOutlined } from '@ant-design/icons';
import { DeleteOutlined } from '@ant-design/icons';
import { EyeOutlined } from '@ant-design/icons';
import { CheckSquareOutlined } from '@ant-design/icons';
import { QualityInspection, QualityStatus, InspectionType } from '../../../types/quality';
import { useQualityInspections, useDeleteQualityInspection } from '../../../api/quality';

interface QualityInspectionsTableProps {
  filter?: any;
  onEdit: (inspection: QualityInspection) => void;
  onView: (inspection: QualityInspection) => void;
  onExport: (inspections: QualityInspection[]) => void;
  userRole: string;
}

export const QualityInspectionsTable: React.FC<QualityInspectionsTableProps> = ({ 
  filter, 
  onEdit, 
  onView, 
  onExport, 
  userRole 
}) => {
  const { data: inspections = [], isLoading } = useQualityInspections(filter);
  const deleteInspection = useDeleteQualityInspection();
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [search, setSearch] = useState('');

  const filtered = useMemo(() =>
    inspections.filter(i =>
      i.inspectionNumber.includes(search) ||
      i.productName?.includes(search) ||
      i.batchNumber?.includes(search) ||
      i.inspectorName.includes(search)
    ), [inspections, search]);

  const paged = useMemo(() =>
    filtered.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage),
    [filtered, page, rowsPerPage]);

  const handleDelete = (id?: number) => {
    if (!id) return;
    deleteInspection.mutate(id);
  };

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const getStatusColor = (status: QualityStatus) => {
    switch (status) {
      case 'passed':
        return 'success';
      case 'failed':
        return 'error';
      case 'conditional':
        return 'warning';
      case 'in_progress':
        return 'info';
      case 'pending':
        return 'default';
      case 'cancelled':
        return 'error';
      default:
        return 'default';
    }
  };

  const getStatusLabel = (status: QualityStatus) => {
    switch (status) {
      case 'pending':
        return 'در انتظار';
      case 'in_progress':
        return 'در حال انجام';
      case 'passed':
        return 'قبول';
      case 'failed':
        return 'رد';
      case 'conditional':
        return 'مشروط';
      case 'cancelled':
        return 'لغو شده';
      default:
        return status;
    }
  };

  const getInspectionTypeLabel = (type: InspectionType) => {
    switch (type) {
      case 'incoming':
        return 'ورودی';
      case 'in_process':
        return 'فرآیند';
      case 'final':
        return 'نهایی';
      case 'random':
        return 'تصادفی';
      case 'special':
        return 'ویژه';
      default:
        return type;
    }
  };

  const getInspectionTypeColor = (type: InspectionType) => {
    switch (type) {
      case 'incoming':
        return 'primary';
      case 'in_process':
        return 'info';
      case 'final':
        return 'success';
      case 'random':
        return 'warning';
      case 'special':
        return 'secondary';
      default:
        return 'default';
    }
  };

  const calculatePassRate = (inspection: QualityInspection) => {
    if (inspection.inspectedQuantity === 0) return 0;
    return Math.round((inspection.passedQuantity / inspection.inspectedQuantity) * 100);
  };

  if (isLoading) {
    return <LinearProgress />;
  }

  return (
    <div>
      <div style={{  mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center'  }}>
        <Input
          label="جستجو"
          variant="outlined"
          size="small"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{  width: 300  }}
        />
        <Typography.Text>
          تعداد کل: {filtered.length}
        </Typography.Text>
      </div>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>شماره بازرسی</TableCell>
              <TableCell>نوع بازرسی</TableCell>
              <TableCell>محصول/خدمت</TableCell>
              <TableCell>شماره دسته</TableCell>
              <TableCell>تعداد کل</TableCell>
              <TableCell>تعداد بازرسی شده</TableCell>
              <TableCell>نرخ قبولی</TableCell>
              <TableCell>وضعیت</TableCell>
              <TableCell>بازرس</TableCell>
              <TableCell>تاریخ بازرسی</TableCell>
              <TableCell align="right">عملیات</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {paged.length === 0 ? (
              <TableRow>
                <TableCell colSpan={11} align="center">
                  هیچ بازرسی‌ای یافت نشد.
                </TableCell>
              </TableRow>
            ) : (
              paged.map((inspection) => (
                <TableRow key={inspection.id} hover>
                  <TableCell>
                    <Typography.Text>
                      {inspection.inspectionNumber}
                    </Typography.Text>
                  </TableCell>
                  <TableCell>
                    <Tag 
                      label={getInspectionTypeLabel(inspection.type)} 
                      color={getInspectionTypeColor(inspection.type)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Typography.Text>
                      {inspection.productName || '-'}
                    </Typography.Text>
                  </TableCell>
                  <TableCell>
                    <Typography.Text>
                      {inspection.batchNumber || inspection.lotNumber || '-'}
                    </Typography.Text>
                  </TableCell>
                  <TableCell>
                    <Typography.Text>
                      {inspection.quantity.toLocaleString()}
                    </Typography.Text>
                  </TableCell>
                  <TableCell>
                    <Typography.Text>
                      {inspection.inspectedQuantity.toLocaleString()}
                    </Typography.Text>
                  </TableCell>
                  <TableCell>
                    <div>
                      <Typography.Text>
                        {calculatePassRate(inspection)}%
                      </Typography.Text>
                      <LinearProgress 
                        variant="determinate" 
                        value={calculatePassRate(inspection)}
                        style={{  width: 50, height: 6  }}
                        color={calculatePassRate(inspection) >= 95 ? 'success' : 
                               calculatePassRate(inspection) >= 80 ? 'warning' : 'error'}
                      />
                    </div>
                  </TableCell>
                  <TableCell>
                    <Tag 
                      label={getStatusLabel(inspection.status)} 
                      color={getStatusColor(inspection.status)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Typography.Text>
                      {inspection.inspectorName}
                    </Typography.Text>
                  </TableCell>
                  <TableCell>
                    <Typography.Text>
                      {new Date(inspection.inspectionDate).toLocaleDateString()}
                    </Typography.Text>
                  </TableCell>
                  <TableCell align="right">
                    <Tooltip title="مشاهده جزئیات">
                      <Button type="text" onClick={() => onView(inspection)} size="small">
                        <VisibilityIcon />
                      </Button>
                    </Tooltip>
                    <Tooltip title="ویرایش">
                      <Button type="text" onClick={() => onEdit(inspection)} size="small">
                        <EditIcon />
                      </Button>
                    </Tooltip>
                    {inspection.defects.length > 0 && (
                      <Tooltip title={`${inspection.defects.length} نقص`}>
                        <Badge badgeContent={inspection.defects.length} color="error">
                          <AssignmentIcon />
                        </Badge>
                      </Tooltip>
                    )}
                    {userRole === 'admin' && (
                      <Tooltip title="حذف">
                        <Button type="text" 
                          onClick={() => handleDelete(inspection.id)} 
                          size="small"
                          color="error"
                        >
                          <DeleteIcon />
                        </Button>
                      </Tooltip>
                    )}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      <TablePagination
        rowsPerPageOptions={[5, 10, 25]}
        component="div"
        count={filtered.length}
        rowsPerPage={rowsPerPage}
        page={page}
        onPageChange={handleChangePage}
        onRowsPerPageChange={handleChangeRowsPerPage}
        labelRowsPerPage="تعداد در صفحه:"
        labelDisplayedRows={({ from, to, count }) => `${from}-${to} از ${count}`}
      />
    </div>
  );
}; 