# 🏙️ CityX ETL Data Pipeline

CityX is a Dockerized ETL pipeline that extracts crime and district data from structured JSON and a scanned PDF file, transforms it using Python and OCR, and loads it into a PostgreSQL database — ready for use in Power BI. <br><br>

---

## 🧠 What This Project Does 

1. Extracts raw data from:
   - A JSON file of crime records
   - A scanned PDF file containing district data (via OCR)

2. Transforms the data:
   - Cleans and standardizes values
   - Converts units, fixes typos, parses timestamps
   - Merges both data sources

3. Loads the final dataset into:
   - A PostgreSQL table: `core.transformed_crime_data`

The PostgreSQL container stays running and exposes the database so tools like Power BI can connect and use the clean data directly.<br><br><br>

---

## 🚀 How to Run This Project

> <br>✅ You **do not** need to install Python, PostgreSQL, Tesseract, or Poppler. Everything runs inside Docker.<br><br>

### 1. Install Docker

Download and install Docker Desktop:  
👉 https://www.docker.com/products/docker-desktop <br><br><br>

---

### 2. Clone the Project

If you have Git:

```bash
git clone https://github.com/abdrasheed/city_x.git
cd "Crime ETL Docker"
```
<br><br><br>

---
### 3. Run the Project with Docker

In the root of the project (where `docker-compose.yml` is located), run:

```bash
docker-compose up --build
```

#### This command will:

- Start the PostgreSQL container with the credentials defined in .env

- Initialize the database and tables from db/init.sql

- Build and run the ETL container

- Automatically execute the Python ETL script

#### Once successful, you will see output similar to:<br><br><br>

```bash
✅ Database connection successful
✅ Crime data extracted into STAGING Crime table successfully
✅ District data extracted into STAGING Ditrict table successfully
✅ Data transformed and loaded into CORE Crime full data table successfully.
✅ Staging tables truncated successfully.
✅ ETL Data Pipeline has been executed successfully ✅
```
##### If you do not see this message in the terminal, PLEASE RE-RUN THE SAME COMMAND.
```bash
docker-compose up --build
```
OR:
```bash
docker exec cityx_etl python etl.py
```

#### The PostgreSQL container will remain running and exposed on localhost:5432.

---
### 4. Re-run the ETL (if needed)
If you modify the input files (`crime_records.json`, `district_info.pdf`), you can re-run the ETL process:

```bash
docker exec cityx_etl python etl.py
```
<br><br><br>


---
# 📊 Connect Power BI to the PostgreSQL Container
This project includes a ready-made Power BI report file.

### 🔹 Location: Power BI Dashboard/Dashboard.pbix


### 🔹 To Open and Use It:

1. Open `Dashboard.pbix` in **Power BI Desktop**
2. If prompted, update the database connection:
   - **Server**: `localhost:5432`
   - **Database**: `cityx_db`
   - **Username**: `postgres`
   - **Password**: `1234`
3. Click **Load** or **Apply Changes**

The dashboard will connect to the PostgreSQL container and load the data from `core.transformed_crime_data`.

> <br> ✅ Make sure the **Docker Postgres container** are running (`docker-compose up`) before opening the dashboard. <br><br>


<br><br><br>
---

## 🤝 Contributing

Contributions, suggestions, and improvements are welcome.  
If you find a bug or want to add a feature, feel free to open an issue or submit a pull request.

---

## 📫 Contact

For questions, feedback, or collaboration:  
**Abdelrahman Alarqan** — Abdelalarqan@gmail.com  
GitHub: [github.com/abdrasheed](https://github.com/abdrasheed)

---

## 📝 License

This project is licensed under the **MIT License** — you are free to use, modify, and distribute with attribution.

---

## ✅ Project Status

CityX ETL is complete and fully functional.  
You can clone, run, and connect to Power BI with zero local setup — everything runs inside Docker.










# city_x
# city_x
