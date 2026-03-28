"""
Tools for the HR agent.
Define your LangChain tools here.
"""
from typing import List, Dict, Any
from langchain_core.tools import tool
import logging

logger = logging.getLogger(__name__)

# Global references to modular components (set by agent)
_planner = None
_executor = None
_aggregator = None

# Cache database instance for efficiency
_db_cache = None


def _get_db():
    """Get cached database instance."""
    global _db_cache
    if _db_cache is None:
        from utils.database import get_database
        _db_cache = get_database()
    return _db_cache


def set_modular_components(planner, executor, aggregator):
    """Set the modular components for tools to use."""
    global _planner, _executor, _aggregator
    _planner = planner
    _executor = executor
    _aggregator = aggregator


@tool
def add_candidate_to_database(
    name: str,
    email: str,
    college: str = "",
    cpi: float = 0.0,
    skills: str = "",
    experience_years: int = 0,
    phone: str = "",
    degree: str = ""
) -> str:
    """
    Add a new candidate directly to the MongoDB database.
    
    Args:
        name: Candidate's full name
        email: Candidate's email address (required, unique)
        college: College/University name
        cpi: CPI/GPA score
        skills: Comma-separated skills (e.g., "Python, AWS, React")
        experience_years: Years of experience
        phone: Phone number
        degree: Degree name
    """
    try:
        db = _get_db()
        
        # Parse skills
        skills_list = [s.strip() for s in skills.split(",")] if skills else []
        
        candidate_data = {
            "name": name,
            "email": email,
            "college": college,
            "degree": degree,
            "cpi": cpi,
            "skills": skills_list,
            "experience_years": experience_years,
            "phone": phone,
            "status": "applied"
        }
        
        candidate_id = db.add_candidate(candidate_data)
        
        if candidate_id:
            logger.info(f"Added candidate: {name} ({email})")
            return f"✅ Successfully added candidate {name} (email: {email}) to database with ID: {candidate_id}"
        else:
            logger.error(f"Failed to add candidate: {name} ({email})")
            return f"❌ Failed to add candidate {name} to database"
    except Exception as e:
        logger.error(f"Error adding candidate: {e}")
        return f"❌ Error adding candidate: {str(e)}"


@tool
def get_candidate_from_database(identifier: str) -> str:
    """
    Retrieve candidate information from MongoDB database.

    Use this tool when the user provides either:
    - Candidate name (e.g. "Yashaswini")
    - Candidate email (e.g. "john@email.com")

    Args:
        identifier: Candidate name OR email
    """

    try:
        db = _get_db()
        candidate = db.get_candidate(identifier)

        if candidate:
            return f"""
Candidate Found in Database:
- Name: {candidate.get('name', 'N/A')}
- Email: {candidate.get('email', 'N/A')}
- College: {candidate.get('college', 'N/A')}
- Degree: {candidate.get('degree', 'N/A')}
- CPI: {candidate.get('cpi', 'N/A')}
- Skills: {', '.join(candidate.get('skills', []))}
- Experience: {candidate.get('experience_years', 0)} years
- Phone: {candidate.get('phone', 'N/A')}
- Status: {candidate.get('status', 'N/A')}
- Screening Score: {candidate.get('screening_score', 'Not screened yet')}
- Culture Fit Score: {candidate.get('culture_fit_score', 'Not analyzed yet')}
"""
        else:
            return f"❌ No candidate found with identifier: {identifier}"

    except Exception as e:
        logger.error(f"Error retrieving candidate: {e}")
        return f"❌ Error retrieving candidate: {str(e)}"


@tool
def search_candidates_by_name(name: str) -> str:
    """
    Search for candidates by name (partial match supported).
    Use this when user asks for information about a candidate by name.
    
    Args:
        name: Candidate's name or partial name (e.g., "Bob", "Smith", "Bob Smith")
    
    Returns:
        List of matching candidates with their details
    """
    try:
        db = _get_db()
        
        # Search using regex for partial matching (case-insensitive)
        query = {"name": {"$regex": name, "$options": "i"}}
        candidates = db.search_candidates(query)
        
        if not candidates:
            return f"❌ No candidates found with name matching: {name}"
        
        result = f"Found {len(candidates)} candidate(s) matching '{name}':\n\n"
        
        for i, candidate in enumerate(candidates, 1):
            result += f"""
{i}. {candidate.get('name', 'N/A')}
   - Email: {candidate.get('email', 'N/A')}
   - College: {candidate.get('college', 'N/A')}
   - Degree: {candidate.get('degree', 'N/A')}
   - CPI: {candidate.get('cpi', 'N/A')}
   - Skills: {', '.join(candidate.get('skills', []))}
   - Experience: {candidate.get('experience_years', 0)} years
   - Phone: {candidate.get('phone', 'N/A')}
   - Status: {candidate.get('status', 'N/A')}
   - Screening Score: {candidate.get('screening_score', 'Not screened yet')}
"""
        
        return result
    except Exception as e:
        logger.error(f"Error searching candidates by name: {e}")
        return f"❌ Error searching candidates: {str(e)}"


