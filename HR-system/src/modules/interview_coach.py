"""
Interview Coach module - Unique feature for interview preparation and feedback.
"""
from typing import Dict, Any, List
from core.base_module import BaseModule
from langchain_openai import ChatOpenAI


class InterviewCoach(BaseModule):
    """Provides interview preparation, practice questions, and feedback."""
    
    def __init__(self):
        super().__init__("interview_coach")
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.4)
    
    def can_handle(self, task: Dict[str, Any]) -> bool:
        """Check if this module can handle the task."""
        task_type = task.get("type", "")
        keywords = ["interview prep", "practice", "questions", "coaching", "feedback", "mock interview"]
        description = task.get("description", "").lower()
        
        return task_type == "interview_prep" or any(kw in description for kw in keywords)
    
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute interview coaching task."""
        params = task.get("params", {})
        description = task.get("description", "").lower()
        
        if "questions" in description or "prepare" in description:
            return self._generate_interview_questions(params)
        elif "feedback" in description or "evaluate" in description:
            return self._provide_interview_feedback(params)
        elif "tips" in description or "advice" in description:
            return self._provide_interview_tips(params)
        else:
            return self._comprehensive_interview_prep(params)
    
    def _generate_interview_questions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate tailored interview questions."""
        job_role = params.get("job_role", "Software Engineer")
        interview_type = params.get("interview_type", "technical")
        difficulty = params.get("difficulty", "medium")
        
        prompt = f"""You are an expert interview coach. Generate {difficulty} difficulty {interview_type} interview questions for a {job_role} position.

Provide:
1. 5 core questions with:
   - The question
   - What the interviewer is looking for
   - Key points for a strong answer
   - Common pitfalls to avoid

2. 2 behavioral questions (STAR method applicable)

3. 2 situational questions

Make questions realistic and role-appropriate."""

        response = self.llm.invoke(prompt)
        
        return {
            "success": True,
            "role": job_role,
            "interview_type": interview_type,
            "difficulty": difficulty,
            "questions_and_guidance": response.content,
            "message": f"Generated {interview_type} interview prep for {job_role}"
        }
    
    def _provide_interview_feedback(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Provide feedback on interview performance."""
        candidate_name = params.get("candidate_name", "Candidate")
        interview_notes = params.get("interview_notes", "")
        strengths = params.get("strengths", [])
        weaknesses = params.get("weaknesses", [])
        
        prompt = f"""You are an interview coach providing constructive feedback.

Candidate: {candidate_name}
Interview Notes: {interview_notes if interview_notes else "General feedback requested"}
Observed Strengths: {', '.join(strengths) if strengths else "To be determined"}
Areas for Improvement: {', '.join(weaknesses) if weaknesses else "To be determined"}

Provide:
1. Overall Performance Assessment (1-10 scale with explanation)
2. Key Strengths (be specific)
3. Areas for Improvement (constructive)
4. Actionable Recommendations (3-5 specific steps)
5. Resources for improvement

Be encouraging but honest."""

        response = self.llm.invoke(prompt)
        
        return {
            "success": True,
            "candidate": candidate_name,
            "feedback": response.content,
            "message": f"Interview feedback provided for {candidate_name}"
        }
    
    def _provide_interview_tips(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Provide interview tips and best practices."""
        job_role = params.get("job_role", "any position")
        interview_stage = params.get("interview_stage", "general")
        
        prompt = f"""Provide expert interview tips for a {job_role} candidate at the {interview_stage} stage.

Cover:
1. Preparation strategies
2. Communication best practices
3. Body language and presence
4. How to handle difficult questions
5. Questions to ask the interviewer
6. Post-interview follow-up

Be practical and actionable."""

        response = self.llm.invoke(prompt)
        
        return {
            "success": True,
            "role": job_role,
            "stage": interview_stage,
            "tips": response.content,
            "message": "Interview tips and best practices provided"
        }
    
    def _comprehensive_interview_prep(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Provide comprehensive interview preparation package."""
        job_role = params.get("job_role", "Software Engineer")
        company_name = params.get("company_name", "the company")
        
        prompt = f"""Create a comprehensive interview preparation guide for a {job_role} position at {company_name}.

Include:
1. Company Research Checklist
2. Role-Specific Preparation Areas
3. Top 10 Likely Questions
4. Your Questions to Ask
5. Day-of Interview Checklist
6. First Impression Tips
7. Follow-up Strategy

Make it actionable and confidence-building."""

        response = self.llm.invoke(prompt)
        
        return {
            "success": True,
            "role": job_role,
            "company": company_name,
            "prep_guide": response.content,
            "message": f"Comprehensive interview prep guide created for {job_role} at {company_name}"
        }
    
    def get_capabilities(self) -> List[str]:
        """Return module capabilities."""
        return [
            "Generate interview questions",
            "Provide interview feedback",
            "Mock interview practice",
            "Interview tips and strategies",
            "Behavioral question coaching",
            "Technical interview prep",
            "Post-interview analysis"
        ]
