import { useEffect, useMemo, useRef, useState } from "react";
import "./App.css";
import { analyzeResume } from "./services/api";

const Icon = ({ name, size = 18 }) => {
  const common = {
    width: size,
    height: size,
    viewBox: "0 0 24 24",
    fill: "currentColor",
    stroke: "none",
    "aria-hidden": "true",
  };

  const paths = {
    file: <path fill="currentColor" d="M6 2.75A2.25 2.25 0 0 1 8.25.5h6.2L20.5 6.55v14.2A2.25 2.25 0 0 1 18.25 23h-10A2.25 2.25 0 0 1 6 20.75zM14 2.9v4.45h4.25zM9 12.25h6.5a1 1 0 1 0 0-2H9a1 1 0 1 0 0 2m0 4h6.5a1 1 0 1 0 0-2H9a1 1 0 1 0 0 2m0 4h4.5a1 1 0 1 0 0-2H9a1 1 0 1 0 0 2" />,
    upload: <path fill="currentColor" d="M11 16V7.83L8.41 10.4 7 9l5-5 5 5-1.41 1.4L13 7.83V16zM5 20v-2h14v2z" />,
    check: <path fill="currentColor" d="m9.15 18.25-5.4-5.4 1.9-1.9 3.5 3.5 9.2-9.2 1.9 1.9z" />,
    x: <path fill="currentColor" d="m7.05 5.64 4.95 4.95 4.95-4.95 1.41 1.41-4.95 4.95 4.95 4.95-1.41 1.41L12 13.41l-4.95 4.95-1.41-1.41 4.95-4.95-4.95-4.95z" />,
    arrow: <path fill="currentColor" d="M4 11h11.17l-4.58-4.59L12 5l7 7-7 7-1.41-1.41L15.17 13H4z" />,
    briefcase: <path fill="currentColor" d="M8 5V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v1h3a3 3 0 0 1 3 3v9a3 3 0 0 1-3 3H5a3 3 0 0 1-3-3V8a3 3 0 0 1 3-3zm2-1v1h4V4zM4 10v2h16v-2zm6 4v2h4v-2z" />,
    spark: <path fill="currentColor" d="m12 2 1.8 6.2L20 10l-6.2 1.8L12 18l-1.8-6.2L4 10l6.2-1.8zm7 13 1 3 3 1-3 1-1 3-1-3-3-1 3-1z" />,
    clock: <path fill="currentColor" d="M12 2a10 10 0 1 0 10 10A10.01 10.01 0 0 0 12 2m1 10.59 3.7 2.14-1 1.73L11 13.45V7h2z" />,
    graduation: <path fill="currentColor" d="m2 9 10-5 10 5-10 5zm5 3.5v4.2c3.1 2.1 6.9 2.1 10 0v-4.2l-5 2.5zM20 10v6h-2v-5z" />,
    chevron: <path fill="currentColor" d="m6.7 8.3 5.3 5.3 5.3-5.3L19 10l-7 7-7-7z" />,
    rotate: <path fill="currentColor" d="M19.8 8.2A8.96 8.96 0 0 0 4.4 6.5L2.7 4.8v5.5h5.5L6.1 8.2a6.96 6.96 0 0 1 11.9 1.1zM4.2 15.8a8.96 8.96 0 0 0 15.4 1.7l1.7 1.7v-5.5h-5.5l2.1 2.1a6.96 6.96 0 0 1-11.9-1.1z" />,
  };

  return <svg {...common}>{paths[name] || paths.spark}</svg>;
};