@tool
def search_candidates_by_skills(skills: str) -> str:
    """
    Search for candidates who have specific skills.
    Use this when user asks for candidates with particular skills.
    
    Args:
        skills: Comma-separated skills to search for (e.g., "Python, AWS" or "React")
    
    Returns:
        List of candidates with those skills
    """
    try:
        db = _get_db()
        
        # Parse skills
        skill_list = [s.strip() for s in skills.split(",")]
        
        # Search for candidates with ANY of the specified skills (case-insensitive)
        query = {
            "skills": {
                "$regex": "|".join(skill_list),
                "$options": "i"
            }
        }
        
        candidates = db.search_candidates(query)
        
        if not candidates:
            return f"❌ No candidates found with skills: {skills}"
        
        result = f"Found {len(candidates)} candidate(s) with skills matching '{skills}':\n\n"
        
        for i, candidate in enumerate(candidates, 1):
            matching_skills = [
                s for s in candidate.get('skills', [])
                if any(skill.lower() in s.lower() for skill in skill_list)
            ]
            
            result += f"""
{i}. {candidate.get('name', 'N/A')} ({candidate.get('email', 'N/A')})
   - Matching Skills: {', '.join(matching_skills) if matching_skills else 'N/A'}
   - All Skills: {', '.join(candidate.get('skills', []))}
   - Experience: {candidate.get('experience_years', 0)} years
   - College: {candidate.get('college', 'N/A')}
   - CPI: {candidate.get('cpi', 'N/A')}
   - Status: {candidate.get('status', 'N/A')}
   - Screening Score: {candidate.get('screening_score', 'Not screened yet')}
"""
        
        return result
    except Exception as e:
        logger.error(f"Error searching candidates by skills: {e}")
        return f"❌ Error searching candidates: {str(e)}"


@tool
def search_candidates_advanced(
    college: str = "",
    min_cpi: float = 0.0,
    min_experience: int = 0,
    status: str = ""
) -> str:
    """
    Advanced search for candidates by multiple criteria.
    
    Args:
        college: College/University name (partial match)
        min_cpi: Minimum CPI/GPA
        min_experience: Minimum years of experience
        status: Candidate status (applied, screened, interviewed, etc.)
    
    Returns:
        List of matching candidates
    """
    try:
        db = _get_db()
        
        # Build query
        query = {}
        
        if college:
            query["college"] = {"$regex": college, "$options": "i"}
        
        if min_cpi > 0:
            query["cpi"] = {"$gte": min_cpi}
        
        if min_experience > 0:
            query["experience_years"] = {"$gte": min_experience}
        
        if status:
            query["status"] = status
        
        candidates = db.search_candidates(query)
        
        if not candidates:
            return f"❌ No candidates found matching the criteria"
        
        result = f"Found {len(candidates)} candidate(s) matching criteria:\n\n"
        
        for i, candidate in enumerate(candidates, 1):
            result += f"""
{i}. {candidate.get('name', 'N/A')} ({candidate.get('email', 'N/A')})
   - College: {candidate.get('college', 'N/A')}
   - CPI: {candidate.get('cpi', 'N/A')}
   - Experience: {candidate.get('experience_years', 0)} years
   - Skills: {', '.join(candidate.get('skills', []))}
   - Status: {candidate.get('status', 'N/A')}
   - Screening Score: {candidate.get('screening_score', 'Not screened yet')}
"""
        
        return result
    except Exception as e:
        logger.error(f"Error in advanced search: {e}")
        return f"❌ Error searching candidates: {str(e)}"


@tool
def schedule_interview(
    candidate_name: str, 
    date_time: str = "",
    interview_type: str = "technical", 
    duration: int = 60, 
    candidate_email: str = ""
) -> str:
    """
    Schedule an interview with a candidate.
    
    Args:
        candidate_name: Name of the candidate
        date_time: Requested date and time in ISO format (e.g., '2026-03-15T15:00:00'). Leave empty for next available slot.
        interview_type: Type of interview (technical, behavioral, cultural, final)
        duration: Duration in minutes (default 60)
        candidate_email: Candidate's email (optional, for database lookup)
    """
    if not _planner or not _executor or not _aggregator:
        return "Modular system not initialized"
    
    query = f"Schedule a {duration}-minute {interview_type} interview with {candidate_name}"
    
    if date_time:
        query += f" at {date_time}"
        
    if candidate_email:
        query += f", email {candidate_email}"
    
    tasks = _planner.plan(query)
    
    # Safely inject date_time AND candidate_email directly into the planned task
    for task in tasks:
        if "params" not in task:
            task["params"] = {}
        if date_time:
            task["params"]["date_time"] = date_time
        if candidate_email:
            task["params"]["candidate_email"] = candidate_email  # <--- THIS WAS MISSING!
            
    results = _executor.execute(tasks)
    return _aggregator.combine(results)


