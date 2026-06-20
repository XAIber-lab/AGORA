import React, { useState } from 'react';
import { Button, Modal, Form } from 'react-bootstrap';
import './log_modal.css';

// Point Eel web socket to the instance
export const eel = window.eel;
eel.set_host('ws://localhost:8080');

const DefineLogModal = ({ show, handleClose }) => {
  const [file, setFile] = useState(null);  // State to store the uploaded file
  const [result, setResult] = useState(null);  // State to store the result

  // Function to handle file input change
  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setFile(file);
    }
  };

  // Function to read the file content and handle save
  const handleSave = async () => {
    if (!file) {
      setResult('No file selected');
      return;
    }

    try {
      // Read the file content as text
      const reader = new FileReader();
      reader.onload = async (e) => {
        const fileContent = e.target.result;

        // Send file content to Python
        const result = await eel.communicate_log_py(fileContent)();
        setResult(result);
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
        <Modal.Title>Define Reference Model</Modal.Title>
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
          <div className={`result-message ${result === 'File saved successfully' ? 'valid' : 'invalid'} mt-3`}>
            {result === 'File saved successfully' ? (
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

export default DefineLogModal;
