import React, { useState } from 'react';
import { Button, Modal, Form } from 'react-bootstrap';
import './SecurityControlsModal.css';
import { eel } from './App';


const SecurityControlsModal = ({ show, handleClose, refreshControls }) => {
  const [file, setFile] = useState(null); // State to store the uploaded file
  const [result, setResult] = useState(null); // State to store the result

  // Function to handle file input change
  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setFile(file);
    }
  };

  // Function to process the CSV file and translate rows into security controls
  const handleSave = async () => {
    if (!file) {
      setResult('No file selected');
      return;
    }

    try {
      const reader = new FileReader();
      reader.onload = async (e) => {
        const fileContent = e.target.result;

        // Parse the CSV content using a custom parser
        const parseCSV = (csv) => {
          const rows = [];
          const lines = csv.split('\n');
          const headers = lines[0].split(',').map((header) => header.trim());

          let currentRow = [];
          let inQuotes = false;

          for (let i = 1; i < lines.length; i++) {
            let line = lines[i];

            // Handle multiline fields
            if (inQuotes) {
              currentRow[currentRow.length - 1] += `\n${line}`;
              if (line.includes('"')) {
                inQuotes = false;
              }
              continue;
            }

            const values = [];
            let current = '';
            for (let char of line) {
              if (char === '"' && !inQuotes) {
                inQuotes = true; // Start of quoted field
              } else if (char === '"' && inQuotes) {
                inQuotes = false; // End of quoted field
              } else if (char === ',' && !inQuotes) {
                values.push(current.trim());
                current = ''; // Reset for the next value
              } else {
                current += char; // Append character to the current value
              }
            }
            values.push(current.trim()); // Add the last value

            if (values.length === headers.length) {
              const row = {};
              headers.forEach((header, index) => {
                row[header] = values[index];
              });
              rows.push(row);
            }
          }

          return rows;
        };

        const rows = parseCSV(fileContent);

        if (rows.length === 0) {
          setResult('Invalid CSV file: No data rows found');
          return;
        }

        // Process each row and insert as a security control
        for (const row of rows) {
          const title = row['Security Control'] || '';
          const description = row['Description'] || '';
          const operatorName = row['Service Responsible'] || '';

          // Validate required fields
          if (!title || !description || !operatorName) {
            console.error('Missing required fields:', { title, description, operatorName });
            setResult('Error: Missing required fields in one or more rows');
            return;
          }

          // Insert the security control using eel
          eel.insert_security_control(title, description, operatorName)((response) => {
            console.log('Response from Python:', response);
            if (response !== 'Success') {
              setResult(`Error inserting security control: ${response}`);
            } else {
              setResult('File processed successfully');
              refreshControls(); // Refresh the list of security controls
            }
          });
        }
      };
      reader.readAsText(file);
    } catch (error) {
      console.error('Error processing the file:', error);
      setResult('Error processing the file');
    }
  };

  return (
    <Modal show={show} onHide={handleClose} centered>
      <Modal.Header closeButton>
        <Modal.Title>Import Security Controls</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Form>
          <Form.Group controlId="formFileUpload">
            <Form.Label>Upload CSV File</Form.Label>
            <Form.Control
              type="file"
              accept=".csv"
              onChange={handleFileChange}
            />
          </Form.Group>
        </Form>
        {result && (
          <div className={`result-message ${result === 'File processed successfully' ? 'valid' : 'invalid'} mt-3`}>
            {result === 'File processed successfully' ? (
              <i className="fas fa-check-circle"></i>
            ) : (
              <i className="fas fa-times-circle"></i>
            )}
            {` ${result}`}
          </div>
        )}
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={handleClose}>
          Close
        </Button>
        <Button variant="primary" onClick={handleSave}>
          Save
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default SecurityControlsModal;
