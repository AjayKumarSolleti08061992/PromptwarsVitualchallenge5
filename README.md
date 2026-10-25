# Google Cloud Technologies Conference Site

A premium, 1-day technical conference informational site demonstrating a modern aesthetic using HTML, CSS (Vanilla), and JavaScript for the frontend, powered by a Python Flask server acting as an API. 

## Features
- **Dynamic Schedule:** Agenda entries are loaded dynamically via a `/api/schedule` endpoint.
- **Search and Filter:** Real-time client-side filtering by "Infrastructure & Compute" or "Data & AI" categories, and instantaneous search matching by talk title or speaker name.
- **Premium Design:** Implements modern visuals, dark mode aesthetics, gradients, and micro-interactions for a premium feel without bulky frameworks or generic UI toolkits.

## Tech Stack
- **Backend:** Python + Flask
- **Frontend:** HTML5, CSS3, ES6 JavaScript 
- **Fonts:** Inter (Google Fonts)

## Setup Instructions
To run this project locally, ensure you have Python 3 installed. Then follow these steps:

1. **Clone or download** the repository.
2. **Open a terminal** in the root of the project.
3. **Create a virtual environment:**
    ```bash
    python -m venv venv
    ```
4. **Activate the environment:**
    * Windows: `.\venv\Scripts\activate`
    * Mac/Linux: `source venv/bin/activate`
5. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Running the App
After setup, start the Flask development server:

```bash
python app.py
```
Then navigate to `http://127.0.0.1:5000` in your web browser. 

## Making Changes
- **Data (Events/Speakers):** Modify the `events_data` array within `app.py`.
- **Styling:** Edit `static/css/style.css`.
- **Client Logic (Search/Rendering):** Edit `static/js/app.js`.
- **Layout:** Edit `templates/index.html`.
