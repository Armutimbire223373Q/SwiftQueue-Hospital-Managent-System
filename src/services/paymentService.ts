const API_BASE = '/api/payments';

export interface PaymentRequest {
  method: 'ecocash' | 'innbucks' | 'omari' | 'medical_aid';
  amount: number;
  reference?: string;
  membership_number?: string;
}

export async function initiatePayment(req: PaymentRequest) {
  const res = await fetch(`${API_BASE}/initiate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  });
  if (!res.ok) throw new Error('Failed to initiate payment');
  return res.json();
}

export async function verifyPayment(paymentId: string) {
  const res = await fetch(`${API_BASE}/verify/${paymentId}`);
  if (!res.ok) throw new Error('Failed to verify payment');
  return res.json();
}

export async function verifyMedicalAid(membershipNumber: string) {
  const res = await fetch(`${API_BASE}/verify-medical-aid`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ membership_number: membershipNumber }),
  });
  if (!res.ok) throw new Error('Failed to verify medical aid');
  return res.json();
}

export default { initiatePayment, verifyPayment, verifyMedicalAid };
