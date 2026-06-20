import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css';

import NavigationBar from './NavigationBar.js'; // Import the Top component
import SideBar from './SideBar.js'; // Import the left Side component 
// import ProcessAnalysis from './ProcessAnalysis.js'; // Import the Process Analysis component
import Reporting from './Reporting.js';  // Import the new Reporting component
import ComplianceConfiguration from './ComplianceConfiguration.js'; // Import the ComplianceConfiguration component
import { useState } from 'react';

// Point Eel web socket to the instance
export const eel = window.eel;
eel.set_host('ws://localhost:8080');

// Expose the `sayHelloJS` function to Python as `say_hello_js`
function sayHelloJS(x) {
  console.log('Hello from ' + x);
}
// WARN: must use window.eel to keep parse-able eel.expose{...}
window.eel.expose(sayHelloJS, 'say_hello_js');

// Test anonymous function when minimized. See https://github.com/samuelhwilliams/Eel/issues/363
function show_log(msg) {
  console.log(msg);
}
window.eel.expose(show_log, 'show_log');

// Test calling sayHelloJS, then call the corresponding Python function
sayHelloJS('Javascript World!');
eel.say_hello_py('Javascript World!');

function App() {
  const [refreshTrigger, setRefreshTrigger] = useState(false);
  const [activeTab, setActiveTab] = useState('complianceConfig'); // Default to Compliance Configuration

  const refreshSecurityControls = () => {
    setRefreshTrigger(!refreshTrigger);
  };

  const handleSelectionChange = () => {
    setRefreshTrigger(prev => !prev);
  };

  const handleUpdateProgress = () => {
    setRefreshTrigger(!refreshTrigger);
  }

  // Function to switch tabs
  const handleTabChange = (tab) => {
    setActiveTab(tab);
  };

  return (
    <>
      <div className="main-container">
        <NavigationBar
          onSelectionChange={handleSelectionChange}
          refreshTrigger={refreshTrigger}
          activeTab={activeTab}
          onTabChange={handleTabChange}
        />
        <div className="assessment-container">
          <div className="assessment-sub-container">
            <SideBar refreshTrigger={refreshTrigger} refreshControls={refreshSecurityControls} />
            {/* Render the selected tab's component */}
            {/*{activeTab === 'processAnalysis' && (
              <ProcessAnalysis />
            )}*/}
            {activeTab === 'reporting' && (
              <Reporting />
            )}
            {activeTab === 'complianceConfig' && (
              <ComplianceConfiguration />
            )}
          </div>
        </div>
      </div>
    </>
  );
}

export default App;
