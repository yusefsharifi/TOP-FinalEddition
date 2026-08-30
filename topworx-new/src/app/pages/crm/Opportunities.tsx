import React, { useState, useMemo } from "react";
import { Alert, Button, Card, Col, Drawer, Input, InputNumber, Modal, Pagination, Row, Table, Tabs, Tag, Tooltip, Typography } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { EditOutlined } from '@ant-design/icons';
import { DeleteOutlined } from '@ant-design/icons';
import { EyeOutlined } from '@ant-design/icons';
import { AppstoreOutlined } from '@ant-design/icons';
import { UnorderedListOutlined } from '@ant-design/icons';
import { useForm } from "react-hook-form";
import { DragDropContext, Droppable, Draggable, DropResult } from "@hello-pangea/dnd";

// تعریف نوع فرصت
export interface Opportunity {
  id?: number;
  name: string;
  customer: string;
  value: number;
  stage: "ایده اولیه" | "پیشنهاد" | "مذاکره" | "قرارداد" | "بسته شده";
  probability: number;
}

const mockOpportunities: Opportunity[] = [
  { id: 1, name: "پیاده‌سازی نرم‌افزار جدید", customer: "شرکت الف", value: 50000, stage: "پیشنهاد", probability: 60 },
  { id: 2, name: "ارتقاء سخت‌افزار", customer: "شرکت ب", value: 25000, stage: "مذاکره", probability: 80 },
  { id: 3, name: "قرارداد پشتیبانی", customer: "شرکت ج", value: 15000, stage: "قرارداد", probability: 90 },
  { id: 4, name: "فروش تجهیزات", customer: "شرکت د", value: 30000, stage: "ایده اولیه", probability: 30 },
];

const USER_ROLE = "admin"; // برای تست RBAC

const stageColors: Record<string, "primary" | "secondary" | "success" | "warning" | "error" | "default"> = {
  "ایده اولیه": "default",
  "پیشنهاد": "primary",
  "مذاکره": "warning",
  "قرارداد": "success",
  "بسته شده": "secondary",
};

// فرم افزودن/ویرایش فرصت
const OpportunityForm: React.FC<{
  open: boolean;
  onClose: () => void;
  opportunity?: Opportunity | null;
  onSave: (data: Opportunity) => void;
}> = ({ open, onClose, opportunity, onSave }) => {
  const { register, handleSubmit, reset, formState: { errors } } = useForm<Opportunity>({
    defaultValues: opportunity || { name: "", customer: "", value: 0, stage: "ایده اولیه", probability: 0 },
  });
  React.useEffect(() => {
    reset(opportunity || { name: "", customer: "", value: 0, stage: "ایده اولیه", probability: 0 });
  }, [opportunity, reset]);
  const onSubmit = (data: Opportunity) => {
    onSave(data);
    onClose();
  };
  return (
    <Modal open={false} onCancel={() => {}} footer={null}>
      <div>{opportunity ? "ویرایش فرصت" : "افزودن فرصت جدید"}</div>
      <form onSubmit={handleSubmit(onSubmit)}>
        <div>
          <Row gutter={[16, 16]}>
            <Col xs={Math.round(12 / 12 * 24)}>
              <Input
                label="عنوان فرصت"
                fullWidth
                {...register("name", { required: "عنوان الزامی است" })}
                error={!!errors.name}
                helperText={errors.name?.message}
              />
            </Col>
            <Col xs={Math.round(12 / 12 * 24)}>
              <Input
                label="مشتری"
                fullWidth
                {...register("customer", { required: "مشتری الزامی است" })}
                error={!!errors.customer}
                helperText={errors.customer?.message}
              />
            </Col>
            <Col xs={Math.round(12 / 12 * 24)}>
              <Input
                label="ارزش (تومان)"
                type="number"
                fullWidth
                {...register("value", { required: "ارزش الزامی است", min: { value: 0, message: "ارزش باید مثبت باشد" } })}
                error={!!errors.value}
                helperText={errors.value?.message}
              />
            </Col>
            <Col xs={Math.round(12 / 12 * 24)}>
              <Input
                select
                label="مرحله"
                fullWidth
                {...register("stage", { required: true })}
                defaultValue={opportunity?.stage || "ایده اولیه"}
              >
                {Object.keys(stageColors).map((stage) => (
                  <MenuItem key={stage} value={stage}>{stage}</Select.Option>
                ))}
              </Input>
            </Col>
            <Col xs={Math.round(12 / 12 * 24)}>
              <Input
                label="احتمال موفقیت (%)"
                type="number"
                fullWidth
                {...register("probability", { required: "احتمال الزامی است", min: { value: 0, message: "حداقل 0" }, max: { value: 100, message: "حداکثر 100" } })}
                error={!!errors.probability}
                helperText={errors.probability?.message}
              />
            </Col>
          </Row>
        </div>
        <div>
          <Button onClick={onClose}>انصراف</Button>
          <Button type="submit" variant="contained">{opportunity ? "ذخیره" : "افزودن"}</Button>
        </div>
      </form>
    </Modal>
  );
};

