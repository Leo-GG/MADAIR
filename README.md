# MADAIR

Madrid's air quality data visualization.
This is a simple web application for interactive data visualization using [Streamlit](http://streamlit.io/). 

# [ACCESS THE APP](https://github.com/Leo-GG/MADAIR)

I gathered public data from the [official city hall repository](https://datos.madrid.es/), merged and cleaned it, ran a quick outlier detection process and uploaded them to an [AWS RDS](http://aws.com/rds). The data consists of measurements of different air contaminants at different locations in the city in the period between 2001 and 2024. 

- Follow the [Gather_data](https://github.com/Leo-GG/MADAIR/blob/main/Gather_data.ipynb) notebook to see how I downloaded the data.
- The [Outlier_detection](https://github.com/Leo-GG/MADAIR/blob/main/Outlier_detection.ipynb) notebook has code to run a simple detection process, in which any measure larger than 5 times the standard deviation for a given contaminant and measuring station is labeled as an outlier.
- On the [Gen_DB](https://github.com/Leo-GG/MADAIR/blob/main/Gen_DB.ipynb) notebook you can see how I created a database on the AWS server and how I uploaded the data.
