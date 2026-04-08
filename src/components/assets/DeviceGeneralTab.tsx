import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Monitor, 
  Cpu, 
  HardDrive, 
  MemoryStick, 
  Globe, 
  Calendar, 
  User, 
  Tag, 
  Hash,
  ShieldCheck,
  Settings
} from 'lucide-react';
import { format } from 'date-fns';

interface DeviceGeneralTabProps {
  device: any;
}

const DeviceGeneralTab: React.FC<DeviceGeneralTabProps> = ({ device }) => {
  const specs = [
    { label: 'Hostname', value: device.hostname, icon: Monitor },
    { label: 'Serial Number', value: device.serial_number, icon: Hash },
    { label: 'Type', value: device.device_type, icon: Tag },
    { label: 'Status', value: device.status, icon: ShieldCheck },
    { label: 'IP Address', value: device.ip_address || 'N/A', icon: Globe },
    { label: 'MAC Address', value: device.mac_address || 'N/A', icon: Globe },
    { label: 'Operating System', value: device.os_name || 'N/A', icon: Monitor },
    { label: 'CPU', value: device.cpu_model || 'N/A', icon: Cpu },
    { label: 'RAM', value: `${device.ram_gb || 0} GB`, icon: MemoryStick },
    { label: 'Disk', value: `${device.disk_gb || 0} GB`, icon: HardDrive },
    { label: 'Last Seen', value: device.last_seen ? format(new Date(device.last_seen), 'PPP p') : 'Never', icon: Calendar },
    { label: 'Assigned To', value: device.assigned_to_id || 'Unassigned', icon: User },
  ];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {specs.map((spec, index) => (
          <Card key={index} className="hover:shadow-md transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {spec.label}
              </CardTitle>
              <spec.icon className="h-4 w-4 text-primary" />
            </CardHeader>
            <CardContent>
              <div className="text-lg font-semibold truncate">{spec.value}</div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Peripheral Devices Section */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Tag className="h-5 w-5 text-primary" />
            Peripheral Devices & Expansion Cards
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {device.components?.filter((c: any) => !c.is_internal || ['SCANNER', 'PRINTER', 'PCI_CARD', 'PCIE_CARD'].includes(c.component_type)).map((comp: any) => (
              <div key={comp.id} className="flex items-center gap-3 p-3 rounded-lg border bg-muted/30">
                <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center text-primary">
                  {comp.component_type.includes('SCANNER') ? <Tag className="h-5 w-5" /> : <Settings className="h-5 w-5" />}
                </div>
                <div>
                  <p className="text-sm font-bold">{comp.model || comp.component_type}</p>
                  <p className="text-[10px] text-muted-foreground">{comp.manufacturer} • {comp.serial_number || 'No SN'}</p>
                  {comp.new_peripheral && <Badge className="text-[8px] h-3 px-1 mt-1" variant="outline">New</Badge>}
                </div>
              </div>
            ))}
            {(!device.components || device.components.filter((c: any) => !c.is_internal || ['SCANNER', 'PRINTER', 'PCI_CARD', 'PCIE_CARD'].includes(c.component_type)).length === 0) && (
              <p className="text-sm text-muted-foreground italic col-span-full py-4 text-center border-2 border-dashed rounded-lg">
                No peripheral devices or expansion cards detected.
              </p>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default DeviceGeneralTab;
