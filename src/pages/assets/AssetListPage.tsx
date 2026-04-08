import React, { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from '@/components/ui/table';
import { 
  Plus, 
  Search, 
  Filter, 
  MoreVertical, 
  Monitor, 
  Laptop, 
  Smartphone, 
  Server, 
  HardDrive, 
  Download, 
  Trash2, 
  Edit, 
  ExternalLink,
  ShieldCheck,
  ShieldAlert,
  Network
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuLabel, 
  DropdownMenuSeparator, 
  DropdownMenuTrigger 
} from '@/components/ui/dropdown-menu';
import { 
  Dialog, 
  DialogContent, 
  DialogDescription, 
  DialogFooter, 
  DialogHeader, 
  DialogTitle, 
  DialogTrigger 
} from '@/components/ui/dialog';
import { 
  Card, 
  CardContent, 
  CardHeader, 
  CardTitle 
} from '@/components/ui/card';
import { Checkbox } from '@/components/ui/checkbox';
import { Skeleton } from '@/components/ui/skeleton';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import apiClient from '@/api/client';
import { toast } from 'sonner';

const AssetListPage: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [search, setSearch] = useState('');
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('all');

  // Fetch Assets
  const { data: assets, isLoading, error, refetch } = useQuery({
    queryKey: ['assets', activeTab],
    queryFn: async () => {
      const params = activeTab === 'pending' ? { status: 'PENDING_APPROVAL' } : {};
      const response = await apiClient.get('/devices', { params });
      return response.data;
    },
  });

  // Approve Mutation
  const approveMutation = useMutation({
    mutationFn: async (id: string) => {
      await apiClient.put(`/devices/${id}/approve`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assets'] });
      toast.success('Device approved successfully');
      refetch();
    },
    onError: (err: any) => {
      toast.error(`Failed to approve device: ${err.message}`);
    }
  });

  // Delete Mutation
  const deleteMutation = useMutation({
    mutationFn: async (ids: string[]) => {
      // In a real app, this would be a bulk delete API
      for (const id of ids) {
        await apiClient.delete(`/devices/${id}`);
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assets'] });
      toast.success(`Successfully deleted ${selectedIds.length} assets`);
      setSelectedIds([]);
      setIsDeleteDialogOpen(false);
    },
    onError: (err: any) => {
      toast.error(`Failed to delete assets: ${err.message}`);
    }
  });

  const filteredAssets = useMemo(() => {
    if (!assets) return [];
    return assets.filter((asset: any) => 
      asset.hostname.toLowerCase().includes(search.toLowerCase()) ||
      asset.serial_number.toLowerCase().includes(search.toLowerCase()) ||
      asset.ip_address?.toLowerCase().includes(search.toLowerCase())
    );
  }, [assets, search]);

  const toggleSelectAll = () => {
    if (selectedIds.length === filteredAssets.length) {
      setSelectedIds([]);
    } else {
      setSelectedIds(filteredAssets.map((a: any) => a.id));
    }
  };

  const toggleSelect = (id: string) => {
    if (selectedIds.includes(id)) {
      setSelectedIds(selectedIds.filter(i => i !== id));
    } else {
      setSelectedIds([...selectedIds, id]);
    }
  };

  const getDeviceIcon = (type: string) => {
    switch (type?.toUpperCase()) {
      case 'LAPTOP': return <Laptop className="h-4 w-4" />;
      case 'SERVER': return <Server className="h-4 w-4" />;
      case 'MOBILE': return <Smartphone className="h-4 w-4" />;
      default: return <Monitor className="h-4 w-4" />;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status?.toUpperCase()) {
      case 'ONLINE': return <Badge className="bg-green-500/10 text-green-500 border-green-500/20 hover:bg-green-500/20">Online</Badge>;
      case 'OFFLINE': return <Badge variant="secondary" className="bg-slate-500/10 text-slate-500 border-slate-500/20">Offline</Badge>;
      case 'PENDING_APPROVAL': return <Badge variant="outline" className="bg-blue-500/10 text-blue-500 border-blue-500/20 animate-pulse">Pending Approval</Badge>;
      case 'MAINTENANCE': return <Badge variant="outline" className="bg-amber-500/10 text-amber-500 border-amber-500/20">Maintenance</Badge>;
      case 'RETIRED': return <Badge variant="destructive" className="bg-red-500/10 text-red-500 border-red-500/20">Retired</Badge>;
      default: return <Badge variant="outline">{status}</Badge>;
    }
  };

  if (error) return <div className="p-8 text-red-500">Error loading assets: {(error as any).message}</div>;

  return (
    <div className="p-8 space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-4xl font-black tracking-tighter text-foreground flex items-center gap-3">
            <HardDrive className="h-10 w-10 text-primary" />
            Asset <span className="text-primary">Inventory</span>
          </h1>
          <p className="text-muted-foreground font-medium mt-1">Manage and track all IT hardware assets across the organization.</p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" className="rounded-xl font-bold gap-2">
            <Download className="h-4 w-4" /> Export
          </Button>
          <Button className="rounded-xl font-bold gap-2 shadow-lg shadow-primary/20" onClick={() => navigate('/assets/new')}>
            <Plus className="h-4 w-4" /> Add Asset
          </Button>
        </div>
      </div>

      {/* Stats Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { label: 'Total Assets', value: assets?.length || 0, icon: HardDrive, color: 'text-blue-500' },
          { label: 'Online Now', value: assets?.filter((a: any) => a.status === 'ONLINE').length || 0, icon: ShieldCheck, color: 'text-green-500' },
          { label: 'Critical Alerts', value: 3, icon: ShieldAlert, color: 'text-red-500' },
          { label: 'Network Nodes', value: 12, icon: Network, color: 'text-purple-500' },
        ].map((stat, i) => (
          <Card key={i} className="bg-card/50 backdrop-blur-sm border-white/5 rounded-2xl overflow-hidden group hover:border-primary/20 transition-all">
            <CardContent className="p-6 flex items-center justify-between">
              <div>
                <p className="text-xs font-bold uppercase tracking-widest text-muted-foreground">{stat.label}</p>
                <p className="text-3xl font-black mt-1">{stat.value}</p>
              </div>
              <div className={`h-12 w-12 rounded-2xl bg-muted/50 flex items-center justify-center group-hover:scale-110 transition-transform ${stat.color}`}>
                <stat.icon className="h-6 w-6" />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Toolbar */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="bg-card/30 border border-white/5 p-1 rounded-xl mb-6">
          <TabsTrigger value="all" className="rounded-lg font-bold px-6">All Assets</TabsTrigger>
          <TabsTrigger value="pending" className="rounded-lg font-bold px-6 flex items-center gap-2">
            Pending Approval
            {assets?.filter((a: any) => a.status === 'PENDING_APPROVAL').length > 0 && (
              <Badge variant="secondary" className="h-5 w-5 p-0 flex items-center justify-center rounded-full text-[10px]">
                {assets?.filter((a: any) => a.status === 'PENDING_APPROVAL').length}
              </Badge>
            )}
          </TabsTrigger>
        </TabsList>

        <div className="flex flex-col md:flex-row items-center justify-between gap-4 bg-card/30 p-4 rounded-2xl border border-white/5 mb-6">
        <div className="flex items-center gap-4 w-full md:w-auto">
          <div className="relative w-full md:w-80">
            <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
            <Input 
              placeholder="Search by hostname, serial, IP..." 
              className="pl-10 bg-background/50 border-white/5 rounded-xl h-10 focus:ring-primary"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <Button variant="outline" size="icon" className="rounded-xl border-white/5">
            <Filter className="h-4 w-4" />
          </Button>
        </div>

        {selectedIds.length > 0 && (
          <div className="flex items-center gap-2 animate-in slide-in-from-right-4">
            <span className="text-xs font-bold text-primary uppercase tracking-widest mr-2">{selectedIds.length} Selected</span>
            <Button variant="outline" size="sm" className="rounded-lg h-8 text-xs font-bold border-white/5">Update Status</Button>
            <Button variant="destructive" size="sm" className="rounded-lg h-8 text-xs font-bold" onClick={() => setIsDeleteDialogOpen(true)}>
              <Trash2 className="h-3 w-3 mr-1" /> Delete
            </Button>
          </div>
        )}
      </div>

      {/* Table */}
      <Card className="border-white/5 bg-card/30 backdrop-blur-sm rounded-2xl overflow-hidden">
        <Table>
          <TableHeader className="bg-muted/50">
            <TableRow className="hover:bg-transparent border-white/5">
              <TableHead className="w-12">
                <Checkbox 
                  checked={selectedIds.length === filteredAssets.length && filteredAssets.length > 0}
                  onCheckedChange={toggleSelectAll}
                />
              </TableHead>
              <TableHead className="text-xs font-bold uppercase tracking-widest">Device Info</TableHead>
              <TableHead className="text-xs font-bold uppercase tracking-widest">Status</TableHead>
              <TableHead className="text-xs font-bold uppercase tracking-widest">Network</TableHead>
              <TableHead className="text-xs font-bold uppercase tracking-widest">User / Dept</TableHead>
              <TableHead className="text-xs font-bold uppercase tracking-widest">Last Ingest</TableHead>
              <TableHead className="w-12"></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <TableRow key={i} className="border-white/5">
                  <TableCell><Skeleton className="h-4 w-4 rounded" /></TableCell>
                  <TableCell>
                    <div className="flex items-center gap-3">
                      <Skeleton className="h-10 w-10 rounded-xl" />
                      <div className="space-y-1">
                        <Skeleton className="h-4 w-32" />
                        <Skeleton className="h-3 w-24" />
                      </div>
                    </div>
                  </TableCell>
                  <TableCell><Skeleton className="h-6 w-20 rounded-full" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-24" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-32" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-24" /></TableCell>
                  <TableCell><Skeleton className="h-8 w-8 rounded-lg" /></TableCell>
                </TableRow>
              ))
            ) : filteredAssets.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} className="h-64 text-center">
                  <div className="flex flex-col items-center justify-center text-muted-foreground">
                    <HardDrive className="h-12 w-12 mb-4 opacity-20" />
                    <p className="font-bold text-lg">No assets found</p>
                    <p className="text-sm">Try adjusting your search or filters.</p>
                  </div>
                </TableCell>
              </TableRow>
            ) : (
              filteredAssets.map((asset: any) => (
                <TableRow key={asset.id} className="hover:bg-white/5 transition-colors border-white/5 group">
                  <TableCell>
                    <Checkbox 
                      checked={selectedIds.includes(asset.id)}
                      onCheckedChange={() => toggleSelect(asset.id)}
                    />
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-3">
                      <div className="h-10 w-10 rounded-xl bg-primary/10 flex items-center justify-center text-primary group-hover:scale-110 transition-transform">
                        {getDeviceIcon(asset.device_type)}
                      </div>
                      <div>
                        <p className="font-bold text-sm leading-none">{asset.hostname}</p>
                        <p className="text-[10px] text-muted-foreground font-medium mt-1 uppercase tracking-wider">{asset.serial_number}</p>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    {getStatusBadge(asset.status)}
                  </TableCell>
                  <TableCell>
                    <div className="space-y-1">
                      <p className="text-xs font-bold">{asset.ip_address || 'N/A'}</p>
                      <p className="text-[10px] text-muted-foreground font-mono">{asset.mac_address || 'No MAC'}</p>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="space-y-1">
                      <p className="text-xs font-bold">{asset.assigned_to_name || 'Unassigned'}</p>
                      <p className="text-[10px] text-muted-foreground uppercase tracking-widest">{asset.department_name || 'IT Dept'}</p>
                    </div>
                  </TableCell>
                  <TableCell>
                    <p className="text-xs text-muted-foreground font-medium">
                      {asset.last_seen ? new Date(asset.last_seen).toLocaleDateString() : 'Never'}
                    </p>
                  </TableCell>
                  <TableCell>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="icon" className="rounded-lg hover:bg-white/10">
                          <MoreVertical className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end" className="w-48">
                        <DropdownMenuLabel>Actions</DropdownMenuLabel>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem onClick={() => navigate(`/assets/${asset.id}`)}>
                          <ExternalLink className="mr-2 h-4 w-4" /> View Details
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => navigate(`/assets/${asset.id}/edit`)}>
                          <Edit className="mr-2 h-4 w-4" /> Edit Asset
                        </DropdownMenuItem>
                        {asset.status === 'PENDING_APPROVAL' && (
                          <DropdownMenuItem className="text-blue-500 focus:text-blue-500" onClick={() => approveMutation.mutate(asset.id)}>
                            <ShieldCheck className="mr-2 h-4 w-4" /> Approve Device
                          </DropdownMenuItem>
                        )}
                        <DropdownMenuItem className="text-red-500 focus:text-red-500" onClick={() => {
                          setSelectedIds([asset.id]);
                          setIsDeleteDialogOpen(true);
                        }}>
                          <Trash2 className="mr-2 h-4 w-4" /> Delete
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </Card>
      </Tabs>

      {/* Delete Confirmation Dialog */}
      <Dialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <DialogContent className="bg-slate-950 border-white/10">
          <DialogHeader>
            <DialogTitle className="text-2xl font-black tracking-tighter text-white">Confirm Deletion</DialogTitle>
            <DialogDescription className="text-slate-400 font-medium">
              Are you sure you want to delete {selectedIds.length} selected asset(s)? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="gap-2 sm:gap-0">
            <Button variant="ghost" className="rounded-xl font-bold" onClick={() => setIsDeleteDialogOpen(false)}>Cancel</Button>
            <Button variant="destructive" className="rounded-xl font-bold" onClick={() => deleteMutation.mutate(selectedIds)} disabled={deleteMutation.isPending}>
              {deleteMutation.isPending ? 'Deleting...' : 'Confirm Delete'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default AssetListPage;
