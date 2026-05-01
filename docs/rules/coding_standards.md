# Global Coding Standards & Architecture Guidelines

## 1. Purpose
This document enforces strict "Clean Code" and "SOLID" engineering principles for all software development within the SeaTurtle Photo-ID project. Every agent, tool, or AI assistant (e.g., Claude Code, VS Code Agents) MUST evaluate their code against these rules BEFORE writing or modifying any file.

## 2. SOLID Principles (Strictly Enforced)

All object-oriented designs and architectural patterns must adhere to the following:

*   **[S] Single Responsibility Principle (SRP):** 
    *   A class, module, or function must have one, and only one, reason to change.
    *   *Rule:* Never mix data fetching/I-O logic with image processing or model training logic. Keep domains strictly isolated.
*   **[O] Open/Closed Principle (OCP):**
    *   Software entities must be open for extension but closed for modification.
    *   *Rule:* Use Abstract Base Classes (ABCs) or Interfaces. If we want to add a new CNN model (e.g., switching from ResNet to EfficientNet), we should only need to add a new class, not modify existing training pipelines.
*   **[L] Liskov Substitution Principle (LSP):**
    *   Derived classes must be substitutable for their base classes without altering the correctness of the program.
    *   *Rule:* Ensure consistent return types and avoid raising unexpected exceptions in overridden methods.
*   **[I] Interface Segregation Principle (ISP):**
    *   Do not force clients to depend on interfaces they do not use.
    *   *Rule:* Create small, role-specific interfaces rather than large, monolithic ones.
*   **[D] Dependency Inversion Principle (DIP):**
    *   High-level modules should not depend on low-level modules. Both should depend on abstractions.
    *   *Rule:* Always inject dependencies (Dependency Injection). Do not hardcode configurations, database connections, or specific external libraries directly inside business logic classes.

## 3. Clean Code Practices

### 3.1. Naming Conventions
*   Names must reveal intent. If a variable requires a comment to explain what it does, the name is wrong.
*   Use descriptive and searchable names. Avoid abbreviations. 
*   *Bad:* `def proc_img(d):` | *Good:* `def apply_clahe_to_turtle_image(image_data):`

### 3.2. Function & Method Design
*   **Size:** Functions should be small. A function should ideally not exceed 20-25 lines of code.
*   **Arguments:** Strive for zero to two arguments. If a function requires more than three arguments, consider wrapping them in a Data Transfer Object (DTO) or a configuration class.
*   **Side Effects:** Functions should do exactly what their name suggests and nothing else. Avoid hidden side effects.

### 3.3. Magic Numbers and Strings
*   NEVER use "magic numbers" or hardcoded strings directly in the code logic.
*   *Rule:* Extract all hardcoded values (e.g., `224` for image size, `0.001` for learning rate) into highly visible constant files, configuration classes, or environment variables.

### 3.4. Error Handling
*   **Fail Fast:** Validate inputs immediately. Don't let bad data propagate deeply into the system.
*   Use standard exceptions appropriately and provide clear, informative error messages.
*   *Rule:* NEVER use an empty `try...except` or `except Exception: pass` block. If an exception is caught, it must be handled or logged properly.

### 3.5. Comments and Documentation
*   **Why over What:** Code should explain *what* it does; comments should explain *why* it does it. Avoid redundant comments that just restate the code.
*   **Docstrings:** All public classes, methods, and functions must have descriptive docstrings explaining their purpose, arguments, and return types.
*   *Rule:* Keep documentation updated alongside code changes. Stale documentation is worse than no documentation.

### 3.6. Code Formatting and Linting
*   **Consistency:** Adhere to language-specific formatting standards (e.g., PEP 8 for Python, standard C# conventions for .NET).
*   **Automated Tools:** Use automated formatters (like Black) and linters (like Flake8 or SonarQube) before committing any code to catch formatting issues and code smells.

## 4. Agent Execution Protocol
**MANDATORY:** Before executing a file write operation, the AI Agent must silently ask itself: 
1. *Did I violate any SOLID principles?*
2. *Is this code self-documenting and clean?*
3. *Are there any magic numbers?*

If the answer to (1) is Yes, or (2/3) is No, the Agent MUST refactor the code before committing the changes.