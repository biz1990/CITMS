import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  Card, CardContent, CardHeader, CardTitle, CardDescription 
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from '@/components/ui/table';
import { 
  History, 
  Search, 
  Filter,
  Download,
  Eye,
  User,
  Clock,
  Database
} from 'lucide-react';
import { 
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogTrigger,
} from "@/components/ui/dialog";
import apiClient from '@/api/client';
import { format } from 'date-fns';

const AuditLogPage: React.FC = () => {
  const { data: logs, isLoading } = useQuery({
    queryKey: ['audit-logs'],
    queryFn: async () => {
      const response = await apiClient.get('/audit-logs');
      return response.data;
    },
  });

  const getActionColor = (action: string) => {
    switch (action?.toUpperCase()) {
      case 'CREATE': return 'bg-green-100 text-green-700 border-green-200';
      case 'UPDATE': return 'bg-blue-100 text-blue-700 border-blue-200';
      case 'DELETE': return 'bg-red-100 text-red-700 border-red-200';
      default: return 'bg-muted text-muted-foreground';
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6 animate-in fade-in duration-500">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
            <History className="h-8 w-8 text-primary" />
            Audit Logs
          </h1>
          <p className="text-muted-foreground">Track all system changes, user activities, and administrative actions.</p>
        </div>
        <Button variant="outline">
          <Download className="h-4 w-4 mr-2" /> Export Logs
        </Button>
      </div>

      <div className="flex flex-col md:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input 
            className="w-full pl-10 pr-4 py-2 rounded-lg border bg-background focus:ring-2 focus:ring-primary/20 outline-none transition-all"
            placeholder="Search logs by user, action, or resource ID..."
          />
        </div>
        <Button variant="outline">
          <Filter className="h-4 w-4 mr-2" /> Filters
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>System Activity</CardTitle>
          <CardDescription>Detailed history of all operations.</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Timestamp</TableHead>
                <TableHead>User</TableHead>
                <TableHead>Action</TableHead>
                <TableHead>Resource</TableHead>
                <TableHead>Details</TableHead>
                <TableHead className="text-right">View</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                <TableRow><TableCell colSpan={6} className="text-center py-8">Loading...</TableCell></TableRow>
              ) : logs?.length === 0 ? (
                <TableRow><TableCell colSpan={6} className="text-center py-8">No logs found.</TableCell></TableRow>
              ) : logs?.map((log: any) => (
                <TableRow key={log.id}>
                  <TableCell className="text-xs font-mono text-muted-foreground">
                    {format(new Date(log.created_at), 'MMM dd, HH:mm:ss')}
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <div className="h-6 w-6 rounded-full bg-primary/10 flex items-center justify-center text-[10px] font-bold text-primary">
                        {log.user_name?.[0] || 'U'}
                      </div>
                      <span className="text-xs">{log.user_name}</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline" className={`text-[10px] ${getActionColor(log.action)}`}>
                      {log.action}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-xs font-mono">
                    {log.resource_type} / {log.resource_id?.substring(0, 8)}
                  </TableCell>
                  <TableCell className="text-xs max-w-[300px] truncate">
                    {log.description}
                  </TableCell>
                  <TableCell className="text-right">
                    <Dialog>
                      <DialogTrigger asChild>
                        <Button variant="ghost" size="icon">
                          <Eye className="h-4 w-4" />
                        </Button>
                      </DialogTrigger>
                      <DialogContent className="max-w-2xl">
                        <DialogHeader>
                          <DialogTitle>Audit Log Details</DialogTitle>
                          <DialogDescription>
                            {log.action} on {log.resource_type} ({log.resource_id})
                          </DialogDescription>
                        </DialogHeader>
                        <div className="grid grid-cols-2 gap-4 mt-4">
                          <div className="space-y-2">
                            <h4 className="text-xs font-bold uppercase tracking-widest text-muted-foreground">Before</h4>
                            <pre className="p-4 rounded-lg bg-muted text-[10px] font-mono overflow-auto max-h-[300px]">
                              {JSON.stringify(log.old_value || {}, null, 2)}
                            </pre>
                          </div>
                          <div className="space-y-2">
                            <h4 className="text-xs font-bold uppercase tracking-widest text-muted-foreground">After</h4>
                            <pre className="p-4 rounded-lg bg-muted text-[10px] font-mono overflow-auto max-h-[300px]">
                              {JSON.stringify(log.new_value || {}, null, 2)}
                            </pre>
                          </div>
                        </div>
                        <div className="mt-4 pt-4 border-t text-[10px] text-muted-foreground flex justify-between">
                          <span>User: {log.user_name}</span>
                          <span>IP: {log.ip_address || 'N/A'}</span>
                          <span>{format(new Date(log.created_at), 'yyyy-MM-dd HH:mm:ss')}</span>
                        </div>
                      </DialogContent>
                    </Dialog>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
};

export default AuditLogPage;
