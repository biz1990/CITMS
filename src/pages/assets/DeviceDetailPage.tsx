import React, { useState, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { 
  Tabs, 
  TabsContent, 
  TabsList, 
  TabsTrigger 
} from '@/components/ui/tabs';
import { 
  Card, 
  CardContent, 
  CardHeader, 
  CardTitle, 
  CardDescription 
} from '@/components/ui/card';
import { 
  ArrowLeft, 
  Monitor, 
  Network, 
  Package, 
  Cpu, 
  Wrench, 
  ShieldAlert,
  History
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import apiClient from '@/api/client';

// Tab Components (to be created)
import DeviceGeneralTab from '@/components/assets/DeviceGeneralTab';
import DeviceConnectionsTab from '@/components/assets/DeviceConnectionsTab';
import DeviceSoftwareTab from '@/components/assets/DeviceSoftwareTab';
import DeviceComponentsTab from '@/components/assets/DeviceComponentsTab';
import DeviceMaintenanceTab from '@/components/assets/DeviceMaintenanceTab';

const DeviceDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('general');

  // Fetch Device Data
  const { data: device, isLoading, error } = useQuery({
    queryKey: ['device', id],
    queryFn: async () => {
      const response = await apiClient.get(`/devices/${id}`);
      return response.data;
    },
    enabled: !!id,
  });

  if (isLoading) return <div className="flex h-screen items-center justify-center">Loading device details...</div>;
  if (error) return <div className="p-8 text-red-500">Error loading device: {(error as any).message}</div>;
  if (!device) return <div className="p-8">Device not found</div>;

  return (
    <div className="container mx-auto p-6 space-y-6 animate-in fade-in duration-500">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => navigate('/assets')}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
              <Monitor className="h-8 w-8 text-primary" />
              {device.hostname}
            </h1>
            <div className="flex items-center gap-2 mt-1">
              <Badge variant={device.status === 'ONLINE' ? 'default' : 'secondary'}>
                {device.status}
              </Badge>
              <span className="text-sm text-muted-foreground">SN: {device.serial_number}</span>
              {device.invalid_serial && (
                <Badge variant="destructive" className="animate-pulse">Invalid Serial</Badge>
              )}
              {device.alternative_macs && device.alternative_macs.length > 1 && (
                <Badge variant="outline" className="border-orange-500 text-orange-600">MAC Changed</Badge>
              )}
              {device.components?.some((c: any) => c.new_peripheral) && (
                <Badge variant="outline" className="border-blue-500 text-blue-600">New Peripheral</Badge>
              )}
            </div>
          </div>
        </div>
        <div className="flex gap-2 items-center">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-muted/50 border text-xs font-medium">
            <div className={`h-2 w-2 rounded-full ${
              device.last_seen && (new Date().getTime() - new Date(device.last_seen).getTime() < 5 * 60 * 1000)
                ? 'bg-green-500 animate-pulse'
                : 'bg-red-500'
            }`} />
            RustDesk: {device.last_seen && (new Date().getTime() - new Date(device.last_seen).getTime() < 5 * 60 * 1000) ? 'Online' : 'Offline'}
          </div>
          <Button variant="outline" onClick={() => navigate(`/devices/${id}/remote-session`)}>
            <Network className="mr-2 h-4 w-4" /> Remote Control
          </Button>
          <Button>Edit Device</Button>
        </div>
      </div>

      {/* Main Content Tabs */}
      <Tabs defaultValue="general" className="w-full" onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-5 lg:w-[600px]">
          <TabsTrigger value="general" className="flex items-center gap-2">
            <Monitor className="h-4 w-4" /> <span className="hidden sm:inline">General</span>
          </TabsTrigger>
          <TabsTrigger value="connections" className="flex items-center gap-2">
            <Network className="h-4 w-4" /> <span className="hidden sm:inline">Connections</span>
          </TabsTrigger>
          <TabsTrigger value="software" className="flex items-center gap-2">
            <ShieldAlert className="h-4 w-4" /> <span className="hidden sm:inline">Software</span>
          </TabsTrigger>
          <TabsTrigger value="components" className="flex items-center gap-2">
            <Cpu className="h-4 w-4" /> <span className="hidden sm:inline">Components</span>
          </TabsTrigger>
          <TabsTrigger value="maintenance" className="flex items-center gap-2">
            <Wrench className="h-4 w-4" /> <span className="hidden sm:inline">Maintenance</span>
          </TabsTrigger>
        </TabsList>

        <div className="mt-6">
          <TabsContent value="general">
            <DeviceGeneralTab device={device} />
          </TabsContent>
          
          <TabsContent value="connections">
            <DeviceConnectionsTab deviceId={id!} />
          </TabsContent>
          
          <TabsContent value="software">
            <DeviceSoftwareTab deviceId={id!} />
          </TabsContent>
          
          <TabsContent value="components">
            <DeviceComponentsTab deviceId={id!} />
          </TabsContent>
          
          <TabsContent value="maintenance">
            <DeviceMaintenanceTab deviceId={id!} />
          </TabsContent>
        </div>
      </Tabs>
    </div>
  );
};

export default DeviceDetailPage;
