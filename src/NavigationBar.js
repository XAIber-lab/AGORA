import React, { useState, useEffect } from 'react';
import './NavigationBar.css';
import { eel } from './App.js';
import ThresholdSlider from './ThresholdSlider';
import TimeThresholds from './TimeThresholds.js';
import IncidentSelection from './IncidentSelection.js';
import { FaSearch, FaFileAlt, FaCog } from 'react-icons/fa';

function NavigationBar({ refreshTrigger, onSelectionChange, activeTab, onTabChange }) {
  const [showSettings, setShowSettings] = useState(false);
  const [notCoveredCount, setNotCoveredCount] = useState(0);
  const [partiallyCoveredCount, setPartiallyCoveredCount] = useState(0);
  const [coveredCount, setCoveredCount] = useState(0);

  // Remove local activeTab state, use prop from App.js
  const [profileDropdownOpen, setProfileDropdownOpen] = useState(false);
  const [profileRole, setProfileRole] = useState('FULL INTERFACE');

  const profileRoles = ['FULL INTERFACE', 'MANAGER', 'MONITOR', 'RESPONDER', 'ANALYST'];

  const handleSettingsChange = () => {

    console.log("Updated settings");
  };

  const handleSettingsClick = () => {
    setShowSettings(!showSettings);
  };

  const handleSelectionChange = () => {
    onSelectionChange();
    console.log("Here works");
  };

  const handleTabClick = (tab) => {
    onTabChange(tab); // Call parent handler to switch tab
  };

  const handleProfileClick = () => {
    setProfileDropdownOpen(!profileDropdownOpen);
  };

  const handleRoleSelect = (role) => {
    setProfileRole(role);
    setProfileDropdownOpen(false);
  };

  useEffect(() => {
    const fetchSecurityControlsCounts = async () => {
      try {
        const notCoveredResponse = await eel.count_security_controls('not covered')();
        const partiallyCoveredResponse = await eel.count_security_controls('partially covered')();
        const coveredResponse = await eel.count_security_controls('covered')();

        setNotCoveredCount(notCoveredResponse);
        setPartiallyCoveredCount(partiallyCoveredResponse);
        setCoveredCount(coveredResponse);
      } catch (error) {
        console.error('Failed to fetch security control counts:', error);
      }
    };

    fetchSecurityControlsCounts();
  }, [refreshTrigger]);

  return (
    <div className="navbar-container">
      <div className="section-container">
        <div className="control-count">
          <div className="count-circle" style={{ backgroundColor: '#b80000' }}>{notCoveredCount}</div>
          <div className="count-label">Not covered Controls</div>
        </div>
        <div className="control-count">
          <div className="count-circle" style={{ backgroundColor: '#FF7A00' }}>{partiallyCoveredCount}</div>
          <div className="count-label">Partially covered Controls</div>
        </div>
        <div className="control-count">
          <div className="count-circle" style={{ backgroundColor: '#00b81d' }}>{coveredCount}</div>
          <div className="count-label">Covered Controls</div>
        </div>
      </div>

      <div className='section-container'>
        <IncidentSelection onSelectionChange={handleSelectionChange} />
      </div>

      <div className="section-container">
        {/* Process Analysis Button */}
        {/*<div
          className={`section-content ${activeTab === 'processAnalysis' ? 'active-tab' : ''}`}
          onClick={() => handleTabClick('processAnalysis')} style={{ backgroundColor: 'grey'}}
        >
          <div style={{ display: 'inline-flex', alignItems: 'center' }}>
            <FaSearch style={{ marginRight: 8, width: 18, height: 18, color: 'white' }} />
            <div className="label">Analysis</div>
          </div>
        </div>*/}

        {/* Compliance Configuration Button */}
        <div
          className={`section-content ${activeTab === 'complianceConfig' ? 'active-tab' : ''}`}
          onClick={() => handleTabClick('complianceConfig')}
        >
          <div style={{ display: 'inline-flex', alignItems: 'center' }}>
            <FaCog style={{ marginRight: 8, width: 18, height: 18, color: 'white' }} />
            <div className="label">Compliance Configuration</div>
          </div>
        </div>

        {/* Reporting Button */}
        <div
          className={`section-content ${activeTab === 'reporting' ? 'active-tab' : ''}`}
          onClick={() => handleTabClick('reporting')}
        >
          <div style={{ display: 'inline-flex', alignItems: 'center' }}>
            <FaFileAlt style={{ marginRight: 8, width: 18, height: 18, color: 'white' }} />
            <div className="label">Reporting</div>
          </div>
        </div>
        
      </div>

      <div className="settings-section">
        <div className="settings-icon" onClick={handleSettingsClick}>
          <img
            loading="lazy"
            src="https://cdn.builder.io/api/v1/image/assets/TEMP/a0dc1aa43d8dcaab4ca7b2f4afa065dfacdf8e35c3817a3f65d71e91a8101128?"
            className="icon"
          />
        </div>

        {showSettings && (
          <div className="settings-dropdown">
            <ThresholdSlider onSettingsChange={handleSettingsChange} />
            <TimeThresholds />
          </div>
        )}

        <div className="settings-icon">
          <img
            loading="lazy"
            src="https://cdn.builder.io/api/v1/image/assets/TEMP/11b127d01f10e38475e271d30a9081d6eb85debdad6155a1bfc6158be65009a0?"
            className="icon"
          />
        </div>

        <div className="profile-section" style={{ position: 'relative' }}>
          <div className="profile-details" onClick={handleProfileClick} style={{ cursor: 'pointer' }}>
            <div className="profile-name">Operator</div>
            <div className="profile-role">{profileRole}</div>
          </div>
          {profileDropdownOpen && (
            <div className="profile-dropdown" style={{
              position: 'absolute',
              top: '100%',
              right: 0,
              background: '#222',
              color: '#fff',
              borderRadius: '6px',
              boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
              zIndex: 100,
              minWidth: '140px',
              padding: '8px 0'
            }}>
              {profileRoles.map(role => (
                <div
                  key={role}
                  onClick={() => handleRoleSelect(role)}
                  style={{
                    padding: '8px 16px',
                    cursor: 'pointer',
                    background: profileRole === role ? '#0099db' : 'none'
                  }}
                >
                  {role}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default NavigationBar;
