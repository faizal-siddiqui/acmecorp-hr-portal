import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { CompensationEditForm } from './CompensationEditForm';
import { updateCompensation } from '@/lib/api';
import { vi, describe, it, expect, beforeEach } from 'vitest';

vi.mock('@/lib/api', () => ({
  updateCompensation: vi.fn(),
}));

const mockEmployee = {
  id: 1,
  employee_code: 'E1',
  first_name: 'Alice',
  last_name: 'Zebra',
  email: 'alice@example.com',
  country: 'US',
  level: 'L3',
  status: 'active',
  hire_date: '2020-01-01',
  department_name: 'Engineering',
  base_annual: 100000,
  bonus_annual: 10000,
  currency: 'USD',
  base_usd: 100000,
  monthly_base: 8333.33,
  total_comp: 110000,
  total_comp_usd: 110000,
};

describe('CompensationEditForm', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders with initial values', () => {
    render(<CompensationEditForm employee={mockEmployee as any} onClose={vi.fn()} onSuccess={vi.fn()} />);
    
    expect(screen.getByLabelText(/Base Annual Salary/)).toHaveValue(100000);
    expect(screen.getByLabelText(/Bonus Annual/)).toHaveValue(10000);
    expect(screen.getByLabelText(/Currency/)).toHaveValue('USD');
  });

  it('validates required fields and min values', () => {
    render(<CompensationEditForm employee={mockEmployee as any} onClose={vi.fn()} onSuccess={vi.fn()} />);
    
    const baseInput = screen.getByLabelText(/Base Annual Salary/);
    const bonusInput = screen.getByLabelText(/Bonus Annual/);
    
    fireEvent.change(baseInput, { target: { value: '-100' } });
    fireEvent.change(bonusInput, { target: { value: '-50' } });
    
    // HTML5 validation will prevent submission, but we can check the attributes
    expect(baseInput).toHaveAttribute('min', '1');
    expect(bonusInput).toHaveAttribute('min', '0');
  });

  it('submits successfully', async () => {
    const mockOnSuccess = vi.fn();
    const mockOnClose = vi.fn();
    (updateCompensation as any).mockResolvedValue({ success: true });

    render(<CompensationEditForm employee={mockEmployee as any} onClose={mockOnClose} onSuccess={mockOnSuccess} />);
    
    const baseInput = screen.getByLabelText(/Base Annual Salary/);
    fireEvent.change(baseInput, { target: { value: '120000' } });
    
    const submitButton = screen.getByText('Save Changes');
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(updateCompensation).toHaveBeenCalledWith(1, expect.objectContaining({
        base_annual: 120000,
      }));
      expect(screen.getByText('Success!')).toBeInTheDocument();
    });

    // Wait for the timeout in the component
    await waitFor(() => {
      expect(mockOnSuccess).toHaveBeenCalled();
      expect(mockOnClose).toHaveBeenCalled();
    }, { timeout: 2000 });
  });

  it('handles submission error', async () => {
    (updateCompensation as any).mockRejectedValue(new Error('API Error'));

    render(<CompensationEditForm employee={mockEmployee as any} onClose={vi.fn()} onSuccess={vi.fn()} />);
    
    const submitButton = screen.getByText('Save Changes');
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText('API Error')).toBeInTheDocument();
    });
  });
});
