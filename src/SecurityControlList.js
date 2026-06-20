import React, { useState, useEffect } from 'react';
import './SecurityControlList.css';
import { eel } from './App';
import Collapsible from 'react-collapsible';
import DefineSecurityControl from './define_security_control.js';
import SecurityControlsModal from './SecurityControlsModal'; // Import the modal component

function SecurityControlList({ refreshTrigger, refreshControls }) {
    const [securityControls, setSecurityControls] = useState([]);
    const [showOptions, setShowOptions] = useState(null); // State to manage delete option visibility
    const [totalSecurityControls, setTotalSecurityControls] = useState(0);
    const [showModal, setShowModal] = useState(false); // State to control modal visibility
    const [additionalInstructions, setAdditionalInstructions] = useState({}); // Store instructions per control
    const [assessmentStatus, setAssessmentStatus] = useState({}); // { [controlId]: 'idle' | 'loading' | 'received' }

    useEffect(() => {
        const fetchSecurityControls = async () => {
            try {
                const response = await eel.fetch_all_security_controls()();
                console.log('Received security controls:', response);
                const controls = JSON.parse(response);
                setSecurityControls(controls);
                setTotalSecurityControls(controls.length);
            } catch (error) {
                console.error('Failed to fetch or parse security controls:', error);
            }
        };

        fetchSecurityControls(); // Fetch controls on mount and when refreshTrigger changes
    }, [refreshTrigger]);

    const handleDelete = async (controlId) => {
        try {
            await eel.delete_security_control(controlId)();
            setShowOptions(null); // Hide delete option after deletion
            refreshControls();
        } catch (error) {
            console.error('Failed to delete security control:', error);
        }
    };

    const handleGenerateAssessment = async (controlId) => {
        try {
            const instruction = additionalInstructions[controlId] || '';
        setAssessmentStatus(prev => ({ ...prev, [controlId]: 'loading' }));
        const result = await eel.generate_assessment_security_control(controlId, instruction)();
        setAssessmentStatus(prev => ({ ...prev, [controlId]: 'received' }));
            setShowOptions(null); // Hide delete option after deletion
            refreshControls();
        } catch (error) {
            console.error('Failed to failed to generate assessment for security control:', error);
        }
    };

    // Function to get the CSS class based on status
    const getStatusClass = (status) => {
        switch (status.toLowerCase()) {
            case 'covered':
                return 'status-covered';
            case 'partially covered':
                return 'status-partially-covered';
            case 'not covered':
                return 'status-not-covered';
            default:
                return '';
        }
    };

    return (
        <div>
            <div className="div-85">
                <div className="div-86">
                    <div className="div-87">
                        <div className="div-88" />
                        <div className="div-89">
                            <div className="div-90">Security Controls</div>
                            <div className="total-number-security-controls">{totalSecurityControls}</div>
                        </div>
                    </div>
                    <div className="div-92">
                        {/* Show the modal when clicking this image */}
                        <img
                            loading="lazy"
                            src="https://cdn.builder.io/api/v1/image/assets/TEMP/38c07b170bfeb7835adc20b28bcff61a5a96acfa9c8b83250fd741f77e854b5d?"
                            className="img-27"
                            onClick={() => setShowModal(true)} // Open the modal
                            style={{ cursor: 'pointer' }}
                        />
                        <img
                            loading="lazy"
                            src="https://cdn.builder.io/api/v1/image/assets/TEMP/f0bb51f1a4dc291f66d0f5ec145a7a201665d1b86cc9f0c4ca42e25210e085e7?"
                            className="img-28"
                        />
                    </div>
                </div>
                <div className="div-103">
                    <div className="div-104">
                        <Collapsible
                            trigger={[
                                <div key="define-security-control-text" className="div-105">Define new Security Control</div>,
                                <img
                                    key="define-security-control-icon"
                                    loading="lazy"
                                    src="https://cdn.builder.io/api/v1/image/assets/TEMP/c9992667147f295b32eec0696cb0fef65388fa9af146ce7034e2a192b713c079?"
                                    className="img-30"
                                />
                            ]}
                        >
                            <DefineSecurityControl refreshControls={refreshControls} />
                        </Collapsible>
                    </div>
                </div>
                {securityControls.length > 0 ? securityControls.map((control) => (
                    <div key={control.id} className="security-control-container">
                        <div className={`security-control-content ${showOptions === control.id ? 'blurred' : ''}`}>
                            <div className="security-control-header">
                                <div className={`security-control-status ${getStatusClass(control.status)}`}>
                                    {control.status}
                                </div>
                                <div className="div-109">{control.date || ''}</div>
                                <img
                                    loading="lazy"
                                    src="https://cdn.builder.io/api/v1/image/assets/TEMP/8895bd9f8d97cf1ce797fbfd735df7d6f317969a72619e5b468bb33460611015?"
                                    className="img-41"
                                    onClick={() => setShowOptions(showOptions === control.id ? null : control.id)} // Toggle delete option visibility
                                    style={{ cursor: 'pointer' }}
                                />
                            </div>
                            <div className="security-control-tags">
                                {control.tags && control.tags.split(',').map((tag) => (
                                    <div key={tag.trim()} className="tag">{tag}</div>
                                ))}
                            </div>
                            <div className="security-control-title">{control.title}</div>
                            <div className="security-control-description">{control.description}</div>
                            <div className="security-control-footer">
                                <div className="security-control-operator">Assigned to: {control.operator_id}</div>
                            </div>
                        </div>
                            {showOptions === control.id && (
                                <>
                                    <div className="delete-option" style={{ marginBottom: '8px' }}>
                                        <button onClick={() => handleDelete(control.id)}>Delete</button>
                                    </div>
                                    <div className="assessment-action-box" style={{ marginTop: 4, padding: '12px', border: '2px solid #0099db', borderRadius: '8px', background: '#fafbfc', display: 'flex', flexDirection: 'column', alignItems: 'center', backgroundColor: 'black' }}>
                                        <div className="generate-assessment" style={{ width: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '12px' }}>
                                            <button
                                                onClick={() => handleGenerateAssessment(control.id)}
                                                style={{ minWidth: '180px' }}
                                                disabled={assessmentStatus[control.id] === 'loading'}
                                            >
                                                Generate Assessment
                                            </button>
                                            {assessmentStatus[control.id] === 'loading' && (
                                                <span className="loader" style={{ display: 'inline-block', width: 22, height: 22 }}>
                                                    <svg viewBox="0 0 50 50" style={{ width: 22, height: 22 }}>
                                                        <circle cx="25" cy="25" r="20" fill="none" stroke="#0099db" strokeWidth="5" strokeDasharray="31.4 31.4" strokeLinecap="round">
                                                            <animateTransform attributeName="transform" type="rotate" from="0 25 25" to="360 25 25" dur="0.8s" repeatCount="indefinite" />
                                                        </circle>
                                                    </svg>
                                                </span>
                                            )}
                                            {assessmentStatus[control.id] === 'received' && (
                                                <span style={{ color: '#009900', fontSize: 20, marginLeft: 4 }} title="Assessment received">&#10003;</span>
                                            )}
                                        </div>
                                        <div className="additional-instruction-box" style={{ marginTop: 10, width: '100%',}}>
                                            <input
                                                type="text" 
                                                placeholder="e.g. additional instruction"
                                                    value={additionalInstructions[control.id] || ''}
                                                    onChange={e => setAdditionalInstructions({ ...additionalInstructions, [control.id]: e.target.value })}
                                                    style={{ width: '100%', padding: '6px', fontSize: '14px', borderRadius: '4px', border: '1px solid #ccc', backgroundColor: 'black', color: 'white' }}
                                            />
                                        </div>
                                    </div>
                                </>
                            )}
                    </div>
                )) : <div className="security-control-container">No security controls found.</div>}
            </div>

            {/* SecurityControlsModal for importing security controls */}
            <SecurityControlsModal
                show={showModal}
                handleClose={() => setShowModal(false)} // Close the modal
                refreshControls={refreshControls} // Refresh the list after importing
            />
        </div>
    );
}

export default SecurityControlList;
