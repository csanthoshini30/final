"""
RAG Maintenance Agent - Retrieval-Augmented Generation
"""
import json
import numpy as np
from pathlib import Path
from config.config import VECTOR_DB_DIR, MAINTENANCE_MANUALS_DIR

class RAGMaintenanceAgent:
    """RAG-based maintenance assistant"""

    def __init__(self):
        self.vector_db_dir = VECTOR_DB_DIR
        self.manuals_dir = MAINTENANCE_MANUALS_DIR
        self.vector_db_dir.mkdir(parents=True, exist_ok=True)
        self.manuals_dir.mkdir(parents=True, exist_ok=True)
        self.knowledge_base = self.build_knowledge_base()

    def build_knowledge_base(self):
        """Build maintenance knowledge base"""
        kb = {
            'Engine': {
                'Compressor Degradation': {
                    'causes': [
                        'Blade erosion from sand or debris ingestion',
                        'Corrosion from environmental exposure',
                        'Mechanical damage from foreign objects',
                        'Normal wear and tear'
                    ],
                    'inspection_procedures': [
                        'Visual inspection of compressor blades',
                        'Borescope examination for cracks',
                        'Performance trend analysis',
                        'Vibration monitoring'
                    ],
                    'corrective_actions': [
                        'Clean compressor using approved wash cycle',
                        'Replace damaged blades',
                        'Adjust fuel flow parameters',
                        'Schedule overhaul if degradation exceeds limits'
                    ],
                    'spare_parts': [
                        'Compressor blades (various stages)',
                        'Compressor seal kit',
                        'Fastening hardware'
                    ],
                    'safety_considerations': [
                        'Follow lockout/tagout procedures',
                        'Allow engine to cool before inspection',
                        'Use proper PPE during service'
                    ]
                },
                'Bearing Wear': {
                    'causes': [
                        'Inadequate lubrication',
                        'Contaminated oil',
                        'Misalignment',
                        'Excessive load'
                    ],
                    'inspection_procedures': [
                        'Oil analysis for metal particles',
                        'Vibration analysis',
                        'Temperature monitoring',
                        'Visual inspection for wear patterns'
                    ],
                    'corrective_actions': [
                        'Change oil and filters immediately',
                        'Inspect bearing surfaces',
                        'Replace worn bearings',
                        'Check alignment'
                    ],
                    'spare_parts': [
                        'Bearing assemblies',
                        'Seal kits',
                        'Lubrication system components'
                    ],
                    'safety_considerations': [
                        'Ensure proper ventilation',
                        'Use explosion-proof equipment if required'
                    ]
                },
                'Turbine Blade Erosion': {
                    'causes': [
                        'High-temperature exposure',
                        'Particle ingestion',
                        'Environmental erosion',
                        'Fatigue cracking'
                    ],
                    'inspection_procedures': [
                        'Borescope inspection',
                        'Thermal imaging',
                        'Ultrasonic thickness measurement',
                        'Eddy current testing'
                    ],
                    'corrective_actions': [
                        'Apply thermal barrier coatings',
                        'Replace severely eroded blades',
                        'Monitor inlet air quality',
                        'Adjust operating parameters'
                    ],
                    'spare_parts': [
                        'Turbine blades',
                        'Thermal coatings',
                        'Heat shields'
                    ],
                    'safety_considerations': [
                        'Handle blades with care to avoid damage',
                        'Use thermal protection during installation'
                    ]
                }
            },
            'Electrical': {
                'Battery Capacity Loss': {
                    'causes': [
                        'Cycle aging',
                        'Calendar aging',
                        'Overcharging',
                        'Deep discharge',
                        'Temperature extremes'
                    ],
                    'inspection_procedures': [
                        'Capacity test under load',
                        'Voltage under load measurement',
                        'Internal resistance testing',
                        'Thermal imaging'
                    ],
                    'corrective_actions': [
                        'Condition charging and discharging cycles',
                        'Balance battery cells',
                        'Replace if capacity below 80%',
                        'Implement proper charging protocol'
                    ],
                    'spare_parts': [
                        'Battery modules',
                        'Charging regulators',
                        'Monitoring electronics'
                    ],
                    'safety_considerations': [
                        'Proper grounding during replacement',
                        'Fire suppression equipment nearby'
                    ]
                },
                'Voltage Regulation Fault': {
                    'causes': [
                        'Regulator failure',
                        'Wiring issues',
                        'Diode failure',
                        'Sensor malfunction'
                    ],
                    'inspection_procedures': [
                        'Voltage measurement at multiple points',
                        'Waveform analysis',
                        'Component testing',
                        'Thermal inspection'
                    ],
                    'corrective_actions': [
                        'Test and replace regulator',
                        'Check wiring connections',
                        'Replace failed components',
                        'Verify proper calibration'
                    ],
                    'spare_parts': [
                        'Voltage regulators',
                        'Wiring and connectors',
                        'Sensor units'
                    ],
                    'safety_considerations': [
                        'De-energize before service',
                        'Use insulated tools'
                    ]
                }
            },
            'Hydraulic': {
                'Pump Efficiency Degradation': {
                    'causes': [
                        'Internal leakage',
                        'Wear of pump internals',
                        'Contaminated fluid',
                        'Incorrect operating parameters'
                    ],
                    'inspection_procedures': [
                        'Flow rate and pressure testing',
                        'Fluid sampling and analysis',
                        'Acoustic analysis',
                        'Thermal monitoring'
                    ],
                    'corrective_actions': [
                        'Flush hydraulic system',
                        'Replace or rebuild pump',
                        'Replace fluid and filters',
                        'Adjust system parameters'
                    ],
                    'spare_parts': [
                        'Pump assemblies',
                        'Internal seals',
                        'Hydraulic fluid (correct type)',
                        'Filters and accumulators'
                    ],
                    'safety_considerations': [
                        'Relieve system pressure before service',
                        'Proper disposal of hydraulic fluid',
                        'Use PPE for fluid handling'
                    ]
                },
                'Pressure Regulation Fault': {
                    'causes': [
                        'Relief valve sticking',
                        'Pressure sensor failure',
                        'System blockage',
                        'Internal leakage'
                    ],
                    'inspection_procedures': [
                        'Pressure gauge measurement',
                        'Relief valve testing',
                        'Sensor calibration check',
                        'Flow visualization'
                    ],
                    'corrective_actions': [
                        'Clean or replace relief valve',
                        'Replace pressure sensor',
                        'Clear blockages',
                        'Rebuild if necessary'
                    ],
                    'spare_parts': [
                        'Relief valves',
                        'Pressure sensors',
                        'Fittings and lines'
                    ],
                    'safety_considerations': [
                        'Follow pressure relief procedures',
                        'Use pressure-rated equipment'
                    ]
                },
                'Leak Detection': {
                    'causes': [
                        'Worn seals',
                        'Cracked lines',
                        'Loose connections',
                        'Fatigue failure'
                    ],
                    'inspection_procedures': [
                        'Visual inspection',
                        'Dye penetrant testing',
                        'Ultrasonic leak detection',
                        'Pressure decay testing'
                    ],
                    'corrective_actions': [
                        'Tighten connections',
                        'Replace seals',
                        'Repair or replace lines',
                        'Full system pressure test after repair'
                    ],
                    'spare_parts': [
                        'Seal kits',
                        'Hydraulic lines',
                        'Connectors and fittings'
                    ],
                    'safety_considerations': [
                        'Contain fluid spillage properly',
                        'Protect skin from high-pressure spray'
                    ]
                }
            }
        }
        return kb

    def search(self, fault_info):
        """Search knowledge base for relevant information"""
        subsystem = fault_info.get('subsystem', '').title()
        fault = fault_info.get('fault', '')

        results = {
            'subsystem': subsystem,
            'fault': fault,
            'found': False,
            'causes': [],
            'inspection_procedures': [],
            'corrective_actions': [],
            'spare_parts': [],
            'safety_considerations': []
        }

        if subsystem in self.knowledge_base:
            if fault in self.knowledge_base[subsystem]:
                kb_entry = self.knowledge_base[subsystem][fault]
                results['found'] = True
                results['causes'] = kb_entry.get('causes', [])
                results['inspection_procedures'] = kb_entry.get('inspection_procedures', [])
                results['corrective_actions'] = kb_entry.get('corrective_actions', [])
                results['spare_parts'] = kb_entry.get('spare_parts', [])
                results['safety_considerations'] = kb_entry.get('safety_considerations', [])

        return results

    def generate_maintenance_report(self, fault_info):
        """Generate comprehensive maintenance report"""
        search_result = self.search(fault_info)

        report = {
            'title': f"Maintenance Report - {search_result['subsystem']}: {search_result['fault']}",
            'summary': self._generate_summary(search_result),
            'details': search_result,
            'maintenance_steps': self._generate_maintenance_steps(search_result),
            'risk_mitigation': self._generate_risk_mitigation(search_result)
        }

        return report

    def _generate_summary(self, search_result):
        """Generate summary text"""
        if not search_result['found']:
            return f"Maintenance guidance not found for {search_result['subsystem']}: {search_result['fault']}"

        summary = f"""
        {search_result['subsystem']} System - {search_result['fault']}

        Common Causes:
        """
        for cause in search_result['causes'][:3]:
            summary += f"\n  • {cause}"

        summary += "\n\nImmediate Recommended Actions:"
        for action in search_result['corrective_actions'][:2]:
            summary += f"\n  • {action}"

        return summary

    def _generate_maintenance_steps(self, search_result):
        """Generate step-by-step maintenance procedure"""
        steps = []

        for i, procedure in enumerate(search_result['inspection_procedures'], 1):
            steps.append({
                'step': i,
                'type': 'Inspection',
                'description': procedure
            })

        for i, action in enumerate(search_result['corrective_actions'], 1):
            steps.append({
                'step': len(search_result['inspection_procedures']) + i,
                'type': 'Correction',
                'description': action
            })

        return steps

    def _generate_risk_mitigation(self, search_result):
        """Generate risk mitigation strategies"""
        mitigation = {
            'safety_procedures': search_result['safety_considerations'],
            'quality_checks': [
                'Perform pre-flight inspection after maintenance',
                'Test system under load conditions',
                'Monitor for 24 hours post-maintenance',
                'Document all work performed'
            ],
            'follow_up': [
                'Schedule follow-up inspection',
                'Monitor system performance metrics',
                'Update maintenance logs',
                'Plan preventive maintenance'
            ]
        }

        return mitigation
