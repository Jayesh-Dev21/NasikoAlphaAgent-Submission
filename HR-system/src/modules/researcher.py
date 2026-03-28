"""
Researcher module for gathering information about candidates and companies.
"""
from typing import Dict, Any, List
from core.base_module import BaseModule
from langchain_openai import ChatOpenAI
from utils.database import get_database
import logging

logger = logging.getLogger(__name__)


class Researcher(BaseModule):
    """Conducts research on candidates, companies, and market trends."""
    
    def __init__(self):
        super().__init__("researcher")
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.3)
        self.db = get_database()
    
    def can_handle(self, task: Dict[str, Any]) -> bool:
        """Check if this module can handle the task."""
        task_type = task.get("type", "")
        keywords = ["research", "background", "investigate", "find", "lookup", "information"]
        description = task.get("description", "").lower()
        
        return task_type == "research" or any(kw in description for kw in keywords)
    
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute research task."""
        params = task.get("params", {})
        description = task.get("description", "").lower()
        
        if "candidate" in description:
            return self._research_candidate(params)
        elif "company" in description or "organization" in description:
            return self._research_company(params)
        elif "salary" in description or "compensation" in description:
            return self._research_salary(params)
        elif "market" in description or "trend" in description:
            return self._research_market_trends(params)
        else:
            return self._general_research(params, description)
    
    def _research_candidate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Research candidate background using actual database data."""
        candidate_name = params.get("candidate_name", "Candidate")
        focus_areas = params.get("focus_areas", ["professional background", "skills", "achievements"])
        
        # Try to find candidate in database
        candidate_data = None
        
        # Search by name in database
        try:
            query = {"name": {"$regex": candidate_name, "$options": "i"}}
            candidates = self.db.search_candidates(query)
            if candidates:
                candidate_data = candidates[0]  # Take first match
                logger.info(f"Found candidate data for {candidate_name} in database")
        except Exception as e:
            logger.warning(f"Could not search database for candidate: {e}")
        
        # If we have real data, use it
        if candidate_data:
            return self._research_from_database(candidate_data, focus_areas)
        else:
            # No data found - return minimal response
            return {
                "success": False,
                "candidate": candidate_name,
                "research_summary": f"No detailed information found for {candidate_name} in our database. Please add the candidate to the system first or provide more details.",
                "message": f"No data available for {candidate_name}"
            }
    
    def _research_from_database(self, candidate_data: Dict[str, Any], focus_areas: List[str]) -> Dict[str, Any]:
        """Create research summary from actual database data."""
        name = candidate_data.get('name', 'Unknown')
        email = candidate_data.get('email', 'N/A')
        
        # Build research summary from real data
        summary_parts = []
        
        # Professional Background
        summary_parts.append(f"### Professional Background for {name}")
        summary_parts.append(f"**Email**: {email}")
        
        # Education
        college = candidate_data.get('college', '')
        degree = candidate_data.get('degree', '')
        cpi = candidate_data.get('cpi', 0)
        if college:
            summary_parts.append(f"\n**Education**:")
            summary_parts.append(f"- College: {college}")
            if degree:
                summary_parts.append(f"- Degree: {degree}")
            if cpi > 0:
                summary_parts.append(f"- CPI/GPA: {cpi}")
        
        # Experience
        experience_years = candidate_data.get('experience_years', 0)
        current_company = candidate_data.get('current_company', '')
        current_position = candidate_data.get('current_position', '')
        if experience_years > 0:
            summary_parts.append(f"\n**Experience**: {experience_years} years")
            if current_company:
                summary_parts.append(f"- Current Company: {current_company}")
            if current_position:
                summary_parts.append(f"- Current Position: {current_position}")
        
        # Skills
        skills = candidate_data.get('skills', [])
        if skills:
            summary_parts.append(f"\n**Key Skills**:")
            for skill in skills:
                summary_parts.append(f"- {skill}")
        
        # Professional Links (only if they exist)
        available_links = []
        linkedin_url = candidate_data.get('linkedin_url', '')
        github_url = candidate_data.get('github_url', '')
        portfolio_url = candidate_data.get('portfolio_url', '')
        
        if linkedin_url:
            available_links.append(f"- LinkedIn: {linkedin_url}")
        if github_url:
            available_links.append(f"- GitHub: {github_url}")
        if portfolio_url:
            available_links.append(f"- Portfolio: {portfolio_url}")
        
        if available_links:
            summary_parts.append(f"\n**Professional Links**:")
            summary_parts.extend(available_links)
        
        # Screening Results (if available)
        screening_score = candidate_data.get('screening_score')
        culture_fit_score = candidate_data.get('culture_fit_score')
        technical_score = candidate_data.get('technical_score')
        
        if screening_score or culture_fit_score or technical_score:
            summary_parts.append(f"\n**Assessment Scores**:")
            if screening_score:
                summary_parts.append(f"- Screening Score: {screening_score}/100")
            if culture_fit_score:
                summary_parts.append(f"- Culture Fit Score: {culture_fit_score}/100")
            if technical_score:
                summary_parts.append(f"- Technical Score: {technical_score}/100")
        
        # Status
        status = candidate_data.get('status', 'unknown')
        summary_parts.append(f"\n**Current Status**: {status.title()}")
        
        # Notes (if any)
        notes = candidate_data.get('notes', '')
        if notes:
            summary_parts.append(f"\n**Additional Notes**: {notes}")
        
        research_summary = "\n".join(summary_parts)
        
        # Determine available sources based on what data exists
        sources = ["Internal Database"]
        if linkedin_url:
            sources.append("LinkedIn Profile Available")
        if github_url:
            sources.append("GitHub Profile Available")
        if portfolio_url:
            sources.append("Portfolio Available")
        
        return {
            "success": True,
            "candidate": name,
            "email": email,
            "research_summary": research_summary,
            "sources": sources,
            "has_linkedin": bool(linkedin_url),
            "has_github": bool(github_url),
            "has_portfolio": bool(portfolio_url),
            "message": f"Completed background research on {name} using database records"
        }
    
    def _research_company(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Research company information."""
        company_name = params.get("company_name", "Target Company")
        
        prompt = f"""Provide a comprehensive company overview for {company_name} from an HR perspective.

Include:
1. Company size and industry
2. Work culture and values
3. Employee benefits and perks
4. Growth trajectory
5. Reputation as an employer

Be realistic and professional."""

        response = self.llm.invoke(prompt)
        
        return {
            "success": True,
            "company": company_name,
            "research_summary": response.content,
            "message": f"Completed company research on {company_name}"
        }
    
    def _research_salary(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Research salary and compensation data."""
        job_role = params.get("job_role", "Software Engineer")
        location = params.get("location", "United States")
        experience_level = params.get("experience_level", "mid-level")
        
        # Simulated salary data
        salary_ranges = {
            "entry-level": {"min": 60000, "max": 85000, "median": 72000},
            "mid-level": {"min": 85000, "max": 130000, "median": 105000},
            "senior": {"min": 130000, "max": 180000, "median": 155000},
            "lead": {"min": 160000, "max": 220000, "median": 190000}
        }
        
        salary_data = salary_ranges.get(experience_level, salary_ranges["mid-level"])
        
        return {
            "success": True,
            "role": job_role,
            "location": location,
            "experience_level": experience_level,
            "salary_range": {
                "minimum": f"${salary_data['min']:,}",
                "maximum": f"${salary_data['max']:,}",
                "median": f"${salary_data['median']:,}"
            },
            "additional_info": "Includes base salary. Total compensation may include bonuses, equity, and benefits.",
            "message": f"Salary research completed for {experience_level} {job_role} in {location}"
        }
    
    def _research_market_trends(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Research hiring market trends."""
        industry = params.get("industry", "Technology")
        
        prompt = f"""Provide current hiring market trends for the {industry} industry.

Include:
1. In-demand skills
2. Hiring challenges
3. Salary trends
4. Remote work trends
5. Key predictions for the next 6-12 months

Be data-informed and practical."""

        response = self.llm.invoke(prompt)
        
        return {
            "success": True,
            "industry": industry,
            "trends_summary": response.content,
            "message": f"Market trends research completed for {industry}"
        }
    
    def _general_research(self, params: Dict[str, Any], description: str) -> Dict[str, Any]:
        """Conduct general research."""
        prompt = f"""You are an HR researcher. Provide helpful research for this request:

Request: {description}
Context: {params}

Provide comprehensive, well-organized information."""

        response = self.llm.invoke(prompt)
        
        return {
            "success": True,
            "research_summary": response.content,
            "message": "Research completed"
        }
    
    def get_capabilities(self) -> List[str]:
        """Return module capabilities."""
        return [
            "Research candidate backgrounds",
            "Company information lookup",
            "Salary and compensation research",
            "Market trend analysis",
            "Industry insights",
            "Competitive intelligence"
        ]
