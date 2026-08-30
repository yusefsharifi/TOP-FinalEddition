import { Input, InputNumber } from 'antd';
const [search, setSearch] = useState("");
const [category, setCategory] = useState("");
const [status, setStatus] = useState("");

<div>
  <Input placeholder="جستجو" value={search} onChange={e => setSearch(e.target.value)} />
  <Input select label="دسته‌بندی" value={category} onChange={e => setCategory(e.target.value)}>
    <MenuItem value="">همه</Select.Option>
    <MenuItem value="fixed">اموال ثابت</Select.Option>
    <MenuItem value="equipment">تجهیزات</Select.Option>
    <MenuItem value="vehicle">وسایل نقلیه</Select.Option>
    <MenuItem value="it">فناوری اطلاعات</Select.Option>
    <MenuItem value="other">سایر</Select.Option>
  </Input>
  <Input select label="وضعیت" value={status} onChange={e => setStatus(e.target.value)}>
    <MenuItem value="">همه</Select.Option>
    <MenuItem value="active">فعال</Select.Option>
    <MenuItem value="inactive">غیرفعال</Select.Option>
    <MenuItem value="maintenance">در تعمیر</Select.Option>
    <MenuItem value="disposed">خارج شده</Select.Option>
  </Input>
  <Input select label="وضعیت" value={filters.status || ""} onChange={e => onChange({ ...filters, status: e.target.value })}>
    <MenuItem value="">همه</Select.Option>
    <MenuItem value="active">فعال</Select.Option>
    <MenuItem value="inactive">غیرفعال</Select.Option>
    <MenuItem value="maintenance">در تعمیر</Select.Option>
    <MenuItem value="disposed">خارج شده</Select.Option>
    <MenuItem value="archived">آرشیو شده</Select.Option>
  </Input>
</div>