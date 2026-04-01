import React from 'react'
import { Table, Button, Space, Typography } from 'antd'

const { Title } = Typography

export default function Assets() {
  const columns = [
    { title: 'Asset Tag', dataIndex: 'asset_tag', key: 'asset_tag' },
    { title: 'Name', dataIndex: 'name', key: 'name' },
    { title: 'Type', dataIndex: 'device_type', key: 'device_type' },
    { title: 'Status', dataIndex: 'status', key: 'status' },
    {
      title: 'Action',
      key: 'action',
      render: (_: any, record: any) => (
        <Space size="middle">
          <a>View Detail (5 Tabs)</a>
        </Space>
      ),
    },
  ]

  const data = [
    { key: '1', asset_tag: 'LPT-CITMS-001', name: 'Dev Laptop 1', device_type: 'LAPTOP', status: 'IN_USE' },
    { key: '2', asset_tag: 'SCN-CITMS-012', name: 'Zebra Wireless', device_type: 'SCANNER', status: 'IN_USE' },
  ]

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <Title level={3}>Asset Inventory</Title>
        <Button type="primary">Register Device</Button>
      </div>
      <Table columns={columns} dataSource={data} />
    </div>
  )
}
