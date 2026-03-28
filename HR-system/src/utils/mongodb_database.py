"""
MongoDB database implementation for HR Agent.
Stores candidates, interviews, and recruitment data.
"""
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, DuplicateKeyError
import logging

logger = logging.getLogger(__name__)


class MongoDBDatabase:
    """
    MongoDB database for candidate and recruitment management.
    
    Setup:
    1. Install MongoDB: https://www.mongodb.com/docs/manual/installation/
    2. Start MongoDB: mongod --dbpath /path/to/data
    3. Set environment variables:
       - MONGODB_URI (default: mongodb://localhost:27017/)
       - MONGODB_DATABASE (default: hr_agent)
    
    Or use MongoDB Atlas (cloud):
    - MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
    """
    
    def __init__(
        self,
        uri: Optional[str] = None,
        database_name: Optional[str] = None
    ):
        self.uri = uri or os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
        self.database_name = database_name or os.getenv("MONGODB_DATABASE", "hr_agent")
        
        self.client = None
        self.db = None
        self.candidates = None
        self.interviews = None
        self.jobs = None
        
        self._connect()
    
    def _connect(self):
        """Connect to MongoDB and initialize collections."""
        try:
            self.client = MongoClient(
                self.uri,
                serverSelectionTimeoutMS=30000,  # 30 seconds
                connectTimeoutMS=30000,
                socketTimeoutMS=30000,
                retryWrites=True,
                w='majority'
            )
            
            # Test connection
            self.client.admin.command('ping')
            
            self.db = self.client[self.database_name]
            
            # Initialize collections
            self.candidates = self.db.candidates
            self.interviews = self.db.interviews
            self.jobs = self.db.jobs
            
            # Create indexes
            self._create_indexes()
            
            logger.info(f"✅ Connected to MongoDB: {self.database_name}")
            
        except ConnectionFailure as e:
            logger.warning(f"⚠️ MongoDB connection failed: {e}")
            logger.warning("Falling back to mock database mode")
            self.client = None
    
    def _create_indexes(self):
        """Create database indexes for better performance."""
        if not self.is_connected():
            return
        
        try:
            # Candidates indexes
            self.candidates.create_index("email", unique=True)
            self.candidates.create_index("status")
            self.candidates.create_index("screening_score")
            self.candidates.create_index("culture_fit_score")
            self.candidates.create_index([("name", ASCENDING)])
            self.candidates.create_index([("created_at", DESCENDING)])
            
            # Interviews indexes
            self.interviews.create_index("candidate_email")
            self.interviews.create_index("scheduled_at")
            self.interviews.create_index("status")
            
            # Jobs indexes
            self.jobs.create_index("title")
            self.jobs.create_index("status")
            
            logger.info("✅ Database indexes created")
            
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")
    
    def is_connected(self) -> bool:
        """Check if connected to MongoDB."""
        return self.client is not None
    
    # ==================== CANDIDATE OPERATIONS ====================
    
    def add_candidate(self, candidate_data: Dict[str, Any]) -> Optional[str]:
        """
        Add a new candidate to the database.
        
        Args:
            candidate_data: Dictionary with candidate information
        
        Returns:
            Candidate email (ID) if successful, None otherwise
        """
        if not self.is_connected():
            logger.warning("MongoDB not connected - candidate not saved")
            return None
        
        try:
            # Prepare candidate document
            candidate = {
                "email": candidate_data.get("email", ""),
                "name": candidate_data.get("name", ""),
                "phone": candidate_data.get("phone", ""),
                
                # Education
                "college": candidate_data.get("college", ""),
                "degree": candidate_data.get("degree", ""),
                "cpi": candidate_data.get("cpi", 0.0),
                "graduation_year": candidate_data.get("graduation_year", ""),
                
                # Professional
                "skills": candidate_data.get("skills", []),
                "experience_years": candidate_data.get("experience_years", 0),
                "current_company": candidate_data.get("current_company", ""),
                "current_position": candidate_data.get("current_position", ""),
                
                # Links
                "resume_url": candidate_data.get("resume_url", ""),
                "linkedin_url": candidate_data.get("linkedin_url", ""),
                "github_url": candidate_data.get("github_url", ""),
                "portfolio_url": candidate_data.get("portfolio_url", ""),
                
                # Application
                "applied_position": candidate_data.get("applied_position", ""),
                "status": candidate_data.get("status", "applied"),
                "source": candidate_data.get("source", "direct"),
                
                # Scores
                "screening_score": candidate_data.get("screening_score"),
                "culture_fit_score": candidate_data.get("culture_fit_score"),
                "technical_score": candidate_data.get("technical_score"),
                
                # Metadata
                "notes": candidate_data.get("notes", ""),
                "tags": candidate_data.get("tags", []),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                
                # Interview history (references)
                "interview_ids": []
            }
            
            # Validate required fields
            if not candidate["email"]:
                logger.error("Email is required for candidate")
                return None
            
            # Insert candidate
            result = self.candidates.insert_one(candidate)
            
            logger.info(f"✅ Candidate added: {candidate['email']}")
            return candidate["email"]
            
        except DuplicateKeyError:
            logger.warning(f"Candidate already exists: {candidate_data.get('email')}")
            return candidate_data.get("email")
        except Exception as e:
            logger.error(f"Failed to add candidate: {e}")
            return None
    
    def get_candidate(self, identifier: str) -> Optional[Dict[str, Any]]:
        """
        Get candidate by email OR name.

        Args:
            identifier: Candidate email or name

        Returns:
            Candidate document or None
        """
        if not self.is_connected():
            return None

        try:
            candidate = self.candidates.find_one({
                "$or": [
                    {"email": identifier},
                    {"name": {"$regex": f"^{identifier}$", "$options": "i"}}
                ]
            })

            if candidate:
                candidate["_id"] = str(candidate["_id"])

            return candidate

        except Exception as e:
            logger.error(f"Failed to get candidate: {e}")
            return None
    
    def update_candidate(self, identifier: str, updates: Dict[str, Any]) -> bool:
        """
        Update candidate by name or email.
        """

        if not self.is_connected():
            return False

        try:
            updates["updated_at"] = datetime.utcnow()

            result = self.candidates.update_one(
                {
                    "$or": [
                        {"email": identifier},
                        {"name": {"$regex": f"^{identifier}$", "$options": "i"}}
                    ]
                },
                {"$set": updates}
            )

            return result.modified_count > 0

        except Exception as e:
            logger.error(f"Failed to update candidate: {e}")
            return False
    
    def search_candidates(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search candidates by criteria.
        
        Args:
            query: MongoDB query dictionary
        
        Returns:
            List of matching candidates
        """
        if not self.is_connected():
            return []
        
        try:
            candidates = list(self.candidates.find(query))
            
            # Convert ObjectIds to strings
            for candidate in candidates:
                candidate["_id"] = str(candidate["_id"])
            
            return candidates
        except Exception as e:
            logger.error(f"Failed to search candidates: {e}")
            return []
    
    def get_all_candidates(
        self,
        limit: int = 100,
        skip: int = 0,
        sort_by: str = "created_at",
        sort_order: int = DESCENDING
    ) -> List[Dict[str, Any]]:
        """
        Get all candidates with pagination.
        
        Args:
            limit: Maximum number of candidates to return
            skip: Number of candidates to skip
            sort_by: Field to sort by
            sort_order: ASCENDING or DESCENDING
        
        Returns:
            List of candidates
        """
        if not self.is_connected():
            return []
        
        try:
            candidates = list(
                self.candidates.find()
                .sort(sort_by, sort_order)
                .skip(skip)
                .limit(limit)
            )
            
            # Convert ObjectIds to strings
            for candidate in candidates:
                candidate["_id"] = str(candidate["_id"])
            
            return candidates
        except Exception as e:
            logger.error(f"Failed to get candidates: {e}")
            return []
    
    def delete_candidate(self, identifier: str) -> bool:
        """Delete candidate by name or email."""

        if not self.is_connected():
            return False

        try:
            result = self.candidates.delete_one({
                "$or": [
                    {"email": identifier},
                    {"name": {"$regex": f"^{identifier}$", "$options": "i"}}
                ]
            })

            return result.deleted_count > 0

        except Exception as e:
            logger.error(f"Failed to delete candidate: {e}")
            return False
    
    # ==================== INTERVIEW OPERATIONS ====================
    
    def add_interview(
        self,
        candidate_email: str,
        interview_data: Dict[str, Any]
    ) -> Optional[str]:
        """
        Add an interview record.
        
        Args:
            candidate_email: Candidate's email
            interview_data: Interview details
        
        Returns:
            Interview ID if successful, None otherwise
        """
        if not self.is_connected():
            return None
        
        try:
            interview = {
                "candidate_email": candidate_email,
                "type": interview_data.get("type", "technical"),
                "scheduled_at": interview_data.get("scheduled_at"),
                "duration": interview_data.get("duration", 60),
                "meeting_link": interview_data.get("meeting_link", ""),
                "calendar_event_id": interview_data.get("calendar_event_id", ""),
                "status": interview_data.get("status", "scheduled"),
                "interviewer": interview_data.get("interviewer", ""),
                "interviewer_email": interview_data.get("interviewer_email", ""),
                "notes": interview_data.get("notes", ""),
                "feedback": interview_data.get("feedback", ""),
                "score": interview_data.get("score"),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            result = self.interviews.insert_one(interview)
            interview_id = str(result.inserted_id)
            
            # Add interview reference to candidate
            self.candidates.update_one(
                {"email": candidate_email},
                {"$push": {"interview_ids": interview_id}}
            )
            
            logger.info(f"✅ Interview added for {candidate_email}")
            return interview_id
            
        except Exception as e:
            logger.error(f"Failed to add interview: {e}")
            return None
    
    def get_interviews(
        self,
        candidate_email: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get interviews, optionally filtered by candidate or status.
        
        Args:
            candidate_email: Filter by candidate email
            status: Filter by status (scheduled, completed, cancelled)
        
        Returns:
            List of interviews
        """
        if not self.is_connected():
            return []
        
        try:
            query = {}
            if candidate_email:
                query["candidate_email"] = candidate_email
            if status:
                query["status"] = status
            
            interviews = list(self.interviews.find(query).sort("scheduled_at", DESCENDING))
            
            # Convert ObjectIds to strings
            for interview in interviews:
                interview["_id"] = str(interview["_id"])
            
            return interviews
        except Exception as e:
            logger.error(f"Failed to get interviews: {e}")
            return []
    
    def update_interview(self, interview_id: str, updates: Dict[str, Any]) -> bool:
        """Update interview information."""
        if not self.is_connected():
            return False
        
        try:
            from bson.objectid import ObjectId
            
            updates["updated_at"] = datetime.utcnow()
            
            result = self.interviews.update_one(
                {"_id": ObjectId(interview_id)},
                {"$set": updates}
            )
            
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to update interview: {e}")
            return False
    
    # ==================== JOB OPERATIONS ====================
    
    def add_job(self, job_data: Dict[str, Any]) -> Optional[str]:
        """
        Add a job posting.
        
        Args:
            job_data: Job details
        
        Returns:
            Job ID if successful, None otherwise
        """
        if not self.is_connected():
            return None
        
        try:
            job = {
                "title": job_data.get("title", ""),
                "department": job_data.get("department", ""),
                "location": job_data.get("location", ""),
                "type": job_data.get("type", "full-time"),
                "experience_level": job_data.get("experience_level", "mid-level"),
                "salary_min": job_data.get("salary_min", 0),
                "salary_max": job_data.get("salary_max", 0),
                "description": job_data.get("description", ""),
                "requirements": job_data.get("requirements", []),
                "skills": job_data.get("skills", []),
                "status": job_data.get("status", "open"),
                "posted_at": datetime.utcnow(),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            result = self.jobs.insert_one(job)
            
            logger.info(f"✅ Job added: {job['title']}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Failed to add job: {e}")
            return None
    
    def get_jobs(self, status: str = "open") -> List[Dict[str, Any]]:
        """Get job postings by status."""
        if not self.is_connected():
            return []
        
        try:
            jobs = list(self.jobs.find({"status": status}).sort("posted_at", DESCENDING))
            
            for job in jobs:
                job["_id"] = str(job["_id"])
            
            return jobs
        except Exception as e:
            logger.error(f"Failed to get jobs: {e}")
            return []
    
    # ==================== ANALYTICS ====================
    
    def get_pipeline_stats(self) -> Dict[str, Any]:
        """Get recruitment pipeline statistics."""
        if not self.is_connected():
            return {}
        
        try:
            pipeline = [
                {
                    "$group": {
                        "_id": "$status",
                        "count": {"$sum": 1}
                    }
                }
            ]
            
            results = list(self.candidates.aggregate(pipeline))
            
            stats = {result["_id"]: result["count"] for result in results}
            stats["total"] = sum(stats.values())
            
            return stats
        except Exception as e:
            logger.error(f"Failed to get pipeline stats: {e}")
            return {}
    
    def get_average_scores(self) -> Dict[str, float]:
        """Get average screening and culture fit scores."""
        if not self.is_connected():
            return {}
        
        try:
            pipeline = [
                {
                    "$group": {
                        "_id": None,
                        "avg_screening": {"$avg": "$screening_score"},
                        "avg_culture_fit": {"$avg": "$culture_fit_score"},
                        "avg_technical": {"$avg": "$technical_score"}
                    }
                }
            ]
            
            results = list(self.candidates.aggregate(pipeline))
            
            if results:
                return {
                    "average_screening_score": round(results[0].get("avg_screening", 0), 2),
                    "average_culture_fit_score": round(results[0].get("avg_culture_fit", 0), 2),
                    "average_technical_score": round(results[0].get("avg_technical", 0), 2)
                }
            
            return {}
        except Exception as e:
            logger.error(f"Failed to get average scores: {e}")
            return {}
    
    # ==================== UTILITY ====================
    
    def close(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")


# Global database instance
_db = None

def get_database() -> MongoDBDatabase:
    """Get or create MongoDB database instance."""
    global _db
    if _db is None:
        _db = MongoDBDatabase()
    return _db
