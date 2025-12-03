# Radioactive Decay Simulator (Radio-active)
#### Video Demo: https://youtu.be/eh2eJb9oVl4
#### Description:

Radio-active is a web-based scientific simulator that models radioactive decay using a mathematical model. Designed for students, educators, and researchers, this application allows users to select a radioactive isotope, input an initial quantity, and specify elapsed time to visualize the decay process. The app calculates the decay constant (λ), remaining quantity N(t), and generates an interactive plot to illustrate the decay curve. It also supports PDF export with a static plot for academic documentation.

This project was built using Flask (Python), SQLite, Plotly, Matplotlib, and Bootstrap 5. The technology Copilot was also used to find bibliography and as support for decision making. The app integrates secure user authentication, dynamic form validation, and responsive design for desktop and mobile devices. The application is fully localized in English and supports scientific notation for precision.

---

## Mathematical Foundation

Radioactive decay is governed by a first-order linear differential equation that models the rate at which a radioactive element decays over time. The equation is:

\[
\frac{dN}{dt} = -\lambda N
\]

Where:
- \( N(t) \) is the quantity of the radioactive substance at time \( t \)
- \( \lambda \) is the decay constant (in units of inverse time)
- \( \frac{dN}{dt} \) represents the rate of change of the quantity over time

This equation states that the rate of decay is proportional to the current amount of isotope. Solving this differential equation yields the exponential decay law:

\[
N(t) = N_0 \cdot e^{-\lambda t}
\]

Where:
- \( N_0 \) is the initial quantity at time \( t = 0 \)
- \( e \) is Euler’s number (approximately 2.71828)

This function is used throughout the application to compute the remaining quantity and to generate both interactive and static decay plots.

---

## Features

- 📊 **Interactive Plot**: Uses Plotly to render dynamic decay curves with hover tooltips.
- 🖼️ **Static Plot for PDF**: Generates Matplotlib-based PNG graphs for export.
- 📄 **PDF Export**: Allows users to download a formatted report of their simulation.
- 🔐 **User Authentication**: Secure login, registration, and password change functionality.
- 📁 **Simulation History**: Users can view and edit past simulations.
- 🌐 **Responsive Design**: Optimized for mobile and desktop using Bootstrap 5.
- 🧪 **Element Database**: Includes a curated list of radioactive isotopes with half-life and unit metadata.

---

## File Overview

- `__init__.py`: This file initializes the Flask application and sets up core configurations.
- `run.py`: File used as the main entry point for running the application locally.
- `routes.py`: Main Flask application with all route definitions, including simulation logic, user authentication, and PDF export.
- `forms.py`: Contains all WTForms classes for simulation input, login, registration, and password change. Includes field validation.
- `init_db.py`: Used to create the database radioactive.db in SQLite.
- `populate_alements.py`: Used to populate the table 'elements' in the database.
- `templates/`: HTML templates using Jinja2. Includes `index.html`, `simulation_detail.html`, `edit_simulation.html`, `pdf_exp.html`, `history.html`, `register.html`,
`result.html`, `login.html`, `layout.html` and `change_password.html`
- `static/css/theme_radioactive.css`: Custom CSS theme with electric background and accent colors for scientific aesthetics.
- `static/plots/`: Folder where Matplotlib saves static PNG plots for PDF export.
- `static/css/pdf_style.css`: Contains a more solemn style to generate a PDF report.
- `requirements.txt`: List of Python dependencies (Flask, Plotly, Matplotlib, WeasyPrint, etc.).
- `plot.py`: Contains the functions to build both the static and interactive plots.
- `schema.sql`: File used to create the primary tables in database.

---

## Design Decisions

- **Plotly vs. Matplotlib**: Plotly was chosen for interactive web visualization, while Matplotlib was used for static image generation compatible with PDF export.
- **WeasyPrint for PDF**: Selected for its ability to render HTML and CSS into high-quality PDFs, including embedded images.
- **Session-based Access Control**: All simulation data is filtered by `user_id` to prevent unauthorized access.
- **Scientific Notation**: Decay constants are often very small or large; formatting with `%.5e` ensures clarity.
- **Dynamic Form Choices**: Element dropdowns are populated from the database to ensure consistency and scalability.
- **Minimum Time Range for Visualization**: For isotopes with very short half-lives (e.g., Iodine-131), the graphing functions enforce a minimum `t_max` to ensure visibility.
- **Less resolution for plots with a huge half-life**: For isotopes with a large half-life (e.g., Uranium-235), the graphing funtion reduces the resolution.

---

## Challenges and Solutions

- **Short Half-Life Visualization**: Simulations with extremely short half-lives required dynamic scaling of the time axis to render meaningful plots.
- **Large Half-Life Visualization**: Some crashes occurred whent trying to plot simulations with extremely large half-lives. The resolution was reduced so that the browser doesn't have to draw millions of points, and it doesn't saturate causing the application to crash.
- **Responsive Layout**: Adjusted color schemes and added viewport meta tags to ensure usability on mobile devices.
- **Security**: Implemented CSRF protection with Flask-WTF and session-based filtering to prevent unauthorized access to simulations.
- **Plots**: At first, Matplotlib was chosen to build plots in the results and simulation details pages, but it was replaced by Plotly because it was more desirable that the user has more interaction with the plot being able to see every value of remaining quantity (N) at any value of time of the simulation.
- **Jinja conflict with math**: Jinja doesn't support mathematical operations, so all of the values needed to be passed as results from operations.
- **Generating PDF document**: First of all, the plot needed to be a static one, so Matplotlib was chosen to generate it. Second, a verifications was done in order to determine if the image file exists and is readable. Third, a relative path and a base URL were define. Fouth, the HTML was rendered with all of the data and then converted to PDF. Finally, the PDF was generated as an HTTP response.


---

## How to Run

1. Clone the repository.
2. Create a virtual environment and install dependencies from `requirements.txt`.
3. Run `flask run` to start the server.
4. Access the app at `http://localhost:5000`.
5. Register a user, simulate decay, and export results.

---
