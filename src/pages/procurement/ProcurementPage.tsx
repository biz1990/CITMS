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
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  ShoppingCart, 
  Plus, 
  CheckCircle2, 
  XCircle, 
  Clock, 
  FileText,
  MoreVertical
} from 'lucide-react';
import apiClient from '@/api/client';
import { format } from 'date-fns';
import { toast } from 'sonner';

const ProcurementPage: React.FC = () => {
  const { data: pos, isLoading, refetch } = useQuery({
    queryKey: ['purchase-orders'],
    queryFn: async () => {
      const response = await apiClient.get('/procurement/purchase-orders');
      return response.data;
    },
  });

  const handleUpdateStatus = async (id: string, status: string) => {
    try {
      await apiClient.patch(`/procurement/purchase-orders/${id}/status`, { status });
      toast.success(`Order ${status.toLowerCase()} successfully`);
      refetch();
    } catch (error) {
      toast.error('Failed to update order status');
    }
  };

  const pendingPOs = pos?.filter((p: any) => p.status === 'PENDING_APPROVAL') || [];
  const approvedPOs = pos?.filter((p: any) => ['APPROVED', 'RECEIVING', 'COMPLETED'].includes(p.status)) || [];

  return (
    <div className="container mx-auto p-6 space-y-6 animate-in fade-in duration-500">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
            <ShoppingCart className="h-8 w-8 text-primary" />
            Procurement Management
          </h1>
          <p className="text-muted-foreground">Manage asset purchase orders and approvals.</p>
        </div>
        <Button>
          <Plus className="h-4 w-4 mr-2" /> New Purchase Order
        </Button>
      </div>

      <Tabs defaultValue="pending" className="w-full">
        <TabsList className="grid w-full grid-cols-2 lg:w-[400px]">
          <TabsTrigger value="pending" className="flex items-center gap-2">
            <Clock className="h-4 w-4" /> Pending Approval
            <Badge variant="secondary" className="ml-1">{pendingPOs.length}</Badge>
          </TabsTrigger>
          <TabsTrigger value="approved" className="flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4" /> Approved & History
          </TabsTrigger>
        </TabsList>

        <div className="mt-6">
          <TabsContent value="pending">
            <Card>
              <CardHeader>
                <CardTitle>Pending Approval</CardTitle>
                <CardDescription>Purchase orders awaiting manager approval.</CardDescription>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>PO Number</TableHead>
                      <TableHead>Items</TableHead>
                      <TableHead>Total Amount</TableHead>
                      <TableHead>Requested By</TableHead>
                      <TableHead>Date</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {isLoading ? (
                      <TableRow><TableCell colSpan={6} className="text-center py-8">Loading...</TableCell></TableRow>
                    ) : pendingPOs.length === 0 ? (
                      <TableRow><TableCell colSpan={6} className="text-center py-8">No pending purchase orders.</TableCell></TableRow>
                    ) : pendingPOs.map((po: any) => (
                      <TableRow key={po.id}>
                        <TableCell className="font-bold">{po.po_number}</TableCell>
                        <TableCell>
                          <div className="text-xs">
                            {po.items?.map((item: any) => `${item.item_name} (x${item.quantity})`).join(', ')}
                          </div>
                        </TableCell>
                        <TableCell className="font-mono font-bold text-primary">${po.total_amount?.toLocaleString()}</TableCell>
                        <TableCell>{po.requested_by_name || 'System'}</TableCell>
                        <TableCell>{format(new Date(po.created_at), 'MMM dd, yyyy')}</TableCell>
                        <TableCell className="text-right space-x-2">
                          <Button variant="outline" size="sm" className="text-green-600 hover:text-green-700 hover:bg-green-50" onClick={() => handleUpdateStatus(po.id, 'APPROVED')}>
                            <CheckCircle2 className="h-4 w-4 mr-1" /> Approve
                          </Button>
                          <Button variant="outline" size="sm" className="text-red-600 hover:text-red-700 hover:bg-red-50" onClick={() => handleUpdateStatus(po.id, 'REJECTED')}>
                            <XCircle className="h-4 w-4 mr-1" /> Reject
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="approved">
            <Card>
              <CardHeader>
                <CardTitle>Order History</CardTitle>
                <CardDescription>History of approved and processed purchase orders.</CardDescription>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>PO Number</TableHead>
                      <TableHead>Total Amount</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Date</TableHead>
                      <TableHead className="text-right">Action</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {approvedPOs.map((po: any) => (
                      <TableRow key={po.id}>
                        <TableCell className="font-bold">{po.po_number}</TableCell>
                        <TableCell>${po.total_amount?.toLocaleString()}</TableCell>
                        <TableCell>
                          <Badge variant={po.status === 'COMPLETED' ? 'default' : 'secondary'}>
                            {po.status}
                          </Badge>
                        </TableCell>
                        <TableCell>{format(new Date(po.created_at), 'MMM dd, yyyy')}</TableCell>
                        <TableCell className="text-right">
                          <Button variant="ghost" size="icon">
                            <MoreVertical className="h-4 w-4" />
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>
        </div>
      </Tabs>
    </div>
  );
};

export default ProcurementPage;
