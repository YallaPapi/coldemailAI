# AI Cold Email Generator

## Overview

This is a Flask-based web application that generates personalized cold emails from lead spreadsheets using OpenAI's GPT-4. Users upload Excel or CSV files containing lead data, and the system generates tailored cold emails for each prospect based on their company, industry, and location information.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows a simple Flask web application architecture with the following key components:

### Frontend Architecture
- Server-side rendered HTML templates using Jinja2
- Bootstrap-based responsive UI with dark theme
- Client-side JavaScript for form validation and user experience enhancements
- File upload interface with drag-and-drop functionality

### Backend Architecture
- **Flask Web Framework**: Lightweight Python web server handling HTTP requests
- **Modular Design**: Separation of concerns with dedicated `EmailGenerator` class
- **File Processing**: Pandas-based spreadsheet parsing for Excel and CSV files
- **AI Integration**: OpenAI GPT-4 API for personalized email generation

## Key Components

### 1. Web Server (`app.py`)
- Handles file uploads with security validation
- Processes spreadsheet data using Pandas with flexible column mapping
- Manages user sessions and flash messages
- Implements file size and type restrictions (16MB max, Excel/CSV only)
- **Enhanced Data Support**: Automatically detects and uses high-value fields:
  - Job titles for role-specific messaging
  - Company size for scale-appropriate solutions
  - Founded year for maturity-based context
  - Organization descriptions for unique business insights
  - Multiple location field formats

### 2. Email Generation Engine (`email_generator.py`)
- **Purpose**: Generates personalized cold emails using AI
- **AI Model**: OpenAI GPT-4o for natural language generation
- **Multi-Field Personalization**: Uses comprehensive prospect data including:
  - Personal: Name, job title/role
  - Company: Name, industry, size, founding year, description
  - Location: City, state, country
- **Intelligent Contextualization**: AI adapts messaging based on:
  - Role-specific challenges (CEO vs Operations Manager)
  - Company scale (startup vs enterprise solutions)
  - Company maturity (growth vs established operations)
  - Unique business context from descriptions
- **Flexible Field Mapping**: Supports multiple column name formats from different data sources

### 3. Frontend Interface (`templates/index.html`, `static/js/app.js`)
- **Upload Form**: Secure file upload with client-side validation
- **User Feedback**: Flash message system for success/error notifications
- **Progressive Enhancement**: JavaScript validation with fallback to server-side validation

## Data Flow

1. **File Upload**: User uploads Excel/CSV file through web interface
2. **Validation**: File type, size, and format validation on both client and server
3. **Data Processing**: Pandas reads spreadsheet and extracts lead information (required + optional columns)
4. **AI Processing**: For each lead, system builds highly personalized prompt using organization description when available
5. **Email Generation**: GPT-4o generates tailored cold email based on prospect data and unique business context
6. **Output Delivery**: Generated emails are compiled and delivered to user

## External Dependencies

### Core Dependencies
- **Flask**: Web framework for handling HTTP requests and routing
- **Pandas**: Data manipulation and spreadsheet processing
- **OpenAI Python SDK**: API client for GPT-4 integration
- **Werkzeug**: Security utilities for file handling

### Frontend Dependencies
- **Bootstrap 5**: UI framework with dark theme support
- **Font Awesome**: Icon library for enhanced user interface

### Environment Requirements
- **OPENAI_API_KEY**: Required environment variable for AI functionality
- **SESSION_SECRET**: Flask session security (falls back to development key)

## Deployment Strategy

### Current Configuration
- **Development Server**: Flask development server on port 5000
- **Container Ready**: Dockerfile provided for containerized deployment
- **Cloud Deployment**: Configured for Google Cloud Run deployment
- **Environment Variables**: Externalized configuration for API keys and secrets

### Security Considerations
- File upload restrictions (type and size limits)
- Secure filename handling with Werkzeug
- Session management with secret key configuration
- Proxy-aware deployment with ProxyFix middleware

### Scalability Notes
- Stateless design suitable for horizontal scaling
- File processing handled in-memory (suitable for moderate file sizes)
- API rate limiting considerations for OpenAI integration
- Potential for queue-based processing for larger datasets

## Key Architectural Decisions

### Problem Addressed
Manual cold email personalization is time-consuming and doesn't scale effectively for sales teams processing hundreds of leads.

### Chosen Solution
AI-powered email generation using GPT-4 with structured prompts that leverage lead data for personalization.

### Design Rationale
- **Flask over Django**: Chosen for simplicity and lightweight deployment needs
- **Server-side Processing**: Ensures API key security and centralized AI processing
- **In-memory Processing**: Simpler deployment without database requirements
- **OpenAI GPT-4**: Provides high-quality, contextually aware email generation

### Trade-offs
- **Pros**: Simple deployment, fast development, secure API key handling
- **Cons**: Limited by server memory for very large files, synchronous processing may cause timeouts for large datasets

## Recent Changes: Latest modifications with dates

### July 29, 2025 - Dynamic Column Mapping System Implemented
- **Complete Dynamic Field Mapping**: Built two-step upload process with dynamic column mapping interface
- **Universal Spreadsheet Support**: System now accepts any CSV/Excel format from Apollo.io or other lead sources
- **User-Friendly Mapping Interface**: 
  - Step 1: File upload with validation
  - Step 2: Interactive mapping page showing all spreadsheet columns
  - Dropdown selection for each system parameter (name, company, title, industry, location, description)
  - Required fields (First Name, Company Name) clearly marked
  - Optional fields default to "Skip This Field"
- **Enhanced AI Integration**: New `process_leads_with_mapping()` method uses user-defined column mappings
- **Maintained Location Personalization**: Vegas heat, California innovation, Texas scaling, NYC speed, Florida sunshine references
- **Production Ready**: Handles 10k+ leads with proper session management and error handling