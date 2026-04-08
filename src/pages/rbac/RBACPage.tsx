import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  Card, CardContent, CardHeader, CardTitle, CardDescription 
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from '@/components/ui/table';
import { 
  ShieldCheck, 
  Plus, 
  Search, 
  Filter,
  Edit2,
  Trash2,
  Users,
  Lock,
  CheckCircle2,
  XCircle
} from 'lucide-react';
import apiClient from '@/api/client';
import { toast } from 'sonner';

const RBACPage: React.FC = () => {
  const { data: roles, isLoading, refetch } = useQuery({
    queryKey: ['rbac-roles'],
    queryFn: async () => {
      const response = await apiClient.get('/auth/roles');
      return response.data;
    },
  });

  const handleDelete = async (id: string) => {
    try {
      await apiClient.delete(`/auth/roles/${id}`);
      toast.success('Role deleted');
      refetch();
    } catch (error) {
      toast.error('Failed to delete role');
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6 animate-in fade-in duration-500">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
            <ShieldCheck className="h-8 w-8 text-primary" />
            Roles & Permissions
          </h1>
          <p className="text-muted-foreground">Manage user roles, module-level permissions, and access control policies.</p>
        </div>
        <Button>
          <Plus className="h-4 w-4 mr-2" /> Create New Role
        </Button>
      </div>

      <div className="flex flex-col md:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input 
            className="w-full pl-10 pr-4 py-2 rounded-lg border bg-background focus:ring-2 focus:ring-primary/20 outline-none transition-all"
            placeholder="Search roles by name or description..."
          />
        </div>
        <Button variant="outline">
          <Filter className="h-4 w-4 mr-2" /> Filters
        </Button>
      </div>

      <Tabs defaultValue="roles" className="w-full">
        <TabsList className="grid w-[400px] grid-cols-2">
          <TabsTrigger value="roles">Role Cards</TabsTrigger>
          <TabsTrigger value="matrix">Permission Matrix</TabsTrigger>
        </TabsList>

        <div className="mt-6">
          <TabsContent value="roles">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {isLoading ? (
                Array.from({ length: 3 }).map((_, i) => (
                  <Card key={i} className="animate-pulse h-64" />
                ))
              ) : roles?.length === 0 ? (
                <div className="col-span-full text-center py-20 text-muted-foreground italic border-2 border-dashed rounded-xl">
                  <ShieldCheck className="h-12 w-12 mx-auto mb-4 opacity-10" />
                  No roles defined.
                </div>
              ) : roles?.map((role: any) => (
                <Card key={role.id} className="hover:shadow-lg transition-all group border-l-4 border-l-primary">
                  <CardHeader className="pb-2">
                    <div className="flex items-start justify-between">
                      <div className="h-10 w-10 rounded-xl bg-primary/10 flex items-center justify-center text-primary">
                        <Lock className="h-5 w-5" />
                      </div>
                      <Badge variant="secondary" className="text-[10px]">{role.user_count || 0} Users</Badge>
                    </div>
                    <CardTitle className="mt-4 text-lg">{role.name}</CardTitle>
                    <CardDescription className="text-xs line-clamp-2">{role.description}</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex flex-wrap gap-1">
                      {role.permissions?.slice(0, 5).map((perm: string) => (
                        <Badge key={perm} variant="outline" className="text-[8px] px-1 h-4 bg-muted/50">{perm}</Badge>
                      ))}
                      {role.permissions?.length > 5 && (
                        <Badge variant="outline" className="text-[8px] px-1 h-4 bg-muted/50">+{role.permissions.length - 5} more</Badge>
                      )}
                    </div>
                    <div className="pt-4 border-t flex items-center justify-between">
                      <Button variant="ghost" size="sm" className="h-8 text-[10px] text-muted-foreground hover:text-primary">
                        <Edit2 className="h-3 w-3 mr-1" /> Edit Role
                      </Button>
                      <Button variant="ghost" size="icon" className="h-8 w-8 text-red-500 hover:text-red-600 hover:bg-red-50" onClick={() => handleDelete(role.id)}>
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="matrix">
            <Card>
              <CardHeader>
                <CardTitle>Permission Matrix</CardTitle>
                <CardDescription>Cross-reference roles with specific module permissions.</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="rounded-md border overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow className="bg-muted/50">
                        <TableHead className="w-[200px]">Permission</TableHead>
                        {roles?.map((role: any) => (
                          <TableHead key={role.id} className="text-center min-w-[100px]">{role.name}</TableHead>
                        ))}
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {[
                        'dashboard.view',
                        'asset.view',
                        'asset.edit',
                        'asset.delete',
                        'user.view',
                        'ticket.view',
                        'ticket.manage',
                        'procurement.view',
                        'procurement.approve',
                        'inventory.view',
                        'workflow.view',
                        'report.export',
                        'settings.manage'
                      ].map((perm) => (
                        <TableRow key={perm} className="hover:bg-muted/30 transition-colors">
                          <TableCell className="font-mono text-[10px] font-bold">{perm}</TableCell>
                          {roles?.map((role: any) => (
                            <TableCell key={role.id} className="text-center">
                              {role.permissions?.includes(perm) ? (
                                <CheckCircle2 className="h-4 w-4 text-green-500 mx-auto" />
                              ) : (
                                <XCircle className="h-4 w-4 text-muted-foreground/30 mx-auto" />
                              )}
                            </TableCell>
                          ))}
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </div>
      </Tabs>
    </div>
  );
};

export default RBACPage;
