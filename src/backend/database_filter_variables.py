# This file contains all the globval database variables for
import eel
import json

assessment_filters = {
    "filters": {
        "compliance_metric": "fitness",
        "cost_function": {
            "missing": {"N":0.2,"A":0.05, "W":0, "R":0.45,"C":0.30},
            "repetition": {"N":0.1,"A":0.2,"W":0.1,"R":0.3,"C":0.3},
            "mismatch": {"N":0.1,"A":0.25,"W":0.2,"R":0.3,"C":0.15},
            "cost": {"missing":0.4,"repetition":0.2,"mismatch":0.4},
        }, 
        "thresholds": {
            "compliance_metric_severity_levels": {
                "low": ">= 0.85 AND <= 1",
                "moderate": ">= 0.65 AND < 0.85",
                "high": ">= 0.5 AND < 0.65",
                "critical": ">= 0 AND <= 0.5"
            },
            "compliance_metric_severity_levels2": {
                "fitness": {
                    "low": ">= 0.85 AND <= 1",
                    "moderate": ">= 0.65 AND < 0.85",
                    "high": ">= 0.5 AND < 0.65",
                    "critical": ">= 0 AND <= 0.5"
                },
                "cost": {
                    "low": ">= 0.0 AND < 0.1",
                    "moderate": ">= 0.1 AND < 0.2",
                    "high": ">= 0.2 AND < 0.3",
                    "critical": ">= 0.3 AND <= 2.0"
                }
            },
            "detection": {
                "acceptableTime": "<= 1440",
                "nonAcceptableTime": ">= 2880",
                "deviations": {
                    "acceptableMissing": "<=20",
                    "acceptableRepetition": "<=500",
                    "acceptableMismatch": "<=5"
                },
                "fitness": {
                    "acceptableCompliance": ">= 0.10 AND <= 0.2",
                },
                "cost": {
                    "acceptableCompliance": "<= 0.05",
                }
            },
            "activation": {
                "acceptableTime": "<= 4320",
                "nonAcceptableTime": ">= 7200",
                "deviations": {
                    "acceptableMissing": "<=200",
                    "acceptableRepetition": "<=500",
                    "acceptableMismatch": "<=50"
                },
                "fitness": {
                    "acceptableCompliance": ">= 0.15 AND <= 0.2",
                },
                "cost": {
                    "acceptableCompliance": "<= 0.05",
                }
            },
            "awaiting": {
                "acceptableTime": "<= 7200",
                "nonAcceptableTime": ">= 14400",
                "deviations": {
                    "acceptableMissing": "<=100",
                    "acceptableRepetition": "<=200",
                    "acceptableMismatch": "<=20"
                },
                "fitness": {
                    "acceptableCompliance": ">= 0.15 AND <= 0.2",
                },
                "cost": {
                    "acceptableCompliance": "<= 0.05",
                }
            },
            "resolution": {
                "acceptableTime": "<= 2880",
                "nonAcceptableTime": ">= 4320",
                "deviations": {
                    "acceptableMissing": "<=10",
                    "acceptableRepetition": "<=50",
                    "acceptableMismatch": "<=20"
                },
                "fitness": {
                    "acceptableCompliance": ">= 0.15 AND <= 0.2",
                },
                "cost": {
                    "acceptableCompliance": "<= 0.05",
                }
            },
            "closure": {
                "acceptableTime": "<= 720",
                "nonAcceptableTime": ">= 1440",
                "deviations": {
                    "acceptableMissing": "<=100",
                    "acceptableRepetition": "<=50",
                    "acceptableMismatch": "<=5"
                },
                "fitness": {
                    "acceptableCompliance": ">= 0.15 AND <= 0.2",
                },
                "cost": {
                    "acceptableCompliance": "<= 0.05",
                }
            },
        },
        "overview_metrics": {
            "date_range": {
                "min_date": "2016-06-01",
                "max_date": "2016-07-01",
                "closed_incidents_in_time_period": False
            },
            "compliance_bar": {
                "low": False,
                "moderate": False,
                "high": False,
                "critical": False
            }
        },
        "reference_model": {
            "selected_states": False,
        },
        "common_variants": None,
        "statistical_analysis": {
            "perc_sla_met": None,
            "avg_time_to_resolve": None,
            "perc_assigned_to_resolved_by": None,
            "perc_false_positives": None,
        },
        "deviations_distribution": {
            "missing": False,
            "repetition": False,
            "mismatch": False,
        },
        "most_critical_incidents": False,
        "technical_analysis": {
            "symptom": [],
            "impact_level": [],
            "urgency_level": [],
            "priority_level": [],
            "location": [],
            "category": [],
            "subcategory": [],
        },
        "graph_x-axis-sliders": {
            "min_date": False,
            "max_date": False
        },
        "tabular_incident_selection": False,
        "whatIf_Analyis": []
    }
}

