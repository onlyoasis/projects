import React from 'react';
import { Bar } from '@ant-design/plots';

interface BarChartProps {
  data: Record<string, number>;
}

const BarChart: React.FC<BarChartProps> = ({ data }) => {
  const chartData = Object.entries(data).map(([key, value]) => ({
    type: key,
    value: value,
  }));

  const config = {
    data: chartData,
    xField: 'value',
    yField: 'type',
    seriesField: 'type',
    legend: {
      position: 'top' as const,
    },
  };

  return <Bar {...config} />;
};

export default BarChart; 