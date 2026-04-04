import React, { useState, useMemo } from 'react'
import {
  Tabs, Table, Card, Row, Col, Select, Input, Button, Badge,
  Space, Tag, Typography, Statistic, DatePicker, Alert,
} from 'antd'
import type { ColumnsType } from 'antd/es/table'
import {
  DownloadOutlined, FilterOutlined, ReloadOutlined,
  ExclamationCircleOutlined, CheckCircleOutlined, StopOutlined,
} from '@ant-design/icons'
import { useQuery } from '@tanstack/react-query'
import dayjs from 'dayjs'

import {
  getRAMInventory, getSoftwareUsage, getComponentSummary, exportReport,
  RAMComponentRow, SoftwareInstallationRow, ComponentSummaryRow,
  RAMInventoryFilters, SoftwareUsageFilters,
} from '../../services/reports'

const { Title, Text } = Typography
const { RangePicker } = DatePicker
const { Option } = Select

// ─── Shared download helper ───────────────────────────────────────────────
function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

// ═════════════════════════════════════════════════════════════════════════ //
// TAB 1 — RAM Inventory
// ═════════════════════════════════════════════════════════════════════════ //
function RAMInventoryTab() {
  const [filters, setFilters] = useState<RAMInventoryFilters>({})
  const [applied, setApplied] = useState<RAMInventoryFilters>({})
  const [exporting, setExporting] = useState(false)

  const { data, isLoading, isError } = useQuery({
    queryKey: ['ram-inventory', applied],
    queryFn: () => getRAMInventory(applied).then(r => r.data),
    staleTime: 5 * 60 * 1000,
  })

  const handleExport = async (fmt: 'excel' | 'pdf') => {
    setExporting(true)
    try {
      const res = await exportReport('ram-inventory', fmt, applied)
      downloadBlob(res.data as Blob, `ram_inventory.${fmt === 'excel' ? 'xlsx' : 'pdf'}`)
    } finally {
      setExporting(false)
    }
  }

  const columns: ColumnsType<RAMComponentRow> = [
    { title: 'Hostname',     dataIndex: 'hostname',    key: 'hostname',    sorter: (a, b) => (a.hostname || '').localeCompare(b.hostname || ''), width: 140, fixed: 'left' },
    { title: 'Asset Tag',    dataIndex: 'asset_tag',   key: 'asset_tag',   width: 110 },
    { title: 'Department',   dataIndex: 'department',  key: 'department',  width: 130, render: v => v ? <Tag color="blue">{v}</Tag> : '—' },
    { title: 'Location',     dataIndex: 'location_name', key: 'location',  width: 120 },
    { title: 'Slot',         dataIndex: 'slot_name',   key: 'slot_name',   width: 100, render: v => v ? <Tag color="purple">{v}</Tag> : '—' },
    { title: 'Manufacturer', dataIndex: 'manufacturer', key: 'manufacturer', width: 120, sorter: (a, b) => (a.manufacturer || '').localeCompare(b.manufacturer || '') },
    { title: 'Model',        dataIndex: 'ram_model',   key: 'ram_model',   width: 160 },
    {
      title: 'Capacity', dataIndex: 'capacity_gb', key: 'capacity_gb', width: 100,
      sorter: (a, b) => (a.capacity_gb || 0) - (b.capacity_gb || 0),
      render: v => v != null ? <Tag color="green">{v} GB</Tag> : '—',
    },
    {
      title: 'Type', dataIndex: 'memory_type', key: 'memory_type', width: 90,
      render: v => v ? <Tag color={v === 'DDR5' ? 'gold' : 'cyan'}>{v}</Tag> : '—',
    },
    {
      title: 'Speed (MHz)', dataIndex: 'speed_mhz', key: 'speed_mhz', width: 110,
      sorter: (a, b) => (a.speed_mhz || 0) - (b.speed_mhz || 0),
      render: v => v ? `${v} MHz` : '—',
    },
    { title: 'Form Factor',  dataIndex: 'form_factor', key: 'form_factor', width: 100 },
    { title: 'Status',       dataIndex: 'component_status', key: 'status', width: 100,
      render: v => <Tag color={v === 'active' ? 'success' : 'warning'}>{v || '—'}</Tag> },
  ]

  return (
    <div>
      {/* Filter panel */}
      <Card size="small" style={{ marginBottom: 16, background: '#f8fafc' }}>
        <Row gutter={[12, 8]} align="middle">
          <Col span={4}>
            <Input
              placeholder="Manufacturer (e.g. Samsung)"
              prefix={<FilterOutlined />}
              value={filters.manufacturer || ''}
              onChange={e => setFilters(f => ({ ...f, manufacturer: e.target.value || undefined }))}
            />
          </Col>
          <Col span={3}>
            <Select
              placeholder="Memory Type"
              allowClear
              style={{ width: '100%' }}
              value={filters.memory_type}
              onChange={v => setFilters(f => ({ ...f, memory_type: v }))}
            >
              <Option value="DDR4">DDR4</Option>
              <Option value="DDR5">DDR5</Option>
              <Option value="DDR3">DDR3</Option>
            </Select>
          </Col>
          <Col span={7}>
            <RangePicker
              style={{ width: '100%' }}
              placeholder={['Install From', 'Install To']}
              onChange={vals => setFilters(f => ({
                ...f,
                date_from: vals?.[0]?.format('YYYY-MM-DD'),
                date_to: vals?.[1]?.format('YYYY-MM-DD'),
              }))}
            />
          </Col>
          <Col span={4}>
            <Space>
              <Button type="primary" icon={<FilterOutlined />} onClick={() => setApplied({ ...filters })}>
                Apply Filter
              </Button>
              <Button icon={<ReloadOutlined />} onClick={() => { setFilters({}); setApplied({}) }}>
                Reset
              </Button>
            </Space>
          </Col>
          <Col span={6} style={{ textAlign: 'right' }}>
            <Space>
              <Button icon={<DownloadOutlined />} loading={exporting} onClick={() => handleExport('excel')}>
                Excel
              </Button>
              <Button icon={<DownloadOutlined />} loading={exporting} onClick={() => handleExport('pdf')} danger>
                PDF
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* Summary cards */}
      {data && (
        <Row gutter={[12, 12]} style={{ marginBottom: 16 }}>
          <Col span={4}><Card size="small"><Statistic title="Total Modules" value={data.total_records} /></Card></Col>
          <Col span={4}><Card size="small"><Statistic title="Total RAM" value={`${data.total_gb} GB`} valueStyle={{ color: '#1677ff' }} /></Card></Col>
          {Object.entries(data.by_type).map(([k, v]) => (
            <Col span={3} key={k}>
              <Card size="small">
                <Statistic title={k} value={v} suffix="modules" />
              </Card>
            </Col>
          ))}
          {Object.entries(data.by_manufacturer).slice(0, 3).map(([k, v]) => (
            <Col span={4} key={k}>
              <Card size="small">
                <Statistic title={k} value={`${v} GB`} />
              </Card>
            </Col>
          ))}
        </Row>
      )}

      {isError && <Alert type="error" message="Failed to load RAM inventory. Check API connection." style={{ marginBottom: 12 }} />}

      <Table<RAMComponentRow>
        dataSource={data?.items}
        columns={columns}
        rowKey="component_id"
        loading={isLoading}
        scroll={{ x: 1200 }}
        pagination={{ pageSize: 20, showSizeChanger: true, showTotal: t => `${t} records` }}
        size="small"
      />
    </div>
  )
}