// نمایش جزئیات فرصت
const OpportunityDetails: React.FC<{
  open: boolean;
  onClose: () => void;
  opportunity: Opportunity | null;
}> = ({ open, onClose, opportunity }) => {
  if (!opportunity) return null;
  return (
    <Drawer anchor="right" open={open} onClose={onClose}>
      <div style={{  width: 350, p: 3  }}>
        <div style={{  display: "flex", justifyContent: "space-between", alignItems: "center"  }}>
          <Typography.Title level={4}>جزئیات فرصت</Typography.Title>
          <Button type="text" onClick={onClose}><DeleteIcon /></Button>
        </div>
        <Typography variant="subtitle2">عنوان:</Typography>
        <Typography style={{  mb: 1  }}>{opportunity.name}</Typography>
        <Typography variant="subtitle2">مشتری:</Typography>
        <Typography style={{  mb: 1  }}>{opportunity.customer}</Typography>
        <Typography variant="subtitle2">ارزش:</Typography>
        <Typography style={{  mb: 1  }}>{opportunity.value.toLocaleString()} تومان</Typography>
        <Typography variant="subtitle2">مرحله:</Typography>
        <Typography style={{  mb: 1  }}>{opportunity.stage}</Typography>
        <Typography variant="subtitle2">احتمال موفقیت:</Typography>
        <Typography style={{  mb: 1  }}>{opportunity.probability}٪</Typography>
      </div>
    </Drawer>
  );
};

// Kanban Board حرفه‌ای با Drag & Drop
const OpportunityKanban: React.FC<{
  opportunities: Opportunity[];
  onEdit: (op: Opportunity) => void;
  onDetails: (op: Opportunity) => void;
  onStageChange: (id: number, newStage: string) => void;
}> = ({ opportunities, onEdit, onDetails, onStageChange }) => {
  const stages = Object.keys(stageColors);
  // گروه‌بندی فرصت‌ها بر اساس مرحله
  const columns = stages.map(stage => ({
    stage,
    items: opportunities.filter(o => o.stage === stage),
  }));

  return (
    <DragDropContext
      onDragEnd={(result: DropResult) => {
        if (!result.destination) return;
        const sourceStage = result.source.droppableId;
        const destStage = result.destination.droppableId;
        if (sourceStage !== destStage) {
          const id = Number(result.draggableId);
          onStageChange(id, destStage);
        }
      }}
    >
      <div>
        {columns.map((col) => (
          <Droppable droppableId={col.stage} key={col.stage}>
            {(provided, snapshot) => (
              <Card
                ref={provided.innerRef}
                {...provided.droppableProps}
                style={{  minWidth: 250, p: 2, flex: 1, bgcolor: snapshot.isDraggingOver ? "grey.200" : undefined  }}
              >
                <Typography.Title level={5}>{col.stage}</Typography.Title>
                {col.items.map((op, idx) => (
                  <Draggable draggableId={String(op.id)} index={idx} key={op.id}>
                    {(provided, snapshot) => (
                      <Card
                        ref={provided.innerRef}
                        {...provided.draggableProps}
                        {...provided.dragHandleProps}
                        style={{  my: 1, p: 1, bgcolor: snapshot.isDragging ? "primary.light" : "grey.100"  }}
                      >
                        <Typography fontWeight="bold">{op.name}</Typography>
                        <Typography.Text>{op.customer}</Typography.Text>
                        <div>
                          <Tag label={`${op.probability}%`} size="small" color="primary" />
                          <div>
                            <Tooltip title="جزئیات"><Button type="text" size="small" onClick={() => onDetails(op)}><VisibilityIcon fontSize="small" /></Button></Tooltip>
                            <Tooltip title="ویرایش"><Button type="text" size="small" onClick={() => onEdit(op)}><EditIcon fontSize="small" /></Button></Tooltip>
                          </div>
                        </div>
                      </Card>
                    )}
                  </Draggable>
                ))}
                {provided.placeholder}
              </Card>
            )}
          </Droppable>
        ))}
      </div>
    </DragDropContext>
  );
};

