import React, { useState, useEffect } from 'react';
import { eel } from './App'; // Adjust the import path based on your project structure
import './Reporting.css';  // Include your styles here

const Reporting = () => {
  const [controls, setControls] = useState([]);
  const [assessmentResultsWithImages, setAssessmentResultsWithImages] = useState([]);
  const [loadingAssessmentResultsWithImages, setLoadingAssessmentResultsWithImages] = useState(true);
  const [assessmentDetails, setAssessmentDetails] = useState([]);
  const [loadingAssessmentDetails, setLoadingAssessmentDetails] = useState(true);
  const [loadingControls, setLoadingControls] = useState(true);
  const [expandedIncidentIds, setExpandedIncidentIds] = useState({}); // Track expanded states for incident IDs
  const [selectedControl, setSelectedControl] = useState(null); // Track the selected control

  // Fetch security controls and assessment results when the component mounts
  useEffect(() => {
    const fetchControls = async () => {
      try {
        const result = await eel.fetch_all_security_controls()(); // Fetch security controls
        const controlsData = JSON.parse(result);
        setControls(controlsData);
      } catch (error) {
        console.error('Error fetching security controls:', error);
      } finally {
        setLoadingControls(false);
      }
    };

    const fetchAssessmentResultsWithImages = async () => {
      try {
        const result = await eel.fetch_all_assessment_views()();  // Fetch assessment results with images
        const assessmentData = JSON.parse(result);
        setAssessmentResultsWithImages(assessmentData);
      } catch (error) {
        console.error('Error fetching assessment results with images:', error);
      } finally {
        setLoadingAssessmentResultsWithImages(false);
      }
    };

    const fetchAssessmentDetails = async () => {
      try {
        const result = await eel.get_all_assessment_details()();  // Fetch all assessment details
        const assessmentData = JSON.parse(result);
        setAssessmentDetails(assessmentData);
      } catch (error) {
        console.error('Error fetching assessment details:', error);
      } finally {
        setLoadingAssessmentDetails(false);
      }
    };

    fetchControls();
    fetchAssessmentResultsWithImages();
    fetchAssessmentDetails();
  }, []);

  // Find the security control that matches the assessment's evidence filename
  const getControlForAssessmentByFilename = (evidenceFilename) => {
    return controls.find(control => {
      if (control.evidence) {
        const evidenceFiles = control.evidence.split(';'); // Split by ';' to handle multiple filenames
        return evidenceFiles.includes(evidenceFilename); // Check if the filename is in the list
      }
      return false;
    });
  };

  // Find the security control that matches the assessment's name
  const getControlForAssessmentByName = (assessmentName) => {
    return controls.find(control => {
      if (control.evidence) {
        const evidenceFiles = control.evidence.split(';');
        return evidenceFiles.includes(assessmentName);
      }
      return false;
    });
  };

  // Toggle the expansion of incident IDs
  const toggleIncidentIds = (assessmentId) => {
    setExpandedIncidentIds(prevState => ({
      ...prevState,
      [assessmentId]: !prevState[assessmentId] // Toggle expanded state for this assessment ID
    }));
  };

  // Handle control selection
  const handleControlClick = (controlId) => {
    setSelectedControl(controlId === selectedControl ? null : controlId); // Deselect if the same control is clicked again
  };

  // Filter the assessment results by selected control
  const filteredAssessmentResultsWithImages = assessmentResultsWithImages.filter(result => {
    const linkedControl = getControlForAssessmentByFilename(result.image_filename);
    return selectedControl ? linkedControl && linkedControl.id === selectedControl : true;
  });

  const filteredAssessmentDetails = assessmentDetails.filter(result => {
    const linkedControl = getControlForAssessmentByName(result.name);
    return selectedControl ? linkedControl && linkedControl.id === selectedControl : true;
  });

  const exportControlsToCSV = (controls) => {
    if (!controls || controls.length === 0) return;
    const headers = Object.keys(controls[0]);
    const csvRows = [
      headers.join(','),
      ...controls.map(row => headers.map(h => `"${row[h] ?? ''}"`).join(','))
    ];
    const csvContent = "data:text/csv;charset=utf-8," + csvRows.join('\n');
    const link = document.createElement('a');
    link.href = encodeURI(csvContent);
    link.download = 'security_controls.csv';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const exportControlsToPDF = async (controls, assessmentResultsWithImages) => {
    if (!controls || controls.length === 0) return;
    const { default: jsPDF } = await import('jspdf');
    const doc = new jsPDF({ unit: 'pt', format: 'a4' });

    // PDF layout constants
    const leftMargin = 40;
    const rightMargin = 40;
    const pageWidth = doc.internal.pageSize.getWidth();
    const usableWidth = pageWidth - leftMargin - rightMargin;
    const maxImageHeight = doc.internal.pageSize.getHeight() - 100; // leave space for margins
    const lineHeight = 14;
    const pageBottom = doc.internal.pageSize.getHeight() - 60; // bottom margin

    // Date and time
    const now = new Date();
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.text(`Incident Management Assessment Report`, leftMargin, 40);
    doc.setFontSize(10);
    doc.setFont('helvetica', 'italic');
    doc.text(`Generated: ${now.toLocaleString()}`, leftMargin, 60);
    doc.setFont('helvetica', 'normal');

    let y = 80;

    // Helper to wrap text and return lines
    const wrap = (text, fontSize = 10) => {
      doc.setFontSize(fontSize);
      return doc.splitTextToSize(String(text ?? ''), usableWidth);
    };

    // Helper to get image dimensions from base64
    const getImageDimensions = (base64) => {
      return new Promise(resolve => {
        const img = new window.Image();
        img.onload = () => {
          resolve({ width: img.width, height: img.height });
        };
        img.src = `data:image/png;base64,${base64}`;
      });
    };

    for (const control of controls) {
      doc.setFontSize(12);
      doc.setTextColor(40, 40, 40);

      [
        { label: `Control ID: ${control.id}`, fontSize: 12 },
        { label: `Title: ${control.title}` },
        { label: `Description: ${control.description}` },
        { label: `Operator ID: ${control.operator_id}` },
        { label: `Status: ${control.status}` },
        { label: `Evidence: ${control.evidence}` },
        { label: `Automatic recommender Comments: ${control.comments}` }
      ].forEach(({ label, fontSize }) => {
        const lines = wrap(label, fontSize || 10);
        for (const line of lines) {
          if (y + lineHeight > pageBottom) {
            doc.addPage();
            y = 40;
          }
          doc.text(line, leftMargin, y);
          y += lineHeight;
        }
      });

      // Linked assessment images and comments
      const evidenceFiles = control.evidence ? control.evidence.split(';') : [];
      const linkedAssessments = assessmentResultsWithImages.filter(a =>
        evidenceFiles.includes(a.image_filename)
      );
      for (const a of linkedAssessments) {
        const evidenceLines = wrap(`Evidence Name: ${a.image_filename}`);
        for (const line of evidenceLines) {
          if (y + lineHeight > pageBottom) {
            doc.addPage();
            y = 40;
          }
          doc.text(line, leftMargin + 20, y);
          y += lineHeight;
        }

        // Image (original aspect ratio, scaled to fit within usableWidth and maxImageHeight)
        if (a.encoded_image) {
          try {
            const { width: imgW, height: imgH } = await getImageDimensions(a.encoded_image);
            let drawW = imgW, drawH = imgH;
            // Scale down if too large for PDF
            const widthScale = usableWidth / imgW;
            const heightScale = maxImageHeight / imgH;
            const scale = Math.min(1, widthScale, heightScale);
            drawW = imgW * scale;
            drawH = imgH * scale;

            if (y + drawH > pageBottom) {
              doc.addPage();
              y = 40;
            }

            doc.addImage(
              `data:image/png;base64,${a.encoded_image}`,
              'PNG',
              leftMargin + 20, y, drawW, drawH
            );
            y += drawH + 15;
          } catch (err) {
            const errorLines = wrap('Image could not be rendered.');
            for (const line of errorLines) {
              if (y + lineHeight > pageBottom) {
                doc.addPage();
                y = 40;
              }
              doc.text(line, leftMargin + 20, y);
              y += lineHeight;
            }
          }
        }

        // Comments
        doc.setFont('helvetica', 'bold');
        const commentLines = wrap(`Assessment Comments: ${a.comments}`);
        for (const line of commentLines) {
          if (y + lineHeight > pageBottom) {
            doc.addPage();
            y = 40;
          }
          doc.text(line, leftMargin + 20, y);
          y += lineHeight;
        }
        doc.setFont('helvetica', 'normal');
      }

      y += 10;
      if (y > pageBottom) {
        doc.addPage();
        y = 40;
      }
    }

    doc.save('security_controls_report.pdf');
  };

  return (
    <div className="reporting-container">
      <div className="div-114">
        <div className="aggregated-view">
          {/* Security Controls Section */}
          <div className="view" style={{ flex: '2', display: 'flex', flexDirection: 'column', height: '100%' }}>
            <div className="view-header">
              <div className="view-title">
                <div className="view-color" />
                <div className="view-name">Security Controls List</div>
              </div>
              <div className="view-options" style={{ marginLeft: 'auto', display: 'flex', gap: '10px' }}>
                {/*<button
                  className="export-btn"
                  onClick={() => exportControlsToCSV(controls)}
                  style={{
                    background: '#0099db',
                    color: '#fff',
                    border: 'none',
                    borderRadius: '4px',
                    padding: '4px 12px',
                    cursor: 'pointer'
                  }}
                >
                  Export CSV
                </button>*/}
                <button
                  className="export-btn"
                  onClick={() => exportControlsToPDF(controls, assessmentResultsWithImages)}
                  style={{
                    background: '#db0099',
                    color: '#fff',
                    border: 'none',
                    borderRadius: '4px',
                    padding: '4px 12px',
                    cursor: 'pointer'
                  }}
                >
                  Export PDF
                </button>
              </div>
            </div>
            {/* Security Controls Table */}
             <div className="controls-table-container" style={{ maxHeight: '1050px', overflowY: 'auto' }}>
              {loadingControls ? (
                <p>Loading security controls...</p>
              ) : controls.length === 0 ? (
                <p>No security controls available.</p>
              ) : (
                <table className="controls-table">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Title</th>
                      <th>Description</th>
                      <th>Operator ID</th>
                      <th>Status</th>
                      {/* <th>Evidence</th> */}
                      <th>Automatic Recommender Comments</th>
                    </tr>
                  </thead>
                  <tbody>
                    {controls.map((control) => (
                      <tr
                        key={control.id}
                        className={selectedControl === control.id ? 'selected-row-stroke' : ''}
                        onClick={() => handleControlClick(control.id)}
                      >
                        <td>{control.id}</td>
                        <td>{control.title}</td>
                        <td>{control.description}</td>
                        <td>{control.operator_id}</td>
                        <td>{control.status}</td>
                        {/* <td>{control.evidence}</td> */}
                        <td>{control.comments}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>

          {/* Assessment Results View */}
          <div className="view" style={{ flex: '1' }}>
            <div className="view-header">
              <div className="view-title">
                <div className="view-color" />
                <div className="view-name">Assessment Results</div>
              </div>
              <div className="view-options">
                {/* Options icons (if any) */}
              </div>
            </div>
            {/* Assessment Results Display */}
            <div className="assessment-results-container" style={{ maxHeight: '1000px', overflowY: 'auto' }}>
              {/* First, display assessment results with images */}
              <h2>Assessment Views</h2>
              {loadingAssessmentResultsWithImages ? (
                <p>Loading assessment results with images...</p>
              ) : filteredAssessmentResultsWithImages.length === 0 ? (
                <p>No assessment results with images available.</p>
              ) : (
                <div className="assessment-results-list">
                  {filteredAssessmentResultsWithImages.map((result) => {
                    const linkedControl = getControlForAssessmentByFilename(result.image_filename);
                    return (
                      <div key={result.id} className={`assessment-item ${selectedControl ? 'selected-stroke' : ''}`}>
                        {result.encoded_image ? (
                          <img
                            src={`data:image/png;base64,${result.encoded_image}`}
                            alt="Assessment Screenshot"
                            className="assessment-screenshot"
                            style={{
                              maxHeight: '300px',
                              maxWidth: '100%',
                              objectFit: 'contain',
                            }}
                          />
                        ) : (
                          <p>No image available</p>
                        )}
                        {linkedControl ? (
                          <p className="assessment-control-info">
                            Linked Control: ID {linkedControl.id} - {linkedControl.title}
                          </p>
                        ) : (
                          <p className="assessment-control-info">No linked control found</p>
                        )}
                        <p className="assessment-comments">Comments: {result.comments}</p>
                      </div>
                    );
                  })}
                </div>
              )}

              {/* Now, display assessment details */}
              <h2>Incident Tags</h2>
              {loadingAssessmentDetails ? (
                <p>Loading assessment details...</p>
              ) : filteredAssessmentDetails.length === 0 ? (
                <p>No assessment details available.</p>
              ) : (
                <div className="assessment-results-list">
                  {filteredAssessmentDetails.map((result) => {
                    const linkedControl = getControlForAssessmentByName(result.name);
                    return (
                      <div key={result.id} className={`assessment-item ${selectedControl ? 'selected-stroke' : ''}`}>
                        <p className="assessment-id-name">Tag Name: {result.name}</p>
                        {linkedControl ? (
                          <p className="assessment-control-info">
                            Linked Control: ID {linkedControl.id} - {linkedControl.title}
                          </p>
                        ) : (
                          <p className="assessment-control-info">No linked control found</p>
                        )}
                        <p
                          className="assessment-incident-ids-toggle"
                          onClick={() => toggleIncidentIds(result.id)}
                        >
                          {expandedIncidentIds[result.id] ? 'Hide' : 'Show'} Incident IDs
                        </p>
                        {expandedIncidentIds[result.id] && (
                          <div className="assessment-incident-ids">
                            Incident IDs: {result.incident_ids_list}
                          </div>
                        )}
                        <p className="assessment-type">Type: {result.type}</p>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Reporting;
