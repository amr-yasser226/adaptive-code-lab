# ACCL – Adaptive Collaborative Coding Lab  
**CSAI 203 – Phase 2: Software Requirements Specification (SRS)**  

---

## Team Members
| Name                | ID         |
|---------------------|------------|
| Amr Yasser          | 202301043  |
| Omar Hazem          | 202300800​  |
| Omar Darwish        | 202301146  |
| Hady Saeed          | 202301707  |
| Abdelrahman Mohamed | 202301645  |

*Representative: Amr Yasser Anwar – 202301043*

---

## Project Overview
ACCL is a **real-time collaborative coding platform** with adaptive learning paths and instructor oversight.  
Built with **Flask (backend) + HTML (frontend)** and will follow the **MVC** pattern.

---

## Phase 2 Deliverable – SRS  

**[SRS PDF (Official Submission)](./docs/CSAI203_SRS_Team18_202301043.pdf)**  
*Markdown source for editing:* [`CSAI203_SRS_Team18_202301043.md`](./docs/CSAI203_SRS_Team18_202301043.md)

The document follows the **exact outline** (10–15 pages, cover page, 1.5 line spacing, Times New Roman/Arial 12 pt) and contains:

* **Introduction** – purpose, scope, definitions, references  
* **Overall Description** – perspective, functions, users, environment, constraints, assumptions  
* **Specific Requirements** – ≥10 functional, ≥2 non-functional, external interfaces  
* **Use-Case Model** – **3 separate diagrams** + IEEE descriptions  
* **Domain Model** – **2 conceptual class diagrams** + class descriptions  
* **Appendices** – data dictionary, glossary  

---

## Diagrams (All embedded in the PDF)

| Figure | What it Shows | Link |
|--------|---------------|------|
| **Student Use-Case** | Login, join session, edit code, view progress, request hints (`<<include>>` auth, `<<extend>>` AI hints) | [student_use_case_diagram.png](./docs/figures/student_use_case_diagram.png) |
| **Instructor Use-Case** | Create session, monitor code, grade, manage paths, reports (multiplicity) | [instructor_use_case.png](./docs/figures/instructor_use_case.png) |
| **Admin Use-Case** | Manage users, backups, server config, logs (`<<extend>>` emergency) | [admin_use_case.png](./docs/figures/admin_use_case.png) |
| **Automation Use-Case** | Auto-save, code analysis, difficulty adjustment, notifications | [automation_use_case.png](./docs/figures/automation_use_case.png) |
| **Conceptual Class #1** | `User`, `CodeSession`, `LearningPath`, `Exercise`, `Progress` – associations & multiplicity | [class_diagram_1.png](./docs/figures/class_diagram_1.png) |
| **Conceptual Class #2** | `RealtimeEditor`, `ChangeLog`, `ConflictResolver`, `WebSocketConnection` – aggregation/composition | [class_diagram_2.png](./docs/figures/class_diagram_2.png) |

---

## Repository Structure (Phase 2)

```
phase-2-srs/
├── docs/
│   ├── CSAI203_SRS_Team18_202301043.pdf
│   ├── CSAI203_SRS_Team18_202301043.md
│   └── figures/  (all PNGs above)
├── src/          (empty – code in Phase 4)
├── tests/        (empty – tests in Phase 4)
├── deployment/   (empty – deployment in Phase 5)
├── LICENSE       (project-wide)
├── README.md     (project-wide – from main)
└── README-phase2.md   ← **THIS FILE**
```

---

## Setup & Running (Phase 2)

> **No code yet.** Implementation starts in **Phase 4**.  
> See the **[SRS PDF](./docs/CSAI203_SRS_Team18_202301043.pdf)** for full requirements.

---

## Next Steps
1. Merge `phase-2-srs` → `main` after TA review.  
2. Start **Phase 3 – Design Document** (sequence diagrams, detailed class diagram, MVC mapping, wireframes).