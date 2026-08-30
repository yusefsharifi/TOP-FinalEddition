import React from "react";
import { Card, Typography } from "antd";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar, PieChart, Pie, Cell, Legend,
} from "recharts";

const { Text } = Typography;
export type ChartType = "line" | "bar" | "pie";

export interface ChartWidgetProps {
  title: string;
  data: any[];
  type: ChartType;
  dataKey?: string;
  categoryKey?: string;
  color?: string;
  loading?: boolean;
}

const COLORS = ["#1677ff", "#52c41a", "#faad14", "#ff4d4f", "#722ed1", "#13c2c2"];

export const ChartWidget: React.FC<ChartWidgetProps> = ({
  title, data, type, dataKey = "value", categoryKey = "name", color = "#1677ff",
}) => (
  <Card style={{ height: 320 }} title={<Text strong>{title}</Text>} bodyStyle={{ padding: "0 16px 16px" }}>
    <div style={{ width: "100%", height: 240 }}>
      <ResponsiveContainer width="100%" height="100%">
        {type === "line" && (
          <LineChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey={categoryKey} />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey={dataKey} stroke={color} strokeWidth={3} dot={{ r: 5 }} />
          </LineChart>
        )}
        {type === "bar" && (
          <BarChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey={categoryKey} />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey={dataKey} fill={color} radius={[8, 8, 0, 0]} />
          </BarChart>
        )}
        {type === "pie" && (
          <PieChart>
            <Tooltip />
            <Legend />
            <Pie data={data} dataKey={dataKey} nameKey={categoryKey} cx="50%" cy="50%" outerRadius={80} fill={color} label>
              {data.map((_, index) => <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />)}
            </Pie>
          </PieChart>
        )}
      </ResponsiveContainer>
    </div>
  </Card>
);
