import React, { useMemo } from 'react'
import { Row, Col, Card, Statistic, Typography, Badge, Spin, Alert } from 'antd'
import { ArrowUpOutlined, WarningOutlined } from '@ant-design/icons'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
  BarChart, Bar,
} from 'recharts'
import { useQuery } from '@tanstack/react-query'

import { getRAMInventory, getSoftwareUsage } from '../../services/reports'

const { Title, Text } = Typography

// ── Tick velocity trend data (mock – replace with real API when ITSM module exposes endpoint) ──
const trendData = [
  { name: 'Mon', tickets: 12 }, { name: 'Tue', tickets: 19 },
  { name: 'Wed', tickets: 15 }, { name: 'Thu', tickets: 22 },
  { name: 'Fri', tickets: 30 }, { name: 'Sat', tickets: 5 }, { name: 'Sun', tickets: 8 },
]

// Color palette for pie/bar charts
const CHART_COLORS = ['#1d4ed8', '#16a34a', '#d97706', '#dc2626', '#7c3aed', '#0891b2', '#be185d', '#65a30d']

// ─── Widget: RAM Summary (Donut chart by manufacturer) ──────────────────────
function RAMSummaryWidget() {
  const { data, isLoading } = useQuery({
    queryKey: ['ram-inventory-dashboard', {}],
    queryFn: () => getRAMInventory({}).then(r => r.data),
    staleTime: 15 * 60 * 1000,
  })

  const pieData = useMemo(() => {
    if (!data?.by_manufacturer) return []
    return Object.entries(data.by_manufacturer)
      .map(([name, value]) => ({ name, value }))
      .sort((a, b) => b.value - a.value)
      .slice(0, 6)
  }, [data])

  return (
    <Card
      title={
        <span>
          <span style={{ marginRight: 8 }}>🖥</span>
          RAM Summary
          {data && <Text type="secondary" style={{ fontWeight: 400, marginLeft: 8, fontSize: 12 }}>
            Total: {data.total_gb} GB · {data.total_records} modules
          </Text>}
        </span>
      }
      bordered={false}
      style={{ height: 320 }}
    >
      {isLoading ? (
        <div style={{ textAlign: 'center', paddingTop: 80 }}><Spin /></div>
      ) : pieData.length === 0 ? (
        <Alert message="No RAM data available" type="info" showIcon style={{ marginTop: 40 }} />
      ) : (
        <ResponsiveContainer width="100%" height={230}>
          <PieChart>
            <Pie
              data={pieData}
              cx="40%"
              cy="50%"
              innerRadius={55}
              outerRadius={90}
              paddingAngle={3}
              dataKey="value"
              label={({ name, value }) => `${value.toFixed(0)}GB`}
              labelLine={false}
            >
              {pieData.map((_, i) => (
                <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
              ))}
            </Pie>
            <Tooltip formatter={(v: number) => [`${v.toFixed(1)} GB`, 'Total']} />
            <Legend
              layout="vertical"
              align="right"
              verticalAlign="middle"
              formatter={(v) => <span style={{ fontSize: 12 }}>{v}</span>}
            />
          </PieChart>
        </ResponsiveContainer>
      )}
    </Card>
  )
}

// ─── Widget: Software Usage Breakdown (Bar chart top 8 + violations badge) ───
function SoftwareUsageWidget() {
  const { data, isLoading } = useQuery({
    queryKey: ['software-usage-dashboard', {}],
    queryFn: () => getSoftwareUsage({}).then(r => r.data),
    staleTime: 15 * 60 * 1000,
  })

  const barData = useMemo(() => {
    if (!data?.by_software) return []
    return data.by_software.slice(0, 8).map(s => ({
      name: s.software_name.length > 16 ? s.software_name.slice(0, 16) + '…' : s.software_name,
      fullName: s.software_name,
      installs: s.total_installs,
    }))
  }, [data])

  return (
    <Card
      title={
        <span>
          <span style={{ marginRight: 8 }}>📦</span>
          Software Usage Breakdown
          {data && data.violation_count > 0 && (
            <Badge
              count={data.violation_count}
              style={{ backgroundColor: '#dc2626', marginLeft: 10 }}
              title={`${data.violation_count} license violation(s)`}
            />
          )}
        </span>
      }
      bordered={false}
      style={{ height: 320 }}
      extra={data?.violation_count ? (
        <Text type="danger" style={{ fontSize: 12 }}>
          <WarningOutlined /> {data.violation_count} violations
        </Text>
      ) : null}
    >
      {isLoading ? (
        <div style={{ textAlign: 'center', paddingTop: 80 }}><Spin /></div>
      ) : barData.length === 0 ? (
        <Alert message="No software data available" type="info" showIcon style={{ marginTop: 40 }} />
      ) : (
        <ResponsiveContainer width="100%" height={230}>
          <BarChart data={barData} margin={{ top: 5, right: 10, bottom: 30, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} />
            <XAxis
              dataKey="name"
              tick={{ fontSize: 10 }}
              angle={-30}
              textAnchor="end"
              interval={0}
            />
            <YAxis tick={{ fontSize: 11 }} />
            <Tooltip
              formatter={(v: number, _, { payload }) => [v, payload?.fullName || '']}
            />
            <Bar dataKey="installs" radius={[4, 4, 0, 0]}>
              {barData.map((_, i) => (
                <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      )}
    </Card>
  )
}

// ─── Main Dashboard ───────────────────────────────────────────────────────────
export default function Dashboard() {
  return (
    <div>
      <Title level={3}>Dashboard Command Center</Title>

      {/* KPI widgets row */}
      <Row gutter={[16, 16]}>
        <Col span={8}>
          <Card bordered={false}>
            <Statistic title="SLA Breached / Total Open Tickets" value="5 / 45" valueStyle={{ color: '#cf1322' }} />
          </Card>
        </Col>
        <Col span={8}>
          <Card bordered={false}>
            <Statistic title="License Expirations / Violations" value="12 / 3" valueStyle={{ color: '#faad14' }} />
          </Card>
        </Col>
        <Col span={8}>
          <Card bordered={false}>
            <Statistic title="Purchase Orders Pending/Active" value="5 / 2" />
          </Card>
        </Col>
        <Col span={8}>
          <Card bordered={false}>
            <Statistic title="Active Network Offline Alerts" value={2} prefix={<ArrowUpOutlined />} valueStyle={{ color: '#cf1322' }} />
          </Card>
        </Col>
        <Col span={8}>
          <Card bordered={false}>
            <Statistic title="Active Vendors" value={14} valueStyle={{ color: '#1677ff' }} />
          </Card>
        </Col>
        <Col span={8}>
          <Card bordered={false}>
            <Statistic title="Critical Spare Parts Stock" value={23} valueStyle={{ color: '#faad14' }} />
          </Card>
        </Col>
      </Row>

      {/* Charts row 1: ITSM trend */}
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

      {/* Charts row 2: NEW Module 8 widgets */}
      <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
        <Col span={12}>
          <RAMSummaryWidget />
        </Col>
        <Col span={12}>
          <SoftwareUsageWidget />
        </Col>
      </Row>
    </div>
  )
}
