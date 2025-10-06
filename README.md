# 💰 AWS Cost Dashboard

A simple FinOps project that tracks AWS spending using the **AWS Cost Explorer API**.  
This dashboard fetches daily cost data by service and presents it in a clean, easy-to-read format.

---

## 🚀 Features
- Fetches real AWS billing data with `boto3`
- Breaks down cost by date and service
- Easily extendable to add graphs (e.g. Matplotlib, Plotly)
- Great for FinOps learning or interview portfolio

---

## 🧠 Tech Stack
- Python
- AWS SDK (boto3)
- Pandas

---

## 📊 Example Output
| Date       | Service    | Cost ($) |
| ---------- | ---------- | -------- |
| 2025-10-01 | Amazon EC2 | 1.23     |
| 2025-10-01 | Amazon S3  | 0.05     |

---

## 🔧 How to Run
```bash
git clone https://github.com/EmmanuellaAlaso/aws-cost-dashboard.git
cd aws-cost-dashboard
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python get_cost_data.py
