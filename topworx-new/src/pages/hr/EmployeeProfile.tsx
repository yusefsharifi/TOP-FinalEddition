import { Tabs } from 'antd';
const [tab, setTab] = useState(0);

<Tabs value={tab} onChange={(_, v) => setTab(v)}>
  <Tab label="اطلاعات پایه" />
  <Tab label="قراردادها" />
  <Tab label="حضور و غیاب" />
  <Tab label="مدارک" />
  <Tab label="پروژه‌ها" />
  <Tab label="وظایف" />
</Tabs>
<div>{/* اطلاعات پایه */}</div>
<div><EmployeeContracts ... /></div>
<div><EmployeeAttendance ... /></div>
<div><EmployeeDocuments ... /></div>
{/* ... */}

// فرض: useProjects و useTasks با فیلتر userId
const { data: projects = [] } = useProjects({ memberId: employee.id });
const { data: tasks = [] } = useTasks({ assignee: employee.id });

{/* نمایش لیست پروژه‌ها و وظایف */}