@eel.expose
def get_filter_value(path=None):
    """
    Retrieves the value from the assessment_filters dictionary using the dot-separated path.
    If no path is provided, returns the entire assessment_filters dictionary.

    Args:
        path (str, optional): Dot-separated path to the value, e.g., "filters.overview_metrics.date_range.min_date".
                              If not provided, the entire assessment_filters object is returned.

    Returns:
        The value at the specified path, or the entire assessment_filters if no path is provided,
        or None if the path is invalid.

    Interpretation:
        - If a valid dot-separated path is provided, the function traverses the nested assessment_filters dictionary and returns the value at that path.
        - If no path is provided, the function returns the entire assessment_filters dictionary.
        - If the path is invalid (does not exist in the dictionary), the function returns None.
        - The returned value can be any type stored in the dictionary (str, int, float, bool, list, dict).
        - This function is useful for dynamically accessing configuration, filter, or threshold values for analytics, reporting, or backend logic.
        - The output can be directly consumed by JavaScript via Eel for frontend use.
    """
    # If no path is provided, return the entire assessment_filters object
    if not path:
        return assessment_filters

    # Otherwise, retrieve the value using the provided path
    keys = path.split('.')
    value = assessment_filters
    try:
        for key in keys:
            value = value[key]
        return value
    except KeyError:
        return None


@eel.expose
def set_filter_value(path, new_value):
    """
    Sets a new value in the assessment_filters dictionary using the dot-separated path.

    Args:
        path (str): Dot-separated path to the value, e.g., "filters.overview_metrics.date_range.min_date".
        new_value: The new value to set at the specified path.

    Returns:
        bool: True if the value was successfully set, False if the path is invalid.
    """
    keys = path.split('.')
    value = assessment_filters
    try:
        for key in keys[:-1]:
            value = value[key]
        value[keys[-1]] = new_value

        # Print the newly set filter value
        print("database_filter_variables.py")
        print(f"Filter updated: {path} = {new_value}")

        return True
    except KeyError:
        print("database_filter_variables.py")
        print(f"Failed to set filter: {path} is an invalid path.")
        return False


def apply_whatif_analysis_filter():
    """
    Retrieves the 'whatif_analysis' filter and crafts a SQL condition to exclude the specified incident IDs.
    
    Args:
        filters (dict): The filters dictionary returned from get_filter_value().

    Returns:
        str: A SQL fragment to exclude specific incident IDs.
    """

    whatif_analysis_ids = get_filter_value("filters.whatIf_analysis")
    
    if whatif_analysis_ids:
        # Format the incident IDs to exclude for SQL query
        formatted_ids = ', '.join(f"'{incident_id}'" for incident_id in whatif_analysis_ids)
        return f"incident_id NOT IN ({formatted_ids})"
    
    return ""


