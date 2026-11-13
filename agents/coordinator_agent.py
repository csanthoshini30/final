"""
Coordinator Agent - Aggregates Subsystem Analysis
"""
import numpy as np
from config.config import RISK_CRITICAL, RISK_HIGH, RISK_MEDIUM, RISK_LOW, RISK_NORMAL

class CoordinatorAgent:
    """Coordinates subsystem agents and generates overall assessment"""

    def __init__(self, engine_agent, electrical_agent, hydraulic_agent):
        self.engine_agent = engine_agent
        self.electrical_agent = electrical_agent
        self.hydraulic_agent = hydraulic_agent

    def calculate_weighted_health(self, engine_result, electrical_result, hydraulic_result):
        """Calculate weighted overall aircraft health"""
        weights = {
            'engine': 0.45,
            'electrical': 0.30,
            'hydraulic': 0.25
        }

        health_scores = []

        if engine_result['health_score'] is not None:
            health_scores.append(engine_result['health_score'] * weights['engine'])

        if electrical_result['health_score'] is not None:
            health_scores.append(electrical_result['health_score'] * weights['electrical'])

        if hydraulic_result['health_score'] is not None:
            health_scores.append(hydraulic_result['health_score'] * weights['hydraulic'])

        if health_scores:
            return sum(health_scores) / sum([weights[k] for k in weights.keys() if
                                            (k == 'engine' and engine_result['health_score']) or
                                            (k == 'electrical' and electrical_result['health_score']) or
                                            (k == 'hydraulic' and hydraulic_result['health_score'])])
        return None

    def determine_overall_risk(self, engine_result, electrical_result, hydraulic_result):
        """Determine overall aircraft risk level"""
        risk_levels = {
            RISK_CRITICAL: 4,
            RISK_HIGH: 3,
            RISK_MEDIUM: 2,
            RISK_LOW: 1,
            RISK_NORMAL: 0
        }

        max_risk_score = 0
        risks = [engine_result['risk'], electrical_result['risk'], hydraulic_result['risk']]

        for risk in risks:
            score = risk_levels.get(risk, 0)
            max_risk_score = max(max_risk_score, score)

        # Map score back to risk level
        reverse_map = {v: k for k, v in risk_levels.items()}
        return reverse_map.get(max_risk_score, RISK_NORMAL)

    def get_priority_subsystem(self, engine_result, electrical_result, hydraulic_result):
        """Identify which subsystem requires immediate attention"""
        priority_scores = {}

        # Calculate priority based on health and risk
        subsystems = {
            'Engine': engine_result,
            'Electrical': electrical_result,
            'Hydraulic': hydraulic_result
        }

        for name, result in subsystems.items():
            score = 0

            # Health score component (lower is worse)
            if result['health_score'] is not None:
                score += (100 - result['health_score'])

            # Risk level component
            risk_value = {RISK_CRITICAL: 40, RISK_HIGH: 30, RISK_MEDIUM: 20,
                         RISK_LOW: 10, RISK_NORMAL: 0}
            score += risk_value.get(result['risk'], 0)

            # Anomaly component
            if result['anomaly']:
                score += 15

            # RUL component (lower RUL = higher priority)
            if result['rul'] is not None and result['rul'] < 100:
                score += (100 - result['rul']) * 0.5

            priority_scores[name] = score

        # Return subsystem with highest priority score
        if priority_scores:
            priority_subsystem = max(priority_scores, key=priority_scores.get)
            return priority_subsystem
        return "Unknown"

    def rank_subsystems(self, engine_result, electrical_result, hydraulic_result):
        """Rank subsystems by criticality"""
        subsystems = {
            'Engine': engine_result,
            'Electrical': electrical_result,
            'Hydraulic': hydraulic_result
        }

        scores = {}
        for name, result in subsystems.items():
            score = 0

            if result['health_score'] is not None:
                score += (100 - result['health_score']) * 0.6

            risk_value = {RISK_CRITICAL: 40, RISK_HIGH: 30, RISK_MEDIUM: 20,
                         RISK_LOW: 10, RISK_NORMAL: 0}
            score += risk_value.get(result['risk'], 0) * 0.4

            scores[name] = score

        # Sort by score (descending)
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [item[0] for item in ranked]

    def coordinate(self, engine_data, electrical_data, hydraulic_data):
        """Coordinate all agents and generate overall assessment"""
        # Get individual diagnoses
        engine_result = self.engine_agent.diagnose(engine_data)
        electrical_result = self.electrical_agent.diagnose(electrical_data)
        hydraulic_result = self.hydraulic_agent.diagnose(hydraulic_data)

        # Calculate overall metrics
        overall_health = self.calculate_weighted_health(engine_result, electrical_result, hydraulic_result)
        overall_risk = self.determine_overall_risk(engine_result, electrical_result, hydraulic_result)
        priority_subsystem = self.get_priority_subsystem(engine_result, electrical_result, hydraulic_result)
        ranked_subsystems = self.rank_subsystems(engine_result, electrical_result, hydraulic_result)

        # Generate assessment
        assessment = {
            'timestamp': None,
            'overall_health': int(overall_health) if overall_health else None,
            'overall_risk': overall_risk,
            'priority': priority_subsystem,
            'ranked_subsystems': ranked_subsystems,
            'subsystem_results': {
                'engine': engine_result,
                'electrical': electrical_result,
                'hydraulic': hydraulic_result
            },
            'recommendations': self.generate_recommendations(
                engine_result, electrical_result, hydraulic_result, overall_risk
            )
        }

        return assessment

    def generate_recommendations(self, engine_result, electrical_result, hydraulic_result, overall_risk):
        """Generate maintenance recommendations"""
        recommendations = []

        # Engine recommendations
        if engine_result['health_score'] is not None and engine_result['health_score'] < 70:
            recommendations.append({
                'subsystem': 'Engine',
                'priority': 'High',
                'action': f"Inspect engine for {engine_result['fault']}",
                'rul_warning': f"RUL: {engine_result['rul']} hours" if engine_result['rul'] else None
            })

        # Electrical recommendations
        if electrical_result['health_score'] is not None and electrical_result['health_score'] < 70:
            recommendations.append({
                'subsystem': 'Electrical',
                'priority': 'Medium',
                'action': f"Check electrical system for {electrical_result['fault']}",
                'rul_warning': f"RUL: {electrical_result['rul']} hours" if electrical_result['rul'] else None
            })

        # Hydraulic recommendations
        if hydraulic_result['health_score'] is not None and hydraulic_result['health_score'] < 70:
            recommendations.append({
                'subsystem': 'Hydraulic',
                'priority': 'Medium',
                'action': f"Inspect hydraulic system for {hydraulic_result['fault']}",
                'rul_warning': f"RUL: {hydraulic_result['rul']} hours" if hydraulic_result['rul'] else None
            })

        # Overall system recommendation
        if overall_risk in [RISK_CRITICAL, RISK_HIGH]:
            recommendations.insert(0, {
                'subsystem': 'Aircraft',
                'priority': 'Critical',
                'action': 'Schedule immediate maintenance',
                'reason': f'Overall risk level is {overall_risk}'
            })

        return recommendations
