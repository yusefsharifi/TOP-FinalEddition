import React from 'react';
import { Alert, Card, Spin, Table, Tag, Typography } from 'antd';
import { useProducts } from '../../api/inventory';
import { InventoryItem } from '../../api/inventory/types';

export const Products: React.FC = () => {
  const { data: items, isLoading, isError } = useProducts();

  const getStockStatusColor = (status: InventoryItem['status']) => {
    switch (status) {
      case 'ok':    return 'success';
      case 'low':   return 'warning';
      case 'over':  return 'info';
      default:      return 'default';
    }
  };

  const getStatusLabel = (status: InventoryItem['status']) => {
    switch (status) {
      case 'ok':   return 'موجود';
      case 'low':  return 'کم‌موجود';
      case 'over': return 'بیش از حد';
      default:     return status;
    }
  };

  if (isLoading) return <div><Spin /></div>;
  if (isError)   return <Alert severity="error">خطا در دریافت محصولات</Alert>;

  return (
    <div>
      <Typography.Title level={2}>محصولات</Typography.Title>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>نام محصول</TableCell>
              <TableCell>کد</TableCell>
              <TableCell>دسته‌بندی</TableCell>
              <TableCell>واحد</TableCell>
              <TableCell align="right">موجودی</TableCell>
              <TableCell align="right">حداقل موجودی</TableCell>
              <TableCell>وضعیت</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {items?.map((item) => (
              <TableRow key={item.id}>
                <TableCell>{item.product.name}</TableCell>
                <TableCell>{item.product.code}</TableCell>
                <TableCell>{item.product.category}</TableCell>
                <TableCell>{item.product.unit}</TableCell>
                <TableCell align="right">{item.quantity}</TableCell>
                <TableCell align="right">{item.product.minStock}</TableCell>
                <TableCell>
                  <Tag
                    label={getStatusLabel(item.status)}
                    color={getStockStatusColor(item.status)}
                    size="small"
                  />
                </TableCell>
              </TableRow>
            ))}
            {!items?.length && (
              <TableRow>
                <TableCell colSpan={7} align="center">محصولی یافت نشد</TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
};
