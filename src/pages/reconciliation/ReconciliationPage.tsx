import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  Card, CardContent, CardHeader, CardTitle, CardDescription 
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Scale, 
  RefreshCw, 
  CheckCircle2, 
  XCircle, 
  AlertTriangle, 
  Search, 
  Filter,
  ArrowRightCircle,
  Database,
  Monitor
} from 'lucide-react';
import apiClient from '@/api/client';
import { toast } from 'sonner';

const ReconciliationPage: React.FC = () => {
  const { data: conflicts, isLoading, refetch } = useQuery({
    queryKey: ['reconciliation-conflicts'],
    queryFn: async () => {
      const response = await apiClient.get('/reconciliation/conflicts');
      return response.data;
    },
  });

  const handleResolve = async (id: string, choice: 'AGENT' | 'MANUAL') => {
    try {
      await apiClient.post(`/reconciliation/conflicts/${id}/resolve`, { choice });
      toast.success(`Conflict resolved using ${choice} data`);
      refetch();
    } catch (error) {
      toast.error('Failed to resolve conflict');
    }
  };

  const handleAutoMerge = async () => {
    try {
      const res = await apiClient.post('/reconciliation/auto-merge');
      toast.success(`Auto-merge complete. Merged ${res.data.merged_count} devices.`);
      refetch();
    } catch (error) {
      toast.error('Failed to perform auto-merge');
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6 animate-in fade-in duration-500">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
            <Scale className="h-8 w-8 text-primary" />
            Data Reconciliation
          </h1>
          <p className="text-muted-foreground">Compare and resolve discrepancies between Agent data and Server data.</p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" className="border-primary text-primary hover:bg-primary/5" onClick={handleAutoMerge}>
            <RefreshCw className="h-4 w-4 mr-2" /> Auto Merge Duplicates
          </Button>
          <Button variant="outline" onClick={() => refetch()}>
            <RefreshCw className="h-4 w-4 mr-2" /> Sync Conflicts
          </Button>
        </div>
      </div>

      <div className="flex flex-col md:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input 
            className="w-full pl-10 pr-4 py-2 rounded-lg border bg-background focus:ring-2 focus:ring-primary/20 outline-none transition-all"
            placeholder="Search conflicts by hostname, serial, or field..."
          />
        </div>
        <Button variant="outline">
          <Filter className="h-4 w-4 mr-2" /> Filters
        </Button>
      </div>

      <div className="space-y-6">
        {isLoading ? (
          Array.from({ length: 3 }).map((_, i) => (
            <Card key={i} className="animate-pulse h-48" />
          ))
        ) : conflicts?.length === 0 ? (
          <div className="text-center py-20 text-muted-foreground italic border-2 border-dashed rounded-xl">
            <CheckCircle2 className="h-12 w-12 mx-auto mb-4 opacity-10" />
            No data discrepancies found. System is in sync.
          </div>
        ) : conflicts?.map((conflict: any) => (
          <Card key={conflict.id} className="border-orange-500/50 bg-orange-500/5 overflow-hidden">
            <CardHeader className="bg-orange-500/10 border-b border-orange-500/20">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <AlertTriangle className="h-5 w-5 text-orange-600" />
                  <CardTitle className="text-lg">Discrepancy: {conflict.hostname}</CardTitle>
                </div>
                <Badge variant="outline" className="bg-white border-orange-500/50 text-orange-700">
                  Field: {conflict.field_name}
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="p-0">
              <div className="grid grid-cols-1 md:grid-cols-2 divide-x divide-orange-500/20">
                <div className="p-6 space-y-4">
                  <div className="flex items-center gap-2 text-xs font-bold text-muted-foreground uppercase tracking-widest">
                    <Monitor className="h-4 w-4" /> Agent Reported Data
                  </div>
                  <div className="p-4 border rounded-xl bg-background shadow-sm">
                    <p className="text-sm font-mono text-blue-600">{conflict.agent_value}</p>
                    <p className="text-[10px] text-muted-foreground mt-2">Reported: {new Date(conflict.agent_reported_at).toLocaleString()}</p>
                  </div>
                  <Button className="w-full bg-blue-600 hover:bg-blue-700" onClick={() => handleResolve(conflict.id, 'AGENT')}>
                    Accept Agent Data
                  </Button>
                </div>
                <div className="p-6 space-y-4">
                  <div className="flex items-center gap-2 text-xs font-bold text-muted-foreground uppercase tracking-widest">
                    <Database className="h-4 w-4" /> Manual / Server Data
                  </div>
                  <div className="p-4 border rounded-xl bg-background shadow-sm">
                    <p className="text-sm font-mono text-orange-600">{conflict.manual_value}</p>
                    <p className="text-[10px] text-muted-foreground mt-2">Last Modified: {new Date(conflict.server_updated_at).toLocaleString()}</p>
                  </div>
                  <Button variant="outline" className="w-full border-orange-500 text-orange-700 hover:bg-orange-50" onClick={() => handleResolve(conflict.id, 'MANUAL')}>
                    Keep Manual Data
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default ReconciliationPage;
