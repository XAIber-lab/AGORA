import React, { useState, useEffect } from 'react';
import { Button, Modal, Form } from 'react-bootstrap';
import './mapping_modal.css';

// Point Eel web socket to the instance
import { eel } from './App';

const MappingModal = ({ show, handleClose }) => {
  const [places, setPlaces] = useState([]);
  const [mapping, setMapping] = useState({});
  const [result, setResult] = useState(null);  // State to store the result from Python

  useEffect(() => {
    const fetchPlaces = async () => {
      try {
        const placesFromPnml = await eel.extract_places_from_pnml()();
        setPlaces(placesFromPnml || []);
      } catch (error) {
        console.error('Failed to fetch places:', error);
      }
    };

    if (show) {
      fetchPlaces();
    }
  }, [show]);

  const handleMappingChange = (place, event) => {
    setMapping(prev => ({ ...prev, [place]: event.target.value.trim() }));
  };

  const handleSave = async () => {
    try {
        const placesArray = Object.keys(mapping); // Array of place names
        const mappingObject = mapping; // Dictionary mapping places to states
        console.log('Saving Mapping:', placesArray, mappingObject);
        const saveResult = await eel.write_mapping_to_file(placesArray, mappingObject)();
        setResult('Mapping saved successfully');
        console.log('Result from Python:', saveResult);
    } catch (error) {
        console.error('Error saving mapping:', error);
        setResult('Error communicating with Python');
    }
};


  return (
    <Modal show={show} onHide={handleClose} centered>
      <Modal.Header closeButton>
        <Modal.Title>Define Model/Log Mapping</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Form>
          {places.map(place => (
            <Form.Group key={place} className="mb-3">
              <Form.Label>{place}</Form.Label>
              <Form.Control
                type="text"
                placeholder="Enter state code (e.g., N, A, R)"
                value={mapping[place] || ''}
                onChange={(e) => handleMappingChange(place, e)}
              />
            </Form.Group>
          ))}
        </Form>
        {result && <div className={`result-message ${result.includes('successfully') ? 'text-success' : 'text-danger'} mt-3`}>
            {result}
          </div>
        }
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

export default MappingModal;
