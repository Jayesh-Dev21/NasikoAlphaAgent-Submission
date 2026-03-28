"""
Database utilities for storing candidate information.
Supports both MongoDB (production) and file-based (development).
"""
import os
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Global database instance (singleton pattern)
_db_instance = None


def get_database():
    """
    Get database instance (singleton pattern for efficiency).
    
    Priority:
    1. MongoDB (if MONGODB_URI is set or MongoDB is available)
    2. File-based (fallback for development)
    """
    global _db_instance
    
    # Return existing instance if available
    if _db_instance is not None:
        return _db_instance
    
    # Try MongoDB first
    mongodb_uri = os.getenv("MONGODB_URI")
    use_mongodb = os.getenv("USE_MONGODB", "true").lower() == "true"
    
    if use_mongodb and mongodb_uri:
        try:
            from utils.mongodb_database import get_database as get_mongo_db
            db = get_mongo_db()
            if db.is_connected():
                _db_instance = db
                logger.info("✅ Using MongoDB database")
                return _db_instance
        except ImportError:
            logger.warning("⚠️ MongoDB libraries not installed. Run: pip install pymongo")
        except Exception as e:
            logger.warning(f"⚠️ MongoDB connection failed: {e}")
    
    # Fallback to file-based database
    logger.info("ℹ️ Using file-based database (development mode)")
    _db_instance = CandidateDatabase()
    return _db_instance


class CandidateDatabase:
    """Simple file-based database for candidate information.
    In production, use MongoDB (see mongodb_database.py)."""
    
    def __init__(self, db_path: str = "/tmp/candidates_db.json"):
        self.db_path = db_path
        self._ensure_db_exists()
    
    def is_connected(self) -> bool:
        """Check if database is available."""
        return os.path.exists(self.db_path)
    
    def _ensure_db_exists(self):
        """Create database file if it doesn't exist."""
        if not os.path.exists(self.db_path):
            with open(self.db_path, 'w') as f:
                json.dump({"candidates": {}}, f)
    
    def _load_db(self) -> Dict:
        """Load database from file."""
        try:
            with open(self.db_path, 'r') as f:
                return json.load(f)
        except:
            return {"candidates": {}}
    
    def _save_db(self, data: Dict):
        """Save database to file."""
        with open(self.db_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_candidate(self, candidate_data: Dict[str, Any]) -> str:
        """Add a new candidate to the database."""
        db = self._load_db()
        
        candidate_id = candidate_data.get('email', f"candidate_{len(db['candidates']) + 1}")
        
        # Structure candidate data
        candidate = {
            "id": candidate_id,
            "name": candidate_data.get("name", ""),
            "email": candidate_data.get("email", ""),
            "phone": candidate_data.get("phone", ""),
            "college": candidate_data.get("college", ""),
            "degree": candidate_data.get("degree", ""),
            "cpi": candidate_data.get("cpi", 0.0),
            "graduation_year": candidate_data.get("graduation_year", ""),
            "skills": candidate_data.get("skills", []),
            "experience_years": candidate_data.get("experience_years", 0),
            "resume_url": candidate_data.get("resume_url", ""),
            "linkedin_url": candidate_data.get("linkedin_url", ""),
            "github_url": candidate_data.get("github_url", ""),
            "applied_position": candidate_data.get("applied_position", ""),
            "status": candidate_data.get("status", "applied"),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "notes": candidate_data.get("notes", ""),
            "screening_score": candidate_data.get("screening_score", None),
            "culture_fit_score": candidate_data.get("culture_fit_score", None),
            "interviews": []
        }
        
        db["candidates"][candidate_id] = candidate
        self._save_db(db)
        
        return candidate_id
    
    def get_candidate(self, candidate_id: str) -> Optional[Dict[str, Any]]:
        """Get candidate by ID or email."""
        db = self._load_db()
        return db["candidates"].get(candidate_id)
    
    def search_candidates(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search candidates by criteria."""
        db = self._load_db()
        results = []
        
        for candidate in db["candidates"].values():
            match = True
            for key, value in query.items():
                if key in candidate and candidate[key] != value:
                    match = False
                    break
            if match:
                results.append(candidate)
        
        return results
    
    def update_candidate(self, candidate_id: str, updates: Dict[str, Any]) -> bool:
        """Update candidate information."""
        db = self._load_db()
        
        if candidate_id not in db["candidates"]:
            return False
        
        db["candidates"][candidate_id].update(updates)
        db["candidates"][candidate_id]["updated_at"] = datetime.now().isoformat()
        
        self._save_db(db)
        return True
    
    def add_interview(self, candidate_id: str, interview_data: Dict[str, Any]) -> bool:
        """Add interview record to candidate."""
        db = self._load_db()
        
        if candidate_id not in db["candidates"]:
            return False
        
        interview = {
            "id": f"interview_{len(db['candidates'][candidate_id]['interviews']) + 1}",
            "type": interview_data.get("type", "technical"),
            "scheduled_at": interview_data.get("scheduled_at", ""),
            "duration": interview_data.get("duration", 60),
            "meeting_link": interview_data.get("meeting_link", ""),
            "status": interview_data.get("status", "scheduled"),
            "interviewer": interview_data.get("interviewer", ""),
            "notes": interview_data.get("notes", ""),
            "created_at": datetime.now().isoformat()
        }
        
        db["candidates"][candidate_id]["interviews"].append(interview)
        self._save_db(db)
        
        return True
    
    def get_all_candidates(self) -> List[Dict[str, Any]]:
        """Get all candidates."""
        db = self._load_db()
        return list(db["candidates"].values())


# Global database instance
_db = None

def get_database_instance():
    """Get or create database instance (legacy function - use get_database() instead)."""
    return get_database()
