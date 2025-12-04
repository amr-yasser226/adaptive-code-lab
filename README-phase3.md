# ACCL – Adaptive Collaborative Coding Lab  
**CSAI 203 – Phase 3: Software Design Document (SDD)**  

---

## Team Members
| Name                | ID         |
|---------------------|------------|
| Amr Yasser          | 202301043  |
| Omar Hazem          | 202300800  |
| Omar Darwish        | 202301146  |
| Hady Saeed          | 202301707  |
| Abdelrahman Mohamed | 202301645  |

*Representative: Amr Yasser Anwar – 202301043*

---

## Project Overview
ACCL is a **real-time collaborative coding platform** with adaptive learning paths and instructor oversight.  
Built with **Flask (backend) + HTML (frontend)** and follows the **MVC** pattern.

---

## Phase 3 Deliverable – Software Design Document (SDD)

**[SDD PDF (Official Submission)](./docs/design/CSAI203_Design_Team18_202301043.pdf)**  
**[SDD Markdown Source](./docs/design/CSAI203_Design_Team18_202301043.md)**  
**[Interactive Design Documentation](https://amr-yasser226.github.io/adaptive-code-lab/)**

The document follows the required structure and contains:

* **Introduction** – purpose, scope, intended audience, document overview
* **System Overview** – brief description, design goals & constraints
* **Architectural Design** – system architecture diagram, architectural style discussion, technology stack
* **Detailed Design** – MVC pattern implementation, UML diagrams, UI/UX wireframes, data design
* **Conclusion** – summary of design decisions and rationale

---

## Design Artifacts

### 1. System Architecture
| Artifact | Description | Link |
|----------|-------------|------|
| **System Architecture Diagram** | High-level component interaction and layered architecture | [View SVG](https://amr-yasser226.github.io/adaptive-code-lab/design/architecture/system_architecture.svg) |

### 2. UML Diagrams

#### Class Diagram
| Artifact | Description | Link |
|----------|-------------|------|
| **UML Class Diagram** | Detailed domain model with Model, View, Controller, Repository, and Service layers | [View SVG](https://amr-yasser226.github.io/adaptive-code-lab/design/class_diagram/uml_class_diagram.svg) |

#### Sequence Diagrams
| Artifact | Description | Link |
|----------|-------------|------|
| **Submit Assignment** | Student code submission workflow with sandbox execution | [View SVG](https://amr-yasser226.github.io/adaptive-code-lab/design/sequence/sequence_submit_assignment.svg) |
| **Manual Regrade** | Instructor-initiated regrade process | [View SVG](https://amr-yasser226.github.io/adaptive-code-lab/design/sequence/sequence_manual_regrade.svg) |
| **Batch Plagiarism Detection** | Similarity detection across multiple submissions | [View SVG](https://amr-yasser226.github.io/adaptive-code-lab/design/sequence/sequence_batch_plagiarism_detection.svg) |
| **AI Hint Request** | Progressive hint generation workflow | [View SVG](https://amr-yasser226.github.io/adaptive-code-lab/design/sequence/sequence_ai_hint_request.svg) |
| **Peer Review Submission** | Student peer review assignment workflow | [View SVG](https://amr-yasser226.github.io/adaptive-code-lab/design/sequence/sequence_peer_review_submission.svg) |
| **Student Course Enrollment** | Course enrollment and assignment access | [View SVG](https://amr-yasser226.github.io/adaptive-code-lab/design/sequence/sequence_student_course_enrollment.svg) |
| **MVC Interaction** | Request-response flow through MVC layers | [View SVG](https://amr-yasser226.github.io/adaptive-code-lab/design/sequence/sequence_mvc_interaction.svg) |

### 3. Database Design
| Artifact | Description | Link |
|----------|-------------|------|
| **ER Diagram** | Entity-Relationship model showing database schema | [View SVG](https://amr-yasser226.github.io/adaptive-code-lab/design/er/er_diagrams.svg) |
| **Data Dictionary** | Comprehensive data definitions and constraints | [View PDF](https://github.com/amr-yasser226/adaptive-code-lab/blob/feature/sdd/docs/design/reference/data_dictionary.pdf) |

### 4. UI/UX Wireframes

All wireframes available in desktop, mobile, and merged responsive versions.

#### Assignment Dashboard
| Version | Link |
|---------|------|
| Desktop v1 | [View SVG](https://amr-yasser226.github.io/adaptive-code-lab/design/ui_ux/wireframe_assignment_dashboard_desktop.svg) |
| Desktop v2 | [View SVG](https://amr-yasser226.github.io/adaptive-code-lab/design/ui_ux/wireframe_assignment_dashboard_desktop_v2.svg) |
| Mobile v1 | [View SVG](https://amr-yasser226.github.io/adaptive-code-lab/design/ui_ux/wireframe_assignment_dashboard_mobile.svg) |
| Mobile v2 | [View SVG](https://amr-yasser226.github.io/adaptive-code-lab/design/ui_ux/wireframe_assignment_dashboard_mobile_v2.svg) |

#### Code Editor
| Version | Link |
|---------|------|
| Desktop v1-v4 | [v1](https://amr-yasser226.github.io/adaptive-code-lab/design/ui_ux/wireframe_code_editor_desktop.svg) • [v2](https://amr-yasser226.github.io/adaptive-code-lab/design/ui_ux/wireframe_code_editor_desktop_v2.svg) • [v3](https://amr-yasser226.github.io/adaptive-code-lab/design/ui_ux/wireframe_code_editor_desktop_v3.svg) • [v4](https://amr-yasser226.github.io/adaptive-code-lab/design/ui_ux/wireframe_code_editor_desktop_v4.svg) |
| Mobile v1-v2 | [v1](https://amr-yasser226.github.io/adaptive-code-lab/design/ui_ux/wireframe_code_editor_mobile.svg) • [v2](https://amr-yasser226.github.io/adaptive-code-lab/design/ui_ux/wireframe_code_editor_mobile_v2.svg) |
| Merged v1-v4 | [v1](https://amr-yasser226.github.io/adaptive-code-lab/design/ui_ux/wireframe_code_editor_merged.svg) • [v2](https://amr-yasser226.github.io/adaptive-code-lab/design/ui_ux/wireframe_code_editor_merged_v2.svg) • [v3](https://amr-yasser226.github.io/adaptive-code-lab/design/ui_ux/wireframe_code_editor_merged_v3.svg) • [v4](https://amr-yasser226.github.io/adaptive-code-lab/design/ui_ux/wireframe_code_editor_merged_v4.svg) |

#### Progress Feedback
| Version | Link |
|---------|------|
| Desktop v1 | [View SVG](https://amr-yasser226.github.io/adaptive-code-lab/design/ui_ux/wireframe_progress_feedback_desktop.svg) |
| Desktop v2 | [View SVG](https://amr-yasser226.github.io/adaptive-code-lab/design/ui_ux/wireframe_progress_feedback_desktop_v2.svg) |
| Mobile v1 | [View SVG](https://amr-yasser226.github.io/adaptive-code-lab/design/ui_ux/wireframe_progress_feedback_mobile.svg) |
| Mobile v2 | [View SVG](https://amr-yasser226.github.io/adaptive-code-lab/design/ui_ux/wireframe_progress_feedback_mobile_v2.svg) |

#### Similarity Dashboard
| Version | Link |
|---------|------|
| Desktop v1 | [View SVG](https://amr-yasser226.github.io/adaptive-code-lab/design/ui_ux/wireframe_similarity_dashboard_desktop.svg) |
| Desktop v2 | [View SVG](https://amr-yasser226.github.io/adaptive-code-lab/design/ui_ux/wireframe_similarity_dashboard_desktop_v2.svg) |
| Mobile v1 | [View SVG](https://amr-yasser226.github.io/adaptive-code-lab/design/ui_ux/wireframe_similarity_dashboard_mobile.svg) |
| Mobile v2 | [View SVG](https://amr-yasser226.github.io/adaptive-code-lab/design/ui_ux/wireframe_similarity_dashboard_mobile_v2.svg) |

#### Submission History
| Version | Link |
|---------|------|
| Desktop v1 | [View SVG](https://amr-yasser226.github.io/adaptive-code-lab/design/ui_ux/wireframe_submission_history_desktop.svg) |
| Desktop v2 | [View SVG](https://amr-yasser226.github.io/adaptive-code-lab/design/ui_ux/wireframe_submission_history_desktop_v2.svg) |
| Mobile v1 | [View SVG](https://amr-yasser226.github.io/adaptive-code-lab/design/ui_ux/wireframe_submission_history_mobile.svg) |
| Mobile v2 | [View SVG](https://amr-yasser226.github.io/adaptive-code-lab/design/ui_ux/wireframe_submission_history_mobile_v2.svg) |

---

## Design Patterns & Architecture Decisions

### MVC Pattern Implementation
- **Model Layer:** SQLAlchemy models, Repository pattern for data access
- **View Layer:** Jinja2 templates with Bootstrap 5 styling
- **Controller Layer:** Flask Blueprints organizing routes by feature domain
- **Service Layer:** Business logic separation from controllers

### Key Architectural Choices
1. **Monolithic Architecture** – Single Flask application for Phase-4 simplicity
2. **Background Workers** – Redis + RQ/Celery for async sandbox execution
3. **Docker Sandboxing** – Isolated, resource-limited code execution environment
4. **Repository Pattern** – Clean data access abstraction
5. **Factory Pattern** – App factory for flexible Flask initialization
6. **Singleton Pattern** – Shared service instances (AI adapters, cache)

### Technology Stack
- **Backend:** Python 3.x, Flask, SQLAlchemy, Redis
- **Frontend:** Jinja2, Bootstrap 5, Vanilla JS
- **Database:** SQLite (Phase-4), with migration path to PostgreSQL
- **Execution:** Docker containers with security restrictions
- **AI/Analysis:** External API adapters with caching and fallback
- **Testing:** pytest, coverage, integration test suite
- **CI/CD:** GitHub Actions

---

## Repository Structure (Phase 3)

```
adaptive-code-lab/
├── docs/
│   ├── CSAI203_SRS_Team18_202301043.md          # Phase 2 - Requirements
│   ├── CSAI203_SRS_Team18_202301043.pdf
│   ├── design/
│   │   ├── CSAI203_Design_Team18_202301043.md   # Phase 3 - Design Doc
│   │   ├── CSAI203_Design_Team18_202301043.pdf
│   │   ├── CSAI203_Design_Team18_202301043.docx
│   │   ├── architecture/
│   │   │   └── system_architecture.svg
│   │   ├── class_diagram/
│   │   │   └── uml_class_diagram.svg
│   │   ├── er/
│   │   │   └── er_diagrams.svg
│   │   ├── sequence/                            # 7 sequence diagrams
│   │   │   ├── sequence_submit_assignment.svg
│   │   │   ├── sequence_manual_regrade.svg
│   │   │   ├── sequence_batch_plagiarism_detection.svg
│   │   │   ├── sequence_ai_hint_request.svg
│   │   │   ├── sequence_peer_review_submission.svg
│   │   │   ├── sequence_student_course_enrollment.svg
│   │   │   └── sequence_mvc_interaction.svg
│   │   ├── ui_ux/                               # 30 wireframes (desktop/mobile)
│   │   │   └── wireframe_*.svg
│   │   └── reference/
│   │       ├── data_dictionary.md
│   │       └── data_dictionary.pdf
│   ├── figures/                                  # Phase 2 use-case diagrams
│   │   ├── student_use_case_diagram.png
│   │   ├── instructor_use_case.png
│   │   ├── admin_use_case.png
│   │   ├── automation_use_case.png
│   │   ├── class_diagram_1.png
│   │   └── class_diagram_2.png
│   └── index.html                                # Interactive design viewer
├── src/                                          # (empty – Phase 4)
├── tests/                                        # (empty – Phase 4)
├── deployment/                                   # (empty – Phase 5)
├── LICENSE
├── README.md                                     # Project-wide overview
├── README-phase2.md                              # Phase 2 documentation
└── README-phase3.md                              # THIS FILE
```

---

## Viewing the Design Documentation

### Option 1: GitHub Pages (Recommended)
Visit the **[Interactive Design Documentation](https://amr-yasser226.github.io/adaptive-code-lab/)** to browse all diagrams with navigation and zoom capabilities.

### Option 2: Local Viewing
1. Clone the repository:
   ```bash
   git clone https://github.com/amr-yasser226/adaptive-code-lab.git
   cd adaptive-code-lab
   ```

2. Open `docs/index.html` in your browser to view all diagrams locally

3. View individual SVG files directly from the `docs/design/` subdirectories

### Option 3: PDF Documents
Download the complete design document:
- [CSAI203_Design_Team18_202301043.pdf](./docs/design/CSAI203_Design_Team18_202301043.pdf)
- [Data Dictionary PDF](./docs/design/reference/data_dictionary.pdf)

---

## Design Document Highlights

### Complete Coverage
✅ System architecture with component interaction  
✅ MVC pattern implementation and mapping  
✅ 7 sequence diagrams covering critical workflows  
✅ Detailed class diagram with all layers  
✅ 30 UI/UX wireframes (desktop, mobile, merged)  
✅ ER diagram with normalized schema  
✅ Data dictionary with field definitions  
✅ Technology stack justification  
✅ Design pattern documentation (MVC, Repository, Factory, Singleton)  

### Design Decisions Documented
- Monolithic vs. microservices trade-offs
- SQLite for Phase-4, migration path noted
- Docker sandboxing for security
- Background worker separation for performance
- AI adapter pattern for extensibility
- Repository pattern for testability

---

## Next Steps

1. ✅ **Phase 2 Complete** – Requirements specification
2. ✅ **Phase 3 Complete** – Design document and artifacts
3. **Phase 4 (Next)** – Core functionality prototype implementation
   - Implement Flask application with MVC structure
   - Set up SQLAlchemy models and repositories
   - Create basic UI with Jinja2 templates
   - Implement sandbox execution
   - Add authentication and authorization
   - Write unit and integration tests
4. **Phase 5** – Deployment and final presentation

---

## Team Contributions

All team members contributed to:
- System architecture design
- Sequence diagram creation
- Wireframe design iterations
- Database schema design
- Document writing and review
- Diagram refinement and documentation

---

## Feedback & Questions

For questions about the design or implementation approach, contact:

**Team Representative:** Amr Yasser Anwar  
**Email:** s-amr.anwar@zewailcity.edu.eg  
**Student ID:** 202301043

---

## License

This project is part of CSAI 203 coursework at Zewail City University.  
See [LICENSE](./LICENSE) for details.