import './SideBar.css';
import { useState } from 'react';
import Collapsible from 'react-collapsible';
import { Button } from 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import DefineReferenceModelModal from './reference_model_modal.js';
import DefineLogModal from './log_modal.js';
import SecurityControlList from './SecurityControlList.js';
import DefineMapping from './mapping_modal.js';
import GlobalProgress from './GlobalProgress.js';

function SideBar({ refreshTrigger, refreshControls }) {
    const [showReferenceModelModal, setShowReferenceModelModal] = useState(false);
    const [showLogModal, setShowLogModal] = useState(false);
    const [showMappingModal, setShowMappingModal] = useState(false);

    const handleMappingModelLog = () => {
        setShowMappingModal(true);
    };

    const handleDefineReferenceModel = () => {
        setShowReferenceModelModal(true);
    };

    const handleCloseReferenceModelModal = () => {
        setShowReferenceModelModal(false);
    };

    const handleDefineLog = () => {
        setShowLogModal(true);
    };

    const handleCloseLogModal = () => {
        setShowLogModal(false);
    };

    const handleDefineMapping = () => {
        setShowMappingModal(true);
    };

    const handleCloseMappingModal = () => {
        setShowMappingModal(false);
    };

    return (
        <div className="sidebar">
            <div className="div-36">
                <div className="div-37">
                    <div className="div-38">
                        <div className="div-39">
                            <div className="div-40" />
                            <Collapsible
                                trigger={[
                                    "Init Assessment",
                                    <img
                                        key="init-assessment-icon" // Add a unique key here
                                        loading="lazy"
                                        src="https://cdn.builder.io/api/v1/image/assets/TEMP/c9992667147f295b32eec0696cb0fef65388fa9af146ce7034e2a192b713c079?"
                                        className="img-30"
                                    />
                                ]}
                            >
                                <div className="div-41">
                                    <Button onClick={handleDefineReferenceModel}>Define Reference Model</Button>
                                    <DefineReferenceModelModal show={showReferenceModelModal} handleClose={handleCloseReferenceModelModal} />
                                    <Button onClick={handleDefineLog}>Define Log</Button>
                                    <DefineLogModal show={showLogModal} handleClose={handleCloseLogModal} />
                                    <Button onClick={handleMappingModelLog}>Mapping Log/Model</Button>
                                    <DefineMapping show={showMappingModal} handleClose={handleCloseMappingModal} />
                                </div>
                            </Collapsible>
                        </div>
                    </div>
                </div>
                <div className="div-43">
                    <div className="div-44">
                        <div className="div-45">
                            <div className="div-46" />
                            <div className="div-47">Global Progress</div>
                        </div>
                        
                    </div>
                    
                        <GlobalProgress updateProgress={refreshTrigger}/>
                    
                </div>
            </div>
            <SecurityControlList refreshTrigger={refreshTrigger} refreshControls={refreshControls} />
        </div>
    );
}

export default SideBar;
