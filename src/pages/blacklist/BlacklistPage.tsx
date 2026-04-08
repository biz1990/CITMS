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
  ShieldX, 
  Plus, 
  Search, 
  Filter,
  Trash2,
  AlertCircle,
  Monitor,
  Package
} from 'lucide-react';
import apiClient from '@/api/client';
import { format } from 'date-fns';
import { toast } from 'sonner';

const BlacklistPage: React.FC = () => {
  const { data: blacklist, isLoading, refetch } = useQuery({
    queryKey: ['blacklist'],
    queryFn: async () => {
      const response = await apiClient.get('/blacklist');
      return response.data;
    },
  });

  const handleDelete = async (id: string) => {
    try {
      await apiClient.delete(`/blacklist/${id}`);
      toast.success('Blacklist entry removed');
      refetch();
    } catch (error) {
      toast.error('Failed to remove blacklist entry');
    }
  };

  const serialBlacklist = blacklist?.filter((b: any) => b.type === 'SERIAL') || [];
  const softwareBlacklist = blacklist?.filter((b: any) => b.type === 'SOFTWARE') || [];

  return (
    <div className="container mx-auto p-6 space-y-6 animate-in fade-in duration-500">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
            <ShieldX className="h-8 w-8 text-primary" />
            System Blacklist
          </h1>
          <p className="text-muted-foreground">Manage prohibited hardware serial numbers and software applications.</p>
        </div>
        <Button variant="destructive">
          <Plus className="h-4 w-4 mr-2" /> Add Blacklist
        </Button>
      </div>

      <Tabs defaultValue="serial" className="w-full">
        <TabsList className="grid w-full grid-cols-2 lg:w-[400px]">
          <TabsTrigger value="serial" className="flex items-center gap-2">
            <Monitor className="h-4 w-4" /> Serial Blacklist
          </TabsTrigger>
          <TabsTrigger value="software" className="flex items-center gap-2">
            <Package className="h-4 w-4" /> Software Blacklist
          </TabsTrigger>
        </TabsList>

        <div className="mt-6">
          <TabsContent value="serial">
            <Card>
              <CardHeader>
                <CardTitle>Prohibited Serial Numbers</CardTitle>
                <CardDescription>Devices with these serials will be flagged as unauthorized.</CardDescription>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Serial Number</TableHead>
                      <TableHead>Reason</TableHead>
                      <TableHead>Added By</TableHead>
                      <TableHead>Date</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {isLoading ? (
                      <TableRow><TableCell colSpan={5} className="text-center py-8">Loading...</TableCell></TableRow>
                    ) : serialBlacklist.length === 0 ? (
                      <TableRow><TableCell colSpan={5} className="text-center py-8">No serials blacklisted.</TableCell></TableRow>
                    ) : serialBlacklist.map((item: any) => (
                      <TableRow key={item.id}>
                        <TableCell className="font-mono font-bold text-red-600">{item.value}</TableCell>
                        <TableCell>{item.reason}</TableCell>
                        <TableCell>{item.added_by_name}</TableCell>
                        <TableCell>{format(new Date(item.created_at), 'MMM dd, yyyy')}</TableCell>
                        <TableCell className="text-right">
                          <Button variant="ghost" size="icon" className="text-red-500 hover:text-red-600 hover:bg-red-50" onClick={() => handleDelete(item.id)}>
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="software">
            <Card>
              <CardHeader>
                <CardTitle>Prohibited Software</CardTitle>
                <CardDescription>Applications that are not allowed to be installed on organization devices.</CardDescription>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Software Name</TableHead>
                      <TableHead>Version Range</TableHead>
                      <TableHead>Reason</TableHead>
                      <TableHead>Date</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {softwareBlacklist.map((item: any) => (
                      <TableRow key={item.id}>
                        <TableCell className="font-medium">{item.value}</TableCell>
                        <TableCell>{item.version_range || 'All'}</TableCell>
                        <TableCell>{item.reason}</TableCell>
                        <TableCell>{format(new Date(item.created_at), 'MMM dd, yyyy')}</TableCell>
                        <TableCell className="text-right">
                          <Button variant="ghost" size="icon" className="text-red-500 hover:text-red-600 hover:bg-red-50" onClick={() => handleDelete(item.id)}>
                            <Trash2 className="h-4 w-4" />
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

export default BlacklistPage;
