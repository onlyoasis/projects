import React, { useState, useEffect } from 'react';
import { 
  Table, 
  Card, 
  Row, 
  Col, 
  Select, 
  Input, 
  Space,
  Typography,
  Statistic,
  message,
  Dropdown,
  Button,
  Menu
} from 'antd';
import { ReloadOutlined, DownOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';

const { Title } = Typography;
const { Search } = Input;

interface DiskPrice {
  product_name: string;
  capacity: string;
  price: string;
  price_per_tb: string;
  interface: string;
  form_factor: string;
  seller: string;
  rating?: string;
  product_url?: string;
  seller_url?: string;
  date_scraped: string;
}

interface DataFile {
  name: string;
  size: number;
  date: string;
  path: string;
}

const App: React.FC = () => {
  const [data, setData] = useState<DiskPrice[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchText, setSearchText] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [dataFiles, setDataFiles] = useState<DataFile[]>([]);
  const [currentFile, setCurrentFile] = useState<string>('最新数据');

  useEffect(() => {
    fetchData();
    fetchDataFiles();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/latest');
      if (!response.ok) {
        throw new Error('未能获取数据');
      }
      const json = await response.json();
      setData(json);
      message.success('数据加载成功');
    } catch (error) {
      console.error('Error fetching data:', error);
      message.error('数据加载失败');
      // 使用模拟数据作为后备
      import('./mockData').then(module => {
        setData(module.mockDiskData);
        message.warning('加载了模拟数据');
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchDataFiles = async () => {
    try {
      const response = await fetch('/api/files');
      if (!response.ok) {
        throw new Error('未能获取文件列表');
      }
      const json = await response.json();
      setDataFiles(json);
    } catch (error) {
      console.error('Error fetching file list:', error);
    }
  };

  const loadFileData = async (filename: string) => {
    setLoading(true);
    try {
      const response = await fetch(`/api/file/${filename}`);
      if (!response.ok) {
        throw new Error(`未能加载文件 ${filename}`);
      }
      const json = await response.json();
      setData(json);
      setCurrentFile(filename);
      message.success(`成功加载文件: ${filename}`);
    } catch (error) {
      console.error('Error loading file:', error);
      message.error(`加载文件失败: ${filename}`);
    } finally {
      setLoading(false);
    }
  };

  const columns: ColumnsType<DiskPrice> = [
    {
      title: '产品名称',
      dataIndex: 'product_name',
      render: (text, record) => (
        <a href={record.product_url} target="_blank" rel="noopener noreferrer">
          {text}
        </a>
      ),
      sorter: (a, b) => a.product_name.localeCompare(b.product_name),
    },
    {
      title: '容量',
      dataIndex: 'capacity',
      sorter: (a, b) => {
        // 处理容量值以便排序
        const getValue = (str: string) => {
          const num = parseFloat(str.replace(/[^0-9.]/g, ''));
          if (str.includes('TB')) return num * 1000;
          return num;
        };
        return getValue(a.capacity) - getValue(b.capacity);
      },
    },
    {
      title: '价格',
      dataIndex: 'price',
      sorter: (a, b) => {
        const aNum = parseFloat(a.price.replace(/[^0-9.]/g, ''));
        const bNum = parseFloat(b.price.replace(/[^0-9.]/g, ''));
        return aNum - bNum;
      },
    },
    {
      title: '每TB价格',
      dataIndex: 'price_per_tb',
      sorter: (a, b) => {
        const aNum = parseFloat(a.price_per_tb.replace(/[^0-9.]/g, ''));
        const bNum = parseFloat(b.price_per_tb.replace(/[^0-9.]/g, ''));
        return aNum - bNum;
      },
    },
    {
      title: '接口',
      dataIndex: 'interface',
      filters: [
        { text: 'SATA', value: 'SATA' },
        { text: 'NVMe', value: 'NVMe' },
        { text: 'USB', value: 'USB' },
      ],
      onFilter: (value, record) => record.interface.includes(value as string),
    },
    {
      title: '硬盘形态',
      dataIndex: 'form_factor',
    },
    {
      title: '卖家',
      dataIndex: 'seller',
      render: (text, record) => (
        <a href={record.seller_url} target="_blank" rel="noopener noreferrer">
          {text}
        </a>
      ),
    },
    {
      title: '评分',
      dataIndex: 'rating',
    },
  ];

  const filteredData = data.filter(item => {
    const matchesSearch = item.product_name?.toLowerCase().includes(searchText.toLowerCase());
    const matchesType = filterType === 'all' || (item.interface && item.interface.includes(filterType));
    return matchesSearch && matchesType;
  });

  // 创建文件选择菜单
  const fileMenu = (
    <Menu
      onClick={({ key }) => loadFileData(key)}
      items={dataFiles.map(file => ({
        key: file.name,
        label: `${file.name} (${new Date(file.date).toLocaleDateString()})`
      }))}
    />
  );

  // 计算价格统计数据
  const getPriceStats = () => {
    if (!data.length) return { min: 0, max: 0, avg: 0 };
    
    const prices = data.map(item => parseFloat(item.price.replace(/[^0-9.]/g, '')))
                       .filter(num => !isNaN(num));
    
    return {
      min: Math.min(...prices),
      max: Math.max(...prices),
      avg: prices.reduce((sum, price) => sum + price, 0) / prices.length
    };
  };

  const priceStats = getPriceStats();

  return (
    <div style={{ padding: '24px' }}>
      <Title level={2}>硬盘价格监控</Title>
      
      <Row gutter={[16, 16]}>
        <Col span={6}>
          <Card>
            <Statistic title="总产品数" value={data.length} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="数据更新时间" value={data[0]?.date_scraped || '-'} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="平均价格" 
              value={priceStats.avg.toFixed(2)} 
              prefix="$" 
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="价格范围" 
              value={`$${priceStats.min.toFixed(2)} - $${priceStats.max.toFixed(2)}`} 
            />
          </Card>
        </Col>
      </Row>

      <Card style={{ marginTop: '24px' }}>
        <Space style={{ marginBottom: '16px' }}>
          <Search
            placeholder="搜索产品"
            onChange={e => setSearchText(e.target.value)}
            style={{ width: 200 }}
          />
          <Select
            defaultValue="all"
            style={{ width: 120 }}
            onChange={value => setFilterType(value)}
            options={[
              { value: 'all', label: '全部类型' },
              { value: 'SATA', label: 'SATA' },
              { value: 'NVMe', label: 'NVMe' },
              { value: 'USB', label: 'USB' },
            ]}
          />
          <Button 
            type="primary" 
            icon={<ReloadOutlined spin={loading} />} 
            onClick={fetchData}
          >
            刷新数据
          </Button>
          <Dropdown overlay={fileMenu} disabled={dataFiles.length === 0}>
            <Button>
              {currentFile} <DownOutlined />
            </Button>
          </Dropdown>
        </Space>

        <Table
          columns={columns}
          dataSource={filteredData}
          loading={loading}
          rowKey={(record, index) => `${record.product_name}-${index}`}
          pagination={{ pageSize: 10 }}
          scroll={{ x: true }}
        />
      </Card>
    </div>
  );
};

export default App; 