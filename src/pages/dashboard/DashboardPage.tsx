import React from 'react';
import { 
  Card, CardContent, CardHeader, CardTitle, CardDescription 
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  PieChart, Pie, Cell, ResponsiveContainer, 
  BarChart, Bar, XAxis, YAxis, Tooltip, Legend,
  LineChart, Line
} from 'recharts';
import { 
  Ticket, 
  ShieldAlert, 
  Activity, 
  HardDrive, 
  Clock, 
  CheckCircle2, 
  AlertCircle,
  ShieldCheck,
  TrendingUp,
  Users,
  Zap,
  ArrowUpRight,
  ArrowDownRight
} from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import apiClient from '@/api/client';
import { useNotifications } from '@/hooks/useNotifications';
import { formatDistanceToNow } from 'date-fns';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

const DashboardPage: React.FC = () => {
  const { notifications } = useNotifications();

  // Fetch Dashboard Stats
  const { data: stats, isLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: async () => {
      const response = await apiClient.get('/dashboard/stats');
      return response.data;
    },
    refetchInterval: 30000, // Poll every 30s as fallback
  });

  if (isLoading) return <div className="p-8 text-center animate-pulse">Loading Dashboard...</div>;

  // Prepare Chart Data
  const assetStatusData = stats?.assets?.by_status ? Object.entries(stats.assets.by_status).map(([name, value]) => ({
    name: name.replace('_', ' '),
    value
  })) : [];

  const weeklyTicketData = stats?.tickets?.weekly_count || [];

  const recentActivity = stats?.recent_activity || [];
  const timeline = stats?.timeline || [];

  return (
    <div className="container mx-auto p-6 space-y-8 animate-in fade-in duration-700">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-4xl font-extrabold tracking-tight bg-gradient-to-r from-primary to-blue-600 bg-clip-text text-transparent">
            System Overview
          </h1>
          <p className="text-muted-foreground mt-1">Real-time health and performance monitoring for CITMS 3.6.</p>
        </div>
        <div className="flex items-center gap-3 bg-muted/50 p-2 rounded-2xl border">
          <div className="h-3 w-3 rounded-full bg-green-500 animate-pulse" />
          <span className="text-xs font-bold uppercase tracking-widest">Live Monitoring Active</span>
        </div>
      </div>

      {/* Top Stats Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="relative overflow-hidden group hover:shadow-xl transition-all border-none bg-gradient-to-br from-blue-500/10 to-blue-600/5">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-bold text-blue-500 uppercase tracking-widest mb-1">Total Assets</p>
                <h3 className="text-3xl font-black">{stats?.assets?.total || 0}</h3>
              </div>
              <div className="h-12 w-12 rounded-2xl bg-blue-500/20 flex items-center justify-center text-blue-600 group-hover:scale-110 transition-transform">
                <HardDrive className="h-6 w-6" />
              </div>
            </div>
            <div className="mt-4 flex items-center gap-2 text-[10px] font-bold text-blue-600/60">
              <TrendingUp className="h-3 w-3" /> +12% from last month
            </div>
          </CardContent>
        </Card>

        <Card className="relative overflow-hidden group hover:shadow-xl transition-all border-none bg-gradient-to-br from-orange-500/10 to-orange-600/5">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-bold text-orange-500 uppercase tracking-widest mb-1">Open Tickets</p>
                <h3 className="text-3xl font-black">{stats?.tickets?.by_status?.OPEN || 0}</h3>
              </div>
              <div className="h-12 w-12 rounded-2xl bg-orange-500/20 flex items-center justify-center text-orange-600 group-hover:scale-110 transition-transform">
                <Ticket className="h-6 w-6" />
              </div>
            </div>
            <div className="mt-4 flex items-center gap-2 text-[10px] font-bold text-orange-600/60">
              <ArrowUpRight className="h-3 w-3" /> 5 new in last hour
            </div>
          </CardContent>
        </Card>

        <Card className="relative overflow-hidden group hover:shadow-xl transition-all border-none bg-gradient-to-br from-red-500/10 to-red-600/5">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-bold text-red-500 uppercase tracking-widest mb-1">SLA Breaches</p>
                <h3 className="text-3xl font-black">{stats?.tickets?.sla_breaches || 0}</h3>
              </div>
              <div className="h-12 w-12 rounded-2xl bg-red-500/20 flex items-center justify-center text-red-600 group-hover:scale-110 transition-transform">
                <ShieldAlert className="h-6 w-6" />
              </div>
            </div>
            <div className="mt-4 flex items-center gap-2 text-[10px] font-bold text-red-600/60">
              <AlertCircle className="h-3 w-3" /> Critical attention required
            </div>
          </CardContent>
        </Card>

        <Card className="relative overflow-hidden group hover:shadow-xl transition-all border-none bg-gradient-to-br from-green-500/10 to-green-600/5">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-bold text-green-500 uppercase tracking-widest mb-1">Agent Health</p>
                <h3 className="text-3xl font-black">{stats?.agent_health?.health_score || 0}%</h3>
              </div>
              <div className="h-12 w-12 rounded-2xl bg-green-500/20 flex items-center justify-center text-green-600 group-hover:scale-110 transition-transform">
                <Zap className="h-6 w-6" />
              </div>
            </div>
            <div className="mt-4 flex items-center gap-4">
              <div className="flex items-center gap-1 text-[10px] font-bold text-green-600">
                <div className="h-1.5 w-1.5 rounded-full bg-green-500" /> {stats?.agent_health?.online || 0} Online
              </div>
              <div className="flex items-center gap-1 text-[10px] font-bold text-orange-500">
                <div className="h-1.5 w-1.5 rounded-full bg-orange-500" /> {stats?.agent_health?.offline || 0} Offline
              </div>
              <div className="flex items-center gap-1 text-[10px] font-bold text-red-500">
                <div className="h-1.5 w-1.5 rounded-full bg-red-500" /> {stats?.agent_health?.missing || 0} Missing
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Identification Alerts Row */}
      {(stats?.agent_health?.invalid_serials > 0 || stats?.agent_health?.mac_changes > 0) && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card className="border-red-200 bg-red-50/30 dark:bg-red-950/10">
            <CardContent className="p-4 flex items-center gap-4">
              <div className="h-10 w-10 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center text-red-600">
                <ShieldAlert className="h-5 w-5" />
              </div>
              <div>
                <p className="text-sm font-bold text-red-600">Invalid Serial Numbers Detected</p>
                <p className="text-xs text-muted-foreground">{stats?.agent_health?.invalid_serials} devices are using auto-generated asset tags.</p>
              </div>
              <Badge variant="destructive" className="ml-auto">Action Required</Badge>
            </CardContent>
          </Card>
          <Card className="border-orange-200 bg-orange-50/30 dark:bg-orange-950/10">
            <CardContent className="p-4 flex items-center gap-4">
              <div className="h-10 w-10 rounded-full bg-orange-100 dark:bg-orange-900/30 flex items-center justify-center text-orange-600">
                <Activity className="h-5 w-5" />
              </div>
              <div>
                <p className="text-sm font-bold text-orange-600">Device MAC Address Changes</p>
                <p className="text-xs text-muted-foreground">{stats?.agent_health?.mac_changes} devices have updated or multiple MAC addresses.</p>
              </div>
              <Badge variant="outline" className="ml-auto border-orange-200 text-orange-600">Review</Badge>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <Card className="lg:col-span-1 border-none shadow-lg bg-card/50 backdrop-blur-xl">
          <CardHeader>
            <CardTitle className="text-lg font-bold">Asset Status</CardTitle>
            <CardDescription>Inventory distribution</CardDescription>
          </CardHeader>
          <CardContent className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={assetStatusData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {assetStatusData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }}
                />
                <Legend verticalAlign="bottom" height={36}/>
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card className="lg:col-span-2 border-none shadow-lg bg-card/50 backdrop-blur-xl">
          <CardHeader>
            <CardTitle className="text-lg font-bold">Weekly Ticket Volume</CardTitle>
            <CardDescription>New tickets in last 7 days</CardDescription>
          </CardHeader>
          <CardContent className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={weeklyTicketData}>
                <XAxis dataKey="day" axisLine={false} tickLine={false} />
                <YAxis axisLine={false} tickLine={false} />
                <Tooltip cursor={{fill: 'transparent'}} contentStyle={{ borderRadius: '12px', border: 'none' }} />
                <Legend />
                <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} name="New Tickets" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Real-time Activity & Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <Card className="lg:col-span-1 border-none shadow-lg bg-card/50 backdrop-blur-xl">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle className="text-lg font-bold">Expiration Timeline</CardTitle>
              <CardDescription>Warranty & License expiry</CardDescription>
            </div>
            <Clock className="h-5 w-5 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {timeline.map((item: any) => (
                <div key={item.id} className="flex items-center gap-4 p-3 rounded-xl bg-muted/30 border border-transparent hover:border-primary/20 transition-all">
                  <div className="h-8 w-8 rounded-lg bg-primary/10 flex items-center justify-center text-primary">
                    {item.type === 'LICENSE' ? <ShieldCheck className="h-4 w-4" /> : <HardDrive className="h-4 w-4" />}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-bold truncate">{item.title}</p>
                    <p className="text-[10px] text-muted-foreground">{new Date(item.date).toLocaleDateString()}</p>
                  </div>
                  <Badge variant="outline" className="text-[8px] h-4 px-1">
                    {formatDistanceToNow(new Date(item.date))} left
                  </Badge>
                </div>
              ))}
              {timeline.length === 0 && (
                <div className="text-center py-12 text-muted-foreground italic text-xs">No upcoming expirations.</div>
              )}
            </div>
          </CardContent>
        </Card>

        <Card className="lg:col-span-1 border-none shadow-lg bg-card/50 backdrop-blur-xl">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle className="text-lg font-bold">Real-time Activity</CardTitle>
              <CardDescription>Latest system events</CardDescription>
            </div>
            <Activity className="h-5 w-5 text-primary animate-pulse" />
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {recentActivity.map((activity: any) => (
                <div key={activity.id} className="flex items-start gap-4 group">
                  <div className={`mt-1 h-2 w-2 rounded-full shrink-0 ${
                    activity.status === 'OPEN' ? 'bg-blue-500' : 'bg-green-500'
                  }`} />
                  <div className="flex-1 space-y-1">
                    <p className="text-sm font-semibold group-hover:text-primary transition-colors">
                      {activity.title}
                    </p>
                    <div className="flex items-center gap-3 text-[10px] text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <Clock className="h-3 w-3" /> {formatDistanceToNow(new Date(activity.created_at))} ago
                      </span>
                      <Badge variant="outline" className="text-[8px] h-4 px-1">{activity.status}</Badge>
                    </div>
                  </div>
                </div>
              ))}
              {recentActivity.length === 0 && (
                <div className="text-center py-12 text-muted-foreground italic">No recent activity.</div>
              )}
            </div>
          </CardContent>
        </Card>

        <Card className="lg:col-span-1 border-none shadow-lg bg-card/50 backdrop-blur-xl">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle className="text-lg font-bold">Active Alerts</CardTitle>
              <CardDescription>Critical notifications</CardDescription>
            </div>
            <Badge variant="destructive" className="animate-bounce">
              {notifications.filter(n => n.type === 'CRITICAL').length} New
            </Badge>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {notifications.map((notif, i) => (
                <div key={i} className={`p-4 rounded-2xl border-l-4 flex items-start gap-4 ${
                  notif.type === 'CRITICAL' ? 'bg-red-500/5 border-l-red-500' : 'bg-blue-500/5 border-l-blue-500'
                }`}>
                  <div className={`h-8 w-8 rounded-full flex items-center justify-center shrink-0 ${
                    notif.type === 'CRITICAL' ? 'bg-red-500/20 text-red-600' : 'bg-blue-500/20 text-blue-600'
                  }`}>
                    {notif.type === 'CRITICAL' ? <ShieldAlert className="h-4 w-4" /> : <AlertCircle className="h-4 w-4" />}
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-bold">{notif.title}</p>
                    <p className="text-xs text-muted-foreground mt-1">{notif.message}</p>
                    <p className="text-[10px] text-muted-foreground mt-2 font-mono">
                      {formatDistanceToNow(new Date(notif.timestamp))} ago
                    </p>
                  </div>
                </div>
              ))}
              {notifications.length === 0 && (
                <div className="text-center py-12 text-muted-foreground italic">
                  <CheckCircle2 className="h-12 w-12 mx-auto mb-4 opacity-10" />
                  No active alerts.
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default DashboardPage;
