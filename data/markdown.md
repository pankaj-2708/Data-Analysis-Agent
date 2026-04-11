# Financial Analysis Report: UPI Transactions Export

## 📌 Overview
This report provides a comprehensive analysis of the UPI transaction history for **Pankaj Maulekhi**, covering the period from **March 16, 2025, to March 14, 2026**. The dataset consists of 267 records, predominantly tracking expenditures in GBP. The analysis focuses on spending habits, category distributions, and temporal trends to identify financial patterns.

---

## 📊 Dataset Overview

### Structural Integrity
- **Total Records**: 267
- **Currency**: GBP (Constant)
- **Wallet**: UPI (Constant)
- **Author**: Pankaj Maulekhi (Constant)
- **Data Quality**: The dataset is clean with no duplicate entries. However, there is high sparsity in the `Note` column (80.9% null) and total emptiness in the `Labels` column (100% null).

### Key Transaction Statistics
| Statistic | Value (GBP) |
| :--- | :--- |
| **Total Income** | £18.67 |
| **Total Expenses** | -£250.21 |
| **Net Balance** | **-£231.54** |
| **Average Daily Spend** | £1.44 |
| **Peak Single Day Spend** | £12.64 (2026-01-17) |

---

## 🔍 Key Spending Insights

### 1. Category Distribution
Spending is heavily skewed toward a few primary categories. **Food & Drink** is the dominant category by far, accounting for nearly 70% of all transaction counts.

| Category | Transaction Count | Proportion (%) |
| :--- | :---: | :---: |
| **Food & Drink** | 186 | 69.66% |
| Shopping | 20 | 7.49% |
| Other | 15 | 5.62% |
| Education | 14 | 5.24% |
| Groceries | 11 | 4.12% |

**Visual Analysis: Frequency & Composition**

![Category Frequency](C:/Users/panka/genai_project/data_analysis_agent/data/category_frequency_bar.png)
*Figure 1: Frequency of transactions per category.*

![Spending Composition](C:/Users/panka/genai_project/data_analysis_agent/data/spending_composition_pie.png)
*Figure 2: Proportion of total spending across the top 5 categories.*

### 2. Pareto Analysis (The 80/20 Rule)
Only **3 categories** (Food & Drink, Shopping, and Bills & Fees) account for **80.68%** of the total expenditures. This suggests that budget optimization should focus almost exclusively on these three areas to achieve a significant impact.

### 3. Spending Behavior & Volatility
While Food & Drink is the most frequent, it consists of small, consistent micro-transactions. Conversely, **Shopping** exhibits the highest volatility and the highest average transaction value (-£3.02).

![Amount Distribution](C:/Users/panka/genai_project/data_analysis_agent/data/amount_distribution_histogram.png)
*Figure 3: Distribution of transaction amounts.*

![Spending Density](C:/Users/panka/genai_project/data_analysis_agent/data/amount_density_kde.png)
*Figure 4: Density distribution of expenses vs income.*

![Category Violin Plot](C:/Users/panka/genai_project/data_analysis_agent/data/category_spending_violin.png)
*Figure 5: Spending density and shape per category.*

![Category Box Plot](C:/Users/panka/genai_project/data_analysis_agent/data/category_amount_boxplot.png)
*Figure 6: Outliers and variance across categories.*

---

## 🕒 Temporal Analysis

### Daily & Weekly Patterns
- **Peak Day**: **Saturdays** are the highest spending days, with the highest total volume (£62.73) and average transaction value (£1.31).
- **Peak Hour**: The most frequent transaction hour is **3:00 PM**, while the highest financial outflow occurs around **1:00 PM**.

### Monthly Trends
Spending fluctuates throughout the year, with peaks observed in **August 2025** (£37.10) and **January 2026** (£35.93).

**Visual Time-Series Analysis**

![Daily Spending Area](C:/Users/panka/genai_project/data_analysis_agent/data/daily_spending_area.png)
*Figure 7: Daily spending trend throughout the year.*

![Spending Time Scatter](C:/Users/panka/genai_project/data_analysis_agent/data/spending_time_scatter.png)
*Figure 8: Individual transaction spikes over time.*

![Cumulative Spending](C:/Users/panka/genai_project/data_analysis_agent/data/cumulative_spending_line.png)
*Figure 9: Growth of total expenditures over the period.*

![Monthly Category Stack](C:/Users/panka/genai_project/data_analysis_agent/data/monthly_category_stack.png)
*Figure 10: Monthly distribution of transactions by category.*

---

## 📈 Comparative & Hierarchical Analysis

### Half-Yearly & Monthly Comparison
Analysis of spending shifts shows how categories evolve over time, specifically comparing the start of the period (March 2025) to the end (March 2026).

![Half Yearly Comparison](C:/Users/panka/genai_project/data_analysis_agent/data/category_comparison_half_yearly.png)
*Figure 11: Category spending comparison: First half vs Second half of the year.*

![Spending Slope](C:/Users/panka/genai_project/data_analysis_agent/data/spending_slope_comparison.png)
*Figure 12: Slope chart comparing top 5 categories between the first and last months.*

### Spending Hierarchy

![Spending Sunburst](C:/Users/panka/genai_project/data_analysis_agent/data/spending_hierarchy_sunburst.png)
*Figure 13: Hierarchical breakdown of spending by Type and Category.*

---

## 🏁 Final Conclusions
- **Financial Position**: The account is in a net deficit of **£231.54**, reflecting a typical expense-tracking ledger where income is recorded infrequently.
- **Spending Habit**: The user has a high frequency of small-ticket items, primarily in the **Food & Drink** category, with spending peaking on weekends.
- **Actionable Insight**: To reduce the burn rate, focusing on reducing the frequency of "Food & Drink" transactions and the magnitude of "Shopping" expenses would be most effective.