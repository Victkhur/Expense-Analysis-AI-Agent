import chainlit as cl
import pandas as pd
import numpy as np
import os
from expense_analyzer import ExpenseAnalyzer

@cl.on_chat_start
async def start():
    # Initialize session state
    cl.user_session.set("analyzer", None)
    
    # Prompt user to upload a CSV file or use sample data
    response = await cl.AskActionMessage(
        content="Would you like to upload your expense CSV file or use sample data?",
        actions=[
            cl.Action(name="upload", payload={"value": "upload"}, label="Upload CSV"),
            cl.Action(name="sample", payload={"value": "sample"}, label="Use Sample Data")
        ]
    ).send()
    
    if response and response.get("payload").get("value") == "sample":
        # Generate sample CSV
        sample_data = pd.DataFrame({
            'date': pd.date_range(start='2025-01-01', periods=100, freq='D'),
            'category': ['Uncategorized']*100,
            'amount': np.random.normal(100, 50, 100).round(2),
            'description': ['Coffee shop', 'Flight ticket', 'Electric bill', 'Movie ticket'] * 25
        })
        sample_csv_path = "sample_expenses.csv"
        sample_data.to_csv(sample_csv_path, index=False)
        await cl.Message(content="Sample CSV generated.").send()
        await process_csv(sample_csv_path)
    elif response and response.get("payload").get("value") == "upload":
        # Prompt for file upload
        files = await cl.AskFileMessage(
            content="Please upload your expense CSV file (must contain 'date', 'category', 'amount', 'description' columns)",
            accept=["text/csv"],
            max_size_mb=10
        ).send()
        
        if files:
            await process_csv(files[0].path)
        else:
            await cl.Message(content="No file uploaded. Please try again.").send()
    else:
        await cl.Message(content="No action selected. Please choose an option.").send()

async def process_csv(file_path):
    try:
        # Initialize and process the data
        analyzer = ExpenseAnalyzer(contamination=0.1)
        analyzer.load_data(file_path)
        analyzer.auto_categorize()
        analyzer.detect_anomalies()
        analyzer.visualize_data()
        # Store analyzer in session
        cl.user_session.set("analyzer", analyzer)
        # Generate and display the report
        report_content = analyzer.generate_report()
        pdf_path = analyzer.generate_pdf_report()
        await cl.Message(content=report_content + f"\n\n[Download PDF Report](/{pdf_path})").send()
    except Exception as e:
        await cl.Message(content=f"Error processing file: {str(e)}").send()

@cl.on_message
async def handle_query(message: cl.Message):
    try:
        analyzer = cl.user_session.get("analyzer")
        if not analyzer or analyzer.data is None:
            await cl.Message(content="No data loaded. Please upload a CSV or use sample data first.").send()
            return
        
        content = message.content.lower()
        categories = ["food", "travel", "utilities", "entertainment"]
        
        if "budget" in content:
            budgets = analyzer.budgets
            response = f"Current budgets:\n" + "\n".join(f"{cat}: ${amt:.2f}" for cat, amt in budgets.items())
            response += "\n\nWould you like to update your budgets?"
            await cl.AskActionMessage(
                content=response,
                actions=[
                    cl.Action(name="update_budget", payload={"value": "update_budget"}, label="Update Budgets"),
                    cl.Action(name="cancel", payload={"value": "cancel"}, label="Cancel")
                ]
            ).send()
        elif any(cat in content for cat in categories):
            category = next(cat.capitalize() for cat in categories if cat in content)
            # Check for date range in query (e.g., "January 2025")
            date_filter = None
            months = ["january", "february", "march", "april", "may", "june", 
                      "july", "august", "september", "october", "november", "december"]
            for month in months:
                if month in content:
                    year = "2025" if "2025" in content else str(pd.Timestamp.now().year)
                    month_num = months.index(month) + 1
                    date_filter = f"{year}-{month_num:02d}"
                    break
            
            expenses = analyzer.data[analyzer.data['category'] == category][['date', 'amount', 'description']]
            if date_filter:
                expenses = expenses[expenses['date'].dt.strftime('%Y-%m') == date_filter]
            
            if not expenses.empty:
                response = f"{category} Expenses:\n{expenses.to_string(index=False)}"
            else:
                response = f"No {category} expenses found" + (f" for {date_filter}" if date_filter else ".")
            await cl.Message(content=response).send()
        elif "update_budget" in content:
            # Prompt for budget updates
            await prompt_budget_update()
        else:
            await cl.Message(content="Query not recognized. Try 'Show Food expenses', 'Check budget status', or 'Show Travel expenses for January 2025'.").send()
    except Exception as e:
        await cl.Message(content=f"Error processing query: {str(e)}").send()

async def prompt_budget_update():
    # Create a form for budget updates
    form = await cl.AskUserMessage(
        content="Enter new budget amounts (e.g., Food: 500, Travel: 1000). Leave blank to keep current value:",
        inputs=[
            cl.Input(id="food_budget", label="Food Budget ($)", type="number", default=str(cl.user_session.get("analyzer").budgets.get("Food", 500))),
            cl.Input(id="travel_budget", label="Travel Budget ($)", type="number", default=str(cl.user_session.get("analyzer").budgets.get("Travel", 1000))),
            cl.Input(id="utilities_budget", label="Utilities Budget ($)", type="number", default=str(cl.user_session.get("analyzer").budgets.get("Utilities", 300))),
            cl.Input(id="entertainment_budget", label="Entertainment Budget ($)", type="number", default=str(cl.user_session.get("analyzer").budgets.get("Entertainment", 200)))
        ]
    ).send()
    
    if form:
        analyzer = cl.user_session.get("analyzer")
        if analyzer:
            new_budgets = {
                "Food": float(form.get("food_budget")) if form.get("food_budget") else analyzer.budgets["Food"],
                "Travel": float(form.get("travel_budget")) if form.get("travel_budget") else analyzer.budgets["Travel"],
                "Utilities": float(form.get("utilities_budget")) if form.get("utilities_budget") else analyzer.budgets["Utilities"],
                "Entertainment": float(form.get("entertainment_budget")) if form.get("entertainment_budget") else analyzer.budgets["Entertainment"]
            }
            analyzer.budgets.update(new_budgets)
            await cl.Message(content=f"Budgets updated: {new_budgets}").send()

if __name__ == "__main__":
    cl.run()