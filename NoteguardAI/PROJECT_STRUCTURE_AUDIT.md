# NoteGuard AI — Project Structure Audit

**Date**: August 16, 2026  
**Auditor**: Senior Machine Learning Engineer & System Architect  
**Audit Mode**: Read-Only Forensic Analysis  

---

## 1. Complete Folder Tree (Top-Level Architecture)

```
d:\PROJECTS\notegurd\NoteguardAI\
├── .env                              # Root environment configuration (AI_PROVIDER, DB, Thresholds)
├── .gitignore                        # Gitignore (excludes datasets, models, checkpoints)
├── alembic.ini                       # Database migration configuration
├── api_contract.md                   # API V1 Specification & Schemas
├── architecture_report.md            # System Architecture Overview
├── audit_env.py                      # Environment validation script
├── cleaned_dataset_manifest.json     # Cleaned dataset image catalog
├── cleaning_report.md                # Phase 2 dataset cleaning report
├── CORE_AI_VALIDATION_REPORT.md      # Core validation sprint metrics
├── database_design.md                # PostgreSQL relational database schema design
├── dataset_inspection_report.json    # Phase 1 dataset inspection metadata
├── dataset_inspection_report.md      # Comprehensive dataset inspection report
├── dataset_manifest.json             # Manifest of 2,840 ingested images
├── dataset_report.md                 # Dataset statistics summary
├── dataset_audit.json                # Forensic filesystem analysis of dataset splits
├── docker-compose.yml                # Container orchestration (PostgreSQL, Redis, MinIO)
├── high_level_design.md              # System HLD documentation
├── low_level_design.md               # System LLD documentation
├── project_understanding.md          # Domain understanding & functional objectives
├── ui_ux_design.md                   # UI/UX design specifications
├── verify_split.py                   # Split verification utility
│
├── backend/                          # FastAPI Backend Application
│   ├── alembic/                      # Database migrations
│   │   ├── versions/                 # Revision scripts (initial, nullable user_id, auth refactor)
│   │   └── env.py                    # Alembic runtime environment
│   ├── src/                          # Application source code
│   │   ├── config.py                 # Pydantic Settings and environment mappings
│   │   ├── main.py                   # FastAPI entrypoint, middleware, startup hooks
│   │   ├── core/                     # Cross-cutting foundational modules
│   │   │   ├── database/             # SQLAlchemy connection & Base model
│   │   │   │   ├── base_model.py     # Timestamped declarative base
│   │   │   │   └── connection.py     # Engine, SessionLocal, get_db dependency
│   │   │   ├── security/             # Security, Auth, Rate Limiting
│   │   │   │   ├── password.py       # Passlib / bcrypt hashing
│   │   │   │   ├── rate_limit.py     # In-memory sliding-window rate limiters
│   │   │   │   └── token.py          # JWT creation, decoding, token validation
│   │   │   └── storage.py            # MinIO / S3 object storage client
│   │   └── modules/                  # Domain-driven feature modules
│   │       ├── ai_engine/            # CNN Inference & Decision Engine
│   │       │   ├── decision.py       # DecisionEngine (aggregate scoring, thresholds, ₹2000 rule)
│   │       │   ├── exceptions.py     # Domain exceptions (InvalidImage, ModelLoad, etc.)
│   │       │   ├── inference.py      # AIInferenceService (thread-safe predict executor)
│   │       │   ├── loaders.py        # ModelLoader (singleton lazy loading with double-check lock)
│   │       │   ├── pipeline.py       # AIInferencePipeline (orchestrator: validate -> preprocess -> infer -> decide)
│   │       │   ├── predict.py        # Standalone prediction helper
│   │       │   ├── preprocessing.py  # ImagePreprocessor (PIL resizing, normalization, OpenCV deskew)
│   │       │   ├── router.py         # /api/v1/verify, /api/v1/history, /admin/models
│   │       │   ├── schemas.py        # VerificationResponse, DecisionState, Authenticity Pydantic models
│   │       │   ├── validation.py     # ImageValidator (magic bytes, size, resolution, aspect ratio)
│   │       │   └── training/         # ML Model Training Pipeline
│   │       │       ├── callbacks.py  # ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
│   │       │       ├── config.py     # TrainingConfig (hyperparameters, class lists, paths)
│   │       │       ├── evaluate.py   # Model evaluation helpers
│   │       │       ├── metrics.py    # Custom metrics (F1, Precision, Recall)
│   │       │       ├── model_builder.py # MobileNetV2 builder with transfer learning & fine-tuning
│   │       │       ├── predict.py    # Training prediction runner
│   │       │       ├── train.py      # Training CLI entrypoint
│   │       │       └── trainer.py    # NoteGuardModelTrainer (data generators, Stage 1/2 training)
│   │       ├── auth/                 # User Authentication & RBAC
│   │       │   ├── models.py         # User, Role, Permission, UserRefreshToken
│   │       │   ├── repositories.py   # UserRepository DB operations
│   │       │   ├── router.py         # /auth/register, /auth/login, /auth/refresh, /auth/me
│   │       │   ├── schemas.py        # UserRegisterRequest, LoginRequest, TokenResponse
│   │       │   └── services.py       # AuthService (authentication logic, token rotation)
│   │       └── verification/         # Verification Record Tracking
│   │           ├── models.py         # CurrencyVerification, VerificationResult, AIPrediction, etc.
│   │           ├── repositories.py   # VerificationRepository DB operations
│   │           ├── router.py         # Verification management endpoints
│   │           └── schemas.py        # Database entity schemas
│   ├── audit.py                      # Integration audit script
│   ├── create_db.py                  # Database creation utility
│   ├── data_leak_check.py            # SHA-256 data leakage verification script
│   ├── evaluate_models.py            # Multi-stage model evaluation script
│   ├── evaluate_phase14.py           # Phase 14 7-class denomination evaluator
│   ├── evaluate_pipelines.py         # Preprocessing pipeline comparative evaluator
│   ├── eval_experiment.py            # Phase 28 Experiment 1 evaluator
│   ├── phase15_investigator.py       # Failure analysis and error priority investigator
│   ├── phase15_report_generator.py   # Investigation report generator
│   ├── phase16_experiment.py         # Threshold sensitivity analyzer
│   ├── reconcile_data.py             # Data reconciliation and validation checker
│   ├── run_stage1.py                 # Standalone Stage 1 training script
│   ├── run_stage2.py                 # Standalone Stage 2 training script
│   ├── smoke_test.py                 # Smoke test for imports, forward pass, and config
│   ├── step1_diagnostic.py           # Decision engine diagnostic runner
│   ├── test_api.py                   # Pytest test suite for API endpoints
│   ├── test_e2e.py                   # End-to-end HTTP integration test
│   ├── test_http.py                  # Basic HTTP verification test
│   ├── test_inference.py             # Low-level inference test
│   ├── test_keras.py                 # Keras model loading test
│   ├── train_phase14.py              # Phase 14 7-class denomination trainer
│   └── verify_split.py               # Dataset split validator
│
├── dataset/                          # Currency Dataset Storage
│   ├── cleaned/                      # Deduplicated, filtered raw images and features
│   │   ├── data/                     # Cleaned currency notes (fake & real)
│   │   └── features/                 # Cleaned security feature crops (10 to 2000)
│   ├── data/                         # Original raw currency notes (13 subfolders, 2,905 images)
│   ├── Features/                     # Feature crops and historical split
│   └── split/                        # Active partition used by TrainingConfig
│       ├── train/                    # 2,495 images across 14 class folders
│       ├── val/                      # 313 images across 11 class folders (MISSING real_20, real_50, real_200!)
│       ├── test/                     # 29 images across 9 class folders (SEVERELY DEPLETED)
│       └── split_report.json         # Split metadata
│
└── frontend/                         # Migrated React.js + TypeScript + Vite SPA
    ├── public/                       # Static public assets (currency samples, logos)
    ├── src/                          # Frontend source code
    │   ├── components/               # UI components
    │   │   ├── layout/               # Layout, Navbar, Sidebar
    │   │   ├── motion/               # AnimatedCounter, ResultReveal, AnimatedPage
    │   │   ├── shared/               # BanknoteScanner, ConfidenceGauge, KPICard, UploadDropzone
    │   │   └── ui/                   # Reusable UI primitives (Button, Card, Dialog, Badge, Input, Table)
    │   ├── core/                     # API client, auth service, utilities
    │   │   ├── api/client.ts         # Axios client with interceptors
    │   │   ├── auth/auth-service.ts  # Token storage and auth state
    │   │   └── utils/cn.ts           # Classnames utility
    │   ├── pages/                    # Routed view pages
    │   │   ├── AboutPage.tsx         # System information & security feature overview
    │   │   ├── AdminPage.tsx         # Model management & admin diagnostics
    │   │   ├── AnalyticsPage.tsx     # System analytics charts
    │   │   ├── DashboardPage.tsx     # Teller/Admin KPI dashboard
    │   │   ├── HistoryPage.tsx       # Paginated verification audit logs
    │   │   ├── LandingPage.tsx       # Public landing page with live interactive demo
    │   │   ├── LoginPage.tsx         # Auth login form
    │   │   ├── LogoutPage.tsx        # Auth logout cleanup
    │   │   ├── ReportsPage.tsx       # Exportable audit reports
    │   │   ├── SettingsPage.tsx      # System threshold & user settings
    │   │   └── VerifyPage.tsx        # Primary note verification page with drag-and-drop & live results
    │   ├── styles/                   # Stylesheets
    │   │   └── globals.css           # Tailwind CSS directives & custom design system tokens
    │   ├── App.tsx                   # React Router route definitions & ThemeProvider
    │   ├── main.tsx                  # React DOM root render
    │   └── vite-env.d.ts             # Vite TypeScript type declarations
    ├── index.html                    # HTML5 entrypoint
    ├── package.json                  # Frontend dependencies and npm scripts
    ├── postcss.config.js             # PostCSS Tailwind plugins
    ├── tailwind.config.js            # Tailwind theme tokens & color definitions
    ├── tsconfig.json                 # TypeScript compiler options
    ├── tsconfig.node.json            # Node-specific TS options
    └── vite.config.ts                # Vite build & proxy configuration
```

