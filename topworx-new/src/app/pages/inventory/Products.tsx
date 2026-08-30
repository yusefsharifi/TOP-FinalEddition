import React from 'react';
import { Card, Table, Tag, Typography } from 'antd';

const mockProducts = [
  {
    id: 1,
    name: 'Product A',
    sku: 'SKU-001',
    category: 'Electronics',
    price: 299.99,
    stock: 100,
    status: 'In Stock',
  },
  {
    id: 2,
    name: 'Product B',
    sku: 'SKU-002',
    category: 'Software',
    price: 499.99,
    stock: 0,
    status: 'Out of Stock',
  },
];

export const Products: React.FC = () => {
  const getStockStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'in stock':
        return 'success';
      case 'out of stock':
        return 'error';
      default:
        return 'default';
    }
  };

  return (
    <div>
      <Typography.Title level={2}>
        Products
      </Typography.Title>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>SKU</TableCell>
              <TableCell>Category</TableCell>
              <TableCell align="right">Price</TableCell>
              <TableCell align="right">Stock</TableCell>
              <TableCell>Status</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {mockProducts.map((product) => (
              <TableRow key={product.id}>
                <TableCell>{product.name}</TableCell>
                <TableCell>{product.sku}</TableCell>
                <TableCell>{product.category}</TableCell>
                <TableCell align="right">
                  ${product.price.toFixed(2)}
                </TableCell>
                <TableCell align="right">{product.stock}</TableCell>
                <TableCell>
                  <Tag
                    label={product.status}
                    color={getStockStatusColor(product.status)}
                    size="small"
                  />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}; 