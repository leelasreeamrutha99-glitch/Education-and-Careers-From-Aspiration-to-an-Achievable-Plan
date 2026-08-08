{
  "app_name": "CareerPath AI — From Aspiration to an Achievable Plan",
  "version": "1.0",
  "purpose": "A GenAI career and learning navigator that helps women turn career aspirations into realistic, personalized and measurable career plans.",
  "target_users": [
    "Final-year college student entering the workforce",
    "Early-career professional seeking progression",
    "Woman returning after a career break",
    "Professional moving into leadership",
    "Woman transitioning into technology or another new field",
    "First-generation learner with limited professional networks"
  ],
  "core_journey": [
    "Discover",
    "Assess",
    "Map",
    "Target",
    "Plan",
    "Learn",
    "Prove",
    "Apply",
    "Recover",
    "Measure"
  ],
  "widgets": [
    {
      "id": "widget_01",
      "name": "Career Persona & Aspiration",
      "description": "Understand the user's career stage, background, aspirations and immediate goals.",
      "input_prompt": "Collect and analyze the user's career persona and aspiration. Ask for career stage, education, current or previous occupation, desired career direction, short-term goal, long-term aspiration, preferred industries and current career situation. Create a concise Career Aspiration Profile. Do not request passwords, government IDs, financial account details or other unnecessary sensitive information.",
      "output": "Career Aspiration Profile"
    },
    {
      "id": "widget_02",
      "name": "Skills & Experience Assessment",
      "description": "Assess existing skills, experience, strengths and evidence.",
      "input_prompt": "Analyze the user's technical skills, soft skills, tools, certifications, projects, internships, employment, volunteering, academic achievements and leadership/community experience. Classify skills as Strong, Developing, Evidence-backed or Potential/Needs Validation. Never assume a skill is absent merely because the user did not mention it. Highlight evidence supporting important skills.",
      "output": "Skills & Experience Profile"
    },
    {
      "id": "widget_03",
      "name": "Transferable Skills Detector",
      "description": "Identify transferable skills from previous education, work and life experience.",
      "input_prompt": "Identify transferable skills from the user's education, employment, projects, volunteering, coordination, communication and other experiences explicitly provided by the user. For every important transferable skill use: Experience → Transferable Skill → Potential Career Application → Evidence Needed. Do not stereotype based on gender, age, family status or socioeconomic background. Treat caregiving or career-break experience as context, not deficiency.",
      "output": "Transferable Skills Map"
    },
    {
      "id": "widget_04",
      "name": "Constraints & Opportunity Assessment",
      "description": "Understand practical constraints so the career plan is realistic.",
      "input_prompt": "Assess available hours per week, preferred learning time, budget, device/internet access, location constraints, remote/hybrid/on-site preference, responsibilities, accessibility needs, learning format, language preferences, confidence barriers and career-break context when voluntarily provided. Treat constraints as planning parameters rather than weaknesses. Create a Career Feasibility Profile.",
      "output": "Career Feasibility Profile"
    },
    {
      "id": "widget_05",
      "name": "Career Destination Explorer",
      "description": "Explore realistic career destinations based on the complete user profile.",
      "input_prompt": "Using the user's aspiration, skills, transferable skills, experience and constraints, generate three realistic career destinations. For each provide: role, why it fits, existing strengths, transferable skills, missing/developing skills, typical entry pathway, proof-of-skill opportunity, compatibility with constraints, risks and trade-offs. Rank them as Best Fit, Strong Alternative and Stretch Destination. Do not guarantee employment, salary or job availability.",
      "output": "Three Career Destination Options"
    },
    {
      "id": "widget_06",
      "name": "Target Role Decision",
      "description": "Help the user select the most achievable target career role.",
      "input_prompt": "Compare the three career destinations using skill fit, experience fit, learning effort, time feasibility, cost feasibility, accessibility, opportunity potential and proof-of-skill feasibility. Recommend the most achievable option with transparent reasoning while allowing the user to override the recommendation. Produce a Target Career Card containing Target Role, Why This Role, Current Strengths, Transferable Advantages, Main Gaps and First Milestone. Explain important trade-offs.",
      "output": "Target Career Card"
    },
    {
      "id": "widget_07",
      "name": "Skill-Gap & Readiness Map",
      "description": "Map current capabilities against the requirements of the target role.",
      "input_prompt": "For the selected target role, identify the most important skills and classify each as Ready, Strengthen, Learn or Demonstrate. For each skill provide Current Level, Required Level, Gap, Priority, How to Build and How to Prove. Prioritize high-impact gaps rather than generating a generic long list. Use evidence from the user's profile when available.",
      "output": "Prioritized Skill-Gap Map"
    },
    {
      "id": "widget_08",
      "name": "Personalized 30/60/90-Day Plan",
      "description": "Create an achievable career development roadmap.",
      "input_prompt": "Create a personalized 30-, 60- or 90-day career development plan based on the target role, skill gaps, available time, budget and constraints. Use Foundation → Applied Practice → Portfolio/Interview Readiness. Every milestone must include Action, Estimated Time, Expected Outcome, Completion Evidence, Priority and Difficulty. If 90 days is unrealistic, recommend a shorter or adjusted plan. Avoid overloading the user.",
      "output": "Personalized Career Plan"
    },
    {
      "id": "widget_09",
      "name": "Adaptive Weekly Schedule",
      "description": "Turn the career plan into a sustainable weekly schedule.",
      "input_prompt": "Convert the personalized career plan into a realistic weekly schedule based on the user's actual available hours, preferred learning times and responsibilities. Include focused learning, practice, project work and review. If useful, show low-, moderate- and high-availability patterns. Avoid assuming uninterrupted study time. Keep the schedule sustainable and tied to the highest-priority milestones.",
      "output": "Weekly Career Learning Schedule"
    },
    {
      "id": "widget_10",
      "name": "Learning Resource & Opportunity Navigator",
      "description": "Recommend relevant learning resources and career opportunities.",
      "input_prompt": "Recommend learning resources and opportunity types relevant to the selected target role and skill gaps. For every recommendation provide: what it teaches, why it is relevant, estimated time, cost category, expected outcome, difficulty, prerequisites and accessibility considerations where appropriate. Prefer free or affordable options when budget is limited. Never fabricate course names, prices, job openings, salaries, certifications or URLs. Clearly label information that requires verification.",
      "output": "Personalized Learning & Opportunity Recommendations"
    },
    {
      "id": "widget_11",
      "name": "Proof-of-Skill Builder",
      "description": "Create a practical project or artifact that proves career readiness.",
      "input_prompt": "Design one achievable proof-of-skill project, portfolio artifact, case study or practical task aligned with the target role. Include Project Title, Problem Statement, Skills Demonstrated, Deliverables, Tools, Step-by-Step Execution, Portfolio Presentation Structure, Evidence Checklist and Evaluation Rubric. Make it achievable within the user's available time and resources. Connect the project directly to the highest-priority skill gaps.",
      "output": "Proof-of-Skill Project"
    },
    {
      "id": "widget_12",
      "name": "Interview & Career Action Simulator",
      "description": "Prepare the user for interviews and identify an immediate career action.",
      "input_prompt": "Generate personalized interview preparation for the target role: five role-specific questions, three behavioral questions and two transferable-skill questions. Provide answer structures and STAR guidance where appropriate. Use the user's actual experience when available and identify the skill being tested. Then recommend exactly one high-value career action that can be completed within 24–72 hours.",
      "output": "Interview Preparation & 72-Hour Career Action"
    },
    {
      "id": "widget_13",
      "name": "AI Recovery Coach",
      "description": "Adapt the plan when the user falls behind or circumstances change.",
      "input_prompt": "Act as a supportive recovery coach. If the user misses a week, has less available time, finds learning too difficult, loses motivation, faces increased responsibilities, cannot afford a resource, completes work faster than expected or changes career direction, identify what changed, preserve completed progress, recalculate remaining tasks, reduce or rearrange workload, protect key milestones and create a revised schedule. Never blame the user and do not restart the entire plan unless necessary.",
      "output": "Adaptive Recovery Plan"
    },
    {
      "id": "widget_14",
      "name": "Career Readiness Dashboard",
      "description": "Measure progress using an interpretable readiness estimate.",
      "input_prompt": "Calculate an interpretable Career Readiness estimate from: Goal Clarity, Skill Readiness, Transferable-Skill Evidence, Portfolio/Proof of Skill, Interview Readiness, Practical Feasibility and Completed Career Action. Display a 0–100 estimate with category breakdown. Also show READY NOW, NEXT PRIORITY, PROOF NEEDED and NEXT CAREER ACTION. Explicitly state that the score is an estimate for planning and is not a prediction or guarantee of employment.",
      "output": "Career Readiness Dashboard"
    },
    {
      "id": "widget_15",
      "name": "Personalized Career Roadmap",
      "description": "Combine the entire journey into one clear final action plan.",
      "input_prompt": "Create a final personalized Career Roadmap using all relevant information from the previous stages. Display: My Career Destination, My Advantages, My Top Skill Gaps, My 30/60/90 Plan, My Weekly Routine, My Proof-of-Skill Project, My Readiness Estimate, My Recovery Strategy and My Next Action within 72 hours. For major recommendations use Recommendation → Evidence → Reason → Trade-off. End with an encouraging but realistic message. Do not guarantee employment.",
      "output": "Final Personalized Career Roadmap"
    }
  ],
  "global_ai_instructions": [
    "Use information from earlier widgets to personalize later outputs.",
    "Do not ask questions that have already been answered.",
    "Do not expose hidden chain-of-thought. Provide concise decision explanations.",
    "For important recommendations use Recommendation → Evidence → Reason → Trade-off.",
    "Never guarantee employment, salary or job placement.",
    "Never fabricate job openings, courses, prices, certifications, salaries or URLs.",
    "Clearly identify estimates and information that requires verification.",
    "Do not make career recommendations using gender stereotypes or assumptions based on age, marital status, family status or socioeconomic background.",
    "Treat career breaks, caregiving and accessibility needs as context and planning constraints, not deficiencies.",
    "Request only information necessary for career planning.",
    "Do not request passwords, government identification numbers, bank details or confidential employer information.",
    "Keep plans achievable within the user's actual time and resources.",
    "When the user falls behind, preserve completed progress and adapt the plan rather than blaming the user.",
    "The readiness score is an estimate for planning and must never be presented as an employment prediction."
  ],
  "success_moment": {
    "before": "I want to restart my career, but I don't know where to begin.",
    "after": "I know my realistic target role, my transferable strengths, my skill gaps, my achievable schedule, my proof of skill and my next career action."
  },
  "innovation": [
    "Transferable Skills Detector",
    "AI Recovery Coach",
    "Interpretable Career Readiness Dashboard",
    "Proof-of-Skill Builder",
    "Constraint-aware career planning"
  ],
  "responsible_ai": {
    "privacy": "Collect only information necessary for career planning and avoid sensitive identifiers.",
    "bias": "Do not stereotype or restrict career options based on demographic characteristics.",
    "accuracy": "Do not invent external facts and clearly communicate uncertainty.",
    "transparency": "Explain recommendations using evidence, reasoning and trade-offs.",
    "human_oversight": "Encourage users to review important career and education decisions with appropriate human advisors when needed.",
    "security": "Do not request or process passwords, government IDs, banking information or confidential organizational information."
  }
}
