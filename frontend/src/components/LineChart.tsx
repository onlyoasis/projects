import React from 'react';
import { Line } from '@ant-design/plots';

interface LineChartProps {
  data: any[];
}

const LineChart: React.FC<LineChartProps> = ({ data }) => {
  const config = {
    data,
    xField: 'date',
    yField: 'avg_price',
    point: {
      size: 5,
      shape: 'diamond',
    },
    tooltip: {
      formatter: (datum: any) => {
        return { name: 'Average Price', value: `$${datum.avg_price.toFixed(2)}` };
      },
    },
  };

  return <Line {...config} />;
};

export default LineChart; 