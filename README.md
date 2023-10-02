# Analyzing Coinbase Order Book in Real Time
This project demonstrates a data pipeline using the [Coinbase websocket feed](https://docs.cloud.coinbase.com/exchange/docs/websocket-channels#level2-batch-channel) to display and analyze their order book in real time.

![coinbase-app-demo](https://github.com/TylerHillery/coinbase-order-book-pipeline/assets/58156078/7c701c08-49b3-4033-8094-646b5d9462a7)

## Reference Commands

### Build docker images
```bash
docker-compose build
```

### Start the services
```bash
docker-compose up -d
```

### Stop the data generator
```bash
docker stop data-generator 
```

### Access the dbt cli
```bash
docker exec -it dbt /bin/bash
```

### Access the Materialize cli 
```bash
docker exec -it mzcli psql -U materialize -h materialized -p 6875 materialize
```

## Ports
- http://localhost:8080/ Redpanda Console
- http://localhost:8000/ dbt Docs
- http://localhost:8501/ Streamlit App

## Resources & References

These are resources and references I used when building this project.
- [Real-Time Financial Exchange Order Book](https://bytewax.io/guides/real-time-financial-exchange-order-book-application?utm_source=pocket_saves)
- [Streaming Data Apps with Bytewax and Streamlit](https://bytewax.io/blog/streaming-data-apps-with-bytewax-and-streamlit?utm_source=pocket_saves)
- [How to Build a Real-Time Feature Pipeline In Python](https://www.realworldmcl.xyz/blog/real-time-pipelines-in-python)
- [Temporal analysis of Wikipedia changes with Redpanda & Materialize & dbt](https://medium.com/@danthelion/temporal-analysis-of-wikipedia-changes-with-redpanda-materialize-dbt-e372186fb951)
- [Breathing life into Streamlit with Materialize & Redpanda](https://medium.com/@danthelion/breathing-life-into-streamlit-with-materialize-redpanda-1c29282cc72b)
- [How to build a real-time crypto tracker with Redpanda and QuestDB](https://redpanda.com/blog/real-time-crypto-tracker-questdb-redpanda)
- [Online Machine Learning in Practice: Interactive dashboards to detect data anomalies in real time](https://bytewax.io/blog/online-machine-learning-in-practice-interactive-dashboards-to-detect-data-anomalies-in-real-time)
- [Materialize Top K by group](https://materialize.com/docs/transform-data/patterns/top-k/#top-1-using-distinct-on)
- [Materialize + Redpanda + dbt Hack Day](https://github.com/MaterializeInc/mz-hack-day-2022)
- [Pandas Table Viz](https://pandas.pydata.org/docs/user_guide/style.html#Table-Styles)
- [Plotly Filled Area Plots](https://plotly.com/python/filled-area-plots/)
- [Deploy Streamlit using Docker](https://docs.streamlit.io/knowledge-base/tutorials/deploy/docker)
