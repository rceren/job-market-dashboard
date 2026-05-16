import sqlite3
import pandas as pd

def get_top_job_titles(cursor, limit=10):
    cursor.execute('''
        SELECT title, COUNT(*) as count 
        FROM postings 
        GROUP BY title 
        ORDER BY count DESC 
        LIMIT ?
    ''', (limit,))
    return cursor.fetchall()

def get_top_companies(cursor, limit=10):
    cursor.execute('''
        SELECT company_name, COUNT(*) as count 
        FROM postings 
        WHERE company_name != 'Unknown'
        GROUP BY company_name 
        ORDER BY count DESC 
        LIMIT ?
    ''', (limit,))
    return cursor.fetchall()

def get_top_locations(cursor, limit=10):
    cursor.execute('''
        SELECT location, COUNT(*) as count 
        FROM postings 
        WHERE location != 'Unknown'
        GROUP BY location 
        ORDER BY count DESC 
        LIMIT ?
    ''', (limit,))
    return cursor.fetchall()

def get_salary_stats(cursor):
    cursor.execute('''
        SELECT 
            ROUND(AVG(med_salary), 2),
            ROUND(MIN(med_salary), 2),
            ROUND(MAX(med_salary), 2)
        FROM postings
        WHERE med_salary IS NOT NULL
        AND med_salary > 0
    ''')
    return cursor.fetchone()

def get_top_skills(cursor, limit=10):
    skills = [
        'Python', 'SQL', 'Excel', 'Power BI', 'Tableau',
        'Machine Learning', 'JavaScript', 'AWS',
        'Azure', 'Docker', 'Git', 'Spark', 'Kotlin',
        'Data Analysis', 'Statistics'
    ]
    
    results = []
    for skill in skills:
        cursor.execute('''
            SELECT COUNT(*) FROM postings 
            WHERE ' ' || title || ' ' LIKE ?
            OR ' ' || title || ' ' LIKE ?
        ''', (f'% {skill} %', f'% {skill},%'))
        count = cursor.fetchone()[0]
        results.append((skill, count))
    
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:limit]

if __name__ == "__main__":
    conn = sqlite3.connect('jobs.db')
    cursor = conn.cursor()
    
    print("=== TOP 10 JOB TITLES ===")
    for title, count in get_top_job_titles(cursor):
        print(f"  {title}: {count}")
    
    print("\n=== TOP 10 COMPANIES ===")
    for company, count in get_top_companies(cursor):
        print(f"  {company}: {count}")

    print("\n=== TOP 10 LOCATIONS ===")
    for location, count in get_top_locations(cursor):
        print(f"  {location}: {count}")

    print("\n=== SALARY STATS ===")
    avg, mn, mx = get_salary_stats(cursor)
    print(f"  Average: ${avg}")
    print(f"  Min: ${mn}")
    print(f"  Max: ${mx}")

    print("\n=== SKILLS IN DEMAND ===")
    for skill, count in get_top_skills(cursor):
        print(f"  {skill}: {count}")
    
    conn.close()