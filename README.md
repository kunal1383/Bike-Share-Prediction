
# Bike Share Prediction Project

## Table of Contents
- [Project Description](#project-description)
- [Important Notes](#important-notes)
- [Dataset Source](#dataset-source)
- [Getting Started](#getting-started)
- [User Interface](#user-interface)
- [Contributor](#contributor)

## Project Description

Bike-sharing systems have evolved as an integral part of urban transportation solutions worldwide. The availability of bikes precisely where and when users need them is vital for their widespread adoption.

**Objective:** Our goal was to develop a machine learning model capable of accurately predicting the demand for bike rentals on a daily basis. By achieving this, we aimed to assist bike-sharing providers in optimizing their resource allocation strategies, leading to increased user satisfaction and operational efficiency.

**Key Findings:**
- Successful creation of an end-to-end regression model.
- Model trained on historical data to predict bike rentals.
- Model evaluation metrics include Mean Absolute Error (MAE), Root Mean Squared Error (RMSE), and R².
- Model deployed and hosted on AWS Elastic Beanstalk.
- Continuous Integration/Continuous Deployment (CI/CD) pipeline established using GitHub Actions.
- User interface created for model testing and predictions.

**Significance:** Accurate bike rental prediction contributes to efficient resource allocation, reduced operational costs, and improved user experiences, making it a crucial component of modern urban transportation systems.

## Important Notes

1. **API Keys and Database Credentials:**
   - To run this project, you'll need your own OpenWeather API key, which should be placed in the `utils.py` file.
   - You also need your Cassandra database credentials, including `cassandra-token` and the `secure-connect-cassandra.zip` file from your own Cassandra account. These files should be placed in the `Cassandra` folder of the project.

2. **Dataset Source:**
   - The dataset used in this project is sourced from the UC Irvine Machine Learning Repository. You can find it [here](https://archive.ics.uci.edu/ml/datasets/Bike+Sharing+Dataset).

## Getting Started

Follow these steps to set up and run the project:

1. Create a new virtual environment using Conda with Python 3.8:

   ```bash
   conda create --name bike-share python=3.8
   ```

2. Activate the virtual environment:

   ```bash
   conda activate bike-share
   ```

3. Install project dependencies from the `requirements.txt` file:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:

   ```bash
   python application.py
   ```

## User Interface

Below is a screenshot of the project's user interface:

![Application](https://github.com/kunal1383/Bike-Share-Prediction/assets/48025219/38627cc7-f864-4fd9-8baa-019313fd06a0)
![result](https://github.com/kunal1383/Bike-Share-Prediction/assets/48025219/e7fb55fa-6a7d-4e81-85b9-6679fe8c0e28)

## Contributor

- Kunal Barve
```
