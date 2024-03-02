# Blockchain State Processor API

This FastAPI application processes simulated Ethereum block data to track registrations between Validators and Operators, and serves the current state through a REST API.

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip

### Installation

1. **Change to code folder** (ensure the code is on your local machine).

```bash
cd <assignment-directory>
```

2. **Create a Virtual Environment** (Optional but recommended):

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

3. **Install Dependencies**:

```bash
pip install -r requirements.txt
```

### Running the Application

1. Navigate to the directory containing your `main.py` file.

2. Start the FastAPI server:

```bash
uvicorn main:app --reload
```

The `--reload` flag is optional and enables automatic reloading of the server upon code changes, which is useful during development.

3. Access the API documentation and test the endpoints by navigating to: `http://127.0.0.1:8000/docs` in your web browser.

## Implementation Details

### GET state endpoint 

This endpoint returns the state for provided block number and fileName
It assumes that file is located in the filesystem next to the `main.py` file

example:
```
GET http://127.0.0.1:8000/state/?fileName=blocks.json&blockNumber=2
```

In order to optimize the response time for large json files I've implemented here block and file level cache. It may cause the Out of Memory exception in some edge cases if the files is too big

To cleare cache there is an e
POST http://127.0.0.1:8000/invalidate_cache/

Other performace considerations, assuming validators can't register in multiple transactions incrementally we can use here parallel processing of blocks with something like this:
```
# Process blocks in parallel using ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=max_workers) as executor:
    futures = {executor.submit(process_block, block): block for block in blocks}
    for future in as_completed(futures):
        block = futures[future]
        try:
            data = future.result()
            # Handle the processed block data
        except Exception as exc:
            print(f'Block {block["id"]} generated an exception: {exc}')
```


In the production environment I would consider using some fast key value storage like Redis in order to be able to scale the application horizontally.