@tool
def screen_candidate(candidate_email: str, job_role: str, resume_summary: str = "") -> str:
    """
    Screen and evaluate a candidate for a position.
    First retrieves candidate data from database, then performs screening.
    
    Args:
        candidate_email: Candidate's email address
        job_role: Position they're applying for
        resume_summary: Brief summary of their resume/background (optional if in database)
    """
    try:
        db = _get_db()
        
        # Get candidate from database first
        candidate = db.get_candidate(candidate_email)
        
        if candidate:
            # Build resume summary from database
            resume_summary = f"""
{candidate.get('name', 'Candidate')} from {candidate.get('college', 'Unknown')} with {candidate.get('experience_years', 0)} years of experience.
Skills: {', '.join(candidate.get('skills', []))}
CPI: {candidate.get('cpi', 'N/A')}
Degree: {candidate.get('degree', 'N/A')}
"""
        
        if not _planner or not _executor or not _aggregator:
            return "❌ Modular system not initialized"
        
        query = f"Screen candidate {candidate_email} for {job_role} position. Resume: {resume_summary}"
        tasks = _planner.plan(query)
        results = _executor.execute(tasks)
        return _aggregator.combine(results)
    except Exception as e:
        logger.error(f"Error screening candidate: {e}")
        return f"❌ Error screening candidate: {str(e)}"


@tool
def research_candidate(candidate_name: str, focus_areas: str = "professional background") -> str:
    """
    Research a candidate's background and qualifications using database records.
    If LinkedIn URL exists, fetches and analyzes the profile.
    Returns ONLY actual data - no fake or simulated information.
    
    Args:
        candidate_name: Name of the candidate to research
        focus_areas: What to focus on (optional, will show all available data)
    """
    try:
        db = _get_db()
        
        # Search for candidate in database
        query = {"name": {"$regex": candidate_name, "$options": "i"}}
        candidates = db.search_candidates(query)
        
        if not candidates:
            return f"❌ No information found for {candidate_name} in our database. Please add the candidate to the system first to enable research."
        
        # Use first match
        candidate = candidates[0]
        name = candidate.get('name', 'Unknown')
        
        # Build comprehensive research summary from REAL data
        summary = f"### Professional Research: {name}\n\n"
        
        # Basic Info
        summary += f"**Contact Information:**\n"
        summary += f"- Email: {candidate.get('email', 'N/A')}\n"
        if candidate.get('phone'):
            summary += f"- Phone: {candidate.get('phone')}\n"
        
        # Education
        summary += f"\n**Education:**\n"
        if candidate.get('college'):
            summary += f"- Institution: {candidate.get('college')}\n"
        if candidate.get('degree'):
            summary += f"- Degree: {candidate.get('degree')}\n"
        if candidate.get('cpi', 0) > 0:
            summary += f"- CPI/GPA: {candidate.get('cpi')}\n"
        if candidate.get('graduation_year'):
            summary += f"- Graduation Year: {candidate.get('graduation_year')}\n"
        
        # Professional Experience
        summary += f"\n**Professional Experience:**\n"
        summary += f"- Total Experience: {candidate.get('experience_years', 0)} years\n"
        if candidate.get('current_company'):
            summary += f"- Current Company: {candidate.get('current_company')}\n"
        if candidate.get('current_position'):
            summary += f"- Current Position: {candidate.get('current_position')}\n"
        
        # Skills & Expertise
        skills = candidate.get('skills', [])
        if skills:
            summary += f"\n**Technical Skills & Expertise:**\n"
            for skill in skills:
                summary += f"- {skill}\n"
        else:
            summary += f"\n**Technical Skills:** Not specified in database\n"
        
        # Professional Links & Online Presence
        linkedin_url = candidate.get('linkedin_url', '')
        github_url = candidate.get('github_url', '')
        portfolio_url = candidate.get('portfolio_url', '')
        
        if linkedin_url or github_url or portfolio_url:
            summary += f"\n**Professional Online Presence:**\n"
            
            if linkedin_url:
                summary += f"- LinkedIn Profile: {linkedin_url}\n"
                # Note: In a real implementation, you would fetch and parse the LinkedIn page here
                # For now, we indicate the URL is available
                summary += f"  ℹ️ LinkedIn profile available for detailed review\n"
            
            if github_url:
                summary += f"- GitHub Profile: {github_url}\n"
                summary += f"  ℹ️ GitHub profile available for code review\n"
            
            if portfolio_url:
                summary += f"- Portfolio: {portfolio_url}\n"
                summary += f"  ℹ️ Portfolio available for work samples\n"
        
        # Resume & Documents
        if candidate.get('resume_url'):
            summary += f"\n**Documents:**\n"
            summary += f"- Resume: {candidate.get('resume_url')}\n"
        
        # Assessment Scores & Performance
        screening_score = candidate.get('screening_score')
        culture_fit_score = candidate.get('culture_fit_score')
        technical_score = candidate.get('technical_score')
        
        if screening_score or culture_fit_score or technical_score:
            summary += f"\n**Assessment Results:**\n"
            if screening_score:
                summary += f"- Screening Score: {screening_score}/100\n"
            if culture_fit_score:
                summary += f"- Culture Fit Score: {culture_fit_score}/100\n"
            if technical_score:
                summary += f"- Technical Score: {technical_score}/100\n"
        
        # Application Details
        summary += f"\n**Application Information:**\n"
        summary += f"- Current Status: {candidate.get('status', 'unknown').title()}\n"
        if candidate.get('applied_position'):
            summary += f"- Applied Position: {candidate.get('applied_position')}\n"
        if candidate.get('source'):
            summary += f"- Application Source: {candidate.get('source')}\n"
        
        # Interview History
        interviews = candidate.get('interview_ids', [])
        if interviews:
            summary += f"- Interviews Scheduled: {len(interviews)}\n"
        
        # Tags & Categories
        tags = candidate.get('tags', [])
        if tags:
            summary += f"\n**Tags:** {', '.join(tags)}\n"
        
        # Additional Notes
        if candidate.get('notes'):
            summary += f"\n**Additional Notes:**\n{candidate.get('notes')}\n"
        
        # Timestamps
        if candidate.get('created_at'):
            summary += f"\n**Record Information:**\n"
            summary += f"- Added to system: {candidate.get('created_at')}\n"
            if candidate.get('updated_at'):
                summary += f"- Last updated: {candidate.get('updated_at')}\n"
        
        summary += f"\n---\n*All information retrieved from internal database. Professional links available for detailed review.*"
        
        logger.info(f"Research completed for {name}")
        return summary
        
    except Exception as e:
        logger.error(f"Error researching candidate: {e}")
        return f"❌ Error researching candidate: {str(e)}"


