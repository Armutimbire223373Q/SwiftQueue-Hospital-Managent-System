import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

type CsvPreview = {
  headers: string[];
  rows: string[][];
};

const REQUIRED_COLUMNS = ['patient_id', 'name', 'dob', 'diagnosis'];
const CANONICAL_FIELDS = [
  'patient_id',
  'name',
  'dob',
  'diagnosis',
  'medications',
  'allergies',
];

const parseCsvSimple = async (file: File): Promise<CsvPreview> => {
  const text = await file.text();
  const lines = text.split(/\r?\n/).filter((l) => l.trim().length > 0);
  if (lines.length === 0) return { headers: [], rows: [] };
  const headers = lines[0].split(',').map((h) => h.trim());
  const rows = lines.slice(1).map((line) => line.split(',').map((c) => c.trim()));
  return { headers, rows };
};

const UploadDataset: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [preview, setPreview] = useState<CsvPreview | null>(null);
  const [valid, setValid] = useState<boolean>(false);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0] ?? null;
    setFile(f);
    setStatus(null);
    setPreview(null);
    setValid(false);
    if (!f) return;
    if (!f.name.toLowerCase().endsWith('.csv')) return setStatus('Only CSV files are supported');

    try {
      const p = await parseCsvSimple(f);
      setPreview({ headers: p.headers, rows: p.rows.slice(0, 10) });

      // prepare default mapping by trying to auto-match headers to canonical fields
      const lowerHeaders = p.headers.map((h) => h.toLowerCase());
      const defaultMap: Record<string, string | null> = {};
      CANONICAL_FIELDS.forEach((field) => {
        const exact = lowerHeaders.find((h) => h === field);
        const contains = lowerHeaders.find((h) => h.includes(field));
        defaultMap[field] = exact ?? contains ?? null;
      });
      setMapping(defaultMap);

      const missing = REQUIRED_COLUMNS.filter((c) => !Object.values(defaultMap).includes(c));
      if (missing.length > 0) {
        setStatus(`Missing required columns (or not auto-mapped): ${missing.join(', ')}`);
        setValid(false);
      } else {
        setStatus('Preview ready — please confirm mappings');
        setValid(true);
      }
    } catch (err: any) {
      setStatus(`Failed to parse CSV: ${err.message ?? err}`);
    }
  };

  const [mapping, setMapping] = React.useState<Record<string, string | null>>(() =>
    CANONICAL_FIELDS.reduce((acc, f) => ({ ...acc, [f]: null }), {} as Record<string, string | null>)
  );

  const updateMapping = (field: string, header: string | null) => {
    setMapping((m) => ({ ...m, [field]: header }));
    // re-evaluate validity
    const mapped = Object.values({ ...mapping, [field]: header });
    const missing = REQUIRED_COLUMNS.filter((c) => !mapped.includes(c));
    setValid(missing.length === 0);
    setStatus(missing.length === 0 ? 'Mappings valid' : `Missing required mappings: ${missing.join(', ')}`);
  };

  const upload = async () => {
    if (!file) return setStatus('Please select a CSV file');
    if (!valid) return setStatus('CSV missing required columns');

  const fd = new FormData();
  fd.append('file', file, file.name);
  // include mapping as JSON so server can process columns accordingly
  fd.append('mapping', JSON.stringify(mapping));

    try {
      setStatus('Uploading...');
      const res = await fetch('/api/uploads', { method: 'POST', body: fd });
      if (!res.ok) throw new Error('Upload failed');
  const json = await res.json();
  setStatus(`Uploaded: ${json.filename}`);
  setUploadedFilename(json.filename);
  setFile(null);
  setPreview(null);
  setValid(false);
    } catch (err: any) {
      setStatus(`Upload failed: ${err.message ?? err}`);
    }
  };

  const [uploadedFilename, setUploadedFilename] = React.useState<string | null>(null);
  const [importReport, setImportReport] = React.useState<any | null>(null);
  const [dryRun, setDryRun] = React.useState<boolean>(true);

  const runImport = async () => {
    if (!uploadedFilename) return setStatus('No uploaded file to import');
    setStatus('Starting import...');
    try {
      const body = new URLSearchParams({ filename: uploadedFilename, mapping: JSON.stringify(mapping), dry_run: dryRun ? 'true' : 'false' });
      const res = await fetch('/api/uploads/import', {
        method: 'POST',
        body,
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      });
      if (!res.ok) {
        const txt = await res.text();
        throw new Error(txt || 'Import failed');
      }
      const json = await res.json();
      setImportReport(json);
      setStatus('Import completed');
    } catch (err: any) {
      setStatus(`Import failed: ${err.message ?? err}`);
    }
  };

  return (
    <div className="p-4 bg-white rounded shadow">
      <h3 className="text-lg font-semibold mb-2">Upload Patient Dataset (CSV)</h3>
      <div className="mb-3">
        <Label>CSV File</Label>
        <Input type="file" accept=".csv" onChange={handleFileChange} />
      </div>

      {preview && (
        <div className="mb-3">
          <h4 className="font-medium">Preview (first {preview.rows.length} rows)</h4>
          <div className="overflow-auto max-h-48 border rounded mt-2">
            <table className="min-w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  {preview.headers.map((h) => (
                    <th key={h} className="px-2 py-1 text-left font-medium">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {preview.rows.map((row, i) => (
                  <tr key={i} className="odd:bg-white even:bg-gray-50">
                    {preview.headers.map((_, cidx) => (
                      <td key={cidx} className="px-2 py-1">{row[cidx] ?? ''}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {preview && (
        <div className="mb-4">
          <h4 className="font-medium mb-2">Column mapping</h4>
          <p className="text-sm text-muted-foreground mb-2">Map CSV headers to canonical fields used by the system.</p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
            {CANONICAL_FIELDS.map((field) => (
              <div key={field} className="flex items-center gap-2">
                <label className="w-28 text-sm">{field}</label>
                <select
                  aria-label={`map-${field}`}
                  value={mapping[field] ?? ''}
                  onChange={(e) => updateMapping(field, e.target.value || null)}
                  className="flex-1 border rounded px-2 py-1"
                >
                  <option value="">-- unmapped --</option>
                  {preview.headers.map((h) => (
                    <option key={h} value={h}>{h}</option>
                  ))}
                </select>
              </div>
            ))}
          </div>

          <h5 className="font-medium mb-2">Mapped preview</h5>
          <div className="overflow-auto max-h-40 border rounded">
            <table className="min-w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  {CANONICAL_FIELDS.map((f) => (
                    <th key={f} className="px-2 py-1 text-left font-medium">{f}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {preview.rows.map((row, i) => (
                  <tr key={i} className="odd:bg-white even:bg-gray-50">
                    {CANONICAL_FIELDS.map((f, cidx) => {
                      const header = mapping[f];
                      const hidx = header ? preview.headers.indexOf(header) : -1;
                      return <td key={f} className="px-2 py-1">{hidx >= 0 ? (row[hidx] ?? '') : ''}</td>;
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <div className="flex items-center space-x-2">
        <Button onClick={upload} disabled={!file || !valid}>Upload</Button>
        <Button variant="ghost" onClick={() => { setFile(null); setStatus(null); setPreview(null); setValid(false); }}>Reset</Button>
      </div>
      {status && <p className="mt-3 text-sm text-gray-600">{status}</p>}
      {uploadedFilename && (
        <div className="mt-3">
          <h4 className="font-medium">Uploaded file: {uploadedFilename}</h4>
          <div className="flex items-center space-x-3 mt-2">
            <label className="flex items-center gap-2">
              <input type="checkbox" checked={dryRun} onChange={(e) => setDryRun(e.target.checked)} />
              <span className="text-sm">Dry run (do not commit)</span>
            </label>
            <Button onClick={runImport}>{dryRun ? 'Run dry-run' : 'Import into DB'}</Button>
          </div>
        </div>
      )}

      {importReport && (
        <div className="mt-4 p-3 border rounded bg-gray-50">
          <h4 className="font-medium">Import Report</h4>
          <p>Inserted: {importReport.inserted}</p>
          <p>Updated: {importReport.updated}</p>
          <p>Failed rows: {importReport.failed?.length ?? 0}</p>
          {importReport.failed && importReport.failed.length > 0 && (
            <div className="mt-2 overflow-auto max-h-40">
              <table className="min-w-full text-sm">
                <thead className="bg-gray-100">
                  <tr><th className="px-2 py-1">Row</th><th className="px-2 py-1">Reason</th></tr>
                </thead>
                <tbody>
                  {importReport.failed.map((f: any, i: number) => (
                    <tr key={i} className="odd:bg-white even:bg-gray-50"><td className="px-2 py-1">{f.row}</td><td className="px-2 py-1">{f.reason}</td></tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default UploadDataset;
