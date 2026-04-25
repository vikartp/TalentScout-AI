"""Resume profile data for sample PDF generation.

12 profiles with varied match levels across 3 JDs:
  - Full-Stack JD:    2 strong, 2 partial, 2 weak/wrong domain, 1 junior
  - Data Scientist JD: 2 strong
  - DevOps JD:         2 strong, 1 partial (sysadmin)
"""

RESUMES = [
    # --- STRONG MATCHES for Full-Stack JD ---
    {
        "filename": "Arjun_Mehta_Resume.pdf",
        "name": "Arjun Mehta",
        "email": "arjun.mehta@email.com",
        "phone": "+91-98765-43210",
        "summary": (
            "Senior Full-Stack Engineer with 6 years of experience building scalable SaaS platforms. "
            "Proficient in React, Next.js, Python (FastAPI), PostgreSQL, Docker, and AWS. "
            "Passionate about clean architecture, mentoring teams, and shipping production-grade software."
        ),
        "skills": [
            "React.js", "Next.js", "TypeScript", "Python", "FastAPI", "Django",
            "PostgreSQL", "MongoDB", "Docker", "Kubernetes", "AWS (EC2, S3, Lambda)",
            "Redis", "RabbitMQ", "Git", "CI/CD (GitHub Actions)", "REST APIs",
            "GraphQL", "Microservices", "System Design", "Agile/Scrum",
        ],
        "experience": [
            {
                "role": "Senior Full-Stack Engineer",
                "company": "CloudNine Technologies",
                "duration": "Jan 2022 - Present (2.5 years)",
                "highlights": [
                    "Led a team of 5 engineers to rebuild the core SaaS dashboard using Next.js and FastAPI, improving page load by 60%.",
                    "Designed and implemented a microservices architecture serving 50K+ daily active users.",
                    "Set up CI/CD pipelines with GitHub Actions, achieving 99.5% deployment success rate.",
                    "Mentored 3 junior developers through code reviews and pair programming sessions.",
                ],
            },
            {
                "role": "Full-Stack Developer",
                "company": "StartupHub India",
                "duration": "Jun 2019 - Dec 2021 (2.5 years)",
                "highlights": [
                    "Built a multi-tenant B2B platform from scratch using React, Node.js, and PostgreSQL.",
                    "Implemented real-time notification system using Redis pub/sub and WebSockets.",
                    "Reduced API response time by 40% through query optimization and caching strategies.",
                ],
            },
            {
                "role": "Junior Developer",
                "company": "TechVentures Pvt. Ltd.",
                "duration": "Jul 2018 - May 2019 (1 year)",
                "highlights": [
                    "Developed internal tools using React and Django REST framework.",
                    "Wrote unit and integration tests, improving code coverage from 45% to 80%.",
                ],
            },
        ],
        "education": [
            {"degree": "B.Tech in Computer Science", "institution": "IIT Hyderabad", "year": "2018"},
        ],
        "achievements": [
            "Speaker at ReactConf India 2023 on 'Scaling Next.js for Enterprise'",
            "Open-source contributor to FastAPI ecosystem (500+ GitHub stars on personal projects)",
        ],
    },
    {
        "filename": "Priya_Sharma_Resume.pdf",
        "name": "Priya Sharma",
        "email": "priya.sharma@email.com",
        "phone": "+91-87654-32109",
        "summary": (
            "Full-Stack Software Engineer with 7 years of experience specializing in React/TypeScript frontends "
            "and Node.js/Python backends. Strong background in PostgreSQL, Docker, cloud deployments, "
            "and leading cross-functional agile teams."
        ),
        "skills": [
            "React.js", "Next.js", "TypeScript", "JavaScript", "Node.js", "Express.js",
            "Python", "Django", "PostgreSQL", "MySQL", "Docker", "Kubernetes",
            "GCP", "Terraform", "GraphQL", "REST APIs", "Redis", "Kafka",
            "Git", "Jenkins", "Technical Writing",
        ],
        "experience": [
            {
                "role": "Lead Full-Stack Engineer",
                "company": "FinEdge Solutions",
                "duration": "Mar 2021 - Present (3 years)",
                "highlights": [
                    "Architected a real-time trading dashboard serving 100K+ concurrent users using React, WebSockets, and GCP.",
                    "Led migration from monolith to microservices, reducing deployment times from 2 hours to 15 minutes.",
                    "Managed a team of 8 engineers, conducting weekly architecture reviews and sprint planning.",
                    "Wrote comprehensive technical documentation and API design guidelines adopted company-wide.",
                ],
            },
            {
                "role": "Senior Software Engineer",
                "company": "DataPrime Analytics",
                "duration": "Aug 2018 - Feb 2021 (2.5 years)",
                "highlights": [
                    "Built an analytics platform frontend with React and D3.js, processing 10M+ data points daily.",
                    "Developed RESTful APIs in Django serving 500+ enterprise clients.",
                    "Implemented Kafka-based event streaming pipeline for real-time data processing.",
                ],
            },
            {
                "role": "Software Engineer",
                "company": "WebCraft Studios",
                "duration": "Jun 2017 - Jul 2018 (1 year)",
                "highlights": [
                    "Developed responsive web applications using React and Node.js.",
                    "Set up Docker-based development environments, improving team onboarding time by 50%.",
                ],
            },
        ],
        "education": [
            {"degree": "M.Tech in Software Engineering", "institution": "BITS Pilani", "year": "2017"},
            {"degree": "B.Tech in Information Technology", "institution": "NIT Trichy", "year": "2015"},
        ],
        "achievements": [
            "Published article on 'Microservices Patterns in FinTech' in IEEE Software (2023)",
            "GCP Professional Cloud Architect certified",
        ],
    },

    # --- PARTIAL MATCHES for Full-Stack JD ---
    {
        "filename": "Rahul_Verma_Resume.pdf",
        "name": "Rahul Verma",
        "email": "rahul.verma@email.com",
        "phone": "+91-76543-21098",
        "summary": (
            "Backend Engineer with 5 years of experience in Python and Go. Strong in API design, "
            "databases, and cloud infrastructure. Limited frontend experience but eager to grow into full-stack roles."
        ),
        "skills": [
            "Python", "FastAPI", "Go", "PostgreSQL", "MongoDB", "Docker",
            "Kubernetes", "AWS", "REST APIs", "gRPC", "Redis", "Celery",
            "Git", "CI/CD", "Linux", "System Design",
        ],
        "experience": [
            {
                "role": "Backend Engineer",
                "company": "ScaleUp Technologies",
                "duration": "Apr 2021 - Present (3 years)",
                "highlights": [
                    "Designed and built high-throughput RESTful APIs in FastAPI handling 10K requests/sec.",
                    "Implemented distributed task queue with Celery and Redis for async processing.",
                    "Optimized PostgreSQL queries reducing average response time by 55%.",
                ],
            },
            {
                "role": "Junior Backend Developer",
                "company": "CodeBase Innovations",
                "duration": "Jun 2019 - Mar 2021 (2 years)",
                "highlights": [
                    "Built microservices in Python and Go for an e-commerce platform.",
                    "Set up monitoring and alerting using Prometheus and Grafana.",
                ],
            },
        ],
        "education": [
            {"degree": "B.Tech in Computer Science", "institution": "VIT Vellore", "year": "2019"},
        ],
        "achievements": [
            "Winner, HackIndia Backend Challenge 2022",
        ],
    },
    {
        "filename": "Sneha_Iyer_Resume.pdf",
        "name": "Sneha Iyer",
        "email": "sneha.iyer@email.com",
        "phone": "+91-65432-10987",
        "summary": (
            "Frontend Developer with 4 years of experience in React and Vue.js. "
            "Focused on building accessible, performant web applications. "
            "Some exposure to Node.js backends but primarily frontend-focused."
        ),
        "skills": [
            "React.js", "Next.js", "Vue.js", "TypeScript", "JavaScript",
            "HTML5", "CSS3", "Tailwind CSS", "Figma", "Storybook",
            "Node.js (basic)", "REST APIs (consumption)", "Git", "Jest", "Cypress",
        ],
        "experience": [
            {
                "role": "Senior Frontend Developer",
                "company": "DesignTech Labs",
                "duration": "Jan 2022 - Present (2 years)",
                "highlights": [
                    "Led frontend development for a design system used across 5 products with 200+ components.",
                    "Improved Core Web Vitals scores by 40% through performance optimization.",
                    "Implemented accessibility standards achieving WCAG 2.1 AA compliance.",
                ],
            },
            {
                "role": "Frontend Developer",
                "company": "PixelPerfect Agency",
                "duration": "Aug 2020 - Dec 2021 (1.5 years)",
                "highlights": [
                    "Built responsive SPAs for 10+ clients using React and Vue.js.",
                    "Created reusable component library reducing development time by 30%.",
                ],
            },
        ],
        "education": [
            {"degree": "B.Des in Interaction Design", "institution": "NID Ahmedabad", "year": "2020"},
        ],
        "achievements": [
            "Featured in CSS-Tricks for open-source UI kit (2K+ GitHub stars)",
        ],
    },

    # --- WEAK MATCHES / DIFFERENT DOMAIN ---
    {
        "filename": "Vikram_Joshi_Resume.pdf",
        "name": "Vikram Joshi",
        "email": "vikram.joshi@email.com",
        "phone": "+91-54321-09876",
        "summary": (
            "Marketing Manager with 8 years of experience in digital marketing, brand strategy, "
            "and team leadership. Strong analytical skills with expertise in SEO, SEM, and social media campaigns."
        ),
        "skills": [
            "Digital Marketing", "SEO/SEM", "Google Analytics", "Facebook Ads",
            "Content Strategy", "Brand Management", "Team Leadership",
            "HubSpot", "Salesforce", "A/B Testing", "Data Analysis",
            "Copywriting", "Public Speaking",
        ],
        "experience": [
            {
                "role": "Marketing Manager",
                "company": "BrandWave Media",
                "duration": "Feb 2020 - Present (4 years)",
                "highlights": [
                    "Led a team of 12 to execute multi-channel campaigns generating 2M+ leads annually.",
                    "Increased organic traffic by 150% through SEO strategy overhaul.",
                    "Managed annual marketing budget of $2M with consistent ROI above 300%.",
                ],
            },
            {
                "role": "Senior Marketing Executive",
                "company": "GrowthPulse Digital",
                "duration": "Jun 2016 - Jan 2020 (3.5 years)",
                "highlights": [
                    "Developed and executed content marketing strategy for B2B SaaS clients.",
                    "Set up marketing automation workflows in HubSpot, improving lead conversion by 45%.",
                ],
            },
        ],
        "education": [
            {"degree": "MBA in Marketing", "institution": "IIM Lucknow", "year": "2016"},
            {"degree": "B.Com", "institution": "Delhi University", "year": "2014"},
        ],
        "achievements": [
            "Google Ads Certified Professional",
            "Speaker at AdTech India 2023",
        ],
    },
    {
        "filename": "Neha_Kapoor_Resume.pdf",
        "name": "Neha Kapoor",
        "email": "neha.kapoor@email.com",
        "phone": "+91-43210-98765",
        "summary": (
            "Mechanical Engineer with 3 years of experience in product design and manufacturing. "
            "Skilled in CAD, simulation, and project management. Looking to transition into tech."
        ),
        "skills": [
            "AutoCAD", "SolidWorks", "ANSYS", "MATLAB", "3D Printing",
            "Project Management", "Six Sigma (Green Belt)", "MS Excel (Advanced)",
            "Python (basic scripting)", "Technical Report Writing",
        ],
        "experience": [
            {
                "role": "Product Design Engineer",
                "company": "Tata Motors",
                "duration": "Jul 2021 - Present (3 years)",
                "highlights": [
                    "Designed automotive components using SolidWorks, reducing material cost by 15%.",
                    "Led a cross-functional team of 6 for a new product launch, delivered 2 weeks ahead of schedule.",
                    "Automated reporting workflows using Python scripts, saving 10 hours/week.",
                ],
            },
        ],
        "education": [
            {"degree": "B.Tech in Mechanical Engineering", "institution": "IIT Bombay", "year": "2021"},
        ],
        "achievements": [
            "Six Sigma Green Belt certified",
            "Winner, Tata InnoVerse Hackathon 2023",
        ],
    },

    # --- MATCHES for Data Scientist JD ---
    {
        "filename": "Ananya_Reddy_Resume.pdf",
        "name": "Ananya Reddy",
        "email": "ananya.reddy@email.com",
        "phone": "+91-32109-87654",
        "summary": (
            "Data Scientist with 4 years of experience building ML models for recommendation systems "
            "and predictive analytics. Strong in Python, deep learning, and production ML deployment. "
            "Published researcher in NLP."
        ),
        "skills": [
            "Python", "NumPy", "Pandas", "Scikit-learn", "TensorFlow", "PyTorch",
            "SQL", "Spark", "NLP", "LLM Fine-tuning", "Feature Engineering",
            "MLflow", "Docker", "AWS SageMaker", "A/B Testing",
            "Statistics", "Data Visualization (Matplotlib, Seaborn)",
        ],
        "experience": [
            {
                "role": "Senior Data Scientist",
                "company": "RecoAI Labs",
                "duration": "May 2022 - Present (2 years)",
                "highlights": [
                    "Built real-time recommendation engine using collaborative filtering and deep learning, improving CTR by 25%.",
                    "Deployed ML models to production using MLflow and SageMaker, serving 5M+ predictions/day.",
                    "Led NLP project for sentiment analysis of customer reviews using fine-tuned BERT models.",
                    "Conducted A/B tests for model variants, establishing experimentation framework for the team.",
                ],
            },
            {
                "role": "Data Scientist",
                "company": "Flipkart",
                "duration": "Jul 2020 - Apr 2022 (2 years)",
                "highlights": [
                    "Developed demand forecasting models using gradient boosting, reducing inventory costs by 18%.",
                    "Built feature engineering pipelines processing 100M+ rows using Spark.",
                    "Collaborated with product team to define ML-driven personalization features.",
                ],
            },
        ],
        "education": [
            {"degree": "M.S. in Data Science", "institution": "ISI Kolkata", "year": "2020"},
            {"degree": "B.Tech in Computer Science", "institution": "IIIT Hyderabad", "year": "2018"},
        ],
        "achievements": [
            "Published 2 papers on NLP at ACL and EMNLP conferences",
            "Kaggle Competition Master (top 1%)",
        ],
    },
    {
        "filename": "Karthik_Nair_Resume.pdf",
        "name": "Karthik Nair",
        "email": "karthik.nair@email.com",
        "phone": "+91-21098-76543",
        "summary": (
            "ML Engineer with 5 years of experience building and deploying machine learning systems at scale. "
            "Expert in Python, deep learning, and MLOps. Experience with both classical ML and modern LLM applications."
        ),
        "skills": [
            "Python", "PyTorch", "TensorFlow", "Scikit-learn", "NumPy", "Pandas",
            "SQL", "MLflow", "Kubeflow", "Docker", "Kubernetes",
            "GCP (Vertex AI)", "Spark", "Feature Engineering",
            "Deep Learning", "Transformers", "Computer Vision",
            "Statistics", "Causal Inference", "Git",
        ],
        "experience": [
            {
                "role": "Senior ML Engineer",
                "company": "Google (Bangalore)",
                "duration": "Jan 2022 - Present (2.5 years)",
                "highlights": [
                    "Built and maintained ML pipelines on Vertex AI serving 100M+ daily predictions.",
                    "Developed computer vision models for Google Lens features, improving accuracy by 12%.",
                    "Established MLOps best practices using Kubeflow, reducing model deployment time from days to hours.",
                    "Mentored 2 junior ML engineers on production ML patterns.",
                ],
            },
            {
                "role": "ML Engineer",
                "company": "Amazon (Hyderabad)",
                "duration": "Aug 2019 - Dec 2021 (2.5 years)",
                "highlights": [
                    "Designed personalization models for product recommendations on Amazon.in.",
                    "Built distributed training pipelines using Spark and SageMaker for large-scale datasets.",
                    "Conducted causal inference studies for pricing optimization experiments.",
                ],
            },
        ],
        "education": [
            {"degree": "M.Tech in AI & ML", "institution": "IISc Bangalore", "year": "2019"},
            {"degree": "B.Tech in ECE", "institution": "NIT Surathkal", "year": "2017"},
        ],
        "achievements": [
            "Google Spot Bonus for ML Lens improvements (2023)",
            "Published paper on efficient transformer training at NeurIPS 2022",
        ],
    },

    # --- STRONG MATCHES for DevOps JD ---
    {
        "filename": "Deepak_Srinivasan_Resume.pdf",
        "name": "Deepak Srinivasan",
        "email": "deepak.srini@email.com",
        "phone": "+91-98712-34567",
        "summary": (
            "Senior DevOps Engineer with 6 years of experience building and managing large-scale "
            "cloud infrastructure on AWS. Expert in Kubernetes, Terraform, CI/CD automation, and "
            "observability. Passionate about platform reliability and developer experience."
        ),
        "skills": [
            "AWS (EC2, EKS, S3, RDS, Lambda, IAM)", "Kubernetes", "Docker",
            "Terraform", "GitHub Actions", "ArgoCD", "Jenkins",
            "Prometheus", "Grafana", "Datadog", "ELK Stack",
            "Python", "Bash", "Linux", "Helm", "Istio",
            "Networking (DNS, VPC, Load Balancing)", "HashiCorp Vault",
            "Ansible", "Git", "SOC2 Compliance",
        ],
        "experience": [
            {
                "role": "Senior DevOps Engineer",
                "company": "PayScale Technologies",
                "duration": "Mar 2022 - Present (2.5 years)",
                "highlights": [
                    "Managed 15 EKS clusters with 500+ pods serving 10M+ daily requests across 3 AWS regions.",
                    "Built zero-downtime deployment pipelines using ArgoCD and GitHub Actions for 40+ microservices.",
                    "Reduced AWS infrastructure costs by 35% through right-sizing, spot instances, and Kubecost analysis.",
                    "Implemented full observability stack (Prometheus + Grafana + Datadog) reducing MTTR from 45min to 8min.",
                    "Led SOC2 Type II compliance automation using OPA policies and Vault for secrets management.",
                ],
            },
            {
                "role": "DevOps Engineer",
                "company": "Freshworks",
                "duration": "Jun 2019 - Feb 2022 (2.5 years)",
                "highlights": [
                    "Migrated 20+ services from EC2 to Kubernetes (EKS), improving deployment frequency by 5x.",
                    "Wrote Terraform modules for entire AWS infrastructure, managing 200+ resources.",
                    "Set up centralized logging with ELK Stack processing 500GB+ logs daily.",
                    "Implemented Istio service mesh for inter-service communication and traffic management.",
                ],
            },
            {
                "role": "Junior Systems Engineer",
                "company": "Infosys",
                "duration": "Jul 2018 - May 2019 (1 year)",
                "highlights": [
                    "Managed Linux servers and automated routine tasks using Bash and Python scripts.",
                    "Set up Jenkins CI pipelines for Java microservices.",
                ],
            },
        ],
        "education": [
            {"degree": "B.Tech in Computer Science", "institution": "NIT Warangal", "year": "2018"},
        ],
        "achievements": [
            "AWS Solutions Architect Professional certified",
            "CKA (Certified Kubernetes Administrator)",
            "Speaker at DevOpsDays Bangalore 2023",
        ],
    },
    {
        "filename": "Meera_Krishnan_Resume.pdf",
        "name": "Meera Krishnan",
        "email": "meera.krishnan@email.com",
        "phone": "+91-87612-45678",
        "summary": (
            "Platform Engineer with 5 years of experience in cloud infrastructure, "
            "Kubernetes orchestration, and CI/CD automation. Strong background in AWS and GCP, "
            "Terraform, and building reliable production systems."
        ),
        "skills": [
            "AWS (EC2, EKS, S3, RDS, VPC, IAM)", "GCP (GKE, Cloud Run)",
            "Kubernetes", "Docker", "Terraform", "CloudFormation",
            "GitHub Actions", "Jenkins", "Prometheus", "Grafana",
            "Python", "Bash", "Go", "Linux", "Helm",
            "Networking (DNS, Load Balancers, VPN)", "Ansible",
            "Git", "Agile/Scrum",
        ],
        "experience": [
            {
                "role": "Platform Engineer",
                "company": "Razorpay",
                "duration": "Jan 2022 - Present (2.5 years)",
                "highlights": [
                    "Designed and managed multi-region Kubernetes infrastructure handling 1B+ payment transactions/month.",
                    "Built self-service deployment platform using ArgoCD, reducing deployment time from 30min to 5min.",
                    "Implemented infrastructure-as-code across 50+ AWS accounts using Terraform with remote state.",
                    "Created automated disaster recovery runbooks, achieving 99.99% uptime SLA.",
                ],
            },
            {
                "role": "DevOps Engineer",
                "company": "Thoughtworks",
                "duration": "Aug 2019 - Dec 2021 (2.5 years)",
                "highlights": [
                    "Consulted for 5+ enterprise clients on cloud migration and DevOps transformation.",
                    "Built CI/CD pipelines using Jenkins and GitHub Actions for polyglot microservices.",
                    "Automated compliance checks using custom Python tools and OPA policies.",
                ],
            },
        ],
        "education": [
            {"degree": "B.Tech in Information Technology", "institution": "Anna University", "year": "2019"},
        ],
        "achievements": [
            "AWS Solutions Architect Associate certified",
            "HashiCorp Terraform Associate certified",
            "Open-source contributor to Helm charts repository",
        ],
    },

    # --- PARTIAL DevOps MATCH (sysadmin, less k8s) ---
    {
        "filename": "Rohan_Gupta_Resume.pdf",
        "name": "Rohan Gupta",
        "email": "rohan.gupta@email.com",
        "phone": "+91-76512-34589",
        "summary": (
            "Linux System Administrator with 4 years of experience in server management, "
            "networking, and basic cloud operations. Some Docker and AWS experience. "
            "Looking to transition into a full DevOps role."
        ),
        "skills": [
            "Linux (Ubuntu, CentOS, RHEL)", "Bash scripting", "Networking",
            "AWS (EC2, S3, basic VPC)", "Docker (basic)",
            "Nagios", "Zabbix", "Apache", "Nginx",
            "MySQL", "Firewall management", "DNS management",
            "Python (basic)", "VMware", "Backup & Recovery",
        ],
        "experience": [
            {
                "role": "Senior System Administrator",
                "company": "TechMahindra",
                "duration": "Apr 2021 - Present (3 years)",
                "highlights": [
                    "Managed 200+ Linux servers across on-premise and AWS environments.",
                    "Automated server provisioning using Bash scripts, reducing setup time by 70%.",
                    "Implemented monitoring with Nagios and Zabbix for 99.9% uptime.",
                    "Migrated 20 on-premise applications to AWS EC2 with basic VPC networking.",
                ],
            },
            {
                "role": "Junior System Administrator",
                "company": "Wipro",
                "duration": "Jul 2020 - Mar 2021 (9 months)",
                "highlights": [
                    "Supported 50+ Linux and Windows servers for enterprise clients.",
                    "Handled DNS, DHCP, and firewall configurations.",
                ],
            },
        ],
        "education": [
            {"degree": "B.Tech in Computer Science", "institution": "SRM University", "year": "2020"},
        ],
        "achievements": [
            "RHCE (Red Hat Certified Engineer)",
            "AWS Cloud Practitioner certified",
        ],
    },

    # --- JUNIOR FULL-STACK (adds variety) ---
    {
        "filename": "Aisha_Khan_Resume.pdf",
        "name": "Aisha Khan",
        "email": "aisha.khan@email.com",
        "phone": "+91-65412-78901",
        "summary": (
            "Junior Full-Stack Developer with 1.5 years of experience building web applications "
            "using React and Node.js. Quick learner eager to grow in a fast-paced environment."
        ),
        "skills": [
            "React.js", "JavaScript", "Node.js", "Express.js",
            "HTML5", "CSS3", "MongoDB", "REST APIs",
            "Git", "VS Code", "Postman", "Basic SQL",
        ],
        "experience": [
            {
                "role": "Junior Full-Stack Developer",
                "company": "StartupBridge",
                "duration": "Jan 2023 - Present (1.5 years)",
                "highlights": [
                    "Built and maintained 3 client-facing web applications using React and Node.js.",
                    "Implemented RESTful APIs serving 5K+ daily users.",
                    "Created responsive UI components following design system guidelines.",
                    "Participated in code reviews and agile ceremonies.",
                ],
            },
        ],
        "education": [
            {"degree": "B.Tech in Computer Science", "institution": "Manipal University", "year": "2022"},
        ],
        "achievements": [
            "Winner, college hackathon 2022 (team of 4)",
            "3-star rating on CodeChef",
        ],
    },
]
