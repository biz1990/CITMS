import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from '../store/useAuthStore'
import RootLayout from '../layouts/RootLayout'

// Lazy load pages
const LoginPage = React.lazy(() => import('../pages/Auth/Login'))
const DashboardPage = React.lazy(() => import('../pages/Dashboard'))
const AssetsPage = React.lazy(() => import('../pages/Assets'))
const ITSMPage = React.lazy(() => import('../pages/ITSM'))
const ReportsPage = React.lazy(() => import('../pages/Reports'))
const PhysicalInventoryPage = React.lazy(() => import('../pages/PhysicalInventory'))
const PhysicalInventoryScanPage = React.lazy(() => import('../pages/PhysicalInventory/Scan'))

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return <>{children}</>
}

export default function AppRoutes() {
  return (
    <React.Suspense fallback={<div>Loading...</div>}>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        
        <Route path="/" element={<ProtectedRoute><RootLayout /></ProtectedRoute>}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="assets" element={<AssetsPage />} />
          <Route path="itsm" element={<ITSMPage />} />
          <Route path="reports" element={<ReportsPage />} />
          <Route path="physical-inventory" element={<PhysicalInventoryPage />} />
          <Route path="physical-inventory/scan/:surveyId" element={<PhysicalInventoryScanPage />} />
        </Route>
      </Routes>
    </React.Suspense>
  )
}