function App() {
  const fileInputRef = useRef(null);
  const [page, setPage] = useState("input");
  const [resumeFile, setResumeFile] = useState(null);
  const [fileError, setFileError] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [jdError, setJdError] = useState("");
  const [loading, setLoading] = useState(false);
  const [apiError, setApiError] = useState("");
  const [analysisResult, setAnalysisResult] = useState(null);
  const [openEvidence, setOpenEvidence] = useState(null);
  const [requirementsOpen, setRequirementsOpen] = useState(true);
  const [evidenceOpen, setEvidenceOpen] = useState(true);

  const handleFileSelect = (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setFileError("");
    setApiError("");
    setAnalysisResult(null);

    if (file.type !== "application/pdf") {
      setResumeFile(null);
      setFileError("Please upload a PDF file only.");
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setResumeFile(null);
      setFileError("Please upload a PDF smaller than 10 MB.");
      return;
    }

    setResumeFile(file);
  };

  const handleBrowse = () => fileInputRef.current?.click();

  const removeFile = () => {
    setResumeFile(null);
    setFileError("");
    setApiError("");
    setAnalysisResult(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const handleJobDescriptionChange = (event) => {
    const value = event.target.value;
    setJobDescription(value);
    setApiError("");
    setAnalysisResult(null);
    if (value.trim()) setJdError("");
  };

  const handleAnalyze = async () => {
    let valid = true;
    setFileError("");
    setJdError("");
    setApiError("");

    if (!resumeFile) {
      setFileError("Please upload your resume PDF.");
      valid = false;
    }

    if (!jobDescription.trim()) {
      setJdError("Please enter a job description.");
      valid = false;
    }

    if (!valid) return;

    try {
      setLoading(true);
      const result = await analyzeResume(resumeFile, jobDescription);
      console.log("API RESPONSE:", result);
      setAnalysisResult(result);
      setOpenEvidence(null);
      setPage("results");

      setTimeout(() => {
        document.getElementById("analysis-results")?.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      }, 80);
    } catch (error) {
      console.error("Analysis failed:", error);
      setApiError(error.message || "Something went wrong while analyzing.");
    } finally {
      setLoading(false);
    }
  };

  const startNewAnalysis = () => {
    setPage("input");
    setAnalysisResult(null);
    setApiError("");
    setTimeout(() => window.scrollTo({ top: 0, behavior: "smooth" }), 40);
  };

  const formatSkillName = (skill) => {
    if (!skill) return "";
    return skill.split(" ").map((word) => {
      const lower = word.toLowerCase();
      if (["api", "aws", "gcp", "ml", "ai"].includes(lower)) return word.toUpperCase();
      if (lower === "node.js") return "Node.js";
      if (lower === "express.js") return "Express.js";
      if (lower === "github") return "GitHub";
      if (lower === "rest") return "REST";
      if (lower === "opencv") return "OpenCV";
      if (lower === "pytorch") return "PyTorch";
      if (lower === "typescript") return "TypeScript";
      return word.charAt(0).toUpperCase() + word.slice(1);
    }).join(" ");
  };

  const getEvidenceClass = (strength) => {
    if (strength === "EXPLICIT") return "evidence-explicit";
    if (strength === "STRONG") return "evidence-strong";
    if (strength === "MODERATE") return "evidence-moderate";
    return "evidence-weak";
  };

  const scoreData = useMemo(() => {
    if (!analysisResult) return [];
    return [
      { label: "Skills", value: Number(analysisResult.skill_score) || 0, description: "Required and preferred skill alignment.", icon: "spark" },
      { label: "Experience", value: Number(analysisResult.experience_score) || 0, description: "Professional experience vs. the role requirement.", icon: "clock" },
      { label: "Education", value: Number(analysisResult.education_score) || 0, description: "Degree level and field compatibility.", icon: "graduation" },
      { label: "Semantic", value: Number(analysisResult.semantic_score) || 0, description: "Meaning-based evidence beyond exact matches.", icon: "spark" },
    ];
  }, [analysisResult]);

  const getScoreClass = (score) => {
    const value = Number(score) || 0;
    if (value >= 80) return "score-high";
    if (value >= 60) return "score-medium";
    if (value >= 40) return "score-low";
    return "score-critical";
  };

  const improvementData = useMemo(() => {
    if (!analysisResult) return [];
    const improvements = [];
    const requiredMissing = analysisResult.required_skills?.missing || [];
    const preferredMissing = analysisResult.preferred_skills?.missing || [];
    const experience = analysisResult.experience || {};
    const education = analysisResult.education || {};

    if (requiredMissing.length) improvements.push({
      type: "required",
      icon: "!",
      title: "Required skills",
      badge: "Required",
      description: "These skills are explicitly required but were not detected in the resume.",
      items: requiredMissing,
    });

    if (preferredMissing.length) improvements.push({
      type: "preferred",
      icon: "+",
      title: "Preferred skills",
      badge: "Preferred",
      description: "Adding these preferred skills could strengthen the match.",
      items: preferredMissing,
    });

    if (Number(experience.required_years || 0) > 0 && !experience.satisfied) improvements.push({
      type: "experience",
      icon: "clock",
      title: "Professional experience",
      badge: "Requirement",
      description: "The detected professional experience does not currently satisfy the job requirement.",
      items: [`Required: ${experience.required_years} years`, `Detected: ${experience.candidate_years || 0} years`],
    });

    if (education?.satisfied === false) improvements.push({
      type: "education",
      icon: "graduation",
      title: "Education requirements",
      badge: "Requirement",
      description: "Review the required degree level and field for this role.",
      items: ["Check the required degree level and field."],
    });

    return improvements;
  }, [analysisResult]);

  const getRequirementText = (group) => {
    const operator = group.group_operator || group.operator;
    const skills = group.group_skills || group.skills || [];
    if (operator === "OR") return skills.map(formatSkillName).join(" OR ");
    return formatSkillName(group.skill || group.required_skill || skills[0] || "");
  };

  const allRequirements = [
    ...(analysisResult?.required_skill_groups || []),
    ...(analysisResult?.preferred_skill_groups || []),
  ];

  useEffect(() => {
    const nodes = document.querySelectorAll(".reveal-on-scroll");
    if (!("IntersectionObserver" in window)) {
      nodes.forEach((node) => node.classList.add("is-visible"));
      return;
    }
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.08 });
    nodes.forEach((node) => observer.observe(node));
    return () => observer.disconnect();
  }, [analysisResult, page]);

  return (
    <div className="app">
      <header className="navbar">
        <button className="brand" type="button" onClick={page === "results" ? startNewAnalysis : undefined}>
          <span className="brand-icon"><Icon name="file" size={21} /></span>
          <span className="brand-copy">
            <strong>Resume Intelligence</strong>
            <small>NLP Resume &amp; JD Matcher</small>
          </span>
        </button>
      </header>

      {page === "input" ? (
        <main className="main-content input-page">
          <section className="hero">
            <p className="eyebrow">NLP RESUME ANALYZER</p>
            <h1>Understand how your resume <span>matches a job.</span></h1>
            <p className="hero-description">
              Compare your resume with a job description using skills, experience,
              education, and semantic evidence.
            </p>
          </section>

          <section className="analyzer-card">
            <div className="input-grid">
              <div className="upload-section">
                <div className="label-row">
                  <label className="section-label"><Icon name="file" size={15} /> Resume</label>
                  <span className="label-hint">PDF only · max 10 MB</span>
                </div>

                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf,application/pdf"
                  onChange={handleFileSelect}
                  hidden
                />

                {!resumeFile ? (
                  <div className="upload-box">
                    <div className="upload-icon"><Icon name="upload" size={23} /></div>
                    <h3>Drop your resume here</h3>
                    <p>or browse a PDF from your device</p>
                    <button type="button" className="browse-button" onClick={handleBrowse}>
                      Choose PDF <Icon name="arrow" size={15} />
                    </button>
                  </div>
                ) : (
                  <div className="selected-file">
                    <div className="file-icon"><Icon name="file" size={22} /></div>
                    <div className="file-details">
                      <strong>{resumeFile.name}</strong>
                      <span><Icon name="check" size={12} /> PDF uploaded · {(resumeFile.size / 1024 / 1024).toFixed(2)} MB</span>
                    </div>
                    <button type="button" className="remove-file" onClick={removeFile}>
                      <Icon name="x" size={15} /> Remove
                    </button>
                  </div>
                )}

                {fileError && <p className="field-error">{fileError}</p>}
              </div>

              <div className="jd-section">
                <div className="label-row">
                  <label className="section-label"><Icon name="briefcase" size={15} /> Job Description</label>
                  <span className="label-hint">{jobDescription.length} characters</span>
                </div>
                <textarea
                  className="jd-input"
                  placeholder="Paste the complete job description here..."
                  value={jobDescription}
                  onChange={handleJobDescriptionChange}
                />
                <div className="input-footer">
                  <span>Include the full role description for a more useful analysis.</span>
                </div>
                {jdError && <p className="field-error">{jdError}</p>}
              </div>
            </div>

            {apiError && <div className="api-error">{apiError}</div>}

            <button type="button" className="analyze-button" onClick={handleAnalyze} disabled={loading}>
              {loading ? (
                <>Analyzing <span className="spinner" /></>
              ) : (
                <>Analyze Resume <Icon name="arrow" size={17} /></>
              )}
            </button>
          </section>

          <div className="input-trust">
            <span><Icon name="check" size={13} /> Skills</span>
            <span><Icon name="check" size={13} /> Experience</span>
            <span><Icon name="check" size={13} /> Education</span>
            <span><Icon name="check" size={13} /> Semantic evidence</span>
          </div>
        </main>
      ) : (
        <main className="results-page" id="analysis-results">
          <section className="results-header reveal-on-scroll">
            <div className="analysis-complete-badge">ANALYSIS COMPLETE</div>
            <h1>Your Resume Analysis</h1>
            <p>Here is how your resume aligns with the job description.</p>
          </section>

          <section className="top-analysis reveal-on-scroll">
            <div className="score-hero">
              <div
                className="score-ring"
                style={{
                  "--score-angle": `${Math.min(Math.max(Number(analysisResult.overall_match_score) || 0, 0), 100) * 3.6}deg`,
                }}
              >
                <div className="score-ring-inner">
                  <strong>{analysisResult.overall_match_score}%</strong>
                  <span>OVERALL MATCH</span>
                </div>
              </div>
              <div className="score-hero-copy">
                <span className="mini-label">OVERALL MATCH SCORE</span>
                <h2>Resume fit for this role</h2>
                <p>Combined from skills, experience, education, and semantic evidence.</p>
              </div>
            </div>

            <div className={`verdict ${analysisResult.eligibility ? "verdict-good" : "verdict-bad"}`}>
              <div className="verdict-icon">
                <Icon name={analysisResult.eligibility ? "check" : "x"} size={19} />
              </div>
              <div>
                <span className="mini-label">FINAL VERDICT</span>
                <strong>{analysisResult.eligibility ? "Eligible" : "Not Eligible"}</strong>
                <p>
                  {analysisResult.eligibility
                    ? "All required matching conditions are satisfied."
                    : "One or more required matching conditions need attention."}
                </p>
              </div>
            </div>
          </section>

          <section className="score-breakdown-card reveal-on-scroll">
            <div className="section-heading">
              <div>
                <span className="mini-label">SCORE DETAILS</span>
                <h2>Match Breakdown</h2>
                <p>How each analysis component contributes to the result.</p>
              </div>
            </div>

            <div className="score-summary-grid">
              {scoreData.map((item) => (
                <div className="score-summary" key={item.label}>
                  <div className="score-summary-top">
                    <span className="metric-icon"><Icon name={item.icon} size={15} /></span>
                    <span>{item.label}</span>
                    <strong className={getScoreClass(item.value)}>{item.value}%</strong>
                  </div>
                  <div className="score-progress">
                    <div className={`score-progress-fill ${getScoreClass(item.value)}`} style={{ width: `${Math.min(Math.max(item.value, 0), 100)}%` }} />
                  </div>
                  <p>{item.description}</p>
                </div>
              ))}
            </div>
          </section>

          <section className="skills-columns reveal-on-scroll">
            <div className="result-card skill-card">
              <div className="card-heading-row">
                <div>
                  <span className="mini-label">CORE REQUIREMENTS</span>
                  <h2>Required Skills</h2>
                </div>
                <strong className="coverage-value">{analysisResult.required_skill_coverage}%</strong>
              </div>
              <p>Skills explicitly required by the job description.</p>
              <div className="skill-list">
                {analysisResult.required_skills?.matched?.map((skill) => (
                  <span className="skill-chip matched" key={`required-matched-${skill}`}><Icon name="check" size={12} /> {formatSkillName(skill)}</span>
                ))}
                {analysisResult.required_skills?.missing?.map((skill) => (
                  <span className="skill-chip missing" key={`required-missing-${skill}`}><Icon name="x" size={12} /> {formatSkillName(skill)}</span>
                ))}
              </div>
              <div className="card-footer-note">
                {analysisResult.required_skills?.matched?.length || 0} of {(analysisResult.required_skills?.matched?.length || 0) + (analysisResult.required_skills?.missing?.length || 0)} detected
              </div>
            </div>

            <div className="result-card skill-card">
              <div className="card-heading-row">
                <div>
                  <span className="mini-label">ADDITIONAL VALUE</span>
                  <h2>Preferred Skills</h2>
                </div>
              </div>
              <p>Additional skills that can strengthen the match.</p>
              <div className="skill-list">
                {analysisResult.preferred_skills?.matched?.map((skill) => (
                  <span className="skill-chip matched" key={`preferred-matched-${skill}`}><Icon name="check" size={12} /> {formatSkillName(skill)}</span>
                ))}
                {analysisResult.preferred_skills?.missing?.map((skill) => (
                  <span className="skill-chip missing" key={`preferred-missing-${skill}`}><Icon name="x" size={12} /> {formatSkillName(skill)}</span>
                ))}
              </div>
              <div className="card-footer-note">
                {analysisResult.preferred_skills?.matched?.length || 0} matched · {(analysisResult.preferred_skills?.missing?.length || 0)} missing
              </div>
            </div>
          </section>

          <section className="improvement-card reveal-on-scroll">
            <div className="improvement-header">
              <div className="improvement-title">
                <span className="improvement-icon"><Icon name="spark" size={17} /></span>
                <div>
                  <span className="mini-label">ACTIONABLE INSIGHTS</span>
                  <h2>What You Can Improve</h2>
                  <p>Focus on these areas to strengthen your match for this role.</p>
                </div>
              </div>
              <span className="improvement-count">{improvementData.length}</span>
            </div>

            {improvementData.length === 0 ? (
              <div className="improvement-success">
                <span><Icon name="check" size={18} /></span>
                <div><strong>No major gaps detected</strong><p>The analysis did not identify missing required conditions.</p></div>
              </div>
            ) : (
              <div className="improvement-grid">
                {improvementData.map((item, index) => (
                  <div className={`improvement-item ${item.type}`} key={`${item.type}-${index}`}>
                    <div className="improvement-item-icon">
                      {item.icon === "clock" ? <Icon name="clock" size={16} /> : item.icon === "graduation" ? <Icon name="graduation" size={16} /> : item.icon}
                    </div>
                    <div>
                      <div className="improvement-item-heading">
                        <h3>{item.title}</h3><span>{item.badge}</span>
                      </div>
                      <p>{item.description}</p>
                      <div className="improvement-tags">
                        {item.items.map((value, itemIndex) => (
                          <span key={`${item.type}-${itemIndex}`}>{item.type === "experience" ? value : formatSkillName(value)}</span>
                        ))}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>

          <section className="analysis-columns reveal-on-scroll">
            <div className="collapsible-card">
              <button className="collapse-header" type="button" onClick={() => setRequirementsOpen((v) => !v)} aria-expanded={requirementsOpen}>
                <div><span className="mini-label">LOGICAL MATCHING</span><h2>Requirement Analysis</h2><p>Logical requirement groups detected from the job description.</p></div>
                <span className={`chevron ${requirementsOpen ? "open" : ""}`}><Icon name="chevron" size={17} /></span>
              </button>

              {requirementsOpen && (
                <div className="collapse-content">
                  {allRequirements.map((group, index) => {
                    const isPreferred = (analysisResult.preferred_skill_groups || []).includes(group);
                    return (
                      <div className="requirement-row" key={`req-${index}`}>
                        <div className="requirement-main">
                          <span className={`status-dot ${group.satisfied ? "ok" : "bad"}`}><Icon name={group.satisfied ? "check" : "x"} size={11} /></span>
                          <span>{getRequirementText(group)}</span>
                          {isPreferred && <small>Preferred</small>}
                        </div>
                        <span className={`requirement-status ${group.satisfied ? "satisfied" : "unsatisfied"}`}>
                          {group.satisfied ? "Satisfied" : "Missing"}
                        </span>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            <div className="collapsible-card">
              <button className="collapse-header" type="button" onClick={() => setEvidenceOpen((v) => !v)} aria-expanded={evidenceOpen}>
                <div><span className="mini-label">NLP TRACEABILITY</span><h2>Requirement Evidence</h2><p>Evidence found in your resume for each requirement.</p></div>
                <div className="header-actions"><span className="evidence-count">{analysisResult.requirement_evidence?.length || 0}</span><span className={`chevron ${evidenceOpen ? "open" : ""}`}><Icon name="chevron" size={17} /></span></div>
              </button>

              {evidenceOpen && (
                <div className="collapse-content evidence-content-list">
                  {analysisResult.requirement_evidence?.map((evidence, index) => {
                    const strength = evidence.evidence_strength || "WEAK";
                    const skill = evidence.skill || evidence.required_skill || "Unknown requirement";
                    const semanticScore = evidence.semantic_score;
                    const isOpen = openEvidence === index;

                    return (
                      <div className={`evidence-item ${isOpen ? "expanded" : ""}`} key={`evidence-${index}`}>
                        <button type="button" className="evidence-item-trigger" onClick={() => setOpenEvidence(isOpen ? null : index)} aria-expanded={isOpen}>
                          <div className="evidence-item-left">
                            <span className={`evidence-status-icon ${strength === "EXPLICIT" ? "good" : "soft"}`}>
                              <Icon name={strength === "EXPLICIT" ? "check" : "spark"} size={13} />
                            </span>
                            <div><strong>{formatSkillName(skill)}</strong>{evidence.importance && <small>{evidence.importance}</small>}</div>
                          </div>
                          <span className={`evidence-badge ${getEvidenceClass(strength)}`}>
                            {strength === "EXPLICIT" ? "EXPLICIT" : strength}
                          </span>
                        </button>

                        {isOpen && (
                          <div className="evidence-detail">
                            {evidence.requirement_text && (
                              <div className="detail-block"><span>Requirement</span><p>{evidence.requirement_text}</p></div>
                            )}
                            <div className="detail-block resume-evidence">
                              <span>Resume Evidence</span>
                              <p>{evidence.evidence || "No strong evidence found in resume."}</p>
                            </div>
                            <div className="evidence-meta">
                              {evidence.matched_alias && <span>Matched alias: <strong>{evidence.matched_alias}</strong></span>}
                              {strength !== "EXPLICIT" && semanticScore !== undefined && semanticScore !== null && (
                                <span>Semantic similarity: <strong>{(Number(semanticScore) * 100).toFixed(1)}%</strong></span>
                              )}
                              {evidence.evidence_status && <span>Status: <strong>{evidence.evidence_status.replaceAll("_", " ")}</strong></span>}
                            </div>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </section>

          <section className="details-grid reveal-on-scroll">
            <div className="result-card detail-card">
              <div className="detail-card-title"><span className="metric-icon"><Icon name="clock" size={16} /></span><div><span className="mini-label">EXPERIENCE</span><h2>Experience Analysis</h2></div></div>
              <div className="info-grid">
                <div><span>Candidate</span><strong>{analysisResult.experience?.candidate_years ?? 0} years</strong></div>
                <div><span>Required</span><strong>{analysisResult.experience?.required_years ?? 0} years</strong></div>
                <div><span>Evidence source</span><strong>{analysisResult.experience?.source || "None"}</strong></div>
                <div><span>Status</span><strong className={analysisResult.experience?.satisfied ? "status-positive" : "status-negative"}>{analysisResult.experience?.satisfied ? "Satisfied" : "Not Satisfied"}</strong></div>
              </div>
            </div>

            <div className="result-card detail-card">
              <div className="detail-card-title"><span className="metric-icon"><Icon name="graduation" size={16} /></span><div><span className="mini-label">EDUCATION</span><h2>Education Analysis</h2></div></div>
              <div className="info-grid">
                <div><span>Degree level</span><strong>{analysisResult.education?.candidate_levels?.join(", ") || "Not detected"}</strong></div>
                <div><span>Field</span><strong>{analysisResult.education?.candidate_fields?.join(", ") || "Not detected"}</strong></div>
                <div><span>Institution</span><strong>{analysisResult.education?.institution || "Not detected"}</strong></div>
                <div><span>Status</span><strong className={analysisResult.education?.satisfied ? "status-positive" : "status-negative"}>{analysisResult.education?.satisfied ? "Satisfied" : "Not Satisfied"}</strong></div>
              </div>
            </div>
          </section>

          <section className="result-card sections-card reveal-on-scroll">
            <div className="card-heading-row">
              <div><span className="mini-label">RESUME STRUCTURE</span><h2>Resume Sections Detected</h2></div>
            </div>
            <div className="section-list">
              {analysisResult.sections_detected?.map((section) => <span className="section-chip" key={section}>{formatSkillName(section)}</span>)}
            </div>
          </section>

          <footer className="results-footer reveal-on-scroll">
            <div><span className="footer-logo"><Icon name="file" size={16} /></span><strong>Resume Intelligence</strong></div>
            <span>NLP Resume &amp; JD Matcher</span>
          </footer>
        </main>
      )}
    </div>
  );
}

export default App;
