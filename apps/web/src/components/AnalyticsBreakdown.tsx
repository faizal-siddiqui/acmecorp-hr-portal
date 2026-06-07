"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { getAnalyticsBreakdown, AnalyticsBreakdown as BreakdownData } from "@/lib/api";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

type GroupBy = "department" | "country" | "level";

export function AnalyticsBreakdown() {
  const searchParams = useSearchParams();
  const [groupBy, setGroupBy] = useState<GroupBy>("department");
  const [data, setData] = useState<BreakdownData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let ignore = false;
    
    const fetchBreakdown = async () => {
      setLoading(true);
      try {
        const params = new URLSearchParams(searchParams.toString());
        params.delete("page");
        params.delete("page_size");
        params.delete("sort_by");
        params.delete("sort_order");
        params.set("group_by", groupBy);

        const result = await getAnalyticsBreakdown(params);
        if (!ignore) {
          setData(result);
        }
      } catch (error) {
        if (!ignore) {
          console.error("Failed to fetch breakdown:", error);
        }
      } finally {
        if (!ignore) {
          setLoading(false);
        }
      }
    };

    fetchBreakdown();
    
    return () => {
      ignore = true;
    };
  }, [searchParams, groupBy]);

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0
    }).format(value);
  };

  const maxAvg = data ? Math.max(...data.items.map(i => i.avg_usd)) : 0;

  return (
    <div className="space-y-6 bg-card border rounded-xl p-6 shadow-sm">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold">Pay Breakdowns</h2>
          <p className="text-sm text-muted-foreground">Detailed aggregates by dimension.</p>
        </div>
        
        <div className="flex bg-muted p-1 rounded-lg">
          {(["department", "country", "level"] as GroupBy[]).map((option) => (
            <button
              key={option}
              onClick={() => setGroupBy(option)}
              className={`px-4 py-1.5 text-sm font-medium rounded-md transition-all ${
                groupBy === option 
                  ? "bg-background text-foreground shadow-sm" 
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              {option.charAt(0).toUpperCase() + option.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="space-y-4">
          <Skeleton className="h-[200px] w-full" />
          <Skeleton className="h-[300px] w-full" />
        </div>
      ) : data && data.items.length > 0 ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Chart Section */}
          <div className="space-y-4">
            <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">Average Salary (USD)</h3>
            <div className="space-y-3">
              {data.items.map((item) => (
                <div key={item.dimension_value} className="space-y-1">
                  <div className="flex justify-between text-xs font-medium">
                    <span>{item.dimension_value}</span>
                    <span>{formatCurrency(item.avg_usd)}</span>
                  </div>
                  <div className="h-2 w-full bg-muted rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-primary transition-all duration-500 ease-out"
                      style={{ width: `${(item.avg_usd / maxAvg) * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Table Section */}
          <div className="overflow-hidden rounded-lg border bg-background">
            <Table>
              <TableHeader>
                <TableRow className="bg-muted/50">
                  <TableHead className="py-2">{groupBy.charAt(0).toUpperCase() + groupBy.slice(1)}</TableHead>
                  <TableHead className="text-right py-2">Count</TableHead>
                  <TableHead className="text-right py-2">Avg</TableHead>
                  <TableHead className="text-right py-2">Median</TableHead>
                  <TableHead className="text-right py-2">Range (Min-Max)</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data.items.map((item) => (
                  <TableRow key={item.dimension_value}>
                    <TableCell className="font-medium py-2">{item.dimension_value}</TableCell>
                    <TableCell className="text-right py-2">{item.count}</TableCell>
                    <TableCell className="text-right py-2">{formatCurrency(item.avg_usd)}</TableCell>
                    <TableCell className="text-right py-2">{formatCurrency(item.median_usd)}</TableCell>
                    <TableCell className="text-right py-2 text-xs text-muted-foreground">
                      {formatCurrency(item.min_usd)} - {formatCurrency(item.max_usd)}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </div>
      ) : (
        <div className="h-[300px] flex items-center justify-center border-2 border-dashed rounded-lg text-muted-foreground">
          No data available for this dimension.
        </div>
      )}
    </div>
  );
}
