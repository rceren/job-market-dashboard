from flask import Flask
from functools import lru_cache
import sqlite3
import json
from analyze import (get_top_job_titles, get_top_companies,
                     get_top_locations, get_salary_stats, get_top_skills)

app = Flask(__name__)

@lru_cache(maxsize=1)
def get_cached_data():
    conn = sqlite3.connect('jobs.db')
    cursor = conn.cursor()
    titles = get_top_job_titles(cursor)
    companies = get_top_companies(cursor)
    locations = get_top_locations(cursor)
    salary = get_salary_stats(cursor)
    skills = get_top_skills(cursor)
    cursor.execute("SELECT COUNT(*) FROM postings")
    total_jobs = cursor.fetchone()[0]
    conn.close()
    return titles, companies, locations, salary, skills, total_jobs

@app.route("/")
def index():
    titles, companies, locations, (avg_salary, min_salary, max_salary), skills, total_jobs = get_cached_data()

    title_labels = json.dumps([t[0] for t in titles])
    title_values = json.dumps([t[1] for t in titles])
    company_labels = json.dumps([c[0] for c in companies])
    company_values = json.dumps([c[1] for c in companies])
    location_labels = json.dumps([l[0] for l in locations])
    location_values = json.dumps([l[1] for l in locations])
    skill_labels = json.dumps([s[0] for s in skills])
    skill_values = json.dumps([s[1] for s in skills])

    html = f'''<!DOCTYPE html>
<html>
<head>
    <title>Job Market Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: Arial, sans-serif; background: #0f172a; color: #e2e8f0; padding: 30px; }}
        h1 {{ color: #38bdf8; text-align: center; margin-bottom: 10px; font-size: 2em; }}
        .subtitle {{ text-align: center; color: #94a3b8; margin-bottom: 30px; }}
        .cards {{ display: flex; gap: 20px; justify-content: center; margin-bottom: 30px; flex-wrap: wrap; }}
        .card {{ background: #1e293b; border-radius: 12px; padding: 20px 35px; text-align: center; min-width: 150px; }}
        .card h2 {{ font-size: 1.8em; color: #38bdf8; }}
        .card p {{ color: #94a3b8; margin-top: 5px; font-size: 0.9em; }}
        .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; max-width: 1200px; margin: 0 auto; }}
        .chart-box {{ background: #1e293b; border-radius: 12px; padding: 25px; }}
        .chart-box h3 {{ color: #38bdf8; margin-bottom: 15px; font-size: 1em; }}
        .full-width {{ grid-column: 1 / -1; }}
    </style>
</head>
<body>
    <h1>📊 Job Market Dashboard</h1>
    <p class="subtitle">Analyzing {total_jobs:,} real LinkedIn job postings</p>

    <div class="cards">
        <div class="card">
            <h2>{total_jobs:,}</h2>
            <p>Total Jobs</p>
        </div>
        <div class="card">
            <h2>${avg_salary:,.0f}</h2>
            <p>Avg Salary</p>
        </div>
        <div class="card">
            <h2>${min_salary:,.0f}</h2>
            <p>Min Salary</p>
        </div>
        <div class="card">
            <h2>${max_salary:,.0f}</h2>
            <p>Max Salary</p>
        </div>
    </div>

    <div class="grid">
        <div class="chart-box">
            <h3>🔧 Top Skills in Demand</h3>
            <canvas id="skillsChart"></canvas>
        </div>
        <div class="chart-box">
            <h3>📍 Top Locations</h3>
            <canvas id="locationsChart"></canvas>
        </div>
        <div class="chart-box full-width">
            <h3>💼 Top Job Titles</h3>
            <canvas id="titlesChart"></canvas>
        </div>
        <div class="chart-box full-width">
            <h3>🏢 Top Hiring Companies</h3>
            <canvas id="companiesChart"></canvas>
        </div>
    </div>

    <script>
        const colors = ["#38bdf8","#818cf8","#34d399","#fb923c","#f472b6",
                      "#a78bfa","#fbbf24","#60a5fa","#4ade80","#f87171"];

        new Chart(document.getElementById("skillsChart"), {{
            type: "bar",
            data: {{
                labels: {skill_labels},
                datasets: [{{ data: {skill_values}, backgroundColor: colors }}]
            }},
            options: {{
                plugins: {{ legend: {{ display: false }} }},
                scales: {{
                    x: {{ ticks: {{ color: "#94a3b8" }} }},
                    y: {{ ticks: {{ color: "#94a3b8" }} }}
                }}
            }}
        }});

        new Chart(document.getElementById("locationsChart"), {{
            type: "doughnut",
            data: {{
                labels: {location_labels},
                datasets: [{{ data: {location_values}, backgroundColor: colors }}]
            }},
            options: {{
                plugins: {{ legend: {{ labels: {{ color: "#94a3b8", boxWidth: 12 }} }} }}
            }}
        }});

        new Chart(document.getElementById("titlesChart"), {{
            type: "bar",
            data: {{
                labels: {title_labels},
                datasets: [{{ data: {title_values}, backgroundColor: colors }}]
            }},
            options: {{
                indexAxis: "y",
                plugins: {{ legend: {{ display: false }} }},
                scales: {{
                    x: {{ ticks: {{ color: "#94a3b8" }} }},
                    y: {{ ticks: {{ color: "#94a3b8" }} }}
                }}
            }}
        }});

        new Chart(document.getElementById("companiesChart"), {{
            type: "bar",
            data: {{
                labels: {company_labels},
                datasets: [{{ data: {company_values}, backgroundColor: colors }}]
            }},
            options: {{
                indexAxis: "y",
                plugins: {{ legend: {{ display: false }} }},
                scales: {{
                    x: {{ ticks: {{ color: "#94a3b8" }} }},
                    y: {{ ticks: {{ color: "#94a3b8" }} }}
                }}
            }}
        }});
    </script>
</body>
</html>'''
    return html

if __name__ == "__main__":
    app.run(debug=True)