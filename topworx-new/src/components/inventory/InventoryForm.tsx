import { Checkbox, Select } from 'antd';
const [access, setAccess] = useState<"public" | "private" | "role">("private");
const [roles, setRoles] = useState<string[]>([]);

<FormControl>
  <InputLabel>دسترسی</span>
  <Select value={access} onChange={e => setAccess(e.target.value)} label="دسترسی">
    <MenuItem value="public">عمومی</Select.Option>
    <MenuItem value="private">خصوصی</Select.Option>
    <MenuItem value="role">نقش‌محور</Select.Option>
  </Select>
</div>
{access === "role" && (
  <FormControl>
    <InputLabel>نقش‌ها</span>
    <Select
      multiple
      value={roles}
      onChange={e => setRoles(e.target.value as string[])}
      renderValue={selected => (selected as string[]).join(", ")}
    >
      <MenuItem value="admin"><Checkbox checked={roles.includes("admin")} /> <ListItemText primary="مدیر" /></Select.Option>
      <MenuItem value="warehouse"><Checkbox checked={roles.includes("warehouse")} /> <ListItemText primary="انباردار" /></Select.Option>
      <MenuItem value="finance"><Checkbox checked={roles.includes("finance")} /> <ListItemText primary="مالی" /></Select.Option>
      {/* ... */}
    </Select>
  </div>
)}