export const Opportunities: React.FC = () => {
  const [opportunities, setOpportunities] = useState<Opportunity[]>(mockOpportunities);
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);
  const [formOpen, setFormOpen] = useState(false);
  const [editOpportunity, setEditOpportunity] = useState<Opportunity | null>(null);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [selectedOpportunity, setSelectedOpportunity] = useState<Opportunity | null>(null);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: "success" | "error" }>({ open: false, message: "", severity: "success" });
  const [viewMode, setViewMode] = useState<"table" | "kanban">("table");
  const theme = useTheme();

  const filtered = useMemo(() =>
    opportunities.filter(o =>
      o.name.toLowerCase().includes(search.toLowerCase()) ||
      o.customer.toLowerCase().includes(search.toLowerCase())
    ), [opportunities, search]);

  const paged = useMemo(() =>
    filtered.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage),
    [filtered, page, rowsPerPage]);

  const handleAdd = () => {
    setEditOpportunity(null);
    setFormOpen(true);
  };
  const handleEdit = (op: Opportunity) => {
    setEditOpportunity(op);
    setFormOpen(true);
  };
  const handleDelete = (id?: number) => {
    setOpportunities(prev => prev.filter(o => o.id !== id));
    setSnackbar({ open: true, message: "فرصت حذف شد.", severity: "success" });
  };
  const handleSave = (data: Opportunity) => {
    if (editOpportunity) {
      setOpportunities(prev => prev.map(o => o.id === editOpportunity.id ? { ...data, id: editOpportunity.id } : o));
      setSnackbar({ open: true, message: "فرصت ویرایش شد.", severity: "success" });
    } else {
      setOpportunities(prev => [...prev, { ...data, id: Math.max(0, ...prev.map(o => o.id || 0)) + 1 }]);
      setSnackbar({ open: true, message: "فرصت جدید افزوده شد.", severity: "success" });
    }
  };
  const handleDetails = (op: Opportunity) => {
    setSelectedOpportunity(op);
    setDetailsOpen(true);
  };
  const handleStageChange = (id: number, newStage: string) => {
    setOpportunities(prev => prev.map(o => o.id === id ? { ...o, stage: newStage as Opportunity["stage"] } : o));
    setSnackbar({ open: true, message: "مرحله فرصت تغییر کرد.", severity: "success" });
  };
  return (
    <div>
      <Typography.Title level={2}>فرصت‌های فروش</Typography.Title>
      <Toolbar style={{  justifyContent: "space-between", flexDirection: "row-reverse"  }}>
        <div>
          <Button variant="contained" startIcon={<AddIcon />} onClick={handleAdd}>افزودن فرصت</Button>
          <Button
            variant={viewMode === "table" ? "contained" : "outlined"}
            startIcon={<TableRowsIcon />}
            onClick={() => setViewMode("table")}
          >جدولی</Button>
          <Button
            variant={viewMode === "kanban" ? "contained" : "outlined"}
            startIcon={<ViewKanbanIcon />}
            onClick={() => setViewMode("kanban")}
          >کانبان</Button>
        </div>
        <Input
          label="جستجو"
          value={search}
          onChange={e => setSearch(e.target.value)}
          size="small"
          style={{  width: 200  }}
        />
      </Toolbar>
      {viewMode === "table" ? (
        <TableContainer component={Paper} style={{  mt: 2  }}>
        <Table>
          <TableHead>
            <TableRow>
                <TableCell align="right">عنوان</TableCell>
                <TableCell align="right">مشتری</TableCell>
                <TableCell align="right">ارزش (تومان)</TableCell>
                <TableCell align="right">مرحله</TableCell>
                <TableCell align="right">احتمال موفقیت (%)</TableCell>
                <TableCell align="right">عملیات</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
              {paged.map((op) => (
                <TableRow key={op.id}>
                  <TableCell align="right">{op.name}</TableCell>
                  <TableCell align="right">{op.customer}</TableCell>
                  <TableCell align="right">{op.value.toLocaleString()}</TableCell>
                <TableCell align="right">
                    <Tag label={op.stage} color={stageColors[op.stage]} size="small" />
                </TableCell>
                  <TableCell align="right">{op.probability}</TableCell>
                  <TableCell align="right">
                    <Tooltip title="جزئیات"><Button type="text" onClick={() => handleDetails(op)}><VisibilityIcon /></Button></Tooltip>
                    <Tooltip title="ویرایش"><Button type="text" onClick={() => handleEdit(op)}><EditIcon /></Button></Tooltip>
                    <Tooltip title="حذف"><Button type="text" onClick={() => handleDelete(op.id)}><DeleteIcon /></Button></Tooltip>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
          <TablePagination
            component="div"
            count={filtered.length}
            page={page}
            onPageChange={(_, newPage) => setPage(newPage)}
            rowsPerPage={rowsPerPage}
            onRowsPerPageChange={e => { setRowsPerPage(parseInt(e.target.value, 10)); setPage(0); }}
            labelRowsPerPage="تعداد در صفحه"
            rowsPerPageOptions={[5, 10, 20]}
            style={{  direction: "ltr"  }}
          />
      </div>
      ) : (
        <OpportunityKanban
          opportunities={filtered}
          onEdit={handleEdit}
          onDetails={handleDetails}
          onStageChange={handleStageChange}
        />
      )}
      <OpportunityForm
        open={formOpen}
        onClose={() => setFormOpen(false)}
        opportunity={editOpportunity}
        onSave={handleSave}
      />
      <OpportunityDetails
        open={detailsOpen}
        onClose={() => setDetailsOpen(false)}
        opportunity={selectedOpportunity}
      />
      <Snackbar
        open={snackbar.open}
        autoHideDuration={3000}
        onClose={() => setSnackbar(s => ({ ...s, open: false }))}
        anchorOrigin={{ vertical: "top", horizontal: "center" }}
      >
        <Alert severity={snackbar.severity}>{snackbar.message}</Alert>
      </div>
    </div>
  );
}; 