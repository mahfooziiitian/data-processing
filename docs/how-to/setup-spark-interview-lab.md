---
diataxis: how-to
---

# Set up the Spark interview lab

Use an existing local PySpark 4.x environment to run the batch examples
from the [second mock interview](../explanation/data-processing-patterns-company-interviews.md#part-5-full-mock-interview-walmart-global-tech-principal-data-engineer-round-2).

1. Open a Python session or notebook in that environment and run this code
   to create a local Spark session with UTC timestamps.

   ```python
   from pyspark.sql import SparkSession, functions as F
   from pyspark.sql.window import Window
   from pyspark.sql.types import (
       StructType, StructField, StringType,
       IntegerType, LongType, DoubleType,
       TimestampType,
   )

   spark = (
       SparkSession.builder
       .appName("Walmart-Principal-DE-Round2")
       .master("local[4]")
       .config("spark.sql.shuffle.partitions", "4")
       .config("spark.sql.session.timeZone", "UTC")
       .getOrCreate()
   )
   spark.sparkContext.setLogLevel("WARN")
   ```

2. Run `spark.range(1).count()` in the same session. A result of `1`
   confirms that the session can execute a job. Keep the session open
   while you work through the examples.

Use a compatible Delta-enabled Spark environment for exercises that
write Delta tables. Streaming snippets that use an `input_path` need
a directory of input files matching the schema in the question.
