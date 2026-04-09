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
  History,
  QrCode,
  Image as ImageIcon
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import apiClient from '@/api/client';

import QRCodeDialog from '@/components/assets/QRCodeDialog';

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
  const [isQRUIOpen, setIsQRUIOpen] = useState(false);
  const [previewData, setPreviewData] = useState<any>(null);
  const [isPreviewLoading, setIsPreviewLoading] = useState(false);

  // Fetch Preview
  const fetchPreview = async () => {
    setIsPreviewLoading(true);
    try {
      const res = await apiClient.get(`/devices/${id}/preview`);
      setPreviewData(res.data);
    } catch (err) {
      console.error('Failed to fetch preview', err);
    } finally {
      setIsPreviewLoading(false);
    }
  };

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
            </div>
          </div>
        </div>
        <div className="flex gap-2 items-center">
          <Button variant="outline" onClick={() => setIsQRUIOpen(true)}>
            <QrCode className="mr-2 h-4 w-4" /> Print QR
          </Button>
          <Button variant="outline" onClick={() => navigate(`/devices/${id}/remote-session`)}>
            <Network className="mr-2 h-4 w-4" /> Remote Control
          </Button>
          <Button>Edit Device</Button>
        </div>
      </div>

      {/* Real-time Preview Section */}
      {device.status === 'ONLINE' && (
        <Card className="border-primary/20 bg-primary/5 overflow-hidden">
          <CardHeader className="py-3 px-4 flex flex-row items-center justify-between border-b bg-card/50">
            <div className="flex items-center gap-2">
              <ImageIcon className="h-4 w-4 text-primary" />
              <CardTitle className="text-sm font-bold">Real-time Desktop Preview</CardTitle>
            </div>
            <Button size="sm" variant="ghost" className="h-7 text-[10px]" onClick={fetchPreview} disabled={isPreviewLoading}>
              {isPreviewLoading ? 'Refreshing...' : 'Refresh Preview'}
            </Button>
          </CardHeader>
          <CardContent className="p-0 flex items-center justify-center min-h-[200px] relative">
            {previewData?.preview_url ? (
              <img 
                src={previewData.preview_url} 
                alt="Desktop Preview" 
                className="w-full h-auto max-h-[400px] object-contain animate-in fade-in zoom-in-95"
              />
            ) : (
              <div className="flex flex-col items-center gap-2 py-12 text-muted-foreground">
                <div className="h-10 w-10 rounded-full bg-muted flex items-center justify-center">
                  <Monitor className="h-5 w-5 opacity-20" />
                </div>
                <p className="text-xs font-medium">Click "Refresh Preview" to view live desktop</p>
              </div>
            )}
          </CardContent>
        </Card>
      )}

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

      <QRCodeDialog 
        isOpen={isQRUIOpen} 
        onClose={() => setIsQRUIOpen(false)} 
        data={`CITMS:ASSET:${device.asset_tag || device.id}`}
        label={device.asset_tag || device.hostname}
      />
    </div>
  );
};

export default DeviceDetailPage;
