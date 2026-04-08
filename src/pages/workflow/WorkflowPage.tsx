import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  Card, CardContent, CardHeader, CardTitle, CardDescription 
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  GitBranch, 
  Plus, 
  Search, 
  Filter,
  UserPlus,
  UserMinus,
  Clock,
  CheckCircle2,
  MoreVertical
} from 'lucide-react';
import apiClient from '@/api/client';
import { format } from 'date-fns';

const WORKFLOW_STATUSES = ['PENDING_IT', 'PREPARING', 'READY_FOR_PICKUP', 'COMPLETED'];

const WorkflowPage: React.FC = () => {
  const { data: workflows, isLoading } = useQuery({
    queryKey: ['workflows'],
    queryFn: async () => {
      const response = await apiClient.get('/workflow/requests');
      return response.data;
    },
  });

  const getWorkflowIcon = (type: string) => {
    switch (type?.toUpperCase()) {
      case 'ONBOARDING': return <UserPlus className="h-5 w-5 text-blue-500" />;
      case 'OFFBOARDING': return <UserMinus className="h-5 w-5 text-red-500" />;
      default: return <GitBranch className="h-5 w-5 text-primary" />;
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6 animate-in fade-in duration-500">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
            <GitBranch className="h-8 w-8 text-primary" />
            Workflow Management
          </h1>
          <p className="text-muted-foreground">Manage onboarding, offboarding, and asset lifecycle workflows.</p>
        </div>
        <Button>
          <Plus className="h-4 w-4 mr-2" /> New Workflow
        </Button>
      </div>

      <div className="flex flex-col md:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input 
            className="w-full pl-10 pr-4 py-2 rounded-lg border bg-background focus:ring-2 focus:ring-primary/20 outline-none transition-all"
            placeholder="Search workflows by user, type, or status..."
          />
        </div>
        <Button variant="outline">
          <Filter className="h-4 w-4 mr-2" /> Filters
        </Button>
      </div>

      <div className="flex gap-6 overflow-x-auto pb-6 min-h-[600px]">
        {WORKFLOW_STATUSES.map((status) => (
          <div key={status} className="flex-shrink-0 w-80 rounded-xl p-4 bg-muted/30 space-y-4">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <h3 className="font-bold text-sm uppercase tracking-wider">{status.replace('_', ' ')}</h3>
                <Badge variant="secondary" className="rounded-full px-2 py-0">
                  {workflows?.filter((w: any) => w.status === status).length || 0}
                </Badge>
              </div>
              <Button variant="ghost" size="icon" className="h-6 w-6">
                <MoreVertical className="h-4 w-4" />
              </Button>
            </div>

            <div className="space-y-4">
              {isLoading ? (
                Array.from({ length: 2 }).map((_, i) => (
                  <Card key={i} className="animate-pulse p-4 h-32" />
                ))
              ) : workflows?.filter((w: any) => w.status === status).map((workflow: any) => (
                <Card key={workflow.id} className="hover:shadow-md transition-all cursor-pointer group">
                  <CardContent className="p-4 space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="h-8 w-8 rounded-lg bg-primary/10 flex items-center justify-center">
                        {getWorkflowIcon(workflow.type)}
                      </div>
                      <Badge variant="outline" className="text-[10px]">{workflow.type}</Badge>
                    </div>
                    <div>
                      <h4 className="text-sm font-bold">{workflow.user_name}</h4>
                      <p className="text-xs text-muted-foreground line-clamp-1">{workflow.description}</p>
                    </div>
                    <div className="flex items-center justify-between pt-2 border-t text-[10px] text-muted-foreground">
                      <div className="flex items-center gap-1">
                        <Clock className="h-3 w-3" /> {format(new Date(workflow.created_at), 'MMM dd')}
                      </div>
                      <div className="flex items-center gap-1">
                        <CheckCircle2 className={`h-3 w-3 ${workflow.progress === 100 ? 'text-green-500' : 'text-blue-500'}`} />
                        {workflow.progress}%
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
              {workflows?.filter((w: any) => w.status === status).length === 0 && (
                <div className="text-center py-12 text-muted-foreground italic text-xs border-2 border-dashed rounded-lg">
                  No items in this stage.
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default WorkflowPage;
