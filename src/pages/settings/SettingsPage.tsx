import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  Card, CardContent, CardHeader, CardTitle, CardDescription 
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Settings, 
  User, 
  Bell, 
  ShieldCheck, 
  Mail, 
  Monitor, 
  Database,
  Globe,
  Save,
  RefreshCw,
  Calendar,
  Plus
} from 'lucide-react';
import apiClient from '@/api/client';
import { toast } from 'sonner';

const SettingsPage: React.FC = () => {
  const [isSaving, setIsSaving] = React.useState(false);

  const handleSave = async () => {
    setIsSaving(true);
    try {
      // Mock save call
      await new Promise(resolve => setTimeout(resolve, 1000));
      toast.success('Settings saved successfully');
    } catch (error) {
      toast.error('Failed to save settings');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6 animate-in fade-in duration-500">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
            <Settings className="h-8 w-8 text-primary" />
            System Settings
          </h1>
          <p className="text-muted-foreground">Configure global system parameters, notifications, and integrations.</p>
        </div>
        <Button onClick={handleSave} disabled={isSaving}>
          {isSaving ? <RefreshCw className="h-4 w-4 mr-2 animate-spin" /> : <Save className="h-4 w-4 mr-2" />}
          Save Changes
        </Button>
      </div>

      <Tabs defaultValue="general" className="w-full">
        <TabsList className="grid w-full grid-cols-2 lg:w-[600px]">
          <TabsTrigger value="general" className="flex items-center gap-2">
            <Globe className="h-4 w-4" /> General
          </TabsTrigger>
          <TabsTrigger value="notifications" className="flex items-center gap-2">
            <Bell className="h-4 w-4" /> Notifications
          </TabsTrigger>
          <TabsTrigger value="holidays" className="flex items-center gap-2">
            <Calendar className="h-4 w-4" /> Holidays
          </TabsTrigger>
          <TabsTrigger value="integrations" className="flex items-center gap-2">
            <Database className="h-4 w-4" /> Integrations
          </TabsTrigger>
          <TabsTrigger value="security" className="flex items-center gap-2">
            <ShieldCheck className="h-4 w-4" /> Security
          </TabsTrigger>
        </TabsList>

        <div className="mt-6 space-y-6">
          <TabsContent value="general">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>System Information</CardTitle>
                  <CardDescription>Basic system configuration.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <label className="text-xs font-bold uppercase tracking-widest text-muted-foreground">Organization Name</label>
                    <input className="w-full p-2 rounded-lg border bg-background" defaultValue="CITMS Enterprise" />
                  </div>
                  <div className="space-y-2">
                    <label className="text-xs font-bold uppercase tracking-widest text-muted-foreground">System URL</label>
                    <input className="w-full p-2 rounded-lg border bg-background" defaultValue="https://citms.internal" />
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardHeader>
                  <CardTitle>Regional Settings</CardTitle>
                  <CardDescription>Timezone and language configuration.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <label className="text-xs font-bold uppercase tracking-widest text-muted-foreground">Timezone</label>
                    <select className="w-full p-2 rounded-lg border bg-background">
                      <option>UTC (GMT+0)</option>
                      <option>Asia/Ho_Chi_Minh (GMT+7)</option>
                      <option>America/New_York (GMT-5)</option>
                    </select>
                  </div>
                  <div className="space-y-2">
                    <label className="text-xs font-bold uppercase tracking-widest text-muted-foreground">Language</label>
                    <select className="w-full p-2 rounded-lg border bg-background">
                      <option>English (US)</option>
                      <option>Vietnamese (VN)</option>
                    </select>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="notifications">
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Email Configuration (SMTP)</CardTitle>
                  <CardDescription>Configure the system email server for alerts and notifications.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <label className="text-xs font-bold uppercase tracking-widest text-muted-foreground">SMTP Server</label>
                      <input className="w-full p-2 rounded-lg border bg-background" placeholder="smtp.gmail.com" />
                    </div>
                    <div className="space-y-2">
                      <label className="text-xs font-bold uppercase tracking-widest text-muted-foreground">SMTP Port</label>
                      <input className="w-full p-2 rounded-lg border bg-background" placeholder="587" />
                    </div>
                  </div>
                  <div className="pt-4 border-t flex items-center justify-between">
                    <span className="text-xs text-muted-foreground italic">Test connection before saving.</span>
                    <Button variant="outline" size="sm">Test SMTP</Button>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Alert Types</CardTitle>
                  <CardDescription>Select which events trigger system notifications.</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {[
                      'New Device Ingestion',
                      'Unauthorized Serial Detected',
                      'Blacklisted Software Installed',
                      'SLA Breach Warning',
                      'License Expiration (30 days)',
                      'License Violation (Over-usage)',
                      'Low Spare Parts Stock',
                      'Device Offline > 7 Days',
                      'New Procurement Request',
                      'Workflow Task Assigned',
                      'Remote Access Started',
                      'Critical System Error'
                    ].map((alert) => (
                      <div key={alert} className="flex items-center space-x-2 p-2 rounded-lg hover:bg-muted/50 transition-colors">
                        <input type="checkbox" id={alert} className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary" defaultChecked />
                        <label htmlFor={alert} className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                          {alert}
                        </label>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="holidays">
            <Card>
              <CardHeader>
                <CardTitle>Holiday Calendar</CardTitle>
                <CardDescription>Configure non-working days for SLA calculations.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex items-center justify-between p-4 border rounded-xl bg-muted/20">
                  <div className="flex items-center gap-3">
                    <Calendar className="h-5 w-5 text-primary" />
                    <div>
                      <p className="text-sm font-bold">New Year's Day</p>
                      <p className="text-xs text-muted-foreground">January 1, 2026</p>
                    </div>
                  </div>
                  <Button variant="ghost" size="sm" className="text-red-500">Remove</Button>
                </div>
                <div className="flex items-center justify-between p-4 border rounded-xl bg-muted/20">
                  <div className="flex items-center gap-3">
                    <Calendar className="h-5 w-5 text-primary" />
                    <div>
                      <p className="text-sm font-bold">Lunar New Year (Tet)</p>
                      <p className="text-xs text-muted-foreground">February 17-21, 2026</p>
                    </div>
                  </div>
                  <Button variant="ghost" size="sm" className="text-red-500">Remove</Button>
                </div>
                <Button variant="outline" className="w-full border-dashed">
                  <Plus className="h-4 w-4 mr-2" /> Add Holiday
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="integrations">
            <Card>
              <CardHeader>
                <CardTitle>RustDesk Configuration</CardTitle>
                <CardDescription>Configure the self-hosted RustDesk server for remote control.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <label className="text-xs font-bold uppercase tracking-widest text-muted-foreground">RustDesk Server Address</label>
                  <input className="w-full p-2 rounded-lg border bg-background" defaultValue="rustdesk.citms.internal" />
                </div>
                <div className="space-y-2">
                  <label className="text-xs font-bold uppercase tracking-widest text-muted-foreground">RustDesk Key</label>
                  <input className="w-full p-2 rounded-lg border bg-background" type="password" defaultValue="••••••••••••••••" />
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="security">
            <Card>
              <CardHeader>
                <CardTitle>Security Policies</CardTitle>
                <CardDescription>Configure authentication and access control policies.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between p-4 border rounded-xl">
                  <div>
                    <h4 className="text-sm font-bold">Two-Factor Authentication (2FA)</h4>
                    <p className="text-xs text-muted-foreground">Require 2FA for all administrative accounts.</p>
                  </div>
                  <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">ENABLED</Badge>
                </div>
                <div className="flex items-center justify-between p-4 border rounded-xl">
                  <div>
                    <h4 className="text-sm font-bold">Session Timeout</h4>
                    <p className="text-xs text-muted-foreground">Automatically logout users after inactivity.</p>
                  </div>
                  <select className="p-2 rounded-lg border bg-background text-xs">
                    <option>15 Minutes</option>
                    <option>30 Minutes</option>
                    <option>1 Hour</option>
                  </select>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </div>
      </Tabs>
    </div>
  );
};

export default SettingsPage;
