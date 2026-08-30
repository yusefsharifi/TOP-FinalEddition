import { PieChart, Pie, Cell, Tooltip, BarChart, Bar, XAxis, YAxis, ResponsiveContainer } from "recharts";

const pieData = [
  { name: "بودجه", value: budget.amount, color: "#1976d2" },
  { name: "هزینه", value: budget.spent, color: "#e53935" },
  { name: "درآمد", value: budget.income, color: "#43a047" },
];

<PieChart width={300} height={200}>
  <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={60}>
    {pieData.map((entry, idx) => <Cell key={idx} fill={entry.color} />)}
  </Pie>
  <Tooltip />
</PieChart>