#incident_ids_from_time_period = ['INC0121064']
incident_ids_from_time_period = ['INC0000324', 'INC0000337', 'INC0001259', 'INC0001636', 'INC0001795', 'INC0001869', 'INC0001996', 'INC0002026', 'INC0002089', 'INC0002138', 'INC0002569', 'INC0002715', 'INC0003150', 'INC0003228', 'INC0003430', 'INC0003513', 'INC0003529', 'INC0005612', 'INC0005831', 'INC0005979', 'INC0006056', 'INC0006096', 'INC0006142', 'INC0006153', 'INC0006384', 'INC0006442', 'INC0007273', 'INC0007399', 'INC0008267', 'INC0008342', 'INC0008631', 'INC0008691', 'INC0008746', 'INC0008908', 'INC0008938', 'INC0009259', 'INC0009444', 'INC0009537', 'INC0009673', 'INC0009713', 'INC0009715', 'INC0009995', 'INC0010087', 'INC0010164', 'INC0010181', 'INC0010214', 'INC0010304', 'INC0010466', 'INC0010502', 'INC0010681', 'INC0010728', 'INC0010730', 'INC0010924', 'INC0011180', 'INC0011182', 'INC0011184', 'INC0011636', 'INC0011776', 'INC0012132', 'INC0012441', 'INC0012623', 'INC0012737', 'INC0012869', 'INC0013244', 'INC0013553', 'INC0013702', 'INC0013947', 'INC0014164', 'INC0014787', 'INC0015097', 'INC0015646', 'INC0015847', 'INC0015866', 'INC0016213', 'INC0016469', 'INC0016480', 'INC0016489', 'INC0016491', 'INC0016573', 'INC0016604', 'INC0016607', 'INC0016717', 'INC0016889', 'INC0016969', 'INC0016970', 'INC0017071', 'INC0017127', 'INC0017570', 'INC0017973', 'INC0018125', 'INC0018211', 'INC0018324', 'INC0018611', 'INC0019231', 'INC0019471', 'INC0019617', 'INC0020261', 'INC0020421', 'INC0020505', 'INC0020591', 'INC0020627', 'INC0020783', 'INC0020816', 'INC0020912', 'INC0020963', 'INC0021467', 'INC0021698', 'INC0021700', 'INC0021718', 'INC0021784', 'INC0021875', 'INC0021990', 'INC0022026', 'INC0022109', 'INC0022121', 'INC0022122', 'INC0022255', 'INC0022313', 'INC0022427', 'INC0022627', 'INC0022665', 'INC0022702', 'INC0022840', 'INC0022897', 'INC0022913', 'INC0022935', 'INC0022948', 'INC0023064', 'INC0023125', 'INC0023144', 'INC0023204', 'INC0023234', 'INC0023288', 'INC0023292', 'INC0023303', 'INC0023355', 'INC0023478', 'INC0023534', 'INC0023599', 'INC0023656', 'INC0023676', 'INC0023726', 'INC0023779', 'INC0023794', 'INC0023859', 'INC0023892', 'INC0023996', 'INC0024055', 'INC0024059', 'INC0024072', 'INC0024077', 'INC0024141', 'INC0024148', 'INC0024179', 'INC0024203', 'INC0024258', 'INC0024259', 'INC0024273', 'INC0024382', 'INC0024400', 'INC0024410', 'INC0024426', 'INC0024460', 'INC0024505', 'INC0024661', 'INC0024742', 'INC0024814', 'INC0024815', 'INC0024950', 'INC0024988', 'INC0025099', 'INC0025104', 'INC0025180', 'INC0025197', 'INC0025212', 'INC0025222', 'INC0025229', 'INC0025230', 'INC0025294', 'INC0025396', 'INC0025405', 'INC0025423', 'INC0025457', 'INC0025497', 'INC0025501', 'INC0025575', 'INC0025648', 'INC0025664', 'INC0025674', 'INC0025696', 'INC0025714', 'INC0025755', 'INC0025795', 'INC0025819', 'INC0025957', 'INC0025993', 'INC0026009', 'INC0026041', 'INC0026142', 'INC0026167', 'INC0026171', 'INC0026205', 'INC0026214', 'INC0026226', 'INC0026234', 'INC0026235', 'INC0026246', 'INC0026264', 'INC0026280', 'INC0026307', 'INC0026309', 'INC0026322', 'INC0026364', 'INC0026365', 'INC0026405', 'INC0026408', 'INC0026437', 'INC0026494', 'INC0026529', 'INC0026556', 'INC0026560', 'INC0026568', 'INC0026575', 'INC0026577', 'INC0026587', 'INC0026630', 'INC0026674', 'INC0026716', 'INC0026733', 'INC0026737', 'INC0026740', 'INC0026744', 'INC0026851', 'INC0026921', 'INC0026965', 'INC0027034', 'INC0027039', 'INC0027139', 'INC0027157', 'INC0027160', 'INC0027172', 'INC0027193', 'INC0027197', 'INC0027236', 'INC0027247', 'INC0027250', 'INC0027305', 'INC0027352', 'INC0027354', 'INC0027381', 'INC0027410', 'INC0027414', 'INC0027451', 'INC0027452', 'INC0027454', 'INC0027486', 'INC0027496', 'INC0027521', 'INC0027539', 'INC0027541', 'INC0027545', 'INC0027547', 'INC0027596', 'INC0027612', 'INC0027613', 'INC0027616', 'INC0027631', 'INC0027708', 'INC0027728', 'INC0027735', 'INC0027744', 'INC0027746', 'INC0027753', 'INC0027764', 'INC0027766', 'INC0027774', 'INC0027786', 'INC0027789', 'INC0027796', 'INC0027801', 'INC0027803', 'INC0027864', 'INC0027866', 'INC0027869', 'INC0027874', 'INC0027897', 'INC0027903', 'INC0027904', 'INC0027930', 'INC0027933', 'INC0027939', 'INC0027979', 'INC0027999', 'INC0028000', 'INC0028062', 'INC0028089', 'INC0028136', 'INC0028175', 'INC0028208', 'INC0028215', 'INC0028216', 'INC0028259', 'INC0028281', 'INC0028284', 'INC0028290', 'INC0028308', 'INC0028315', 'INC0028323', 'INC0028332', 'INC0028343', 'INC0028344', 'INC0028347', 'INC0028360', 'INC0028381', 'INC0028384', 'INC0028391', 'INC0028392', 'INC0028415', 'INC0028429', 'INC0028433', 'INC0028437', 'INC0028442', 'INC0028446', 'INC0028464', 'INC0028469', 'INC0028504', 'INC0028507', 'INC0028512', 'INC0028614', 'INC0028634', 'INC0028657', 'INC0028678', 'INC0028701', 'INC0028703', 'INC0028712', 'INC0028735', 'INC0028761', 'INC0028775', 'INC0028786', 'INC0028808', 'INC0028813', 'INC0028817', 'INC0028828', 'INC0028847', 'INC0028863', 'INC0028870', 'INC0028874', 'INC0028884', 'INC0028928', 'INC0028967', 'INC0029010', 'INC0029116', 'INC0029126', 'INC0029129', 'INC0029131', 'INC0029163', 'INC0029186', 'INC0029187', 'INC0029212', 'INC0029216', 'INC0029244', 'INC0029313', 'INC0029353', 'INC0029366', 'INC0029379', 'INC0029392', 'INC0029394', 'INC0029451', 'INC0029559', 'INC0029564', 'INC0029587', 'INC0029663', 'INC0029669', 'INC0029676', 'INC0029696', 'INC0029705', 'INC0029710', 'INC0029715', 'INC0029758', 'INC0029765', 'INC0029772', 'INC0029775', 'INC0029781', 'INC0029830', 'INC0029831', 'INC0029877', 'INC0029887', 'INC0029900', 'INC0029913', 'INC0029914', 'INC0029923', 'INC0029943', 'INC0029959', 'INC0029962', 'INC0029979', 'INC0030004', 'INC0030007', 'INC0030043', 'INC0030074', 'INC0030086', 'INC0030134', 'INC0030146', 'INC0030201', 'INC0030204', 'INC0030207', 'INC0030232', 'INC0030237', 'INC0030256', 'INC0030258', 'INC0030259', 'INC0030331', 'INC0030378', 'INC0030413', 'INC0030442', 'INC0030448', 'INC0030460', 'INC0030465', 'INC0030490', 'INC0030495', 'INC0030498', 'INC0030500', 'INC0030605', 'INC0030613', 'INC0030625', 'INC0030638', 'INC0030645', 'INC0030652', 'INC0030666', 'INC0030675', 'INC0030676', 'INC0030679', 'INC0030702', 'INC0030704', 'INC0030723', 'INC0030733', 'INC0030736', 'INC0030756', 'INC0030757', 'INC0030758', 'INC0030775', 'INC0030780', 'INC0030786', 'INC0030807', 'INC0030812', 'INC0030850', 'INC0030863', 'INC0030875', 'INC0030887', 'INC0030891', 'INC0030906', 'INC0030924', 'INC0030936', 'INC0030943', 'INC0030977', 'INC0030987', 'INC0031020', 'INC0031036', 'INC0031060', 'INC0031099', 'INC0031103', 'INC0031156', 'INC0031167', 'INC0031255', 'INC0031302', 'INC0031316', 'INC0031327', 'INC0031329', 'INC0031340', 'INC0031344', 'INC0031352', 'INC0031356', 'INC0031377', 'INC0031378', 'INC0031387', 'INC0031397', 'INC0031398', 'INC0031399', 'INC0031400', 'INC0031401', 'INC0031407', 'INC0031418', 'INC0031425', 'INC0031426', 'INC0031437', 'INC0031444', 'INC0031448', 'INC0031470', 'INC0031471', 'INC0031474', 'INC0031485', 'INC0031488', 'INC0031503', 'INC0031513', 'INC0031518', 'INC0031523', 'INC0031551', 'INC0031581', 'INC0031620', 'INC0031634', 'INC0031636', 'INC0031640', 'INC0031651', 'INC0031671', 'INC0031674', 'INC0031683', 'INC0031686', 'INC0031688', 'INC0031729', 'INC0031756', 'INC0031758', 'INC0031765', 'INC0031766', 'INC0031773', 'INC0031776', 'INC0031783', 'INC0031791', 'INC0031797', 'INC0031811', 'INC0031814', 'INC0031831', 'INC0031836', 'INC0031881', 'INC0031896', 'INC0031901', 'INC0031940', 'INC0031951', 'INC0032010', 'INC0032013', 'INC0032015', 'INC0032026', 'INC0032034', 'INC0032048', 'INC0032064', 'INC0032066', 'INC0032078', 'INC0032086', 'INC0032092', 'INC0032097', 'INC0032102', 'INC0032105', 'INC0032114', 'INC0032117', 'INC0032119', 'INC0032129', 'INC0032130', 'INC0032131', 'INC0032134', 'INC0032136', 'INC0032139', 'INC0032149', 'INC0032158', 'INC0032163', 'INC0032169', 'INC0032170', 'INC0032179', 'INC0032185', 'INC0032186', 'INC0032192', 'INC0032197', 'INC0032198', 'INC0032201', 'INC0032211', 'INC0032215', 'INC0032224', 'INC0032231', 'INC0032236', 'INC0032240', 'INC0032267', 'INC0032270', 'INC0032279', 'INC0032283', 'INC0032287', 'INC0032290', 'INC0032291', 'INC0032309', 'INC0032312', 'INC0032316', 'INC0032324', 'INC0032337', 'INC0032347', 'INC0032351', 'INC0032356', 'INC0032358', 'INC0032360', 'INC0032364', 'INC0032368', 'INC0032370', 'INC0032393', 'INC0032395', 'INC0032401', 'INC0032403', 'INC0032410', 'INC0032412', 'INC0032413', 'INC0032414', 'INC0032416', 'INC0032425', 'INC0032428', 'INC0032437', 'INC0032443', 'INC0032444', 'INC0032448', 'INC0032450', 'INC0032451', 'INC0032453', 'INC0032458', 'INC0032461', 'INC0032462', 'INC0032465', 'INC0032488', 'INC0032493', 'INC0032500', 'INC0032502', 'INC0032514', 'INC0032519', 'INC0032523', 'INC0032529', 'INC0032532', 'INC0032534', 'INC0032550', 'INC0032554', 'INC0032561', 'INC0032563', 'INC0032571', 'INC0032581', 'INC0032582', 'INC0032588', 'INC0032590', 'INC0032593', 'INC0032595', 'INC0032599', 'INC0032603', 'INC0032610', 'INC0032611', 'INC0032616', 'INC0032623', 'INC0032633', 'INC0032635', 'INC0032636', 'INC0032646', 'INC0032650', 'INC0032652', 'INC0032653', 'INC0032657', 'INC0032658', 'INC0032659', 'INC0032660', 'INC0032666', 'INC0032669', 'INC0032672', 'INC0032674', 'INC0032678', 'INC0032679', 'INC0032680', 'INC0032681', 'INC0032685', 'INC0032690', 'INC0032698', 'INC0032707', 'INC0032709', 'INC0032710', 'INC0032711', 'INC0032716', 'INC0032722', 'INC0032724', 'INC0032725', 'INC0032732', 'INC0032736', 'INC0032738', 'INC0032748', 'INC0032767', 'INC0032771', 'INC0032775', 'INC0032778', 'INC0032779', 'INC0032784', 'INC0032791', 'INC0032797', 'INC0032804', 'INC0032813', 'INC0032815', 'INC0032821', 'INC0032828', 'INC0032833', 'INC0032834', 'INC0032835', 'INC0032841', 'INC0032849', 'INC0032851', 'INC0032852', 'INC0032853', 'INC0032864', 'INC0032877', 'INC0032897', 'INC0032898', 'INC0032903', 'INC0032914', 'INC0032920', 'INC0032925', 'INC0032927', 'INC0032931', 'INC0032935', 'INC0032937', 'INC0032940', 'INC0032942', 'INC0032960', 'INC0032963', 'INC0032967', 'INC0032985', 'INC0032988', 'INC0032994', 'INC0033002', 'INC0033019', 'INC0033020', 'INC0033024', 'INC0033028', 'INC0033032', 'INC0033035', 'INC0033036', 'INC0033039', 'INC0033040', 'INC0033042', 'INC0033045', 'INC0033046', 'INC0033051', 'INC0033052', 'INC0033053', 'INC0033055', 'INC0033056', 'INC0033059', 'INC0033063', 'INC0033066', 'INC0033072', 'INC0033074', 'INC0033080', 'INC0033081', 'INC0033083', 'INC0033087', 'INC0033090', 'INC0033092', 'INC0033095', 'INC0033101', 'INC0033104', 'INC0033116', 'INC0033120', 'INC0033122', 'INC0033123', 'INC0033126', 'INC0033129', 'INC0033132', 'INC0033133', 'INC0033136', 'INC0033138', 'INC0033147', 'INC0033153', 'INC0033154', 'INC0033157', 'INC0033162', 'INC0033163', 'INC0033177', 'INC0033179', 'INC0033180', 'INC0033181', 'INC0033193', 'INC0033199', 'INC0033209', 'INC0033214', 'INC0033215', 'INC0033219', 'INC0033221', 'INC0033225', 'INC0033226', 'INC0033230', 'INC0033233', 'INC0033234', 'INC0033235', 'INC0033236', 'INC0033243', 'INC0033244', 'INC0033245', 'INC0033246', 'INC0033247', 'INC0033252', 'INC0033260', 'INC0033264', 'INC0033265', 'INC0033268', 'INC0033269', 'INC0033271', 'INC0033272', 'INC0033273', 'INC0033276', 'INC0033277', 'INC0033278', 'INC0033279', 'INC0033280', 'INC0033281', 'INC0033282', 'INC0033283', 'INC0033284', 'INC0033286', 'INC0033287', 'INC0033288', 'INC0033289', 'INC0033291', 'INC0033292', 'INC0033293', 'INC0033294', 'INC0033296', 'INC0033297', 'INC0033298', 'INC0033299', 'INC0033300', 'INC0033301', 'INC0033302', 'INC0033303', 'INC0033304', 'INC0033305', 'INC0033306', 'INC0033308', 'INC0033309', 'INC0033310', 'INC0033311', 'INC0033312', 'INC0033313', 'INC0033314', 'INC0033315', 'INC0033316', 'INC0033317', 'INC0033318', 'INC0033319', 'INC0033320', 'INC0033322', 'INC0033323', 'INC0033324', 'INC0033325', 'INC0033326', 'INC0033327', 'INC0033328', 'INC0033329', 'INC0033330', 'INC0033333', 'INC0033334', 'INC0033338', 'INC0033339', 'INC0033340', 'INC0033341', 'INC0033342', 'INC0033343', 'INC0033344', 'INC0033345', 'INC0033347', 'INC0033348', 'INC0033349', 'INC0033351', 'INC0033352', 'INC0033353', 'INC0033354', 'INC0033355', 'INC0033356', 'INC0033357', 'INC0033359', 'INC0033360', 'INC0033364', 'INC0033366', 'INC0033367', 'INC0033368', 'INC0033369', 'INC0033371', 'INC0033372', 'INC0033374', 'INC0033375', 'INC0033376', 'INC0033377', 'INC0033378', 'INC0033380', 'INC0033381', 'INC0033382', 'INC0033383', 'INC0033384', 'INC0033386', 'INC0033387', 'INC0033388', 'INC0033389', 'INC0033390', 'INC0033391', 'INC0033392', 'INC0033393', 'INC0033394', 'INC0033395', 'INC0033396', 'INC0033397', 'INC0033398', 'INC0033401', 'INC0033403', 'INC0033404', 'INC0033407', 'INC0033408', 'INC0033409', 'INC0033410', 'INC0033411', 'INC0033412', 'INC0033415', 'INC0033417', 'INC0033418', 'INC0033420', 'INC0033421', 'INC0033422', 'INC0033423', 'INC0033424', 'INC0033426', 'INC0033427', 'INC0033428', 'INC0033429', 'INC0033430', 'INC0033431', 'INC0033432', 'INC0033433', 'INC0033434', 'INC0033436', 'INC0033438', 'INC0033439', 'INC0033440', 'INC0033441', 'INC0033442', 'INC0033444', 'INC0033445', 'INC0033447', 'INC0033448', 'INC0033450', 'INC0033451', 'INC0033452', 'INC0033454', 'INC0033455', 'INC0033456', 'INC0033457', 'INC0033459', 'INC0033462', 'INC0033463', 'INC0033464', 'INC0033492', 'INC0033493', 'INC0033494', 'INC0033495', 'INC0033497', 'INC0033498', 'INC0033499', 'INC0033501', 'INC0033502', 'INC0033503', 'INC0033504', 'INC0033505', 'INC0033506', 'INC0033508', 'INC0033509', 'INC0033510', 'INC0033512', 'INC0033513', 'INC0033516', 'INC0033518', 'INC0033520', 'INC0033521', 'INC0033522', 'INC0033523', 'INC0033524', 'INC0033525', 'INC0033527', 'INC0033529', 'INC0033530', 'INC0033531', 'INC0033532', 'INC0033533', 'INC0033534', 'INC0033537', 'INC0033538', 'INC0033539', 'INC0033540', 'INC0033541', 'INC0033542', 'INC0033544', 'INC0033545', 'INC0033546', 'INC0033547', 'INC0033548', 'INC0033549', 'INC0033550', 'INC0033551', 'INC0033553', 'INC0033554', 'INC0033555', 'INC0033558', 'INC0033560', 'INC0033561', 'INC0033562', 'INC0033563', 'INC0033564', 'INC0033565', 'INC0033566', 'INC0033567', 'INC0033568', 'INC0033569', 'INC0033571', 'INC0033573', 'INC0033574', 'INC0033575', 'INC0033577', 'INC0033579', 'INC0033582', 'INC0033583', 'INC0033584', 'INC0033585', 'INC0033586', 'INC0033587', 'INC0033588', 'INC0033589', 'INC0033590', 'INC0033592', 'INC0033593', 'INC0033594', 'INC0033595', 'INC0033596', 'INC0033598', 'INC0033599', 'INC0033600', 'INC0033601', 'INC0033602', 'INC0033603', 'INC0033605', 'INC0033606', 'INC0033607', 'INC0033608', 'INC0033609', 'INC0033610', 'INC0033611', 'INC0033613', 'INC0033614', 'INC0033615', 'INC0033616', 'INC0033617', 'INC0033618', 'INC0033621', 'INC0033622', 'INC0033623', 'INC0033624', 'INC0033627', 'INC0033628', 'INC0033629', 'INC0033630', 'INC0033631', 'INC0033632', 'INC0033633', 'INC0033634', 'INC0033639', 'INC0033643', 'INC0033644', 'INC0033646', 'INC0033647', 'INC0033648', 'INC0033649', 'INC0033650', 'INC0033651', 'INC0033653', 'INC0033654', 'INC0033655', 'INC0033656', 'INC0033657', 'INC0033658', 'INC0033660', 'INC0033661', 'INC0033662', 'INC0033663', 'INC0033667', 'INC0033668', 'INC0033669', 'INC0033671', 'INC0033672', 'INC0033674', 'INC0033675', 'INC0033677', 'INC0033679', 'INC0033681', 'INC0033682', 'INC0033683', 'INC0033684', 'INC0033686', 'INC0033687', 'INC0033690', 'INC0033691', 'INC0033692', 'INC0033693', 'INC0033694', 'INC0033695', 'INC0033697', 'INC0033698', 'INC0033700', 'INC0033701', 'INC0033702', 'INC0033703', 'INC0033704', 'INC0033705', 'INC0033706', 'INC0033708', 'INC0033709', 'INC0033710', 'INC0033711', 'INC0033712', 'INC0033713', 'INC0033714', 'INC0033715', 'INC0033716', 'INC0033717', 'INC0033718', 'INC0033719', 'INC0033720', 'INC0033721', 'INC0033722', 'INC0033723', 'INC0033725', 'INC0033726', 'INC0033727', 'INC0033728', 'INC0033729', 'INC0033731', 'INC0033732', 'INC0033733', 'INC0033734', 'INC0033735', 'INC0033736', 'INC0033738', 'INC0033739', 'INC0033740', 'INC0033741', 'INC0033742', 'INC0033744', 'INC0033747', 'INC0033748', 'INC0033751', 'INC0033752', 'INC0033753', 'INC0033754', 'INC0033756', 'INC0033757', 'INC0033758', 'INC0033760', 'INC0033761', 'INC0033762', 'INC0033764', 'INC0033766', 'INC0033767', 'INC0033768', 'INC0033769', 'INC0033771', 'INC0033773', 'INC0033779', 'INC0033781', 'INC0033785', 'INC0033787', 'INC0033788', 'INC0033789', 'INC0033790', 'INC0033791', 'INC0033792', 'INC0033793', 'INC0033794', 'INC0033795', 'INC0033797', 'INC0033798', 'INC0033801', 'INC0033802', 'INC0033803', 'INC0033804', 'INC0033805', 'INC0033806', 'INC0033807', 'INC0033808', 'INC0033809', 'INC0033810', 'INC0033811', 'INC0033813', 'INC0033815', 'INC0033818', 'INC0033819', 'INC0033820', 'INC0033823', 'INC0033824', 'INC0033825', 'INC0033826', 'INC0033827', 'INC0033828', 'INC0033829', 'INC0033830', 'INC0033831', 'INC0033833', 'INC0033834', 'INC0033835', 'INC0033836', 'INC0033837', 'INC0033838', 'INC0033839', 'INC0033842', 'INC0033843', 'INC0033844', 'INC0033845', 'INC0033846', 'INC0033847', 'INC0033848', 'INC0033849', 'INC0033850', 'INC0033851', 'INC0033852', 'INC0033853', 'INC0033854', 'INC0033855', 'INC0033856', 'INC0033857', 'INC0033858', 'INC0033859', 'INC0033860', 'INC0033861', 'INC0033862', 'INC0033863', 'INC0033866', 'INC0033867', 'INC0033869', 'INC0033870', 'INC0033871', 'INC0033873', 'INC0033876', 'INC0033877', 'INC0033878', 'INC0033879', 'INC0033881', 'INC0033882', 'INC0033883', 'INC0033884', 'INC0033885', 'INC0033887', 'INC0033888', 'INC0033889', 'INC0033894', 'INC0033895', 'INC0033896', 'INC0033897', 'INC0033898', 'INC0033899', 'INC0033901', 'INC0033902', 'INC0033905', 'INC0033906', 'INC0033908', 'INC0033909', 'INC0033910', 'INC0033916', 'INC0033917', 'INC0033918', 'INC0033920', 'INC0033923', 'INC0033926', 'INC0033927', 'INC0033929', 'INC0033931', 'INC0033932', 'INC0033933', 'INC0033934', 'INC0033936', 'INC0033939', 'INC0033940', 'INC0033942', 'INC0033943', 'INC0033945', 'INC0033946', 'INC0033948', 'INC0033949', 'INC0033951', 'INC0033952', 'INC0033953', 'INC0033954', 'INC0033955', 'INC0033956', 'INC0033957', 'INC0033958', 'INC0033960', 'INC0033961', 'INC0033962', 'INC0033963', 'INC0033964', 'INC0033965', 'INC0033966', 'INC0033967', 'INC0033969', 'INC0033970', 'INC0033971', 'INC0033974', 'INC0033975', 'INC0033976', 'INC0033978', 'INC0033979', 'INC0033980', 'INC0033983', 'INC0033985', 'INC0033986', 'INC0033987', 'INC0033990', 'INC0033993', 'INC0033994', 'INC0033995', 'INC0033996', 'INC0033997', 'INC0033999', 'INC0034000', 'INC0034001', 'INC0034002', 'INC0034003', 'INC0034004', 'INC0034005', 'INC0034006', 'INC0034007', 'INC0034010', 'INC0034011', 'INC0034013', 'INC0034014', 'INC0034016', 'INC0034017', 'INC0034018', 'INC0034019', 'INC0034020', 'INC0034021', 'INC0034023', 'INC0034025', 'INC0034026', 'INC0034027', 'INC0034028', 'INC0034030', 'INC0034031', 'INC0034032', 'INC0034033', 'INC0034034', 'INC0034035', 'INC0034038', 'INC0034039', 'INC0034040', 'INC0034044', 'INC0034045', 'INC0034046', 'INC0034047', 'INC0034048', 'INC0034050', 'INC0034051', 'INC0034052', 'INC0034053', 'INC0034054', 'INC0034056', 'INC0034059', 'INC0034060', 'INC0034061', 'INC0034062', 'INC0034064', 'INC0034066', 'INC0034067', 'INC0034069', 'INC0034074', 'INC0034125', 'INC0034126', 'INC0034127', 'INC0034128', 'INC0034129', 'INC0034130', 'INC0034131', 'INC0034132', 'INC0034133', 'INC0034134', 'INC0034135', 'INC0034136', 'INC0034138', 'INC0034141', 'INC0034142', 'INC0034143', 'INC0034144', 'INC0034145', 'INC0034146', 'INC0034147', 'INC0034148', 'INC0034149', 'INC0034150', 'INC0034151', 'INC0034152', 'INC0034153', 'INC0034159', 'INC0034160', 'INC0034161', 'INC0034163', 'INC0034164', 'INC0034168', 'INC0034169', 'INC0034170', 'INC0034171', 'INC0034172', 'INC0034173', 'INC0034174', 'INC0034175', 'INC0034176', 'INC0034177', 'INC0034178', 'INC0034179', 'INC0034180', 'INC0034181', 'INC0034183', 'INC0034186', 'INC0034188', 'INC0034189', 'INC0034190', 'INC0034191', 'INC0034196', 'INC0034198', 'INC0034199', 'INC0034200', 'INC0034206', 'INC0034207', 'INC0034208', 'INC0034209', 'INC0034210', 'INC0034211', 'INC0034213', 'INC0034214', 'INC0034215', 'INC0034216', 'INC0034217', 'INC0034219', 'INC0034223', 'INC0034224', 'INC0034225', 'INC0034226', 'INC0034228', 'INC0034229', 'INC0034230', 'INC0034232', 'INC0034233', 'INC0034234', 'INC0034236', 'INC0034237', 'INC0034239', 'INC0034240', 'INC0034241', 'INC0034242', 'INC0034244', 'INC0034245', 'INC0034248', 'INC0034249', 'INC0034250', 'INC0034251', 'INC0034252', 'INC0034254', 'INC0034255', 'INC0034257', 'INC0034258', 'INC0034259', 'INC0034260', 'INC0034261', 'INC0034262', 'INC0034263', 'INC0034264', 'INC0034265', 'INC0034266', 'INC0034267', 'INC0034270', 'INC0034271', 'INC0034272', 'INC0034273', 'INC0034274', 'INC0034275', 'INC0034276', 'INC0034277', 'INC0034278', 'INC0034279', 'INC0034280', 'INC0034281', 'INC0034282', 'INC0034283', 'INC0034285', 'INC0034287', 'INC0034288', 'INC0034289', 'INC0034291', 'INC0034292', 'INC0034293', 'INC0034295', 'INC0034297', 'INC0034298', 'INC0034299', 'INC0034301', 'INC0034303', 'INC0034304', 'INC0034305', 'INC0034308', 'INC0034309', 'INC0034310', 'INC0034311', 'INC0034312', 'INC0034313', 'INC0034314', 'INC0034315', 'INC0034316', 'INC0034318', 'INC0034320', 'INC0034321', 'INC0034322', 'INC0034323', 'INC0034324', 'INC0034325', 'INC0034328', 'INC0034329', 'INC0034331', 'INC0034332', 'INC0034333', 'INC0034334', 'INC0034335', 'INC0034336', 'INC0034338', 'INC0034339', 'INC0034340', 'INC0034341', 'INC0034342', 'INC0034343', 'INC0034344', 'INC0034345', 'INC0034346', 'INC0034348', 'INC0034350', 'INC0034351', 'INC0034352', 'INC0034354', 'INC0034355', 'INC0034356', 'INC0034357', 'INC0034358', 'INC0034359', 'INC0034360', 'INC0034362', 'INC0034363', 'INC0034364', 'INC0034365', 'INC0034367', 'INC0034368', 'INC0034369', 'INC0034370', 'INC0034372', 'INC0034374', 'INC0034375', 'INC0034376', 'INC0034378', 'INC0034380', 'INC0034381', 'INC0034382', 'INC0034384', 'INC0034385', 'INC0034387', 'INC0034388', 'INC0034389', 'INC0034390', 'INC0034391', 'INC0034392', 'INC0034393', 'INC0034395', 'INC0034398', 'INC0034399', 'INC0034401', 'INC0034402', 'INC0034403', 'INC0034404', 'INC0034405', 'INC0034406', 'INC0034407', 'INC0034408', 'INC0034409', 'INC0034412', 'INC0034413', 'INC0034415', 'INC0034416', 'INC0034418', 'INC0034419', 'INC0034421', 'INC0034422', 'INC0034423', 'INC0034424', 'INC0034425', 'INC0034426', 'INC0034427', 'INC0034428', 'INC0034429', 'INC0034431', 'INC0034432', 'INC0034433', 'INC0034434', 'INC0034435', 'INC0035024', 'INC0037768', 'INC0040267', 'INC0041652']
incident_compliance_metric = 'fitness'
compliance_metric_thresholds = {
    "critical": [0, 0.25],
    "moderate": [0.25, 0.5],
    "high": [0.5, 0.75],
    "low": [0.75, 1]
}