// ═════════════════════════════════════════════════════════════════════════ //
// TAB 2 — Software Usage
// ═════════════════════════════════════════════════════════════════════════ //
function SoftwareUsageTab() {
  const [filters, setFilters] = useState<SoftwareUsageFilters>({})
  const [applied, setApplied] = useState<SoftwareUsageFilters>({})
  const [exporting, setExporting] = useState(false)
  const [activeSubTab, setActiveSubTab] = useState<'all' | 'violations'>('all')

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ['software-usage', applied],
    queryFn: () => getSoftwareUsage(applied).then(r => r.data),
    staleTime: 5 * 60 * 1000,
  })

  const handleExport = async (fmt: 'excel' | 'pdf') => {
    setExporting(true)
    try {
      const res = await exportReport('software-usage', fmt, applied)
      downloadBlob(res.data as Blob, `software_usage.${fmt === 'excel' ? 'xlsx' : 'pdf'}`)
    } finally {
      setExporting(false)
    }
  }

  const violationRender = (row: SoftwareInstallationRow) => {
    const tags = []
    if (row.over_license) tags.push(<Tag key="ol" color="orange" icon={<ExclamationCircleOutlined />}>Over License</Tag>)
    if (row.is_blacklisted) tags.push(<Tag key="bl" color="red" icon={<StopOutlined />}>Blacklisted</Tag>)
    if (row.is_blocked)     tags.push(<Tag key="bk" color="volcano" icon={<StopOutlined />}>Blocked</Tag>)
    if (!tags.length)       return <Tag color="success" icon={<CheckCircleOutlined />}>OK</Tag>
    return <>{tags}</>
  }

  const columns: ColumnsType<SoftwareInstallationRow> = [
    {
      title: 'Software', dataIndex: 'software_name', key: 'software_name', fixed: 'left', width: 200,
      sorter: (a, b) => a.software_name.localeCompare(b.software_name),
    },
    { title: 'Version',    dataIndex: 'version',    key: 'version',  width: 100 },
    { title: 'Publisher',  dataIndex: 'publisher',  key: 'publisher', width: 130 },
    { title: 'Hostname',   dataIndex: 'hostname',   key: 'hostname',  width: 140 },
    { title: 'Asset Tag',  dataIndex: 'asset_tag',  key: 'asset_tag', width: 110 },
    {
      title: 'Department', dataIndex: 'department', key: 'department', width: 130,
      render: v => v ? <Tag color="blue">{v}</Tag> : '—',
    },
    {
      title: 'License Type', dataIndex: 'license_type', key: 'license_type', width: 120,
      render: v => v ? <Tag>{v}</Tag> : <Tag color="default">No License</Tag>,
    },
    {
      title: 'Seats', key: 'seats', width: 110,
      render: (_, row) => row.total_seats != null
        ? <span style={{ color: row.over_license ? '#dc2626' : 'inherit' }}>{row.used_seats}/{row.total_seats}</span>
        : '—',
    },
    {
      title: 'License Expiry', dataIndex: 'license_expire_date', key: 'license_expire_date', width: 130,
      render: v => {
        if (!v) return '—'
        const expired = dayjs(v).isBefore(dayjs())
        return <span style={{ color: expired ? '#dc2626' : undefined }}>{v}</span>
      },
    },
    {
      title: 'Status', key: 'status', width: 220, fixed: 'right',
      render: (_, row) => violationRender(row),
    },
  ]

  const displayData = activeSubTab === 'violations' ? data?.violations : data?.items

  return (
    <div>
      {/* Filter panel */}
      <Card size="small" style={{ marginBottom: 16, background: '#f8fafc' }}>
        <Row gutter={[12, 8]} align="middle">
          <Col span={5}>
            <Input
              placeholder="Software name (e.g. Microsoft Office)"
              prefix={<FilterOutlined />}
              value={filters.software_name || ''}
              onChange={e => setFilters(f => ({ ...f, software_name: e.target.value || undefined }))}
            />
          </Col>
          <Col span={3}>
            <Select
              placeholder="License type"
              allowClear
              style={{ width: '100%' }}
              value={filters.license_type}
              onChange={v => setFilters(f => ({ ...f, license_type: v }))}
            >
              <Option value="volume">Volume</Option>
              <Option value="subscription">Subscription</Option>
              <Option value="OEM">OEM</Option>
              <Option value="freeware">Freeware</Option>
            </Select>
          </Col>
          <Col span={4}>
            <Input
              placeholder="Publisher"
              value={filters.publisher || ''}
              onChange={e => setFilters(f => ({ ...f, publisher: e.target.value || undefined }))}
            />
          </Col>
          <Col span={4}>
            <Space>
              <Button type="primary" icon={<FilterOutlined />} onClick={() => setApplied({ ...filters })}>Apply</Button>
              <Button icon={<ReloadOutlined />} onClick={() => { setFilters({}); setApplied({}) }}>Reset</Button>
            </Space>
          </Col>
          <Col span={8} style={{ textAlign: 'right' }}>
            <Space>
              <Button icon={<DownloadOutlined />} loading={exporting} onClick={() => handleExport('excel')}>Excel</Button>
              <Button icon={<DownloadOutlined />} loading={exporting} onClick={() => handleExport('pdf')} danger>PDF</Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* Summary row */}
      {data && (
        <Row gutter={[12, 12]} style={{ marginBottom: 16 }}>
          <Col span={4}><Card size="small"><Statistic title="Total Installations" value={data.total_records} /></Card></Col>
          <Col span={4}>
            <Card size="small" style={{ background: data.violation_count > 0 ? '#fef2f2' : undefined }}>
              <Statistic title="Violations" value={data.violation_count}
                valueStyle={{ color: data.violation_count > 0 ? '#dc2626' : '#16a34a' }} />
            </Card>
          </Col>
          <Col span={4}><Card size="small"><Statistic title="Unique Software" value={data.by_software.length} /></Card></Col>
          {data.by_software.slice(0, 3).map(s => (
            <Col span={4} key={s.software_name}>
              <Card size="small">
                <Statistic title={s.software_name.length > 18 ? s.software_name.slice(0, 18) + '…' : s.software_name}
                  value={s.total_installs} suffix="installs" />
              </Card>
            </Col>
          ))}
        </Row>
      )}

      {isError && <Alert type="error" message="Failed to load software usage data." style={{ marginBottom: 12 }} />}

      {/* Sub-tab: All / Violations only */}
      <Space style={{ marginBottom: 12 }}>
        <Button type={activeSubTab === 'all' ? 'primary' : 'default'} onClick={() => setActiveSubTab('all')}>
          All Installations
        </Button>
        <Button
          type={activeSubTab === 'violations' ? 'primary' : 'default'}
          danger={activeSubTab === 'violations'}
          onClick={() => setActiveSubTab('violations')}
        >
          <Badge count={data?.violation_count || 0} offset={[6, -2]}>
            Violations Only
          </Badge>
        </Button>
      </Space>

      <Table<SoftwareInstallationRow>
        dataSource={displayData}
        columns={columns}
        rowKey="installation_id"
        loading={isLoading}
        scroll={{ x: 1400 }}
        pagination={{ pageSize: 20, showSizeChanger: true, showTotal: t => `${t} records` }}
        size="small"
        rowClassName={row =>
          row.is_blacklisted ? 'ant-table-row-blacklisted'
          : row.over_license || row.is_blocked ? 'ant-table-row-violation'
          : ''
        }
      />

      {/* Inline styles for row highlighting */}
      <style>{`
        .ant-table-row-blacklisted > td { background: #fef3c7 !important; }
        .ant-table-row-violation > td { background: #fee2e2 !important; }
      `}</style>
    </div>
  )
}

