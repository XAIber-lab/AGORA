# sankey_input.py

COLORS = {
    "RED": "rgba(231, 76, 60, 0.8)",      # Security / Critical
    "BLUE": "rgba(52, 152, 219, 0.8)",     # Functional / UI
    "GREEN": "rgba(46, 204, 113, 0.8)",    # Infrastructure / Hardware
    "PURPLE": "rgba(155, 89, 182, 0.8)",   # Backend / Logic
    "ORANGE": "rgba(230, 126, 34, 0.8)",   # Database / Storage
    "YELLOW": "rgba(241, 196, 15, 0.8)",   # Networking / External API
    "TEAL": "rgba(26, 188, 156, 0.8)",     # Documentation / Compliance
    "NAVY": "rgba(44, 62, 80, 0.8)",       # Core System / Kernel
    "PINK": "rgba(255, 105, 180, 0.8)",    # Quality Assurance / Testing
    "BROWN": "rgba(121, 85, 72, 0.8)",     # Legacy / Maintenance
    "GREY": "rgba(149, 165, 166, 0.8)",    # General Reference
    "LIME": "rgba(191, 255, 0, 0.8)"       # New Features / Prototype
}

# Define colors for Functional Requirement classes
FR_CLASSES = {
    "FR_Framework": COLORS["RED"],
    "FR_Design": COLORS["BLUE"],
    "FR_ComplianceModel": COLORS["GREEN"]
}

# Define colors for System Requirement classes
SR_CLASSES = {
    "SR_Dashboard": COLORS["ORANGE"],
    "SR_Report": COLORS["PURPLE"],
    "SR_AnalyticFeatures": COLORS["YELLOW"],
    "SR_Modeling": COLORS["TEAL"],
    "SR_NonFunctional": COLORS["PINK"],
    "SR_UserInterface": COLORS["BROWN"],
}

# Define colors for System Requirement classes
REF_CLASSES = {
    "REF_Standard": COLORS["BROWN"],
    "REF_Literature": COLORS["LIME"],
}