filter_compliance_metric_thresholds = {}

incident_selection_from_tabular_analysis = []

@eel.expose
def get_incident_ids_selection():
    return incident_ids_from_time_period


def set_incident_ids_selection(incident_ids):
    global incident_ids_from_time_period 
    incident_ids_from_time_period = incident_ids
    return

@eel.expose
def get_incident_compliance_metric():
    return incident_compliance_metric

@eel.expose
def set_incident_compliance_metric(selected_metric):
    global incident_compliance_metric
    incident_compliance_metric = selected_metric
    return

@eel.expose
def get_compliance_metric_thresholds():
    return json.dumps(compliance_metric_thresholds)

@eel.expose
def set_compliance_metric_thresholds(thresholds):
    global compliance_metric_thresholds
    compliance_metric_thresholds = json.loads(thresholds)
    return

@eel.expose
def get_filter_compliance_metric_thresholds():
    return filter_compliance_metric_thresholds




@eel.expose
def set_filter_compliance_metric_thresholds(metric_name, range_start, range_end):
    global filter_compliance_metric_thresholds
    
    # Create a unique key for the range filter
    filter_key = f"{metric_name}_{range_start}_{range_end}"

    # Check if the filter is already applied (if it exists in the global variable)
    if filter_key in filter_compliance_metric_thresholds:
        # If the filter exists, remove it (this means the user unclicked the severity level)
        del filter_compliance_metric_thresholds[filter_key]
        print("database_filter_variables.py")
        print(f"Removed filter: {filter_key}")
    else:
        # Otherwise, add the filter to the global variable
        filter_compliance_metric_thresholds[filter_key] = (metric_name, range_start, range_end)
        print("database_filter_variables.py")
        print(f"Added filter: {filter_key}")

    # For debugging, print the current filters
    print("database_filter_variables.py")
    print("Current filters:", filter_compliance_metric_thresholds)

    # Optionally, return the current filters as a string or any format you need
    return filter_compliance_metric_thresholds


@eel.expose
def get_incident_ids_from_tabular_selection():
    return incident_selection_from_tabular_analysis

@eel.expose
def set_incident_ids_from_tabular_selection(incident_ids):
    global incident_selection_from_tabular_analysis
    incident_selection_from_tabular_analysis = incident_ids
    return