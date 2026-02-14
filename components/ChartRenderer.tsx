import React, { useMemo } from 'react';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  AreaChart,
  Area,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ScatterChart,
  Scatter,
} from 'recharts';
import { ChartConfig } from '../types';

interface ChartRendererProps {
  config: ChartConfig;
}

// Modern, accessible color palette
const COLORS = [
  '#3b82f6', // blue-500
  '#8b5cf6', // violet-500
  '#10b981', // emerald-500
  '#f59e0b', // amber-500
  '#ef4444', // red-500
  '#ec4899', // pink-500
  '#6366f1', // indigo-500
  '#14b8a6', // teal-500
];

export const ChartRenderer: React.FC<ChartRendererProps> = ({ config }) => {
  const { type, data, title, xAxisLabel, yAxisLabel } = config;

  // Transform nested series data into flat objects for Recharts
  // Input: { name: 'Jan', series: [{ name: 'Sales', value: 100 }, { name: 'Profit', value: 50 }] }
  // Output: { name: 'Jan', Sales: 100, Profit: 50 }
  const transformedData = useMemo(() => {
    return data.map((point) => {
      const flatPoint: any = { name: point.name };
      point.series.forEach((s) => {
        flatPoint[s.name] = s.value;
      });
      return flatPoint;
    });
  }, [data]);

  // Extract all unique series names to create lines/bars
  const seriesNames = useMemo(() => {
    const names = new Set<string>();
    data.forEach((point) => {
      point.series.forEach((s) => names.add(s.name));
    });
    return Array.from(names);
  }, [data]);

  const commonProps = {
    data: transformedData,
    margin: { top: 20, right: 30, left: 20, bottom: 20 },
  };

  const renderChart = () => {
    switch (type) {
      case 'line':
        return (
          <LineChart {...commonProps}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="name" stroke="#94a3b8" tick={{ fill: '#94a3b8' }} label={{ value: xAxisLabel, position: 'insideBottom', offset: -10, fill: '#94a3b8' }} />
            <YAxis stroke="#94a3b8" tick={{ fill: '#94a3b8' }} label={{ value: yAxisLabel, angle: -90, position: 'insideLeft', fill: '#94a3b8' }} />
            <Tooltip
              contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#f8fafc' }}
              itemStyle={{ color: '#f8fafc' }}
            />
            <Legend wrapperStyle={{ paddingTop: '20px' }} />
            {seriesNames.map((key, index) => (
              <Line
                key={key}
                type="monotone"
                dataKey={key}
                stroke={COLORS[index % COLORS.length]}
                strokeWidth={3}
                dot={{ r: 4, fill: '#1e293b', strokeWidth: 2 }}
                activeDot={{ r: 6 }}
              />
            ))}
          </LineChart>
        );
      case 'area':
        return (
          <AreaChart {...commonProps}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="name" stroke="#94a3b8" tick={{ fill: '#94a3b8' }} />
            <YAxis stroke="#94a3b8" tick={{ fill: '#94a3b8' }} />
            <Tooltip
              contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#f8fafc' }}
            />
            <Legend wrapperStyle={{ paddingTop: '20px' }} />
            {seriesNames.map((key, index) => (
              <Area
                key={key}
                type="monotone"
                dataKey={key}
                stackId="1"
                stroke={COLORS[index % COLORS.length]}
                fill={COLORS[index % COLORS.length]}
                fillOpacity={0.6}
              />
            ))}
          </AreaChart>
        );
      case 'bar':
        return (
          <BarChart {...commonProps}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="name" stroke="#94a3b8" tick={{ fill: '#94a3b8' }} />
            <YAxis stroke="#94a3b8" tick={{ fill: '#94a3b8' }} />
            <Tooltip
              contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#f8fafc' }}
              cursor={{ fill: 'rgba(255,255,255,0.05)' }}
            />
            <Legend wrapperStyle={{ paddingTop: '20px' }} />
            {seriesNames.map((key, index) => (
              <Bar
                key={key}
                dataKey={key}
                fill={COLORS[index % COLORS.length]}
                radius={[4, 4, 0, 0]}
              />
            ))}
          </BarChart>
        );
      case 'pie':
        // Pie charts typically visualize one series at a time or aggregate data.
        // For simplicity, we take the first series of each data point.
        const pieData = transformedData.map((d) => ({
          name: d.name,
          value: d[seriesNames[0]] || 0,
        }));

        return (
          <PieChart>
            <Pie
              data={pieData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              outerRadius={100}
              fill="#8884d8"
              dataKey="value"
            >
              {pieData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#f8fafc' }}
            />
            <Legend />
          </PieChart>
        );
        case 'scatter':
          // Recharts Scatter requires explicit x/y numeric values or specific structure.
          // Our schema puts 'name' as string. We can try to use it if it's parseable, or just index.
          return (
            <ScatterChart {...commonProps}>
               <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
               <XAxis dataKey="name" type="category" stroke="#94a3b8" name={xAxisLabel} />
               <YAxis type="number" stroke="#94a3b8" name={yAxisLabel} />
               <Tooltip cursor={{ strokeDasharray: '3 3' }} contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#f8fafc' }} />
               <Legend />
               {seriesNames.map((key, index) => (
                 <Scatter key={key} name={key} data={transformedData.map(d => ({ name: d.name, [key]: d[key] }))} fill={COLORS[index % COLORS.length]} />
               ))}
            </ScatterChart>
          )
      default:
        return <div className="text-red-400">Unsupported chart type: {type}</div>;
    }
  };

  return (
    <div className="w-full bg-surface rounded-xl p-4 md:p-6 shadow-xl border border-gray-700/50 mt-4 animate-fade-in">
      <h3 className="text-xl font-semibold mb-2 text-white">{title}</h3>
      {config.description && <p className="text-gray-400 mb-6 text-sm">{config.description}</p>}
      <div className="h-[300px] md:h-[400px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          {renderChart()}
        </ResponsiveContainer>
      </div>
    </div>
  );
};
