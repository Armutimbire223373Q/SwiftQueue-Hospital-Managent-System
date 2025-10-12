import React, { useState } from 'react';
import { initiatePayment, verifyPayment, verifyMedicalAid } from '@/services/paymentService';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

const PaymentWidget: React.FC = () => {
  const [amount, setAmount] = useState<number>(0);
  const [paymentId, setPaymentId] = useState<string | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [medicalAidNo, setMedicalAidNo] = useState<string>('');

  const startPayment = async () => {
    setStatus('Initiating payment...');
    try {
      // default to ecocash for now; UI can be extended to choose method
      const res = await initiatePayment({ method: 'ecocash', amount });
      setPaymentId(res.payment_id);
      setStatus('Payment initiated. Use provider_url to complete payment.');
    } catch (err: any) {
      setStatus(`Failed: ${err.message ?? err}`);
    }
  };

  const checkPayment = async () => {
    if (!paymentId) return setStatus('No payment id available');
    setStatus('Verifying...');
    try {
      const res = await verifyPayment(paymentId);
      setStatus(`Payment status: ${res.status}`);
    } catch (err: any) {
      setStatus(`Verify failed: ${err.message ?? err}`);
    }
  };

  const checkMedicalAid = async () => {
    setStatus('Verifying medical aid...');
    try {
      // paymentService expects a membership number string
      const res = await verifyMedicalAid(medicalAidNo);
      setStatus(`Medical aid valid: ${res.valid}`);
    } catch (err: any) {
      setStatus(`Verify failed: ${err.message ?? err}`);
    }
  };

  return (
    <div className="p-4 bg-white rounded shadow">
      <h3 className="text-lg font-semibold mb-2">Payment</h3>

      <div className="mb-3">
        <Label>Amount</Label>
        <Input type="number" value={amount} onChange={(e) => setAmount(Number(e.target.value))} />
      </div>

      <div className="flex space-x-2 mb-3">
        <Button onClick={startPayment}>Initiate Payment</Button>
        <Button onClick={checkPayment} disabled={!paymentId}>Verify Payment</Button>
      </div>

      <div className="mb-3">
        <Label>Medical Aid Number</Label>
        <Input value={medicalAidNo} onChange={(e) => setMedicalAidNo(e.target.value)} />
      </div>
      <div className="flex space-x-2">
        <Button onClick={checkMedicalAid}>Verify Medical Aid</Button>
      </div>

      {paymentId && <p className="mt-3 text-sm">Payment ID: {paymentId}</p>}
      {status && <p className="mt-2 text-sm text-gray-600">{status}</p>}
    </div>
  );
};

export default PaymentWidget;
