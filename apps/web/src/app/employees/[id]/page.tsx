"use client";

import { useEffect, useState, use } from "react";
import { useRouter } from "next/navigation";
import { getEmployee, EmployeeDetail } from "@/lib/api";
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
  Edit
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { CompensationEditForm } from "@/components/CompensationEditForm";

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

  const fetchEmployee = async () => {
    try {
      setLoading(true);
      const data = await getEmployee(resolvedParams.id);
      setEmployee(data);
    } catch (err: any) {
      setError(err.message || "Failed to load employee details");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEmployee();
  }, [resolvedParams.id]);

  if (loading) {
    return (
      <div className="container mx-auto py-10 px-4">
        <Button variant="ghost" className="mb-6" disabled>
          <ArrowLeft className="mr-2 h-4 w-4" /> Back to Directory
        </Button>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-6">
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
      <div className="container mx-auto py-20 px-4 text-center">
        <div className="max-w-md mx-auto">
          <div className="bg-red-50 text-red-600 p-4 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
            <ShieldCheck className="h-8 w-8" />
          </div>
          <h1 className="text-2xl font-bold mb-2">Employee Not Found</h1>
          <p className="text-muted-foreground mb-6">{error || "The employee you are looking for does not exist or you don't have permission to view it."}</p>
          <Button onClick={() => router.push("/employees")}>
            <ArrowLeft className="mr-2 h-4 w-4" /> Back to Directory
          </Button>
        </div>
      </div>
    );
  }

  const formatCurrency = (amount: number, currency: string) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const formatUSD = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0
    }).format(amount);
  };

  return (
    <div className="container mx-auto py-10 px-4">
      <Button 
        variant="ghost" 
        className="mb-6 hover:bg-muted"
        onClick={() => router.push("/employees")}
      >
        <ArrowLeft className="mr-2 h-4 w-4" /> Back to Directory
      </Button>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Profile Header & Info */}
        <div className="lg:col-span-2 space-y-8">
          {/* Main Profile Card */}
          <div className="bg-card rounded-xl border shadow-sm overflow-hidden">
            <div className="h-32 bg-linear-to-r from-primary/10 to-primary/5 border-b" />
            <div className="px-8 pb-8">
              <div className="relative flex justify-between items-end -mt-12 mb-6">
                <div className="h-24 w-24 rounded-2xl bg-primary text-primary-foreground flex items-center justify-center text-3xl font-bold border-4 border-background shadow-lg">
                  {employee.first_name[0]}{employee.last_name[0]}
                </div>
                <div className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${
                  employee.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'
                }`}>
                  {employee.status}
                </div>
              </div>
              
              <div>
                <h1 className="text-3xl font-bold">{employee.first_name} {employee.last_name}</h1>
                <p className="text-muted-foreground font-mono text-sm mt-1">{employee.employee_code}</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
                <div className="flex items-center text-muted-foreground">
                  <Mail className="h-5 w-5 mr-3 text-primary/60" />
                  <span>{employee.email}</span>
                </div>
                <div className="flex items-center text-muted-foreground">
                  <MapPin className="h-5 w-5 mr-3 text-primary/60" />
                  <span>{employee.country}</span>
                </div>
                <div className="flex items-center text-muted-foreground">
                  <Briefcase className="h-5 w-5 mr-3 text-primary/60" />
                  <span>{employee.department_name} • {employee.level}</span>
                </div>
                <div className="flex items-center text-muted-foreground">
                  <Calendar className="h-5 w-5 mr-3 text-primary/60" />
                  <span>Hired on {new Date(employee.hire_date).toLocaleDateString(undefined, { dateStyle: 'long' })}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Compensation Details */}
          <div className="bg-card rounded-xl border shadow-sm p-8">
            <h2 className="text-xl font-bold mb-6 flex items-center">
              <DollarSign className="h-5 w-5 mr-2 text-primary" />
              Compensation Overview
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Base Salary (Annual)</p>
                <p className="text-2xl font-bold">{formatCurrency(employee.base_annual, employee.currency)}</p>
                {employee.currency !== 'USD' && (
                  <p className="text-xs text-muted-foreground italic">≈ {formatUSD(employee.base_usd)}</p>
                )}
              </div>
              
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Target Bonus (Annual)</p>
                <p className="text-2xl font-bold">{formatCurrency(employee.bonus_annual, employee.currency)}</p>
              </div>

              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Total Compensation</p>
                <p className="text-2xl font-bold text-primary">{formatCurrency(employee.total_comp, employee.currency)}</p>
                {employee.currency !== 'USD' && (
                  <p className="text-xs text-muted-foreground italic">≈ {formatUSD(employee.total_comp_usd)}</p>
                )}
              </div>
            </div>

            <div className="mt-8 pt-8 border-t grid grid-cols-1 md:grid-cols-2 gap-8">
              <div className="flex items-start">
                <div className="bg-primary/10 p-2 rounded-lg mr-4">
                  <Clock className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <p className="text-sm font-medium">Monthly Gross</p>
                  <p className="text-lg font-bold">{formatCurrency(employee.monthly_base, employee.currency)}</p>
                  <p className="text-xs text-muted-foreground">Based on annual base salary</p>
                </div>
              </div>
              
              <div className="flex items-start">
                <div className="bg-primary/10 p-2 rounded-lg mr-4">
                  <TrendingUp className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <p className="text-sm font-medium">USD Equivalent (Total)</p>
                  <p className="text-lg font-bold">{formatUSD(employee.total_comp_usd)}</p>
                  <p className="text-xs text-muted-foreground">Using current exchange rates</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-8">
          <div className="bg-card rounded-xl border shadow-sm p-6">
            <h3 className="font-bold mb-4 flex items-center">
              <User className="h-4 w-4 mr-2" />
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
                <Edit className="h-4 w-4 mr-2" />
                Update Compensation
              </Button>
              <Button className="w-full justify-start text-red-600 hover:text-red-700 hover:bg-red-50" variant="ghost" disabled>
                Deactivate Employee
              </Button>
            </div>
          </div>

          <div className="bg-muted/50 rounded-xl border border-dashed p-6">
            <h3 className="font-bold mb-2 text-sm">Notes</h3>
            <p className="text-xs text-muted-foreground italic">
              No private notes for this employee. Click "Edit" to add internal HR documentation.
            </p>
          </div>
        </div>
      </div>

      {isEditModalOpen && (
        <CompensationEditForm 
          employee={employee} 
          onClose={() => setIsEditModalOpen(false)}
          onSuccess={() => fetchEmployee()}
        />
      )}
    </div>
  );
}
