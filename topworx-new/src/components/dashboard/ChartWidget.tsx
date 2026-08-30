import React from "react";
import { Card, Typography } from 'antd';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from "recharts";

export const ChartWidget: React.FC<{ title: string; data: any[]; type: "line" | "bar" | "pie" }> = ({
  title, data, type
}) => {
  return (
    <Card style={{  p: 2  }}>
      <Typography.Title level={4}>{title}</Typography.Title>
      <ResponsiveContainer width="100%" height={250}>
        {type === "line" && (
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="value" stroke="#1976d2" />
          </LineChart>
        )}
        {type === "bar" && (
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="value" fill="#1976d2" />
          </BarChart>
        )}
        {type === "pie" && (
          <PieChart>
            <Pie data={data} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} fill="#1976d2" label>
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color || "#1976d2"} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        )}
      </ResponsiveContainer>
    </Card>
  );
};