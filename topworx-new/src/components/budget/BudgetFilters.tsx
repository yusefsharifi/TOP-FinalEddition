import { Input, InputNumber } from 'antd';
const [search, setSearch] = useState("");
const [type, setType] = useState("");
const [status, setStatus] = useState("");

<div>
  <Input placeholder="جستجو" value={search} onChange={e => setSearch(e.target.value)} />
  <Input select label="نوع بودجه" value={type} onChange={e => setType(e.target.value)}>
    <MenuItem value="">همه</Select.Option>
    <MenuItem value="annual">سالانه</Select.Option>
    <MenuItem value="monthly">ماهانه</Select.Option>
    <MenuItem value="project">پروژه‌ای</Select.Option>
  </Input>
  <Input select label="وضعیت" value={status} onChange={e => setStatus(e.target.value)}>
    <MenuItem value="">همه</Select.Option>
    <MenuItem value="active">فعال</Select.Option>
    <MenuItem value="closed">بسته‌شده</Select.Option>
    <MenuItem value="over">عبور از سقف</Select.Option>
  </Input>
</div>

<Input select label="وضعیت" value={filters.status || ""} onChange={e => onChange({ ...filters, status: e.target.value })}>
  <MenuItem value="">همه</Select.Option>
  <MenuItem value="active">فعال</Select.Option>
  <MenuItem value="closed">بسته‌شده</Select.Option>
  <MenuItem value="over">عبور از سقف</Select.Option>
  <MenuItem value="archived">آرشیو شده</Select.Option>
</Input>