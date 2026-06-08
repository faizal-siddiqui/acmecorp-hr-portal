"use client";

import { useEffect, useState, use, useCallback } from "react";
import { useRouter } from "next/navigation";
import { getEmployee, EmployeeDetail, updateEmployeeStatus } from "@/lib/api";
import {
  ArrowLeft,
  Mail,
  MapPin,
  Briefcase,
  Calendar,
  User,
  DollarSign,
  TrendingUp,
  Clock,
  ShieldCheck,
  Edit,
  History,
  UserX,
  Loader2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { CompensationEditForm } from "@/components/CompensationEditForm";
import { CompensationHistory } from "@/components/CompensationHistory";

interface PageProps {
  params: Promise<{ id: string }>;
}

export default function EmployeeDetailPage({ params }: PageProps) {
  const resolvedParams = use(params);
  const router = useRouter();
  const [employee, setEmployee] = useState<EmployeeDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [refreshHistory, setRefreshHistory] = useState(0);
  const [deactivating, setDeactivating] = useState(false);

  const fetchEmployee = useCallback(async () => {
    try {
      const data = await getEmployee(resolvedParams.id);
      setEmployee(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to load employee details");
    } finally {
      setLoading(false);
    }
  }, [resolvedParams.id]);

  useEffect(() => {
    let isMounted = true;
    const load = async () => {
      try {
        const data = await getEmployee(resolvedParams.id);
        if (isMounted) {
          setEmployee(data);
          setLoading(false);
        }
      } catch (err: unknown) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : "Failed to load employee details");
          setLoading(false);
        }
      }
    };
    load();
    return () => {
      isMounted = false;
    };
  }, [resolvedParams.id]);

  const handleDeactivate = async () => {
    if (
      !employee ||
      !confirm(`Are you sure you want to deactivate ${employee.first_name} ${employee.last_name}?`)
    ) {
      return;
    }

    setDeactivating(true);
    try {
      await updateEmployeeStatus(employee.id, "inactive");
      await fetchEmployee();
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : "Failed to deactivate employee");
    } finally {
      setDeactivating(false);
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-10 sm:px-6 lg:px-8">
        <Button variant="ghost" className="mb-6" disabled>
          <ArrowLeft className="mr-2 h-4 w-4" /> Back to Directory
        </Button>
        <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
          <div className="space-y-6 lg:col-span-2">
            <Skeleton className="h-48 w-full rounded-xl" />
            <Skeleton className="h-64 w-full rounded-xl" />
          </div>
          <div className="space-y-6">
            <Skeleton className="h-96 w-full rounded-xl" />
          </div>
        </div>
      </div>
    );
  }

  if (error || !employee) {
    return (
      <div className="container mx-auto px-4 py-20 text-center sm:px-6 lg:px-8">
        <div className="mx-auto max-w-md">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-red-50 p-4 text-red-600">
            <ShieldCheck className="h-8 w-8" />
          </div>
          <h1 className="mb-2 text-2xl font-bold">Employee Not Found</h1>
          <p className="text-muted-foreground mb-6">
            {error ||
              "The employee you are looking for does not exist or you don't have permission to view it."}
          </p>
          <Button onClick={() => router.push("/employees")}>
            <ArrowLeft className="mr-2 h-4 w-4" /> Back to Directory
          </Button>
        </div>
      </div>
    );
  }

  const formatCurrency = (amount: number, currency: string) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: currency,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatUSD = (amount: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      maximumFractionDigits: 0,
    }).format(amount);
  };

  return (
    <div className="container mx-auto px-4 py-10 sm:px-6 lg:px-8">
      <Button
        variant="ghost"
        className="hover:bg-muted mb-6"
        onClick={() => router.push("/employees")}
      >
        <ArrowLeft className="mr-2 h-4 w-4" /> Back to Directory
      </Button>

      <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
        {/* Profile Header & Info */}
        <div className="space-y-8 lg:col-span-2">
          {/* Main Profile Card */}
          <div className="bg-card overflow-hidden rounded-xl border shadow-sm">
            <div className="from-primary/10 to-primary/5 h-32 border-b bg-linear-to-r" />
            <div className="px-8 pb-8">
              <div className="relative -mt-12 mb-6 flex items-end justify-between">
                <div className="bg-primary text-primary-foreground border-background flex h-24 w-24 items-center justify-center rounded-2xl border-4 text-3xl font-bold shadow-lg">
                  {employee.first_name[0]}
                  {employee.last_name[0]}
                </div>
                <div
                  className={`rounded-full px-3 py-1 text-xs font-bold tracking-wider uppercase ${
                    employee.status === "active"
                      ? "bg-green-100 text-green-700"
                      : "bg-gray-100 text-gray-600"
                  }`}
                >
                  {employee.status}
                </div>
              </div>

              <div>
                <h1 className="text-3xl font-bold">
                  {employee.first_name} {employee.last_name}
                </h1>
                <p className="text-muted-foreground mt-1 font-mono text-sm">
                  {employee.employee_code}
                </p>
              </div>

              <div className="mt-8 grid grid-cols-1 gap-6 md:grid-cols-2">
                <div className="text-muted-foreground flex items-center">
                  <Mail className="text-primary/60 mr-3 h-5 w-5" />
                  <span>{employee.email}</span>
                </div>
                <div className="text-muted-foreground flex items-center">
                  <MapPin className="text-primary/60 mr-3 h-5 w-5" />
                  <span>{employee.country}</span>
                </div>
                <div className="text-muted-foreground flex items-center">
                  <Briefcase className="text-primary/60 mr-3 h-5 w-5" />
                  <span>
                    {employee.department_name} • {employee.level}
                  </span>
                </div>
                <div className="text-muted-foreground flex items-center">
                  <Calendar className="text-primary/60 mr-3 h-5 w-5" />
                  <span>
                    Hired on{" "}
                    {new Date(employee.hire_date + "T00:00:00").toLocaleDateString(undefined, {
                      dateStyle: "long",
                    })}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Compensation Details */}
          <div className="bg-card rounded-xl border p-8 shadow-sm">
            <h2 className="mb-6 flex items-center text-xl font-bold">
              <DollarSign className="text-primary mr-2 h-5 w-5" />
              Compensation Overview
            </h2>

            <div className="grid grid-cols-1 gap-8 md:grid-cols-3">
              <div className="space-y-1">
                <p className="text-muted-foreground text-sm">Base Salary (Annual)</p>
                <p className="text-2xl font-bold">
                  {formatCurrency(employee.base_annual, employee.currency)}
                </p>
                {employee.currency !== "USD" && (
                  <p className="text-muted-foreground text-xs italic">
                    ≈ {formatUSD(employee.base_usd)}
                  </p>
                )}
              </div>

              <div className="space-y-1">
                <p className="text-muted-foreground text-sm">Target Bonus (Annual)</p>
                <p className="text-2xl font-bold">
                  {formatCurrency(employee.bonus_annual, employee.currency)}
                </p>
              </div>

              <div className="space-y-1">
                <p className="text-muted-foreground text-sm">Total Compensation</p>
                <p className="text-primary text-2xl font-bold">
                  {formatCurrency(employee.total_comp, employee.currency)}
                </p>
                {employee.currency !== "USD" && (
                  <p className="text-muted-foreground text-xs italic">
                    ≈ {formatUSD(employee.total_comp_usd)}
                  </p>
                )}
              </div>
            </div>

            <div className="mt-8 grid grid-cols-1 gap-8 border-t pt-8 md:grid-cols-2">
              <div className="flex items-start">
                <div className="bg-primary/10 mr-4 rounded-lg p-2">
                  <Clock className="text-primary h-5 w-5" />
                </div>
                <div>
                  <p className="text-sm font-medium">Monthly Gross</p>
                  <p className="text-lg font-bold">
                    {formatCurrency(employee.monthly_base, employee.currency)}
                  </p>
                  <p className="text-muted-foreground text-xs">Based on annual base salary</p>
                </div>
              </div>

              <div className="flex items-start">
                <div className="bg-primary/10 mr-4 rounded-lg p-2">
                  <TrendingUp className="text-primary h-5 w-5" />
                </div>
                <div>
                  <p className="text-sm font-medium">USD Equivalent (Total)</p>
                  <p className="text-lg font-bold">{formatUSD(employee.total_comp_usd)}</p>
                  <p className="text-muted-foreground text-xs">Using current exchange rates</p>
                </div>
              </div>
            </div>
          </div>

          {/* Change History */}
          <div className="bg-card rounded-xl border p-8 shadow-sm">
            <h2 className="mb-8 flex items-center text-xl font-bold">
              <History className="text-primary mr-2 h-5 w-5" />
              Change History
            </h2>
            <CompensationHistory employeeId={resolvedParams.id} refreshTrigger={refreshHistory} />
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-8">
          <div className="bg-card rounded-xl border p-6 shadow-sm">
            <h3 className="mb-4 flex items-center font-bold">
              <User className="mr-2 h-4 w-4" />
              Quick Actions
            </h3>
            <div className="space-y-3">
              <Button className="w-full justify-start" variant="outline" disabled>
                Edit Profile
              </Button>
              <Button
                className="w-full justify-start"
                variant="outline"
                onClick={() => setIsEditModalOpen(true)}
              >
                <Edit className="mr-2 h-4 w-4" />
                Update Compensation
              </Button>
              <Button
                className="w-full justify-start text-red-600 hover:bg-red-50 hover:text-red-700"
                variant="ghost"
                onClick={handleDeactivate}
                disabled={deactivating || employee.status === "inactive"}
              >
                {deactivating ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <UserX className="mr-2 h-4 w-4" />
                )}
                {employee.status === "inactive" ? "Already Inactive" : "Deactivate Employee"}
              </Button>
            </div>
          </div>

          <div className="bg-muted/50 rounded-xl border border-dashed p-6">
            <h3 className="mb-2 text-sm font-bold">Notes</h3>
            <p className="text-muted-foreground text-xs italic">
              No private notes for this employee. Click &quot;Edit&quot; to add internal HR
              documentation.
            </p>
          </div>
        </div>
      </div>

      {isEditModalOpen && (
        <CompensationEditForm
          employee={employee}
          onClose={() => setIsEditModalOpen(false)}
          onSuccess={() => {
            fetchEmployee();
            setRefreshHistory((prev) => prev + 1);
          }}
        />
      )}
    </div>
  );
}
