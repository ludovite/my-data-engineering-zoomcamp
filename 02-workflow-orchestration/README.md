## Module 2 − Workflow Orchestration


We'll be working with the _green_ taxi dataset located here:

`https://github.com/DataTalksClub/nyc-tlc-data/releases/tag/green/download`

To get a `wget`-able link, use this prefix (note that the link itself gives 404):

`https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/`

### Assignment

So far in the course, we processed data for the year 2019 and 2020. Your task is to extend the existing flows to include data for the year 2021.

![homework datasets](../../../02-workflow-orchestration/images/homework.png)

As a hint, Kestra makes that process really easy:
1. You can leverage the backfill functionality in the [scheduled flow](../../../02-workflow-orchestration/flows/09_gcp_taxi_scheduled.yaml) to backfill the data for the year 2021. Just make sure to select the time period for which data exists i.e. from `2021-01-01` to `2021-07-31`. Also, make sure to do the same for both `yellow` and `green` taxi data (select the right service in the `taxi` input).
2. Alternatively, run the flow manually for each of the seven months of 2021 for both `yellow` and `green` taxi data. Challenge for you: find out how to loop over the combination of Year-Month and `taxi`-type using `ForEach` task which triggers the flow for each combination using a `Subflow` task.

### Quiz Questions

Complete the quiz shown below. It's a set of 6 multiple-choice questions to test your understanding of workflow orchestration, Kestra, and ETL pipelines.

1) To determine the uncompressed file size (e.g., yellow_tripdata_2020-12.csv) from Kestra `extract` task after execution, the follow-up task can be added immediatly after the `extract` task.
```yml
  - id: get_size
    type: io.kestra.plugin.core.storage.Size
    uri: "{{ outputs.extract.outputFiles[render(vars.file)] }}"
```
Within the execution for `Yellow` Taxi data for the year `2020` and month `12`: in `Outputs` tab of `get_size` task, the field `size` is 134,481,400. So the output file `yellow_tripdata_2020-12.csv` of the `extract` task has a size of **134.5 MiB**.


2) As the variable `file` is thus defined: 
```yaml
  file: "{{inputs.taxi}}_tripdata_{{inputs.year}}-{{inputs.month}}.csv"
```
The rendered value of the variable `file` when the inputs `taxi` is set to `green`, `year` is set to `2020`, and `month` is set to `04` during execution is **`green_tripdata_2020-04.csv`**.


3) How many rows are there for the `Yellow` Taxi data for all CSV files in the year 2020?
```sql
SELECT 'Yellow Taxi' as "type", COUNT(*) as "total_rows"
FROM yellow_tripdata
WHERE filename LIKE '%2020%'
;
```
The answer is: **24,648,499**.


4) How many rows are there for the `Green` Taxi data for all CSV files in the year 2020?
```sql
SELECT 'Green Taxi' as "type", COUNT(*) as "total_rows"
FROM green_tripdata
WHERE filename LIKE '%2020%'
;
```
The answer is: **1,734,051**.


5) The `rowCount` output from `yellow_copy_in_to_staging_table` task shows how many rows there are inside the `Yellow` Taxi data for the March 2021 CSV file: **1,925,152**.


6) How to configure the timezone to New York in a Schedule trigger?
- Add a `timezone` property set to `America/New_York` or `US/Eastern` in the `Schedule` trigger configuration
Example:
```yml
triggers:
  - id: green_schedule
    type: io.kestra.plugin.core.trigger.Schedule
    timezone: US/Eastern
    cron: "0 9 1 * *"
    inputs:
      taxi: green
```

## Submitting the solutions

* Form for submitting: https://courses.datatalks.club/de-zoomcamp-2026/homework/hw2
* Check the link above to see the due date

## Solution

Will be added after the due date


## Learning in Public

We encourage everyone to share what they learned. This is called "learning in public".

Read more about the benefits [here](https://alexeyondata.substack.com/p/benefits-of-learning-in-public-and).

### Example post for LinkedIn

```
🚀 Week 2 of Data Engineering Zoomcamp by @DataTalksClub and @Will Russel complete!

Just finished Module 2 - Workflow Orchestration with @Kestra. Learned how to:

✅ Orchestrate data pipelines with Kestra flows
✅ Use variables and expressions for dynamic workflows
✅ Implement backfill for historical data
✅ Schedule workflows with timezone support
✅ Process NYC taxi data (Yellow & Green) for 2019-2021

Built ETL pipelines that extract, transform, and load taxi trip data automatically!

Thanks to the @Kestra team for the great orchestration tool!

Here's my homework solution: <LINK>

Following along with this amazing free course - who else is learning data engineering?

You can sign up here: https://github.com/DataTalksClub/data-engineering-zoomcamp/
```

### Example post for Twitter/X

```
Module 2 of DE Zoomcamp by @DataTalksClub @wrussell1999 done!

- @kestra_io workflow orchestration
- ETL pipelines for taxi data
- Backfill & scheduling
- Variables & dynamic flows

My solution: <LINK>

Join me here: https://github.com/DataTalksClub/data-engineering-zoomcamp/
```