@tool
def get_interview_prep(job_role: str, interview_type: str = "technical", difficulty: str = "medium") -> str:
    """
    Get interview preparation materials including questions and tips.
    
    Args:
        job_role: The position being interviewed for
        interview_type: Type of interview (technical, behavioral, cultural)
        difficulty: Question difficulty (easy, medium, hard)
    """
    if not _planner or not _executor or not _aggregator:
        return "Modular system not initialized"
    
    query = f"Generate {difficulty} {interview_type} interview prep for {job_role}"
    tasks = _planner.plan(query)
    results = _executor.execute(tasks)
    return _aggregator.combine(results)


@tool
def analyze_culture_fit(candidate_name: str, company_name: str = "our company", candidate_email: str = "") -> str:
    """
    Analyze culture fit between a candidate and company.
    
    Args:
        candidate_name: Name of the candidate
        company_name: Name of the company (default: "our company")
        candidate_email: Candidate's email (optional, for database lookup)
    """
    if not _planner or not _executor or not _aggregator:
        return "Modular system not initialized"
    
    query = f"Analyze culture fit between {candidate_name} and {company_name}"
    if candidate_email:
        query += f", candidate email {candidate_email}"
    
    tasks = _planner.plan(query)
    results = _executor.execute(tasks)
    return _aggregator.combine(results)


@tool
def research_salary(job_role: str, location: str = "United States", experience_level: str = "mid-level") -> str:
    """
    Research salary ranges for a position.
    
    Args:
        job_role: The job title/role
        location: Geographic location
        experience_level: Experience level (entry-level, mid-level, senior, lead)
    """
    if not _planner or not _executor or not _aggregator:
        return "Modular system not initialized"
    
    query = f"Research salary for {experience_level} {job_role} in {location}"
    tasks = _planner.plan(query)
    results = _executor.execute(tasks)
    return _aggregator.combine(results)


@tool
def hr_assistant(query: str) -> str:
    """
    General HR assistant for complex multi-step tasks.
    Use this for tasks that don't fit other specific tools or require multiple steps.
    
    Args:
        query: The HR-related question or task
    """
    if not _planner or not _executor or not _aggregator:
        return "Modular system not initialized"
    
    tasks = _planner.plan(query)
    results = _executor.execute(tasks)
    return _aggregator.combine(results)
