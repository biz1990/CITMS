import React from 'react'
import { Row, Col, Card, Statistic, Typography } from 'antd'
import { ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

const { Title } = Typography

// Mock data for Recharts
const trendData = [
  { name: 'Mon', tickets: 12 }, { name: 'Tue', tickets: 19 },
  { name: 'Wed', tickets: 15 }, { name: 'Thu', tickets: 22 },
  { name: 'Fri', tickets: 30 }, { name: 'Sat', tickets: 5 }, { name: 'Sun', tickets: 8 }
]

export default function Dashboard() {
  return (
    <div>
      <Title level={3}>Dashboard Command Center</Title>
      
      {/* 6 Requested Widgets */}
      <Row gutter={[16, 16]}>
        <Col span={8}><Card bordered={false}><Statistic title="SLA Breached / Total Open Tickets" value="5 / 45" valueStyle={{ color: '#cf1322' }} /></Card></Col>
        <Col span={8}><Card bordered={false}><Statistic title="License Expirations / Violations" value="12 / 3" valueStyle={{ color: '#faad14' }} /></Card></Col>
        <Col span={8}><Card bordered={false}><Statistic title="Purchase Orders Pending/Active" value="5 / 2" /></Card></Col>
        <Col span={8}><Card bordered={false}><Statistic title="Active Network Offline Alerts" value={2} prefix={<ArrowUpOutlined />} valueStyle={{ color: '#cf1322' }} /></Card></Col>
        <Col span={8}><Card bordered={false}><Statistic title="Active Vendors" value={14} valueStyle={{ color: '#1677ff' }} /></Card></Col>
        <Col span={8}><Card bordered={false}><Statistic title="Critical Spare Parts Stock" value={23} valueStyle={{ color: '#faad14' }} /></Card></Col>
      </Row>

      <div style={{ marginTop: 24 }}>
        <Card title="ITSM Ticket Velocity Trends (7 Days)">
          <div style={{ height: 300, width: '100%' }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trendData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                <Line type="monotone" dataKey="tickets" stroke="#1677ff" activeDot={{ r: 8 }} strokeWidth={3} />
                <CartesianGrid stroke="#ccc" strokeDasharray="5 5" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>
    </div>
  )
}
