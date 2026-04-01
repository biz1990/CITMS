import React from 'react'
import { Card, Tabs, Typography, Descriptions, List, Tag } from 'antd'
import ReactFlow, { Background, Controls } from 'reactflow'
import 'reactflow/dist/style.css'

const { Title } = Typography

// Dummy React Flow Node
const initialNodes = [
  { id: '1', position: { x: 250, y: 5 }, data: { label: 'LPT-CITMS-001 (Root)' }, type: 'input' },
  { id: '2', position: { x: 100, y: 100 }, data: { label: 'Zebra Docking Station' } },
  { id: '3', position: { x: 400, y: 100 }, data: { label: 'External Monitor' } },
]
const initialEdges = [{ id: 'e1-2', source: '1', target: '2' }, { id: 'e1-3', source: '1', target: '3' }]

export default function DeviceDetail() {
  const tabItems = [
    {
      key: 'info', label: '1. Device Info',
      children: (
        <Descriptions bordered column={2}>
          <Descriptions.Item label="Asset Tag">LPT-CITMS-001</Descriptions.Item>
          <Descriptions.Item label="Device Type">LAPTOP</Descriptions.Item>
          <Descriptions.Item label="Serial Number">SN12345678X</Descriptions.Item>
          <Descriptions.Item label="Status"><Tag color="green">IN_USE</Tag></Descriptions.Item>
        </Descriptions>
      )
    },
    {
      key: 'software', label: '2. Software Licenses',
      children: <List bordered dataSource={['Office 365 ProPlus - (Valid)', 'Adobe Photoshop (Violated)']} renderItem={(item) => <List.Item>{item}</List.Item>} />
    },
    {
      key: 'topology', label: '3. Network Topology',
      children: (
        <div style={{ height: 400, border: '1px solid #d9d9d9', borderRadius: 8 }}>
          <ReactFlow nodes={initialNodes} edges={initialEdges} fitView>
            <Background />
            <Controls />
          </ReactFlow>
        </div>
      )
    },
    {
      key: 'tickets', label: '4. Related Tickets',
      children: <p>No open tickets associated with this asset.</p>
    },
    {
      key: 'logs', label: '5. Audit/History Log',
      children: <p>2026-03-31: Device checked out by User A.<br/>2026-02-15: Device registered.</p>
    }
  ]

  return (
    <div>
      <Title level={3}>Device Configuration - LPT-CITMS-001</Title>
      <Card>
        <Tabs defaultActiveKey="info" items={tabItems} />
      </Card>
    </div>
  )
}
