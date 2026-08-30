import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
const stats = [
  { name: "جمع پرداختی", value: payrolls.reduce((sum, p) => sum + p.net, 0) },
  { name: "مالیات", value: payrolls.reduce((sum, p) => sum + (p.items.find(i => i.type === "tax")?.amount || 0), 0) },
  { name: "بیمه", value: payrolls.reduce((sum, p) => sum + (p.items.find(i => i.type === "insurance")?.amount || 0), 0) },
];

<ResponsiveContainer width="100%" height={200}>
  <BarChart data={stats}>
    <XAxis dataKey="name" />
    <YAxis />
    <Tooltip />
    <Bar dataKey="value" fill="#1976d2" />
  </BarChart>
</ResponsiveContainer>