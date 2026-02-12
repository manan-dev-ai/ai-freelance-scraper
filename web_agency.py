import json
import time
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- 1. THE INTERN (WebAgent) ---
# Job: Go to the website, grab the text/links, come back.
class WebAgent:
    def __init__(self, agent_id):
        self.agent_id = agent_id 
        self.driver = None 

    def perform_task(self, url):
        try:
            print(f"⚙️ {self.agent_id} is starting...")
            
            # Setup (Visible Mode for now)
            options = webdriver.ChromeOptions()
            options.add_argument("--disable-blink-features=AutomationControlled") 
            
            service_obj = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service_obj, options=options)
            
            # Navigate
            print(f"🚀 Going to {url}...")
            self.driver.get(url)
            
            # Wait & Search
            wait = WebDriverWait(self.driver, 10)
            search_box = wait.until(EC.presence_of_element_located((By.NAME, "q")))
            
            search_box.send_keys("AI Freelance Jobs")
            search_box.send_keys(Keys.RETURN)
            
            # Wait for Results
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[data-testid='result-title-a']")))
            
            # Scrape
            results = self.driver.find_elements(By.CSS_SELECTOR, "a[data-testid='result-title-a']")
            extracted_data = []
            
            for result in results[:10]:
                title = result.text
                link = result.get_attribute("href")
                if len(title) > 5 and link:
                    # Create a dictionary for each job
                    extracted_data.append({"title": title, "url": link})
            
            self.driver.quit()
            return extracted_data 

        except Exception as e:
            print(f"⚠️ Error: {str(e)}")
            if self.driver: self.driver.quit()
            return []

# --- 2. THE MANAGER (Client) ---
# Job: Hire the intern, collect the data, save it to files.
class Client:
    def __init__(self, name, assigned_agent=None, leads=None):
        self.name = name
        self.assigned_agent = assigned_agent
        self.leads = leads if leads else []

    def run_automation(self, url):
        if self.assigned_agent:
            # 1. Send the Intern
            new_leads = self.assigned_agent.perform_task(url)
            
            # 2. Add new leads to our list
            if new_leads:
                self.leads.extend(new_leads) 
                return f"✅ Added {len(new_leads)} leads."
            return "⚠️ No leads found."
        return "❌ No agent assigned."

    def save_to_json(self):
        # Save raw data to JSON (The Backup)
        data = {"name": self.name, "leads": self.leads}
        filename = f"{self.name}_data.json"
        with open(filename, "w") as file:
            json.dump(data, file, indent=4)
        print(f"💾 Saved backup to {filename}")

    def clean_and_export(self):
        # Save clean data to Excel (The Product)
        if not self.leads: return

        # 1. Load into Pandas
        df = pd.DataFrame(self.leads)
        
        # 2. Remove Duplicates (The "Analyst" Job)
        initial_count = len(df)
        df.drop_duplicates(subset=['url'], keep='first', inplace=True)
        removed_count = initial_count - len(df)
        
        # 3. Add Timestamp
        df['date_scraped'] = datetime.now().strftime("%Y-%m-%d")
        
        # 4. Save
        filename = f"{self.name}_leads_clean.xlsx"
        df.to_excel(filename, index=False)
        
        print(f"🧹 Cleaned Data: Removed {removed_count} duplicates.")
        print(f"📊 Report Ready: {filename}")
    def visualize_data(self):
        if not self.leads: return

        import matplotlib.pyplot as plt
        import pandas as pd

        # 1. Load Data
        df = pd.DataFrame(self.leads)
        
        # 2. Count Keywords (Simple Analytics)
        # We will count how many times "AI", "Python", and "Bot" appear
        keywords = ["AI", "Python", "Bot", "Freelance", "Engineer"]
        counts = []
        
        for word in keywords:
            # Check how many titles contain this word (Case insensitive)
            count = df['title'].str.contains(word, case=False).sum()
            counts.append(count)
            
        # 3. Draw the Chart
        plt.figure(figsize=(10, 6)) # Size of the image
        plt.bar(keywords, counts, color='skyblue') # Bar chart
        
        plt.title(f"Job Market Analysis for {self.name}")
        plt.xlabel("Skills")
        plt.ylabel("Number of Jobs Found")
        
        # 4. Save the Image
        image_name = f"{self.name}_chart.png"
        plt.savefig(image_name)
        print(f"📈 Chart Generated: {image_name}")
        
        # Optional: Show it on screen
        # plt.show()

# --- 3. THE EXECUTION ---
if __name__ == "__main__":
    # Create the Team
    bot = WebAgent("Agent_007")
    manan = Client("Manan", assigned_agent=bot)

    # Run the Job
    print(manan.run_automation('https://duckduckgo.com'))
    
    # Save the Work
    manan.save_to_json()       # The "Memory"
    manan.clean_and_export()   # The "Product"
    manan.visualize_data()     # 3. Graph Image