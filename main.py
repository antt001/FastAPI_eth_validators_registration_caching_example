from fastapi import FastAPI, HTTPException, Query, status
import json
from typing import Optional
from pathlib import Path
from block_cache import BlockCache

# Create the FastAPI app

app = FastAPI()

# In-memory cache to store the content of blocks.json files
file_cache = {}

blocks_cache = {}

def read_and_cache_file(file_name: str) -> dict:
    """
    Reads a file from the filesystem, parses it as JSON, and caches it.
    If the file is already cached, returns the cached content.
    """
    if file_name in file_cache:
        return file_cache[file_name]
    
    file_path = Path(file_name)
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail=f"File {file_name} not found")
    
    with open(file_path, 'r') as file:
        content = json.load(file)
        file_cache[file_name] = content  # Cache the content for future requests
        return content

def process_blocks(blocks, blockNumber: Optional[int], block_cache: BlockCache) -> dict:
    """
    Processes the blocks up to the specified blockNumber, updating validators and operators.
    """
    validators = {}
    operators = {}
    validator_id_counter = 0

    cached_block, nearest_state = block_cache.get_nearest_checkpoint(blockNumber)
    if nearest_state is not None:
        validators = nearest_state["validators"]
        operators = nearest_state["operators"]
        validator_id_counter = len(validators)

    # Process blocks up to the specified blockNumber
    for block_num in range(cached_block, len(blocks)):
        block = blocks[block_num]
        if blockNumber is not None and block["id"] > blockNumber:
            break  # Stop processing if we've reached the specified blockNumber
        
        for transaction in block["transactions"]:
            if "register" in transaction and transaction["register"]:
                address = transaction["address"]
                
                # Skip validators registration with less than 3 operators
                # assuming validators can't register in multiple transactions incrementally
                if len(transaction["register"]) < 3:
                    continue 
                
                # Update validators and operators
                if address not in validators:
                    validators[address] = {
                        "address": address,
                        "id": validator_id_counter,
                        "operators": transaction["register"]
                    }
                    validator_id_counter += 1
                else:
                    validators[address]["operators"] = transaction["register"]
                
                for operator_id in transaction["register"]:
                    if operator_id not in operators:
                        operators[operator_id] = {
                            "id": operator_id,
                            "validators": [validators[address]["id"]]
                        }
                    else:
                        if validators[address]["id"] not in operators[operator_id]:
                            operators[operator_id]["validators"].append(validators[address]["id"]) 
        
        # Update the block cache
        block_cache.save_checkpoint(block_num, {"validators": validators, "operators": operators})
    
    
    return {"validators": list(validators.values()), "operators": list(operators.values())}

@app.get("/state/")
async def get_state(fileName: str = Query(..., alias="fileName"), blockNumber: Optional[int] = Query(None, alias="blockNumber")) -> dict:
    """
    Returns the state of validators and operators up to the specified block number.
    If blockNumber is not provided, returns the state for all processed blocks.
    """
    blocks_data = read_and_cache_file(fileName)

    if fileName not in blocks_cache:
        blocks_cache[fileName] = BlockCache()
    
    # Process blocks up to the specified blockNumber and return the state
    state = process_blocks(blocks_data["blocks"], blockNumber, blocks_cache[fileName]) 

    return state

@app.post("/invalidate_cache/", status_code=status.HTTP_204_NO_CONTENT)
def invalidate_cache():
    """
    Invalidate (clear) the cache, forcing the application to reload data from the filesystem on the next request.
    """
    file_cache.clear()
    blocks_cache.clear()
    return {"detail": "Cache invalidated successfully."}