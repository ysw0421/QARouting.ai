import React from 'react';
import { saveReport, loadReport, listReports } from '../api';
import { useBlocks } from '../hooks/useBlocks';
import BlockEditor from '../editor/BlockEditor';
import { Box, TextField, Button } from '@mui/material';

const NotionReport = ({ externalAddTextBlock }) => {
  const [blocks, setBlocks, addBlock, editBlock, deleteBlock, undo, redo] = useBlocks();
  const [reportTitle, setReportTitle] = React.useState('');
  const [reportId, setReportId] = React.useState('');
  const [availableReports, setAvailableReports] = React.useState([]);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState('');

  React.useEffect(() => {
    (async () => {
      try {
        setLoading(true);
        const reports = await listReports();
        setAvailableReports(reports);
      } catch (e) {
        setError('Failed to fetch reports');
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const handleSave = async () => {
    setError('');
    try {
      setLoading(true);
      const report = {
        id: reportId || undefined,
        title: reportTitle,
        blocks,
      };
      const saved = await saveReport(report);
      setReportId(saved.id);
      setReportTitle(saved.title);
      const reports = await listReports();
      setAvailableReports(reports);
    } catch (e) {
      setError('Failed to save report');
    } finally {
      setLoading(false);
    }
  };

  const handleLoad = async (id) => {
    setError('');
    try {
      setLoading(true);
      const report = await loadReport(id);
      setBlocks(report.blocks || []);
      setReportId(report.id);
      setReportTitle(report.title);
    } catch (e) {
      setError('Failed to load report');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ maxWidth: 700, margin: '0 auto', p: 2 }}>
      <Box sx={{ mb: 2, display: 'flex', gap: 2 }}>
        <TextField label="Report Title" value={reportTitle} onChange={e => setReportTitle(e.target.value)} size="small" />
        <Button onClick={handleSave} variant="contained" disabled={loading}>Save</Button>
        <Button onClick={() => handleLoad(reportId)} variant="outlined" disabled={loading || !reportId}>Reload</Button>
        <TextField label="Report ID" value={reportId} onChange={e => setReportId(e.target.value)} size="small" sx={{ width: 120 }} />
      </Box>
      <Box sx={{ mb: 2 }}>
        <strong>Available Reports:</strong>
        {loading ? ' Loading...' : (
          <ul>
            {availableReports.map(r => (
              <li key={r.id}>
                <Button size="small" onClick={() => handleLoad(r.id)}>{r.title} ({r.id})</Button>
              </li>
            ))}
          </ul>
        )}
      </Box>
      {error && <Box color="red" mb={2}>{error}</Box>}
      <BlockEditor
        blocks={blocks}
        setBlocks={setBlocks}
        addBlock={addBlock}
        editBlock={editBlock}
        deleteBlock={deleteBlock}
        undo={undo}
        redo={redo}
        externalAddTextBlock={externalAddTextBlock}
      />
    </Box>
  );
};

export default NotionReport; 