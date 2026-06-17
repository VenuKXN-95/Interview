"""
Seed script: Populates the question_bank collection with 300+ questions.
Run once:
    python scripts/seed_questions.py

Idempotent: checks if questions already exist before inserting.
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv

load_dotenv()

from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings

# ──────────────────────────────────────────────────────────────────────────────
# QUESTION DATA
# Each entry: (category, difficulty, question, tags)
# ──────────────────────────────────────────────────────────────────────────────

HR_QUESTIONS = [
    # Behavioral
    ("Behavioral", "easy", "Tell me about yourself and your professional background.", ["self-introduction", "background"]),
    ("Behavioral", "easy", "Why are you looking for a new opportunity?", ["motivation", "career-change"]),
    ("Behavioral", "easy", "What are your greatest strengths?", ["self-awareness", "strengths"]),
    ("Behavioral", "easy", "What is your biggest weakness and how are you working on it?", ["self-awareness", "growth"]),
    ("Behavioral", "medium", "Describe a situation where you had to meet a tight deadline. How did you handle it?", ["time-management", "pressure"]),
    ("Behavioral", "medium", "Tell me about a time you made a mistake. What did you learn?", ["accountability", "learning"]),
    ("Behavioral", "medium", "Describe a time you disagreed with your manager. How did you resolve it?", ["conflict-resolution", "communication"]),
    ("Behavioral", "medium", "Tell me about a time you went above and beyond your job responsibilities.", ["initiative", "dedication"]),
    ("Behavioral", "hard", "Describe a situation where you had to lead a team through a difficult project. What was the outcome?", ["leadership", "team"]),
    ("Behavioral", "hard", "Tell me about a time when you had to make a critical decision with incomplete information.", ["decision-making", "risk"]),
    ("Behavioral", "medium", "How do you handle competing priorities when multiple tasks are urgent?", ["prioritization", "multitasking"]),
    ("Behavioral", "easy", "Where do you see yourself in 5 years?", ["career-goals", "ambition"]),
    ("Behavioral", "medium", "Describe a time you received critical feedback. How did you respond?", ["feedback", "growth"]),
    ("Behavioral", "medium", "Tell me about a project you are most proud of.", ["achievement", "pride"]),
    ("Behavioral", "hard", "Describe a time you had to influence someone without direct authority.", ["influence", "persuasion"]),
    # Communication
    ("Communication", "easy", "How would you explain a complex technical concept to a non-technical stakeholder?", ["communication", "simplification"]),
    ("Communication", "medium", "Describe a time your communication skills helped resolve a difficult situation.", ["communication", "conflict"]),
    ("Communication", "medium", "How do you ensure your team is aligned on project goals and progress?", ["communication", "alignment"]),
    ("Communication", "easy", "How do you approach giving constructive feedback to a colleague?", ["feedback", "communication"]),
    ("Communication", "hard", "Tell me about a time you had to present to senior leadership. How did you prepare?", ["presentation", "leadership"]),
    ("Communication", "medium", "How do you handle misunderstandings in written communication (email, Slack)?", ["written-communication", "clarity"]),
    ("Communication", "easy", "How do you stay informed and communicate updates when working remotely?", ["remote-work", "communication"]),
    ("Communication", "medium", "Describe a time you had to deliver bad news to a client or stakeholder.", ["communication", "difficult-conversations"]),
    # Teamwork
    ("Teamwork", "easy", "Describe your ideal team environment.", ["teamwork", "culture"]),
    ("Teamwork", "medium", "How do you handle a team member who is not contributing equally?", ["teamwork", "conflict"]),
    ("Teamwork", "medium", "Tell me about a successful cross-functional project you participated in.", ["collaboration", "cross-functional"]),
    ("Teamwork", "hard", "How do you build trust within a newly formed team?", ["trust", "leadership"]),
    ("Teamwork", "medium", "Describe a time you helped a struggling colleague.", ["mentoring", "support"]),
    ("Teamwork", "easy", "How do you contribute to a positive team culture?", ["culture", "teamwork"]),
    ("Teamwork", "hard", "Tell me about a time you had to work with a difficult team member. What was your approach?", ["conflict", "teamwork"]),
    ("Teamwork", "medium", "How do you ensure everyone's voice is heard in team meetings?", ["inclusion", "teamwork"]),
    # Career Growth
    ("Career Growth", "easy", "Why are you interested in this role specifically?", ["motivation", "career"]),
    ("Career Growth", "easy", "What motivated you to pursue a career in this field?", ["motivation", "career"]),
    ("Career Growth", "medium", "How do you stay current with industry trends and new technologies?", ["learning", "growth"]),
    ("Career Growth", "medium", "What professional development activities have you undertaken in the last year?", ["learning", "growth"]),
    ("Career Growth", "hard", "How do you measure your own professional success?", ["self-assessment", "career"]),
    ("Career Growth", "medium", "Describe a skill you actively worked to improve. What was the outcome?", ["improvement", "skill-development"]),
    ("Career Growth", "easy", "What type of work environment helps you perform best?", ["work-environment", "productivity"]),
    ("Career Growth", "medium", "How do you balance professional growth with day-to-day responsibilities?", ["time-management", "growth"]),
    # Additional HR
    ("Work Ethics", "easy", "How do you manage your workload when under pressure?", ["stress-management", "workload"]),
    ("Work Ethics", "medium", "Describe a time you had to work with minimal supervision.", ["autonomy", "self-management"]),
    ("Work Ethics", "medium", "How do you handle situations where you disagree with company policy?", ["professionalism", "adaptability"]),
    ("Work Ethics", "easy", "How do you ensure quality in your work?", ["quality", "attention-to-detail"]),
    ("Work Ethics", "hard", "Tell me about a time you had to juggle multiple high-priority projects simultaneously.", ["multitasking", "prioritization"]),
    ("Adaptability", "medium", "Tell me about a time you had to adapt quickly to a major change.", ["adaptability", "change-management"]),
    ("Adaptability", "medium", "How do you approach learning a completely new technology or process?", ["learning", "adaptability"]),
    ("Adaptability", "easy", "How have you adapted to remote or hybrid work?", ["remote-work", "adaptability"]),
    ("Problem Solving", "medium", "Describe a situation where you identified a problem before it became critical.", ["proactive", "problem-solving"]),
    ("Problem Solving", "hard", "Tell me about the most complex problem you have solved professionally.", ["problem-solving", "complexity"]),
    ("Problem Solving", "medium", "How do you approach a problem you have never encountered before?", ["problem-solving", "creativity"]),
    # More HR to hit 100
    ("Behavioral", "easy", "Describe your typical workday and how you stay organized.", ["organization", "productivity"]),
    ("Behavioral", "medium", "How do you maintain work-life balance?", ["balance", "wellbeing"]),
    ("Behavioral", "easy", "What do you find most rewarding about your current role?", ["motivation", "satisfaction"]),
    ("Teamwork", "easy", "How do you celebrate team successes?", ["teamwork", "recognition"]),
    ("Teamwork", "medium", "How do you handle a situation where a team decision conflicts with your opinion?", ["teamwork", "consensus"]),
    ("Communication", "hard", "How do you tailor your communication style to different audiences?", ["communication", "adaptability"]),
    ("Career Growth", "hard", "What is your long-term career vision and how does this role fit into it?", ["career-vision", "ambition"]),
    ("Adaptability", "hard", "Tell me about a time you had to completely change your approach mid-project.", ["adaptability", "flexibility"]),
    ("Work Ethics", "hard", "Describe a time you had to make a decision that was right but unpopular.", ["integrity", "courage"]),
    ("Behavioral", "medium", "How do you approach setting goals for yourself?", ["goal-setting", "planning"]),
    ("Behavioral", "medium", "Describe a time you had to build a relationship with a difficult stakeholder.", ["relationship-building", "stakeholder-management"]),
    ("Behavioral", "easy", "What are you passionate about outside of work?", ["personal", "interests"]),
    ("Communication", "medium", "How do you handle information overload?", ["communication", "information-management"]),
    ("Teamwork", "hard", "How do you manage knowledge sharing within your team?", ["knowledge-sharing", "teamwork"]),
    ("Career Growth", "easy", "What kind of mentor or manager do you work best with?", ["mentorship", "management-style"]),
    ("Work Ethics", "medium", "How do you ensure you meet deadlines consistently?", ["time-management", "reliability"]),
    ("Behavioral", "hard", "Tell me about a time you initiated change that had a significant positive impact.", ["change-management", "initiative"]),
    ("Behavioral", "medium", "How do you recover from a professional setback?", ["resilience", "growth"]),
    ("Problem Solving", "easy", "Walk me through how you approach solving a day-to-day work problem.", ["problem-solving", "process"]),
    ("Adaptability", "easy", "How comfortable are you with changing priorities in a fast-paced environment?", ["adaptability", "flexibility"]),
    ("Communication", "easy", "How do you ensure clarity when delegating tasks?", ["delegation", "communication"]),
    ("Teamwork", "medium", "Tell me about a time you successfully onboarded a new team member.", ["onboarding", "mentoring"]),
    ("Career Growth", "medium", "What skills are you currently developing and why?", ["skill-development", "learning"]),
    ("Behavioral", "medium", "Describe the most challenging project you have worked on.", ["challenge", "resilience"]),
    ("Behavioral", "easy", "How do you handle repetitive or monotonous tasks?", ["persistence", "attitude"]),
    ("Work Ethics", "easy", "How do you handle constructive criticism?", ["feedback", "growth"]),
    ("Communication", "medium", "How do you build rapport with a new team quickly?", ["rapport", "communication"]),
    ("Problem Solving", "medium", "Describe a time you solved a problem with limited resources.", ["resourcefulness", "problem-solving"]),
    ("Adaptability", "medium", "How have you handled working across different time zones?", ["remote-work", "flexibility"]),
    ("Behavioral", "hard", "Tell me about a risk you took professionally. What was the outcome?", ["risk-taking", "decision-making"]),
    ("Career Growth", "hard", "How do you identify and pursue stretch opportunities?", ["ambition", "growth"]),
    ("Teamwork", "easy", "What role do you naturally gravitate toward in a team?", ["teamwork", "self-awareness"]),
    ("Behavioral", "medium", "How do you deal with ambiguity in your role?", ["ambiguity", "adaptability"]),
    ("Work Ethics", "medium", "How do you ensure you remain productive during slow periods?", ["productivity", "initiative"]),
    ("Behavioral", "easy", "Describe a time you helped a client or customer solve a problem.", ["customer-focus", "problem-solving"]),
    ("Communication", "hard", "Tell me about a time you had to mediate a conflict between two colleagues.", ["mediation", "conflict-resolution"]),
    ("Career Growth", "medium", "How do you evaluate whether a role is the right fit for you?", ["decision-making", "self-awareness"]),
    ("Behavioral", "medium", "Describe a time you exceeded expectations in your role.", ["performance", "achievement"]),
    ("Problem Solving", "hard", "How do you approach a situation where the root cause of a problem is unclear?", ["root-cause-analysis", "problem-solving"]),
    ("Teamwork", "hard", "How do you lead by example to set team culture?", ["leadership", "culture"]),
    ("Adaptability", "hard", "Describe a time you had to learn something complex under significant time pressure.", ["learning-under-pressure", "adaptability"]),
    ("Behavioral", "easy", "What does success look like to you in the first 90 days of a new role?", ["onboarding", "planning"]),
    ("Communication", "medium", "How do you handle a situation where a stakeholder keeps changing requirements?", ["stakeholder-management", "communication"]),
    ("Work Ethics", "hard", "Describe a time you maintained high standards under significant organizational pressure.", ["integrity", "standards"]),
    ("Behavioral", "medium", "How do you ensure continuous improvement in your work?", ["continuous-improvement", "growth"]),
    ("Career Growth", "easy", "What excites you most about this industry right now?", ["industry-awareness", "enthusiasm"]),
    ("Teamwork", "medium", "How do you handle disagreements about technical approaches with peers?", ["conflict", "technical"]),
]

TECHNICAL_QUESTIONS = [
    # Python / General Programming
    ("Programming", "easy", "What are the differences between lists, tuples, and sets in Python?", ["python", "data-structures"]),
    ("Programming", "easy", "Explain the concept of decorators in Python with an example.", ["python", "decorators"]),
    ("Programming", "medium", "How does Python's GIL (Global Interpreter Lock) affect multi-threading?", ["python", "concurrency"]),
    ("Programming", "medium", "Explain generators and how they differ from regular functions.", ["python", "generators"]),
    ("Programming", "hard", "How would you implement a thread-safe singleton in Python?", ["python", "design-patterns", "concurrency"]),
    ("Programming", "medium", "What is the difference between asyncio, threading, and multiprocessing in Python?", ["python", "concurrency"]),
    ("Programming", "easy", "What are Python context managers and how do you create a custom one?", ["python", "context-managers"]),
    ("Programming", "medium", "Explain Python's memory management and garbage collection.", ["python", "memory"]),
    ("Programming", "hard", "How do metaclasses work in Python?", ["python", "advanced", "metaclasses"]),
    ("Programming", "easy", "What is the difference between `is` and `==` in Python?", ["python", "fundamentals"]),
    # Data Structures & Algorithms
    ("Data Structures", "easy", "Explain the difference between a stack and a queue.", ["data-structures", "algorithms"]),
    ("Data Structures", "medium", "How does a hash table work? What is a hash collision and how do you resolve it?", ["data-structures", "hashing"]),
    ("Data Structures", "medium", "Explain the difference between BFS and DFS. When would you use each?", ["algorithms", "graphs"]),
    ("Data Structures", "hard", "How would you detect a cycle in a directed graph?", ["graphs", "algorithms"]),
    ("Data Structures", "medium", "What is the time complexity of common operations on a balanced BST?", ["data-structures", "complexity"]),
    ("Data Structures", "hard", "How would you implement an LRU cache from scratch?", ["data-structures", "cache"]),
    ("Data Structures", "medium", "Explain dynamic programming and give an example problem.", ["algorithms", "dp"]),
    ("Data Structures", "easy", "What is Big O notation? How do you analyze time and space complexity?", ["algorithms", "complexity"]),
    # System Design
    ("System Design", "medium", "How would you design a URL shortener service?", ["system-design", "scalability"]),
    ("System Design", "hard", "How would you design a distributed message queue like Kafka?", ["system-design", "distributed-systems"]),
    ("System Design", "medium", "Explain the CAP theorem and its implications for distributed systems.", ["system-design", "distributed-systems"]),
    ("System Design", "hard", "How would you design a rate limiter for an API?", ["system-design", "api"]),
    ("System Design", "medium", "What is the difference between horizontal and vertical scaling?", ["system-design", "scalability"]),
    ("System Design", "hard", "How would you design a real-time notification system for millions of users?", ["system-design", "scalability"]),
    ("System Design", "medium", "Explain microservices architecture. What are its advantages and disadvantages?", ["system-design", "architecture"]),
    ("System Design", "hard", "How would you design a global CDN?", ["system-design", "cdn"]),
    ("System Design", "medium", "What is eventual consistency and when is it acceptable?", ["system-design", "consistency"]),
    ("System Design", "medium", "How would you handle database migrations without downtime?", ["database", "devops"]),
    # Databases
    ("Database", "easy", "What is the difference between SQL and NoSQL databases?", ["database", "sql", "nosql"]),
    ("Database", "medium", "Explain database indexing. When should you add an index?", ["database", "indexing"]),
    ("Database", "medium", "What is database normalization? Explain 1NF, 2NF, and 3NF.", ["database", "normalization"]),
    ("Database", "hard", "How do you optimize a slow SQL query?", ["database", "performance", "sql"]),
    ("Database", "medium", "What are ACID properties? Give a real-world example.", ["database", "transactions"]),
    ("Database", "hard", "How does MongoDB handle horizontal scaling with sharding?", ["mongodb", "nosql", "scaling"]),
    ("Database", "medium", "What is the N+1 query problem and how do you solve it?", ["database", "orm", "performance"]),
    ("Database", "easy", "What is a database transaction and why is it important?", ["database", "transactions"]),
    # APIs
    ("API Design", "easy", "What is the difference between REST and GraphQL?", ["api", "rest", "graphql"]),
    ("API Design", "medium", "How would you version a REST API?", ["api", "versioning"]),
    ("API Design", "medium", "What HTTP status codes would you use for different error scenarios?", ["api", "http"]),
    ("API Design", "hard", "How do you design idempotent API endpoints?", ["api", "idempotency"]),
    ("API Design", "medium", "What is the difference between authentication and authorization?", ["api", "security"]),
    ("API Design", "easy", "Explain the concept of pagination in APIs. What are cursor-based vs offset-based?", ["api", "pagination"]),
    ("API Design", "medium", "How would you implement API rate limiting?", ["api", "rate-limiting"]),
    ("API Design", "hard", "How do you handle backward compatibility when changing an API?", ["api", "versioning"]),
    # Architecture & Patterns
    ("Architecture", "medium", "Explain the Repository pattern and why it's useful.", ["design-patterns", "architecture"]),
    ("Architecture", "medium", "What is Dependency Injection and how does it benefit testability?", ["design-patterns", "di"]),
    ("Architecture", "hard", "How does event-driven architecture differ from request-response?", ["architecture", "events"]),
    ("Architecture", "medium", "What is CQRS and when would you use it?", ["architecture", "cqrs"]),
    ("Architecture", "hard", "Explain the Saga pattern for distributed transactions.", ["architecture", "distributed-systems"]),
    ("Architecture", "easy", "What are SOLID principles? Explain one with an example.", ["design-patterns", "solid"]),
    ("Architecture", "medium", "What is the difference between coupling and cohesion?", ["architecture", "design"]),
    ("Architecture", "medium", "Explain the Circuit Breaker pattern.", ["architecture", "resilience"]),
    # Cloud & DevOps
    ("DevOps", "easy", "What is the difference between Docker containers and virtual machines?", ["docker", "devops"]),
    ("DevOps", "medium", "How does Kubernetes orchestrate containerized applications?", ["kubernetes", "devops"]),
    ("DevOps", "medium", "What is CI/CD and what tools have you used?", ["devops", "ci-cd"]),
    ("DevOps", "easy", "What is infrastructure as code? Give an example.", ["devops", "iac"]),
    ("DevOps", "hard", "How would you design a zero-downtime deployment strategy?", ["devops", "deployment"]),
    ("DevOps", "medium", "Explain the difference between blue-green and canary deployments.", ["devops", "deployment"]),
    # Security
    ("Security", "easy", "What is SQL injection and how do you prevent it?", ["security", "sql"]),
    ("Security", "medium", "How does JWT authentication work?", ["security", "jwt", "authentication"]),
    ("Security", "medium", "What is OWASP and what are the top vulnerabilities?", ["security", "owasp"]),
    ("Security", "hard", "How would you implement secure secret management in a microservices environment?", ["security", "secrets"]),
    ("Security", "easy", "What is HTTPS and why is it important?", ["security", "https"]),
    # FastAPI Specific
    ("FastAPI", "easy", "How does FastAPI handle request validation using Pydantic?", ["fastapi", "pydantic", "validation"]),
    ("FastAPI", "medium", "How does dependency injection work in FastAPI?", ["fastapi", "di"]),
    ("FastAPI", "medium", "How would you implement background tasks in FastAPI?", ["fastapi", "background-tasks"]),
    ("FastAPI", "hard", "How do you implement custom middleware in FastAPI?", ["fastapi", "middleware"]),
    ("FastAPI", "medium", "How do you handle file uploads in FastAPI?", ["fastapi", "files"]),
    # Problem Solving
    ("Problem Solving", "medium", "How would you find the most frequent element in a list efficiently?", ["algorithms", "problem-solving"]),
    ("Problem Solving", "hard", "How do you find the shortest path between two nodes in a weighted graph?", ["algorithms", "graphs"]),
    ("Problem Solving", "medium", "How would you check if a binary tree is balanced?", ["algorithms", "trees"]),
    ("Problem Solving", "hard", "How would you implement a distributed lock?", ["distributed-systems", "concurrency"]),
    ("Problem Solving", "medium", "Given a stream of numbers, how would you find the median at any point?", ["algorithms", "data-structures"]),
    # Testing
    ("Testing", "easy", "What is the difference between unit tests, integration tests, and end-to-end tests?", ["testing", "quality"]),
    ("Testing", "medium", "How do you test asynchronous code in Python?", ["testing", "async", "python"]),
    ("Testing", "medium", "What is mocking and when should you use it?", ["testing", "mocking"]),
    ("Testing", "hard", "How would you design a test strategy for a distributed microservices system?", ["testing", "microservices"]),
    ("Testing", "easy", "What is TDD and how does it affect software design?", ["testing", "tdd"]),
    # More Technical
    ("Programming", "medium", "Explain the difference between concurrency and parallelism.", ["concurrency", "parallelism"]),
    ("Programming", "hard", "How do you profile a slow Python application?", ["python", "performance", "profiling"]),
    ("Database", "hard", "How do you implement optimistic locking in a database?", ["database", "concurrency"]),
    ("System Design", "hard", "How would you design a search engine indexer?", ["system-design", "search"]),
    ("Architecture", "hard", "Explain Domain-Driven Design (DDD) and when to apply it.", ["architecture", "ddd"]),
    ("DevOps", "hard", "How would you implement observability (logs, metrics, traces) in a microservices system?", ["devops", "observability"]),
    ("Security", "hard", "How do you prevent SSRF attacks in a backend service?", ["security", "ssrf"]),
    ("API Design", "hard", "How would you implement webhook delivery with retry logic?", ["api", "webhooks"]),
    ("Data Structures", "hard", "Explain skip lists and their advantages over balanced BSTs.", ["data-structures", "algorithms"]),
    ("Database", "hard", "How does PostgreSQL's MVCC (Multi-Version Concurrency Control) work?", ["database", "postgresql", "concurrency"]),
    ("System Design", "hard", "How would you design a distributed cache invalidation strategy?", ["system-design", "cache"]),
    ("Architecture", "hard", "What is the Strangler Fig pattern and when do you use it for legacy migration?", ["architecture", "migration"]),
    ("Programming", "hard", "How do you implement connection pooling in a database-backed application?", ["python", "database", "performance"]),
    ("Testing", "hard", "How do you ensure data consistency in tests that involve a real database?", ["testing", "database"]),
    ("Security", "medium", "How does OAuth 2.0 authorization code flow work?", ["security", "oauth", "authentication"]),
]

TELEPHONIC_QUESTIONS = [
    # Screening
    ("Screening", "easy", "Can you briefly walk me through your resume?", ["screening", "background"]),
    ("Screening", "easy", "What is your current notice period?", ["screening", "logistics"]),
    ("Screening", "easy", "Are you open to relocation or remote work?", ["screening", "logistics"]),
    ("Screening", "easy", "What are your salary expectations?", ["screening", "compensation"]),
    ("Screening", "easy", "Can you describe your current role in one sentence?", ["screening", "communication"]),
    ("Screening", "easy", "Why are you looking to leave your current position?", ["screening", "motivation"]),
    ("Screening", "easy", "Have you worked in a similar industry or domain before?", ["screening", "domain"]),
    ("Screening", "easy", "What type of team size have you worked in before?", ["screening", "experience"]),
    ("Screening", "medium", "What is your experience with agile or scrum methodologies?", ["screening", "agile"]),
    ("Screening", "medium", "Can you describe the size and scope of the largest project you have worked on?", ["screening", "experience"]),
    ("Screening", "easy", "How soon can you start?", ["screening", "logistics"]),
    ("Screening", "easy", "Are you interviewing with any other companies currently?", ["screening", "status"]),
    ("Screening", "medium", "What technologies or tools are you most comfortable with?", ["screening", "skills"]),
    ("Screening", "easy", "Have you managed or mentored junior developers?", ["screening", "leadership"]),
    ("Screening", "medium", "Can you tell me about a recent project you're proud of?", ["screening", "achievement"]),
    # Resume Validation
    ("Resume Validation", "easy", "I see you worked at [Company]. What were your main responsibilities there?", ["resume", "experience"]),
    ("Resume Validation", "medium", "Can you elaborate on the [technology/project] listed on your resume?", ["resume", "experience"]),
    ("Resume Validation", "easy", "How long did you work with [technology]?", ["resume", "skills"]),
    ("Resume Validation", "medium", "What was the team size in your last role?", ["resume", "experience"]),
    ("Resume Validation", "medium", "I noticed a gap in your employment history. Can you explain?", ["resume", "gaps"]),
    ("Resume Validation", "easy", "Which of your listed skills do you consider your strongest?", ["resume", "skills"]),
    ("Resume Validation", "medium", "Can you explain the architecture of the system you built at [Company]?", ["resume", "architecture"]),
    ("Resume Validation", "easy", "What was your specific contribution to the [project] on your resume?", ["resume", "contribution"]),
    ("Resume Validation", "medium", "Have you led teams before? What was your leadership style?", ["resume", "leadership"]),
    ("Resume Validation", "hard", "How did you measure the success of the project you described?", ["resume", "metrics"]),
    # Communication
    ("Communication", "easy", "How would you rate your communication skills on a scale of 1-10 and why?", ["communication", "self-assessment"]),
    ("Communication", "medium", "How do you ensure alignment with remote team members?", ["communication", "remote-work"]),
    ("Communication", "easy", "Are you comfortable speaking up in meetings or with senior stakeholders?", ["communication", "confidence"]),
    ("Communication", "medium", "How do you typically handle miscommunication in a project?", ["communication", "conflict"]),
    ("Communication", "easy", "Describe how you typically communicate project status to your manager.", ["communication", "reporting"]),
    ("Communication", "medium", "Have you worked with international teams? How did you navigate cultural differences?", ["communication", "global-teams"]),
    ("Communication", "easy", "Do you prefer written or verbal communication? Why?", ["communication", "style"]),
    ("Communication", "medium", "How do you handle it when you don't understand something in a meeting?", ["communication", "learning"]),
    # General Telephonic
    ("General", "easy", "What do you know about our company?", ["research", "preparation"]),
    ("General", "easy", "Why do you want to work at our company specifically?", ["motivation", "company"]),
    ("General", "medium", "What is your biggest professional achievement in the last 2 years?", ["achievement", "experience"]),
    ("General", "easy", "How do you handle working under pressure?", ["stress-management", "resilience"]),
    ("General", "medium", "Tell me about a time you had to quickly learn a new technology.", ["learning", "adaptability"]),
    ("General", "easy", "How important is team culture to you?", ["culture", "values"]),
    ("General", "medium", "What kind of projects excite you the most?", ["motivation", "interests"]),
    ("General", "easy", "What do you do to stay productive while working from home?", ["remote-work", "productivity"]),
    ("General", "medium", "Are you comfortable with on-call responsibilities?", ["commitment", "availability"]),
    ("General", "easy", "Do you have any questions for me?", ["curiosity", "engagement"]),
    # Additional
    ("Screening", "hard", "Tell me about a time you disagreed with a technical decision made by leadership.", ["conflict", "professionalism"]),
    ("Resume Validation", "hard", "What metrics did you use to track the performance of your system?", ["metrics", "performance"]),
    ("Communication", "hard", "Describe a time you had to present a complex technical topic to non-technical executives.", ["communication", "presentation"]),
    ("General", "hard", "If hired, what would your 30-60-90 day plan look like?", ["planning", "initiative"]),
    ("General", "hard", "What challenges do you anticipate in this role based on the job description?", ["self-awareness", "preparation"]),
]

VIRTUAL_QUESTIONS = [
    # Mixed Interview Questions
    ("Technical-Behavioral", "medium", "Tell me about a technically challenging project you led from design to deployment.", ["technical", "leadership", "projects"]),
    ("Technical-Behavioral", "hard", "Describe a situation where a system you designed failed in production. How did you diagnose and fix it?", ["incident-management", "problem-solving", "technical"]),
    ("Technical-Behavioral", "medium", "How do you balance technical debt against feature delivery?", ["technical", "planning", "tradeoffs"]),
    ("Technical-Behavioral", "hard", "Walk me through a time you introduced a new technology to your team. What was the adoption process?", ["technical", "change-management", "leadership"]),
    ("Technical-Behavioral", "medium", "Describe a time you had to mentor a junior developer on a complex technical topic.", ["mentoring", "technical", "communication"]),
    ("Technical-Behavioral", "hard", "Tell me about a system you designed that needed to handle 10x the original expected load.", ["system-design", "scalability", "technical"]),
    ("Technical-Behavioral", "medium", "How do you approach code reviews? What do you look for?", ["code-review", "quality", "teamwork"]),
    ("Technical-Behavioral", "easy", "How do you ensure your code is maintainable for future developers?", ["code-quality", "documentation"]),
    ("Technical-Behavioral", "medium", "Describe a time you advocated for a different technical approach than what the team initially chose.", ["advocacy", "technical", "communication"]),
    ("Technical-Behavioral", "hard", "How have you contributed to improving the engineering culture at a previous company?", ["culture", "leadership", "technical"]),
    # Situational
    ("Situational", "easy", "How would you approach your first week in this role?", ["onboarding", "planning"]),
    ("Situational", "medium", "A critical bug is found in production on a Friday afternoon. Walk me through your response.", ["incident-management", "problem-solving"]),
    ("Situational", "medium", "You're given a project with an unclear scope and tight deadline. What do you do first?", ["planning", "communication", "ambiguity"]),
    ("Situational", "hard", "You discover a major security vulnerability in production. How do you handle it?", ["security", "incident-management"]),
    ("Situational", "medium", "Two senior engineers disagree on architecture. You're asked to make the final call. How do you decide?", ["decision-making", "leadership", "architecture"]),
    ("Situational", "hard", "Your team is behind schedule and the client is unhappy. What actions do you take?", ["stakeholder-management", "leadership", "planning"]),
    ("Situational", "easy", "A colleague asks for your review on their code, but you're in the middle of a critical task. What do you do?", ["prioritization", "teamwork"]),
    ("Situational", "medium", "You realize a third-party dependency your system relies on is being deprecated. How do you handle it?", ["risk-management", "technical", "planning"]),
    # Case Study Style
    ("Case Study", "hard", "Design a microservices architecture for a large-scale e-commerce platform.", ["system-design", "microservices"]),
    ("Case Study", "hard", "How would you migrate a monolithic application to microservices with zero downtime?", ["architecture", "migration", "devops"]),
    ("Case Study", "medium", "A web application is experiencing high latency. Walk me through your debugging approach.", ["debugging", "performance"]),
    ("Case Study", "hard", "Design a data pipeline that processes 10 million events per day.", ["system-design", "data-engineering"]),
    ("Case Study", "medium", "How would you implement authentication and authorization for a multi-tenant SaaS platform?", ["security", "system-design", "saas"]),
    # Presentation
    ("Presentation", "easy", "How do you structure your presentations when explaining technical decisions?", ["communication", "presentation"]),
    ("Presentation", "medium", "Walk me through the architecture of the most complex system you have built.", ["architecture", "communication", "presentation"]),
    ("Presentation", "hard", "Present your technical approach to solving [a given problem] in 5 minutes.", ["communication", "technical", "presentation"]),
    ("Presentation", "medium", "How do you create technical documentation that is both thorough and accessible?", ["documentation", "communication"]),
    # Critical Thinking
    ("Critical Thinking", "medium", "What is the most important technical decision you have regretted? What would you do differently?", ["reflection", "learning"]),
    ("Critical Thinking", "hard", "If you could change one thing about how software is developed today, what would it be and why?", ["industry-knowledge", "critical-thinking"]),
    ("Critical Thinking", "medium", "How do you evaluate whether a new technology is worth adopting?", ["decision-making", "technology-evaluation"]),
    ("Critical Thinking", "hard", "What do you think is the biggest technical challenge the industry will face in the next 5 years?", ["industry-knowledge", "foresight"]),
    # General Virtual
    ("General", "easy", "How do you ensure effective collaboration when working in a fully remote team?", ["remote-work", "collaboration"]),
    ("General", "medium", "What tools and practices do you rely on for async communication?", ["remote-work", "tools"]),
    ("General", "easy", "How do you stay engaged and productive in a virtual interview setting?", ["professionalism", "communication"]),
    ("General", "medium", "How do you build relationships with colleagues you have never met in person?", ["remote-work", "relationship-building"]),
    ("General", "hard", "Describe how you would run a virtual project kickoff for a distributed team across 3 time zones.", ["remote-work", "leadership", "project-management"]),
    # Additional Virtual
    ("Technical-Behavioral", "easy", "How do you keep your technical skills sharp while managing day-to-day responsibilities?", ["learning", "growth"]),
    ("Situational", "hard", "You join a team mid-project with poor documentation. How do you get up to speed quickly?", ["onboarding", "adaptability"]),
    ("Case Study", "hard", "Design a scalable file storage and retrieval system.", ["system-design", "storage"]),
    ("Technical-Behavioral", "hard", "Tell me about a time you had to roll back a deployment. What caused it and what did you learn?", ["devops", "incident-management", "learning"]),
    ("Situational", "medium", "A key engineer unexpectedly leaves mid-project. How do you manage the transition?", ["risk-management", "leadership"]),
    ("Critical Thinking", "medium", "How do you decide between building a solution in-house versus using a third-party service?", ["decision-making", "build-vs-buy"]),
    ("General", "hard", "What would you do in the first 30 days to make an immediate impact in this role?", ["initiative", "planning"]),
    ("Presentation", "hard", "How would you present a post-mortem for a major production outage to leadership?", ["communication", "incident-management", "presentation"]),
    ("Situational", "easy", "You notice your team's morale is low. What steps do you take?", ["leadership", "culture", "empathy"]),
    ("Technical-Behavioral", "medium", "How do you approach debugging a problem you have never seen before?", ["debugging", "problem-solving"]),
]


async def seed(db_url: str, db_name: str) -> None:
    client = AsyncIOMotorClient(db_url)
    db = client[db_name]
    col = db["question_bank"]

    existing_count = await col.count_documents({})
    if existing_count > 0:
        print(f"Question bank already has {existing_count} questions. Skipping seed.")
        client.close()
        return

    def make_docs(questions: list, interview_type: str) -> list[dict]:
        return [
            {
                "interview_type": interview_type,
                "category": cat,
                "difficulty": diff,
                "question": q,
                "tags": tags,
                "is_active": True,
            }
            for cat, diff, q, tags in questions
        ]

    all_docs = (
        make_docs(HR_QUESTIONS, "hr")
        + make_docs(TECHNICAL_QUESTIONS, "technical")
        + make_docs(TELEPHONIC_QUESTIONS, "telephonic")
        + make_docs(VIRTUAL_QUESTIONS, "virtual")
    )

    result = await col.insert_many(all_docs)
    print(f"✅ Seeded {len(result.inserted_ids)} questions into question_bank.")

    # Summary
    for itype in ["hr", "technical", "telephonic", "virtual"]:
        count = await col.count_documents({"interview_type": itype})
        print(f"   {itype}: {count} questions")

    client.close()


if __name__ == "__main__":
    asyncio.run(seed(settings.mongodb_url, settings.mongodb_db_name))
