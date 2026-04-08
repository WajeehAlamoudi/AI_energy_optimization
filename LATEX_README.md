# Checkpoint 2 LaTeX Documentation

This directory contains the LaTeX source code for **Checkpoint 2** of the AI Energy Optimization project, focusing on the frontend development and API integration.

## File

- **Checkpoint2.tex** - Complete LaTeX source document (1,339 lines)

## Document Contents

The document includes comprehensive coverage of:

### 1. Introduction
- Project context and objectives
- Checkpoint 2 goals and scope

### 2. Technology Stack
- Backend technologies (FastAPI, PyTorch, XGBoost, etc.)
- Frontend technologies (HTML5, CSS3, Vanilla JavaScript)
- Design philosophy and rationale

### 3. System Architecture
- High-level architecture diagram (using TikZ)
- Component breakdown (Frontend, API, Business Logic, Data layers)

### 4. Frontend Implementation
- User interface structure (6 views)
- Welcome screen with animated logo
- Navigation system
- Styling and design (glassmorphism, color palette, animations)

### 5. API Development
- RESTful API design principles
- 13+ endpoint implementations with code examples
- Error handling and CORS configuration

### 6. Frontend-Backend Integration
- Communication protocol (Fetch API)
- Data flow examples (initialization, home management, training)
- State management patterns

### 7. Key Features
- Dynamic home management
- Device catalog management
- AI training interface
- Simulation and testing capabilities

### 8. Additional Topics
- Data persistence (JSON-based storage)
- User experience design (responsive, accessibility)
- Performance optimization
- Security considerations
- Testing and validation
- Deployment guidelines
- Future enhancements
- Challenges and solutions

### 9. Appendices
- Complete API reference
- Frontend file structure
- Technology versions

## Features

The LaTeX document includes:

✓ Professional formatting with custom colors matching the "Aura Energy" theme
✓ Syntax-highlighted code listings (Python, JavaScript, HTML, CSS, JSON, Bash)
✓ Architecture diagrams using TikZ
✓ Tables with booktabs styling
✓ Colored section headers
✓ Executive summary in a colored box
✓ Hyperlinked table of contents
✓ Headers and footers with page numbers
✓ Comprehensive appendices

## Compiling the Document

### Requirements

You need a LaTeX distribution installed on your system:

- **Windows**: MiKTeX or TeX Live
- **macOS**: MacTeX
- **Linux**: TeX Live

```bash
# Ubuntu/Debian
sudo apt-get install texlive-full

# macOS with Homebrew
brew install --cask mactex

# Fedora
sudo dnf install texlive-scheme-full
```

### Compilation Commands

#### Using pdflatex (recommended)

```bash
# Navigate to the directory
cd AI_energy_optimization

# Compile (run twice for table of contents)
pdflatex Checkpoint2.tex
pdflatex Checkpoint2.tex

# Clean up auxiliary files (optional)
rm -f Checkpoint2.aux Checkpoint2.log Checkpoint2.out Checkpoint2.toc
```

#### Using latexmk (automatic compilation)

```bash
# Compile with automatic reruns
latexmk -pdf Checkpoint2.tex

# Clean up
latexmk -c Checkpoint2.tex
```

### Online Compilation

If you don't have LaTeX installed locally, you can use online services:

1. **Overleaf**: Upload `Checkpoint2.tex` to [overleaf.com](https://www.overleaf.com)
2. **Papeeria**: Upload to [papeeria.com](https://papeeria.com)
3. **LaTeX Base**: Upload to [latexbase.com](https://latexbase.com)

## Output

After compilation, you will get:

- **Checkpoint2.pdf** - The final PDF document (~30-40 pages)

The PDF includes:
- Professional title page
- Table of contents with hyperlinks
- Colored headers and formatted sections
- Code listings with syntax highlighting
- Architecture diagrams
- Tables and appendices

## Customization

### Changing Colors

Edit the color definitions in the preamble:

```latex
\definecolor{primarycolor}{RGB}{255, 107, 53}    % Orange
\definecolor{secondarycolor}{RGB}{46, 196, 182}  % Teal
```

### Modifying Page Layout

Adjust the geometry settings:

```latex
\geometry{
    a4paper,
    top=2.5cm,
    bottom=2.5cm,
    left=2.5cm,
    right=2.5cm
}
```

### Adding Content

The document is well-structured. To add new sections:

```latex
\section{Your New Section}
\subsection{Your Subsection}

Your content here...
```

## Package Dependencies

The document uses these LaTeX packages:

- **inputenc, fontenc** - Character encoding
- **geometry** - Page layout
- **graphicx** - Image support
- **float** - Float positioning
- **amsmath, amssymb** - Mathematical symbols
- **hyperref** - Hyperlinks and PDF metadata
- **listings** - Code syntax highlighting
- **xcolor** - Color support
- **enumitem** - Enhanced lists
- **titlesec** - Section formatting
- **fancyhdr** - Headers and footers
- **tcolorbox** - Colored boxes
- **booktabs** - Professional tables
- **tikz** - Diagrams and graphics
- **caption, subcaption** - Figure captions

All packages are included in standard TeX distributions.

## Troubleshooting

### Missing Packages Error

If you get "File '*.sty' not found" errors:

```bash
# Install missing packages (Ubuntu/Debian)
sudo apt-get install texlive-latex-extra texlive-fonts-extra

# Or use tlmgr (package manager)
tlmgr install <package-name>
```

### Compilation Errors

1. **Check syntax**: Ensure all LaTeX commands are properly closed
2. **Run twice**: Some features (TOC, references) need multiple compilations
3. **Check logs**: Review `Checkpoint2.log` for detailed error messages

### UTF-8 Issues

If you see encoding errors, ensure your editor saves the file as UTF-8.

## Version Information

- **Document Version**: 1.0
- **Created**: January 2026
- **LaTeX Class**: article (12pt, a4paper)
- **Lines of Code**: 1,339

## License

This documentation is part of the AI Energy Optimization project.

## Contact

For issues or questions about this LaTeX documentation:
- Check the [GitHub repository](https://github.com/WajeehAlamoudi/AI_energy_optimization)
- Review the project README.md
- Contact the project maintainers

---

**Happy Compiling! 📄✨**
