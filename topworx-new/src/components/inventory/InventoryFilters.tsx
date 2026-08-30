import { Input, InputNumber } from 'antd';

const [search, setSearch] = useState("");
const [category, setCategory] = useState("");
const [warehouse, setWarehouse] = useState("");
const [status, setStatus] = useState("");

<div>
  <Input placeholder="جستجو" value={search} onChange={e => setSearch(e.target.value)} />
  <Input placeholder="دسته‌بندی" value={category} onChange={e => setCategory(e.target.value)} />
  <Input select label="انبار" value={warehouse} onChange={e => setWarehouse(e.target.value)}>
    <MenuItem value="">همه</Select.Option>
    {/* warehouses.map(w => <MenuItem key={w.id} value={w.id}>{w.name}</Select.Option>) */}
  </Input>
  <Input select label="وضعیت" value={status} onChange={e => setStatus(e.target.value)}>
    <MenuItem value="">همه</Select.Option>
    <MenuItem value="ok">عادی</Select.Option>
    <MenuItem value="low">کمبود</Select.Option>
    <MenuItem value="over">مازاد</Select.Option>
  </Input>
  <Input select label="وضعیت" value={filters.status || ""} onChange={e => onChange({ ...filters, status: e.target.value })}>
    <MenuItem value="">همه</Select.Option>
    <MenuItem value="ok">عادی</Select.Option>
    <MenuItem value="low">کمبود</Select.Option>
    <MenuItem value="over">مازاد</Select.Option>
    <MenuItem value="archived">آرشیو شده</Select.Option>
  </Input>
</div>