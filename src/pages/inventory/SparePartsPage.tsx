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
  Package, 
  Plus, 
  AlertTriangle, 
  CheckCircle2, 
  Search, 
  Filter,
  ArrowRightCircle
} from 'lucide-react';
import apiClient from '@/api/client';
import { toast } from 'sonner';

const SparePartsPage: React.FC = () => {
  const { data: parts, isLoading } = useQuery({
    queryKey: ['spare-parts'],
    queryFn: async () => {
      const response = await apiClient.get('/inventory/spare-parts');
      return response.data;
    },
  });

  return (
    <div className="container mx-auto p-6 space-y-6 animate-in fade-in duration-500">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
            <Package className="h-8 w-8 text-primary" />
            Spare Parts Inventory
          </h1>
          <p className="text-muted-foreground">Manage hardware components, spare parts, and stock levels.</p>
        </div>
        <Button>
          <Plus className="h-4 w-4 mr-2" /> Add Spare Part
        </Button>
      </div>

      <div className="flex flex-col md:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input 
            className="w-full pl-10 pr-4 py-2 rounded-lg border bg-background focus:ring-2 focus:ring-primary/20 outline-none transition-all"
            placeholder="Search parts by name, category, or manufacturer..."
          />
        </div>
        <Button variant="outline">
          <Filter className="h-4 w-4 mr-2" /> Filters
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Inventory List</CardTitle>
          <CardDescription>Monitor stock levels and reorder points.</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Part Name</TableHead>
                <TableHead>Category</TableHead>
                <TableHead>Manufacturer</TableHead>
                <TableHead>In Stock</TableHead>
                <TableHead>Min Quantity</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                <TableRow><TableCell colSpan={7} className="text-center py-8">Loading...</TableCell></TableRow>
              ) : parts?.length === 0 ? (
                <TableRow><TableCell colSpan={7} className="text-center py-8">No parts found.</TableCell></TableRow>
              ) : parts?.map((part: any) => {
                const isLowStock = part.quantity <= part.min_quantity;
                return (
                  <TableRow key={part.id}>
                    <TableCell className="font-medium">{part.name}</TableCell>
                    <TableCell>{part.category}</TableCell>
                    <TableCell>{part.manufacturer}</TableCell>
                    <TableCell className={isLowStock ? "text-red-500 font-bold" : ""}>
                      {part.quantity}
                    </TableCell>
                    <TableCell>{part.min_quantity}</TableCell>
                    <TableCell>
                      {isLowStock ? (
                        <Badge variant="destructive" className="flex w-fit items-center gap-1">
                          <AlertTriangle className="h-3 w-3" /> Low Stock
                        </Badge>
                      ) : (
                        <Badge variant="outline" className="flex w-fit items-center gap-1 border-green-500 text-green-500">
                          <CheckCircle2 className="h-3 w-3" /> In Stock
                        </Badge>
                      )}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex items-center justify-end gap-2">
                        {isLowStock && (
                          <Button variant="outline" size="sm" className="h-8 text-xs border-red-200 text-red-600 hover:bg-red-50" onClick={() => toast.info(`Reorder request sent for ${part.name}`)}>
                            Reorder
                          </Button>
                        )}
                        <Button variant="ghost" size="icon">
                          <ArrowRightCircle className="h-5 w-5 hover:text-primary transition-colors" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
};

export default SparePartsPage;
