import React, { useState } from "react";
import { Button, Col, Input, InputNumber, Row, Select } from 'antd';

export const InventoryTransfer: React.FC<{
  products: { id: string; name: string }[];
  warehouses: { id: string; name: string }[];
  onSubmit: (data: any) => void;
}> = ({ products, warehouses, onSubmit }) => {
  const [product, setProduct] = useState("");
  const [fromWarehouse, setFromWarehouse] = useState("");
  const [toWarehouse, setToWarehouse] = useState("");
  const [quantity, setQuantity] = useState(0);
  const [description, setDescription] = useState("");

  return (
    <div>
      <Row gutter={[16, 16]}>
        <Col xs={Math.round(3 / 12 * 24)}>
          <FormControl fullWidth>
            <InputLabel>کالا</span>
            <Select value={product} onChange={e => setProduct(e.target.value)} label="کالا">
              {products.map(p => <MenuItem key={p.id} value={p.id}>{p.name}</Select.Option>)}
            </Select>
          </div>
        </Col>
        <Col xs={Math.round(2 / 12 * 24)}>
          <FormControl fullWidth>
            <InputLabel>از انبار</span>
            <Select value={fromWarehouse} onChange={e => setFromWarehouse(e.target.value)} label="از انبار">
              {warehouses.map(w => <MenuItem key={w.id} value={w.id}>{w.name}</Select.Option>)}
            </Select>
          </div>
        </Col>
        <Col xs={Math.round(2 / 12 * 24)}>
          <FormControl fullWidth>
            <InputLabel>به انبار</span>
            <Select value={toWarehouse} onChange={e => setToWarehouse(e.target.value)} label="به انبار">
              {warehouses.map(w => <MenuItem key={w.id} value={w.id}>{w.name}</Select.Option>)}
            </Select>
          </div>
        </Col>
        <Col xs={Math.round(2 / 12 * 24)}>
          <Input label="مقدار" type="number" value={quantity} onChange={e => setQuantity(Number(e.target.value))} fullWidth />
        </Col>
        <Col xs={Math.round(3 / 12 * 24)}>
          <Input label="توضیحات" value={description} onChange={e => setDescription(e.target.value)} fullWidth />
        </Col>
        <Col xs={Math.round(12 / 12 * 24)}>
          <Button
            variant="contained"
            onClick={() => onSubmit({ product, fromWarehouse, toWarehouse, quantity, description })}
            disabled={!product || !fromWarehouse || !toWarehouse || !quantity}
          >
            ثبت انتقال
          </Button>
        </Col>
      </Row>
    </div>
  );
};