import React, { Suspense, lazy } from 'react';
import { BrowserRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { useAuthStore } from '@/store/useAuthStore';
import { ThemeProvider } from '@/components/theme-provider';
import { Toaster } from '@/components/ui/sonner';
import { useNotifications } from '@/hooks/useNotifications';
import Layout from '@/components/Layout';

const LoginPage = lazy(() => import('@/pages/auth/LoginPage'));
const DashboardPage = lazy(() => import('@/pages/dashboard/DashboardPage'));
const AssetListPage = lazy(() => import('@/pages/assets/AssetListPage'));
const DeviceDetailPage = lazy(() => import('@/pages/assets/DeviceDetailPage'));
const UserListPage = lazy(() => import('@/pages/users/UserListPage'));
const TicketListPage = lazy(() => import('@/pages/tickets/TicketListPage'));
const PhysicalInventoryPage = lazy(() => import('@/pages/inventory/PhysicalInventoryPage'));
const LicenseListPage = lazy(() => import('@/pages/inventory/LicenseListPage'));
const ProcurementPage = lazy(() => import('@/pages/procurement/ProcurementPage'));
const SparePartsPage = lazy(() => import('@/pages/inventory/SparePartsPage'));
const WorkflowPage = lazy(() => import('@/pages/workflow/WorkflowPage'));
const ReconciliationPage = lazy(() => import('@/pages/reconciliation/ReconciliationPage'));
const ReportsPage = lazy(() => import('@/pages/reports/ReportsPage'));
const BlacklistPage = lazy(() => import('@/pages/blacklist/BlacklistPage'));
const AuditLogPage = lazy(() => import('@/pages/audit/AuditLogPage'));
const RBACPage = lazy(() => import('@/pages/rbac/RBACPage'));
const SettingsPage = lazy(() => import('@/pages/settings/SettingsPage'));

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

const ProtectedRoute = ({ children, permission }: { children: React.ReactNode; permission?: string }) => {
  const { isAuthenticated, hasPermission } = useAuthStore();
  
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  if (permission && !hasPermission(permission)) return <Navigate to="/unauthorized" replace />;
  
  return <>{children}</>;
};

const AppLayout = () => (
  <Layout>
    <Suspense fallback={<div className="flex h-screen items-center justify-center">Loading...</div>}>
      <Outlet />
    </Suspense>
  </Layout>
);

function App() {
  useNotifications();
  
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider defaultTheme="dark" storageKey="citms-ui-theme">
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            
            <Route element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
              <Route path="/" element={<DashboardPage />} />
              
              <Route path="/assets" element={<AssetListPage />} />
              <Route path="/assets/:id" element={<DeviceDetailPage />} />
              
              <Route path="/users" element={<UserListPage />} />
              
              <Route path="/tickets" element={<TicketListPage />} />
              
              <Route path="/inventory/physical" element={<PhysicalInventoryPage />} />
              <Route path="/inventory/licenses" element={<LicenseListPage />} />
              <Route path="/inventory/spare-parts" element={<SparePartsPage />} />
              
              <Route path="/procurement" element={<ProcurementPage />} />
              <Route path="/workflow" element={<WorkflowPage />} />
              <Route path="/reconciliation" element={<ReconciliationPage />} />
              <Route path="/reports" element={<ReportsPage />} />
              <Route path="/blacklist" element={<BlacklistPage />} />
              <Route path="/audit-log" element={<AuditLogPage />} />
              <Route path="/rbac" element={<RBACPage />} />
              <Route path="/settings" element={<SettingsPage />} />
            </Route>
            
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
        <Toaster position="top-right" richColors />
      </ThemeProvider>
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}

export default App;