// ═════════════════════════════════════════════════════════════════════════ //
// TAB 3 — Component Summary
// ═════════════════════════════════════════════════════════════════════════ //
function ComponentSummaryTab() {
  const [applied, setApplied] = useState({})
  const [exporting, setExporting] = useState(false)

  const { data, isLoading, isError } = useQuery({
    queryKey: ['component-summary', applied],
    queryFn: () => getComponentSummary(applied).then(r => r.data),
    staleTime: 5 * 60 * 1000,
  })

  const handleExport = async (fmt: 'excel' | 'pdf') => {
    setExporting(true)
    try {
      const res = await exportReport('component-summary', fmt, applied)
      downloadBlob(res.data as Blob, `component_summary.${fmt === 'excel' ? 'xlsx' : 'pdf'}`)
    } finally {
      setExporting(false)
    }
  }

  const columns: ColumnsType<ComponentSummaryRow> = [
    { title: 'Hostname', dataIndex: 'hostname', key: 'hostname', fixed: 'left', width: 140, sorter: (a, b) => (a.hostname || '').localeCompare(b.hostname || '') },
    { title: 'Asset Tag', dataIndex: 'asset_tag', key: 'asset_tag', width: 110 },
    { title: 'Department', dataIndex: 'department', key: 'department', width: 130, render: v => v ? <Tag color="blue">{v}</Tag> : '—' },
    { title: 'OS', dataIndex: 'os_name', key: 'os_name', width: 120 },
    {
      title: 'CPU', key: 'cpu', width: 200,
      render: (_, r) => r.cpu_model ? `${r.cpu_manufacturer || ''} ${r.cpu_model}`.trim() : '—',
    },
    { title: 'Cores', dataIndex: 'cpu_cores', key: 'cpu_cores', width: 80, sorter: (a, b) => (a.cpu_cores || 0) - (b.cpu_cores || 0) },
    {
      title: 'RAM (Total)', dataIndex: 'total_ram_gb', key: 'total_ram_gb', width: 110,
      sorter: (a, b) => (a.total_ram_gb || 0) - (b.total_ram_gb || 0),
      render: v => v != null ? <Tag color="green">{v} GB</Tag> : '—',
    },
    { title: 'RAM Slots', dataIndex: 'ram_slots_used', key: 'ram_slots_used', width: 100 },
    {
      title: 'Mainboard', key: 'mainboard', width: 200,
      render: (_, r) => r.mainboard_model ? `${r.mainboard_manufacturer || ''} ${r.mainboard_model}`.trim() : '—',
    },
    { title: 'BIOS', dataIndex: 'bios_version', key: 'bios_version', width: 120 },
  ]

  return (
    <div>
      <Row justify="end" style={{ marginBottom: 16 }}>
        <Space>
          <Button icon={<DownloadOutlined />} loading={exporting} onClick={() => handleExport('excel')}>Excel</Button>
          <Button icon={<DownloadOutlined />} loading={exporting} onClick={() => handleExport('pdf')} danger>PDF</Button>
        </Space>
      </Row>

      {data && (
        <Row gutter={[12, 12]} style={{ marginBottom: 16 }}>
          <Col span={4}><Card size="small"><Statistic title="Total Devices" value={data.total_devices} /></Card></Col>
          {Object.entries(data.by_cpu_manufacturer).map(([k, v]) => (
            <Col span={4} key={k}><Card size="small"><Statistic title={`CPU: ${k}`} value={v} suffix="devices" /></Card></Col>
          ))}
          {Object.entries(data.by_ram_size).slice(0, 3).map(([k, v]) => (
            <Col span={3} key={k}><Card size="small"><Statistic title={`RAM ${k}`} value={v} suffix="devices" /></Card></Col>
          ))}
        </Row>
      )}

      {isError && <Alert type="error" message="Failed to load component summary." style={{ marginBottom: 12 }} />}

      <Table<ComponentSummaryRow>
        dataSource={data?.items}
        columns={columns}
        rowKey="device_id"
        loading={isLoading}
        scroll={{ x: 1200 }}
        pagination={{ pageSize: 20, showSizeChanger: true, showTotal: t => `${t} devices` }}
        size="small"
      />
    </div>
  )
}

// ═════════════════════════════════════════════════════════════════════════ //
// MAIN Reports Page
// ═════════════════════════════════════════════════════════════════════════ //
export default function ReportsPage() {
  return (
    <div>
      <Title level={3} style={{ marginBottom: 4 }}>📊 Reports & Export</Title>
      <Text type="secondary" style={{ display: 'block', marginBottom: 20 }}>
        Detailed hardware inventory, software compliance, and component summary reports.
        All reports are cached for 15 minutes. Export as Excel or PDF.
      </Text>

      <Tabs
        defaultActiveKey="ram"
        size="large"
        type="card"
        items={[
          {
            key: 'ram',
            label: '🖥 RAM Inventory',
            children: <RAMInventoryTab />,
          },
          {
            key: 'software',
            label: '📦 Software Usage',
            children: <SoftwareUsageTab />,
          },
          {
            key: 'components',
            label: '🔧 Component Summary',
            children: <ComponentSummaryTab />,
          },
        ]}
      />
    </div>
  )
}