---

## 2. Directory Purpose Analysis

| Directory Path | Architectural Purpose | Criticality |
| :--- | :--- | :--- |
| `/backend/src/modules/ai_engine` | Core AI pipeline: validation, preprocessing, model loading, CNN inference, and decision policy evaluation. | **Critical** |
| `/backend/src/modules/ai_engine/training` | Model definitions, dataset generators, callbacks, loss functions, and transfer learning routines. | **Critical** |
| `/backend/src/modules/auth` | User identity, password hashing (bcrypt), JWT generation/refresh, and RBAC enforcement. | **High** |
| `/backend/src/modules/verification` | Relational audit tracking: persisting verification requests, results, AI prediction scores, and security features. | **High** |
| `/backend/src/core/database` | SQLAlchemy async/sync connection pooling and Base entity abstractions. | **High** |
| `/backend/src/core/security` | Rate limiting middleware, JWT handling, and password security. | **High** |
| `/dataset/data` | Master repository of raw currency images (2,905 notes across denominations). | **Critical** |
| `/dataset/cleaned` | Cleaned currency and security feature crops. | **High** |
| `/dataset/split` | Current train/val/test splits used by training scripts. | **Critical (Defective)** |
| `/frontend/src/pages` | User interface views (Verify, Dashboard, History, Analytics, Admin, Settings). | **High** |
| `/frontend/src/core/api` | Centralized Axios HTTP client communicating with FastAPI `/api/v1`. | **High** |

