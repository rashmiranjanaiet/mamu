export type ChartType = 'bar' | 'line' | 'area' | 'pie' | 'scatter';

export interface DataPoint {
  name: string;
  series: {
    name: string;
    value: number;
  }[];
}

export interface ChartConfig {
  type: ChartType;
  title: string;
  description?: string;
  xAxisLabel?: string;
  yAxisLabel?: string;
  data: DataPoint[];
}

export interface AIResponse {
  text: string;
  chart?: ChartConfig;
}

export interface Message {
  id: string;
  role: 'user' | 'model';
  content: string;
  chart?: ChartConfig;
  timestamp: number;
  isError?: boolean;
}
