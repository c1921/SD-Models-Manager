// 模型接口定义
export interface Model {
  id: string;
  name: string;
  filename: string;
  type: string;
  size?: number;
  preview?: string;
  nsfw?: boolean;
  created_at?: string;
  hash?: string;
  tags?: string[];
  base_model?: string;
  url?: string;
}

// 筛选器选项接口
export interface FilterOption {
  label: string;
  value: string;
  count: number;
}

// 筛选器接口
export interface Filter {
  label: string;
  options: FilterOption[];
  selected: string[];
} 