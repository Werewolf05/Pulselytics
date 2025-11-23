// Export data to CSV format
export const exportToCSV = (data, filename = 'export.csv') => {
  if (!data || data.length === 0) {
    throw new Error('No data to export');
  }

  // Get headers from first object
  const headers = Object.keys(data[0]);
  
  // Create CSV content
  const csvContent = [
    headers.join(','), // Header row
    ...data.map(row => 
      headers.map(header => {
        const value = row[header];
        // Escape values that contain commas or quotes
        if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
          return `"${value.replace(/"/g, '""')}"`;
        }
        return value;
      }).join(',')
    )
  ].join('\n');

  // Create blob and download
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  
  link.setAttribute('href', url);
  link.setAttribute('download', filename);
  link.style.visibility = 'hidden';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

// Export data to JSON format
export const exportToJSON = (data, filename = 'export.json') => {
  if (!data) {
    throw new Error('No data to export');
  }

  const jsonContent = JSON.stringify(data, null, 2);
  
  const blob = new Blob([jsonContent], { type: 'application/json' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  
  link.setAttribute('href', url);
  link.setAttribute('download', filename);
  link.style.visibility = 'hidden';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

// Format data for different export types
export const formatDataForExport = (data, type = 'csv') => {
  if (type === 'csv') {
    // Flatten nested objects for CSV
    return data.map(item => {
      const flattened = {};
      Object.keys(item).forEach(key => {
        if (typeof item[key] === 'object' && item[key] !== null) {
          flattened[key] = JSON.stringify(item[key]);
        } else {
          flattened[key] = item[key];
        }
      });
      return flattened;
    });
  }
  return data;
};
