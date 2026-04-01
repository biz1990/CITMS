import React, { useState } from 'react'
import { Layout, Menu, Button, theme } from 'antd'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import {
  DesktopOutlined,
  PieChartOutlined,
  TeamOutlined,
  ToolOutlined,
  LogoutOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined
} from '@ant-design/icons'
import { useAuthStore } from '../store/useAuthStore'

const { Header, Sider, Content } = Layout

export default function RootLayout() {
  const [collapsed, setCollapsed] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()
  const logout = useAuthStore(state => state.logout)
  
  const { token: { colorBgContainer, borderRadiusLG } } = theme.useToken()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const menuItems = [
    { key: '/dashboard', icon: <PieChartOutlined />, label: 'Dashboard' },
    { key: '/assets', icon: <DesktopOutlined />, label: 'Assets & IT' },
    { key: '/itsm', icon: <ToolOutlined />, label: 'ITSM Service' },
    { key: '/users', icon: <TeamOutlined />, label: 'User Roles' },
  ]

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider trigger={null} collapsible collapsed={collapsed}>
        <div style={{ height: 64, margin: 16, background: 'rgba(255, 255, 255, 0.2)', borderRadius: 6 }} />
        <Menu 
          theme="dark" 
          mode="inline" 
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
        />
      </Sider>
      <Layout>
        <Header style={{ padding: 0, background: colorBgContainer, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Button
            type="text"
            icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            onClick={() => setCollapsed(!collapsed)}
            style={{ fontSize: '16px', width: 64, height: 64 }}
          />
          <div style={{ paddingRight: 24 }}>
            <Button type="text" danger icon={<LogoutOutlined />} onClick={handleLogout}>Logout</Button>
          </div>
        </Header>
        <Content style={{ margin: '24px 16px', padding: 24, minHeight: 280, background: colorBgContainer, borderRadius: borderRadiusLG }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  )
}
