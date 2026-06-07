"use client";

import { useEffect, useState } from "react";
import { getEmployeeHistory, SalaryHistoryItem } from "@/lib/api";
import { History, User, Calendar, ArrowRight } from "lucide-react";

interface CompensationHistoryProps {
  employeeId: string;
  refreshTrigger?: number;
}

export function CompensationHistory({ employeeId, refreshTrigger }: CompensationHistoryProps) {
  const [history, setHistory] = useState<SalaryHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        setLoading(true);
        const data = await getEmployeeHistory(employeeId);
        setHistory(data);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : "Failed to load history");
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, [employeeId, refreshTrigger]);

  if (loading && history.length === 0) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-20 bg-muted animate-pulse rounded-lg" />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 text-red-600 rounded-lg text-sm">
        {error}
      </div>
    );
  }

  if (history.length === 0) {
    return (
      <div className="text-center py-12 bg-muted/30 rounded-xl border border-dashed">
        <History className="h-8 w-8 mx-auto mb-3 text-muted-foreground/50" />
        <p className="text-muted-foreground text-sm">No compensation changes recorded yet.</p>
      </div>
    );
  }

  const formatField = (field: string) => {
    return field.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const formatValue = (field: string, value: string | null) => {
    if (value === null) return "N/A";
    if (field.includes('annual') || field.includes('base')) {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD', // This is a simplification, ideally we'd use the record's currency
        maximumFractionDigits: 0
      }).format(parseInt(value));
    }
    return value;
  };

  return (
    <div className="relative space-y-0">
      {/* Vertical line */}
      <div className="absolute left-[19px] top-2 bottom-2 w-0.5 bg-border" />

      <div className="space-y-6">
        {history.map((item) => (
          <div key={item.id} className="relative pl-12">
            {/* Dot */}
            <div className="absolute left-0 top-1.5 h-10 w-10 rounded-full bg-background border-2 border-primary flex items-center justify-center z-10 shadow-sm">
              <History className="h-4 w-4 text-primary" />
            </div>

            <div className="bg-card border rounded-xl p-4 shadow-xs hover:shadow-md transition-shadow">
              <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary/10 text-primary">
                  {formatField(item.field)}
                </span>
                <div className="flex items-center text-xs text-muted-foreground">
                  <Calendar className="h-3 w-3 mr-1" />
                  {new Date(item.changed_at).toLocaleString(undefined, { 
                    dateStyle: 'medium',
                    timeStyle: 'short'
                  })}
                </div>
              </div>

              <div className="flex items-center gap-3 mb-3 text-sm">
                <span className="font-medium text-muted-foreground line-through">
                  {formatValue(item.field, item.old_value)}
                </span>
                <ArrowRight className="h-4 w-4 text-muted-foreground" />
                <span className="font-bold text-foreground">
                  {formatValue(item.field, item.new_value)}
                </span>
              </div>

              <div className="flex items-center text-xs text-muted-foreground pt-3 border-t">
                <User className="h-3 w-3 mr-1" />
                <span>Changed by {item.changed_by_email}</span>
              </div>
              
              {item.note && (
                <p className="mt-2 text-xs text-muted-foreground italic bg-muted/50 p-2 rounded">
                  &quot;{item.note}&quot;
                </p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
