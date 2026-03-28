"""
Culture Fit Analyzer module - Unique feature for assessing candidate-company alignment.
"""
from typing import Dict, Any, List
from core.base_module import BaseModule
from langchain_openai import ChatOpenAI


class CultureAnalyzer(BaseModule):
    """Analyzes culture fit between candidates and companies."""
    
    def __init__(self):
        super().__init__("culture_analyzer")
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.3)
    
    def can_handle(self, task: Dict[str, Any]) -> bool:
        """Check if this module can handle the task."""
        task_type = task.get("type", "")
        keywords = ["culture", "fit", "values", "alignment", "compatibility", "team dynamics"]
        description = task.get("description", "").lower()
        
        return task_type == "culture_fit" or any(kw in description for kw in keywords)
    
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute culture fit analysis."""
        params = task.get("params", {})
        description = task.get("description", "").lower()
        
        if "assess" in description or "analyze" in description:
            return self._assess_culture_fit(params)
        elif "profile" in description:
            return self._create_culture_profile(params)
        elif "team" in description:
            return self._analyze_team_dynamics(params)
        else:
            return self._comprehensive_culture_analysis(params)
    
    def _assess_culture_fit(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Assess culture fit between candidate and company."""
        candidate_name = params.get("candidate_name", "Candidate")
        company_name = params.get("company_name", "Company")
        candidate_values = params.get("candidate_values", [])
        company_values = params.get("company_values", [])
        work_style = params.get("work_style", "")
        
        prompt = f"""You are a culture fit expert. Analyze the alignment between this candidate and company.

Candidate: {candidate_name}
Candidate Values: {', '.join(candidate_values) if candidate_values else "Innovation, collaboration, work-life balance"}
Work Style: {work_style if work_style else "Flexible, team-oriented"}

Company: {company_name}
Company Values: {', '.join(company_values) if company_values else "Excellence, integrity, customer focus"}

Provide:
1. Culture Fit Score (0-100) with explanation
2. Alignment Areas (where they match well)
3. Potential Friction Points (where there might be challenges)
4. Recommendations for Success (how to bridge gaps)
5. Red Flags (if any serious concerns)
6. Overall Recommendation (Strong Fit / Good Fit / Moderate Fit / Poor Fit)

Be thorough and balanced."""

        response = self.llm.invoke(prompt)
        
        # Calculate a simulated fit score
        fit_score = self._calculate_fit_score(candidate_values, company_values)
        
        return {
            "success": True,
            "candidate": candidate_name,
            "company": company_name,
            "fit_score": fit_score,
            "analysis": response.content,
            "message": f"Culture fit analysis completed for {candidate_name} and {company_name}"
        }
    
    def _create_culture_profile(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a culture profile for candidate or company."""
        entity_name = params.get("name", "Entity")
        entity_type = params.get("type", "candidate")  # candidate or company
        background_info = params.get("background", "")
        
        prompt = f"""Create a comprehensive culture profile for this {entity_type}.

{entity_type.title()}: {entity_name}
Background: {background_info if background_info else "General profile"}

Provide:
1. Core Values (top 5)
2. Work Style Preferences
3. Communication Style
4. Decision-Making Approach
5. Ideal Environment Characteristics
6. Potential Culture Clashes to Watch For
7. Strengths in Team Settings

Be specific and insightful."""

        response = self.llm.invoke(prompt)
        
        return {
            "success": True,
            "entity": entity_name,
            "type": entity_type,
            "culture_profile": response.content,
            "message": f"Culture profile created for {entity_name}"
        }
    
    def _analyze_team_dynamics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze how a candidate would fit into existing team dynamics."""
        candidate_name = params.get("candidate_name", "Candidate")
        team_description = params.get("team_description", "")
        team_size = params.get("team_size", 5)
        candidate_personality = params.get("personality", "")
        
        prompt = f"""Analyze how this candidate would integrate into the existing team.

Candidate: {candidate_name}
Personality Traits: {candidate_personality if candidate_personality else "Collaborative, analytical, proactive"}

Team Context:
- Size: {team_size} members
- Description: {team_description if team_description else "Cross-functional, fast-paced environment"}

Provide:
1. Integration Potential (High / Medium / Low) with reasoning
2. Role They Might Naturally Fill (e.g., mediator, innovator, executor)
3. Complementary Strengths (what they add to the team)
4. Potential Challenges (dynamics to watch)
5. Onboarding Recommendations (how to set them up for success)
6. Team Composition Impact (how they change team balance)

Be practical and team-focused."""

        response = self.llm.invoke(prompt)
        
        return {
            "success": True,
            "candidate": candidate_name,
            "team_size": team_size,
            "dynamics_analysis": response.content,
            "message": f"Team dynamics analysis completed for {candidate_name}"
        }
    
    def _comprehensive_culture_analysis(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Provide comprehensive culture analysis."""
        candidate_name = params.get("candidate_name", "Candidate")
        company_name = params.get("company_name", "Company")
        
        prompt = f"""Provide a comprehensive culture compatibility analysis for {candidate_name} joining {company_name}.

Include:
1. Cultural Dimensions Analysis (Hofstede's dimensions or similar)
2. Values Alignment Matrix
3. Work Environment Compatibility
4. Communication Style Match
5. Growth and Development Alignment
6. Long-term Success Indicators
7. Risk Factors and Mitigation Strategies

Be comprehensive and actionable."""

        response = self.llm.invoke(prompt)
        
        return {
            "success": True,
            "candidate": candidate_name,
            "company": company_name,
            "comprehensive_analysis": response.content,
            "message": "Comprehensive culture analysis completed"
        }
    
    def _calculate_fit_score(self, candidate_values: List[str], company_values: List[str]) -> int:
        """Calculate a simulated culture fit score."""
        if not candidate_values or not company_values:
            return 75  # Default moderate-high fit
        
        # Simple overlap calculation
        candidate_set = set(v.lower() for v in candidate_values)
        company_set = set(v.lower() for v in company_values)
        
        if not candidate_set or not company_set:
            return 75
        
        overlap = len(candidate_set & company_set)
        total = len(candidate_set | company_set)
        
        # Score between 60-95 based on overlap
        base_score = 60
        overlap_bonus = (overlap / total) * 35 if total > 0 else 15
        
        return int(base_score + overlap_bonus)
    
    def get_capabilities(self) -> List[str]:
        """Return module capabilities."""
        return [
            "Assess culture fit",
            "Create culture profiles",
            "Analyze team dynamics",
            "Values alignment analysis",
            "Work style compatibility",
            "Long-term success prediction",
            "Culture clash identification"
        ]
