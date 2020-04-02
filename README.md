# Dynoscaler

An easy to use python script to scale Heroku dynos on any running app inside Heroku. 
This uses very basic cron jobs to scale the application at certain intervals during the day. 
It also includes a basic health check to scale up pods if the application is not responding.

## Things to add

- Real auto scaling: so it will scale up and down based on traffic
- Metrics dashboard to show current stats
- Alerting/Notifications