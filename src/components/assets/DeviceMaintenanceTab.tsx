import React from 'react';
import { useQuery } from '@tanstack/react-query';
import apiClient from '@/api/client';
import { 
  Card, 
  CardContent, 
  CardHeader, 
  CardTitle 
} from '@/components/ui/card';
import { 
  Wrench, 
  Calendar, 
  User, 
  Paperclip, 
  Clock,
  History
} from 'lucide-react';
import { format } from 'date-fns';
import { Badge } from '@/components/ui/badge';

interface DeviceMaintenanceTabProps {
  deviceId: string;
}

const DeviceMaintenanceTab: React.FC<DeviceMaintenanceTabProps> = ({ deviceId }) => {
  const { data: logs, isLoading } = useQuery({
    queryKey: ['device-maintenance', deviceId],
    queryFn: async () => {
      const response = await apiClient.get(`/devices/${deviceId}/maintenance`);
      return response.data;
    },
  });

  if (isLoading) return <div className="p-8 text-center">Loading maintenance history...</div>;

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <Wrench className="h-5 w-5 text-primary" />
          Maintenance History & Service Logs
        </h3>
        <Badge variant="outline" className="flex items-center gap-1">
          <History className="h-3 w-3" /> {logs?.length || 0} Logs
        </Badge>
      </div>

      <div className="relative space-y-8 before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-slate-300 before:to-transparent dark:before:via-slate-700">
        {logs?.map((log: any) => (
          <div key={log.id} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
            {/* Dot */}
            <div className="flex items-center justify-center w-10 h-10 rounded-full border border-white bg-slate-300 dark:bg-slate-700 text-slate-500 shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2">
              <Wrench className="h-5 w-5" />
            </div>
            
            {/* Card */}
            <Card className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] p-4 rounded-xl shadow-sm hover:shadow-md transition-shadow border-slate-200 dark:border-slate-800">
              <CardHeader className="p-0 pb-2 flex flex-row items-center justify-between space-y-0">
                <div className="flex items-center gap-2">
                  <Badge variant={log.status === 'COMPLETED' ? 'default' : 'secondary'} className="text-[10px] uppercase font-bold">
                    {log.status}
                  </Badge>
                  <span className="text-xs text-muted-foreground flex items-center gap-1">
                    <Calendar className="h-3 w-3" /> {format(new Date(log.performed_at), 'PPP')}
                  </span>
                </div>
                <div className="text-xs text-muted-foreground flex items-center gap-1">
                  <User className="h-3 w-3" /> {log.technician_name || 'System'}
                </div>
              </CardHeader>
              <CardContent className="p-0 space-y-3">
                <div className="text-sm font-semibold text-slate-900 dark:text-slate-100">
                  {log.action_taken}
                </div>
                <p className="text-xs text-muted-foreground leading-relaxed">
                  {log.description || 'No detailed description provided for this maintenance log.'}
                </p>
                
                {/* Spare Parts Used */}
                {log.spare_parts_used && Object.keys(log.spare_parts_used).length > 0 && (
                  <div className="bg-muted/50 p-2 rounded-md space-y-1">
                    <div className="text-[10px] font-bold uppercase text-muted-foreground">Spare Parts Used</div>
                    <div className="flex flex-wrap gap-1">
                      {Object.entries(log.spare_parts_used).map(([part, qty]: [string, any]) => (
                        <Badge key={part} variant="outline" className="text-[10px] bg-background">
                          {part}: {qty}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                {/* Attachments */}
                {log.attachments && log.attachments.length > 0 && (
                  <div className="flex flex-wrap gap-2 pt-2">
                    {log.attachments.map((file: any, idx: number) => (
                      <div key={idx} className="flex items-center gap-1 text-[10px] text-primary hover:underline cursor-pointer bg-primary/5 px-2 py-1 rounded border border-primary/20">
                        <Paperclip className="h-3 w-3" /> {file.name || `Attachment ${idx + 1}`}
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        ))}
        
        {logs?.length === 0 && (
          <div className="text-center py-12 text-muted-foreground bg-muted/20 rounded-lg border border-dashed">
            <Clock className="h-12 w-12 mx-auto mb-4 opacity-20" />
            <p>No maintenance logs found for this device.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default DeviceMaintenanceTab;
