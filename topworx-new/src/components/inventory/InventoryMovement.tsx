import React, { useState } from "react";
import { Button, Col, Input, InputNumber, Row, Select } from 'antd';

export const InventoryMovement: React.FC<{
  products: { id: string; name: string }[];
  warehouses: { id: string; name: string }[];
  onSubmit: (data: any) => void;
}> = ({ products, warehouses, onSubmit }) => {
  const [type, setType] = useState<"in" | "out">("in");
  const [product, setProduct] = useState("");
  const [warehouse, setWarehouse] = useState("");
  const [quantity, setQuantity] = useState(0);
  const [description, setDescription] = useState("");

  return (
    <div>
      <Row gutter={[16, 16]}>
        <Col xs={Math.round(2 / 12 * 24)}>
          <FormControl fullWidth>
            <InputLabel>نوع</span>
            <Select value={type} onChange={e => setType(e.target.value as any)} label="نوع">
              <MenuItem value="in">ورود</Select.Option>
              <MenuItem value="out">خروج</Select.Option>
            </Select>
          </div>
        </Col>
        <Col xs={Math.round(3 / 12 * 24)}>
          <FormControl fullWidth>
            <InputLabel>کالا</span>
            <Select value={product} onChange={e => setProduct(e.target.value)} label="کالا">
              {products.map(p => <MenuItem key={p.id} value={p.id}>{p.name}</Select.Option>)}
            </Select>
          </div>
        </Col>
        <Col xs={Math.round(3 / 12 * 24)}>
          <FormControl fullWidth>
            <InputLabel>انبار</span>
            <Select value={warehouse} onChange={e => setWarehouse(e.target.value)} label="انبار">
              {warehouses.map(w => <MenuItem key={w.id} value={w.id}>{w.name}</Select.Option>)}
            </Select>
          </div>
        </Col>
        <Col xs={Math.round(2 / 12 * 24)}>
          <Input label="مقدار" type="number" value={quantity} onChange={e => setQuantity(Number(e.target.value))} fullWidth />
        </Col>
        <Col xs={Math.round(2 / 12 * 24)}>
          <Input label="توضیحات" value={description} onChange={e => setDescription(e.target.value)} fullWidth />
        </Col>
        <Col xs={Math.round(12 / 12 * 24)}>
          <Button
            variant="contained"
            onClick={() => onSubmit({ type, product, warehouse, quantity, description })}
            disabled={!product || !warehouse || !quantity}
          >
            ثبت
          </Button>
        </Col>
      </Row>
    </div>
  );
};