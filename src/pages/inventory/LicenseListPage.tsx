import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { licenseApi } from '@/api/license';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Progress } from '@/components/ui/progress';
import { AlertTriangle, CheckCircle2, ShieldAlert } from 'lucide-react';
import { format } from 'date-fns';

const LicenseListPage = () => {
  const { data: licenses, isLoading, error } = useQuery({
    queryKey: ['licenses'],
    queryFn: licenseApi.list,
  });

  if (error) {
    return (
      <div className="flex h-[400px] items-center justify-center text-destructive">
        Error loading licenses. Please try again later.
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Software Licenses</h1>
          <p className="text-muted-foreground">
            Manage and monitor software compliance across the organization.
          </p>
        </div>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>License Type</TableHead>
              <TableHead>Total Seats</TableHead>
              <TableHead>Usage</TableHead>
              <TableHead>Compliance Status</TableHead>
              <TableHead>Expiration</TableHead>
              <TableHead>Created At</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <TableRow key={i}>
                  <TableCell><Skeleton className="h-4 w-[120px]" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-[60px]" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-[150px]" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-[100px]" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-[100px]" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-[100px]" /></TableCell>
                </TableRow>
              ))
            ) : licenses?.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} className="h-24 text-center">
                  No licenses found.
                </TableCell>
              </TableRow>
            ) : (
              licenses?.map((license) => {
                const isViolation = license.used_seats > license.total_seats;
                const isNearLimit = license.used_seats >= license.total_seats * 0.9;
                const percentage = Math.min(100, (license.used_seats / license.total_seats) * 100);
                
                return (
                  <TableRow key={license.id} className={isViolation ? "bg-destructive/10 hover:bg-destructive/20" : ""}>
                    <TableCell className="font-medium">{license.type}</TableCell>
                    <TableCell>{license.total_seats}</TableCell>
                    <TableCell>
                      <div className="flex flex-col gap-1 w-[150px]">
                        <div className="flex justify-between text-[10px]">
                          <span>{license.used_seats} used</span>
                          <span>{Math.round(percentage)}%</span>
                        </div>
                        <Progress value={percentage} className="h-1.5" />
                      </div>
                    </TableCell>
                    <TableCell>
                      {isViolation ? (
                        <Badge variant="destructive" className="flex w-fit items-center gap-1">
                          <ShieldAlert className="h-3 w-3" />
                          Violation
                        </Badge>
                      ) : isNearLimit ? (
                        <Badge variant="outline" className="flex w-fit items-center gap-1 border-yellow-500 text-yellow-500">
                          <AlertTriangle className="h-3 w-3" />
                          Near Limit
                        </Badge>
                      ) : (
                        <Badge variant="outline" className="flex w-fit items-center gap-1 border-green-500 text-green-500">
                          <CheckCircle2 className="h-3 w-3" />
                          Compliant
                        </Badge>
                      )}
                    </TableCell>
                    <TableCell>
                      {license.expire_date ? format(new Date(license.expire_date), 'MMM dd, yyyy') : 'N/A'}
                    </TableCell>
                    <TableCell>
                      {format(new Date(license.created_at), 'MMM dd, yyyy')}
                    </TableCell>
                  </TableRow>
                );
              })
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
};

export default LicenseListPage;
