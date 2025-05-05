# Expense Analysis AI Agent

## Overview

The **Expense Analysis AI Agent** is a powerful tool designed to help users manage their personal or business finances by analyzing expense data, detecting anomalies, and generating actionable financial reports. Built with a user-friendly [Chainlit](https://docs.chainlit.io/) frontend, the application supports automatic expense categorization, budget tracking, conversational queries, and PDF report exporting. It leverages machine learning (Isolation Forest) for anomaly detection and provides insightful visualizations to aid financial decision-making.

### Key Features
- **Automatic Categorization**: Assigns categories (e.g., Food, Travel) to expenses based on description keywords.
- **Anomaly Detection**: Identifies unusual transactions using the Isolation Forest algorithm.
- **Budget Tracking**: Allows users to set and monitor category-specific budgets with alerts for overspending.
- **Conversational Interface**: Supports natural language queries (e.g., "Show Food expenses for January 2025") via Chainlit’s chat interface.
- **Report Generation**: Produces detailed financial reports with embedded visualizations and downloadable PDF versions.
- **Data Flexibility**: Processes user-uploaded CSV files or generates sample data for testing.

## Prerequisites

- **Python**: Version 3.8–3.11 (64-bit recommended).
- **Operating System**: Windows, macOS, or Linux.
- **Dependencies**: Listed in `requirements.txt` (see Installation).

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/<your-username>/expense-analysis-ai-agent.git
   cd expense-analysis-ai-agent
   ```

2. **Create a Virtual Environment**:
   ```bash
   python -m venv chainlit-env
   source chainlit-env/bin/activate  # On Windows: chainlit-env\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   The `requirements.txt` should include:
   ```
   chainlit==2.5.5
   pandas>=2.0.0
   numpy>=1.24.0
   scikit-learn>=1.2.0
   matplotlib>=3.7.0
   reportlab>=4.0.0
   pydantic==2.10.1
   ```

4. **Verify Installation**:
   ```bash
   chainlit --version
   ```
   Ensure Chainlit version 2.5.5 is installed.

## Usage

1. **Run the Application**:
   ```bash
   chainlit run app.py -w
   ```
   The `-w` flag enables auto-reloading. The app will open at `http://localhost:8000`.

2. **Interact with the Application**:
   - **Load Data**:
     - Select “Use Sample Data” to generate a 100-row CSV with example expenses.
     - Or select “Upload CSV” to upload a file with columns: `date`, `category`, `amount`, `description`. Example:
       ```csv
       date,category,amount,description
       2025-01-01,Uncategorized,50.25,Coffee shop
       2025-01-02,Uncategorized,200.00,Flight ticket
       ```
     - The app automatically categorizes expenses based on descriptions (e.g., “Coffee shop” → “Food”).
   - **View Report**: After loading data, a financial report appears with:
     - Total expenses, average transaction, and anomaly count.
     - Budget status (e.g., “Food: Budget $500, Spent $3200, Over budget”).
     - Visualizations (daily trends, category breakdown, anomalies).
     - A downloadable PDF report link.
   - **Query Expenses**: Use the chat interface to ask questions like:
     - “Show Food expenses”
     - “Show Travel expenses for January 2025”
     - “Check budget status”
   - **Update Budgets**: Type “Check budget status” and select “Update Budgets” to set new budget amounts via a form.

3. **Example Output**:
   ```markdown
   # Financial Report
   ## Generated on: 2025-05-05 11:09:00
   ## Report ID: <uuid>

   ## Executive Summary
   - **Total Expenses**: $10,123.45
   - **Average Transaction**: $101.23
   - **Number of Anomalies Detected**: 10

   ## Budget Status
   Food: Budget $500.00, Spent $3200.50, Remaining $-2700.50 (Over budget)
   ...

   ## Visualizations
   ![Daily Expense Trend](/public/reports/expense_trend_<uuid>.png)
   ...

   [Download PDF Report](/public/reports/financial_report_<uuid>.pdf)
   ```

   **Query Example**:
   - Input: “Show Food expenses”
   - Output:
     ```
     Food Expenses:
     date       amount  description
     2025-01-01  50.25  Coffee shop
     2025-01-05  75.00  Restaurant
     ...
     ```

## Project Structure

```
expense-analysis-ai-agent/
├── app.py                  # Chainlit frontend and main application logic
├── expense_analyzer.py     # Core logic for expense analysis, categorization, and reporting
├── public/reports/         # Directory for storing visualizations and PDF reports
├── requirements.txt        # Python dependencies
├── README.md              # Project documentation
└── sample_expenses.csv    # Generated sample data (created during runtime)
```

## Troubleshooting

- **Conversational Query Fails**: Ensure data is loaded before querying. If “Show Food expenses” returns no output, verify that the CSV was processed successfully and contains Food transactions.
- **PDF Link Broken**: Check that `public/reports/` is writable and `reportlab` is installed. Inspect the browser console for 404 errors.
- **Chainlit Errors**: Confirm Chainlit 2.5.5 and Pydantic 2.10.1 are installed:
  ```bash
  pip install chainlit==2.5.5 pydantic==2.10.1
  ```
- **CSV Format Issues**: Ensure uploaded CSVs have the required columns (`date`, `category`, `amount`, `description`). The `category` column can be “Uncategorized” as it will be overwritten by automatic categorization.

## Contributing

Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Make changes and commit (`git commit -m "Add your feature"`).
4. Push to your branch (`git push origin feature/your-feature`).
5. Open a Pull Request with a detailed description of your changes.

Please ensure your code follows PEP 8 style guidelines and includes tests where applicable.

## Future Enhancements

- **Expense Forecasting**: Predict future expenses using time series analysis (e.g., Prophet).
- **Bank Integration**: Import transactions via APIs like Plaid.
- **Interactive Visualizations**: Use Plotly for clickable charts.
- **Multi-User Support**: Add authentication for shared expense tracking.
- **Receipt Scanning**: Extract expense details from uploaded receipt images using OCR.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Chainlit](https://docs.chainlit.io/) for the interactive frontend.
- Uses [scikit-learn](https://scikit-learn.org/) for anomaly detection.
- Inspired by features in leading expense tracking apps like QuickBooks and YNAB.

## Contact

For questions or feedback, please open an issue on GitHub.
