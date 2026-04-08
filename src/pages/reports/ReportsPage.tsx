import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  Card, CardContent, CardHeader, CardTitle, CardDescription 
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  BarChart3, 
  FileText, 
  Download, 
  Search, 
  Filter,
  ArrowRightCircle,
  PieChart,
  LineChart,
  Calendar,
  ShieldAlert,
  ShoppingCart,
  GitBranch
} from 'lucide-react';
import apiClient from '@/api/client';
import { toast } from 'sonner';

const ReportsPage: React.FC = () => {
  const reports = [
    { id: 'asset-inventory', title: 'Asset Inventory Report', endpoint: '/reports/asset-inventory', description: 'Overview of all hardware assets by status and type.', icon: PieChart, category: 'Inventory' },
    { id: 'asset-depreciation', title: 'Asset Depreciation Report', endpoint: '/reports/asset-depreciation', description: 'Current value and depreciation schedule of assets.', icon: LineChart, category: 'Finance' },
    { id: 'ticket-sla', title: 'ITSM SLA Performance', endpoint: '/reports/ticket-sla', description: 'Ticket volume, resolution time, and SLA compliance.', icon: BarChart3, category: 'ITSM' },
    { id: 'software-usage', title: 'Software Usage Analysis', endpoint: '/reports/software-usage', description: 'Top 10 software by installation count.', icon: FileText, category: 'Compliance' },
    { id: 'license-expiration', title: 'License Expiration', endpoint: '/reports/license-expiration', description: 'Upcoming software license expirations.', icon: Calendar, category: 'Compliance' },
    { id: 'offline-missing', title: 'Offline/Missing Devices', endpoint: '/reports/offline-missing', description: 'Devices not seen for more than 7 days.', icon: ShieldAlert, category: 'Security' },
    { id: 'audit-log', title: 'Audit Log Summary', endpoint: '/reports/audit-log', description: 'Critical system changes and user activities.', icon: FileText, category: 'Security' },
    { id: 'procurement', title: 'Procurement Summary', endpoint: '/reports/procurement', description: 'Summary of all purchase orders and spend.', icon: ShoppingCart, category: 'Finance' },
    { id: 'workflow', title: 'Workflow Efficiency', endpoint: '/reports/workflow', description: 'Onboarding and offboarding completion metrics.', icon: GitBranch, category: 'Lifecycle' },
  ];

  const handleExport = async (endpoint: string, format: string) => {
    try {
      toast.info(`Generating ${format} report...`);
      const response = await apiClient.get(endpoint, {
        params: { format },
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `Report_${new Date().getTime()}.${format.toLowerCase()}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      toast.success('Report downloaded successfully');
    } catch (error) {
      toast.error('Failed to generate report');
      console.error(error);
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6 animate-in fade-in duration-500">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
            <BarChart3 className="h-8 w-8 text-primary" />
            System Reports
          </h1>
          <p className="text-muted-foreground">Generate and export detailed reports for all system modules.</p>
        </div>
      </div>

      <div className="flex flex-col md:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input 
            className="w-full pl-10 pr-4 py-2 rounded-lg border bg-background focus:ring-2 focus:ring-primary/20 outline-none transition-all"
            placeholder="Search reports by title or category..."
          />
        </div>
        <Button variant="outline">
          <Filter className="h-4 w-4 mr-2" /> Filters
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {reports.map((report) => (
          <Card key={report.id} className="hover:shadow-lg transition-all group">
            <CardHeader className="pb-2">
              <div className="flex items-start justify-between">
                <div className="h-10 w-10 rounded-xl bg-primary/10 flex items-center justify-center text-primary">
                  <report.icon className="h-5 w-5" />
                </div>
                <Badge variant="secondary" className="text-[10px]">{report.category}</Badge>
              </div>
              <CardTitle className="mt-4 text-lg">{report.title}</CardTitle>
              <CardDescription className="text-xs line-clamp-2">{report.description}</CardDescription>
            </CardHeader>
            <CardContent className="pt-4 border-t flex items-center justify-between">
              <div className="flex gap-2">
                <Button variant="outline" size="sm" className="h-8 text-[10px]" onClick={() => handleExport(report.endpoint, 'pdf')}>
                  <Download className="h-3 w-3 mr-1" /> PDF
                </Button>
                <Button variant="outline" size="sm" className="h-8 text-[10px]" onClick={() => handleExport(report.endpoint, 'xlsx')}>
                  <Download className="h-3 w-3 mr-1" /> Excel
                </Button>
              </div>
              <Button variant="ghost" size="icon">
                <ArrowRightCircle className="h-5 w-5 group-hover:text-primary transition-colors" />
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default ReportsPage;