# DATA: [Source, Target, Value, SourceClass, TargetClass]
REQUIREMENTS_DATA = [
    # Reference -> FR
    ["ISO 37301", "FRQ1 - In order to allow the operator to perform an investigation the system shall provision the accessibility to and adequate handling of resources under investigation and in use", 1, "REF_Standard", "FR_Framework"],
    ["NIST SP-800-61", "FRQ1 - In order to allow the operator to perform an investigation the system shall provision the accessibility to and adequate handling of resources under investigation and in use", 1, "REF_Standard", "FR_Framework"],
    ["COBIT", "FRQ2 - The operator shall be competent in tool operation and compliance assessment", 1, "REF_Standard", "FR_Framework"],
    ["ISO 37301", "FRQ2 - The operator shall be competent in tool operation and compliance assessment", 1, "REF_Standard", "FR_Framework"],
    ["COBIT", "FRQ3 - The operator shall be able to analyse the organization's policy for IM process implementation against a reference model", 1, "REF_Standard", "FR_Framework"],
    ["COBIT", "FRQ4 - The operator shall be capable to see a high-level overview of analyzed incidents, the reference model and required assessment security controls", 1, "REF_Standard", "FR_Framework"],
    ["ISO 19011", "FRQ4 - The operator shall be capable to see a high-level overview of analyzed incidents, the reference model and required assessment security controls", 1, "REF_Standard", "FR_Framework"],
    ["COBIT", "FRQ5 - The operator shall be able to timely identify and analyze the main process errors using predefined metrics and methods for analysis and evaluation", 1, "REF_Standard", "FR_Framework"],
    ["ISO 37301", "FRQ5 - The operator shall be able to timely identify and analyze the main process errors using predefined metrics and methods for analysis and evaluation", 1, "REF_Standard", "FR_Framework"],
    ["NIST SP-800-61", "FRQ5 - The operator shall be able to timely identify and analyze the main process errors using predefined metrics and methods for analysis and evaluation", 1, "REF_Standard", "FR_Framework"],
    ["COBIT", "FRQ6 - The operator shall be able to identify and analyze procedure and impact metrics of resolved and closed incidents", 1, "REF_Standard", "FR_Framework"],
    ["COBIT", "FRQ7 - The operator shall be able to identify the temporal compliance development and areas of concern", 1, "REF_Standard", "FR_Framework"],
    ["NIST SP-800-61", "FRQ7 - The operator shall be able to identify the temporal compliance development and areas of concern", 1, "REF_Standard", "FR_Framework"],
    ["COBIT", "FRQ8 - The operator shall be capable to control or correct individual or multiple incident traces in order to predict the influence on the overall IM compliance", 1, "REF_Standard", "FR_Framework"],
    ["ISO 37301", "FRQ8 - The operator shall be capable to control or correct individual or multiple incident traces in order to predict the influence on the overall IM compliance", 1, "REF_Standard", "FR_Framework"],
    ["NIST SP-800-61", "FRQ8 - The operator shall be capable to control or correct individual or multiple incident traces in order to predict the influence on the overall IM compliance", 1, "REF_Standard", "FR_Framework"],
    ["COBIT", "FRQ9 - The operator shall be able to identify and analyze details of the most critical errors", 1, "REF_Standard", "FR_Framework"],
    ["ISO 27035-3", "FRQ9 - The operator shall be able to identify and analyze details of the most critical errors", 1, "REF_Standard", "FR_Framework"],
    ["NIST SP-800-61", "FRQ9 - The operator shall be able to identify and analyze details of the most critical errors", 1, "REF_Standard", "FR_Framework"],
    ["ISO 27035-1", "FRQ10 - The operator shall be capable to produce an assessment report from analysis and evaluation of the IM log", 1, "REF_Standard", "FR_Framework"],
    ["ISO 27035-2", "FRQ10 - The operator shall be capable to produce an assessment report from analysis and evaluation of the IM log", 1, "REF_Standard", "FR_Framework"],
    ["ISO 37301", "FRQ10 - The operator shall be capable to produce an assessment report from analysis and evaluation of the IM log", 1, "REF_Standard", "FR_Framework"],
    ["ISO 19011", "FRQ10 - The operator shall be capable to produce an assessment report from analysis and evaluation of the IM log", 1, "REF_Standard", "FR_Framework"],
    ["ISO 27035-2", "FRQ11 - The system shall adhere to legal and regulatory documents", 1, "REF_Standard", "FR_Framework"],

    ["Galesic M, Garcia-Retamero R. Graph Literacy: A Cross-Cultural Comparison. Medical Decision Making. 2011;31(3):444-457. doi:10.1177/0272989X10373805", "DRQ1 - User Interface and Competence", 1, "REF_Literature", "FR_Design"],
    ["M. Schufrin, H. Lücke-Tieke and J. Kohlhammer, Visual Firewall Log Analysis - At the Border Between Analytical and Appealing, 2022 IEEE Symposium on Visualization for Cyber Security (VizSec), Oklahoma City, OK, USA, 2022, pp. 1-11, doi: 10.1109/VizSec56996.2022.9941462.", "DRQ1 - User Interface and Competence", 1, "REF_Literature", "FR_Design"],
    ["Macedo, I., Wanous, S., Oliveira, N., Sousa, O., Praça, I. (2021). A Tool to Support the Investigation and Visualization of Cyber and/or Physical Incidents. In: Rocha, Á., Adeli, H., Dzemyda, G., Moreira, F., Ramalho Correia, A.M. (eds) Trends and Applications in Information Systems and Technologies. WorldCIST 2021. Advances in Intelligent Systems and Computing, vol 1368. Springer, Cham. https://doi.org/10.1007/978-3-030-72654-6_13", "DRQ1 - User Interface and Competence", 1, "REF_Literature", "FR_Design"],
    ["Gall, M., Rinderle-Ma, S. (2021). Evaluating Compliance State Visualizations for Multiple Process Models and Instances. In: Polyvyanyy, A., Wynn, M.T., Van Looy, A., Reichert, M. (eds) Business Process Management Forum. BPM 2021. Lecture Notes in Business Information Processing, vol 427. Springer, Cham. https://doi.org/10.1007/978-3-030-85440-9_8", "DRQ1 - User Interface and Competence", 1, "REF_Literature", "FR_Design"],
    ["R. Gove, Automatic Narrative Summarization for Visualizing Cyber Security Logs and Incident Reports, in IEEE Transactions on Visualization and Computer Graphics, vol. 28, no. 1, pp. 1182-1190, Jan. 2022, doi: 10.1109/TVCG.2021.3114843.", "DRQ1 - User Interface and Competence", 1, "REF_Literature", "FR_Design"],
    ["R. Gove, Automatic Narrative Summarization for Visualizing Cyber Security Logs and Incident Reports, in IEEE Transactions on Visualization and Computer Graphics, vol. 28, no. 1, pp. 1182-1190, Jan. 2022, doi: 10.1109/TVCG.2021.3114843.", "DRQ1 - User Interface and Competence", 1, "REF_Literature", "FR_Design"],
    ["Peter Bodesinsky, Paolo Federico, and Silvia Miksch. 2013. Visual Analysis of Compliance with Clinical Guidelines. In Proceedings of the 13th International Conference on Knowledge Management and Knowledge Technologies (i-Know '13). Association for Computing Machinery, New York, NY, USA, Article 12, 1–8. https://doi.org/10.1145/2494188.2494202", "DRQ2 - Assessment Management", 1, "REF_Literature", "FR_Design"],
    ["S. Jamil, J. D. Aeiker and D. R. Crow, Auditing is key, in IEEE Industry Applications Magazine, vol. 16, no. 1, pp. 47-56, January-February 2010, doi: 10.1109/MIAS.2009.934968.", "DRQ3 - Templates", 1, "REF_Literature", "FR_Design"],
    ["Graeme Horsman, Part 2:- quality assurance mechanisms for digital forensic investigations: Knowledge sharing and the Capsule of Digital Evidence (CODE), Forensic Science International: Reports, Volume 2, 2020,100035, ISSN 2665-9107, https://doi.org/10.1016/j.fsir.2019.100035.", "DRQ4 - Documentation Management", 1, "REF_Literature", "FR_Design"],
    ["R. Gove, Automatic Narrative Summarization for Visualizing Cyber Security Logs and Incident Reports, in IEEE Transactions on Visualization and Computer Graphics, vol. 28, no. 1, pp. 1182-1190, Jan. 2022, doi: 10.1109/TVCG.2021.3114843.", "DRQ5 - Assessment Execution", 1, "REF_Literature", "FR_Design"],
    ["Graeme Horsman, Part 2:- quality assurance mechanisms for digital forensic investigations: Knowledge sharing and the Capsule of Digital Evidence (CODE), Forensic Science International: Reports, Volume 2, 2020,100035, ISSN 2665-9107, https://doi.org/10.1016/j.fsir.2019.100035.", "DRQ6 - Issue Management", 1, "REF_Literature", "FR_Design"],
    ["M. Schufrin, H. Lücke-Tieke and J. Kohlhammer, Visual Firewall Log Analysis - At the Border Between Analytical and Appealing, 2022 IEEE Symposium on Visualization for Cyber Security (VizSec), Oklahoma City, OK, USA, 2022, pp. 1-11, doi: 10.1109/VizSec56996.2022.9941462.", "DRQ7 - Reporting and Analytics", 1, "REF_Literature", "FR_Design"],
    ["Li, C., Ge, J., Li, Z., Huang, L., Yang, H., Luo, B.: Monitoring interactions across multi business processes with token carried data. IEEE Transactions on Services Computing pp. 1–1 (2018)", "DRQ8 - Compliance Monitoring", 1, "REF_Literature", "FR_Design"],
    ["Talamo, M., Povilionis, A., Arcieri, F., Schunck, C.H.: Providing online operational support for distributed, security sensitive electronic business processes. In: Int. Carnahan Conf. on Security Technology. pp. 49–54 (2015)", "DRQ8 - Compliance Monitoring", 1, "REF_Literature", "FR_Design"],
    ["Böhmer, K., Rinderle-Ma, S.: Multi-perspective anomaly detection in business process execution events. In: OTM Confederated Int. Conferences ”On the Move to Meaningful Internet Systems”. pp. 80–98. Springer (2016)", "DRQ8 - Compliance Monitoring", 1, "REF_Literature", "FR_Design"],
    ["Fazzinga, B., Folino, F., Furfaro, F., Pontieri, L.: An ensemble-based approach to the security-oriented classification of low-level log traces. Expert Systems with Applications 153, 113386 (2020)", "DRQ8 - Compliance Monitoring", 1, "REF_Literature", "FR_Design"],
    ["Gschwandtner, T. (2017). Visual Analytics Meets Process Mining: Challenges and Opportunities. In: Ceravolo, P., Rinderle-Ma, S. (eds) Data-Driven Process Discovery and Analysis. SIMPDA 2015. Lecture Notes in Business Information Processing, vol 244. Springer, Cham. https://doi.org/10.1007/978-3-319-53435-0_7", "DRQ9 - Frontend Scalability", 1, "REF_Literature", "FR_Design"],
    ["Rafiei, M., Schnitzler, A. and van der Aalst, W.M., 2021. PC4PM: A tool for privacy/confidentiality preservation in process mining. arXiv preprint arXiv:2107.14499.", "DRQ10 - Security of Resources", 1, "REF_Literature", "FR_Design"],
    ["M. Felderer, C. Haisjackl, R. Breu, and J. Motz, “Integrating Manual and Automatic Risk Assessment for Risk-Based Testing,” in Software Quality. Process Automation in Software Development, vol. 94, S. Biffl, D. Winkler, and J. Bergsmann, Eds., in Lecture Notes in Business Information Processing, vol. 94. , Berlin, Heidelberg: Springer Berlin Heidelberg, 2012, pp. 159–180. doi: 10.1007/978-3-642-27213-4_11.", "DRQ11 - Automated assessment security controls", 1, "REF_Literature", "FR_Design"],
    ["Fischer, F., Fuchs, J., Mansmann, F., & Keim, D. A. (2015). BANKSAFE: Visual analytics for big data in large-scale computer networks. Information Visualization, 14(1), 51-61. https://doi.org/10.1177/1473871613488572", "DRQ12 - Backend Scalability", 1, "REF_Literature", "FR_Design"],
    ["L. Zhang et al., Visual analytics for the big data era — A comparative review of state-of-the-art commercial systems, 2012 IEEE Conference on Visual Analytics Science and Technology (VAST), Seattle, WA, USA, 2012, pp. 173-182, doi: 10.1109/VAST.2012.6400554.", "DRQ12 - Backend Scalability", 1, "REF_Literature", "FR_Design"],
    ["Masiello, Italo, Zeynab (Artemis) Mohseni, Francis Palma, Susanna Nordmark, Hanna Augustsson, and Rebecka Rundquist. 2024. A Current Overview of the Use of Learning Analytics Dashboards Education Sciences 14, no. 1: 82. https://doi.org/10.3390/educsci14010082", "DRQ13 - Issue Tracking", 1, "REF_Literature", "FR_Design"],

    ["A. Palma and M. Angelini, Visually Supporting the Assessment of the Incident Management Process. The Eurographics Association, 2024. Accessed: May 31, 2024. [Online]. Available: https://doi.org/10.2312/eurova.20241116", "CMRQ1 - In order to support the operator the system shall be able to suggest mutiple deviation parameterizations based on automated analysis of different IM log KPIs", 1, "REF_Literature", "FR_ComplianceModel"],
    ["A. Palma and M. Angelini, Visually Supporting the Assessment of the Incident Management Process. The Eurographics Association, 2024. Accessed: May 31, 2024. [Online]. Available: https://doi.org/10.2312/eurova.20241116", "CMRQ2 - The operator shall be able to adjust a suggested deviation parameterization in order to build own parameterization that reflects assessment preferences", 1, "REF_Literature", "FR_ComplianceModel"],
    ["A. Palma and M. Angelini, Visually Supporting the Assessment of the Incident Management Process. The Eurographics Association, 2024. Accessed: May 31, 2024. [Online]. Available: https://doi.org/10.2312/eurova.20241116", "CMRQ3 - The operator shall be able to define a new context-aware deviation parameterization in order to handle specific cases for costs of non-compliance causes or if parameterizations shall be based on unidentified IM log KPIs or other reasoning", 1, "REF_Literature", "FR_ComplianceModel"],
    ["A. Palma and M. Angelini, Visually Supporting the Assessment of the Incident Management Process. The Eurographics Association, 2024. Accessed: May 31, 2024. [Online]. Available: https://doi.org/10.2312/eurova.20241116", "CMRQ4 - The operator shall be able to analyze how non-compliance cost is distributed in order to identify patterns and trends", 1, "REF_Literature", "FR_ComplianceModel"],
    ["A. Palma and M. Angelini, Visually Supporting the Assessment of the Incident Management Process. The Eurographics Association, 2024. Accessed: May 31, 2024. [Online]. Available: https://doi.org/10.2312/eurova.20241116", "CMRQ5 - The operator shall be capable to prioritize and select incidents based on their compliance severity in order to isolate severity ranges and determine their root causes", 1, "REF_Literature", "FR_ComplianceModel"],

    # FR -> SR
    ["DRQ1 - User Interface and Competence", "SRQ42 - The system shall be divided into mutiple assessment sections, called Aggregated Views, where each is dedicated to specific functional requirements during the assessment", 1, "FR_Design", "SR_Dashboard"],
    ["FRQ3 - The operator shall be able to analyse the organization's policy for IM process implementation against a reference model", "SRQ1 - The system shall provide an Aggregated View that allows the operator to access the organization's policy for IM process implementation and evaluation against the integrated IM reference model", 1, "FR_Framework", "SR_Dashboard"],
    ["FRQ1 - In order to allow the operator to perform an investigation the system shall provision the accessibility to and adequate handling of resources under investigation and in use", "SRQ1 - The system shall provide an Aggregated View that allows the operator to access the organization's policy for IM process implementation and evaluation against the integrated IM reference model", 1, "FR_Framework", "SR_Dashboard"],
    ["DRQ5 - Assessment Execution", "SRQ1 - The system shall provide an Aggregated View that allows the operator to access the organization's policy for IM process implementation and evaluation against the integrated IM reference model", 1, "FR_Design", "SR_Dashboard"],
    ["FRQ4 - The operator shall be capable to see a high-level overview of analyzed incidents, the reference model and required assessment security controls", "SRQ6 - The system shall provide an Aggregated View to the operator with a high-level overview that displays summarized information on analyzed incidents, average values for key performance metrics, the integrated IM reference model and required assessment activities ", 1, "FR_Framework", "SR_Dashboard"],
    ["DRQ2 - Assessment Management", "SRQ6 - The system shall provide an Aggregated View to the operator with a high-level overview that displays summarized information on analyzed incidents, average values for key performance metrics, the integrated IM reference model and required assessment activities", 1, "FR_Design", "SR_Dashboard"],
    ["DRQ5 - Assessment Execution", "SRQ6 - The system shall provide an Aggregated View to the operator with a high-level overview that displays summarized information on analyzed incidents, average values for key performance metrics, the integrated IM reference model and required assessment activities", 1, "FR_Design", "SR_Dashboard"],
    ["FRQ6 - The operator shall be able to identify and analyze procedure and impact metrics of resolved and closed incidents", "SRQ11 - The system shall provide an Aggregated View that contains incidents and process statistics regarding the activation and detection as well as resolving and closure of incidents", 1, "FR_Framework", "SR_Dashboard"],
    ["FRQ7 - The operator shall be able to identify the temporal compliance development and areas of concern", "SRQ11 - The system shall provide an Aggregated View that contains incidents and process statistics regarding the activation and detection as well as resolving and closure of incidents", 1, "FR_Framework", "SR_Dashboard"],
    ["DRQ5 - Assessment Execution", "SRQ11 - The system shall provide an Aggregated View that contains incidents and process statistics regarding the activation and detection as well as resolving and closure of incidents", 1, "FR_Design", "SR_Dashboard"],
    ["FRQ7 - The operator shall be able to identify the temporal compliance development and areas of concern", "SRQ13 - The system shall provide an Aggregated View that allows to analyze the compliance development within the selected time period", 1, "FR_Framework", "SR_Dashboard"],
    ["CMRQ4 - The operator shall be able to analyze how non-compliance cost is distributed in order to identify patterns and trends", "SRQ13 - The system shall provide an Aggregated View that allows to analyze the compliance development within the selected time period", 1, "FR_ComplianceModel", "SR_Dashboard"],
    ["DRQ5 - Assessment Execution", "SRQ13 - The system shall provide an Aggregated View that allows to analyze the compliance development within the selected time period", 1, "FR_Design", "SR_Dashboard"],
    ["FRQ7 - The operator shall be able to identify the temporal compliance development and areas of concern", "SRQ15 - The system shall provide an Aggregated View that allows to analyze incident characteristics and details of selected incidents that are critical or belong to areas of concern", 1, "FR_Framework", "SR_Dashboard"],
    ["FRQ9 - The operator shall be able to identify and analyze details of the most critical errors", "SRQ15 - The system shall provide an Aggregated View that allows to analyze incident characteristics and details of selected incidents that are critical or belong to areas of concern", 1, "FR_Framework", "SR_Dashboard"],
    ["CMRQ5 - The operator shall be capable to prioritize and select incidents based on their compliance severity in order to isolate severity ranges and determine their root causes", "SRQ15 - The system shall provide an Aggregated View that allows to analyze incident characteristics and details of selected incidents that are critical or belong to areas of concern", 1, "FR_ComplianceModel", "SR_Dashboard"],
    ["DRQ5 - Assessment Execution", "SRQ15 - The system shall provide an Aggregated View that allows to analyze incident characteristics and details of selected incidents that are critical or belong to areas of concern", 1, "FR_Design", "SR_Dashboard"],
    ["FRQ8 - The operator shall be capable to control or correct individual or multiple incident traces in order to predict the influence on the overall IM compliance", "SRQ32 - The system shall provide an Aggregaetd View that is dedicated to the What-if analysis", 1, "FR_Framework", "SR_Dashboard"],
    ["DRQ5 - Assessment Execution", "SRQ32 - The system shall provide an Aggregaetd View that is dedicated to the What-if analysis", 1, "FR_Design", "SR_Dashboard"],
    ["CMRQ1 - In order to support the operator the system shall be able to suggest mutiple deviation parameterizations based on automated analysis of different IM log KPIs", "SRQ41 - The system shall provide an Aggregated View that is dedicated to cost model parameterization", 1, "FR_ComplianceModel", "SR_Dashboard"],
    ["CMRQ2 - The operator shall be able to adjust a suggested deviation parameterization in order to build own parameterization that reflects assessment preferences", "SRQ41 - The system shall provide an Aggregated View that is dedicated to cost model parameterization", 1, "FR_ComplianceModel", "SR_Dashboard"],
    ["CMRQ3 - The operator shall be able to define a new context-aware deviation parameterization in order to handle specific cases for costs of non-compliance causes or if parameterizations shall be based on unidentified IM log KPIs or other reasoning", "SRQ41 - The system shall provide an Aggregated View that is dedicated to cost model parameterization", 1, "FR_ComplianceModel", "SR_Dashboard"],
    ["DRQ5 - Assessment Execution", "SRQ41 - The system shall provide an Aggregated View that is dedicated to cost model parameterization", 1, "FR_Design", "SR_Dashboard"],
    ["DRQ7 - Reporting and Analytics", "SRQ43 - The system shall provide an Aggregated View that is dedicated to the global assessment progress", 1, "FR_Design", "SR_Dashboard"],
    ["FRQ10 - The operator shall be capable to produce an assessment report from analysis and evaluation of the IM log", "SRQ20 - The system shall enable the operator to produce an assessment report from the reported sections", 1, "FR_Framework", "SR_Report"],
    ["DRQ7 - Reporting and Analytics", "SRQ20 - The system shall enable the operator to produce an assessment report from the reported sections", 1, "FR_Design", "SR_Report"],
    ["FRQ3 - The operator shall be able to analyse the organization's policy for IM process implementation against a reference model", "SRQ5 - The system shall generate a report section that lists any deviations found between the organization's policy for IM process implementation and the integrated IM reference model", 1, "FR_Framework", "SR_Report"],
    ["DRQ2 - Assessment Management", "SRQ5 - The system shall generate a report section that lists any deviations found between the organization's policy for IM process implementation and the integrated IM reference model", 1, "FR_Design", "SR_Report"],
    ["FRQ4 - The operator shall be capable to see a high-level overview of analyzed incidents, the reference model and required assessment security controls", "SRQ9 - The system shall generate a report section that includes the assessment criteria and justfies how results will be evaluated against assessment criteria", 1, "FR_Framework", "SR_Report"],
    ["FRQ6 - The operator shall be able to identify and analyze procedure and impact metrics of resolved and closed incidents", "SRQ12 - The system shall provide a report section dedicated to the detection and activation as well as resolving and closure procedure of incidents", 1, "FR_Framework", "SR_Report"],
    ["FRQ7 - The operator shall be able to identify the temporal compliance development and areas of concern", "SRQ16 - The system shall provide a report section that is dedicated to temporal compliance development and areas of concern ", 1, "FR_Framework", "SR_Report"],
    ["FRQ9 - The operator shall be able to identify and analyze details of the most critical errors", "SRQ19 - The system shall provide a report section dedicated to the most critical incidents in terms of fitness, non-compliance costs and exceeded response times", 1, "FR_Framework", "SR_Report"],

    ["FRQ10 - The operator shall be capable to produce an assessment report from analysis and evaluation of the IM log", "SRQ21-A - The system shall provide a report subsection within a section that is dedicated to the assessed time period, past asessments and changes to the used assessment framework if available", 1, "FR_Framework", "SR_Report"],
    ["DRQ7 - Reporting and Analytics", "SRQ21-A - The system shall provide a report subsection within a section that is dedicated to the assessed time period, past asessments and changes to the used assessment framework if available", 1, "FR_Design", "SR_Report"],

    ["FRQ10 - The operator shall be capable to produce an assessment report from analysis and evaluation of the IM log", "SRQ21-B - The system shall provide a report subsection within a section that is dedicated to the versioning and, if applicable, changes in the versioning of the currently used assessment framework if available", 1, "FR_Framework", "SR_Report"],
    ["DRQ7 - Reporting and Analytics", "SRQ21-B - The system shall provide a report subsection within a section that is dedicated to the versioning and, if applicable, changes in the versioning of the currently used assessment framework if available", 1, "FR_Design", "SR_Report"],

    ["FRQ10 - The operator shall be capable to produce an assessment report from analysis and evaluation of the IM log", "SRQ25 - The system shall store all the reports to allow reproducibility of the analyses", 1, "FR_Framework", "SR_Report"],
    ["DRQ7 - Reporting and Analytics", "SRQ25 - The system shall store all the reports to allow reproducibility of the analyses", 1, "FR_Design", "SR_Report"],
    ["FRQ10 - The operator shall be capable to produce an assessment report from analysis and evaluation of the IM log", "SRQ26 - The system shall provide a report section that explains effectiveness, sufficiency and provides recommendations from an assessment", 1, "FR_Framework", "SR_Report"],
    ["FRQ8 - The operator shall be capable to control or correct individual or multiple incident traces in order to predict the influence on the overall IM compliance", "SRQ33 - The system shall provide a report section that is dedicated to what-if analysis", 1, "FR_Framework", "SR_Report"],
    ["DRQ7 - Reporting and Analytics", "SRQ44 - The system shall provide a functionality to export the produced assessment report", 1, "FR_Design", "SR_Report"],

    ["FRQ3 - The operator shall be able to analyse the organization's policy for IM process implementation against a reference model", "SRQ3 - The system shall provide a functionality to compare the organization's policy for IM process implementation with the integrated IM reference model", 1, "FR_Framework", "SR_AnalyticFeatures"],
    ["DRQ2 - Assessment Management", "SRQ3 - The system shall provide a functionality to compare the organization's policy for IM process implementation with the integrated IM reference model", 1, "FR_Design", "SR_AnalyticFeatures"],

    ["FRQ3 - The operator shall be able to analyse the organization's policy for IM process implementation against a reference model", "SRQ4 - The system shall detect possible deviations between the organization's policy for IM process implementation and the integrated reference model if prior is processable", 1, "FR_Framework", "SR_AnalyticFeatures"],
    ["DRQ2 - Assessment Management", "SRQ4 - The system shall detect possible deviations between the organization's policy for IM process implementation and the integrated reference model if prior is processable", 1, "FR_Design", "SR_AnalyticFeatures"],
    
    ["FRQ4 - The operator shall be capable to see a high-level overview of analyzed incidents, the reference model and required assessment security controls", "SRQ7 - The system shall enable the operator to check if information is complete, correct, consistent and current", 1, "FR_Framework", "SR_AnalyticFeatures"],

    ["FRQ4 - The operator shall be capable to see a high-level overview of analyzed incidents, the reference model and required assessment security controls", "SRQ8 - The system shall provide digital checklists as well as the possibility to define and/or automatically suggest assessment security controls", 1, "FR_Framework", "SR_AnalyticFeatures"],
    ["DRQ3 - Templates", "SRQ8 - The system shall provide digital checklists as well as the possibility to define and/or automatically suggest assessment security controls", 1, "FR_Design", "SR_AnalyticFeatures"],
    ["DRQ11 - Automated assessment security controls", "SRQ8 - The system shall provide digital checklists as well as the possibility to define and/or automatically suggest assessment security controls", 1, "FR_Design", "SR_AnalyticFeatures"],

    ["FRQ6 - The operator shall be able to identify and analyze procedure and impact metrics of resolved and closed incidents", "SRQ10 - The system shall enable the operator to identify the activation and detection as well as resolving and closure procedure of incidents through suitable metrics", 1, "FR_Framework", "SR_AnalyticFeatures"],
    ["FRQ7 - The operator shall be able to identify the temporal compliance development and areas of concern", "SRQ10 - The system shall enable the operator to identify the activation and detection as well as resolving and closure procedure of incidents through suitable metrics", 1, "FR_Framework", "SR_AnalyticFeatures"],


    ["FRQ7 - The operator shall be able to identify the temporal compliance development and areas of concern", "SRQ14 - The system shall enable the operator to analyze multiple incidents to identify trends and patterns as areas of concern", 1, "FR_Framework", "SR_AnalyticFeatures"],
    ["CMRQ4 - The operator shall be able to analyze how non-compliance cost is distributed in order to identify patterns and trends", "SRQ14 - The system shall enable the operator to analyze multiple incidents to identify trends and patterns as areas of concern", 1, "FR_ComplianceModel", "SR_AnalyticFeatures"],

    ["FRQ9 - The operator shall be able to identify and analyze details of the most critical errors", "SRQ17 - The system shall enable the operator to prioritize and analyze details of the most critical incidents with respect to fitness and non-compliance cost individually", 1, "FR_Framework", "SR_AnalyticFeatures"],
    ["CMRQ5 - The operator shall be capable to prioritize and select incidents based on their compliance severity in order to isolate severity ranges and determine their root causes", "SRQ17 - The system shall enable the operator to prioritize and analyze details of the most critical incidents with respect to fitness and non-compliance cost individually", 1, "FR_ComplianceModel", "SR_AnalyticFeatures"],

    ["FRQ10 - The operator shall be capable to produce an assessment report from analysis and evaluation of the IM log", "SRQ23 - The system shall retain assessment findings, areas of concern and non-conformities during an assessment", 1, "FR_Framework", "SR_AnalyticFeatures"],
    ["DRQ13 - Issue Tracking", "SRQ23 - The system shall retain assessment findings, areas of concern and non-conformities during an assessment", 1, "FR_Design", "SR_AnalyticFeatures"],
    ["DRQ6 - Issue Management", "SRQ23 - The system shall retain assessment findings, areas of concern and non-conformities during an assessment", 1, "FR_Design", "SR_AnalyticFeatures"],

    ["FRQ5 - The operator shall be able to timely identify and analyze the main process errors using predefined metrics and methods for analysis and evaluation", "SRQ27 - The system shall implement and maintain the controls to monitor and assess the IM log in order to meet compliance obligations and deduce compliance risks", 1, "FR_Framework", "SR_AnalyticFeatures"],

    ["FRQ8 - The operator shall be capable to control or correct individual or multiple incident traces in order to predict the influence on the overall IM compliance", "SRQ31 - The system shall provide the operator with basic tools to perform what-if analysis towards the IM log to determine if changes to organization's IM affect the IM compliance performance", 1, "FR_Framework", "SR_AnalyticFeatures"],

    ["CMRQ1 - In order to support the operator the system shall be able to suggest mutiple deviation parameterizations based on automated analysis of different IM log KPIs", "SRQ38 - The system shall suggest multiple deviation paramterizations based on different IM log KPIs", 1, "FR_ComplianceModel", "SR_AnalyticFeatures"],

    ["CMRQ2 - The operator shall be able to adjust a suggested deviation parameterization in order to build own parameterization that reflects assessment preferences", "SRQ39 - The system shall allow the operator to adjust a suggested deviation parameterization that reflects assessment preferences", 1, "FR_ComplianceModel", "SR_AnalyticFeatures"],

    ["CMRQ3 - The operator shall be able to define a new context-aware deviation parameterization in order to handle specific cases for costs of non-compliance causes or if parameterizations shall be based on unidentified IM log KPIs or other reasoning", "SRQ40 - The system shall allow the operator to define a new context-aware deviation parameterization independently", 1, "FR_ComplianceModel", "SR_AnalyticFeatures"],

    ["DRQ9 - Frontend Scalability", "SRQ47 - The system shall be capable to limit the assessed data of the IM log to a specific time period", 1, "FR_Design", "SR_AnalyticFeatures"],

    ["FRQ3 - The operator shall be able to analyse the organization's policy for IM process implementation against a reference model", "SRQ2 - The system shall model an IM reference model based on a standard or framework for IM processes", 1, "FR_Framework", "SR_Modeling"],
    ["DRQ2 - Assessment Management", "SRQ2 - The system shall model an IM reference model based on a standard or framework for IM processes", 1, "FR_Design", "SR_Modeling"],

    ["FRQ4 - The operator shall be capable to see a high-level overview of analyzed incidents, the reference model and required assessment security controls", "SRQ28 - The system shall determine metrics to measure how activities deviate from and impact compliance to the reference model", 1, "FR_Framework", "SR_Modeling"],
    ["FRQ5 - The operator shall be able to timely identify and analyze the main process errors using predefined metrics and methods for analysis and evaluation", "SRQ28 - The system shall determine metrics to measure how activities deviate from and impact compliance to the reference model", 1, "FR_Framework", "SR_Modeling"],
    ["FRQ6 - The operator shall be able to identify and analyze procedure and impact metrics of resolved and closed incidents", "SRQ28 - The system shall determine metrics to measure how activities deviate from and impact compliance to the reference model", 1, "FR_Framework", "SR_Modeling"],
    ["FRQ7 - The operator shall be able to identify the temporal compliance development and areas of concern", "SRQ28 - The system shall determine metrics to measure how activities deviate from and impact compliance to the reference model", 1, "FR_Framework", "SR_Modeling"],
    ["FRQ9 - The operator shall be able to identify and analyze details of the most critical errors", "SRQ28 - The system shall determine metrics to measure how activities deviate from and impact compliance to the reference model", 1, "FR_Framework", "SR_Modeling"],
    ["CMRQ4 - The operator shall be able to analyze how non-compliance cost is distributed in order to identify patterns and trends", "SRQ28 - The system shall determine metrics to measure how activities deviate from and impact compliance to the reference model", 1, "FR_ComplianceModel", "SR_Modeling"],

    ["FRQ10 - The operator shall be capable to produce an assessment report from analysis and evaluation of the IM log", "SRQ22 - The system shall produce system logs during an assessment to follow all assessment steps taken by the operator", 1, "FR_Framework", "SR_NonFunctional"],
    ["DRQ4 - Documentation Management", "SRQ22 - The system shall produce system logs during an assessment to follow all assessment steps taken by the operator", 1, "FR_Design", "SR_NonFunctional"],

    ["FRQ10 - The operator shall be capable to produce an assessment report from analysis and evaluation of the IM log", "SRQ24 - The system shall ensure appropriate identification and description, format and media when creating or updating information", 1, "FR_Framework", "SR_NonFunctional"],

    ["FRQ5 - The operator shall be able to timely identify and analyze the main process errors using predefined metrics and methods for analysis and evaluation", "SRQ30 - The system shall maintain a description for each function that processes data of the IM log for analysis and evaluation", 1, "FR_Framework", "SR_NonFunctional"],

    ["FRQ11 - The system shall adhere to legal and regulatory documents", "SRQ35 - The system shall ensure Data Protection and Privacy based on EU regulations (GDPR) and directives as well as other mandatory legal requirements", 1, "FR_Framework", "SR_NonFunctional"],
    ["DRQ4 - Documentation Management", "SRQ35 - The system shall ensure Data Protection and Privacy based on EU regulations (GDPR) and directives as well as other mandatory legal requirements", 1, "FR_Design", "SR_NonFunctional"],

    ["FRQ11 - The system shall adhere to legal and regulatory documents", "SRQ36 - The system shall communicate its Use Policy to the operator prior to start of the assessment", 1, "FR_Framework", "SR_NonFunctional"],
    ["DRQ4 - Documentation Management", "SRQ36 - The system shall communicate its Use Policy to the operator prior to start of the assessment", 1, "FR_Design", "SR_NonFunctional"],

    ["FRQ1 - In order to allow the operator to perform an investigation the system shall provision the accessibility to and adequate handling of resources under investigation and in use", "SRQ37 - The system shall provision the accessibility to and adequate handling of the organization's IM process implementation documents and the IM log that is to be assessed", 1, "FR_Framework", "SR_NonFunctional"],
    ["DRQ10 - Security of Resources", "SRQ37 - The system shall provision the accessibility to and adequate handling of the organization's IM process implementation documents and the IM log that is to be assessed", 1, "FR_Design", "SR_NonFunctional"],

    ["DRQ8 - Compliance Monitoring", "SRQ45 - The system shall support real-time capabilities", 1, "FR_Design", "SR_NonFunctional"],

    ["DRQ12 - Backend Scalability", "SRQ48 - The system shall seperate computational resources from resources for UX in order to ensure that neither depletes the other's resources", 1, "FR_Design", "SR_NonFunctional"],
    ["FRQ5 - The operator shall be able to timely identify and analyze the main process errors using predefined metrics and methods for analysis and evaluation", "SRQ49 - The system shall maintain a description for each tool of visualization that is used for analysis and evaluation of the IM log", 1, "FR_Framework", "SR_NonFunctional"],

    ["FRQ5 - The operator shall be able to timely identify and analyze the main process errors using predefined metrics and methods for analysis and evaluation", "SRQ29 - The system shall enable the operator to assess the IM log in a timely manner", 1, "FR_Framework", "SR_UserInterface"],
    ["DRQ8 - Compliance Monitoring", "SRQ29 - The system shall enable the operator to assess the IM log in a timely manner", 1, "FR_Design", "SR_UserInterface"],

    ["FRQ2 - The operator shall be competent in tool operation and compliance assessment", "SRQ34 - The system shall allow the operator with experience in the domain of IM to use it effectively without prior training by adopting best practices in interface design, naming conventions, help and support, workflows, visual feedback, accessibility and consistency", 1, "FR_Framework", "SR_UserInterface"],
    ["DRQ1 - User Interface and Competence", "SRQ34 - The system shall allow the operator with experience in the domain of IM to use it effectively without prior training by adopting best practices in interface design, naming conventions, help and support, workflows, visual feedback, accessibility and consistency", 1, "FR_Design", "SR_UserInterface"],
    ["DRQ5 - Assessment Execution", "SRQ34 - The system shall allow the operator with experience in the domain of IM to use it effectively without prior training by adopting best practices in interface design, naming conventions, help and support, workflows, visual feedback, accessibility and consistency", 1, "FR_Design", "SR_UserInterface"],

    ["DRQ9 - Frontend Scalability", "SRQ46 - The system shall make use of a frontend that is scalable", 1, "FR_Design", "SR_UserInterface"],



]