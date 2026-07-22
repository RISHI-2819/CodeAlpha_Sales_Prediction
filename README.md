# 📈 AI Business Intelligence & Sales Analytics Platform

[![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat&logo=html5&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/HTML)
[![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=flat&logo=css3&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/CSS)
[![JavaScript](https://img.shields.io/badge/JavaScript-ES6%2B-F7DF1E?style=flat&logo=javascript&logoColor=black)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=flat&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![Chart.js](https://img.shields.io/badge/Chart.js-4.0-FF6384?style=flat&logo=chartdotjs&logoColor=white)](https://www.chartjs.org/)
[![Plotly](https://img.shields.io/badge/Plotly.js-2.24-3F4F75?style=flat&logo=plotly&logoColor=white)](https://plotly.com/javascript/)
[![PapaParse](https://img.shields.io/badge/PapaParse-5.4-green?style=flat)](https://www.papaparse.com/)
[![License](https://img.shields.io/badge/License-MIT-brightgreen.svg)](LICENSE)

> **Commercial-Grade Enterprise Business Intelligence & AI Sales Analytics SaaS Platform** combining sales prediction, 100 products inventory catalog, 200 customer lifetime value analytics, marketing campaign ROI tracking, AI business recommendations, financial accounting, and 1-click report generation.

---

## 🚀 Enterprise Platform Features

### 📊 1. Executive Overview Dashboard
- Real-time KPI summary cards: **Today's Sales**, **Yearly Revenue ($3.82M)**, **Net Profit Margin ($1.45M / 38.0%)**, **Conversion Rate (5.12%)**, Orders, Customers, Advertising Budget, and Health Score.
- Interactive **Chart.js** 12-Month Sales & Revenue trend line charts.
- Interactive **Plotly.js** advertising correlation heatmap.

### 📦 2. Product Catalog & Inventory Management (100 Items)
- **100 Realistic Enterprise Products** pre-loaded with images, brands, categories (*Electronics, Audio & Sound, Wearables, Accessories, Smart Home*), MRP, Selling Price, Cost, Profit Margins, Stock levels, Rating ⭐, and Reviews.
- Search filter, category filters, price sorting, and paginated grid layout (12 products per page).
- Stock status tracking (*In Stock, Low Stock Warning, Out of Stock*), supplier details, and warranty info.

### 👥 3. Customer Analytics & CLV Tracking (200 Customers)
- **200 Customer Profiles** featuring Location, Demographics, Purchase Counts, Total Spending, Favorite Categories, and calculated **Customer Lifetime Value (CLV)**.
- Customer loyalty classification (*VIP Gold, Silver Member, Standard*).

### 🛒 4. Order Management & Financial Accounting
- Transaction logs table capturing Order ID, Product, Customer, Date, Status (*Delivered, Processing, Shipped*), Payment Method, Revenue, and Profit.
- Financial statement overview: Gross Revenue, Operating Costs, Net Profit, and Profit Margin.

### 🤖 5. AI Sales Predictor & AI Business Advisor
- Multi-channel spend inputs ($TV, Radio, Newspaper, Discount, Price$).
- Predicts expected sales volume, revenue output, profit return, confidence rating %, and ROI.
- **Rule-based AI Advisor**: Automatically generates strategic recommendations (e.g. *"Shift 12% budget from Newspaper to TV for optimal reach"*).

### 📈 6. Marketing Analytics & Campaign ROI
- Multi-channel campaign performance comparison (*Digital Ads, Social Media, TV Ads, Radio Ads, Email Marketing*).

### 🌐 7. Multilingual & Theme Customization
- Built-in instant switcher for **English** and **தமிழ் (Tamil)** UI labels.
- Glassmorphic UI design system with persistent **Dark Mode** and **Light Mode**.

### 📑 8. One-Click Executive Reports & Exports
- Download full **Products CSV** and **Customers CSV** reports.
- **Print Dashboard View** (`@media print`) formatted for board presentations.

---

## 🛠️ Technology Stack

| Component | Technology |
| :--- | :--- |
| **Frontend Core** | HTML5, CSS3 (Glassmorphism), JavaScript (ES6+), Bootstrap 5.3 |
| **Data Visualizations** | Chart.js 4.0, Plotly.js 2.24 |
| **CSV Parsing & Export** | PapaParse 5.4 |
| **Data Storage & State** | Browser LocalStorage API & Local JSON Datasets |

---

## 📁 Repository Architecture

```text
Sales-Prediction-AI/
├── index.html              # Main Single Page Application (All Modules & Modals)
├── style.css               # Apple/Google/Microsoft UI System (Dark/Light Themes, Glassmorphism)
├── script.js               # Core Enterprise Engine (JS ML Engine, Charts, Router, CSV Exporter)
├── dataset/
│   ├── advertising.csv     # Kaggle Advertising Dataset (200 records)
│   ├── products.json       # 100 Realistic Enterprise Products
│   ├── customers.json      # 200 Detailed Customer Profiles
│   ├── orders.json         # Order Transactions Dataset
│   └── inventory.json      # Inventory Warehouse Dataset
├── images/                 # SVG Assets & Vector Graphics
└── README.md               # Production Documentation
```

---

## ⚡ How to Run

No backend, Python server, or installation required!

1. **Option 1**: Open [`index.html`](file:///c:/Users/rishi/Desktop/project%20rishi3/index.html) directly in any modern web browser.
2. **Option 2** (Live Server):
   ```bash
   python -m http.server 8000
   ```
   Navigate to `http://localhost:8000`.

- **Default Admin Credentials**: Username `admin` | Password `admin123`

---

## 📜 License

This enterprise platform is released under the [MIT License](LICENSE).
