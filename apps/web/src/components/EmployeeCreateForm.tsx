"use client";

import { useState, useEffect } from "react";
import { X, Loader2, AlertCircle, CheckCircle2, UserPlus } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  createEmployee,
  getDepartments,
  Department,
  EmployeeCreate,
  EmployeeDetail,
} from "@/lib/api";

interface EmployeeCreateFormProps {
  onClose: () => void;
  onSuccess: (newEmployee: EmployeeDetail) => void;
}

export function EmployeeCreateForm({ onClose, onSuccess }: EmployeeCreateFormProps) {
  const [departments, setDepartments] = useState<Department[]>([]);
  const [formData, setFormData] = useState<EmployeeCreate>({
    employee_code: "",
    first_name: "",
    last_name: "",
    email: "",
    country: "US",
    level: "L1",
    hire_date: new Date().toISOString().split("T")[0],
    department_id: 0,
    base_annual: 0,
    bonus_annual: 0,
    currency: "USD",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    const fetchDepartments = async () => {
      try {
        const data = await getDepartments();
        setDepartments(data);
        if (data.length > 0) {
          setFormData((prev) => ({ ...prev, department_id: data[0].id }));
        }
      } catch (err) {
        console.error("Failed to fetch departments", err);
      }
    };
    fetchDepartments();
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]:
        name === "department_id" || name === "base_annual" || name === "bonus_annual"
          ? value === ""
            ? 0
            : parseInt(value) || 0
          : value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const result = await createEmployee(formData);
      setSuccess(true);
      setTimeout(() => {
        onSuccess(result);
        onClose();
      }, 1500);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to create employee");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto bg-black/50 p-4 backdrop-blur-sm">
      <div className="bg-card animate-in fade-in zoom-in my-8 w-full max-w-2xl overflow-hidden rounded-2xl border shadow-2xl duration-200">
        <div className="flex items-center justify-between border-b p-6">
          <div className="flex items-center gap-2">
            <UserPlus className="text-primary h-5 w-5" />
            <h2 className="text-xl font-bold">Add New Employee</h2>
          </div>
          <button
            onClick={onClose}
            className="text-muted-foreground hover:text-foreground hover:bg-muted rounded-full p-1 transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {success ? (
          <div className="space-y-4 p-12 text-center">
            <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-green-100 p-3 text-green-600">
              <CheckCircle2 className="h-10 w-10" />
            </div>
            <h3 className="text-xl font-bold text-green-700">Employee Created!</h3>
            <p className="text-muted-foreground">
              The new employee has been added to the directory.
            </p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-8 p-6">
            {error && (
              <div className="flex items-start rounded-xl border border-red-100 bg-red-50 p-4 text-sm text-red-600">
                <AlertCircle className="mt-0.5 mr-3 h-5 w-5 shrink-0" />
                <p>{error}</p>
              </div>
            )}

            <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
              {/* Basic Info */}
              <div className="space-y-4">
                <h3 className="text-muted-foreground text-sm font-semibold tracking-wider uppercase">
                  Basic Information
                </h3>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Employee Code</label>
                  <input
                    type="text"
                    name="employee_code"
                    value={formData.employee_code}
                    onChange={handleChange}
                    required
                    placeholder="e.g. ACME-001"
                    className="border-input bg-background focus-visible:ring-ring flex h-10 w-full rounded-md border px-3 py-2 text-sm focus-visible:ring-2 focus-visible:outline-none"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">First Name</label>
                    <input
                      type="text"
                      name="first_name"
                      value={formData.first_name}
                      onChange={handleChange}
                      required
                      className="border-input bg-background focus-visible:ring-ring flex h-10 w-full rounded-md border px-3 py-2 text-sm focus-visible:ring-2 focus-visible:outline-none"
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Last Name</label>
                    <input
                      type="text"
                      name="last_name"
                      value={formData.last_name}
                      onChange={handleChange}
                      required
                      className="border-input bg-background focus-visible:ring-ring flex h-10 w-full rounded-md border px-3 py-2 text-sm focus-visible:ring-2 focus-visible:outline-none"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Email Address</label>
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    required
                    className="border-input bg-background focus-visible:ring-ring flex h-10 w-full rounded-md border px-3 py-2 text-sm focus-visible:ring-2 focus-visible:outline-none"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Country (ISO)</label>
                    <input
                      type="text"
                      name="country"
                      value={formData.country}
                      onChange={handleChange}
                      required
                      maxLength={2}
                      placeholder="US"
                      className="border-input bg-background focus-visible:ring-ring flex h-10 w-full rounded-md border px-3 py-2 text-sm focus-visible:ring-2 focus-visible:outline-none"
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Level</label>
                    <input
                      type="text"
                      name="level"
                      value={formData.level}
                      onChange={handleChange}
                      required
                      placeholder="L1, L2, etc."
                      className="border-input bg-background focus-visible:ring-ring flex h-10 w-full rounded-md border px-3 py-2 text-sm focus-visible:ring-2 focus-visible:outline-none"
                    />
                  </div>
                </div>
              </div>

              {/* Employment & Compensation */}
              <div className="space-y-4">
                <h3 className="text-muted-foreground text-sm font-semibold tracking-wider uppercase">
                  Employment & Pay
                </h3>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Department</label>
                  <select
                    name="department_id"
                    value={formData.department_id}
                    onChange={handleChange}
                    required
                    className="border-input bg-background focus-visible:ring-ring flex h-10 w-full rounded-md border px-3 py-2 text-sm focus-visible:ring-2 focus-visible:outline-none"
                  >
                    {departments.map((dept) => (
                      <option key={dept.id} value={dept.id}>
                        {dept.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Hire Date</label>
                  <input
                    type="date"
                    name="hire_date"
                    value={formData.hire_date}
                    onChange={handleChange}
                    required
                    className="border-input bg-background focus-visible:ring-ring flex h-10 w-full rounded-md border px-3 py-2 text-sm focus-visible:ring-2 focus-visible:outline-none"
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Base Annual Salary</label>
                  <div className="relative">
                    <span className="text-muted-foreground absolute top-1/2 left-3 -translate-y-1/2 text-sm font-medium">
                      {formData.currency}
                    </span>
                    <input
                      type="number"
                      name="base_annual"
                      value={formData.base_annual === 0 ? "" : formData.base_annual}
                      onChange={handleChange}
                      onFocus={(e) => e.target.select()}
                      required
                      min="1"
                      className="border-input bg-background focus-visible:ring-ring flex h-10 w-full rounded-md border px-3 py-2 pl-12 text-sm focus-visible:ring-2 focus-visible:outline-none"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Bonus Annual</label>
                    <input
                      type="number"
                      name="bonus_annual"
                      value={formData.bonus_annual === 0 ? "" : formData.bonus_annual}
                      onChange={handleChange}
                      onFocus={(e) => e.target.select()}
                      required
                      min="0"
                      className="border-input bg-background focus-visible:ring-ring flex h-10 w-full rounded-md border px-3 py-2 text-sm focus-visible:ring-2 focus-visible:outline-none"
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Currency</label>
                    <select
                      name="currency"
                      value={formData.currency}
                      onChange={handleChange}
                      required
                      className="border-input bg-background focus-visible:ring-ring flex h-10 w-full rounded-md border px-3 py-2 text-sm focus-visible:ring-2 focus-visible:outline-none"
                    >
                      <option value="USD">USD</option>
                      <option value="EUR">EUR</option>
                      <option value="GBP">GBP</option>
                      <option value="CAD">CAD</option>
                      <option value="AUD">AUD</option>
                      <option value="JPY">JPY</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-3 border-t pt-6">
              <Button type="button" variant="outline" onClick={onClose} disabled={loading}>
                Cancel
              </Button>
              <Button type="submit" disabled={loading} className="min-w-[140px]">
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Creating...
                  </>
                ) : (
                  "Create Employee"
                )}
              </Button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