---

## 3. Dead, Unused, and Duplicate Code

1. **Duplicate Diagnostic Scripts**: Multiple standalone evaluation scripts exist in `backend/` (`evaluate_models.py`, `evaluate_phase14.py`, `evaluate_pipelines.py`, `eval_experiment.py`, `phase15_investigator.py`, `phase16_experiment.py`, `reconcile_data.py`, `step1_diagnostic.py`). Many contain hardcoded absolute paths to `C:\PROJECTS\fakecurrency` (which do not exist on this machine, located at `D:\PROJECTS\notegurd\NoteguardAI`).
2. **Unused Feature Validation Relational Table**: `feature_validations` table exists in PostgreSQL and SQLAlchemy models (`models.py`), but the single-model CNN does not extract individual microtext/thread ROI crops.
3. **Deskewing Bypass**: In `backend/src/modules/ai_engine/pipeline.py` (lines 37-41), OpenCV contour deskewing is explicitly commented out and bypassed because the CNN was trained on raw unaligned images.
4. **Hardcoded Fallbacks**: Several test scripts contain mock fallback payloads.

---

## 4. Potential Architectural Conflicts & Deficiencies

1. **Path Discrepancies**: Scripts reference `C:\PROJECTS\fakecurrency`, whereas the active workspace is `d:\PROJECTS\notegurd\NoteguardAI`.
2. **Dataset Split Corruption**: `dataset/split/val` and `dataset/split/test` are severely unbalanced and missing whole classes (e.g. `real_20`, `real_50`, `real_200` are absent in `val`).
3. **Class Indexing Mismatch**: `TrainingConfig.CLASS_NAMES` order differs from standard alphabetical Keras directory loading order, causing severe denomination misclassification.
4. **Model Checkpoint Location**: No pre-compiled `.keras` weights were committed into git due to `.gitignore`, requiring systematic retraining with proper class mappings on the cleaned dataset.
