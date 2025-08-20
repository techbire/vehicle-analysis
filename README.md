# Vehicle Registration Dashboard

An interactive dashboard for analyzing vehicle registration data from the Vahan Dashboard, designed with an investor's perspective in mind.

🎯 **Live Demo**: [Deploy on Streamlit Cloud](https://share.streamlit.io)

## Features

- **YoY & QoQ Growth Analysis**: Track year-over-year and quarter-over-quarter growth rates
- **Vehicle Category Analysis**: Compare 2W, 3W, and 4W vehicle registrations
- **Manufacturer Insights**: Analyze manufacturer-wise registration trends
- **Interactive Filters**: Date range selection and category/manufacturer filters
- **Investor-Friendly UI**: Clean, professional interface built with Streamlit
- **Auto Data Generation**: Sample data generation for demo purposes

## Project Structure

```
vehicle-dashboard/
├── src/
│   ├── data_collector.py      # Data scraping and collection
│   ├── data_processor.py      # Data processing and calculations
│   ├── dashboard.py           # Main Streamlit dashboard
│   └── database.py            # Database operations
├── data/
│   ├── raw/                   # Raw scraped data
│   ├── processed/             # Processed data files
│   └── vehicle_data.db        # SQLite database
├── notebooks/
│   └── data_analysis.ipynb    # Exploratory data analysis
├── requirements.txt
└── README.md
```

## Installation

1. Clone the repository
```bash
git clone <repository-url>
cd vehicle-dashboard
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Run the data collector
```bash
python src/data_collector.py
```

4. Launch the dashboard
```bash
streamlit run src/dashboard.py
```

## Data Source

This project uses public data from the [Vahan Dashboard](https://vahan.parivahan.gov.in/vahan4dashboard/) which provides vehicle registration statistics across India.

## Technical Stack

- **Python**: Core programming language
- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive visualizations
- **SQLite**: Local database for data storage
- **BeautifulSoup/Selenium**: Web scraping tools

## Key Metrics

- Total vehicle registrations by category (2W/3W/4W)
- Manufacturer-wise registration data
- YoY and QoQ growth calculations
- Trend analysis and percentage changes

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.
