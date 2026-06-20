import React, { useState } from 'react';
import { Button, Modal, Form } from 'react-bootstrap';
import './reference_model_modal.css';

// Point Eel web socket to the instance
export const eel = window.eel;
eel.set_host('ws://localhost:8080');

const DefineReferenceModelModal = ({ show, handleClose }) => {
  const [pnmlInput, setPnmlInput] = useState('');
  const [result, setResult] = useState(null);  // State to store the result

  const handleSave = async () => {
    try {
      console.log('Saving PNML input:', pnmlInput);  // Debug log
      const result = await eel.communicate_pnml_validation_py(pnmlInput)();  // Call the eel function and await the result
      console.log('Result from Python:', result);  // Debug log
      setResult(result);  // Set the result to the state
    } catch (error) {
      console.error('Error communicating with Python:', error);
      setResult('Error communicating with Python');
    }
  };

  return (
    <Modal show={show} onHide={handleClose} centered>
      <Modal.Header closeButton>
        <Modal.Title>Define Reference Model</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Form>
          <Form.Group controlId="formPnmlInput">
            <Form.Label>PNML Connotation</Form.Label>
            <Form.Control
              type="text"
              placeholder="Enter PNML connotation"
              value={pnmlInput}
              onChange={(e) => setPnmlInput(e.target.value)}
            />
          </Form.Group>
        </Form>
        {result && (
          <div className={`result-message ${result === 'Valid PNML' ? 'valid' : 'invalid'} mt-3`}>
            {result === 'Valid PNML' ? (
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

export default DefineReferenceModelModal;
