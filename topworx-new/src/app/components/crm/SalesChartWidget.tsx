import React from "react";
import { Card, Typography } from 'antd';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell, Legend } from "recharts";

export type ChartType = "line" | "bar" | "pie";

export interface SalesChartWidgetProps {
  type: ChartType;
  data: any[];
  title: string;
  dataKey: string;
  valueKey: string;
  color?: string;
}

const COLORS = ["#1976d2", "#388e3c", "#fbc02d", "#d32f2f", "#7b1fa2", "#0288d1", "#c2185b"];

export const SalesChartWidget: React.FC<SalesChartWidgetProps> = ({ type, data, title, dataKey, valueKey, color }) => {
  return (
    <Card style={{ width: "100%" }}>
      <Typography.Title level={5}>{title}</Typography.Title>
      <ResponsiveContainer width="100%" height={250}>
        {type === "line" && (
          <LineChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey={dataKey} />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey={valueKey} stroke={color || COLORS[0]} strokeWidth={3} />
          </LineChart>
        )}
        {type === "bar" && (
          <BarChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey={dataKey} />
            <YAxis />
            <Tooltip />
            <Bar dataKey={valueKey} fill={color || COLORS[1]} />
          </BarChart>
        )}
        {type === "pie" && (
          <PieChart>
            <Pie data={data} dataKey={valueKey} nameKey={dataKey} cx="50%" cy="50%" outerRadius={80} label>
              {data.map((_, idx) => (
                <Cell key={idx} fill={COLORS[idx % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        )}
      </ResponsiveContainer>
    </Card>
  );
}; 