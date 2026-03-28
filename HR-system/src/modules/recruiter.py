"""
Recruiter module for candidate screening and management.
"""
from typing import Dict, Any, List
from core.base_module import BaseModule
from langchain_openai import ChatOpenAI
from utils.database import get_database
from utils.gmail import get_gmail


class Recruiter(BaseModule):
    """Handles candidate screening, evaluation, and recruitment tasks."""
    
    def __init__(self):
        super().__init__("recruiter")
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.2)
        self.db = get_database()
        self.gmail_api = get_gmail()
    
    def can_handle(self, task: Dict[str, Any]) -> bool:
        """Check if this module can handle the task."""
        task_type = task.get("type", "")
        keywords = ["recruit", "candidate", "screening", "hire", "applicant", "resume"]
        description = task.get("description", "").lower()
        
        return task_type == "recruit" or any(kw in description for kw in keywords)
    
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute recruitment task."""
        params = task.get("params", {})
        description = task.get("description", "").lower()
        
        # Determine specific recruitment action
        if "screen" in description or "evaluate" in description:
            return self._screen_candidate(params)
        elif "shortlist" in description or "recommend" in description:
            return self._shortlist_candidates(params)
        elif "status" in description or "track" in description:
            return self._track_candidate_status(params)
        elif "add" in description or "register" in description:
            return self._add_candidate(params)
        else:
            return self._general_recruitment_advice(params, description)
    
    def _add_candidate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new candidate to the database."""
        try:
            candidate_id = self.db.add_candidate(params)
            
            return {
                "success": True,
                "candidate_id": candidate_id,
                "message": f"Candidate {params.get('name', 'Unknown')} added to database",
                "email": params.get('email', '')
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to add candidate to database"
            }
    
    def _screen_candidate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Screen a candidate based on job requirements."""
        candidate_name = params.get("candidate_name", "Candidate")
        candidate_email = params.get("candidate_email", "")
        job_role = params.get("job_role", "Software Engineer")
        resume_summary = params.get("resume_summary", "")
        required_skills = params.get("required_skills", [])
        
        # Check if candidate exists in database
        candidate_data = None
        if candidate_email:
            candidate_data = self.db.get_candidate(candidate_email)
        
        # Build context from database if available
        db_context = ""
        if candidate_data:
            db_context = f"""
Database Information:
- Email: {candidate_data.get('email', 'N/A')}
- College: {candidate_data.get('college', 'N/A')}
- Degree: {candidate_data.get('degree', 'N/A')}
- CPI/GPA: {candidate_data.get('cpi', 'N/A')}
- Graduation Year: {candidate_data.get('graduation_year', 'N/A')}
- Skills: {', '.join(candidate_data.get('skills', []))}
- Experience: {candidate_data.get('experience_years', 0)} years
- LinkedIn: {candidate_data.get('linkedin_url', 'N/A')}
- GitHub: {candidate_data.get('github_url', 'N/A')}
"""
        
        prompt = f"""You are an expert recruiter. Screen this candidate for the {job_role} position.

Candidate: {candidate_name}
Resume Summary: {resume_summary if resume_summary else "Not provided"}
Required Skills: {', '.join(required_skills) if required_skills else "General technical skills"}

{db_context}

Provide:
1. Match Score (0-100)
2. Key Strengths (3-5 points)
3. Potential Concerns (if any)
4. Recommendation (Strong Yes / Yes / Maybe / No)
5. Suggested Interview Focus Areas

Be concise and professional."""

        response = self.llm.invoke(prompt)
        
        # Extract score from response (simple heuristic)
        score = 75  # default
        if "Strong Yes" in response.content or "95" in response.content or "90" in response.content:
            score = 92
        elif "Yes" in response.content or "85" in response.content:
            score = 85
        elif "Maybe" in response.content or "70" in response.content:
            score = 70
        elif "No" in response.content:
            score = 50
        
        # Update database with screening score
        if candidate_email and candidate_data:
            self.db.update_candidate(candidate_email, {
                "screening_score": score,
                "status": "screened"
            })
        
        return {
            "success": True,
            "candidate": candidate_name,
            "email": candidate_email,
            "role": job_role,
            "screening_score": score,
            "screening_result": response.content,
            "action": "Candidate screened successfully",
            "from_database": candidate_data is not None
        }
    
    def _shortlist_candidates(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a shortlist of top candidates from database."""
        job_role = params.get("job_role", "Position")
        num_candidates = params.get("num_candidates", 5)
        min_score = params.get("min_score", 70)
        
        # Get all candidates from database
        all_candidates = self.db.get_all_candidates()
        
        # Filter by screening score and sort
        qualified = [
            c for c in all_candidates 
            if c.get('screening_score', 0) >= min_score
        ]
        qualified.sort(key=lambda x: x.get('screening_score', 0), reverse=True)
        
        shortlist = qualified[:num_candidates]
        
        # Format shortlist
        formatted_shortlist = [
            {
                "name": c.get('name', 'Unknown'),
                "email": c.get('email', ''),
                "score": c.get('screening_score', 0),
                "college": c.get('college', 'N/A'),
                "experience": f"{c.get('experience_years', 0)} years",
                "skills": c.get('skills', [])
            }
            for c in shortlist
        ]
        
        return {
            "success": True,
            "role": job_role,
            "shortlist": formatted_shortlist,
            "total_candidates": len(all_candidates),
            "qualified_candidates": len(qualified),
            "message": f"Generated shortlist of top {len(formatted_shortlist)} candidates for {job_role}"
        }
    
    def _track_candidate_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Track candidate progress through recruitment pipeline."""
        candidate_email = params.get("candidate_email", "")
        
        if candidate_email:
            # Get specific candidate
            candidate = self.db.get_candidate(candidate_email)
            if candidate:
                return {
                    "success": True,
                    "candidate": candidate.get('name', 'Unknown'),
                    "email": candidate_email,
                    "status": candidate.get('status', 'unknown'),
                    "screening_score": candidate.get('screening_score'),
                    "culture_fit_score": candidate.get('culture_fit_score'),
                    "interviews": candidate.get('interviews', []),
                    "message": f"Status for {candidate.get('name', 'Unknown')}"
                }
        
        # Get pipeline overview
        all_candidates = self.db.get_all_candidates()
        
        pipeline = {}
        for candidate in all_candidates:
            status = candidate.get('status', 'unknown')
            pipeline[status] = pipeline.get(status, 0) + 1
        
        return {
            "success": True,
            "pipeline_status": pipeline,
            "total_candidates": len(all_candidates),
            "message": "Current recruitment pipeline status"
        }
    
    def _general_recruitment_advice(self, params: Dict[str, Any], description: str) -> Dict[str, Any]:
        """Provide general recruitment guidance."""
        prompt = f"""You are an expert recruiter. Provide helpful advice for this request:

Request: {description}
Context: {params}

Give practical, actionable advice in 3-5 bullet points."""

        response = self.llm.invoke(prompt)
        
        return {
            "success": True,
            "advice": response.content,
            "message": "Recruitment guidance provided"
        }
    
    def get_capabilities(self) -> List[str]:
        """Return module capabilities."""
        capabilities = [
            "Screen candidates",
            "Evaluate resumes",
            "Create candidate shortlists",
            "Track recruitment pipeline",
            "Provide hiring recommendations",
            "Assess candidate-role fit",
            "✅ Database integration active",
            f"📊 {len(self.db.get_all_candidates())} candidates in database"
        ]
        
        if self.gmail_api.is_available():
            capabilities.append("✅ Email notifications active")
        else:
            capabilities.append("⚠️ Email notifications not configured")
        
        return capabilities
