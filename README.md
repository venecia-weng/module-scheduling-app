# Module Scheduler App

A comprehensive academic module scheduling and planning application built with Python and Tkinter. This application helps students visualize their course progress, plan future semesters, and understand module dependencies through an intuitive graphical interface.

## Features

### 🎓 Core Functionality
- **Student Login System**: Secure 6-digit student ID authentication
- **Module Progress Tracking**: View completed modules with credit tracking
- **Dependency Visualization**: Interactive graph showing module prerequisites
- **Course Path Planning**: Simulate and validate course sequences
- **Credit Planning**: Automated semester planning with credit limits
- **Module Search**: Find modules by code or name
- **Eligibility Checker**: Identify modules you can currently take

### 🔍 Advanced Features
- **Topological Sorting**: Intelligent module ordering based on prerequisites
- **Cycle Detection**: Identifies and reports circular dependencies
- **Cross-Course Compatibility**: Support for related course modules
- **What-If Analysis**: Test different course paths before committing
- **Progress Dashboard**: Visual progress tracking with completion statistics

## Installation

### Prerequisites
- Python 3.7 or higher
- Required Python packages:

```bash
pip install tkinter matplotlib networkx
```

### Setup
1. Clone or download the repository
2. Ensure you have the following files in the same directory:
   - `ModuleSchedulerAppV2.py` (main application)
   - `modules.json` (module catalog)
   - `students.json` (student data)

3. Run the application:
```bash
python ModuleSchedulerAppV2.py
```

## Data Files

### modules.json
Contains the module catalog with the following structure:
```json
[
  {
    "code": "CS101",
    "name": "Introduction to Computer Science",
    "tracks": ["Computer Science", "Data Science"],
    "prerequisites": [],
    "credits": 3
  }
]
```

### students.json
Contains student information:
```json
[
  {
    "student_id": "123456",
    "name": "John Doe",
    "course": "Computer Science",
    "year": 2,
    "semester": 1,
    "completed": ["CS101", "MATH101"]
  }
]
```

## Usage Guide

### Getting Started
1. **Login**: Enter your 6-digit student ID
2. **Main Menu**: Choose from various options to manage your academic journey

### Key Features

#### 📚 View Completed Modules
- See all modules you've completed
- Track total credits earned
- View module details and tracks

#### 📅 View Upcoming Core Modules
- Modules ordered using topological sorting algorithm
- Shows prerequisite requirements
- Identifies your next eligible modules

#### 🕸️ Module Dependency Graph
- Visual representation of module relationships
- Filter options:
  - **All Modules**: Complete course structure
  - **Current + Next Semester**: Focused view of immediate path
  - **Eligible Modules Only**: What you can take now
- Color coding: Green (completed), Blue (not completed)

#### 📊 Progress Dashboard
- Overall course completion percentage
- Credit tracking and requirements
- Recommended modules for next semester
- Visual progress bar

#### 🔮 Simulate Course Path
- Test module sequences before enrollment
- Validates prerequisite requirements
- Credit load analysis and warnings
- Path feasibility checking

#### 📋 Credit Semester Planner
- Automated semester planning
- Customizable credit limits per semester
- Optimal module distribution
- Timeline estimation

#### 🔍 Module Search
- Search by module code or name
- View tracks and prerequisites
- Comprehensive module information

#### ✅ Eligible Modules
- Shows modules you can currently enroll in
- Includes related course modules
- Prerequisite validation

## Algorithm Details

### Topological Sorting
The application uses **Kahn's Algorithm** for topological sorting to:
- Order modules based on prerequisite dependencies
- Ensure valid course sequences
- Detect impossible scheduling scenarios

### Cycle Detection
Uses **Depth-First Search (DFS)** to:
- Identify circular dependencies in prerequisites
- Prevent infinite loops in course planning
- Report problematic module chains

### Related Courses
Supports cross-disciplinary learning through predefined course relationships:
- Data Science ↔ Mathematics, Computer Science, Economics
- Biology ↔ Chemistry, Medicine, Microbiology
- And many more combinations

## Technical Architecture

### Core Components
- **Module Class**: Represents individual academic modules
- **Student Class**: Manages student data and progress
- **GUI Framework**: Tkinter-based interface with ttk styling
- **Graph Visualization**: matplotlib integration for dependency graphs
- **Data Management**: JSON-based configuration and student data

### Key Algorithms
- **Topological Sort**: Module ordering with cycle detection
- **Graph Theory**: NetworkX for dependency visualization
- **Credit Optimization**: Greedy algorithm for semester planning

## Customization

### Adding New Modules
Edit `modules.json` to add new modules:
```json
{
  "code": "NEW101",
  "name": "New Module Name",
  "tracks": ["Your Course"],
  "prerequisites": ["PREREQ101"],
  "credits": 3
}
```

### Adding Students
Edit `students.json` to add new students:
```json
{
  "student_id": "654321",
  "name": "Jane Smith",
  "course": "Mathematics",
  "year": 1,
  "semester": 2,
  "completed": []
}
```

### Course Relationships
Modify the `related_courses` dictionary in the code to add new course relationships.

## Error Handling

The application includes robust error handling for:
- Missing or corrupted data files
- Invalid student IDs
- Circular dependencies in prerequisites
- Invalid module codes in simulations
- File loading failures

## Demo Data

The application includes demo student accounts for testing. Student IDs are displayed on the login screen for easy access during demonstration.

## Contributing

To contribute to this project:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly with demo data
5. Submit a pull request

## License

This project is open source. Please ensure proper attribution when using or modifying the code.

## Support

For issues or questions:
1. Check that all required Python packages are installed
2. Verify that `modules.json` and `students.json` are in the correct format
3. Ensure the data files are in the same directory as the main script

## Future Enhancements

Potential improvements could include:
- Database integration for larger datasets
- Web-based interface
- Advanced scheduling algorithms
- Integration with university systems
- Mobile application support
- Advanced analytics and reporting