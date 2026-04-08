import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow 
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { 
  Cpu, 
  Database, 
  HardDrive, 
  History, 
  Info, 
  Layout, 
  Settings,
  ArrowRight,
  Clock,
  Monitor,
  Tag,
  CheckCircle,
  XCircle,
  AlertTriangle
} from 'lucide-react';
import apiClient from '@/api/client';
import { format } from 'date-fns';
import { useAuthStore } from '@/store/useAuthStore';
import { toast } from 'sonner';

interface DeviceComponentsTabProps {
  deviceId: string;
}

const DeviceComponentsTab: React.FC<DeviceComponentsTabProps> = ({ deviceId }) => {
  const [selectedComponentId, setSelectedComponentId] = useState<string | null>(null);
  const [confirmModal, setConfirmModal] = useState<{
    isOpen: boolean;
    type: 'approve' | 'reject' | null;
    component: any | null;
  }>({
    isOpen: false,
    type: null,
    component: null
  });

  const queryClient = useQueryClient();
  const { hasPermission } = useAuthStore();
  const canManage = hasPermission('asset.admin');

  // Fetch Components
  const { data: components, isLoading } = useQuery({
    queryKey: ['device-components', deviceId],
    queryFn: async () => {
      const response = await apiClient.get(`/devices/${deviceId}/components`);
      return response.data;
    },
  });

  // Mutations
  const approveMutation = useMutation({
    mutationFn: async (componentId: string) => {
      return apiClient.patch(`/devices/${deviceId}/components/${componentId}/approve`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['device-components', deviceId] });
      toast.success('Linh kiện đã được phê duyệt thành công');
      setConfirmModal({ isOpen: false, type: null, component: null });
    },
    onError: (error: any) => {
      toast.error(`Lỗi: ${error.message}`);
    }
  });

  const rejectMutation = useMutation({
    mutationFn: async (componentId: string) => {
      return apiClient.patch(`/devices/${deviceId}/components/${componentId}/reject`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['device-components', deviceId] });
      toast.success('Linh kiện đã được đánh dấu là không hợp lệ');
      setConfirmModal({ isOpen: false, type: null, component: null });
    },
    onError: (error: any) => {
      toast.error(`Lỗi: ${error.message}`);
    }
  });

  // Fetch Component History
  const { data: history, isLoading: isLoadingHistory } = useQuery({
    queryKey: ['component-history', selectedComponentId],
    queryFn: async () => {
      const response = await apiClient.get(`/devices/components/${selectedComponentId}/history`);
      return response.data;
    },
    enabled: !!selectedComponentId,
  });

  const getIcon = (type: string) => {
    switch (type.toUpperCase()) {
      case 'CPU': return <Cpu className="h-4 w-4" />;
      case 'RAM': return <Database className="h-4 w-4" />;
      case 'DISK': return <HardDrive className="h-4 w-4" />;
      case 'GPU': return <Layout className="h-4 w-4" />;
      case 'SCANNER': return <Tag className="h-4 w-4" />;
      case 'PRINTER': return <Monitor className="h-4 w-4" />;
      case 'PCI_CARD':
      case 'PCIE_CARD': return <Settings className="h-4 w-4" />;
      default: return <Settings className="h-4 w-4" />;
    }
  };

  const handleAction = (type: 'approve' | 'reject', component: any) => {
    setConfirmModal({
      isOpen: true,
      type,
      component
    });
  };

  const confirmAction = () => {
    if (!confirmModal.component || !confirmModal.type) return;
    
    if (confirmModal.type === 'approve') {
      approveMutation.mutate(confirmModal.component.id);
    } else {
      rejectMutation.mutate(confirmModal.component.id);
    }
  };

  if (isLoading) return <div className="p-8 text-center">Loading Components...</div>;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-in fade-in slide-in-from-bottom-4">
      {/* Components Table */}
      <div className="lg:col-span-2 space-y-4">
        <div className="border rounded-xl overflow-hidden bg-card">
          <Table>
            <TableHeader className="bg-muted/50">
              <TableRow className="text-left">
                <TableHead className="p-4 font-medium">Component</TableHead>
                <TableHead className="p-4 font-medium">Type</TableHead>
                <TableHead className="p-4 font-medium">Slot/Port</TableHead>
                <TableHead className="p-4 font-medium">Serial Number</TableHead>
                <TableHead className="p-4 font-medium">Status</TableHead>
                <TableHead className="p-4 font-medium text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody className="divide-y">
              {components?.map((comp: any) => (
                <TableRow key={comp.id} className={`hover:bg-muted/30 transition-colors ${selectedComponentId === comp.id ? 'bg-primary/5' : ''} ${comp.new_peripheral ? 'border-l-4 border-l-orange-500' : ''}`}>
                  <TableCell className="p-4">
                    <div className="flex items-center gap-3">
                      <div className={`h-8 w-8 rounded-lg flex items-center justify-center ${comp.new_peripheral ? 'bg-orange-500/10 text-orange-600' : comp.invalid_serial ? 'bg-red-500/10 text-red-600' : 'bg-primary/10 text-primary'}`}>
                        {getIcon(comp.component_type)}
                      </div>
                      <div>
                        <div className="flex flex-col gap-1">
                          <div className="flex items-center gap-2">
                            <p className="font-medium">{comp.model || comp.component_type}</p>
                            {comp.new_peripheral && (
                              <Badge variant="outline" className="text-[8px] h-4 px-1 border-orange-500 text-orange-600 animate-pulse">
                                NEW PERIPHERAL
                              </Badge>
                            )}
                            {comp.invalid_serial && (
                              <Badge variant="destructive" className="text-[8px] h-4 px-1">
                                INVALID SERIAL
                              </Badge>
                            )}
                          </div>
                          <p className="text-xs text-muted-foreground">{comp.manufacturer}</p>
                        </div>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell className="p-4">
                    <Badge variant="outline" className="text-[10px] uppercase">{comp.component_type}</Badge>
                  </TableCell>
                  <TableCell className="p-4 text-xs">
                    {comp.slot_name || comp.port_name || 'N/A'}
                  </TableCell>
                  <TableCell className="p-4 font-mono text-xs">{comp.serial_number || 'N/A'}</TableCell>
                  <TableCell className="p-4">
                    <Badge variant={comp.status === 'ACTIVE' ? 'default' : 'secondary'}>
                      {comp.status}
                    </Badge>
                  </TableCell>
                  <TableCell className="p-4 text-right">
                    <div className="flex items-center justify-end gap-2">
                      {canManage && (comp.new_peripheral || comp.invalid_serial) && (
                        <>
                          {comp.new_peripheral && (
                            <Button 
                              variant="ghost" 
                              size="icon" 
                              className="h-8 w-8 text-green-600 hover:text-green-700 hover:bg-green-50"
                              onClick={() => handleAction('approve', comp)}
                              title="Approve Peripheral"
                            >
                              <CheckCircle className="h-4 w-4" />
                            </Button>
                          )}
                          {!comp.invalid_serial && (
                            <Button 
                              variant="ghost" 
                              size="icon" 
                              className="h-8 w-8 text-red-600 hover:text-red-700 hover:bg-red-50"
                              onClick={() => handleAction('reject', comp)}
                              title="Mark as Invalid"
                            >
                              <XCircle className="h-4 w-4" />
                            </Button>
                          )}
                        </>
                      )}
                      <Button 
                        variant="ghost" 
                        size="sm" 
                        onClick={() => setSelectedComponentId(comp.id)}
                        className={selectedComponentId === comp.id ? 'text-primary' : ''}
                      >
                        <History className="h-4 w-4 mr-2" /> History
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </div>

      {/* Movement History Sidebar */}
      <div className="lg:col-span-1">
        <div className="border rounded-xl p-6 bg-card sticky top-6">
          <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
            <History className="h-5 w-5 text-primary" />
            Movement History
          </h3>
          
          {!selectedComponentId ? (
            <div className="text-center py-12 text-muted-foreground italic border-2 border-dashed rounded-xl">
              <Info className="h-8 w-8 mx-auto mb-2 opacity-20" />
              <p className="text-xs">Select a component to view its movement history across devices.</p>
            </div>
          ) : isLoadingHistory ? (
            <div className="text-center py-12">Loading history...</div>
          ) : (
            <div className="space-y-6 relative before:absolute before:left-[15px] before:top-2 before:bottom-2 before:w-[2px] before:bg-muted">
              {history?.map((event: any, i: number) => (
                <div key={event.id} className="relative pl-10">
                  <div className={`absolute left-0 top-1 h-8 w-8 rounded-full border-4 border-card flex items-center justify-center ${
                    i === 0 ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground'
                  }`}>
                    <Monitor className="h-3 w-3" />
                  </div>
                  <div className="space-y-1">
                    <p className="text-sm font-bold flex items-center gap-2">
                      {event.hostname}
                      {i === 0 && <Badge className="text-[8px] h-4 px-1">Current</Badge>}
                    </p>
                    <div className="flex items-center gap-2 text-[10px] text-muted-foreground">
                      <Clock className="h-3 w-3" />
                      {format(new Date(event.installation_date), 'MMM d, yyyy')}
                      {event.removed_date && (
                        <>
                          <ArrowRight className="h-2 w-2" />
                          {format(new Date(event.removed_date), 'MMM d, yyyy')}
                        </>
                      )}
                    </div>
                    <p className="text-[10px] uppercase tracking-wider font-bold opacity-50">{event.status}</p>
                  </div>
                </div>
              ))}
              {history?.length === 0 && (
                <p className="text-center text-xs text-muted-foreground italic">No movement history found.</p>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Confirmation Modal */}
      <Dialog open={confirmModal.isOpen} onOpenChange={(open) => !open && setConfirmModal(prev => ({ ...prev, isOpen: false }))}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              {confirmModal.type === 'approve' ? (
                <CheckCircle className="h-5 w-5 text-green-600" />
              ) : (
                <AlertTriangle className="h-5 w-5 text-red-600" />
              )}
              {confirmModal.type === 'approve' ? 'Phê duyệt linh kiện' : 'Đánh dấu không hợp lệ'}
            </DialogTitle>
            <DialogDescription className="pt-4">
              {confirmModal.type === 'approve' 
                ? "Bạn có chắc chắn muốn phê duyệt linh kiện này không? Hành động này sẽ đánh dấu linh kiện là hợp lệ và tắt flag new_peripheral."
                : "Bạn có chắc chắn muốn đánh dấu linh kiện này là không hợp lệ? Hành động này sẽ set invalid_serial = TRUE và ghi log hệ thống."
              }
            </DialogDescription>
          </DialogHeader>
          <div className="py-4 px-2 bg-muted/30 rounded-lg border text-sm">
            <p><strong>Linh kiện:</strong> {confirmModal.component?.model || confirmModal.component?.component_type}</p>
            <p><strong>S/N:</strong> {confirmModal.component?.serial_number || 'N/A'}</p>
          </div>
          <DialogFooter className="gap-2 sm:gap-0">
            <Button variant="ghost" onClick={() => setConfirmModal({ isOpen: false, type: null, component: null })}>
              Hủy
            </Button>
            <Button 
              variant={confirmModal.type === 'approve' ? 'default' : 'destructive'}
              onClick={confirmAction}
              disabled={approveMutation.isPending || rejectMutation.isPending}
            >
              {approveMutation.isPending || rejectMutation.isPending ? 'Đang xử lý...' : 'Xác nhận'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default DeviceComponentsTab;
