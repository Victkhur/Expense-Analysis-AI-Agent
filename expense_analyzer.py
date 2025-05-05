import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import matplotlib.pyplot as plt
from datetime import datetime
import uuid
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet

class ExpenseAnalyzer:
    def __init__(self, contamination=0.1):
        """Initialize the analyzer with anomaly detection parameters."""
        self.contamination = contamination
        self.model = IsolationForest(contamination=contamination, random_state=42)
        self.data = None
        self.anomalies = None
        self.report_id = str(uuid.uuid4())
        self.output_dir = "public/reports"
        os.makedirs(self.output_dir, exist_ok=True)
        self.budgets = {
            "Food": 500,
            "Travel": 1000,
            "Utilities": 300,
            "Entertainment": 200
        }
        self.category_keywords = {
            "Food": ["coffee", "restaurant", "cafe", "lunch", "dinner", "grocery"],
            "Travel": ["flight", "uber", "taxi", "hotel", "train"],
            "Utilities": ["electric", "water", "internet", "bill"],
            "Entertainment": ["movie", "concert", "game", "ticket"]
        }

    def load_data(self, data_path):
        """Load expense data from a CSV file."""
        try:
            self.data = pd.read_csv(data_path)
            required_columns = ['date', 'category', 'amount', 'description']
            if not all(col in self.data.columns for col in required_columns):
                raise ValueError("CSV must contain 'date', 'category', 'amount', 'description' columns")
            self.data['date'] = pd.to_datetime(self.data['date'])
            print("Data loaded successfully.")
        except Exception as e:
            print(f"Error loading data: {e}")
            raise

    def auto_categorize(self):
        """Automatically categorize expenses based on description keywords."""
        if self.data is None:
            raise ValueError("No data loaded. Call load_data first.")
        
        def categorize_description(description):
            description = description.lower()
            for category, keywords in self.category_keywords.items():
                if any(keyword in description for keyword in keywords):
                    return category
            return "Other"
        
        self.data['category'] = self.data['description'].apply(categorize_description)
        print("Automatic categorization completed.")

    def preprocess_data(self):
        """Preprocess data for anomaly detection."""
        self.data['day_of_week'] = self.data['date'].dt.dayofweek
        self.data['month'] = self.data['date'].dt.month
        features = self.data[['amount', 'day_of_week', 'month']].values
        return features

    def detect_anomalies(self):
        """Detect anomalies using Isolation Forest."""
        if self.data is None:
            raise ValueError("No data loaded. Call load_data first.")
        
        features = self.preprocess_data()
        self.data['anomaly'] = self.model.fit_predict(features)
        self.anomalies = self.data[self.data['anomaly'] == -1]
        print(f"Detected {len(self.anomalies)} anomalies.")

    def generate_summary(self):
        """Generate a summary of expenses, anomalies, and budget status."""
        if self.data is None:
            raise ValueError("No data loaded. Call load_data first.")
        
        total_expenses = self.data['amount'].sum()
        avg_expense = self.data['amount'].mean()
        category_breakdown = self.data.groupby('category')['amount'].sum()
        anomaly_count = len(self.anomalies) if self.anomalies is not None else 0
        
        budget_status = {}
        for category, budget in self.budgets.items():
            spent = category_breakdown.get(category, 0)
            budget_status[category] = {
                'budget': budget,
                'spent': spent,
                'remaining': budget - spent,
                'status': 'Over budget' if spent > budget else 'Within budget'
            }
        
        summary = {
            'total_expenses': total_expenses,
            'avg_expense': avg_expense,
            'category_breakdown': category_breakdown,
            'anomaly_count': anomaly_count,
            'budget_status': budget_status
        }
        return summary

    def visualize_data(self):
        """Generate visualizations for expenses and anomalies."""
        if self.data is None:
            raise ValueError("No data loaded. Call load_data first.")
        
        # Plot 1: Expense trend over time
        plt.figure(figsize=(10, 6))
        self.data.groupby(self.data['date'].dt.date)['amount'].sum().plot()
        plt.title('Daily Expense Trend')
        plt.xlabel('Date')
        plt.ylabel('Total Expenses ($)')
        plt.grid(True)
        plt.savefig(f"{self.output_dir}/expense_trend_{self.report_id}.png")
        plt.close()

        # Plot 2: Category breakdown
        plt.figure(figsize=(10, 6))
        self.data.groupby('category')['amount'].sum().plot(kind='bar')
        plt.title('Expenses by Category')
        plt.xlabel('Category')
        plt.ylabel('Total Expenses ($)')
        plt.grid(True)
        plt.savefig(f"{self.output_dir}/category_breakdown_{self.report_id}.png")
        plt.close()

        # Plot 3: Anomalies scatter plot
        if self.anomalies is not None and not self.anomalies.empty:
            plt.figure(figsize=(10, 6))
            plt.scatter(self.data['date'], self.data['amount'], c='blue', label='Normal', alpha=0.5)
            plt.scatter(self.anomalies['date'], self.anomalies['amount'], c='red', label='Anomaly', alpha=0.8)
            plt.title('Expense Anomalies')
            plt.xlabel('Date')
            plt.ylabel('Amount ($)')
            plt.legend()
            plt.grid(True)
            plt.savefig(f"{self.output_dir}/anomalies_{self.report_id}.png")
            plt.close()

    def generate_report(self):
        """Generate a detailed financial report with budget analysis."""
        summary = self.generate_summary()
        budget_status_str = "\n".join(
            f"{cat}: Budget ${status['budget']:.2f}, Spent ${status['spent']:.2f}, "
            f"Remaining ${status['remaining']:.2f} ({status['status']})"
            for cat, status in summary['budget_status'].items()
        )
        
        report_content = f"""
# Financial Report
## Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
## Report ID: {self.report_id}

## Executive Summary
- **Total Expenses**: ${summary['total_expenses']:.2f}
- **Average Transaction**: ${summary['avg_expense']:.2f}
- **Number of Anomalies Detected**: {summary['anomaly_count']}

## Category Breakdown
{summary['category_breakdown'].to_string(header=False)}

## Budget Status
{budget_status_str}

## Anomaly Details
{self.anomalies[['date', 'category', 'amount', 'description']].to_string(index=False) if self.anomalies is not None and not self.anomalies.empty else "No anomalies detected."}

## Actionable Insights
1. **Review High-Value Transactions**: Investigate anomalies flagged in the report.
2. **Optimize Spending**: Categories with high expenses (e.g., {summary['category_breakdown'].idxmax() if not summary['category_breakdown'].empty else 'N/A'}) may offer cost reduction opportunities.
3. **Monitor Budgets**: Check categories marked as 'Over budget' and adjust spending.

## Visualizations
![Daily Expense Trend](/public/reports/expense_trend_{self.report_id}.png)
![Category Breakdown](/public/reports/category_breakdown_{self.report_id}.png)
![Anomalies](/public/reports/anomalies_{self.report_id}.png)

## Recommendations
- Implement automated alerts for transactions exceeding ${summary['avg_expense']*3:.2f}.
- Review budget status monthly to stay within limits.
- Consider forecasting models for future expense planning.
"""
        return report_content

    def generate_pdf_report(self):
        """Generate a PDF version of the report."""
        summary = self.generate_summary()
        budget_status_str = "\n".join(
            f"{cat}: Budget ${status['budget']:.2f}, Spent ${status['spent']:.2f}, "
            f"Remaining ${status['remaining']:.2f} ({status['status']})"
            for cat, status in summary['budget_status'].items()
        )
        
        pdf_path = f"{self.output_dir}/financial_report_{self.report_id}.pdf"
        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Add title
        story.append(Paragraph(f"Financial Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Title']))
        story.append(Spacer(1, 12))

        # Executive Summary
        story.append(Paragraph("Executive Summary", styles['Heading2']))
        story.append(Paragraph(f"Total Expenses: ${summary['total_expenses']:.2f}", styles['Normal']))
        story.append(Paragraph(f"Average Transaction: ${summary['avg_expense']:.2f}", styles['Normal']))
        story.append(Paragraph(f"Number of Anomalies Detected: {summary['anomaly_count']}", styles['Normal']))
        story.append(Spacer(1, 12))

        # Category Breakdown
        story.append(Paragraph("Category Breakdown", styles['Heading2']))
        for line in summary['category_breakdown'].to_string(header=False).split('\n'):
            story.append(Paragraph(line.strip(), styles['Normal']))
        story.append(Spacer(1, 12))

        # Budget Status
        story.append(Paragraph("Budget Status", styles['Heading2']))
        for line in budget_status_str.split('\n'):
            story.append(Paragraph(line.strip(), styles['Normal']))
        story.append(Spacer(1, 12))

        # Visualizations
        story.append(Paragraph("Visualizations", styles['Heading2']))
        for img in [
            f"{self.output_dir}/expense_trend_{self.report_id}.png",
            f"{self.output_dir}/category_breakdown_{self.report_id}.png",
            f"{self.output_dir}/anomalies_{self.report_id}.png"
        ]:
            if os.path.exists(img):
                story.append(Image(img, width=400, height=200))
                story.append(Spacer(1, 12))

        doc.build(story)
        return pdf_path