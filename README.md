VOCMax
VOCMax is an application designed to provide customers with a comprehensive dashboard for monitoring and benchmarking the performance of their photovoltaic (PV) plants. The app offers valuable insights into the efficiency and productivity of solar energy systems by visualizing real-time and historical data, enabling users to make informed decisions and optimize energy output.

Features
Dashboard Overview: View real-time and historical performance metrics for your PV plants, including energy production, efficiency, and system health.
Performance Benchmarking: Compare the performance of your PV plants against standard benchmarks to identify areas for improvement.
Data Visualization: Interactive graphs and charts that provide insights into various aspects of solar plant performance, including hourly, daily, and monthly energy production.
Multi-Plant Support: Monitor multiple PV installations from a single dashboard, with the ability to drill down into individual plant performance.
User Permissions: Customizable user access, allowing different levels of data visibility and dashboard customization based on roles.
Alerts & Notifications: Set up notifications for performance thresholds or maintenance alerts.
Installation
To install the VOCMax application, follow these steps:

Clone the repository:

bash
Copy code
git clone https://github.com/MarcelSpeen/pv_p3_dash.git
Navigate to the project directory:

bash
Copy code
cd pv_p3_dash
Install the required dependencies:

bash
Copy code
pip install -r requirements.txt
Set up the database:

Ensure you have a PostgreSQL server running.
Configure the database connection in the Django settings.
Run migrations:
bash
Copy code
python manage.py migrate
Run the server:

bash
Copy code
python manage.py runserver
Access the application:

Open a web browser and go to http://localhost:8000.
Usage
Login to the Dashboard:

Use your credentials to log in. Different user roles will have access to different levels of data.
View Solar Plant Performance:

Navigate through the dashboard to view energy production, efficiency, and benchmarking metrics.
Benchmark Your PV Plant:

Compare your plant's performance with industry benchmarks to determine if it's performing optimally.
Manage Alerts and Notifications:

Set up alerts for underperformance or maintenance needs.
Configuration
Environment Variables
Configure the following environment variables in a .env file:

DATABASE_URL: Connection string for the PostgreSQL database.
SECRET_KEY: The Django secret key for security.
DEBUG: Set to True for development and False for production.
Contributing
Contributions to VOCMax are welcome! To contribute:

Fork the repository.
Create a new branch (git checkout -b feature-branch).
Commit your changes (git commit -am 'Add new feature').
Push to the branch (git push origin feature-branch).
Create a new Pull Request.
License
This project is licensed under the MIT License. See the LICENSE file for more details.

Contact
For questions or support, please contact:

Developer: Marcel van der Veen
Email: your.email@example.com
