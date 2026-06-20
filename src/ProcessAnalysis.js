import './ProcessAnalysis.css';
import { useEffect, useState, useRef } from 'react';
import { eel } from './App';
import html2canvas from 'html2canvas';  

const ProcessAnalysis = ({ analysisTrigger, updateProgress }) => {

  const [isModalVisible, setModalVisible] = useState(false);

  // Create separate refs for each view container
  const activeclosedIncidentsRef = useRef(null);
  const statisticalAnalysisRef = useRef(null);
  const processStatisticsRef = useRef(null);
  const referenceModelRef = useRef(null);
  const commonVariantsRef = useRef(null);
  const criticalIncidentsRef = useRef(null);
  const complianceDevelopmentRef = useRef(null);
  const complianceDistributionRef = useRef(null);
  const technicalAnalysisRef = useRef(null);
  const tabularAnalysisRef = useRef(null);
  const individualAnalysisRef = useRef(null);
  const whatIfAnalysisRef = useRef(null);
  const [infoView, setInfoView] = useState(null);

  const [currentRef, setCurrentRef] = useState(null);

  const openModalWithRef = (ref) => {
    setCurrentRef(ref);  // Set the current ref
    setModalVisible(true);  // Show the modal
  };

  const showViewInformation = (viewKey) => {
    setInfoView(viewKey);
  };

  const closeInfoModal = () => setInfoView(null);

  useEffect(() => {
    setRefreshTrigger(prev => !prev);
    console.log("works?");
  }, [analysisTrigger]);

  const handleSelectionChange = () => {
    setRefreshTrigger(prev => !prev);
  };

  const handleTabularSelectionChange = () => {
    setTabularSelectionTrigger(prev => !prev);
    console.log("Process trigger");
  };

  const handleTabularFilterChange = () => {
    setGlobalFilterTrigger(prev => ! prev);
    console.log("Global Filter trigger");
  };

  const handleGraphCursorChange = () => {
    setGraphCursorTrigger(prev => ! prev);
    console.log("Graph cursor trigger");
  };

  const handleWhatIfAnalysisUpdate = () => {
    setWhatIfAnalysisTrigger(prev => !  prev);
  }


  const handleModalClose = () => {
    setModalVisible(false);
  };

  const handleUpdateProgress = () => {
    updateProgress();
  };

  return (
    <div>
      <p>TBD. Future implementation</p>
    </div>
  );
}

export default ProcessAnalysis;
