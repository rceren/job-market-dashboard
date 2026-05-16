import pandas as pd
import sqlite3

def load_and_clean():
    print("Loading dataset... (this may take a moment, it's a large file!)")
    
    # Load only the columns we need
    cols = ['title', 'company_name', 'location', 'med_salary', 'min_salary', 
            'max_salary', 'listed_time', 'applies', 'views']
    
    df = pd.read_csv('postings.csv', usecols=lambda c: c in cols, low_memory=False)
    
    print(f"Loaded {len(df)} job postings!")
    print("Columns found:", df.columns.tolist())
    
    # Clean up
    df = df.dropna(subset=['title'])
    df['company_name'] = df['company_name'].fillna('Unknown')
    df['location'] = df['location'].fillna('Unknown')
    
    print(f"After cleaning: {len(df)} postings")
    return df

def save_to_db(df):
    print("Saving to database...")
    conn = sqlite3.connect('jobs.db')
    df.to_sql('postings', conn, if_exists='replace', index=False)
    conn.close()
    print("Done! Database created successfully.")

if __name__ == "__main__":
    df = load_and_clean()
    save_to_db(df)